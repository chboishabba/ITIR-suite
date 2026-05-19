#!/usr/bin/env python3
"""Run MyChatArchive semantic search and emit stable JSON for agents."""

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
    parser = argparse.ArgumentParser(description="Semantic search MyChatArchive with JSON output.")
    parser.add_argument("query_terms", nargs="*", help="Search query words.")
    parser.add_argument("--query", default=None, help="Search query. Overrides positional query words.")
    parser.add_argument(
        "--mca-db",
        default=env_first("MYCHATARCHIVE_DB", "MCA_DB"),
        help="MyChatArchive SQLite DB. Env fallback: MYCHATARCHIVE_DB, MCA_DB.",
    )
    parser.add_argument(
        "--canonical-db",
        default=env_first("CHAT_EXPORT_STRUCTURER_DB", "CHAT_ARCHIVE_DB"),
        help="Optional canonical archive SQLite DB for provenance-aware callers.",
    )
    parser.add_argument("--mca-repo", default=os.environ.get("MYCHATARCHIVE_REPO") or str(DEFAULT_MCA_REPO))
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--platform", action="append", default=None)
    parser.add_argument("--hours", type=int, default=None)
    parser.add_argument("--since", default=None, metavar="YYYY-MM-DD")
    parser.add_argument("--sort", choices=["relevance", "time"], default="relevance")
    parser.add_argument("--json", action="store_true", help="Accepted for compatibility; output is always JSON.")
    args = parser.parse_args()
    args.query = args.query if args.query is not None else " ".join(args.query_terms)
    args.mca_db = Path(args.mca_db).expanduser() if args.mca_db else None
    args.canonical_db = Path(args.canonical_db).expanduser() if args.canonical_db else None
    args.mca_repo = Path(args.mca_repo).expanduser()
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


def fallback_result(con: Any, chunk_id: str, distance: float, source_db: Path) -> dict[str, Any] | None:
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
    return {
        "chunk_id": chunk_id,
        "message_id": row[5],
        "canonical_thread_id": row[1],
        "thread_id": row[1],
        "source_thread_id": row[8] or meta.get("source_thread_id"),
        "source_message_id": row[9] or meta.get("source_message_id"),
        "title": row[7] or meta.get("title") or "",
        "role": row[6] or meta.get("role") or "",
        "timestamp": row[2],
        "ts_start": row[2],
        "ts_end": row[3],
        "distance": float(distance),
        "score": max(0.0, 1.0 - float(distance)),
        "excerpt": row[0][:1000],
        "source_db": str(source_db),
        "provenance": {"available": False, "reason": "fallback_chunk_metadata_only"},
    }


def main() -> None:
    args = parse_args()
    payload: dict[str, Any] = {
        "ok": False,
        "script": SCRIPT,
        "operation": "mca_semantic_search",
        "timestamp": utc_now(),
        "inputs": {
            "query": args.query,
            "canonical_db": str(args.canonical_db) if args.canonical_db else None,
            "mca_db": str(args.mca_db) if args.mca_db else None,
            "limit": args.limit,
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
        from mychatarchive.embeddings import embed_single

        con = db.get_connection(args.mca_db)
        embedding = embed_single(args.query)
        matches = db.search_chunks(
            con,
            embedding,
            limit=args.limit,
            platform=args.platform,
            cutoff_iso=cutoff,
            sort_by_time=args.sort == "time",
        )
        try:
            from mychatarchive.retrieval_explain import build_provenance_ranked_chunk_results

            distance_by_chunk = {chunk_id: float(distance) for chunk_id, distance in matches}
            explained = build_provenance_ranked_chunk_results(con, matches, limit=args.limit)
            results = [
                {
                    "chunk_id": item.get("chunk_id"),
                    "message_id": item.get("message_id"),
                    "canonical_thread_id": item.get("thread_id"),
                    "thread_id": item.get("thread_id"),
                    "source_thread_id": item.get("governance", {}).get("source", {}).get("source_thread_id"),
                    "source_message_id": item.get("governance", {}).get("source", {}).get("source_message_id"),
                    "title": item.get("title") or "",
                    "role": item.get("role") or "",
                    "timestamp": item.get("timestamp"),
                    "distance": distance_by_chunk.get(item.get("chunk_id")),
                    "score": item.get("rank_score"),
                    "semantic_similarity": item.get("semantic_similarity"),
                    "excerpt": item.get("text") or "",
                    "source_db": str(args.mca_db),
                    "provenance": item.get("governance") or {},
                }
                for item in explained
            ]
        except Exception as exc:
            results = [r for r in (fallback_result(con, cid, dist, args.mca_db) for cid, dist in matches) if r]
            payload["warning"] = {
                "code": "provenance_explain_unavailable",
                "message": str(exc),
            }
        con.close()
        payload.update({"ok": True, "results": results, "result_count": len(results)})
        emit(payload, 0)
    except Exception as exc:
        payload["error"] = {"code": "mca_semantic_search_failed", "message": str(exc)}
        emit(payload, 1)


if __name__ == "__main__":
    main()
