#!/usr/bin/env python3
"""
Query the local Chat archive SQLite and emit JSON.

This is used by the SvelteKit server to avoid adding native Node sqlite deps.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path


def is_date_text(v: str) -> bool:
    return len(v) == 10 and v[4] == "-" and v[7] == "-"


def start_bound(v: str) -> str:
    return f"{v}T00:00:00Z" if is_date_text(v) else v


def end_bound(v: str) -> str:
    return f"{v}T23:59:59Z" if is_date_text(v) else v


def table_columns(cur: sqlite3.Cursor, table: str) -> set[str]:
    return {str(row[1]) for row in cur.execute(f"pragma table_info({table})")}


def message_select_sql(cols: set[str]) -> str:
    optional = {
        "title": "title",
        "source_id": "source_id",
        "source_thread_id": "source_thread_id",
        "source_message_id": "source_message_id",
    }
    fields = [
        "message_id",
        "canonical_thread_id",
        "platform",
        "account_id",
        "ts",
        "role",
        "text",
    ]
    for alias, column in optional.items():
        if column in cols:
            fields.append(column)
        else:
            fields.append(f"NULL AS {alias}")
    return ", ".join(fields)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True)
    ap.add_argument("--thread-id", default="")
    ap.add_argument("--source-thread-id", default="")
    ap.add_argument("--ts", default="")
    ap.add_argument("--ts-start", default="")
    ap.add_argument("--ts-end", default="")
    ap.add_argument("--prefer-non-empty", action="store_true")
    ap.add_argument("--start", default="")
    ap.add_argument("--end", default="")
    ap.add_argument("--tail", type=int, default=400)
    args = ap.parse_args()

    db_path = Path(args.db)
    if not db_path.exists():
        raise SystemExit(f"DB not found: {db_path}")

    thread_id = args.thread_id.strip()
    source_thread_id = args.source_thread_id.strip()
    if not thread_id and not source_thread_id:
        raise SystemExit("Either --thread-id or --source-thread-id is required.")

    con = sqlite3.connect(f"file:{db_path}?mode=ro&immutable=1", uri=True)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cols = table_columns(cur, "messages")
    select_fields = message_select_sql(cols)

    # Prevent temp file failures in some environments.
    cur.execute("pragma temp_store=memory")

    # Direct timestamp lookup (optionally constrained to a ts-range).
    if args.ts.strip() or args.ts_start.strip() or args.ts_end.strip():
        ts = args.ts.strip()
        prefer_non_empty = bool(args.prefer_non_empty)

        # Archives vary in timestamp formatting:
        # - SB dashboard payloads tend to use `...Z` (seconds precision)
        # - Chat export archives may store `...+00:00` and/or include fractional seconds.
        #
        # We query at second granularity and (optionally) prefer non-empty text to avoid
        # rendering blank chat bubbles when the most recent record is a metadata-only row.
        ts_prefix = ts[:19] if len(ts) >= 19 else ""
        ts_alt = f"{ts[:-1]}+00:00" if ts.endswith("Z") else ts

        where = ["canonical_thread_id = ?"]
        params: list[str] = [thread_id]

        if args.ts_start.strip():
            where.append("ts >= ?")
            params.append(args.ts_start.strip())
        if args.ts_end.strip():
            where.append("ts <= ?")
            params.append(args.ts_end.strip())

        if ts_prefix:
            where.append("(ts = ? or ts = ? or substr(ts, 1, 19) = ?)")
            params.extend([ts, ts_alt, ts_prefix])
        elif ts:
            where.append("(ts = ? or ts = ?)")
            params.extend([ts, ts_alt])

        where_sql = " where " + " and ".join(where)
        # Prefer:
        # - exact ts match (if provided)
        # - non-empty text (if requested)
        # - most recent within the second
        order_sql = " order by "
        order_terms: list[str] = []
        if ts:
            order_terms.append("(ts = ? or ts = ?) desc")
            params.extend([ts, ts_alt])
        if prefer_non_empty:
            order_terms.append("(trim(coalesce(text,'')) <> '') desc")
        order_terms.append("ts desc")
        order_sql += ", ".join(order_terms)

        cur.execute(
            f"""
            select {select_fields}
            from messages
            {where_sql}
            {order_sql}
            limit 1
            """,
            params,
        )
        row = cur.fetchone()

        out = {"message": dict(row) if row else None}
        json.dump(out, fp=sys.stdout, ensure_ascii=True)
        return 0

    # Optional mapping: source_thread_id (online conversation UUID) -> canonical_thread_id.
    # If present, we resolve to the most-populated canonical thread for that upstream id.
    canonical = thread_id
    if source_thread_id:
        if "source_thread_id" not in cols:
            json.dump({"canonical_thread_id": None, "title": None, "total": 0, "tail": tail, "messages": []}, fp=sys.stdout, ensure_ascii=True)
            return 0
        cur.execute(
            """
            select canonical_thread_id, count(*) as c
            from messages
            where source_thread_id = ?
            group by canonical_thread_id
            order by c desc
            limit 1
            """,
            [source_thread_id],
        )
        row = cur.fetchone()
        if row and row["canonical_thread_id"]:
            canonical = row["canonical_thread_id"]
    if not canonical:
        raise SystemExit("Could not resolve canonical thread id from --source-thread-id.")

    tail = max(1, min(2000, int(args.tail)))

    where = ["canonical_thread_id = ?"]
    params: list[str] = [canonical]
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
        select {select_fields}
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
        [canonical],
    )
    row = cur.fetchone()
    title = row["title"] if row else None

    out = {"canonical_thread_id": canonical, "title": title, "total": total, "tail": tail, "messages": rows}
    json.dump(out, fp=sys.stdout, ensure_ascii=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
