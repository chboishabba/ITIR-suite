#!/usr/bin/env python3
"""Resolve conversation context from structurer DB with optional live fallback."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional


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


def _sqlite_ro_uri(path: Path) -> str:
    resolved = path.expanduser().resolve()
    return f"file:{resolved}?mode=ro&immutable=1"


@dataclass
class DbMatch:
    match_type: str
    canonical_thread_id: str
    title: str
    latest_ts: str
    latest_role: str
    latest_text: str
    thread_message_count: int
    matched_thread_count: int
    db_path: str

    @property
    def latest_datetime(self) -> Optional[dt.datetime]:
        return _parse_message_ts(self.latest_ts)


def _fetch_latest_for_thread(
    cur: sqlite3.Cursor, thread_id: str, *, require_text: bool = False
) -> Optional[tuple]:
    text_clause = ""
    if require_text:
        text_clause = "AND text IS NOT NULL AND TRIM(text) <> ''"

    cur.execute(
        f"""
        SELECT canonical_thread_id, COALESCE(NULLIF(title, ''), '(no title)') AS title, ts, role, text
        FROM messages
        WHERE LOWER(canonical_thread_id) = LOWER(?)
          {text_clause}
        ORDER BY ts DESC, rowid DESC
        LIMIT 1
        """,
        (thread_id,),
    )
    row = cur.fetchone()
    if row or not require_text:
        return row

    # If we required text and found nothing, fall back to the absolute latest row.
    return _fetch_latest_for_thread(cur, thread_id, require_text=False)


def _query_thread_message_count(cur: sqlite3.Cursor, thread_id: str) -> int:
    cur.execute(
        "SELECT COUNT(*) FROM messages WHERE LOWER(canonical_thread_id) = LOWER(?)",
        (thread_id,),
    )
    row = cur.fetchone()
    return int(row[0]) if row and row[0] is not None else 0


def _fts_query(selector: str) -> Optional[str]:
    # Avoid arbitrary FTS syntax; convert user input into a safe OR list.
    # Prefix matching helps "wiki" hit "wikipedia", "wikidata", etc.
    tokens = re.findall(r"[A-Za-z0-9_]{2,}", selector.lower())
    if not tokens:
        return None
    seen: set[str] = set()
    uniq: list[str] = []
    for token in tokens:
        if token in seen:
            continue
        seen.add(token)
        uniq.append(token)
    return " OR ".join(f"{token}*" for token in uniq)


def _query_db_fts_candidates(
    cur: sqlite3.Cursor,
    selector: str,
    *,
    limit: int = 10,
) -> list[dict]:
    query = _fts_query(selector)
    if not query:
        return []

    cur.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'messages_fts'"
    )
    if cur.fetchone() is None:
        return []

    # Join via rowid: messages_fts.rowid maps to messages.rowid.
    cur.execute(
        """
        SELECT
            m.canonical_thread_id AS canonical_thread_id,
            COALESCE(NULLIF(m.title, ''), '(no title)') AS title,
            MAX(m.ts) AS latest_ts,
            COUNT(*) AS hit_count
        FROM messages_fts
        JOIN messages m ON m.rowid = messages_fts.rowid
        WHERE messages_fts MATCH ?
        GROUP BY m.canonical_thread_id, title
        ORDER BY hit_count DESC, latest_ts DESC
        LIMIT ?
        """,
        (query, limit),
    )
    rows = cur.fetchall()
    candidates: list[dict] = []
    for row in rows:
        candidates.append(
            {
                "canonical_thread_id": row["canonical_thread_id"],
                "title": row["title"],
                "latest_ts": row["latest_ts"],
                "hit_count": int(row["hit_count"] or 0),
            }
        )
    return candidates


def _query_db_match(db_path: Path, selector: str) -> Optional[DbMatch]:
    if not db_path.exists():
        return None

    con = sqlite3.connect(_sqlite_ro_uri(db_path), uri=True)
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    cur.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'messages'"
    )
    if cur.fetchone() is None:
        con.close()
        return None

    # 1) Exact canonical thread id match.
    row = _fetch_latest_for_thread(cur, selector, require_text=True)
    if row:
        count = _query_thread_message_count(cur, row["canonical_thread_id"])
        con.close()
        return DbMatch(
            match_type="canonical_thread_id_exact",
            canonical_thread_id=row["canonical_thread_id"],
            title=row["title"],
            latest_ts=row["ts"],
            latest_role=row["role"],
            latest_text=row["text"],
            thread_message_count=count,
            matched_thread_count=1,
            db_path=str(db_path.expanduser().resolve()),
        )

    # 2) Exact title match (case-insensitive); choose most recent thread.
    cur.execute(
        """
        SELECT canonical_thread_id, COALESCE(NULLIF(title, ''), '(no title)') AS title, ts, role, text
        FROM messages
        WHERE LOWER(title) = LOWER(?)
          AND text IS NOT NULL
          AND TRIM(text) <> ''
        ORDER BY ts DESC, rowid DESC
        LIMIT 1
        """,
        (selector,),
    )
    exact_title_row = cur.fetchone()
    if exact_title_row:
        cur.execute(
            "SELECT COUNT(DISTINCT canonical_thread_id) FROM messages WHERE LOWER(title) = LOWER(?)",
            (selector,),
        )
        matched_count = int(cur.fetchone()[0])
        thread_id = exact_title_row["canonical_thread_id"]
        count = _query_thread_message_count(cur, thread_id)
        con.close()
        return DbMatch(
            match_type="title_exact",
            canonical_thread_id=thread_id,
            title=exact_title_row["title"],
            latest_ts=exact_title_row["ts"],
            latest_role=exact_title_row["role"],
            latest_text=exact_title_row["text"],
            thread_message_count=count,
            matched_thread_count=matched_count,
            db_path=str(db_path.expanduser().resolve()),
        )

    # 3) Fuzzy title match (contains), only if selector is non-trivial.
    if len(selector.strip()) >= 3:
        like = f"%{selector.strip().lower()}%"
        cur.execute(
            """
            SELECT canonical_thread_id, COALESCE(NULLIF(title, ''), '(no title)') AS title, ts, role, text
            FROM messages
            WHERE LOWER(title) LIKE ?
              AND text IS NOT NULL
              AND TRIM(text) <> ''
            ORDER BY ts DESC, rowid DESC
            LIMIT 1
            """,
            (like,),
        )
        fuzzy_row = cur.fetchone()
        if fuzzy_row:
            cur.execute(
                "SELECT COUNT(DISTINCT canonical_thread_id) FROM messages WHERE LOWER(title) LIKE ?",
                (like,),
            )
            matched_count = int(cur.fetchone()[0])
            thread_id = fuzzy_row["canonical_thread_id"]
            count = _query_thread_message_count(cur, thread_id)
            con.close()
            return DbMatch(
                match_type="title_contains",
                canonical_thread_id=thread_id,
                title=fuzzy_row["title"],
                latest_ts=fuzzy_row["ts"],
                latest_role=fuzzy_row["role"],
                latest_text=fuzzy_row["text"],
                thread_message_count=count,
                matched_thread_count=matched_count,
                db_path=str(db_path.expanduser().resolve()),
            )

    con.close()
    return None


def _load_session_token() -> Optional[str]:
    env_token = os.environ.get("CHATGPT_SESSION_TOKEN", "").strip()
    if env_token:
        return env_token

    session_file = Path.home() / ".chatgpt_session"
    if session_file.exists():
        first_line = session_file.read_text(encoding="utf-8", errors="ignore").splitlines()
        if first_line:
            token = first_line[0].strip()
            if token:
                return token

    return None


def _build_re_gpt_command(
    action: str,
    selector: str,
    token: str,
    repo_root: Path,
    venv_python: Path,
) -> tuple[list[str], dict]:
    env = os.environ.copy()
    module_path = str((repo_root / "reverse-engineered-chatgpt").resolve())
    existing = env.get("PYTHONPATH")
    env["PYTHONPATH"] = module_path if not existing else f"{module_path}:{existing}"
    if action == "download":
        # Keep ConversationStorage writes inside the workspace instead of a possibly read-only $HOME.
        env["HOME"] = str(repo_root)

    if action == "view":
        action_args = ["--nostore", "--view", selector]
    elif action == "download":
        action_args = ["--download", selector]
    else:
        raise ValueError(f"Unsupported re_gpt action: {action}")

    re_gpt_bin = shutil.which("re-gpt")
    if re_gpt_bin:
        return [re_gpt_bin, "--key", token, *action_args], env

    return [
        str(venv_python),
        "-m",
        "re_gpt.cli",
        "--key",
        token,
        *action_args,
    ], env


def _redacted_command(command: list[str]) -> list[str]:
    redacted = list(command)
    for idx, part in enumerate(redacted):
        if part == "--key" and idx + 1 < len(redacted):
            redacted[idx + 1] = "<redacted>"
    return redacted


def _run_re_gpt_action(
    action: str,
    selector: str,
    repo_root: Path,
    venv_python: Path,
    timeout: int,
) -> dict:
    token = _load_session_token()
    if not token:
        return {
            "ok": False,
            "error": (
                "No token found for web fallback. Set CHATGPT_SESSION_TOKEN or create "
                "~/.chatgpt_session (first line = token)."
            ),
        }

    cmd, env = _build_re_gpt_command(
        action,
        selector,
        token=token,
        repo_root=repo_root,
        venv_python=venv_python,
    )
    env["CHATGPT_SESSION_TOKEN"] = token

    def _run(cmdline: list[str]) -> subprocess.CompletedProcess:
        proc = subprocess.run(
            cmdline,
            env=env,
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        return proc

    def _missing_websockets(process: subprocess.CompletedProcess) -> bool:
        return (
            process.returncode != 0
            and "ModuleNotFoundError: No module named 'websockets'" in process.stderr
        )

    try:
        proc = _run(cmd)
    except subprocess.TimeoutExpired:
        return {
            "ok": False,
            "error": f"Web fallback timed out after {timeout}s",
            "command": _redacted_command(cmd),
        }
    except OSError as exc:
        return {
            "ok": False,
            "error": f"Failed to run web fallback: {exc}",
            "command": _redacted_command(cmd),
        }

    retried_with = None
    if _missing_websockets(proc):
        alt_python = repo_root / "reverse-engineered-chatgpt/.venv/bin/python"
        if alt_python.exists():
            alt_cmd, _ = _build_re_gpt_command(
                action,
                selector,
                token=token,
                repo_root=repo_root,
                venv_python=alt_python,
            )
            if alt_cmd[0] != cmd[0]:
                try:
                    alt_proc = _run(alt_cmd)
                    proc = alt_proc
                    cmd = alt_cmd
                    retried_with = str(alt_python)
                except (subprocess.TimeoutExpired, OSError):
                    pass

    extra_error = None
    if proc.returncode != 0 and "Could not resolve host: chatgpt.com" in proc.stderr:
        extra_error = (
            "Web fallback failed due DNS/network resolution for chatgpt.com. "
            "Run in an environment with outbound network access."
        )
    elif proc.returncode != 0 and "attempt to write a readonly database" in proc.stderr:
        extra_error = (
            "Web action failed because SQLite storage path is read-only in this environment."
        )
    elif _missing_websockets(proc):
        extra_error = (
            "Web fallback failed because dependency 'websockets' is missing in the selected "
            "Python environment. Install reverse-engineered-chatgpt requirements first."
        )

    return {
        "ok": proc.returncode == 0,
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "command": _redacted_command(cmd),
        "error": extra_error,
        "retried_with_python": retried_with,
    }


def _run_web_view(selector: str, repo_root: Path, venv_python: Path, timeout: int) -> dict:
    return _run_re_gpt_action(
        action="view",
        selector=selector,
        repo_root=repo_root,
        venv_python=venv_python,
        timeout=timeout,
    )


def _run_web_download(selector: str, repo_root: Path, venv_python: Path, timeout: int) -> dict:
    return _run_re_gpt_action(
        action="download",
        selector=selector,
        repo_root=repo_root,
        venv_python=venv_python,
        timeout=timeout,
    )


def _looks_like_conversation_id(selector: str) -> bool:
    return bool(
        re.fullmatch(
            r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}",
            selector.strip(),
        )
    )


def _resolve_live_conversation(chatgpt: object, selector: str) -> Optional[dict]:
    normalized = selector.strip()
    if not normalized:
        return None
    if _looks_like_conversation_id(normalized):
        return {
            "conversation_id": normalized,
            "title": None,
            "match_type": "conversation_id",
        }

    target = normalized.lower()
    fallback_contains: Optional[dict] = None
    offset = 0
    limit = 100
    while True:
        page = chatgpt.list_conversations_page(offset=offset, limit=limit)
        items = page.get("items", []) if isinstance(page, dict) else []
        if not items:
            break
        for item in items:
            title = (item.get("title") or "").strip()
            conversation_id = item.get("id")
            if not title or not conversation_id:
                continue
            lowered = title.lower()
            if lowered == target:
                return {
                    "conversation_id": conversation_id,
                    "title": title,
                    "match_type": "title_exact",
                }
            if target in lowered and fallback_contains is None:
                fallback_contains = {
                    "conversation_id": conversation_id,
                    "title": title,
                    "match_type": "title_contains",
                }
        offset += len(items)
        if len(items) < limit:
            break
    return fallback_contains


def _fetch_web_recent_turns(
    selector: str,
    repo_root: Path,
    limit: int,
    max_text_chars: int,
) -> dict:
    if limit <= 0:
        return {"ok": True, "recent_turns": []}

    token = _load_session_token()
    if not token:
        return {
            "ok": False,
            "error": (
                "No token found for live message timestamp fetch. Set CHATGPT_SESSION_TOKEN "
                "or create ~/.chatgpt_session (first line = token)."
            ),
        }

    module_path = str((repo_root / "reverse-engineered-chatgpt").resolve())
    if module_path not in sys.path:
        sys.path.insert(0, module_path)

    try:
        from re_gpt.storage import extract_ordered_messages
        from re_gpt.sync_chatgpt import SyncChatGPT
    except Exception as exc:
        return {
            "ok": False,
            "error": f"Unable to import reverse-engineered-chatgpt modules: {exc}",
        }

    try:
        with SyncChatGPT(session_token=token) as chatgpt:
            resolved = _resolve_live_conversation(chatgpt, selector)
            if not resolved:
                return {
                    "ok": False,
                    "error": f"Unable to resolve conversation selector for live turns: {selector}",
                }

            conversation = chatgpt.get_conversation(
                resolved["conversation_id"],
                title=resolved.get("title"),
            )
            chat = conversation.fetch_chat()
            ordered = extract_ordered_messages(chat)
            selected = ordered[-limit:]
            start_pos = max(1, len(ordered) - len(selected) + 1)
            turns: list[dict] = []
            for idx, message in enumerate(selected, start=start_pos):
                parsed_ts = _parse_message_ts(message.get("create_time"))
                turns.append(
                    {
                        "position": idx,
                        "ts": message.get("create_time"),
                        "ts_utc": _iso_utc_precise(parsed_ts),
                        "role": message.get("author"),
                        "text": _truncate_text(
                            str(message.get("content") or ""),
                            max_text_chars,
                        ),
                    }
                )
            return {
                "ok": True,
                "conversation_id": resolved["conversation_id"],
                "title": conversation.title or resolved.get("title"),
                "match_type": resolved.get("match_type"),
                "total_message_count": len(ordered),
                "recent_turns": turns,
            }
    except Exception as exc:
        return {
            "ok": False,
            "error": f"Live turn fetch failed: {exc}",
        }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Resolve conversation context by querying structurer DB first, then "
            "fallback to re-gpt --view when missing/stale."
        )
    )
    parser.add_argument("selector", help="Conversation canonical_thread_id or title selector")
    parser.add_argument(
        "--db",
        default="chat-export-structurer/my_archive.sqlite",
        help="Path to chat-export-structurer SQLite archive (default: %(default)s)",
    )
    parser.add_argument(
        "--if-newer-than",
        help=(
            "Datetime (ISO8601 or epoch). If this is newer than DB latest timestamp, "
            "force web fallback."
        ),
    )
    parser.add_argument(
        "--venv-python",
        default=".venv/bin/python",
        help="Python interpreter for module fallback to re_gpt.cli (default: %(default)s)",
    )
    parser.add_argument(
        "--web-timeout",
        type=int,
        default=120,
        help="Timeout seconds for web fallback command (default: %(default)s)",
    )
    parser.add_argument(
        "--no-web",
        action="store_true",
        help="Do not run web fallback; fail if DB does not satisfy the request.",
    )
    parser.add_argument(
        "--persist-web-miss",
        action="store_true",
        help=(
            "When DB lookup misses and web fallback runs, also run export download + "
            "ingest into structurer DB. Disabled by default for faster lookups."
        ),
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON output.",
    )
    parser.add_argument(
        "--max-text-chars",
        type=int,
        default=1200,
        help=(
            "Max characters of latest DB message to return/print "
            "(default: %(default)s, use 0 for unlimited)."
        ),
    )
    parser.add_argument(
        "--latest-paragraphs",
        action="store_true",
        help="Include latest DB message split into a paragraph list.",
    )
    parser.add_argument(
        "--recent-turns",
        type=int,
        default=0,
        help=(
            "Include the most recent N turns with per-message timestamps "
            "(DB when source=db; live fetch when source=web)."
        ),
    )
    parser.add_argument(
        "--check-web-newer",
        action="store_true",
        help=(
            "When DB has a match, fetch live recent turn timestamps and prefer web "
            "if web appears newer than DB."
        ),
    )
    return parser


def _truncate_text(text: str, max_chars: int) -> str:
    if max_chars <= 0 or len(text) <= max_chars:
        return text
    omitted = len(text) - max_chars
    return f"{text[:max_chars]}\n...[truncated {omitted} chars]"


def _split_paragraphs(text: str) -> list[str]:
    return [chunk.strip() for chunk in re.split(r"\n\s*\n+", text) if chunk.strip()]


def _latest_turn_datetime(turns: list[dict]) -> Optional[dt.datetime]:
    latest: Optional[dt.datetime] = None
    for turn in turns:
        parsed = _parse_message_ts(turn.get("ts_utc") or turn.get("ts"))
        if parsed is None:
            continue
        if latest is None or parsed > latest:
            latest = parsed
    return latest


def _query_recent_turns(
    db_path: Path,
    thread_id: str,
    limit: int,
    max_text_chars: int,
) -> list[dict]:
    if limit <= 0:
        return []

    con = sqlite3.connect(_sqlite_ro_uri(db_path), uri=True)
    con.row_factory = sqlite3.Row
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
                "text": _truncate_text(row["text"] or "", max_text_chars),
            }
        )
    return turns


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


def _db_payload(
    match: DbMatch,
    max_text_chars: int,
    latest_paragraphs: bool = False,
    recent_turns: Optional[list[dict]] = None,
) -> dict:
    latest_text_full = match.latest_text or ""
    payload = {
        **asdict(match),
        "latest_ts_utc": _iso_utc(match.latest_datetime),
    }
    payload["latest_text"] = _truncate_text(latest_text_full, max_text_chars)
    if latest_paragraphs:
        payload["latest_paragraphs"] = [
            _truncate_text(paragraph, max_text_chars)
            for paragraph in _split_paragraphs(latest_text_full)
        ]
    if recent_turns:
        payload["recent_turns"] = recent_turns
    return payload


def _print_result(payload: dict, as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return

    source = payload.get("source", "unknown")
    print(f"source: {source}")
    reason = payload.get("decision_reason")
    if reason:
        print(f"decision_reason: {reason}")
    persist = payload.get("persist") or {}
    if persist:
        print(f"persist_ok: {persist.get('ok')}")
        downloaded = persist.get("downloaded_json_paths") or []
        if downloaded:
            print(f"persist_downloaded_json_count: {len(downloaded)}")
        ingest = persist.get("ingest") or {}
        if ingest:
            print(f"persist_ingested_count: {ingest.get('ingested_count', 0)}")

    if source == "db":
        db = payload.get("db_match") or {}
        candidates = payload.get("db_candidates") or []

        if db:
            print(f"match_type: {db.get('match_type')}")
            print(f"title: {db.get('title')}")
            print(f"canonical_thread_id: {db.get('canonical_thread_id')}")
            print(f"latest_ts_utc: {db.get('latest_ts_utc')}")
            print(f"latest_role: {db.get('latest_role')}")
            print(f"thread_message_count: {db.get('thread_message_count')}")
            print(f"matched_thread_count: {db.get('matched_thread_count')}")
            print("latest_text:")
            print(db.get("latest_text", ""))

            latest_paragraphs = db.get("latest_paragraphs") or []
            if latest_paragraphs:
                print("latest_paragraphs:")
                for idx, paragraph in enumerate(latest_paragraphs, start=1):
                    print(f"[{idx}] {paragraph}")
            recent_turns = db.get("recent_turns") or []
            if recent_turns:
                print("recent_turns:")
                for idx, turn in enumerate(recent_turns, start=1):
                    print(
                        f"[{idx}] ts={turn.get('ts')} "
                        f"ts_utc={turn.get('ts_utc')} role={turn.get('role')}:"
                    )
                    print(turn.get("text", ""))
        else:
            print("db_match: (none)")

        if candidates:
            print("db_candidates:")
            for idx, candidate in enumerate(candidates, start=1):
                print(
                    f"[{idx}] hits={candidate.get('hit_count')} "
                    f"latest_ts={candidate.get('latest_ts')} "
                    f"id={candidate.get('canonical_thread_id')} "
                    f"title={candidate.get('title')}"
                )
        return

    if source == "web":
        web = payload.get("web", {})
        print("web_command:")
        print(" ".join(web.get("command", [])))
        if web.get("stderr"):
            print("web_stderr:")
            print(web["stderr"].rstrip())
        live_warning = payload.get("web_recent_turns_warning")
        if live_warning:
            print(f"web_recent_turns_warning: {live_warning}")
        live_turns = payload.get("web_recent_turns") or []
        if live_turns:
            print("web_recent_turns:")
            for idx, turn in enumerate(live_turns, start=1):
                print(
                    f"[{idx}] ts={turn.get('ts')} "
                    f"ts_utc={turn.get('ts_utc')} role={turn.get('role')}:"
                )
                print(turn.get("text", ""))
        print("web_stdout:")
        print((web.get("stdout") or "").rstrip())
        return

    print(payload.get("error", "unknown error"))


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
    if not db_path.exists():
        extra = f"DB path does not exist: {db_path}"
        db_error = f"{db_error}; {extra}" if db_error else extra
    else:
        try:
            db_match = _query_db_match(db_path, args.selector)
        except sqlite3.Error as exc:
            extra = f"DB lookup failed: {exc}"
            db_error = f"{db_error}; {extra}" if db_error else extra
        if db_match is None and len(args.selector.strip()) >= 3:
            # Prefer DB-local candidate suggestions over immediately hitting live web fallback.
            try:
                con = sqlite3.connect(_sqlite_ro_uri(db_path), uri=True)
                con.row_factory = sqlite3.Row
                cur = con.cursor()
                db_candidates = _query_db_fts_candidates(cur, args.selector, limit=10)
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
        preloaded_web_recent = _fetch_web_recent_turns(
            selector=db_match.canonical_thread_id,
            repo_root=repo_root,
            limit=preview_limit,
            max_text_chars=args.max_text_chars,
        )
        if preloaded_web_recent.get("ok"):
            web_turns = preloaded_web_recent.get("recent_turns") or []
            web_latest = _latest_turn_datetime(web_turns)
            db_latest = db_match.latest_datetime
            if web_latest is not None and (db_latest is None or web_latest > db_latest):
                needs_web = True
                reason = "web_newer_than_db"
        else:
            extra = f"Web freshness check failed: {preloaded_web_recent.get('error')}"
            db_error = f"{db_error}; {extra}" if db_error else extra

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
            args.selector,
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
                        selector=args.selector,
                        repo_root=repo_root,
                        limit=args.recent_turns,
                        max_text_chars=args.max_text_chars,
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
                    args.selector,
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
                    args.max_text_chars,
                    latest_paragraphs=args.latest_paragraphs,
                    recent_turns=db_recent_turns,
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
                args.max_text_chars,
                latest_paragraphs=args.latest_paragraphs,
                recent_turns=db_recent_turns,
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
            args.max_text_chars,
            latest_paragraphs=args.latest_paragraphs,
            recent_turns=db_recent_turns,
        )
    if db_candidates:
        payload["db_candidates"] = db_candidates
    if threshold is not None:
        payload["requested_threshold_utc"] = _iso_utc(threshold)
    if db_error:
        payload["db_warning"] = db_error
    _print_result(payload, args.json)
    return 0


if __name__ == "__main__":
    sys.exit(main())
