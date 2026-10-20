"""Metadata-first, evidence-gated AO frontier selection. Never bulk-read message bodies."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sqlite3
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from .comparison_tools import build_envelope, compare_observations, score_coherence
from .pnf_work_packet_provider import canonical_archive_path

SCHEMA = "itir.ao.frontier_evidence.v1"
MAX_EVALUATED = 64
STATES = frozenset({"candidate", "active_waiting", "processing", "merged", "parked", "retired"})
TRANSITIONS = {
    None: {"candidate"},
    "candidate": {"active_waiting", "processing", "merged", "parked", "retired"},
    "active_waiting": {"processing", "parked", "retired"},
    "processing": {"active_waiting", "merged", "parked", "retired"},
    "parked": {"candidate", "retired"},
    "merged": {"candidate"},
    "retired": {"candidate"},
}


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


def _ledger_fn() -> Callable[..., dict[str, Any]]:
    """Load the existing authoritative ledger from the repository, including isolated MCP cwd."""
    path = Path(__file__).resolve().parents[3] / "scripts" / "canonical_candidate_ledger.py"
    spec = importlib.util.spec_from_file_location("itir_frontier_canonical_ledger", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("canonical candidate ledger unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.select_candidate_ledger


def _read_metadata(archive: Path) -> list[dict[str, Any]]:
    if not archive.is_file():
        raise FileNotFoundError(f"canonical archive unavailable: {archive}")
    with sqlite3.connect(archive.resolve().as_uri() + "?mode=ro", uri=True) as db:
        cols = {row[1] for row in db.execute("PRAGMA table_info(messages)")}
        needed = {"canonical_thread_id", "source_thread_id", "account_id", "platform", "ts", "role"}
        if not needed <= cols:
            raise ValueError("canonical metadata schema mismatch")
        rows = db.execute(
            """SELECT canonical_thread_id, MIN(source_thread_id), COUNT(*),
                      MIN(ts), MAX(ts),
                      SUM(CASE WHEN role='user' THEN 1 ELSE 0 END),
                      SUM(CASE WHEN role='assistant' THEN 1 ELSE 0 END),
                      COUNT(DISTINCT source_thread_id)
               FROM messages
               WHERE account_id='main' AND platform='chatgpt'
                 AND canonical_thread_id IS NOT NULL
               GROUP BY canonical_thread_id
               ORDER BY MAX(ts) DESC, canonical_thread_id"""
        )
        return [
            {"canonical_thread_id": str(tid), "source_thread_id": source,
             "message_count": count, "first_ts": first, "last_ts": last,
             "user_count": users, "assistant_count": assistants,
             "source_id_count": source_count}
            for tid, source, count, first, last, users, assistants, source_count in rows
        ]


def _init_roster(db: sqlite3.Connection) -> None:
    db.execute("""CREATE TABLE IF NOT EXISTS frontier_roster (
        canonical_thread_id TEXT PRIMARY KEY, source_thread_id TEXT,
        state TEXT NOT NULL, last_receipt_id TEXT NOT NULL)""")
    db.execute("""CREATE TABLE IF NOT EXISTS frontier_transitions (
        receipt_id TEXT PRIMARY KEY, canonical_thread_id TEXT NOT NULL,
        previous_state TEXT, next_state TEXT NOT NULL, reason TEXT NOT NULL,
        source_thread_id TEXT, evidence_digest TEXT NOT NULL)""")


def transition_roster(
    roster_db: str, canonical_thread_id: str, source_thread_id: str | None,
    next_state: str, reason: str, evidence_refs: Sequence[str] = (),
) -> dict[str, Any]:
    """Idempotent, receipt-only roster transition; no corpus writes."""
    if next_state not in STATES or not canonical_thread_id or not reason:
        raise ValueError("invalid roster transition")
    path = Path(roster_db).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as db:
        _init_roster(db)
        row = db.execute(
            "SELECT state, source_thread_id FROM frontier_roster WHERE canonical_thread_id=?",
            (canonical_thread_id,),
        ).fetchone()
        previous = row[0] if row else None
        if row and row[1] and source_thread_id and row[1] != source_thread_id:
            raise ValueError("source_thread_id mapping conflict")
        if previous != next_state and next_state not in TRANSITIONS[previous]:
            raise ValueError(f"forbidden roster transition: {previous} -> {next_state}")
        receipt = {"canonical_thread_id": canonical_thread_id, "source_thread_id": source_thread_id,
                   "previous_state": previous, "next_state": next_state, "reason": reason,
                   "evidence_digest": _digest(sorted(set(evidence_refs)))}
        receipt_id = _digest(receipt)
        db.execute(
            "INSERT OR IGNORE INTO frontier_transitions VALUES (?,?,?,?,?,?,?)",
            (receipt_id, canonical_thread_id, previous, next_state, reason,
             source_thread_id, receipt["evidence_digest"]),
        )
        db.execute("""INSERT INTO frontier_roster VALUES (?,?,?,?)
                      ON CONFLICT(canonical_thread_id) DO UPDATE SET
                      source_thread_id=excluded.source_thread_id,
                      state=excluded.state, last_receipt_id=excluded.last_receipt_id""",
                   (canonical_thread_id, source_thread_id or (row[1] if row else None),
                    next_state, receipt_id))
    return {"receipt_id": receipt_id, **receipt}


def build_frontier(
    *, archive_db: str | None = None,
    evidence: Sequence[Mapping[str, Any]] = (),
    roster_db: str | None = None,
    max_evaluated: int = 24, max_proposals: int = 4,
    gap_evaluator: Callable[[str, str, Mapping[str, Any]], Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """Select only explicitly evidenced threads. Metadata enumeration never selects text."""
    if type(max_evaluated) is not int or not 1 <= max_evaluated <= MAX_EVALUATED:
        raise ValueError("max_evaluated must be 1..64")
    if type(max_proposals) is not int or not 1 <= max_proposals <= 4:
        raise ValueError("max_proposals must be 1..4")
    if len(evidence) > MAX_EVALUATED:
        raise ValueError("explicit evidence exceeds 64 rows")
    archive = canonical_archive_path(archive_db)
    metadata = _read_metadata(archive)
    by_id = {m["canonical_thread_id"]: m for m in metadata}
    evidence_by_id: dict[str, Mapping[str, Any]] = {}
    for item in evidence:
        tid = str(item.get("canonical_thread_id") or "")
        if not tid or tid in evidence_by_id:
            raise ValueError("evidence requires unique canonical_thread_id")
        evidence_by_id[tid] = item
    # Prioritize explicitly evidenced candidates; metadata-only rows are never promoted.
    eligible_ids = sorted(
        (tid for tid in evidence_by_id if tid in by_id),
        key=lambda tid: (-int(bool(evidence_by_id[tid].get("explicit_promotion"))),
                         -len(evidence_by_id[tid].get("formal_gap_receipts") or []),
                         -len(evidence_by_id[tid].get("repo_receipts") or []), tid),
    )
    selected_ids = eligible_ids[:max_evaluated]
    abstentions: list[dict[str, Any]] = []
    gap_receipts: list[dict[str, Any]] = []
    rows: list[dict[str, Any]] = []
    for tid in selected_ids:
        source = evidence_by_id[tid]
        meta = by_id[tid]
        refs = [str(ref) for ref in source.get("evidence_refs", [])]
        row = {
            "canonical_thread_id": tid, "task_atom": str(source.get("task_atom") or "").strip(),
            "kind": str(source.get("kind") or "unclassified"),
            "formal_gap_receipts": list(source.get("formal_gap_receipts") or []),
            "repo_receipts": list(source.get("repo_receipts") or []),
            "pnf_receipts": list(source.get("pnf_receipts") or []),
            "explicit_promotion": source.get("explicit_promotion") is True,
            "evidence_refs": sorted(set(refs + ["canonical:thread:" + tid])),
            "outstanding_operation_receipt": source.get("outstanding_operation_receipt"),
        }
        artifact = source.get("formal_artifact")
        if artifact:
            if not isinstance(artifact, str) or not artifact.strip():
                raise ValueError("formal_artifact must be a path string")
            if gap_evaluator is None:
                abstentions.append({"canonical_thread_id": tid, "reason": "gap_evaluator_unavailable"})
            else:
                # Evaluator is injected: real ExactGapComparator adapter must enforce per-thread budgets.
                try:
                    gap = dict(gap_evaluator(tid, artifact, meta))
                    receipt = "gap:" + _digest({"thread": tid, "artifact": artifact, "result": gap})
                    row["formal_gap_receipts"].append(receipt)
                    gap_receipts.append({"canonical_thread_id": tid, "formal_artifact": artifact,
                                         "receipt_id": receipt, "result_digest": _digest(gap),
                                         "source_thread_id": meta["source_thread_id"]})
                except Exception as exc:
                    abstentions.append({"canonical_thread_id": tid, "reason": "gap_evaluator_failed",
                                        "error_type": type(exc).__name__})
        rows.append(row)
    for tid in evidence_by_id:
        if tid not in by_id:
            abstentions.append({"canonical_thread_id": tid, "reason": "canonical_thread_missing"})
    # Pairwise comparison uses only task atoms / external evidence tags, never transcript bodies.
    comparisons = []
    for i, left in enumerate(rows):
        for right in rows[i + 1:]:
            if len(comparisons) >= 128:
                break
            obs_left = {"obs_id": left["canonical_thread_id"], "text": left["task_atom"],
                        "anchor_refs": {"canonical_thread_id": left["canonical_thread_id"]}}
            obs_right = {"obs_id": right["canonical_thread_id"], "text": right["task_atom"],
                         "anchor_refs": {"canonical_thread_id": right["canonical_thread_id"]}}
            comparison = compare_observations({"left": obs_left, "right": obs_right})
            coherence = score_coherence({"observations": [obs_left, obs_right]})
            envelope = build_envelope({"left": obs_left, "right": obs_right, "comparison": comparison})
            comparisons.append({"left": left["canonical_thread_id"],
                                "right": right["canonical_thread_id"],
                                "similarity": comparison["similarity"],
                                "coherence": coherence["coherence"],
                                "envelope_digest": _digest(envelope),
                                "authority": "candidate_similarity_only"})
        if len(comparisons) >= 128:
            break
    ledger = _ledger_fn()(rows, archive_db=str(archive), max_proposals=max_proposals)
    roster = []
    for decision in ledger["decisions"]:
        tid = decision["canonical_thread_id"]
        meta = by_id[tid]
        if meta["source_id_count"] != 1:
            abstentions.append({"canonical_thread_id": tid, "reason": "ambiguous_source_thread_mapping"})
        state = {"admit": "candidate", "park": "parked", "retire": "retired", "merge": "merged"}[decision["decision"]]
        if roster_db:
            roster.append(transition_roster(roster_db, tid, meta["source_thread_id"],
                                            state, decision["reason"], decision["evidence_refs"]))
    return {
        "schema": SCHEMA, "authority": "candidate_evidence_only",
        "dispatch_performed": False, "archive_ref": str(archive),
        "enumerated_threads": len(metadata), "evaluated_threads": len(rows),
        "proposals": [{**p, "source_thread_id": by_id[p["canonical_thread_id"]]["source_thread_id"]}
                      for p in ledger["proposals"]],
        "decisions": ledger["decisions"], "evidence_rows": rows,
        "comparison_receipts": comparisons, "gap_receipts": gap_receipts,
        "abstentions": abstentions, "roster": roster,
        "source_mapping": [{"canonical_thread_id": tid,
                            "source_thread_id": by_id[tid]["source_thread_id"],
                            "mapping_ambiguous": by_id[tid]["source_id_count"] != 1}
                           for tid in selected_ids],
        "truncation": {"explicit_candidates": len(evidence_by_id),
                       "evaluated": len(rows), "max_evaluated": max_evaluated,
                       "candidate_limit_hit": len(eligible_ids) > max_evaluated,
                       "pairwise_limit_hit": len(rows) * (len(rows) - 1) // 2 > 128,
                       "metadata_only_not_evaluated": len(metadata) - len(selected_ids)},
        "comparison_authority": "candidate_only_not_merge_proof",
    }
