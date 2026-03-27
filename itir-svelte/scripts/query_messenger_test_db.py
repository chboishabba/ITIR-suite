#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path


def _connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def _latest_run_id(conn: sqlite3.Connection) -> str | None:
    row = conn.execute(
        "SELECT run_id FROM messenger_test_ingest_runs ORDER BY created_at DESC, rowid DESC LIMIT 1"
    ).fetchone()
    if row is None:
        return None
    return str(row["run_id"])


def _list_runs(conn: sqlite3.Connection, limit: int) -> list[dict[str, object]]:
    rows = conn.execute(
        """
        SELECT
          r.run_id,
          r.created_at,
          r.source_db_path,
          r.source_db_size,
          r.sample_limit,
          r.source_namespace,
          r.source_class,
          r.retention_policy,
          r.redaction_policy,
          r.note,
          COUNT(m.row_order) AS message_count,
          COUNT(DISTINCT m.conversation_hash) AS conversation_count
        FROM messenger_test_ingest_runs r
        LEFT JOIN messenger_test_messages m ON m.run_id = r.run_id
        GROUP BY r.run_id
        ORDER BY r.created_at DESC, r.rowid DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    return [dict(row) for row in rows]


def _run_summary(conn: sqlite3.Connection, run_id: str) -> dict[str, object] | None:
    run_row = conn.execute(
        """
        SELECT
          r.run_id,
          r.created_at,
          r.source_db_path,
          r.source_db_size,
          r.sample_limit,
          r.source_namespace,
          r.source_class,
          r.retention_policy,
          r.redaction_policy,
          r.note,
          COUNT(m.row_order) AS message_count,
          COUNT(DISTINCT m.conversation_hash) AS conversation_count,
          MIN(m.ts) AS first_ts,
          MAX(m.ts) AS last_ts
        FROM messenger_test_ingest_runs r
        LEFT JOIN messenger_test_messages m ON m.run_id = r.run_id
        WHERE r.run_id = ?
        GROUP BY r.run_id
        """,
        (run_id,),
    ).fetchone()
    if run_row is None:
        return None

    filter_stats = conn.execute(
        """
        SELECT reason, count
        FROM messenger_test_filter_stats
        WHERE run_id = ?
        ORDER BY count DESC, reason ASC
        """,
        (run_id,),
    ).fetchall()

    top_conversations = conn.execute(
        """
        SELECT
          conversation_hash,
          conversation_type,
          COUNT(*) AS message_count,
          MIN(ts) AS first_ts,
          MAX(ts) AS last_ts,
          MIN(sender) AS sample_sender
        FROM messenger_test_messages
        WHERE run_id = ?
        GROUP BY conversation_hash, conversation_type
        ORDER BY message_count DESC, last_ts DESC
        LIMIT 12
        """,
        (run_id,),
    ).fetchall()

    return {
        **dict(run_row),
        "filter_counts": {str(row["reason"]): int(row["count"]) for row in filter_stats},
        "top_conversations": [dict(row) for row in top_conversations],
    }


def _list_messages(
    conn: sqlite3.Connection,
    *,
    run_id: str,
    conversation_hash: str | None,
    text_query: str | None,
    limit: int,
) -> list[dict[str, object]]:
    where = ["run_id = ?"]
    params: list[object] = [run_id]
    if conversation_hash:
        where.append("conversation_hash = ?")
        params.append(conversation_hash)
    if text_query:
        where.append("(lower(text) LIKE ? OR lower(sender) LIKE ?)")
        like = f"%{text_query.strip().lower()}%"
        params.extend([like, like])
    rows = conn.execute(
        f"""
        SELECT
          run_id,
          row_order,
          conversation_hash,
          conversation_type,
          ts,
          sender,
          text
        FROM messenger_test_messages
        WHERE {' AND '.join(where)}
        ORDER BY ts DESC, row_order DESC
        LIMIT ?
        """,
        (*params, limit),
    ).fetchall()
    payload = [dict(row) for row in rows]
    payload.reverse()
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Query messenger_test_db content for itir-svelte corpus browsing.")
    parser.add_argument("--db-path", type=Path, default=Path(".cache_local/itir_messenger_test.sqlite"))
    subparsers = parser.add_subparsers(dest="command", required=True)

    runs_parser = subparsers.add_parser("runs", help="List ingest runs")
    runs_parser.add_argument("--limit", type=int, default=10)

    summary_parser = subparsers.add_parser("summary", help="Summarize one run")
    summary_parser.add_argument("--run-id", default=None)

    messages_parser = subparsers.add_parser("messages", help="List recent messages")
    messages_parser.add_argument("--run-id", default=None)
    messages_parser.add_argument("--conversation-hash", default=None)
    messages_parser.add_argument("--text-query", default=None)
    messages_parser.add_argument("--limit", type=int, default=100)

    args = parser.parse_args(argv)
    db_path = args.db_path.expanduser().resolve()
    if not db_path.exists():
        raise SystemExit(f"DB not found: {db_path}")

    with _connect(db_path) as conn:
        if args.command == "runs":
            payload = {
                "ok": True,
                "dbPath": str(db_path),
                "runs": _list_runs(conn, limit=max(1, min(50, int(args.limit)))),
            }
        elif args.command == "summary":
            run_id = args.run_id or _latest_run_id(conn)
            payload = {
                "ok": True,
                "dbPath": str(db_path),
                "run_id": run_id,
                "summary": None if run_id is None else _run_summary(conn, run_id),
            }
        else:
            run_id = args.run_id or _latest_run_id(conn)
            payload = {
                "ok": True,
                "dbPath": str(db_path),
                "run_id": run_id,
                "messages": []
                if run_id is None
                else _list_messages(
                    conn,
                    run_id=run_id,
                    conversation_hash=(args.conversation_hash or "").strip() or None,
                    text_query=(args.text_query or "").strip() or None,
                    limit=max(1, min(500, int(args.limit))),
                ),
            }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
