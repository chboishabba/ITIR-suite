"""Bounded reference-only candidate packet projection from canonical structurer SQLite."""
from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from pathlib import Path
from typing import Any, Mapping, Sequence

from scripts.canonical_candidate_ledger import canonical_archive_path

VERSION = "itir.pnf.work_packet.v1"
REQUIRED = {
    "message_id", "canonical_thread_id", "platform", "account_id", "ts",
    "role", "text", "title", "source_id", "source_thread_id",
    "source_message_id", "source_path", "source_bucket", "provenance_json",
    "node_id", "parent_node_id", "branch_membership", "tool_kind",
    "citation_token", "filename", "mime_type", "asset_pointer",
    "body_storage_ref", "source_scope", "visibility",
}
MAX_MESSAGES = 200
MAX_CHARS = 100000
MAX_PACKET_CHARS = 100000
MAX_THREADS = 8
PATTERN = re.compile(r"\b(?:lemma|theorem|proof|formal|agda|lean|gap|TODO|blocked|implement|PR\s*#\d+)\b", re.I)


def _json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _digest(value: Any) -> str:
    return hashlib.sha256(str(value).encode("utf-8")).hexdigest()


def postgres_reference_adapter(*_args: Any, **_kwargs: Any) -> None:
    """Explicit stub: no PostgreSQL connection, persistence or implicit fallback."""
    raise NotImplementedError("PostgreSQL reference materialisation unavailable in v1")


def _policy(policy: Mapping[str, Any] | None) -> tuple[int, int, int]:
    policy = policy or {}
    if set(policy) - {"max_messages", "max_chars", "packet_max_chars"}:
        raise ValueError("unknown span policy field")
    values = tuple(policy.get(k, default) for k, default in (
        ("max_messages", 40), ("max_chars", 24000), ("packet_max_chars", 24000)
    ))
    if any(type(v) is not int or v < 1 for v in values):
        raise ValueError("span policy must contain positive integers")
    if values[0] > MAX_MESSAGES or values[1] > MAX_CHARS or values[2] > MAX_PACKET_CHARS:
        raise ValueError("span policy exceeds hard ceiling")
    return values


def build_work_packet(
    proposals: Sequence[Mapping[str, Any]], *,
    archive_db: str | None = None,
    span_policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    max_messages, max_chars, packet_max = _policy(span_policy)
    if not isinstance(proposals, (list, tuple)) or not 1 <= len(proposals) <= MAX_THREADS:
        raise ValueError("proposals must contain 1..8 thread selectors")
    path = canonical_archive_path(archive_db)
    if not path.is_file():
        raise FileNotFoundError("canonical archive missing")
    packets: list[dict[str, Any]] = []
    with sqlite3.connect(f"file:{path.resolve()}?mode=ro", uri=True) as db:
        cols = {r[1] for r in db.execute("PRAGMA table_info(messages)")}
        if not REQUIRED <= cols:
            raise RuntimeError("canonical messages schema mismatch")
        for proposal in proposals:
            if not isinstance(proposal, Mapping):
                raise ValueError("proposal must be an object")
            if set(proposal) - {
                "canonical_thread_id", "task_atom", "formal_gap_receipts",
                "repo_receipts", "pnf_receipts", "evidence_refs",
            }:
                raise ValueError("unknown proposal field")
            thread = proposal.get("canonical_thread_id")
            task = proposal.get("task_atom")
            if not isinstance(thread, str) or not thread.strip() or not isinstance(task, str) or not task.strip():
                raise ValueError("explicit thread and task required")
            evidence: dict[str, list[str]] = {}
            for key in ("formal_gap_receipts", "repo_receipts", "pnf_receipts", "evidence_refs"):
                value = proposal.get(key, [])
                if not isinstance(value, list) or any(not isinstance(v, str) or not v for v in value):
                    raise ValueError("receipt refs must be arrays of nonempty strings")
                evidence[key] = sorted(set(value))
            total, total_chars = db.execute(
                "SELECT COUNT(*), COALESCE(SUM(LENGTH(text)),0) FROM messages WHERE canonical_thread_id=?",
                (thread,),
            ).fetchone()
            if not total:
                raise ValueError("canonical thread not found")
            # Tail-first window, without loading the entire transcript.
            rows = db.execute(
                """SELECT message_id,source_message_id,node_id,ts,text
                   FROM messages WHERE canonical_thread_id=?
                   ORDER BY ts DESC,message_id DESC LIMIT ?""",
                (thread, max_messages),
            ).fetchall()
            selected = []
            selected_chars = 0
            for message_id, source_id, node_id, ts, body in rows:
                body = str(body or "")
                if selected_chars + len(body) > max_chars:
                    break
                selected.append((message_id, source_id, node_id, ts, body))
                selected_chars += len(body)
            if not selected:
                raise ValueError("empty selection under span policy")
            selected.reverse()
            refs = [{
                "message_id": str(mid), "source_message_id": sid,
                "node_id": node, "ts": ts, "body_sha256": _digest(body),
                "archive_locator": f"sqlite:{path.resolve()}#messages/{mid}",
            } for mid, sid, node, ts, body in selected]
            units = []
            for ref, (_, _, _, _, body) in zip(refs, selected):
                # Candidate-only lexical signals, not a substitute for SLR parsing.
                tags = sorted({m.group(0).lower() for m in PATTERN.finditer(body)})[:8]
                if tags:
                    units.append({"source_message_id": ref["message_id"],
                                  "candidate_kinds": tags, "status": "unverified"})
            truncation = {
                "thread_tail_truncated": total > len(rows),
                "span_char_truncated": len(selected) < len(rows),
                "total_messages": total, "selected_messages": len(selected),
                "total_chars": total_chars, "selected_chars": selected_chars,
                "packet_budget_truncated": False, "derived_units_dropped": 0,
            }
            packet = {
                "canonical_thread_id": thread, "task_atom": task,
                "source_refs": refs, "derived_units": units,
                "evidence_receipts": evidence, "truncation_receipt": truncation,
                "reference_projection": {
                    "adapter": "local_reference_only",
                    "postgres_adapter": "unavailable_stub",
                    "source_count": len(refs), "raw_body_persisted": False,
                },
                "missing_evidence": ["producer_verified_pnf_parse", "postgres_materialisation"],
            }
            packet["packet_id"] = _digest(_json({
                "thread": thread, "task": task, "refs": refs,
                "evidence": evidence, "policy": [max_messages, max_chars, packet_max],
            }))
            packets.append(packet)
    result = {
        "version": VERSION, "authority": "candidate_evidence_only",
        "canonical_truth_mutated": False, "promotion": False,
        "packets": packets,
    }
    # Explicitly shrink derived units from the tail; source refs remain intact.
    while len(_json(result)) > packet_max:
        eligible = [p for p in packets if p["derived_units"]]
        if not eligible:
            raise ValueError("packet exceeds budget even without derived units")
        largest = max(eligible, key=lambda p: len(p["derived_units"]))
        largest["derived_units"].pop()
        largest["truncation_receipt"]["packet_budget_truncated"] = True
        largest["truncation_receipt"]["derived_units_dropped"] += 1
    return result
