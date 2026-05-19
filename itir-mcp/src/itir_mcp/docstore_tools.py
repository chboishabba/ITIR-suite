from __future__ import annotations

import importlib.util
import json
import sys
from collections import Counter
from hashlib import sha256
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from .contracts import JsonDict, ToolHandler, ToolInputError, ToolSpec
from .docstore_producers import collect_producer_pressure_from_paths


DOCSTORE_STATUS_VERSION = "itir.docstore.status.v1"
OPEN_QUESTIONS_VERSION = "itir.docstore.open_questions.v1"
OBSIDIAN_SCAN_VERSION = "itir.obsidian.vault_scan.v1"

_SKIP_DIRS = {
    ".git",
    ".hg",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
    "runs",
    "target",
}

_HEADING_HINTS: tuple[tuple[str, str], ...] = (
    ("open question", "open_question"),
    ("open questions", "open_question"),
    ("question", "open_question"),
    ("questions", "open_question"),
    ("blocker", "blocker"),
    ("blockers", "blocker"),
    ("gap", "gap"),
    ("gaps", "gap"),
    ("assumption", "assumption"),
    ("assumptions", "assumption"),
)


def get_docstore_tools() -> list[tuple[ToolSpec, ToolHandler]]:
    return [
        (
            ToolSpec(
                name="itir.docstore.status",
                title="ITIR docstore status",
                description="Build a read-only global docstore status view from suite artifacts and observer inputs.",
                input_schema=_shared_input_schema(),
                response_version=DOCSTORE_STATUS_VERSION,
                read_only=True,
            ),
            docstore_status,
        ),
        (
            ToolSpec(
                name="itir.docstore.open_questions",
                title="ITIR docstore open questions",
                description="Aggregate structured open questions and promoted hints without broad free-form regex scraping.",
                input_schema=_shared_input_schema(),
                response_version=OPEN_QUESTIONS_VERSION,
                read_only=True,
            ),
            docstore_open_questions,
        ),
        (
            ToolSpec(
                name="itir.obsidian.vault_scan",
                title="Obsidian observer vault scan",
                description="Read allowlisted Obsidian vault or bundle inputs as observer-class candidate hints.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "vault_root": {"type": "string"},
                        "vault_roots": {"type": "array", "items": {"type": "string"}},
                        "bundle_path": {"type": "string"},
                        "bundle_paths": {"type": "array", "items": {"type": "string"}},
                        "max_notes": {"type": "integer", "minimum": 1},
                        "limit": {"type": "integer", "minimum": 1},
                        "include_display_fields": {"type": "boolean"},
                    },
                    "required": [],
                    "additionalProperties": True,
                },
                response_version=OBSIDIAN_SCAN_VERSION,
                read_only=True,
            ),
            obsidian_vault_scan,
        ),
    ]


def docstore_status(payload: Mapping[str, Any]) -> JsonDict:
    roots = _payload_roots(payload)
    artifact_pairs = _collect_normalized_artifacts(payload, roots)
    state_pairs = _collect_state_payloads(payload, roots)
    questions_payload = _collect_open_questions(payload, roots, limit=_int(payload.get("question_limit"), 50))

    artifacts = [item for item, _ in artifact_pairs]
    join_view = _join_artifacts(artifacts) if artifacts else None
    producer_counts = Counter(_artifact_producer(item) for item in artifacts)
    role_counts = Counter(str(item.get("artifact_role") or "unknown") for item in artifacts)
    authority_counts = Counter(str((item.get("authority") or {}).get("authority_class") or "unknown") for item in artifacts)
    unresolved_counts = Counter(str(item.get("unresolved_pressure_status") or "unknown") for item in artifacts)
    state_pressure_counts = Counter()
    for state, _path in state_pairs:
        for key in ("alerts", "open_questions", "blocked_tasks"):
            value = state.get(key)
            if isinstance(value, list) and value:
                state_pressure_counts[key] += len(value)

    latest_artifacts = [
        {
            "artifact_id": str(item.get("artifact_id") or ""),
            "artifact_role": str(item.get("artifact_role") or ""),
            "source_system": _artifact_producer(item),
            "unresolved_pressure_status": str(item.get("unresolved_pressure_status") or "unknown"),
            "path": str(path),
        }
        for item, path in artifact_pairs[: _int(payload.get("limit"), 25)]
    ]

    return {
        "version": DOCSTORE_STATUS_VERSION,
        "roots": [str(root) for root in roots],
        "sources": questions_payload["sources"],
        "artifact_count": len(artifacts),
        "state_count": len(state_pairs),
        "producer_counts": dict(sorted(producer_counts.items())),
        "role_counts": dict(sorted(role_counts.items())),
        "authority_counts": dict(sorted(authority_counts.items())),
        "unresolved_pressure_counts": dict(sorted(unresolved_counts.items())),
        "state_pressure_counts": dict(sorted(state_pressure_counts.items())),
        "open_question_counts": questions_payload["counts"],
        "latest_artifacts": latest_artifacts,
        "join_view": join_view,
    }


def docstore_open_questions(payload: Mapping[str, Any]) -> JsonDict:
    roots = _payload_roots(payload)
    limit = _int(payload.get("limit"), 100)
    return _collect_open_questions(payload, roots, limit=limit)


def obsidian_vault_scan(payload: Mapping[str, Any]) -> JsonDict:
    limit = _int(payload.get("limit"), 100)
    max_notes = _int(payload.get("max_notes"), 200)
    include_display_fields = bool(payload.get("include_display_fields", False))
    vault_roots = _path_list(payload, "vault_roots", "vault_root")
    bundle_paths = _path_list(payload, "bundle_paths", "bundle_path")

    notes: list[JsonDict] = []
    candidates: list[JsonDict] = []
    sources: list[JsonDict] = []

    for root in vault_roots:
        root_path = _resolve_path(root)
        if not root_path.exists() or not root_path.is_dir():
            raise ToolInputError(f"vault root does not exist or is not a directory: {root}")
        vault_id_hash = _hash_text(str(root_path))
        sources.append({"kind": "obsidian_vault_root", "vault_id_hash": vault_id_hash, "note_limit": max_notes})
        for index, note_path in enumerate(_iter_markdown_files(root_path, max_files=max_notes)):
            if index >= max_notes:
                break
            rel = _safe_rel(note_path, root_path)
            content = note_path.read_text(encoding="utf-8", errors="replace")
            note_id_hash = _hash_text(rel)
            note = {
                "schema_version": "obsidian.note_observer.v1",
                "note_id_hash": note_id_hash,
                "vault_id_hash": vault_id_hash,
                "event": "note_scanned",
                "authority_class": "observer",
            }
            if include_display_fields:
                note["display_path"] = rel
            notes.append(note)
            candidates.extend(
                _extract_markdown_hints(
                    content,
                    source_system="Obsidian",
                    lane="obsidian_vault",
                    artifact_id=f"obsidian.note:{note_id_hash}",
                    source_ref={"kind": "obsidian_note", "note_id_hash": note_id_hash, "vault_id_hash": vault_id_hash},
                    authority_class="observer",
                    promotion_level="structured_hint",
                )
            )

    for bundle in bundle_paths:
        bundle_path = _resolve_path(bundle)
        if not bundle_path.exists() or not bundle_path.is_file():
            raise ToolInputError(f"bundle path does not exist or is not a file: {bundle}")
        records = _load_bundle_records(bundle_path)
        sources.append({"kind": "obsidian_bundle", "path": str(bundle_path), "record_count": len(records)})
        for index, record in enumerate(records[:max_notes]):
            note_id_hash = _record_hash(record, "note_id", "note_id_hash")
            vault_id_hash = _record_hash(record, "vault_id", "vault_id_hash")
            notes.append(
                {
                    "schema_version": "obsidian.note_observer.v1",
                    "note_id_hash": note_id_hash,
                    "vault_id_hash": vault_id_hash,
                    "event": str(record.get("event") or "note_observed"),
                    "authority_class": "observer",
                }
            )
            text = _record_text(record)
            if text:
                candidates.extend(
                    _extract_markdown_hints(
                        text,
                        source_system="Obsidian",
                        lane="obsidian_bundle",
                        artifact_id=f"obsidian.bundle_note:{note_id_hash or index}",
                        source_ref={"kind": "obsidian_note", "note_id_hash": note_id_hash, "vault_id_hash": vault_id_hash},
                        authority_class="observer",
                        promotion_level="structured_hint",
                    )
                )

    candidates = candidates[:limit]
    return {
        "version": OBSIDIAN_SCAN_VERSION,
        "authority_class": "observer",
        "notes": notes[:max_notes],
        "candidates": candidates,
        "counts": _question_counts(candidates),
        "sources": sources,
    }


def _collect_open_questions(payload: Mapping[str, Any], roots: Sequence[Path], *, limit: int) -> JsonDict:
    questions: list[JsonDict] = []
    sources: list[JsonDict] = []

    artifact_pairs = _collect_normalized_artifacts(payload, roots)
    sources.append({"kind": "normalized_artifacts", "count": len(artifact_pairs)})
    for artifact, path in artifact_pairs:
        questions.extend(_questions_from_artifact(artifact, path))

    state_pairs = _collect_state_payloads(payload, roots)
    sources.append({"kind": "statiBaker_state", "count": len(state_pairs)})
    for state, path in state_pairs:
        questions.extend(_questions_from_state(state, path))

    review_packets = _collect_review_packets(payload, roots)
    sources.append({"kind": "sensiblaw_review_packets", "count": len(review_packets)})
    for packet, path in review_packets:
        questions.extend(_questions_from_review_packet(packet, path))

    producer_pressure = _collect_explicit_producer_pressure(payload)
    if producer_pressure:
        sources.append({"kind": "producer_pressure_adapters", "count": len(producer_pressure)})
        questions.extend(producer_pressure)

    if payload.get("include_todo_graph", True):
        todo_payload = _todo_graph_payload(payload)
        if todo_payload:
            sources.append({"kind": "todo_graph", "obligation_count": len(todo_payload.get("obligations") or [])})
            questions.extend(_questions_from_todo_graph(todo_payload))

    if payload.get("include_markdown_hints", True):
        markdown_paths = _collect_markdown_paths(payload, roots)
        sources.append({"kind": "markdown_hints", "count": len(markdown_paths)})
        for path in markdown_paths:
            questions.extend(
                _extract_markdown_hints(
                    path.read_text(encoding="utf-8", errors="replace"),
                    source_system="Docstore",
                    lane="markdown_hint",
                    artifact_id=f"doc:{_safe_rel(path, _suite_root())}",
                    source_ref={"kind": "repo_markdown", "path": _safe_rel(path, _suite_root())},
                    authority_class="observer",
                    promotion_level="structured_hint",
                )
            )

    if _path_list(payload, "vault_roots", "vault_root") or _path_list(payload, "bundle_paths", "bundle_path"):
        obsidian_payload = obsidian_vault_scan(payload)
        sources.append({"kind": "obsidian_observer", "count": len(obsidian_payload.get("candidates") or [])})
        questions.extend(list(obsidian_payload.get("candidates") or []))

    questions = _filter_questions(questions, payload)
    return {
        "version": OPEN_QUESTIONS_VERSION,
        "questions": questions[:limit],
        "counts": _question_counts(questions),
        "truncated": len(questions) > limit,
        "sources": sources,
    }


def _shared_input_schema() -> JsonDict:
    path_list = {"type": "array", "items": {"type": "string"}}
    return {
        "type": "object",
        "properties": {
            "roots": path_list,
            "artifact_paths": path_list,
            "state_paths": path_list,
            "review_packet_paths": path_list,
            "markdown_paths": path_list,
            "todo_paths": path_list,
            "sensiblaw_fact_review_paths": path_list,
            "sensiblaw_operator_view_paths": path_list,
            "statibaker_dashboard_paths": path_list,
            "statibaker_codex_trace_paths": path_list,
            "generated_artifact_paths": path_list,
            "repo_root": {"type": "string"},
            "vault_root": {"type": "string"},
            "vault_roots": path_list,
            "bundle_path": {"type": "string"},
            "bundle_paths": path_list,
            "producer": {"type": "string"},
            "status": {"type": "string"},
            "promotion_level": {"type": "string"},
            "limit": {"type": "integer", "minimum": 1},
            "include_todo_graph": {"type": "boolean"},
            "evaluate_todos": {"type": "boolean"},
            "include_markdown_hints": {"type": "boolean"},
            "include_artifacts": {"type": "boolean"},
        },
        "required": [],
        "additionalProperties": True,
    }


def _collect_explicit_producer_pressure(payload: Mapping[str, Any]) -> list[JsonDict]:
    return collect_producer_pressure_from_paths(
        sensiblaw_fact_review_paths=_path_list(payload, "sensiblaw_fact_review_paths", "sensiblaw_fact_review_path"),
        sensiblaw_operator_view_paths=_path_list(payload, "sensiblaw_operator_view_paths", "sensiblaw_operator_view_path"),
        statibaker_dashboard_paths=_path_list(payload, "statibaker_dashboard_paths", "statibaker_dashboard_path"),
        statibaker_codex_trace_paths=_path_list(payload, "statibaker_codex_trace_paths", "statibaker_codex_trace_path"),
        generated_artifact_paths=_path_list(payload, "generated_artifact_paths", "generated_artifact_path"),
        suite_root=_suite_root(),
    )


def _suite_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _payload_roots(payload: Mapping[str, Any]) -> list[Path]:
    roots = _path_list(payload, "roots")
    return [_resolve_path(root) for root in roots] if roots else []


def _path_list(payload: Mapping[str, Any], plural_key: str, singular_key: str | None = None) -> list[str]:
    values: list[str] = []
    raw = payload.get(plural_key)
    if isinstance(raw, str):
        values.append(raw)
    elif isinstance(raw, Sequence) and not isinstance(raw, (bytes, bytearray, str)):
        values.extend(str(item) for item in raw if str(item).strip())
    if singular_key and payload.get(singular_key):
        values.append(str(payload[singular_key]))
    return values


def _resolve_path(value: str | Path) -> Path:
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = _suite_root() / path
    return path.resolve()


def _collect_normalized_artifacts(payload: Mapping[str, Any], roots: Sequence[Path]) -> list[tuple[JsonDict, Path]]:
    paths = [_resolve_path(path) for path in _path_list(payload, "artifact_paths")]
    if not paths:
        if roots:
            for root in roots:
                paths.extend(_discover_json_files(root, max_files=200, name_hints=("suite_normalized_artifact", "normalized_artifact")))
        else:
            paths.extend(_default_normalized_artifact_paths())

    pairs: list[tuple[JsonDict, Path]] = []
    seen: set[Path] = set()
    for path in paths:
        if path in seen or not path.exists() or not path.is_file():
            continue
        seen.add(path)
        payload_obj = _load_json(path)
        if isinstance(payload_obj, Mapping) and payload_obj.get("schema_version") == "itir.normalized.artifact.v1":
            pairs.append((dict(payload_obj), path))
    return pairs


def _collect_state_payloads(payload: Mapping[str, Any], roots: Sequence[Path]) -> list[tuple[JsonDict, Path]]:
    paths = [_resolve_path(path) for path in _path_list(payload, "state_paths")]
    if not paths:
        if roots:
            for root in roots:
                paths.extend(_discover_state_files(root, max_files=80))
        else:
            paths.extend(_default_state_paths())
    pairs: list[tuple[JsonDict, Path]] = []
    seen: set[Path] = set()
    for path in paths:
        if path in seen or not path.exists() or not path.is_file():
            continue
        seen.add(path)
        payload_obj = _load_json(path)
        if isinstance(payload_obj, Mapping) and _looks_like_sb_state(payload_obj):
            pairs.append((dict(payload_obj), path))
    return pairs


def _collect_review_packets(payload: Mapping[str, Any], roots: Sequence[Path]) -> list[tuple[JsonDict, Path]]:
    paths = [_resolve_path(path) for path in _path_list(payload, "review_packet_paths")]
    if not paths:
        if roots:
            for root in roots:
                paths.extend(_discover_json_files(root, max_files=120, name_hints=("review_packet", "operator_review_surface")))
        else:
            paths.extend(_default_review_packet_paths())
    pairs: list[tuple[JsonDict, Path]] = []
    seen: set[Path] = set()
    for path in paths:
        if path in seen or not path.exists() or not path.is_file():
            continue
        seen.add(path)
        payload_obj = _load_json(path)
        if isinstance(payload_obj, Mapping):
            pairs.append((dict(payload_obj), path))
    return pairs


def _collect_markdown_paths(payload: Mapping[str, Any], roots: Sequence[Path]) -> list[Path]:
    paths = [_resolve_path(path) for path in _path_list(payload, "markdown_paths")]
    if paths:
        return [path for path in paths if path.exists() and path.is_file()]
    if not roots:
        return _default_markdown_paths()
    discovered: list[Path] = []
    for root in roots:
        discovered.extend(_iter_markdown_files(root, max_files=200))
    return discovered


def _default_normalized_artifact_paths() -> list[Path]:
    root = _suite_root()
    patterns = (
        "StatiBaker/runs/*/outputs/suite_normalized_artifact.json",
        "StatiBaker/runs_local/*/outputs/suite_normalized_artifact.json",
        "StatiBaker/runs_local_smoke/*/outputs/suite_normalized_artifact.json",
        "SensibLaw/tests/fixtures/**/*normalized_artifact*.json",
    )
    return _glob_existing(root, patterns, limit=120)


def _default_state_paths() -> list[Path]:
    root = _suite_root()
    patterns = (
        "StatiBaker/runs/*/outputs/state.json",
        "StatiBaker/runs_local/*/outputs/state.json",
        "StatiBaker/runs_local_smoke/*/outputs/state.json",
        "StatiBaker/fixtures/*/outputs/state.json",
    )
    return _glob_existing(root, patterns, limit=120)


def _default_review_packet_paths() -> list[Path]:
    root = _suite_root()
    patterns = (
        "SensibLaw/tests/fixtures/**/*review_packet*.json",
        "SensibLaw/tests/fixtures/**/*operator_review_surface*.json",
    )
    return _glob_existing(root, patterns, limit=120)


def _default_markdown_paths() -> list[Path]:
    root = _suite_root()
    paths = [
        root / "README.md",
        root / "TODO.md",
        root / "StatiBaker" / "TODO.md",
        root / "SensibLaw" / "todo.md",
        root / "SensibLaw" / "docs" / "human_tools_integration.md",
    ]
    paths.extend(sorted((root / "docs" / "planning").glob("*.md"))[:80])
    return [path for path in paths if path.exists() and path.is_file()]


def _glob_existing(root: Path, patterns: Sequence[str], *, limit: int) -> list[Path]:
    out: list[Path] = []
    seen: set[Path] = set()
    for pattern in patterns:
        for path in sorted(root.glob(pattern)):
            resolved = path.resolve()
            if resolved not in seen and path.exists() and path.is_file():
                seen.add(resolved)
                out.append(resolved)
                if len(out) >= limit:
                    return out
    return out


def _discover_json_files(root: Path, *, max_files: int, name_hints: Sequence[str]) -> list[Path]:
    if not root.exists():
        return []
    out: list[Path] = []
    for path in _walk_files(root):
        if len(out) >= max_files:
            break
        lowered = path.name.lower()
        if path.suffix.lower() == ".json" and any(hint in lowered for hint in name_hints):
            out.append(path)
    return out


def _discover_state_files(root: Path, *, max_files: int) -> list[Path]:
    if not root.exists():
        return []
    out: list[Path] = []
    for path in _walk_files(root, skip_dirs=_SKIP_DIRS - {"runs"}):
        if len(out) >= max_files:
            break
        if path.name == "state.json" and path.parent.name == "outputs":
            out.append(path)
    return out


def _iter_markdown_files(root: Path, *, max_files: int) -> list[Path]:
    if not root.exists():
        return []
    out: list[Path] = []
    for path in _walk_files(root):
        if len(out) >= max_files:
            break
        if path.suffix.lower() == ".md":
            out.append(path)
    return out


def _walk_files(root: Path, *, skip_dirs: set[str] | None = None) -> Iterable[Path]:
    if root.is_file():
        yield root
        return
    active_skip_dirs = skip_dirs or _SKIP_DIRS
    pending = [root]
    while pending:
        current = pending.pop()
        try:
            entries = sorted(current.iterdir(), key=lambda item: item.name)
        except OSError:
            continue
        for entry in entries:
            if entry.is_dir():
                if entry.name not in active_skip_dirs and not _is_site_build(entry):
                    pending.append(entry)
            elif entry.is_file():
                yield entry


def _is_site_build(path: Path) -> bool:
    parts = path.parts
    return len(parts) >= 2 and parts[-1] == "_site" and parts[-2] == "docs"


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ToolInputError(f"failed to read json: {path}", details={"path": str(path)}) from exc


def _load_bundle_records(path: Path) -> list[JsonDict]:
    if path.suffix.lower() == ".jsonl":
        records: list[JsonDict] = []
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            if not line.strip():
                continue
            record = json.loads(line)
            if isinstance(record, Mapping):
                records.append(dict(record))
        return records
    payload = _load_json(path)
    if isinstance(payload, list):
        return [dict(item) for item in payload if isinstance(item, Mapping)]
    if isinstance(payload, Mapping):
        records = payload.get("records") or payload.get("notes") or [payload]
        if isinstance(records, list):
            return [dict(item) for item in records if isinstance(item, Mapping)]
    return []


def _questions_from_artifact(artifact: Mapping[str, Any], path: Path) -> list[JsonDict]:
    out: list[JsonDict] = []
    source_system = _artifact_producer(artifact)
    artifact_id = str(artifact.get("artifact_id") or path)
    authority_class = str((artifact.get("authority") or {}).get("authority_class") or "unknown")
    source_ref = {"kind": "normalized_artifact", "path": str(path), "artifact_id": artifact_id}

    open_questions = artifact.get("open_questions")
    if isinstance(open_questions, list):
        for index, item in enumerate(open_questions):
            text = _item_text(item, ("question_text", "text", "reason", "scope"))
            if text:
                out.append(
                    _question_record(
                        source_system=source_system,
                        lane="normalized_artifact",
                        artifact_id=artifact_id,
                        item_id=_hash_parts(artifact_id, "open_questions", str(index), text),
                        status=_item_status(item) or "open",
                        pressure_kind="open_question",
                        text=text,
                        next_action=_item_next_action(item),
                        authority_class=authority_class,
                        provenance_refs=[source_ref],
                        promotion_level="typed_source",
                    )
                )

    follow = artifact.get("follow_obligation")
    if isinstance(follow, Mapping):
        text = _item_text(follow, ("scope", "trigger", "reason", "text"))
        if text:
            out.append(
                _question_record(
                    source_system=source_system,
                    lane="normalized_artifact",
                    artifact_id=artifact_id,
                    item_id=_hash_parts(artifact_id, "follow_obligation", text),
                    status=str(artifact.get("unresolved_pressure_status") or "follow_needed"),
                    pressure_kind="follow_obligation",
                    text=text,
                    next_action=str(follow.get("stop_condition") or ""),
                    authority_class=authority_class,
                    provenance_refs=[source_ref],
                    promotion_level="typed_source",
                )
            )
    return out


def _questions_from_state(state: Mapping[str, Any], path: Path) -> list[JsonDict]:
    out: list[JsonDict] = []
    date_text = str(state.get("date") or "unknown")
    artifact_id = f"statiBaker.state:{date_text}"
    source_ref = {"kind": "statiBaker_state", "path": str(path)}
    for key, pressure_kind in (("open_questions", "open_question"), ("blocked_tasks", "blocked_task"), ("alerts", "alert")):
        values = state.get(key)
        if not isinstance(values, list):
            continue
        for index, value in enumerate(values):
            text = str(value).strip()
            if not text:
                continue
            out.append(
                _question_record(
                    source_system="StatiBaker",
                    lane="compiled_state",
                    artifact_id=artifact_id,
                    item_id=_hash_parts(artifact_id, key, str(index), text),
                    status="open" if key == "open_questions" else "follow_needed",
                    pressure_kind=pressure_kind,
                    text=text,
                    next_action="review compiled state pressure",
                    authority_class="state",
                    provenance_refs=[source_ref],
                    promotion_level="typed_source",
                )
            )
    return out


def _questions_from_review_packet(packet: Mapping[str, Any], path: Path) -> list[JsonDict]:
    out: list[JsonDict] = []
    artifact_id = str(packet.get("packet_id") or packet.get("artifact_id") or path.name)
    source_ref = {"kind": "sensiblaw_review_packet", "path": str(path), "artifact_id": artifact_id}

    page_signals = packet.get("page_signals")
    if isinstance(page_signals, Mapping):
        values = page_signals.get("unresolved_questions")
        if isinstance(values, list):
            for index, value in enumerate(values):
                text = _item_text(value, ("question", "question_text", "text", "reason"))
                if text:
                    out.append(
                        _question_record(
                            source_system="SensibLaw",
                            lane="wikidata_review_packet",
                            artifact_id=artifact_id,
                            item_id=_hash_parts(artifact_id, "page_signals", str(index), text),
                            status=_item_status(value) or "open",
                            pressure_kind="open_question",
                            text=text,
                            next_action="review packet unresolved questions",
                            authority_class="review",
                            provenance_refs=[source_ref],
                            promotion_level="typed_source",
                        )
                    )

    for index, receipt in enumerate(packet.get("follow_receipts") or []):
        if not isinstance(receipt, Mapping):
            continue
        value = receipt.get("unresolved_uncertainty")
        text = _item_text(value, ("question", "question_text", "text", "reason")) if isinstance(value, Mapping) else str(value or "").strip()
        if text:
            out.append(
                _question_record(
                    source_system="SensibLaw",
                    lane="wikidata_review_packet",
                    artifact_id=artifact_id,
                    item_id=_hash_parts(artifact_id, "follow_receipts", str(index), text),
                    status="open",
                    pressure_kind="unresolved_uncertainty",
                    text=text,
                    next_action="review unresolved uncertainty receipt",
                    authority_class="review",
                    provenance_refs=[source_ref],
                    promotion_level="typed_source",
                )
            )

    reviewer_view = packet.get("reviewer_view")
    if isinstance(reviewer_view, Mapping):
        flags = reviewer_view.get("uncertainty_flags")
        if isinstance(flags, list):
            for index, flag in enumerate(flags):
                text = str(flag).strip()
                if text:
                    out.append(
                        _question_record(
                            source_system="SensibLaw",
                            lane="reviewer_view",
                            artifact_id=artifact_id,
                            item_id=_hash_parts(artifact_id, "uncertainty_flags", str(index), text),
                            status="open",
                            pressure_kind="uncertainty_flag",
                            text=text,
                            next_action=str(reviewer_view.get("smallest_next_check") or "review uncertainty flag"),
                            authority_class="review",
                            provenance_refs=[source_ref],
                            promotion_level="typed_source",
                        )
                    )
    return out


def _questions_from_todo_graph(payload: Mapping[str, Any]) -> list[JsonDict]:
    out: list[JsonDict] = []
    for item in payload.get("evaluations") or []:
        if not isinstance(item, Mapping):
            continue
        obligation = item.get("obligation")
        if not isinstance(obligation, Mapping):
            continue
        classification = str(item.get("classification") or "")
        if classification not in {"blocked", "needs_human_review", "stale", "contradicted", "partially_satisfied"}:
            continue
        text = str(obligation.get("text") or "").strip()
        if not text:
            continue
        source_path = str(obligation.get("source_path") or "")
        line_no = str(obligation.get("line_no") or "")
        out.append(
            _question_record(
                source_system="StatiBaker",
                lane="todo_graph",
                artifact_id=f"todo:{source_path}",
                item_id=str(obligation.get("obligation_id") or _hash_parts(source_path, line_no, text)),
                status=classification,
                pressure_kind="todo_follow_pressure",
                text=text,
                next_action="review TODO graph classification",
                authority_class="observer",
                provenance_refs=[{"kind": "todo_obligation", "path": source_path, "line_no": line_no}],
                promotion_level="structured_hint",
            )
        )
    return out


def _extract_markdown_hints(
    text: str,
    *,
    source_system: str,
    lane: str,
    artifact_id: str,
    source_ref: JsonDict,
    authority_class: str,
    promotion_level: str,
) -> list[JsonDict]:
    out: list[JsonDict] = []
    active_kind = ""
    active_heading = ""
    for line_no, raw_line in enumerate(text.splitlines(), start=1):
        heading = _parse_heading(raw_line)
        if heading:
            _level, heading_text = heading
            active_kind = _heading_pressure_kind(heading_text)
            active_heading = heading_text
            continue
        stripped = raw_line.strip()
        if not stripped:
            continue
        query_kind = _query_pressure_kind(stripped)
        pressure_kind = query_kind or active_kind
        if not pressure_kind:
            continue
        item_text = _strip_markdown_marker(stripped)
        if not item_text:
            continue
        item_promotion = "candidate_hint" if query_kind else promotion_level
        out.append(
            _question_record(
                source_system=source_system,
                lane=lane,
                artifact_id=artifact_id,
                item_id=_hash_parts(artifact_id, str(line_no), item_text),
                status="open",
                pressure_kind=pressure_kind,
                text=item_text,
                next_action="review structured Markdown hint",
                authority_class=authority_class,
                provenance_refs=[{**source_ref, "line_no": line_no, "heading": active_heading}],
                promotion_level=item_promotion,
            )
        )
    return out


def _parse_heading(line: str) -> tuple[int, str] | None:
    stripped = line.strip()
    if not stripped.startswith("#"):
        return None
    level = 0
    for char in stripped:
        if char == "#":
            level += 1
            continue
        break
    if level < 1 or level > 6:
        return None
    if len(stripped) <= level or stripped[level] != " ":
        return None
    heading = stripped[level:].strip()
    return (level, heading) if heading else None


def _heading_pressure_kind(heading: str) -> str:
    normalized = _normalize_words(heading)
    for token, kind in _HEADING_HINTS:
        if token in normalized:
            return kind
    return ""


def _query_pressure_kind(line: str) -> str:
    lowered = line.lower()
    if ":itir-query:" in lowered or ":sl-query:" in lowered:
        return "query_intent"
    if lowered.endswith("?") and ("todo" in lowered or "question" in lowered):
        return "open_question"
    return ""


def _strip_markdown_marker(line: str) -> str:
    stripped = line.strip()
    for marker in ("- ", "* ", "+ "):
        if stripped.startswith(marker):
            stripped = stripped[2:].strip()
            break
    if stripped[:1].isdigit():
        dot = stripped.find(". ")
        if dot > 0 and stripped[:dot].isdigit():
            stripped = stripped[dot + 2 :].strip()
    for checkbox in ("[ ] ", "[x] ", "[X] "):
        if stripped.startswith(checkbox):
            stripped = stripped[4:].strip()
            break
    return stripped


def _todo_graph_payload(payload: Mapping[str, Any]) -> JsonDict | None:
    repo_root = _resolve_path(str(payload.get("repo_root") or _suite_root()))
    todo_paths = [_resolve_path(path) for path in _path_list(payload, "todo_paths")]
    if not todo_paths:
        todo_paths = [
            path
            for path in (
                repo_root / "TODO.md",
                repo_root / "StatiBaker" / "TODO.md",
                repo_root / "SensibLaw" / "todo.md",
            )
            if path.exists()
        ]
    try:
        module = _load_stati_baker_todo_graph()
        if not payload.get("evaluate_todos", False):
            return _fallback_todo_graph(module, repo_root, todo_paths)
        try:
            return module.analyze_repo_todos(repo_root, todo_paths=todo_paths)
        except Exception:
            return _fallback_todo_graph(module, repo_root, todo_paths)
    except Exception:
        return None


def _fallback_todo_graph(module, repo_root: Path, todo_paths: Sequence[Path]) -> JsonDict:
    obligations: list[JsonDict] = []
    for path in todo_paths:
        if path.exists():
            obligations.extend(module.parse_todo_file(path, repo_root=repo_root))
    evaluations = [
        {
            "obligation": obligation,
            "classification": "needs_human_review"
            if str(obligation.get("state") or "") != "checked_complete"
            else "likely_complete",
            "reason_codes": ["todo_graph_fallback_no_evaluation"],
            "predicates": [],
            "evidence_links": [],
        }
        for obligation in obligations
    ]
    return {
        "version": "todo_graph_v1",
        "fallback": True,
        "repo_root": str(repo_root),
        "todo_files": [str(path) for path in todo_paths],
        "obligations": obligations,
        "evaluations": evaluations,
        "completion_candidates": [],
        "alignment": {},
    }


def _load_stati_baker_todo_graph():
    target = _suite_root() / "StatiBaker" / "sb" / "todo_graph.py"
    module_name = "_itir_stati_baker_todo_graph"
    spec = importlib.util.spec_from_file_location(module_name, target)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load StatiBaker todo_graph")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _join_artifacts(artifacts: Sequence[Mapping[str, Any]]) -> JsonDict | None:
    target = _suite_root() / "normalized_artifact_join.py"
    if not target.exists():
        return None
    try:
        module_name = "_itir_normalized_artifact_join"
        spec = importlib.util.spec_from_file_location(module_name, target)
        if spec is None or spec.loader is None:
            return None
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module.join_suite_normalized_artifacts(artifacts)
    except Exception as exc:
        return {
            "schema_version": "itir.normalized.artifact.join.unavailable.v1",
            "error": str(exc),
        }


def _filter_questions(questions: list[JsonDict], payload: Mapping[str, Any]) -> list[JsonDict]:
    producer = str(payload.get("producer") or "").strip()
    status = str(payload.get("status") or "").strip()
    promotion_level = str(payload.get("promotion_level") or "").strip()
    filtered: list[JsonDict] = []
    for item in questions:
        if producer and str(item.get("source_system") or "") != producer:
            continue
        if status and str(item.get("status") or "") != status:
            continue
        if promotion_level and str(item.get("promotion_level") or "") != promotion_level:
            continue
        filtered.append(item)
    return filtered


def _question_counts(questions: Sequence[Mapping[str, Any]]) -> JsonDict:
    return {
        "total": len(questions),
        "by_source_system": dict(sorted(Counter(str(item.get("source_system") or "unknown") for item in questions).items())),
        "by_status": dict(sorted(Counter(str(item.get("status") or "unknown") for item in questions).items())),
        "by_pressure_kind": dict(sorted(Counter(str(item.get("pressure_kind") or "unknown") for item in questions).items())),
        "by_promotion_level": dict(sorted(Counter(str(item.get("promotion_level") or "unknown") for item in questions).items())),
    }


def _question_record(
    *,
    source_system: str,
    lane: str,
    artifact_id: str,
    item_id: str,
    status: str,
    pressure_kind: str,
    text: str,
    next_action: str,
    authority_class: str,
    provenance_refs: list[JsonDict],
    promotion_level: str,
) -> JsonDict:
    return {
        "schema_version": "itir.open_question.item.v1",
        "source_system": source_system,
        "lane": lane,
        "artifact_id": artifact_id,
        "item_id": item_id,
        "status": status,
        "pressure_kind": pressure_kind,
        "question_text_or_reason": text,
        "next_action": next_action,
        "authority_class": authority_class,
        "promotion_level": promotion_level,
        "provenance_refs": provenance_refs,
    }


def _artifact_producer(artifact: Mapping[str, Any]) -> str:
    anchor = artifact.get("provenance_anchor")
    if isinstance(anchor, Mapping) and anchor.get("source_system"):
        return str(anchor["source_system"])
    summary = artifact.get("summary")
    if isinstance(summary, Mapping) and summary.get("producer"):
        return str(summary["producer"])
    return "unknown"


def _looks_like_sb_state(payload: Mapping[str, Any]) -> bool:
    return isinstance(payload.get("date"), str) and any(key in payload for key in ("open_questions", "blocked_tasks", "alerts"))


def _item_text(item: Any, keys: Sequence[str]) -> str:
    if isinstance(item, Mapping):
        for key in keys:
            value = item.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        return ""
    return str(item).strip()


def _item_status(item: Any) -> str:
    if isinstance(item, Mapping):
        value = item.get("status") or item.get("resolution_status") or item.get("review_status")
        return str(value).strip() if value else ""
    return ""


def _item_next_action(item: Any) -> str:
    if isinstance(item, Mapping):
        value = item.get("next_action") or item.get("smallest_next_check") or item.get("recommended_follow_target")
        return str(value).strip() if value else ""
    return ""


def _record_hash(record: Mapping[str, Any], raw_key: str, hash_key: str) -> str:
    existing = record.get(hash_key)
    if isinstance(existing, str) and existing.strip():
        return existing.strip()
    raw = record.get(raw_key)
    return _hash_text(str(raw)) if raw is not None else ""


def _record_text(record: Mapping[str, Any]) -> str:
    for key in ("markdown", "content", "text", "note_text", "body"):
        value = record.get(key)
        if isinstance(value, str) and value.strip():
            return value
    return ""


def _safe_rel(path: Path, root: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except ValueError:
        return str(path)


def _int(value: Any, default: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return max(1, parsed)


def _normalize_words(text: str) -> str:
    chars = [char.lower() if char.isalnum() else " " for char in text]
    return " ".join("".join(chars).split())


def _hash_text(text: str) -> str:
    return "sha256:" + sha256(text.encode("utf-8")).hexdigest()


def _hash_parts(*parts: str) -> str:
    return _hash_text("|".join(parts))
