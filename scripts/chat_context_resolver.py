#!/usr/bin/env python3
"""Resolve conversation context from structurer DB with optional live fallback."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sqlite3
import subprocess
import sys
import time
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
    fts_query as _fts_query,
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
    build_provider_selector as _build_provider_selector,
    detect_provider as _detect_provider,
    extract_source_thread_id_from_url as _extract_source_thread_id_from_url,
    fetch_web_recent_turns as _fetch_web_recent_turns,
    run_live_download as _run_live_download,
    run_live_view as _run_live_view,
)
from chat_context_resolver_lib.transcript import (
    TranscriptLine,
    build_stitched_transcript,
    filter_transcript_lines,
    latest_turn_datetime,
    truncate_text,
)


class _ProgressReporter:
    def __init__(self, enabled: bool, *, interval: float = 2.0) -> None:
        self.enabled = enabled
        self.interval = max(0.0, interval)
        self.started = time.monotonic()
        self._last_by_stage: dict[str, float] = {}

    def emit(
        self,
        stage: str,
        *,
        done: int | None = None,
        total: int | None = None,
        message: str | None = None,
        force: bool = False,
        **extra: object,
    ) -> None:
        if not self.enabled:
            return
        now = time.monotonic()
        if not force:
            last = self._last_by_stage.get(stage)
            if last is not None and now - last < self.interval:
                return
        self._last_by_stage[stage] = now
        elapsed = now - self.started
        payload: dict[str, object] = {
            "type": "progress",
            "stage": stage,
            "elapsed_s": round(elapsed, 3),
        }
        if done is not None:
            payload["done"] = done
        if total is not None:
            payload["total"] = total
        if done is not None and done > 0:
            rate = done / elapsed if elapsed > 0 else 0.0
            payload["rate_per_s"] = round(rate, 3)
            if total is not None and total >= done and rate > 0:
                payload["eta_s"] = round((total - done) / rate, 3)
        if message:
            payload["message"] = message
        payload.update(extra)
        print(json.dumps(payload, sort_keys=True), file=sys.stderr, flush=True)


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


def _query_thread_messages_with_cursor(
    cur: sqlite3.Cursor,
    thread_id: str,
) -> list[dict]:
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
    return [dict(row) for row in cur.fetchall()]


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


def _fts_tables_ready(cur: sqlite3.Cursor) -> bool:
    cur.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'messages_fts'"
    )
    if cur.fetchone() is None:
        return False
    cur.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'messages_fts_docids'"
    )
    return cur.fetchone() is not None


def _exact_line_stats(text: str, pattern: re.Pattern[str]) -> tuple[int, int, list[tuple[int, re.Match[str], str]]]:
    raw_count = 0
    line_hits = 0
    first_matches: list[tuple[int, re.Match[str], str]] = []
    for line_no, line_text in enumerate(text.splitlines() or [text], start=1):
        matches = list(pattern.finditer(line_text))
        if not matches:
            continue
        raw_count += len(matches)
        line_hits += 1
        for match in matches[: max(0, 3 - len(first_matches))]:
            first_matches.append((line_no, match, line_text))
    return raw_count, line_hits, first_matches


def _cross_thread_analysis_payload_fts(
    db_path: Path,
    selector: str,
    *,
    terms: list[str],
    case_sensitive: bool,
    limit: int,
    max_text_chars: int,
    progress: _ProgressReporter,
) -> dict | None:
    query_terms = terms or [selector]
    query_seed = " ".join(query_terms)
    fts = _fts_query(query_seed)
    if not fts:
        return None

    patterns = [
        (term, re.compile(re.escape(term), 0 if case_sensitive else re.IGNORECASE))
        for term in query_terms
    ]
    con = _connect_sqlite_ro(db_path)
    cur = con.cursor()
    if not _fts_tables_ready(cur):
        con.close()
        return None

    progress.emit("fts_candidate_scan", message="running FTS hit scan", force=True)
    started = time.monotonic()
    rows = cur.execute(
        """
        SELECT
            m.canonical_thread_id AS canonical_thread_id,
            COALESCE(NULLIF(m.title, ''), '(no title)') AS title,
            m.ts AS ts,
            m.role AS role,
            m.text AS text,
            m.message_id AS message_id
        FROM messages_fts
        JOIN messages_fts_docids d ON d.rowid = messages_fts.rowid
        JOIN messages m ON m.message_id = d.message_id
        WHERE messages_fts MATCH ?
          AND m.text IS NOT NULL
          AND TRIM(m.text) <> ''
        ORDER BY m.ts ASC, m.rowid ASC
        """,
        (fts,),
    ).fetchall()
    progress.emit(
        "fts_candidate_scan",
        done=len(rows),
        message="FTS hit rows loaded",
        fts_query=fts,
        force=True,
    )

    by_thread: dict[tuple[str, str], dict] = {}
    processed = 0
    for row in rows:
        processed += 1
        text = str(row["text"] or "")
        term_stats = []
        raw_total = 0
        line_total = 0
        message_hit_terms = 0
        first_matches: list[dict] = []
        for term, pattern in patterns:
            raw_count, line_hits, matches = _exact_line_stats(text, pattern)
            if raw_count <= 0:
                continue
            raw_total += raw_count
            line_total += line_hits
            message_hit_terms += 1
            term_stats.append((term, raw_count, line_hits))
            for line_no, match, line_text in matches:
                first_matches.append(
                    {
                        "term": term,
                        "thread_line_start": None,
                        "thread_line_end": None,
                        "message_index": None,
                        "message_id": row["message_id"],
                        "message_line_start": line_no,
                        "message_line_end": line_no,
                        "role": row["role"],
                        "ts": row["ts"],
                        "ts_utc": _iso_utc_precise(_parse_message_ts(row["ts"])),
                        "matched_text": match.group(0),
                        "line_text": truncate_text(line_text, max_text_chars),
                    }
                )
        if raw_total <= 0:
            progress.emit("hit_aggregation", done=processed, total=len(rows))
            continue

        key = (str(row["canonical_thread_id"]), str(row["title"]))
        item = by_thread.get(key)
        if item is None:
            item = {
                "canonical_thread_id": row["canonical_thread_id"],
                "title": row["title"],
                "latest_ts": row["ts"],
                "hit_message_count": 0,
                "message_count": 0,
                "stitched_line_count": 0,
                "character_count": 0,
                "raw_count": 0,
                "line_hit_count": 0,
                "message_hit_count": 0,
                "term_counts": {term: {"raw_count": 0, "line_hit_count": 0, "message_hit_count": 0} for term in query_terms},
                "first_hits": [],
            }
            by_thread[key] = item
        item["latest_ts"] = max(str(item["latest_ts"] or ""), str(row["ts"] or ""))
        item["hit_message_count"] += 1
        item["message_count"] += 1
        item["stitched_line_count"] += len(text.splitlines() or [text])
        item["character_count"] += len(text)
        item["raw_count"] += raw_total
        item["line_hit_count"] += line_total
        item["message_hit_count"] += 1 if message_hit_terms else 0
        for term, raw_count, line_hits in term_stats:
            stats = item["term_counts"][term]
            stats["raw_count"] += raw_count
            stats["line_hit_count"] += line_hits
            stats["message_hit_count"] += 1
        if len(item["first_hits"]) < 3:
            item["first_hits"].extend(first_matches[: 3 - len(item["first_hits"])])
        progress.emit("hit_aggregation", done=processed, total=len(rows))

    con.close()
    progress.emit(
        "hit_aggregation",
        done=processed,
        total=len(rows),
        message="FTS hit aggregation complete",
        force=True,
    )
    results = []
    for item in by_thread.values():
        chars = int(item.pop("character_count"))
        lines = int(item["stitched_line_count"])
        raw = int(item["raw_count"])
        item["density_per_100_lines"] = round((raw / lines) * 100, 3) if lines else 0.0
        item["density_per_1000_chars"] = round((raw / chars) * 1000, 3) if chars else 0.0
        item["term_stats"] = [
            {"term": term, **stats}
            for term, stats in item.pop("term_counts").items()
            if int(stats["raw_count"]) > 0
        ]
        results.append(item)
    results.sort(
        key=lambda row: (
            -int(row["raw_count"]),
            -int(row["line_hit_count"]),
            -float(row["density_per_100_lines"]),
            str(row["latest_ts"]),
        )
    )
    elapsed = time.monotonic() - started
    return {
        "analysis_scope": "cross_thread",
        "mode": "fts_hit_aggregation",
        "query_terms": query_terms,
        "results": results[:limit],
        "best_match": results[0] if results else None,
        "performance": {
            "fts_query": fts,
            "fts_hit_rows": len(rows),
            "ranked_thread_count": len(results),
            "elapsed_s": round(elapsed, 3),
        },
    }


def _cross_thread_analysis_payload(
    db_path: Path,
    selector: str,
    *,
    terms: list[str],
    regex: bool,
    case_sensitive: bool,
    limit: int,
    max_text_chars: int,
    progress: _ProgressReporter | None = None,
) -> dict:
    progress = progress or _ProgressReporter(False)
    if not regex:
        fast_payload = _cross_thread_analysis_payload_fts(
            db_path,
            selector,
            terms=terms,
            case_sensitive=case_sensitive,
            limit=limit,
            max_text_chars=max_text_chars,
            progress=progress,
        )
        if fast_payload is not None:
            return fast_payload

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
            "mode": "thread_scan_fallback",
            "query_terms": terms,
            "results": [],
        }
    results: list[dict] = []
    total = len(candidates)
    con = _connect_sqlite_ro(db_path)
    cur = con.cursor()
    for idx, candidate in enumerate(candidates, start=1):
        progress.emit("fallback_thread_scan", done=idx - 1, total=total)
        transcript = _build_stitched_transcript(
            _query_thread_messages_with_cursor(cur, str(candidate["canonical_thread_id"])),
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
        progress.emit("fallback_thread_scan", done=idx, total=total)
    con.close()
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
        "mode": "thread_scan_fallback",
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
    provider: str,
) -> dict:
    ingest_script = repo_root / "chat-export-structurer/src/ingest.py"
    if not ingest_script.exists():
        return {"ok": False, "error": f"Missing ingest script: {ingest_script}", "runs": []}

    if not json_paths:
        return {"ok": False, "error": "No downloaded export JSON paths found to ingest.", "runs": []}

    provider_config = {
        "chatgpt": {"format": "chatgpt", "account": "main", "source_prefix": "resolver_auto"},
        "perplexity": {
            "format": "perplexity",
            "account": "perplexity",
            "source_prefix": "resolver_perplexity",
        },
    }.get(provider)
    if provider_config is None:
        return {"ok": False, "error": f"Unsupported ingest provider: {provider}", "runs": []}

    source_id = (
        f"{provider_config['source_prefix']}_"
        f"{dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    )
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
            provider_config["format"],
            "--account",
            provider_config["account"],
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
    provider: str,
    perplexity_scroll_mode: Optional[str] = None,
) -> dict:
    download = _run_live_download(
        provider,
        selector,
        repo_root=repo_root,
        venv_python=venv_python,
        timeout=timeout,
        perplexity_scroll_mode=perplexity_scroll_mode,
    )
    json_paths = _extract_downloaded_json_paths(download.get("stdout") or "", repo_root=repo_root)
    if download.get("output_path"):
        output_path = Path(str(download["output_path"]))
        if not output_path.is_absolute():
            output_path = (repo_root / output_path).resolve()
        if output_path not in json_paths:
            json_paths.append(output_path)
    if not download.get("ok"):
        return {
            "ok": False,
            "download": download,
            "downloaded_json_paths": [str(path) for path in json_paths],
            "ingest": {
                "ok": False,
                "runs": [],
                "ingested_count": 0,
                "error": "Download/export failed or was partial; ingest skipped.",
            },
        }
    ingest = _ingest_exports_to_structurer(
        json_paths=json_paths,
        db_path=db_path,
        venv_python=venv_python,
        repo_root=repo_root,
        timeout=timeout,
        provider=provider,
    )
    return {
        "ok": bool(download.get("ok")) and bool(ingest.get("ok")),
        "download": download,
        "downloaded_json_paths": [str(path) for path in json_paths],
        "ingest": ingest,
    }


def _mca_script_for_mode(mode: str, repo_root: Path) -> Path:
    script_name = {
        "semantic": "mca_semantic_search.py",
        "hybrid": "mca_hybrid_search.py",
    }[mode]
    return repo_root / "scripts" / script_name


def _mca_candidate_id(candidate: dict) -> str | None:
    for key in (
        "canonical_thread_id",
        "thread_id",
        "source_thread_id",
        "online_thread_id",
    ):
        value = candidate.get(key)
        if value is not None and str(value).strip():
            return str(value).strip()
    return None


def _extract_mca_candidates(payload: object) -> list[dict]:
    if isinstance(payload, list):
        source = payload
    elif isinstance(payload, dict):
        source = []
        for key in ("candidates", "results", "matches"):
            value = payload.get(key)
            if isinstance(value, list):
                source = value
                break
    else:
        source = []

    candidates: list[dict] = []
    for index, item in enumerate(source, start=1):
        if isinstance(item, dict):
            candidate = dict(item)
        else:
            candidate = {"value": item}
        candidate.setdefault("rank", index)
        candidates.append(candidate)
    return candidates


def _resolve_mca_candidates(
    db_path: Path,
    candidates: list[dict],
    *,
    max_text_chars: int,
) -> list[dict]:
    if not db_path.exists():
        return candidates

    resolved: list[dict] = []
    for candidate in candidates:
        candidate = dict(candidate)
        candidate_id = _mca_candidate_id(candidate)
        if not candidate_id:
            resolved.append(candidate)
            continue
        try:
            match = _query_db_match(
                db_path,
                candidate_id,
                allow_canonical_match=_looks_like_canonical_thread_id(candidate_id),
            )
        except sqlite3.Error as exc:
            candidate["canonical_resolution_error"] = str(exc)
            resolved.append(candidate)
            continue
        if match is not None:
            candidate["canonical_resolution"] = _db_payload(
                match,
                max_text_chars=max_text_chars,
                latest_paragraphs=False,
                recent_turns=None,
                truncate_text=truncate_text,
                split_paragraphs=_split_paragraphs,
                iso_utc=_iso_utc,
            )
        resolved.append(candidate)
    return resolved


def _run_mca_retrieval(
    *,
    mode: str,
    selector: str,
    repo_root: Path,
    db_path: Path,
    mca_db: Optional[Path],
    limit: int,
    venv_python: Path,
    timeout: int,
    max_text_chars: int,
) -> dict:
    script = _mca_script_for_mode(mode, repo_root)
    requested = {
        "mode": mode,
        "script": str(script),
        "selector": selector,
        "mca_db": str(mca_db) if mca_db is not None else None,
        "limit": max(1, limit),
    }
    if not script.exists():
        return {
            "ok": False,
            "error": f"MyChatArchive {mode} wrapper is unavailable: {script}",
            "requested": requested,
            "candidates": [],
        }

    cmd = [
        str(venv_python),
        str(script),
        selector,
        "--canonical-db",
        str(db_path),
        "--json",
        "--limit",
        str(max(1, limit)),
    ]
    if mca_db is not None:
        cmd.extend(["--mca-db", str(mca_db)])

    try:
        proc = subprocess.run(
            cmd,
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return {
            "ok": False,
            "error": f"MyChatArchive {mode} retrieval timed out after {timeout}s",
            "requested": requested,
            "command": cmd,
            "candidates": [],
        }
    except OSError as exc:
        return {
            "ok": False,
            "error": f"Failed to execute MyChatArchive {mode} retrieval: {exc}",
            "requested": requested,
            "command": cmd,
            "candidates": [],
        }

    try:
        parsed = json.loads(proc.stdout) if proc.stdout.strip() else {}
    except json.JSONDecodeError as exc:
        return {
            "ok": False,
            "error": f"MyChatArchive {mode} wrapper did not emit valid JSON: {exc}",
            "requested": requested,
            "command": cmd,
            "returncode": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "candidates": [],
        }

    candidates = _extract_mca_candidates(parsed)
    return {
        "ok": proc.returncode == 0,
        "mode": mode,
        "requested": requested,
        "command": cmd,
        "returncode": proc.returncode,
        "stderr": proc.stderr,
        "raw": parsed,
        "candidates": _resolve_mca_candidates(
            db_path,
            candidates,
            max_text_chars=max_text_chars,
        ),
    }


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()
    progress = _ProgressReporter(
        bool(getattr(args, "progress", False)),
        interval=float(getattr(args, "progress_interval", 2.0)),
    )
    progress.emit("start", message="resolver started", force=True)

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
    if args.semantic and args.hybrid:
        payload = {"source": "error", "error": "Use only one of --semantic or --hybrid."}
        _print_result(payload, args.json)
        return 2
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
    try:
        selected_provider = _detect_provider(selector_input, args.provider)
    except ValueError as exc:
        payload = {"source": "error", "error": str(exc)}
        _print_result(payload, args.json)
        return 2
    extracted_source_id = _extract_source_thread_id_from_url(
        selector_input,
        provider=selected_provider,
    )
    selector_for_db = extracted_source_id or selector_input
    selector_for_web = _build_provider_selector(
        extracted_source_id or selector_input,
        selected_provider,
    )
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
    mca_mode: Optional[str] = None
    if args.semantic:
        mca_mode = "semantic"
    elif args.hybrid:
        mca_mode = "hybrid"
    mca_db_path: Optional[Path] = None
    if args.mca_db:
        mca_db_path = Path(args.mca_db).expanduser()
        if not mca_db_path.is_absolute():
            mca_db_path = repo_root / mca_db_path

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
    elif args.cross_thread:
        reason = "cross_thread_analysis"
        progress.emit("db_open", message="single-thread DB lookup skipped for cross-thread analysis", force=True)
    else:
        try:
            progress.emit("db_open", message="running DB match lookup", force=True)
            db_match = _query_db_match(
                db_path,
                selector_for_db,
                allow_canonical_match=allow_canonical,
            )
            progress.emit("db_open", message="DB match lookup complete", force=True)
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
        if args.cross_thread:
            needs_web = False
            reason = "cross_thread_analysis"
        elif db_candidates:
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
        if selected_provider == "perplexity":
            extra = "Web freshness check skipped: Perplexity provider uses export-and-ingest."
            db_error = f"{db_error}; {extra}" if db_error else extra
        else:
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
                    web_latest = latest_turn_datetime(
                        web_turns,
                        parse_message_ts=_parse_message_ts,
                    )
                    db_latest = db_match.latest_datetime
                    if web_latest is not None and (db_latest is None or web_latest > db_latest):
                        needs_web = True
                        reason = "web_newer_than_db"
                else:
                    extra = f"Web freshness check failed: {preloaded_web_recent.get('error')}"
                    db_error = f"{db_error}; {extra}" if db_error else extra

    if mca_mode is not None and needs_web and db_match is None and not db_candidates:
        progress.emit("mca_retrieval", message=f"running MyChatArchive {mca_mode} retrieval", force=True)
        mca_result = _run_mca_retrieval(
            mode=mca_mode,
            selector=selector_for_db,
            repo_root=repo_root,
            db_path=db_path,
            mca_db=mca_db_path,
            limit=args.mca_limit,
            venv_python=venv_python_path,
            timeout=args.web_timeout,
            max_text_chars=args.max_text_chars,
        )
        progress.emit("mca_retrieval", message=f"MyChatArchive {mca_mode} retrieval complete", force=True)
        payload = {
            "source": "mca",
            "decision_reason": "mca_candidates_requested_before_web_fallback",
            "mca_retrieval": mca_result,
        }
        if db_error:
            payload["db_warning"] = db_error
        _print_result(payload, args.json)
        return 0 if mca_result.get("ok") else 2

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
            progress=progress,
        )
        if db_error:
            payload["db_warning"] = db_error
        if mca_mode is not None:
            progress.emit("mca_retrieval", message=f"running MyChatArchive {mca_mode} retrieval", force=True)
            mca_result = _run_mca_retrieval(
                mode=mca_mode,
                selector=selector_for_db,
                repo_root=repo_root,
                db_path=db_path,
                mca_db=mca_db_path,
                limit=args.mca_limit,
                venv_python=venv_python_path,
                timeout=args.web_timeout,
                max_text_chars=args.max_text_chars,
            )
            progress.emit("mca_retrieval", message=f"MyChatArchive {mca_mode} retrieval complete", force=True)
            payload["mca_retrieval"] = mca_result
            if not mca_result.get("ok"):
                progress.emit("emit", message="emitting resolver payload", force=True)
                _print_result(payload, args.json)
                return 2
        progress.emit("emit", message="emitting resolver payload", force=True)
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

        live_provider = selected_provider
        if live_provider is None:
            if _looks_like_online_thread_id(selector_for_web):
                payload = {
                    "source": "error",
                    "decision_reason": reason,
                    "error": (
                        "Bare UUID live fallback is ambiguous. Re-run with "
                        "--provider chatgpt or --provider perplexity."
                    ),
                }
                if db_error:
                    payload["db_warning"] = db_error
                _print_result(payload, args.json)
                return 2
            if re.match(r"https?://", selector_for_web, flags=re.IGNORECASE):
                payload = {
                    "source": "error",
                    "decision_reason": reason,
                    "error": (
                        "Unable to auto-detect a supported provider for this URL. "
                        "Use a ChatGPT /c/<uuid> URL, a Perplexity /search/<uuid> URL, "
                        "or pass --provider explicitly."
                    ),
                }
                if db_error:
                    payload["db_warning"] = db_error
                _print_result(payload, args.json)
                return 2
            live_provider = "chatgpt"

        if live_provider == "perplexity":
            persist_result = _persist_selector_to_structurer(
                selector_for_web,
                repo_root=repo_root,
                db_path=db_path,
                venv_python=venv_python_path,
                timeout=args.web_timeout,
                provider=live_provider,
                perplexity_scroll_mode=args.perplexity_scroll_mode,
            )
            if persist_result.get("ok"):
                try:
                    db_match = _query_db_match(
                        db_path,
                        selector_for_db,
                        allow_canonical_match=allow_canonical,
                    )
                except sqlite3.Error as exc:
                    db_match = None
                    extra = f"DB lookup after Perplexity ingest failed: {exc}"
                    db_error = f"{db_error}; {extra}" if db_error else extra

            if persist_result.get("ok") and db_match is not None:
                db_recent_turns = []
                if args.recent_turns > 0:
                    try:
                        db_recent_turns = _query_recent_turns(
                            db_path=db_path,
                            thread_id=db_match.canonical_thread_id,
                            limit=args.recent_turns,
                            max_text_chars=args.max_text_chars,
                        )
                    except sqlite3.Error as exc:
                        extra = f"Unable to load recent turns after ingest: {exc}"
                        db_error = f"{db_error}; {extra}" if db_error else extra
                payload = {
                    "source": "db",
                    "decision_reason": "perplexity_persisted_to_db",
                    "persist": persist_result,
                    "db_match": _db_payload(
                        db_match,
                        max_text_chars=args.max_text_chars,
                        latest_paragraphs=args.latest_paragraphs,
                        recent_turns=db_recent_turns,
                        truncate_text=truncate_text,
                        split_paragraphs=_split_paragraphs,
                        iso_utc=_iso_utc,
                    ),
                }
                if db_error:
                    payload["db_warning"] = db_error
                _print_result(payload, args.json)
                return 0

            payload = {
                "source": "error",
                "decision_reason": reason,
                "error": (
                    "Perplexity export/ingest failed."
                    if not persist_result.get("ok")
                    else "Perplexity export ingested, but the thread was not found in DB afterward."
                ),
                "persist": persist_result,
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

        web_result = _run_live_view(
            live_provider,
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
                    provider=live_provider,
                    perplexity_scroll_mode=args.perplexity_scroll_mode,
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
    if mca_mode is not None:
        progress.emit("mca_retrieval", message=f"running MyChatArchive {mca_mode} retrieval", force=True)
        mca_result = _run_mca_retrieval(
            mode=mca_mode,
            selector=selector_for_db,
            repo_root=repo_root,
            db_path=db_path,
            mca_db=mca_db_path,
            limit=args.mca_limit,
            venv_python=venv_python_path,
            timeout=args.web_timeout,
            max_text_chars=args.max_text_chars,
        )
        progress.emit("mca_retrieval", message=f"MyChatArchive {mca_mode} retrieval complete", force=True)
        payload["mca_retrieval"] = mca_result
        if not mca_result.get("ok"):
            progress.emit("emit", message="emitting resolver payload", force=True)
            _print_result(payload, args.json)
            return 2
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
    progress.emit("emit", message="emitting resolver payload", force=True)
    _print_result(payload, args.json)
    return 0


if __name__ == "__main__":
    sys.exit(main())
