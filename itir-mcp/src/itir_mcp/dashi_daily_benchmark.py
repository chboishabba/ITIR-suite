from __future__ import annotations

import json
import re
import sys
from argparse import ArgumentParser
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping

from .pnf_numeric_abi import SCHEMA as NUMERIC_SCHEMA
from .pnf_numeric_abi import validate_numeric_abi
from .pnf_spectral_numeric_abi import validate_spectral_numeric_abi


DEFAULT_PROFILE = (
    "dashi-formal",
    "dashi-physics",
    "dashi-vs-les",
    "dashicore-readme-outline",
    "branch-formalizing-dashi-kernel",
    "dashi-learner-context5-trading",
)

SOURCE_ROW_SCHEMA = "itir.mirror.dashi_source_row.v0_1"
AUDIT_PACKET_SCHEMA = "itir.mirror.daily_summary_audit_packet.v0_1"
RENDERER_PACKET_SCHEMA = "itir.mirror.compact_renderer_packet.v0_1"
BENCHMARK_SCHEMA = "itir.mirror.dashi_daily_summary_benchmark.v0_1"

_CITATION_RE = re.compile(r"\[([A-Za-z0-9_.:-]+)\]")


def convert_chatgpt_exports(
    export_dir: str | Path,
    *,
    profile: Iterable[str] = DEFAULT_PROFILE,
    chunk_chars: int = 6000,
) -> list[dict[str, Any]]:
    base = Path(export_dir)
    rows: list[dict[str, Any]] = []
    for path in _profile_paths(base, tuple(profile)):
        payload = json.loads(path.read_text(encoding="utf-8"))
        rows.extend(_conversation_rows(payload, path, chunk_chars=chunk_chars))
    return sorted(rows, key=lambda row: (row["profile_id"], row["conversation_id"], row["turn_index"], row["chunk_index"], row["source_row_id"]))


def window_source_rows(
    rows: list[dict[str, Any]],
    *,
    per_thread_cap: int = 30,
    total_cap: int = 180,
) -> list[dict[str, Any]]:
    by_thread: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_thread[str(row["conversation_id"])].append(row)

    selected: list[dict[str, Any]] = []
    for conversation_id in sorted(by_thread):
        thread_rows = sorted(by_thread[conversation_id], key=lambda row: (row["turn_index"], row["chunk_index"], row["source_row_id"]))
        if len(thread_rows) <= per_thread_cap:
            selected.extend(thread_rows)
        else:
            selected.extend(_head_middle_tail(thread_rows, per_thread_cap))
    return sorted(selected, key=lambda row: (row["profile_id"], row["conversation_id"], row["turn_index"], row["chunk_index"]))[:total_cap]


def build_audit_packet(rows: list[dict[str, Any]], *, date: str, profile_id: str = "dashi-spread-v0") -> dict[str, Any]:
    selected_surfaces = []
    weak_surfaces = []
    conflict_surfaces = []
    for index, row in enumerate(rows, start=1):
        surface = {
            "surface_id": f"S{index}",
            "source_row_id": row["source_row_id"],
            "conversation_id": row["conversation_id"],
            "title": row["title"],
            "role": row["role"],
            "text": row["text"],
            "receipt_ids": [f"receipt:{row['source_row_id']}"],
            "span_refs": [{"source_row_id": row["source_row_id"], "start": 0, "end": len(row["text"])}],
            "citation_marker": f"[S{index}]",
        }
        if index % 17 == 0:
            conflict_surfaces.append(surface)
        elif index % 7 == 0:
            weak_surfaces.append(surface)
        else:
            selected_surfaces.append(surface)
    return {
        "schema": AUDIT_PACKET_SCHEMA,
        "date": date,
        "profile_id": profile_id,
        "source_rows": rows,
        "selected_surfaces": selected_surfaces,
        "weak_surfaces": weak_surfaces,
        "conflict_surfaces": conflict_surfaces,
        "blocked_surfaces": [],
        "residual_summary": {
            "selected": len(selected_surfaces),
            "weak": len(weak_surfaces),
            "conflict": len(conflict_surfaces),
            "blocked": 0,
        },
        "compact_summary": _compact_summary(selected_surfaces[:8]),
    }


def build_renderer_packet(audit_packet: Mapping[str, Any]) -> dict[str, Any]:
    selected = list(audit_packet.get("selected_surfaces") or [])
    markers = [str(surface.get("citation_marker")) for surface in selected if surface.get("citation_marker")]
    residual_summary = dict(audit_packet.get("residual_summary") or {})
    return {
        "schema": RENDERER_PACKET_SCHEMA,
        "date": audit_packet.get("date"),
        "profile_id": audit_packet.get("profile_id"),
        "selected_surface_ids": [surface.get("surface_id") for surface in selected],
        "fibre_ids": [surface.get("source_row_id") for surface in selected],
        "facts": [_renderer_fact(surface, index) for index, surface in enumerate(selected, start=1)],
        "support_counts": {"selected": len(selected), "source_rows": len(audit_packet.get("source_rows") or [])},
        "contradiction_counts": {"conflict": int(residual_summary.get("conflict", 0) or 0)},
        "source_counts": _source_counts(audit_packet.get("source_rows") or []),
        "residual_summary": residual_summary,
        "citation_markers": markers,
    }


def compression_metrics(
    *,
    raw_text: str,
    source_rows: list[dict[str, Any]],
    audit_packet: Mapping[str, Any],
    renderer_packet: Mapping[str, Any],
    rendered_summary: str,
) -> dict[str, Any]:
    sizes = {
        "raw_text_bytes": _byte_len(raw_text),
        "source_rows_bytes": _byte_len(source_rows),
        "full_audit_packet_bytes": _byte_len(audit_packet),
        "renderer_packet_bytes": _byte_len(renderer_packet),
        "selected_surfaces_bytes": _byte_len(audit_packet.get("selected_surfaces") or []),
        "rendered_summary_bytes": _byte_len(rendered_summary),
    }
    raw = max(1, sizes["raw_text_bytes"])
    audit = max(1, sizes["full_audit_packet_bytes"])
    sizes["renderer_to_raw_ratio"] = sizes["renderer_packet_bytes"] / raw
    sizes["renderer_to_audit_ratio"] = sizes["renderer_packet_bytes"] / audit
    return sizes


def fact_check_compact_summary(
    compact_summary: str,
    selected_surfaces: list[dict[str, Any]],
    *,
    sensiblaw_available: bool | None = None,
) -> dict[str, Any]:
    if sensiblaw_available is None:
        sensiblaw_available = _sensiblaw_available()
    claims = _extract_cited_bullets(compact_summary)
    if not sensiblaw_available:
        return {
            "status": "unavailable",
            "marker": "UNAVAILABLE",
            "claims": [
                {"claim": claim["claim"], "citation_markers": claim["citation_markers"], "classification": "UNAVAILABLE", "receipt_ids": []}
                for claim in claims
            ],
            "summary": {"UNAVAILABLE": len(claims)},
        }

    surfaces_by_marker = {str(surface.get("citation_marker") or f"[{surface.get('surface_id')}]").strip("[]"): surface for surface in selected_surfaces}
    checked = []
    counts: dict[str, int] = defaultdict(int)
    for claim in claims:
        cited = [surfaces_by_marker[marker] for marker in claim["citation_markers"] if marker in surfaces_by_marker]
        classification = _classify_claim_against_surfaces(claim["claim"], cited)
        counts[classification] += 1
        checked.append(
            {
                "claim": claim["claim"],
                "citation_markers": claim["citation_markers"],
                "classification": classification,
                "receipt_ids": [],
                "surface_ids": [surface.get("surface_id") for surface in cited],
            }
        )
    return {"status": "checked", "marker": "reparse_checked", "claims": checked, "summary": dict(counts)}


def run_dashi_spread_benchmark(
    export_dir: str | Path,
    *,
    date: str,
    profile: Iterable[str] = DEFAULT_PROFILE,
    min_source_units: int = 100,
    allow_small: bool = False,
    spectral_payload: Mapping[str, Any] | None = None,
    spectral_payload_path: str | Path | None = None,
) -> dict[str, Any]:
    source_rows = convert_chatgpt_exports(export_dir, profile=profile)
    windowed = window_source_rows(source_rows)
    if len(windowed) < min_source_units and not allow_small:
        raise ValueError(f"dashi-spread-v0 requires at least {min_source_units} source units")
    audit_packet = build_audit_packet(windowed, date=date)
    renderer_packet = build_renderer_packet(audit_packet)
    compact_summary = str(audit_packet.get("compact_summary") or "")
    raw_text = "\n".join(row["text"] for row in windowed)
    metrics = compression_metrics(
        raw_text=raw_text,
        source_rows=windowed,
        audit_packet=audit_packet,
        renderer_packet=renderer_packet,
        rendered_summary=compact_summary,
    )
    return {
        "schema": BENCHMARK_SCHEMA,
        "profile_id": "dashi-spread-v0",
        "date": date,
        "source_unit_count": len(windowed),
        "variants": {
            "A_raw_dashi": {"context_bytes": metrics["raw_text_bytes"]},
            "B_full_audit_packet": {"context_bytes": metrics["full_audit_packet_bytes"]},
            "C_renderer_packet": {"context_bytes": metrics["renderer_packet_bytes"]},
        },
        "compression_scoreboard": metrics,
        "fact_check": fact_check_compact_summary(compact_summary, audit_packet["selected_surfaces"]),
        "selected_count": len(audit_packet["selected_surfaces"]),
        "weak_count": len(audit_packet["weak_surfaces"]),
        "conflict_count": len(audit_packet["conflict_surfaces"]),
        "blocked_count": len(audit_packet["blocked_surfaces"]),
        "abi_statuses": abi_statuses(
            {"spectral_numeric_abi": spectral_payload} if spectral_payload is not None else {},
            spectral_payload_path=spectral_payload_path,
        ),
        "audit_packet": audit_packet,
        "renderer_packet": renderer_packet,
    }


def abi_statuses(
    candidate_payloads: Mapping[str, Any] | None = None,
    *,
    spectral_payload_path: str | Path | None = None,
) -> dict[str, Any]:
    numeric_payload = {
        "schema": NUMERIC_SCHEMA,
        "dtype": "float32",
        "z": [1.0],
        "A": [[1.0]],
        "row_map": [{"row": 0, "receipt_ids": ["numeric-smoke"]}],
    }
    statuses: dict[str, Any] = {"numeric_abi_smoke": {"status": "PASS", **validate_numeric_abi(numeric_payload), "diagnostic_only": True}}
    try:
        spectral_payload, spectral_source = _resolve_spectral_payload(candidate_payloads or {}, spectral_payload_path=spectral_payload_path)
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        diagnostics = {
            "source": "file" if spectral_payload_path is not None else "candidate_payloads",
            "reason": "spectral payload resolution failed",
            "error": str(exc),
        }
        if spectral_payload_path is not None:
            diagnostics["payload_path"] = str(Path(spectral_payload_path))
        statuses["spectral_numeric_abi_smoke"] = {
            "status": "FAIL",
            "reason": "spectral payload invalid",
            "diagnostic_only": True,
            "diagnostics": diagnostics,
        }
        return statuses
    if spectral_payload is None:
        statuses["spectral_numeric_abi_smoke"] = {
            "status": "SKIPPED",
            "reason": "spectral payload not supplied",
            "diagnostic_only": True,
        }
        return statuses

    try:
        statuses["spectral_numeric_abi_smoke"] = {
            "status": "PASS",
            "source": spectral_source,
            **validate_spectral_numeric_abi(dict(spectral_payload)),
        }
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        diagnostics = {
            "source": spectral_source,
            "reason": "spectral payload validation failed",
            "error": str(exc),
        }
        if spectral_payload_path is not None:
            diagnostics["payload_path"] = str(Path(spectral_payload_path))
        statuses["spectral_numeric_abi_smoke"] = {
            "status": "FAIL",
            "reason": "spectral payload invalid",
            "diagnostic_only": True,
            "diagnostics": diagnostics,
        }
    return statuses


def _resolve_spectral_payload(
    candidate_payloads: Mapping[str, Any],
    *,
    spectral_payload_path: str | Path | None = None,
) -> tuple[dict[str, Any] | None, str]:
    if spectral_payload_path is not None and candidate_payloads.get("spectral_numeric_abi") is not None:
        raise ValueError("provide spectral_payload or spectral_payload_path, not both")
    if spectral_payload_path is not None:
        payload = _load_spectral_payload(Path(spectral_payload_path))
        return payload, "file"

    spectral_payload = candidate_payloads.get("spectral_numeric_abi")
    if isinstance(spectral_payload, Mapping):
        return dict(spectral_payload), "candidate_payloads"
    if spectral_payload is None:
        return None, "unsupplied"
    raise ValueError("spectral_numeric_abi payload must be a JSON object")


def _load_spectral_payload(path: Path) -> dict[str, Any]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, Mapping):
        return dict(_unwrap_spectral_payload_envelope(raw))
    raise ValueError("spectral payload file must contain a JSON object")


def _unwrap_spectral_payload_envelope(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    if "schema" in payload:
        return payload
    nested = payload.get("spectral_numeric_abi")
    if isinstance(nested, Mapping):
        return nested
    return payload


def _profile_paths(base: Path, profile: tuple[str, ...]) -> list[Path]:
    paths = []
    for slug in profile:
        matches = sorted(base.glob(f"{slug}__*.json"))
        if matches:
            paths.append(matches[0])
    return paths


def _conversation_rows(payload: Mapping[str, Any], path: Path, *, chunk_chars: int) -> list[dict[str, Any]]:
    mapping = payload.get("mapping")
    if not isinstance(mapping, Mapping):
        return []
    title = str(payload.get("title") or path.stem)
    conversation_id = str(payload.get("conversation_id") or path.stem)
    profile_id = path.name.split("__", 1)[0]
    messages = []
    for order, node in enumerate(mapping.values()):
        if not isinstance(node, Mapping) or not isinstance(node.get("message"), Mapping):
            continue
        message = node["message"]
        text = _message_text(message)
        if not text:
            continue
        author = message.get("author") if isinstance(message.get("author"), Mapping) else {}
        messages.append(
            {
                "order": order,
                "node_id": str(node.get("id") or message.get("id") or order),
                "role": str(author.get("role") or "unknown"),
                "timestamp": message.get("create_time") or payload.get("create_time"),
                "text": text,
            }
        )
    messages.sort(key=lambda item: (item["timestamp"] is None, item["timestamp"] or 0, item["order"]))
    rows = []
    for turn_index, message in enumerate(messages):
        chunks = _chunks(message["text"], chunk_chars)
        for chunk_index, chunk in enumerate(chunks):
            source_row_id = f"chatgpt:{conversation_id}:{message['node_id']}:c{chunk_index}"
            rows.append(
                {
                    "schema": SOURCE_ROW_SCHEMA,
                    "source_row_id": source_row_id,
                    "profile_id": profile_id,
                    "conversation_id": conversation_id,
                    "title": title,
                    "role": message["role"],
                    "node_id": message["node_id"],
                    "source_path": str(path),
                    "chunk_index": chunk_index,
                    "chunk_count": len(chunks),
                    "turn_index": turn_index,
                    "timestamp": message["timestamp"],
                    "text": chunk,
                }
            )
    return rows


def _message_text(message: Mapping[str, Any]) -> str:
    content = message.get("content")
    if not isinstance(content, Mapping):
        return ""
    parts = content.get("parts")
    if isinstance(parts, list):
        text = "\n".join(part if isinstance(part, str) else json.dumps(part, sort_keys=True) for part in parts)
        return text.strip()
    text = content.get("text")
    return text.strip() if isinstance(text, str) else ""


def _chunks(text: str, size: int) -> list[str]:
    if size <= 0:
        raise ValueError("chunk_chars must be positive")
    return [text[index : index + size] for index in range(0, len(text), size)] or [""]


def _head_middle_tail(rows: list[dict[str, Any]], cap: int) -> list[dict[str, Any]]:
    head_count = cap // 3
    tail_count = cap // 3
    middle_count = cap - head_count - tail_count
    middle_start = max(head_count, (len(rows) - middle_count) // 2)
    indexes = set(range(head_count))
    indexes.update(range(middle_start, min(len(rows), middle_start + middle_count)))
    indexes.update(range(max(0, len(rows) - tail_count), len(rows)))
    return [row for index, row in enumerate(rows) if index in indexes][:cap]


def _compact_summary(surfaces: list[dict[str, Any]]) -> str:
    bullets = []
    for surface in surfaces:
        payload = _predicate_payload(str(surface.get("text") or ""))
        if payload:
            bullets.append(f"- {payload} {surface['citation_marker']}")
    return "\n".join(bullets)


def _predicate_payload(text: str) -> str:
    normalized = " ".join(text.split())
    if len(normalized) <= 180:
        return normalized
    return normalized[:177].rsplit(" ", 1)[0] + "..."


def _renderer_fact(surface: Mapping[str, Any], index: int) -> dict[str, Any]:
    text = str(surface.get("text") or "")
    payload = _renderer_predicate_payload(text)
    residual_status = "selected"
    return {
        "fact_id": f"fact:{surface.get('surface_id') or index}",
        "normal_form": payload["normal_form"],
        "rendered_fact": _predicate_payload(text),
        "fibre_id": surface.get("source_row_id"),
        "residual_status": residual_status,
        "support_count": 1,
        "contradiction_count": 0,
        "citations": [surface.get("citation_marker")] if surface.get("citation_marker") else [],
        "authority_label": "candidate-only",
    }


def _renderer_predicate_payload(text: str) -> dict[str, Any]:
    normalized = _normalize_for_match(text)
    terms = [term for term in normalized.split() if len(term) > 3]
    return {
        "text_hash": _byte_stable_hash(text),
        "normal_form": f"nf:{_byte_stable_hash(normalized)}",
        "token_count": len(normalized.split()),
        "keywords": terms[:12],
    }


def _source_counts(rows: Iterable[Mapping[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for row in rows:
        counts[str(row.get("conversation_id"))] += 1
    return dict(counts)


def _byte_len(value: Any) -> int:
    if isinstance(value, str):
        return len(value.encode("utf-8"))
    return len(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8"))


def _byte_stable_hash(text: str) -> str:
    import hashlib

    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _extract_cited_bullets(summary: str) -> list[dict[str, Any]]:
    claims = []
    for line in summary.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        markers = _CITATION_RE.findall(stripped)
        if not markers:
            continue
        claim = _CITATION_RE.sub("", stripped.lstrip("-*0123456789. ")).strip()
        claims.append({"claim": claim, "citation_markers": markers})
    return claims


def _sensiblaw_available() -> bool:
    return False


def _classify_claim_against_surfaces(claim: str, surfaces: list[dict[str, Any]]) -> str:
    if not surfaces:
        return "NO_TYPED_MEET"
    claim_norm = _normalize_for_match(claim)
    support = " ".join(_normalize_for_match(str(surface.get("text") or "")) for surface in surfaces)
    if not claim_norm or not support:
        return "NO_TYPED_MEET"
    surface_norms = [_normalize_for_match(str(surface.get("text") or "")) for surface in surfaces]
    if any(claim_norm == surface_norm for surface_norm in surface_norms):
        return "EXACT"
    if _looks_contradictory(claim_norm, support):
        return "CONTRADICTION"
    claim_terms = set(claim_norm.split())
    support_terms = set(support.split())
    if claim_terms and len(claim_terms & support_terms) / len(claim_terms) >= 0.5:
        return "PARTIAL"
    return "NO_TYPED_MEET"


def _normalize_for_match(text: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9 ]+", " ", text.lower()).split())


def _looks_contradictory(claim: str, support: str) -> bool:
    claim_terms = set(claim.split())
    support_terms = set(support.split())
    if len((claim_terms - {"not", "no", "never"}) & (support_terms - {"not", "no", "never"})) < 2:
        return False
    claim_negative = bool(claim_terms & {"not", "no", "never"})
    support_negative = bool(support_terms & {"not", "no", "never"})
    return claim_negative != support_negative


def main(argv: list[str] | None = None) -> int:
    parser = ArgumentParser(description="Run the Dashi daily spread benchmark.")
    parser.add_argument("--export-dir", required=True, help="Directory containing profiled ChatGPT export JSON files.")
    parser.add_argument("--date", required=True, help="Benchmark date, formatted by the caller.")
    parser.add_argument("--profile", action="append", help="Profile slug to include. May be passed more than once.")
    parser.add_argument("--min-source-units", type=int, default=100)
    parser.add_argument("--allow-small", action="store_true")
    parser.add_argument("--spectral-payload", help="Path to a v0.2 spectral ABI JSON payload.")
    args = parser.parse_args(argv)

    result = run_dashi_spread_benchmark(
        args.export_dir,
        date=args.date,
        profile=tuple(args.profile) if args.profile else DEFAULT_PROFILE,
        min_source_units=args.min_source_units,
        allow_small=args.allow_small,
        spectral_payload_path=args.spectral_payload,
    )
    json.dump(result, sys.stdout, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
