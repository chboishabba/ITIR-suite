"""Read-only projection of re-gpt mutation receipts, never canonical corpus truth."""
from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Any, Mapping

from .governed_revival import operation_review
from .pnf_work_packet_provider import REQUIRED, canonical_archive_path

VERSION = "itir.chatgpt.operation_receipts.v1"
REQUIRED_OPERATION_COLUMNS = {
    "operation_id", "operation", "conversation_id", "requested_parent_node_id",
    "prompt_digest", "transport", "state", "started_at", "submitted_at",
    "committed_at", "completed_at", "user_node_id", "assistant_node_id",
}


def operation_receipts(payload: Mapping[str, Any]) -> dict[str, Any]:
    allowed = {"conversation_id", "canonical_thread_id", "archive_db", "db_path", "limit", "active_only"}
    if not isinstance(payload, Mapping) or set(payload) - allowed:
        raise ValueError("unknown operation receipt lookup fields")
    conv_id = payload.get("conversation_id")
    thread = payload.get("canonical_thread_id")
    if (not conv_id or not isinstance(conv_id, str) or not conv_id.strip()) and (
        not thread or not isinstance(thread, str) or not thread.strip()
    ):
        raise ValueError("conversation_id or canonical_thread_id required")
    limit = payload.get("limit", 10)
    if type(limit) is not int or not 1 <= limit <= 50:
        raise ValueError("limit must be 1..50")
    active_only = payload.get("active_only", False)
    if type(active_only) is not bool:
        raise ValueError("active_only must be boolean")

    # Resolve transport conversation ID: direct UUID takes precedence.
    conversation_id = None
    if conv_id and isinstance(conv_id, str) and conv_id.strip():
        conversation_id = conv_id.strip()
    elif thread and isinstance(thread, str) and len(thread.strip()) == 36 and "-" in thread:
        conversation_id = thread.strip()
    else:
        # Legacy canonical thread resolution from canonical archive
        archive = canonical_archive_path(payload.get("archive_db"))
        if archive.is_file():
            with sqlite3.connect(archive.resolve().as_uri() + "?mode=ro", uri=True) as canonical:
                cols = {r[1] for r in canonical.execute("PRAGMA table_info(messages)")}
                if REQUIRED <= cols:
                    ids = [str(row[0]) for row in canonical.execute(
                        "SELECT DISTINCT source_thread_id FROM messages "
                        "WHERE canonical_thread_id=? AND source_thread_id IS NOT NULL LIMIT 3",
                        (thread,),
                    )]
                    if len(ids) == 1:
                        conversation_id = ids[0]
        if not conversation_id:
            conversation_id = str(thread).strip()

    raw_path = payload.get("db_path") or os.environ.get("ITIR_REGPT_RECEIPT_DB") or "~/.chatgpt_history.sqlite3"
    if not isinstance(raw_path, str) or not raw_path.strip():
        raise ValueError("invalid receipt db path")
    receipt_db = Path(raw_path).expanduser()
    if not receipt_db.is_file():
        raise FileNotFoundError("transport receipt cache missing")
    with sqlite3.connect(receipt_db.resolve().as_uri() + "?mode=ro", uri=True) as db:
        db.row_factory = sqlite3.Row
        cols = {r[1] for r in db.execute("PRAGMA table_info(mutation_attempts)")}
        if not REQUIRED_OPERATION_COLUMNS <= cols:
            raise RuntimeError("transport mutation_attempts schema mismatch")
        # Fetch limit+1 for a truthful truncation receipt. No prompts or error_detail.
        where = "conversation_id=?"
        if active_only:
            where += " AND state NOT IN ('complete','failed_precommit','attachment_failed_precommit')"
        rows = db.execute(
            "SELECT operation_id,operation,conversation_id,requested_parent_node_id,"
            "prompt_digest,transport,state,started_at,submitted_at,"
            "committed_at,completed_at,user_node_id,assistant_node_id "
            "FROM mutation_attempts WHERE " + where +
            " ORDER BY started_at DESC,operation_id DESC LIMIT ?",
            (conversation_id, limit + 1),
        ).fetchall()
    truncated = len(rows) > limit
    records = []
    for row in rows[:limit]:
        receipt = dict(row)
        receipt["governance_review"] = operation_review({
            "operation_status": str(row["state"]),
            "operation_id": str(row["operation_id"]),
        })
        records.append(receipt)
    return {
        "version": VERSION,
        "canonical_thread_id": thread or conversation_id,
        "transport_conversation_id": conversation_id,
        "source_authority": "canonical_archive_for_identity_only",
        "receipt_authority": "re_gpt_transport_cache_noncanonical",
        "records": records,
        "truncation_receipt": {
            "limit": limit, "returned": len(records), "more_available": truncated,
            "active_only": active_only,
        },
        "policy": {"read_only": True, "dispatch": False,
                   "automatic_resend": False, "browser_dom": False},
    }
