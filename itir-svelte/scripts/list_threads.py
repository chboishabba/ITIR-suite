#!/usr/bin/env python3
"""
List threads from the local chat archive SQLite and emit JSON.

Used by itir-svelte to provide a lightweight browse/search surface without
adding native Node sqlite deps.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path


def _message_columns(cur: sqlite3.Cursor) -> set[str]:
    cur.execute("select * from messages limit 0")
    return {str(col[0]) for col in (cur.description or [])}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True)
    ap.add_argument("--q", default="")
    ap.add_argument("--limit", type=int, default=200)
    ap.add_argument("--offset", type=int, default=0)
    args = ap.parse_args()

    db_path = Path(args.db)
    if not db_path.exists():
        raise SystemExit(f"DB not found: {db_path}")

    limit = max(1, min(500, int(args.limit)))
    offset = max(0, int(args.offset))
    q = (args.q or "").strip()

    con = sqlite3.connect(f"file:{db_path}?mode=ro&immutable=1", uri=True)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("pragma temp_store=memory")
    columns = _message_columns(cur)

    has_source_thread_id = "source_thread_id" in columns
    source_thread_expr = "source_thread_id" if has_source_thread_id else "null"
    source_thread_filter = "lower(coalesce(latest.source_thread_id, '')) like ?" if has_source_thread_id else "0"
    any_source_thread_expr = (
        "max(case when source_thread_id is not null and trim(source_thread_id) <> '' then source_thread_id else null end)"
        if has_source_thread_id
        else "null"
    )

    # We use a "latest row per canonical_thread_id" window to get title/source_id/platform.
    where_sql = ""
    params: list[object] = []
    if q:
        like = f"%{q.lower()}%"
        where_sql = """
        where
          lower(coalesce(latest.title, '')) like ?
          or lower(latest.canonical_thread_id) like ?
          or lower(coalesce(latest.source_id, '')) like ?
          or {source_thread_filter}
        """
        params.extend([like, like, like])
        if has_source_thread_id:
            params.append(like)

    cur.execute(
        f"""
        with
        per_thread as (
          select
            canonical_thread_id,
            count(*) as message_count,
            max(ts) as latest_ts,
            sum(case when trim(coalesce(text,'')) = '' then 1 else 0 end) as empty_text_count,
            {any_source_thread_expr} as any_source_thread_id
          from messages
          group by canonical_thread_id
        ),
        latest as (
          select canonical_thread_id, title, ts, source_id, platform, account_id, source_thread_id
          from (
            select
              canonical_thread_id,
              title,
              ts,
              source_id,
              platform,
              account_id,
              {source_thread_expr} as source_thread_id,
              row_number() over (partition by canonical_thread_id order by ts desc, rowid desc) as rn
            from messages
          )
          where rn = 1
        )
        select
          per_thread.canonical_thread_id as canonical_thread_id,
          coalesce(nullif(latest.title, ''), '(untitled)') as title,
          per_thread.message_count as message_count,
          per_thread.empty_text_count as empty_text_count,
          per_thread.latest_ts as latest_ts,
          latest.source_id as source_id,
          latest.platform as platform,
          latest.account_id as account_id,
          per_thread.any_source_thread_id as any_source_thread_id
        from per_thread
        join latest using (canonical_thread_id)
        {where_sql}
        order by per_thread.latest_ts desc
        limit ? offset ?
        """,
        [*params, limit, offset],
    )

    rows = [dict(r) for r in cur.fetchall()]
    out = {"threads": rows, "limit": limit, "offset": offset, "q": q}
    json.dump(out, fp=sys.stdout, ensure_ascii=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
