#!/usr/bin/env python3
"""Resolve conversation context from structurer DB with optional live fallback."""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sqlite3
import subprocess
import sys
from pathlib import Path
from typing import Optional

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
from chat_context_resolver_lib.cli import build_parser as _build_parser
from chat_context_resolver_lib.db_lookup import (
    DbMatch,
    connect_sqlite_ro as _connect_sqlite_ro,
    looks_like_canonical_thread_id as _looks_like_canonical_thread_id,
    looks_like_online_thread_id as _looks_like_online_thread_id,
    query_db_fts_candidates as _query_db_fts_candidates,
    query_db_match as _query_db_match,
)
from chat_context_resolver_lib.formatters import (
    db_payload as _db_payload,
    print_result as _print_result,
)
from chat_context_resolver_lib.live_provider import (
    extract_online_thread_id_from_url as _extract_online_thread_id_from_url,
    fetch_web_recent_turns as _fetch_web_recent_turns,
    run_web_download as _run_web_download,
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


def _extract_downloaded_json_paths(stdout: str, repo_root: Path) -> list[Path]:
    paths: list[Path] = []
    seen: set[str] = set()
    pattern = re.compile(r"\bto\s+(.+?\.json)\s*$")
    for raw_line in stdout.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        match = pattern.search(line)
        if not match:
            continue
        raw_path = match.group(1).strip()
        candidate = Path(raw_path)
        if not candidate.is_absolute():
            candidate = (repo_root / candidate).resolve()
        key = str(candidate)
        if key in seen:
            continue
        seen.add(key)
        paths.append(candidate)
    return paths


def _ingest_exports_to_structurer(
    json_paths: list[Path],
    db_path: Path,
    venv_python: Path,
    repo_root: Path,
    timeout: int,
) -> dict:
    ingest_script = repo_root / "chat-export-structurer/src/ingest.py"
    if not ingest_script.exists():
        return {"ok": False, "error": f"Missing ingest script: {ingest_script}", "runs": []}

    if not json_paths:
        return {"ok": False, "error": "No downloaded export JSON paths found to ingest.", "runs": []}

    source_id = f"resolver_auto_{dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    runs = []
    all_ok = True
    for json_path in json_paths:
        if not json_path.exists():
            all_ok = False
            runs.append(
                {
                    "ok": False,
                    "json": str(json_path),
                    "error": "Downloaded export file missing on disk.",
                    "command": [],
                }
            )
            continue

        cmd = [
            str(venv_python),
            str(ingest_script),
            "--in",
            str(json_path),
            "--db",
            str(db_path),
            "--format",
            "chatgpt",
            "--account",
            "main",
            "--source-id",
            source_id,
        ]
        try:
            proc = subprocess.run(
                cmd,
                cwd=str(repo_root),
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
            ok = proc.returncode == 0
            all_ok = all_ok and ok
            runs.append(
                {
                    "ok": ok,
                    "json": str(json_path),
                    "returncode": proc.returncode,
                    "stdout": proc.stdout,
                    "stderr": proc.stderr,
                    "command": cmd,
                    "source_id": source_id,
                }
            )
        except subprocess.TimeoutExpired:
            all_ok = False
            runs.append(
                {
                    "ok": False,
                    "json": str(json_path),
                    "error": f"Ingest timed out after {timeout}s",
                    "command": cmd,
                    "source_id": source_id,
                }
            )
        except OSError as exc:
            all_ok = False
            runs.append(
                {
                    "ok": False,
                    "json": str(json_path),
                    "error": f"Failed to execute ingest command: {exc}",
                    "command": cmd,
                    "source_id": source_id,
                }
            )

    return {
        "ok": all_ok,
        "runs": runs,
        "source_id": source_id,
        "ingested_count": sum(1 for run in runs if run.get("ok")),
    }


def _persist_selector_to_structurer(
    selector: str,
    repo_root: Path,
    db_path: Path,
    venv_python: Path,
    timeout: int,
) -> dict:
    download = _run_web_download(
        selector,
        repo_root=repo_root,
        venv_python=venv_python,
        timeout=timeout,
    )
    json_paths = _extract_downloaded_json_paths(download.get("stdout") or "", repo_root=repo_root)
    ingest = _ingest_exports_to_structurer(
        json_paths=json_paths,
        db_path=db_path,
        venv_python=venv_python,
        repo_root=repo_root,
        timeout=timeout,
    )
    return {
        "ok": bool(download.get("ok")) and bool(ingest.get("ok")),
        "download": download,
        "downloaded_json_paths": [str(path) for path in json_paths],
        "ingest": ingest,
    }


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    db_path = Path(args.db).expanduser()
    if not db_path.is_absolute():
        db_path = repo_root / db_path
    venv_python_path = (
        (repo_root / Path(args.venv_python).expanduser())
        if not Path(args.venv_python).is_absolute()
        else Path(args.venv_python).expanduser()
    )
    analysis_terms = _parse_terms(args.analyze_term)
    if args.term_file:
        term_file = Path(args.term_file).expanduser()
        if not term_file.is_absolute():
            term_file = repo_root / term_file
        if not term_file.exists():
            payload = {"source": "error", "error": f"Term file does not exist: {term_file}"}
            _print_result(payload, args.json)
            return 2
        analysis_terms.extend(
            _parse_terms(
                [line.strip() for line in term_file.read_text(encoding="utf-8").splitlines() if line.strip()]
            )
        )
        analysis_terms = _parse_terms(analysis_terms)
    selector_input = (args.selector or "").strip()
    extracted_online_id = _extract_online_thread_id_from_url(selector_input)
    selector_for_db = extracted_online_id or selector_input
    selector_for_web = extracted_online_id or selector_input
    thread_range: tuple[int, int] | None = None
    message_range: tuple[int, int] | None = None
    try:
        if args.thread_range:
            thread_range = _parse_range_spec(args.thread_range, "--range")
        if args.message_range:
            message_range = _parse_range_spec(args.message_range, "--message-range")
    except ValueError as exc:
        payload = {"source": "error", "error": str(exc)}
        _print_result(payload, args.json)
        return 2
    analysis_requested = bool(
        analysis_terms
        or args.top_terms > 0
        or args.show_lines
        or args.show_line_context > 0
        or thread_range
        or message_range
        or args.cross_thread
        or args.term_frequency
        or args.mention_density
    )

    threshold: Optional[dt.datetime] = None
    if args.if_newer_than:
        try:
            threshold = _parse_datetime(args.if_newer_than)
        except ValueError as exc:
            payload = {"source": "error", "error": f"Invalid --if-newer-than: {exc}"}
            _print_result(payload, args.json)
            return 2

    db_match: Optional[DbMatch] = None
    db_error: Optional[str] = None
    db_candidates: list[dict] = []
    allow_canonical = _looks_like_canonical_thread_id(selector_for_db)
    if not db_path.exists():
        extra = f"DB path does not exist: {db_path}"
        db_error = f"{db_error}; {extra}" if db_error else extra
    else:
        try:
            db_match = _query_db_match(
                db_path,
                selector_for_db,
                allow_canonical_match=allow_canonical,
            )
        except sqlite3.Error as exc:
            extra = f"DB lookup failed: {exc}"
            db_error = f"{db_error}; {extra}" if db_error else extra
        selector_for_candidates = selector_for_db or ""
        if (
            db_match is None
            and len(selector_for_candidates) >= 3
            and not _looks_like_online_thread_id(selector_for_candidates)
            and not _looks_like_canonical_thread_id(selector_for_candidates)
        ):
            # Prefer DB-local candidate suggestions over immediately hitting live web fallback.
            try:
                con = _connect_sqlite_ro(db_path)
                cur = con.cursor()
                db_candidates = _query_db_fts_candidates(
                    cur, selector_for_candidates, limit=10
                )
                con.close()
            except sqlite3.Error as exc:
                extra = f"DB FTS lookup failed: {exc}"
                db_error = f"{db_error}; {extra}" if db_error else extra

    db_recent_turns: list[dict] = []
    if db_match is not None and args.recent_turns > 0:
        try:
            db_recent_turns = _query_recent_turns(
                db_path=db_path,
                thread_id=db_match.canonical_thread_id,
                limit=args.recent_turns,
                max_text_chars=args.max_text_chars,
            )
        except sqlite3.Error as exc:
            extra = f"Unable to load recent turns: {exc}"
            db_error = f"{db_error}; {extra}" if db_error else extra

    needs_web = False
    reason = ""
    if db_match is None:
        if db_candidates:
            needs_web = False
            reason = "db_fts_candidates"
        else:
            needs_web = True
            reason = "not_found_in_db"
    elif threshold is not None:
        latest = db_match.latest_datetime
        if latest is None:
            needs_web = True
            reason = "db_timestamp_unparseable"
        elif threshold > latest:
            needs_web = True
            reason = "provided_datetime_newer_than_db"
        else:
            reason = "db_current_enough"
    else:
        reason = "db_match_found"

    preloaded_web_recent: Optional[dict] = None
    if (
        not needs_web
        and db_match is not None
        and args.check_web_newer
        and not args.no_web
    ):
        preview_limit = max(1, args.recent_turns)
        # Prefer online thread id (UUID) or a title for live lookups; canonical ids
        # are local-only and cannot be resolved by re_gpt.
        web_selector: Optional[str] = None
        if db_match.online_thread_id:
            web_selector = db_match.online_thread_id
        elif _looks_like_online_thread_id(selector_for_web):
            web_selector = selector_for_web
        elif db_match.title and db_match.title != "(no title)":
            web_selector = db_match.title
        if web_selector is None:
            extra = "Web freshness check skipped: no online id or title available"
            db_error = f"{db_error}; {extra}" if db_error else extra
        else:
            preloaded_web_recent = _fetch_web_recent_turns(
                selector=web_selector,
                repo_root=repo_root,
                limit=preview_limit,
                max_text_chars=args.max_text_chars,
                parse_message_ts=_parse_message_ts,
                iso_utc_precise=_iso_utc_precise,
                truncate_text=truncate_text,
            )
            if preloaded_web_recent.get("ok"):
                web_turns = preloaded_web_recent.get("recent_turns") or []
                web_latest = latest_turn_datetime(web_turns, parse_message_ts=_parse_message_ts)
                db_latest = db_match.latest_datetime
                if web_latest is not None and (db_latest is None or web_latest > db_latest):
                    needs_web = True
                    reason = "web_newer_than_db"
            else:
                extra = f"Web freshness check failed: {preloaded_web_recent.get('error')}"
                db_error = f"{db_error}; {extra}" if db_error else extra

    if args.cross_thread and db_path.exists():
        payload = {
            "source": "db",
            "decision_reason": "cross_thread_analysis",
        }
        if db_candidates:
            payload["db_candidates"] = db_candidates
        payload["analysis"] = _cross_thread_analysis_payload(
            db_path,
            args.selector,
            terms=analysis_terms,
            regex=args.regex,
            case_sensitive=args.case_sensitive,
            limit=max(1, args.limit),
            max_text_chars=args.max_text_chars,
        )
        if db_error:
            payload["db_warning"] = db_error
        _print_result(payload, args.json)
        return 0

    if needs_web:
        if args.no_web:
            payload = {
                "source": "error",
                "decision_reason": reason,
                "error": "Web fallback disabled by --no-web.",
            }
            if db_error:
                payload["db_warning"] = db_error
            _print_result(payload, args.json)
            return 1

        web_result = _run_web_view(
            selector_for_web,
            repo_root=repo_root,
            venv_python=venv_python_path,
            timeout=args.web_timeout,
        )
        if web_result.get("ok"):
            web_recent_turns: list[dict] = []
            web_recent_warning: Optional[str] = None
            web_recent_meta: Optional[dict] = None
            if args.recent_turns > 0:
                web_recent = preloaded_web_recent
                if not web_recent or not web_recent.get("ok") or (
                    len(web_recent.get("recent_turns") or []) < args.recent_turns
                ):
                    web_recent = _fetch_web_recent_turns(
                        selector=selector_for_web,
                        repo_root=repo_root,
                        limit=args.recent_turns,
                        max_text_chars=args.max_text_chars,
                        parse_message_ts=_parse_message_ts,
                        iso_utc_precise=_iso_utc_precise,
                        truncate_text=truncate_text,
                    )
                if web_recent.get("ok"):
                    web_recent_turns = web_recent.get("recent_turns") or []
                    web_recent_meta = {
                        "conversation_id": web_recent.get("conversation_id"),
                        "title": web_recent.get("title"),
                        "match_type": web_recent.get("match_type"),
                        "total_message_count": web_recent.get("total_message_count"),
                    }
                else:
                    web_recent_warning = web_recent.get("error")

            payload = {
                "source": "web",
                "decision_reason": reason,
                "web": web_result,
            }
            persist_result: Optional[dict] = None
            if args.persist_web_miss:
                persist_result = _persist_selector_to_structurer(
                    selector_for_web,
                    repo_root=repo_root,
                    db_path=db_path,
                    venv_python=venv_python_path,
                    timeout=args.web_timeout,
                )
                if not persist_result.get("ok"):
                    extra = "Persistence pipeline failed (download and/or ingest)."
                    db_error = f"{db_error}; {extra}" if db_error else extra

            if web_recent_turns:
                payload["web_recent_turns"] = web_recent_turns
            if web_recent_meta is not None:
                payload["web_recent_turns_meta"] = web_recent_meta
            if web_recent_warning:
                payload["web_recent_turns_warning"] = web_recent_warning
            if persist_result is not None:
                payload["persist"] = persist_result
            if db_match is not None:
                payload["db_match"] = _db_payload(
                    db_match,
                    max_text_chars=args.max_text_chars,
                    latest_paragraphs=args.latest_paragraphs,
                    recent_turns=db_recent_turns,
                    truncate_text=truncate_text,
                    split_paragraphs=_split_paragraphs,
                    iso_utc=_iso_utc,
                )
            if db_error:
                payload["db_warning"] = db_error
            _print_result(payload, args.json)
            return 0

        payload = {
            "source": "error",
            "decision_reason": reason,
            "error": web_result.get("error") or "Web fallback failed.",
            "web": web_result,
        }
        if db_match is not None:
            payload["db_match"] = _db_payload(
                db_match,
                max_text_chars=args.max_text_chars,
                latest_paragraphs=args.latest_paragraphs,
                recent_turns=db_recent_turns,
                truncate_text=truncate_text,
                split_paragraphs=_split_paragraphs,
                iso_utc=_iso_utc,
            )
        if db_error:
            payload["db_warning"] = db_error
        _print_result(payload, args.json)
        return 1

    payload = {
        "source": "db",
        "decision_reason": reason,
    }
    if db_match is not None:
        payload["db_match"] = _db_payload(
            db_match,
            max_text_chars=args.max_text_chars,
            latest_paragraphs=args.latest_paragraphs,
            recent_turns=db_recent_turns,
            truncate_text=truncate_text,
            split_paragraphs=_split_paragraphs,
            iso_utc=_iso_utc,
        )
    if db_candidates:
        payload["db_candidates"] = db_candidates
    if threshold is not None:
        payload["requested_threshold_utc"] = _iso_utc(threshold)
    if db_error:
        payload["db_warning"] = db_error
    if analysis_requested:
        if db_match is None:
            payload = {
                "source": "error",
                "decision_reason": reason,
                "error": "Thread-local analysis requires a resolved DB thread. Use --cross-thread for archive-wide ranking.",
            }
            if db_candidates:
                payload["db_candidates"] = db_candidates
            if db_error:
                payload["db_warning"] = db_error
            _print_result(payload, args.json)
            return 1
        payload["analysis"] = _thread_analysis_payload(
            db_path,
            db_match.canonical_thread_id,
            terms=analysis_terms,
            regex=args.regex,
            case_sensitive=args.case_sensitive,
            thread_range=thread_range,
            message_range=message_range,
            show_lines=args.show_lines,
            show_line_context=max(0, args.show_line_context),
            top_terms_limit=max(0, args.top_terms),
            max_text_chars=args.max_text_chars,
        )
    _print_result(payload, args.json)
    return 0


if __name__ == "__main__":
    sys.exit(main())
