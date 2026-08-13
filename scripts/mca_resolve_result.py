#!/usr/bin/env python3
"""Resolve an MCA search hit into canonical identifiers and nearby text."""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).name
DEFAULT_MCA_REPO = Path("/home/c/Documents/code/mychatarchive")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def emit(payload: dict[str, Any], code: int = 0) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))
    raise SystemExit(code)


def env_first(*names: str) -> str | None:
    for name in names:
        value = os.environ.get(name)
        if value:
            return value
    return None


def load_json(raw: str | None) -> dict[str, Any]:
    if not raw:
        return {}
    try:
        data = json.loads(raw)
        return data if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        return {}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Resolve MCA chunk/message IDs into JSON context.")
    parser.add_argument("--mca-db", default=env_first("MYCHATARCHIVE_DB", "MCA_DB"))
    parser.add_argument("--canonical-db", default=env_first("CHAT_EXPORT_STRUCTURER_DB", "CHAT_ARCHIVE_DB"))
    parser.add_argument("--mca-repo", default=os.environ.get("MYCHATARCHIVE_REPO") or str(DEFAULT_MCA_REPO))
    parser.add_argument("--chunk-id", default=None)
    parser.add_argument("--message-id", default=None)
    parser.add_argument("--thread-id", "--canonical-thread-id", dest="thread_id", default=None)
    parser.add_argument("--context-limit", type=int, default=12)
    parser.add_argument("--json", action="store_true", help="Accepted for compatibility; output is always JSON.")
    args = parser.parse_args()
    args.mca_db = Path(args.mca_db).expanduser() if args.mca_db else None
    args.canonical_db = Path(args.canonical_db).expanduser() if args.canonical_db else None
    args.mca_repo = Path(args.mca_repo).expanduser()
    return args


def mca_message(con: sqlite3.Connection, message_id: str) -> dict[str, Any] | None:
    row = con.execute(
        """
        SELECT message_id, canonical_thread_id, platform, account_id, ts, role, text,
               title, source_id, source_thread_id, source_message_id, source_path,
               source_bucket, provenance_json, meta
        FROM messages WHERE message_id = ?
        """,
        (message_id,),
    ).fetchone()
    if not row:
        return None
    return {
        "message_id": row[0],
        "canonical_thread_id": row[1],
        "platform": row[2],
        "account_id": row[3],
        "timestamp": row[4],
        "role": row[5],
        "text": row[6],
        "title": row[7],
        "source_id": row[8],
        "source_thread_id": row[9],
        "source_message_id": row[10],
        "source_path": row[11],
        "source_bucket": row[12],
        "provenance": load_json(row[13]),
        "meta": load_json(row[14]),
    }


def canonical_thread_rows(db_path: Path, thread_id: str, limit: int) -> list[dict[str, Any]]:
    if not db_path.exists():
        return []
    con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    table_rows = con.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name IN ('messages', 'conversation_messages')"
    ).fetchall()
    table_names = {row[0] for row in table_rows}
    if "messages" in table_names:
        columns = {row["name"] for row in con.execute("PRAGMA table_info(messages)").fetchall()}
        id_filters = [
            col for col in ("canonical_thread_id", "thread_id", "source_thread_id")
            if col in columns
        ]
        order_col = next(
            (col for col in ("created_at", "ts", "timestamp") if col in columns),
            None,
        )
        if not id_filters:
            con.close()
            return []
        where_sql = " OR ".join(f"{col} = ?" for col in id_filters)
        order_sql = f" ORDER BY {order_col} ASC" if order_col else ""
        rows = con.execute(
            f"SELECT * FROM messages WHERE {where_sql}{order_sql} LIMIT ?",
            (*([thread_id] * len(id_filters)), limit),
        ).fetchall()
    elif "conversation_messages" in table_names:
        columns = {
            row["name"]
            for row in con.execute("PRAGMA table_info(conversation_messages)").fetchall()
        }
        id_filters = [
            col for col in ("canonical_thread_id", "conversation_id", "source_thread_id")
            if col in columns
        ]
        order_col = next(
            (col for col in ("create_time", "created_at", "timestamp") if col in columns),
            None,
        )
        if not id_filters:
            con.close()
            return []
        where_sql = " OR ".join(f"{col} = ?" for col in id_filters)
        order_sql = f" ORDER BY {order_col} ASC" if order_col else ""
        rows = con.execute(
            f"SELECT * FROM conversation_messages WHERE {where_sql}{order_sql} LIMIT ?",
            (*([thread_id] * len(id_filters)), limit),
        ).fetchall()
    else:
        rows = []
    con.close()
    return [{key: row[key] for key in row.keys()} for row in rows]


def main() -> None:
    args = parse_args()
    payload: dict[str, Any] = {
        "ok": False,
        "script": SCRIPT,
        "operation": "mca_resolve_result",
        "timestamp": utc_now(),
        "inputs": {
            "mca_db": str(args.mca_db) if args.mca_db else None,
            "canonical_db": str(args.canonical_db) if args.canonical_db else None,
            "chunk_id": args.chunk_id,
            "message_id": args.message_id,
            "thread_id": args.thread_id,
            "context_limit": args.context_limit,
        },
        "mca": {"repo": str(args.mca_repo)},
        "result": None,
    }
    if args.mca_db is None:
        payload["error"] = {"code": "missing_mca_db", "message": "Pass --mca-db or set MYCHATARCHIVE_DB/MCA_DB."}
        emit(payload, 2)
    if not args.mca_db.exists():
        payload["error"] = {"code": "mca_db_not_found", "message": f"MyChatArchive DB does not exist: {args.mca_db}"}
        emit(payload, 2)
    if not any([args.chunk_id, args.message_id, args.thread_id]):
        payload["error"] = {
            "code": "missing_lookup_id",
            "message": "Pass one of --chunk-id, --message-id, or --thread-id.",
        }
        emit(payload, 2)

    try:
        con = sqlite3.connect(args.mca_db)
        con.row_factory = sqlite3.Row
        chunk = None
        message_id = args.message_id
        thread_id = args.thread_id
        if args.chunk_id:
            chunk_row = con.execute(
                """
                SELECT chunk_id, message_id, canonical_thread_id, chunk_index, text,
                       ts_start, ts_end, meta
                FROM chunks WHERE chunk_id = ?
                """,
                (args.chunk_id,),
            ).fetchone()
            if chunk_row:
                chunk = {key: chunk_row[key] for key in chunk_row.keys()}
                chunk["meta"] = load_json(chunk.get("meta"))
                message_id = message_id or chunk.get("message_id")
                thread_id = thread_id or chunk.get("canonical_thread_id")
        message = mca_message(con, message_id) if message_id else None
        thread_id = thread_id or (message or {}).get("canonical_thread_id")
        nearby = []
        if thread_id:
            nearby_rows = con.execute(
                """
                SELECT message_id, canonical_thread_id, ts, role, text, title,
                       source_thread_id, source_message_id
                FROM messages
                WHERE canonical_thread_id = ?
                ORDER BY ts ASC
                LIMIT ?
                """,
                (thread_id, args.context_limit),
            ).fetchall()
            nearby = [{key: row[key] for key in row.keys()} for row in nearby_rows]
        con.close()

        canonical_rows = (
            canonical_thread_rows(args.canonical_db, thread_id, args.context_limit)
            if args.canonical_db and thread_id
            else []
        )
        payload.update(
            {
                "ok": True,
                "result": {
                    "chunk": chunk,
                    "message": message,
                    "canonical_thread_id": thread_id,
                    "thread_id": thread_id,
                    "nearby_mca_messages": nearby,
                    "canonical_archive_rows": canonical_rows,
                    "source_db": str(args.mca_db),
                    "canonical_db": str(args.canonical_db) if args.canonical_db else None,
                },
            }
        )
        emit(payload, 0)
    except Exception as exc:
        payload["error"] = {"code": "mca_resolve_result_failed", "message": str(exc)}
        emit(payload, 1)


if __name__ == "__main__":
    main()
