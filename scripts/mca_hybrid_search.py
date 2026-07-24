#!/usr/bin/env python3
"""Run agent-oriented hybrid search over MyChatArchive."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
from datetime import timezone
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).name
DEFAULT_MCA_REPO = Path("/home/c/Documents/code/mychatarchive")


def utc_now() -> str:
    return dt.datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def emit(payload: dict[str, Any], code: int = 0) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))
    raise SystemExit(code)


def env_first(*names: str) -> str | None:
    for name in names:
        value = os.environ.get(name)
        if value:
            return value
    return None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Hybrid keyword + semantic MCA search with JSON output.")
    parser.add_argument("query_terms", nargs="*", help="Search query words.")
    parser.add_argument("--query", default=None, help="Search query. Overrides positional query words.")
    parser.add_argument(
        "--canonical-db",
        default=env_first("CHAT_EXPORT_STRUCTURER_DB", "CHAT_ARCHIVE_DB"),
        help="Optional canonical archive SQLite DB for provenance-aware callers.",
    )
    parser.add_argument("--mca-db", default=env_first("MYCHATARCHIVE_DB", "MCA_DB"))
    parser.add_argument("--mca-repo", default=os.environ.get("MYCHATARCHIVE_REPO") or str(DEFAULT_MCA_REPO))
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--semantic-limit", type=int, default=None)
    parser.add_argument("--keyword-limit", type=int, default=None)
    parser.add_argument("--platform", action="append", default=None)
    parser.add_argument("--hours", type=int, default=None)
    parser.add_argument("--since", default=None, metavar="YYYY-MM-DD")
    parser.add_argument("--sort", choices=["relevance", "time"], default="relevance")
    parser.add_argument("--json", action="store_true", help="Accepted for compatibility; output is always JSON.")
    args = parser.parse_args()
    args.query = args.query if args.query is not None else " ".join(args.query_terms)
    args.canonical_db = Path(args.canonical_db).expanduser() if args.canonical_db else None
    args.mca_db = Path(args.mca_db).expanduser() if args.mca_db else None
    args.mca_repo = Path(args.mca_repo).expanduser()
    args.semantic_limit = args.semantic_limit or args.limit
    args.keyword_limit = args.keyword_limit or args.limit
    return args


def cutoff_iso(args: argparse.Namespace) -> str | None:
    if args.hours is not None:
        return (
            dt.datetime.now(timezone.utc) - dt.timedelta(hours=args.hours)
        ).isoformat()
    if args.since:
        try:
            return dt.datetime.strptime(args.since, "%Y-%m-%d").replace(tzinfo=timezone.utc).isoformat()
        except ValueError as exc:
            raise ValueError("invalid --since; use YYYY-MM-DD") from exc
    return None


def load_json(raw: str | None) -> dict[str, Any]:
    if not raw:
        return {}
    try:
        data = json.loads(raw)
        return data if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        return {}


def semantic_result(con: Any, chunk_id: str, distance: float, source_db: Path) -> dict[str, Any] | None:
    row = con.execute(
        """
        SELECT c.text, c.canonical_thread_id, c.ts_start, c.ts_end, c.meta,
               c.message_id, m.role, m.title, m.source_thread_id, m.source_message_id
        FROM chunks c
        LEFT JOIN messages m ON c.message_id = m.message_id
        WHERE c.chunk_id = ?
        """,
        (chunk_id,),
    ).fetchone()
    if not row:
        return None
    meta = load_json(row[4])
    message_id = row[5]
    thread_id = row[1]
    return {
        "key": f"message:{message_id}" if message_id else f"thread:{thread_id}:chunk:{chunk_id}",
        "match_type": "semantic",
        "chunk_id": chunk_id,
        "message_id": message_id,
        "canonical_thread_id": thread_id,
        "thread_id": thread_id,
        "source_thread_id": row[8] or meta.get("source_thread_id"),
        "source_message_id": row[9] or meta.get("source_message_id"),
        "title": row[7] or meta.get("title") or "",
        "role": row[6] or meta.get("role") or "",
        "timestamp": row[2],
        "distance": float(distance),
        "semantic_score": max(0.0, 1.0 - float(distance)),
        "keyword_score": 0.0,
        "score": max(0.0, 1.0 - float(distance)),
        "excerpt": row[0][:1000],
        "source_db": str(source_db),
    }


def keyword_result(row: Any, source_db: Path) -> dict[str, Any]:
    message_id, text, thread_id, ts, role, title = row
    return {
        "key": f"message:{message_id}",
        "match_type": "keyword",
        "chunk_id": None,
        "message_id": message_id,
        "canonical_thread_id": thread_id,
        "thread_id": thread_id,
        "source_thread_id": None,
        "source_message_id": None,
        "title": title or "",
        "role": role or "",
        "timestamp": ts,
        "distance": None,
        "semantic_score": 0.0,
        "keyword_score": 1.0,
        "score": 1.0,
        "excerpt": (text or "")[:1000],
        "source_db": str(source_db),
    }


def enrich_keyword_sources(con: Any, item: dict[str, Any]) -> dict[str, Any]:
    row = con.execute(
        """
        SELECT source_thread_id, source_message_id, source_path, source_bucket
        FROM messages WHERE message_id = ?
        """,
        (item["message_id"],),
    ).fetchone()
    if row:
        item["source_thread_id"] = row[0]
        item["source_message_id"] = row[1]
        item["source_path"] = row[2]
        item["source_bucket"] = row[3]
    return item


def merge_results(keyword_rows: list[dict[str, Any]], semantic_rows: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    merged: dict[str, dict[str, Any]] = {}
    for item in semantic_rows:
        merged[item["key"]] = item
    for item in keyword_rows:
        key = item["key"]
        if key in merged:
            existing = merged[key]
            existing["match_type"] = "hybrid"
            existing["keyword_score"] = max(existing["keyword_score"], item["keyword_score"])
            existing["score"] = max(existing["score"], 1.25)
            existing["source_thread_id"] = existing.get("source_thread_id") or item.get("source_thread_id")
            existing["source_message_id"] = existing.get("source_message_id") or item.get("source_message_id")
        else:
            item["score"] = 1.25
            merged[key] = item
    rows = list(merged.values())
    rows.sort(key=lambda item: (item["score"], item.get("timestamp") or ""), reverse=True)
    return rows[:limit]


def main() -> None:
    args = parse_args()
    payload: dict[str, Any] = {
        "ok": False,
        "script": SCRIPT,
        "operation": "mca_hybrid_search",
        "timestamp": utc_now(),
        "inputs": {
            "query": args.query,
            "canonical_db": str(args.canonical_db) if args.canonical_db else None,
            "mca_db": str(args.mca_db) if args.mca_db else None,
            "limit": args.limit,
            "semantic_limit": args.semantic_limit,
            "keyword_limit": args.keyword_limit,
            "platform": args.platform,
            "hours": args.hours,
            "since": args.since,
            "sort": args.sort,
        },
        "mca": {"repo": str(args.mca_repo)},
        "results": [],
    }
    if not args.query.strip():
        payload["error"] = {"code": "missing_query", "message": "Pass --query or positional query terms."}
        emit(payload, 2)
    if args.mca_db is None:
        payload["error"] = {"code": "missing_mca_db", "message": "Pass --mca-db or set MYCHATARCHIVE_DB/MCA_DB."}
        emit(payload, 2)
    if not args.mca_db.exists():
        payload["error"] = {"code": "mca_db_not_found", "message": f"MyChatArchive DB does not exist: {args.mca_db}"}
        emit(payload, 2)
    src = args.mca_repo / "src"
    if not src.exists():
        payload["error"] = {"code": "mca_src_not_found", "message": f"MyChatArchive src path does not exist: {src}"}
        emit(payload, 2)
    sys.path.insert(0, str(src))

    try:
        cutoff = cutoff_iso(args)
        from mychatarchive import db

        con = db.get_connection(args.mca_db)
        keyword_matches = db.fts_search(
            con,
            args.query,
            limit=args.keyword_limit,
            platform=args.platform,
            cutoff_iso=cutoff,
            sort_by_time=args.sort == "time",
        )
        keyword_rows = [enrich_keyword_sources(con, keyword_result(row, args.mca_db)) for row in keyword_matches]
        semantic_matches = []
        semantic_warning = None
        try:
            from mychatarchive.embeddings import embed_single

            embedding = embed_single(args.query)
            semantic_matches = db.search_chunks(
                con,
                embedding,
                limit=args.semantic_limit,
                platform=args.platform,
                cutoff_iso=cutoff,
                sort_by_time=args.sort == "time",
            )
        except Exception as exc:
            semantic_warning = {
                "code": "semantic_search_unavailable",
                "message": str(exc),
            }
        semantic_rows = [r for r in (semantic_result(con, cid, dist, args.mca_db) for cid, dist in semantic_matches) if r]
        results = merge_results(keyword_rows, semantic_rows, args.limit)
        con.close()
        payload.update(
            {
                "ok": True,
                "results": results,
                "result_count": len(results),
                "keyword_count": len(keyword_rows),
                "semantic_count": len(semantic_rows),
            }
        )
        if semantic_warning:
            payload["warning"] = semantic_warning
        emit(payload, 0)
    except Exception as exc:
        payload["error"] = {"code": "mca_hybrid_search_failed", "message": str(exc)}
        emit(payload, 1)


if __name__ == "__main__":
    main()
