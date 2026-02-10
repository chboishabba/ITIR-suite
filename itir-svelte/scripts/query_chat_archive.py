#!/usr/bin/env python3
"""
Query the local Chat archive SQLite and emit JSON.

This is used by the SvelteKit server to avoid adding native Node sqlite deps.
"""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
from pathlib import Path


def is_date_text(v: str) -> bool:
    return len(v) == 10 and v[4] == "-" and v[7] == "-"


def start_bound(v: str) -> str:
    return f"{v}T00:00:00Z" if is_date_text(v) else v


def end_bound(v: str) -> str:
    return f"{v}T23:59:59Z" if is_date_text(v) else v


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True)
    ap.add_argument("--thread-id", required=True)
    ap.add_argument("--start", default="")
    ap.add_argument("--end", default="")
    ap.add_argument("--tail", type=int, default=400)
    args = ap.parse_args()

    db_path = Path(args.db)
    if not db_path.exists():
        raise SystemExit(f"DB not found: {db_path}")

    tail = max(1, min(2000, int(args.tail)))

    con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    # Prevent temp file failures in some environments.
    cur.execute("pragma temp_store=memory")

    where = ["canonical_thread_id = ?"]
    params: list[str] = [args.thread_id]
    if args.start.strip():
        where.append("ts >= ?")
        params.append(start_bound(args.start.strip()))
    if args.end.strip():
        where.append("ts <= ?")
        params.append(end_bound(args.end.strip()))
    where_sql = " where " + " and ".join(where)

    cur.execute(f"select count(*) as c from messages{where_sql}", params)
    total = int(cur.fetchone()["c"])

    cur.execute(
        f"""
        select message_id, canonical_thread_id, platform, account_id, ts, role, text, title,
               source_id, source_thread_id, source_message_id
        from messages
        {where_sql}
        order by ts desc
        limit ?
        """,
        [*params, tail],
    )
    rows = [dict(r) for r in cur.fetchall()][::-1]

    cur.execute(
        """
        select title from messages
        where canonical_thread_id = ? and title is not null and trim(title) <> ''
        order by ts desc
        limit 1
        """,
        [args.thread_id],
    )
    row = cur.fetchone()
    title = row["title"] if row else None

    out = {"title": title, "total": total, "tail": tail, "messages": rows}
    json.dump(out, fp=sys.stdout, ensure_ascii=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
