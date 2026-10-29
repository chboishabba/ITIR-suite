#!/usr/bin/env python3
"""Hydrate next tranche of unhydrated conversations in local SQLite using headless curl_cffi."""

from __future__ import annotations

import argparse
import sqlite3
import sys
import time
from pathlib import Path

from re_gpt.mutation_service import MutationService
from re_gpt.storage import DEFAULT_DB_PATH


def hydrate_batch(
    *,
    limit: int = 50,
    db_path: Path = DEFAULT_DB_PATH,
    delay: float = 1.2,
) -> dict[str, int]:
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT c.conversation_id, c.title, c.remote_update_time
            FROM conversations c
            LEFT JOIN messages m ON c.conversation_id = m.conversation_id
            GROUP BY c.conversation_id
            HAVING count(m.message_index) = 0
            ORDER BY c.remote_update_time DESC
            LIMIT ?
        """, (limit,))
        unhydrated = cur.fetchall()

    if not unhydrated:
        print("No unhydrated conversations found.")
        return {"total": 0, "succeeded": 0, "failed": 0}

    print(f"Starting headless CFFI hydration of {len(unhydrated)} conversations...")
    service = MutationService(db_path=db_path)

    succeeded = 0
    failed = 0

    for idx, (cid, title, ts) in enumerate(unhydrated, 1):
        clean_title = (title or cid).strip()[:40]
        print(f"[{idx}/{len(unhydrated)}] Pulling {cid[:8]} ({clean_title})... ", end="", flush=True)
        try:
            res = service._pull_and_persist(cid, browser_fallback=False)
            total_msgs = res.get("total_messages", 0)
            adapter = res.get("read_adapter", "cffi")
            print(f"OK ({total_msgs} msgs, {adapter})", flush=True)
            succeeded += 1
        except Exception as exc:
            print(f"FAILED: {exc}", flush=True)
            failed += 1
        if idx < len(unhydrated):
            time.sleep(delay)

    print(f"\nBatch complete: {succeeded} succeeded, {failed} failed.")
    return {"total": len(unhydrated), "succeeded": succeeded, "failed": failed}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hydrate unhydrated conversations in SQLite")
    parser.add_argument("--limit", type=int, default=20, help="Number of conversations to hydrate")
    parser.add_argument("--delay", type=float, default=1.0, help="Pacing delay between requests in seconds")
    args = parser.parse_args()

    hydrate_batch(limit=args.limit, delay=args.delay)
