#!/usr/bin/env python3
"""Resolve conversation context from structurer DB with optional live fallback."""

from __future__ import annotations

import datetime as dt
import sqlite3
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from chat_context_resolver_lib.analysis import (
    analyze_thread_terms,
    parse_range_spec as _parse_range_spec,
    parse_terms as _parse_terms,
    split_paragraphs as _split_paragraphs,
    top_terms as _top_terms,
)
from chat_context_resolver_lib.cli import (
    build_parser as _build_parser,
    resolve_runtime_options as _resolve_runtime_options,
)
from chat_context_resolver_lib.db_lookup import (
    connect_sqlite_ro as _connect_sqlite_ro,
    looks_like_canonical_thread_id as _looks_like_canonical_thread_id,
    looks_like_online_thread_id as _looks_like_online_thread_id,
    query_db_fts_candidates as _query_db_fts_candidates,
    resolve_db_lookup as _resolve_db_lookup,
)
from chat_context_resolver_lib.formatters import (
    db_payload as _db_payload,
    print_result as _print_result,
)
from chat_context_resolver_lib.flow import (
    FlowDependencies as _FlowDependencies,
    resolve_flow as _resolve_flow,
)
from chat_context_resolver_lib.live_provider import (
    extract_online_thread_id_from_url as _extract_online_thread_id_from_url,
    fetch_web_recent_turns as _fetch_web_recent_turns,
    persist_selector_to_structurer as _persist_selector_to_structurer,
    run_web_view as _run_web_view,
)
from chat_context_resolver_lib.transcript import (
    TranscriptLine,
    build_stitched_transcript,
    filter_transcript_lines,
    latest_turn_datetime,
    truncate_text,
)


def _parse_datetime(value: str) -> dt.datetime:
    text = value.strip()
    if not text:
        raise ValueError("datetime value is empty")

    try:
        epoch = float(text)
    except ValueError:
        normalized = text[:-1] + "+00:00" if text.endswith("Z") else text
        parsed = dt.datetime.fromisoformat(normalized)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=dt.timezone.utc)
        return parsed.astimezone(dt.timezone.utc)

    return dt.datetime.fromtimestamp(epoch, tz=dt.timezone.utc)


def _parse_message_ts(value: object) -> Optional[dt.datetime]:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        return _parse_datetime(text)
    except ValueError:
        return None


def _iso_utc(value: Optional[dt.datetime]) -> Optional[str]:
    if value is None:
        return None
    return value.astimezone(dt.timezone.utc).replace(microsecond=0).isoformat()


def _iso_utc_precise(value: Optional[dt.datetime]) -> Optional[str]:
    if value is None:
        return None
    return value.astimezone(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def _build_stitched_transcript(
    rows: list[dict],
    *,
    max_text_chars: int = 0,
) -> list[TranscriptLine]:
    return build_stitched_transcript(
        rows,
        max_text_chars=max_text_chars,
        parse_message_ts=_parse_message_ts,
        iso_utc_precise=_iso_utc_precise,
    )


def _query_recent_turns(
    db_path: Path,
    thread_id: str,
    limit: int,
    max_text_chars: int,
) -> list[dict]:
    if limit <= 0:
        return []

    con = _connect_sqlite_ro(db_path)
    cur = con.cursor()
    cur.execute(
        """
        SELECT ts, role, text
        FROM messages
        WHERE LOWER(canonical_thread_id) = LOWER(?)
          AND text IS NOT NULL
          AND TRIM(text) <> ''
        ORDER BY ts DESC, rowid DESC
        LIMIT ?
        """,
        (thread_id, limit),
    )
    rows = cur.fetchall()
    con.close()

    turns = []
    for row in reversed(rows):
        parsed_ts = _parse_message_ts(row["ts"])
        turns.append(
            {
                "ts": row["ts"],
                "ts_utc": _iso_utc_precise(parsed_ts),
                "role": row["role"],
                "text": truncate_text(row["text"] or "", max_text_chars),
            }
        )
    return turns


def _query_thread_messages(
    db_path: Path,
    thread_id: str,
) -> list[dict]:
    con = _connect_sqlite_ro(db_path)
    cur = con.cursor()
    cur.execute(
        """
        SELECT message_id, ts, role, text
        FROM messages
        WHERE LOWER(canonical_thread_id) = LOWER(?)
          AND text IS NOT NULL
          AND TRIM(text) <> ''
        ORDER BY ts ASC, rowid ASC
        """,
        (thread_id,),
    )
    rows = cur.fetchall()
    con.close()
    return [dict(row) for row in rows]


def _thread_analysis_payload(
    db_path: Path,
    thread_id: str,
    *,
    terms: list[str],
    regex: bool,
    case_sensitive: bool,
    thread_range: tuple[int, int] | None,
    message_range: tuple[int, int] | None,
    show_lines: bool,
    show_line_context: int,
    top_terms_limit: int,
    max_text_chars: int,
) -> dict:
    rows = _query_thread_messages(db_path, thread_id)
    transcript_full = _build_stitched_transcript(
        rows,
        max_text_chars=max_text_chars,
    )
    transcript = filter_transcript_lines(
        transcript_full,
        thread_range=thread_range,
        message_range=message_range,
    )
    analysis = analyze_thread_terms(
        transcript,
        terms=terms,
        regex=regex,
        case_sensitive=case_sensitive,
        show_line_context=show_line_context,
    )
    payload = {
        "analysis_scope": "thread_local",
        "transcript_stats": analysis["transcript_stats"],
        "term_stats": analysis["term_stats"],
        "mentions": analysis["mentions"],
    }
    if thread_range or message_range:
        payload["range_excerpt"] = {
            "thread_range": list(thread_range) if thread_range else None,
            "message_range": list(message_range) if message_range else None,
            "stitched_line_count": len(transcript),
        }
    if show_lines:
        payload["lines"] = [
            {
                "thread_line": line.thread_line,
                "message_index": line.message_index,
                "message_id": line.message_id,
                "role": line.role,
                "ts": line.ts,
                "ts_utc": line.ts_utc,
                "message_line": line.message_line,
                "text": line.text,
            }
            for line in transcript
        ]
    if top_terms_limit > 0:
        payload["top_terms"] = _top_terms(transcript, top_terms_limit)
    return payload


def _cross_thread_analysis_payload(
    db_path: Path,
    selector: str,
    *,
    terms: list[str],
    regex: bool,
    case_sensitive: bool,
    limit: int,
    max_text_chars: int,
) -> dict:
    con = _connect_sqlite_ro(db_path)
    cur = con.cursor()
    query_seed = " ".join(terms) if terms else selector
    candidates = _query_db_fts_candidates(cur, query_seed, limit=max(10, limit * 4))
    if not candidates:
        rows = cur.execute(
            """
            SELECT canonical_thread_id, COALESCE(NULLIF(title, ''), '(no title)') AS title, MAX(ts) AS latest_ts
            FROM messages
            WHERE text IS NOT NULL
              AND TRIM(text) <> ''
            GROUP BY canonical_thread_id, title
            ORDER BY latest_ts DESC
            LIMIT ?
            """,
            (max(25, limit * 10),),
        ).fetchall()
        candidates = [
            {
                "canonical_thread_id": row["canonical_thread_id"],
                "title": row["title"],
                "latest_ts": row["latest_ts"],
                "hit_count": 0,
            }
            for row in rows
        ]
    con.close()
    if not candidates:
        return {
            "analysis_scope": "cross_thread",
            "query_terms": terms,
            "results": [],
        }
    results: list[dict] = []
    for candidate in candidates:
        transcript = _build_stitched_transcript(
            _query_thread_messages(db_path, str(candidate["canonical_thread_id"])),
            max_text_chars=max_text_chars,
        )
        if not transcript:
            continue
        analysis = analyze_thread_terms(
            transcript,
            terms=terms or [selector],
            regex=regex,
            case_sensitive=case_sensitive,
            show_line_context=0,
        )
        raw_count = sum(int(item["raw_count"]) for item in analysis["term_stats"])
        line_hits = sum(int(item["line_hit_count"]) for item in analysis["term_stats"])
        if raw_count <= 0:
            continue
        results.append(
            {
                "canonical_thread_id": candidate["canonical_thread_id"],
                "title": candidate["title"],
                "latest_ts": candidate["latest_ts"],
                "message_count": analysis["transcript_stats"]["message_count"],
                "stitched_line_count": analysis["transcript_stats"]["stitched_line_count"],
                "raw_count": raw_count,
                "line_hit_count": line_hits,
                "density_per_100_lines": round((raw_count / analysis["transcript_stats"]["stitched_line_count"]) * 100, 3)
                if analysis["transcript_stats"]["stitched_line_count"]
                else 0.0,
                "density_per_1000_chars": round((raw_count / analysis["transcript_stats"]["character_count"]) * 1000, 3)
                if analysis["transcript_stats"]["character_count"]
                else 0.0,
                "first_hits": analysis["mentions"][:3],
            }
        )
    results.sort(
        key=lambda row: (
            -int(row["raw_count"]),
            -int(row["line_hit_count"]),
            -float(row["density_per_100_lines"]),
            str(row["latest_ts"]),
        )
    )
    return {
        "analysis_scope": "cross_thread",
        "query_terms": terms or [selector],
        "results": results[:limit],
        "best_match": results[0] if results else None,
    }

def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    try:
        runtime = _resolve_runtime_options(
            args,
            repo_root=repo_root,
            parse_terms=_parse_terms,
            parse_range_spec=_parse_range_spec,
            parse_datetime=_parse_datetime,
            extract_online_thread_id=_extract_online_thread_id_from_url,
        )
    except ValueError as exc:
        payload = {"source": "error", "error": str(exc)}
        _print_result(payload, args.json)
        return 2

    exit_code, payload = _resolve_flow(
        args,
        runtime,
        repo_root=repo_root,
        deps=_FlowDependencies(
            resolve_db_lookup=_resolve_db_lookup,
            looks_like_canonical_thread_id=_looks_like_canonical_thread_id,
            looks_like_online_thread_id=_looks_like_online_thread_id,
            query_recent_turns=_query_recent_turns,
            fetch_web_recent_turns=_fetch_web_recent_turns,
            latest_turn_datetime=latest_turn_datetime,
            run_web_view=_run_web_view,
            persist_selector_to_structurer=_persist_selector_to_structurer,
            db_payload=_db_payload,
            cross_thread_analysis_payload=_cross_thread_analysis_payload,
            thread_analysis_payload=_thread_analysis_payload,
            parse_message_ts=_parse_message_ts,
            iso_utc=_iso_utc,
            iso_utc_precise=_iso_utc_precise,
            split_paragraphs=_split_paragraphs,
            truncate_text=truncate_text,
        ),
    )
    _print_result(payload, args.json)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
