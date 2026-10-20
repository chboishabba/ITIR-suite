"""Canonical graph handoff: full-span bounded selection and governed read-only review.

The archive is opened mode=ro. Only reference digests, token offsets and
receipts leave this module; no raw transcript is persisted or returned.
"""
from __future__ import annotations

from collections import deque
from functools import lru_cache
import hashlib
import heapq
import json
import re
import sqlite3
import sys
from pathlib import Path
from typing import Any, Mapping

from .pnf_work_packet_provider import REQUIRED, canonical_archive_path

REGPT_COLUMNS = frozenset(("conversation_id", "message_index", "author", "content", "create_time"))

VERSION = "itir.pnf.governed_handoff.v1"
VIEW_VERSION = "itir.archive.thread_view.v1"
OP_VERSION = "itir.ao.operation_review.v1"
MAX_SELECTED = 80
MAX_SCAN = 1000000
MAX_PACKET = 100000
TOKEN_RE = re.compile(r"[a-zA-Z][a-zA-Z0-9_]*")
SIGNALS = frozenset(("lemma", "theorem", "proof", "agda", "lean", "gap",
                     "blocked", "fixed", "commit", "merged", "pr", "todo",
                     "formal", "implement", "receipt", "failed", "verified"))
AMBIGUOUS = frozenset(("async_starting", "commit_unknown", "unknown", "pending"))


def _encoded(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


@lru_cache(maxsize=1)
def _sensiblaw_tokenizer():
    """Load the supported SensibLaw public interface, never a private parser."""
    suite_root = Path(__file__).resolve().parents[3]
    producer = suite_root / "SensibLaw"
    if producer.is_dir() and str(producer) not in sys.path:
        sys.path.insert(0, str(producer))
    try:
        from sensiblaw.interfaces.shared_reducer import tokenize_canonical_with_spans
    except ImportError:
        return None
    return tokenize_canonical_with_spans


def _lexical_spans(body: str, words: frozenset[str]) -> list[dict[str, Any]]:
    """Public producer token spans only; unavailable producer means abstention."""
    tokenize = _sensiblaw_tokenizer()
    if tokenize is None:
        return []
    return [{"kind": token.lower(), "start": start, "end": end,
             "authority": "sensiblaw_public_token_span_candidate"}
            for token, start, end in tokenize(body)
            if token.lower() in words][:12]


def _ref(row: sqlite3.Row, path: Path) -> dict[str, Any]:
    body = str(row["text"] or "")
    return {
        "message_id": str(row["message_id"]),
        "source_message_id": row["source_message_id"],
        "node_id": row["node_id"],
        "parent_node_id": row["parent_node_id"],
        "branch_membership": row["branch_membership"],
        "source_thread_id": row["source_thread_id"],
        "lineage_status": "exact_graph" if row["node_id"] is not None and row["parent_node_id"] is not None else "unavailable_compressed_archive",
        "ts": row["ts"], "role": row["role"],
        "body_sha256": _hash(body),
        "archive_locator": f"sqlite:{path.resolve()}#messages/{row['message_id']}",
    }


def _validated_proposal(proposal: Mapping[str, Any]) -> tuple[str, str, dict[str, list[str]]]:
    allowed = {"canonical_thread_id", "task_atom", "formal_gap_receipts",
               "repo_receipts", "pnf_receipts", "evidence_refs"}
    if not isinstance(proposal, Mapping) or set(proposal) - allowed:
        raise ValueError("invalid proposal fields")
    thread, task = proposal.get("canonical_thread_id"), proposal.get("task_atom")
    if not isinstance(thread, str) or not thread.strip() or not isinstance(task, str) or not task.strip():
        raise ValueError("explicit canonical_thread_id and task_atom required")
    evidence = {}
    for key in ("formal_gap_receipts", "repo_receipts", "pnf_receipts", "evidence_refs"):
        refs = proposal.get(key, [])
        if not isinstance(refs, list) or any(not isinstance(r, str) or not r for r in refs):
            raise ValueError("evidence receipts must be arrays of nonempty strings")
        evidence[key] = sorted(set(refs))
    return thread, task, evidence


def governed_handoff(
    proposal: Mapping[str, Any], *, archive_db: str | None = None,
    max_selected: int = 24, max_packet_chars: int = 24000,
    child_thread_id: str | None = None,
    operation_status: str = "not_requested",
) -> dict[str, Any]:
    """Inspect the entire predecessor with streaming selection; never dispatch."""
    if type(max_selected) is not int or not 2 <= max_selected <= MAX_SELECTED:
        raise ValueError("max_selected must be 2..80")
    if type(max_packet_chars) is not int or not 1000 <= max_packet_chars <= MAX_PACKET:
        raise ValueError("max_packet_chars must be 1000..100000")
    if not isinstance(operation_status, str) or not operation_status.strip():
        raise ValueError("explicit operation_status required")
    if child_thread_id is not None and (not isinstance(child_thread_id, str) or not child_thread_id.strip()):
        raise ValueError("invalid child_thread_id")
    thread, task, evidence = _validated_proposal(proposal)
    path = canonical_archive_path(archive_db)
    if not path.is_file():
        raise FileNotFoundError("canonical archive unavailable")
    task_words = frozenset(m.group().lower() for m in TOKEN_RE.finditer(task))
    words = task_words | SIGNALS
    # Retain newest two rows unconditionally; rank remaining rows by task matches
    # and formal evidence, with a deterministic chronology tie-break.
    tail: deque[tuple[int, dict[str, Any], list[dict[str, Any]]]] = deque(maxlen=2)
    ranked: list[tuple[int, int, dict[str, Any], list[dict[str, Any]]]] = []
    total = 0
    total_chars = 0
    with sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True) as db:
        db.row_factory = sqlite3.Row
        cols = {r[1] for r in db.execute("PRAGMA table_info(messages)")}
        if REQUIRED <= cols:
            cursor = db.execute(
                """SELECT message_id,source_message_id,node_id,parent_node_id,
                          branch_membership,source_thread_id,ts,role,text
                   FROM messages WHERE canonical_thread_id=?
                   ORDER BY ts ASC,message_id ASC""", (thread,),
            )
            archive_schema = "canonical_messages"
        elif REGPT_COLUMNS <= cols:
            # Historical re-gpt rows contain chronological message coordinates,
            # not mapping node IDs or graph parent edges. NULL means unknown.
            cursor = db.execute(
                """SELECT conversation_id || ':' || message_index || ':' || author AS message_id,
                          message_key AS source_message_id,
                          NULL AS node_id, NULL AS parent_node_id,
                          NULL AS branch_membership,
                          conversation_id AS source_thread_id,
                          create_time AS ts, author AS role, content AS text
                   FROM messages WHERE conversation_id=?
                   ORDER BY message_index ASC, author ASC""", (thread,),
            ) if "message_key" in cols else db.execute(
                """SELECT conversation_id || ':' || message_index || ':' || author AS message_id,
                          NULL AS source_message_id,
                          NULL AS node_id, NULL AS parent_node_id,
                          NULL AS branch_membership,
                          conversation_id AS source_thread_id,
                          create_time AS ts, author AS role, content AS text
                   FROM messages WHERE conversation_id=?
                   ORDER BY message_index ASC, author ASC""", (thread,),
            )
            archive_schema = "regpt_compressed_messages"
        else:
            raise RuntimeError("unsupported archive messages schema; no inferred graph projection")
        for row in cursor:
            total += 1
            if total > MAX_SCAN:
                raise ValueError("thread exceeds hard scan ceiling; partition required")
            body = str(row["text"] or "")
            total_chars += len(body)
            source = _ref(row, path)
            spans = _lexical_spans(body, words)
            # Weight exact task words higher than generic proof vocabulary.
            score = sum(4 if item["kind"] in task_words else 1 for item in spans)
            entry = (total, source, spans)
            tail.append(entry)
            if score:
                ranked_item = (score, total, source, spans)
                if len(ranked) < max_selected:
                    heapq.heappush(ranked, ranked_item)
                elif (score, total) > ranked[0][:2]:
                    heapq.heapreplace(ranked, ranked_item)
    if not total:
        raise ValueError("canonical predecessor thread not found")
    chosen = {entry[1]["message_id"]: entry for entry in tail}
    for _, index, source, spans in ranked:
        chosen.setdefault(source["message_id"], (index, source, spans))
    ordered = sorted(chosen.values(), key=lambda item: item[0])
    # Rank top selected, but reserve the two most recent decisions.
    if len(ordered) > max_selected:
        mandatory = {entry[1]["message_id"] for entry in tail}
        ranked_rest = sorted(
            (entry for entry in ordered if entry[1]["message_id"] not in mandatory),
            key=lambda entry: (
                -sum(4 if span["kind"] in task_words else 1 for span in entry[2]),
                -entry[0],
            ),
        )[:max_selected - len(mandatory)]
        ordered = sorted([*tail, *ranked_rest], key=lambda entry: entry[0])
    refs = [source for _, source, _ in ordered]
    candidates = [
        {"message_id": source["message_id"], "spans": spans,
         "status": "lexical_candidate_only", "semantic_pnf": "abstained"}
        for _, source, spans in ordered if spans
    ]
    packet = {
        "version": VERSION,
        "canonical_thread_id": thread,
        "child_thread_id": child_thread_id,
        "task_atom": task,
        "source_refs": refs,
        "pnf_candidates": candidates,
        "producer_receipt": {"interface": "sensiblaw.interfaces.shared_reducer.tokenize_canonical_with_spans",
                             "available": _sensiblaw_tokenizer() is not None,
                             "fallback": "abstain_no_parser_authority" if _sensiblaw_tokenizer() is None else None},
        "evidence_receipts": evidence,
        "lineage_receipt": {
            "parent_thread_id": thread, "child_thread_id": child_thread_id,
            "relationship": "proposed_not_created",
            "node_parent_pointers_preserved": archive_schema == "canonical_messages",
            "status": "exact_graph_coordinates_unavailable_hold" if archive_schema == "regpt_compressed_messages" else "source_graph_coordinates_present",
            "archive_schema": archive_schema,
        },
        "span_receipt": {
            "policy": "full_thread_stream_task_rank_plus_last_two",
            "total_messages": total, "total_chars": total_chars,
            "selected_messages": len(refs), "omitted_messages": total - len(refs),
            "full_thread_scanned": True, "first_30000_char_cutoff": False,
            "tail_anchor_count": min(2, total),
            "packet_units_dropped": 0, "packet_truncated": False,
        },
        "governance": operation_review({"operation_status": operation_status}),
        "semantic_pnf_execution": {
            "status": "abstained_producer_not_executed",
            "producer": "re_gpt.pnf_compiler.PnfFleetCompiler -> sensiblaw-world-compiler",
            "coverage": "not_established",
            "residual": "full_thread_task_span_compilation_and_binary_receipt_unavailable",
            "candidate_only": True, "no_promotion": True,
        },
        "formal_gap": {
            "status": "open_unless_formal_receipt_verified",
            "formal_gap_receipts": evidence["formal_gap_receipts"],
            "no_kernel_proof_inferred": True,
        },
        "authority": {
            "canonical_archive": "source_only", "transport_cache": "not_used",
            "pnf": "lexical_or_token_span_candidate_not_semantic_pnf",
            "reviewed_evidence": "receipt_references_only",
            "formal_evidence": "receipt_references_only",
            "ui": "projection_only", "dispatch": False,
        },
    }
    packet["packet_id"] = _hash(_encoded({
        "thread": thread, "child": child_thread_id, "task": task,
        "refs": refs, "evidence": evidence,
        "policy": [max_selected, max_packet_chars], "operation": operation_status,
    }))
    while len(_encoded(packet)) > max_packet_chars:
        nonempty = [candidate for candidate in candidates if candidate["spans"]]
        if not nonempty:
            raise ValueError("source references exceed packet budget")
        nonempty[-1]["spans"].pop()
        packet["span_receipt"]["packet_units_dropped"] += 1
        packet["span_receipt"]["packet_truncated"] = True
    return packet


def thread_view(payload: Mapping[str, Any]) -> dict[str, Any]:
    if set(payload) - {"canonical_thread_id", "archive_db", "max_selected", "max_packet_chars"}:
        raise ValueError("unknown thread_view fields")
    thread = payload.get("canonical_thread_id")
    packet = governed_handoff(
        {"canonical_thread_id": thread, "task_atom": "canonical context"},
        archive_db=payload.get("archive_db"),
        max_selected=payload.get("max_selected", 24),
        max_packet_chars=payload.get("max_packet_chars", 24000),
    )
    return {"version": VIEW_VERSION, "packet": packet}


def operation_review(payload: Mapping[str, Any]) -> dict[str, Any]:
    if set(payload) - {"operation_status", "operation_id", "review_receipt"}:
        raise ValueError("unknown operation fields")
    status = payload.get("operation_status")
    if not isinstance(status, str) or not status.strip():
        raise ValueError("operation_status required")
    if status in AMBIGUOUS:
        decision = "hold_reconcile_no_resend"
    elif status in {"completed", "committed"}:
        decision = "observe_only"
    else:
        decision = "review_required_no_dispatch"
    return {
        "version": OP_VERSION, "operation_status": status,
        "operation_id": payload.get("operation_id"),
        "review_receipt": payload.get("review_receipt"),
        "decision": decision, "dispatch_allowed": False,
        "automatic_resend_allowed": False, "transport": "direct_async_only",
        "browser_dom_allowed": False,
    }
