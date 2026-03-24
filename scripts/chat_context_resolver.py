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


_TOKEN_RE = re.compile(r"[A-Za-z0-9_]{2,}")
_ONLINE_THREAD_ID_FROM_URL_RE = re.compile(
    r"/c/([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})"
)
_DEFAULT_STOPWORDS = {
    "the",
    "and",
    "for",
    "that",
    "with",
    "this",
    "from",
    "have",
    "your",
    "were",
    "what",
    "when",
    "where",
    "which",
    "would",
    "could",
    "should",
    "into",
    "about",
    "there",
    "their",
    "they",
    "them",
    "then",
    "than",
    "just",
    "also",
    "because",
    "while",
    "been",
    "being",
    "over",
    "under",
    "more",
    "most",
    "some",
    "will",
    "need",
    "next",
    "task",
}


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

def _connect_sqlite_ro(db_path: Path) -> sqlite3.Connection:
    """Open an immutable read-only connection with temp-store hardening.

    SQLite can choose a temp-file backed store for sorts/group-bys/FTS joins.
    In some environments that yields opaque `SQLITE_CANTOPEN` errors during
    stepping. Prefer in-memory temp storage for robustness.
    """

    con = sqlite3.connect(_sqlite_ro_uri(db_path), uri=True)
    con.row_factory = sqlite3.Row
    try:
        con.execute("PRAGMA temp_store=MEMORY")
        con.execute("PRAGMA query_only=ON")
    except sqlite3.Error:
        # Best-effort hardening: don't fail resolver if PRAGMAs are unavailable.
        pass
    return con


@dataclass
class DbMatch:
    match_type: str
    canonical_thread_id: str
    online_thread_id: Optional[str]
    title: str
    earliest_ts: Optional[str]
    latest_ts: str
    latest_role: str
    latest_text: str
    thread_message_count: int
    matched_thread_count: int
    db_path: str

    @property
    def latest_datetime(self) -> Optional[dt.datetime]:
        return _parse_message_ts(self.latest_ts)

    @property
    def earliest_datetime(self) -> Optional[dt.datetime]:
        return _parse_message_ts(self.earliest_ts)


@dataclass
class TranscriptLine:
    thread_line: int
    message_index: int
    message_id: str
    role: str
    ts: str
    ts_utc: Optional[str]
    message_line: int
    text: str


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


def _query_thread_span(cur: sqlite3.Cursor, thread_id: str) -> tuple[int, Optional[str], Optional[str]]:
    cur.execute(
        """
        SELECT COUNT(*) AS message_count, MIN(ts) AS earliest_ts, MAX(ts) AS latest_ts
        FROM messages
        WHERE LOWER(canonical_thread_id) = LOWER(?)
        """,
        (thread_id,),
    )
    row = cur.fetchone()
    if not row:
        return 0, None, None
    return (
        int(row["message_count"] or 0),
        row["earliest_ts"],
        row["latest_ts"],
    )


def _fetch_latest_for_online_thread_id(
    cur: sqlite3.Cursor, online_thread_id: str, *, require_text: bool = False
) -> Optional[tuple]:
    text_clause = ""
    if require_text:
        text_clause = "AND text IS NOT NULL AND TRIM(text) <> ''"

    cur.execute(
        f"""
        SELECT canonical_thread_id, source_thread_id, COALESCE(NULLIF(title, ''), '(no title)') AS title, ts, role, text
        FROM messages
        WHERE LOWER(source_thread_id) = LOWER(?)
          {text_clause}
        ORDER BY ts DESC, rowid DESC
        LIMIT 1
        """,
        (online_thread_id,),
    )
    row = cur.fetchone()
    if row or not require_text:
        return row
    return _fetch_latest_for_online_thread_id(cur, online_thread_id, require_text=False)


def _query_online_thread_span(
    cur: sqlite3.Cursor, online_thread_id: str
) -> tuple[int, Optional[str], Optional[str]]:
    cur.execute(
        """
        SELECT COUNT(*) AS message_count, MIN(ts) AS earliest_ts, MAX(ts) AS latest_ts
        FROM messages
        WHERE LOWER(source_thread_id) = LOWER(?)
        """,
        (online_thread_id,),
    )
    row = cur.fetchone()
    if not row:
        return 0, None, None
    return (
        int(row["message_count"] or 0),
        row["earliest_ts"],
        row["latest_ts"],
    )


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


def _query_db_match(
    db_path: Path, selector: str, *, allow_canonical_match: bool = False
) -> Optional[DbMatch]:
    if not db_path.exists():
        return None

    con = _connect_sqlite_ro(db_path)
    cur = con.cursor()

    cur.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'messages'"
    )
    if cur.fetchone() is None:
        con.close()
        return None

    # 1) Exact online thread id match.
    online_row = _fetch_latest_for_online_thread_id(cur, selector, require_text=True)
    if online_row:
        count, earliest_ts, latest_ts = _query_online_thread_span(
            cur, str(online_row["source_thread_id"])
        )
        con.close()
        return DbMatch(
            match_type="online_thread_id_exact",
            canonical_thread_id=online_row["canonical_thread_id"],
            online_thread_id=online_row["source_thread_id"],
            title=online_row["title"],
            earliest_ts=earliest_ts,
            latest_ts=latest_ts or online_row["ts"],
            latest_role=online_row["role"],
            latest_text=online_row["text"],
            thread_message_count=count,
            matched_thread_count=1,
            db_path=str(db_path.expanduser().resolve()),
        )

    # 2) Exact canonical thread id match.
    if allow_canonical_match:
        row = _fetch_latest_for_thread(cur, selector, require_text=True)
        if row:
            count, earliest_ts, latest_ts = _query_thread_span(
                cur, row["canonical_thread_id"]
            )
            con.close()
            return DbMatch(
                match_type="canonical_thread_id_exact",
                canonical_thread_id=row["canonical_thread_id"],
                online_thread_id=None,
                title=row["title"],
                earliest_ts=earliest_ts,
                latest_ts=latest_ts or row["ts"],
                latest_role=row["role"],
                latest_text=row["text"],
                thread_message_count=count,
                matched_thread_count=1,
                db_path=str(db_path.expanduser().resolve()),
            )

    # 3) Exact title match (case-insensitive); choose most recent thread.
    cur.execute(
        """
        SELECT canonical_thread_id, source_thread_id, COALESCE(NULLIF(title, ''), '(no title)') AS title, ts, role, text
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
        count, earliest_ts, latest_ts = _query_thread_span(cur, thread_id)
        con.close()
        return DbMatch(
            match_type="title_exact",
            canonical_thread_id=thread_id,
            online_thread_id=exact_title_row["source_thread_id"],
            title=exact_title_row["title"],
            earliest_ts=earliest_ts,
            latest_ts=latest_ts or exact_title_row["ts"],
            latest_role=exact_title_row["role"],
            latest_text=exact_title_row["text"],
            thread_message_count=count,
            matched_thread_count=matched_count,
            db_path=str(db_path.expanduser().resolve()),
        )

    # 4) Fuzzy title match (contains), only if selector is non-trivial.
    if len(selector.strip()) >= 3:
        like = f"%{selector.strip().lower()}%"
        cur.execute(
            """
            SELECT canonical_thread_id, source_thread_id, COALESCE(NULLIF(title, ''), '(no title)') AS title, ts, role, text
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
            count, earliest_ts, latest_ts = _query_thread_span(cur, thread_id)
            con.close()
            return DbMatch(
                match_type="title_contains",
                canonical_thread_id=thread_id,
                online_thread_id=fuzzy_row["source_thread_id"],
                title=fuzzy_row["title"],
                earliest_ts=earliest_ts,
                latest_ts=latest_ts or fuzzy_row["ts"],
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

    # Prefer the repo/venv module path so resolver behavior matches the local
    # reverse-engineered-chatgpt environment instead of an unrelated pipx install.
    if venv_python.exists():
        return [
            str(venv_python),
            "-m",
            "re_gpt.cli",
            "--key",
            token,
            *action_args,
        ], env

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


def _looks_like_online_thread_id(selector: str) -> bool:
    return bool(
        re.fullmatch(
            r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}",
            selector.strip(),
        )
    )


def _looks_like_canonical_thread_id(selector: str) -> bool:
    return bool(re.fullmatch(r"[0-9a-f]{40}", selector.strip().lower()))


def _extract_online_thread_id_from_url(selector: str) -> Optional[str]:
    match = _ONLINE_THREAD_ID_FROM_URL_RE.search(selector)
    if match:
        return match.group(1)
    return None


def _resolve_live_conversation(chatgpt: object, selector: str) -> Optional[dict]:
    normalized = selector.strip()
    if not normalized:
        return None
    if _looks_like_online_thread_id(normalized):
        return {
            "conversation_id": normalized,
            "title": None,
            "match_type": "online_thread_id",
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
    parser.add_argument(
        "selector",
        help="Conversation selector: online_thread_id, canonical_thread_id, or title",
    )
    parser.add_argument(
        "--db",
        default="~/chat_archive.sqlite",
        help="Path to canonical chat archive SQLite DB (default: %(default)s)",
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
    parser.add_argument(
        "--analyze-term",
        action="append",
        default=[],
        help="Analyze one or more terms (comma-separated allowed) against the resolved thread or cross-thread result set.",
    )
    parser.add_argument(
        "--term-file",
        help="Read additional analysis terms from a file (one term per line).",
    )
    parser.add_argument(
        "--case-sensitive",
        action="store_true",
        help="Use case-sensitive term matching for analysis mode.",
    )
    parser.add_argument(
        "--regex",
        action="store_true",
        help="Treat analysis terms as regular expressions instead of exact substrings.",
    )
    parser.add_argument(
        "--range",
        dest="thread_range",
        help="Restrict thread-local analysis to stitched transcript lines START:END.",
    )
    parser.add_argument(
        "--message-range",
        help="Restrict thread-local analysis to message ordinals START:END.",
    )
    parser.add_argument(
        "--show-lines",
        action="store_true",
        help="Include stitched transcript lines in thread-local analysis output.",
    )
    parser.add_argument(
        "--show-line-context",
        type=int,
        default=0,
        help="For each mention, include N surrounding stitched transcript lines.",
    )
    parser.add_argument(
        "--term-frequency",
        action="store_true",
        help="Emit term frequency statistics for analysis terms.",
    )
    parser.add_argument(
        "--mention-density",
        action="store_true",
        help="Emit mention density metrics for analysis terms.",
    )
    parser.add_argument(
        "--top-terms",
        type=int,
        default=0,
        help="Include the top N simple lexical terms for the selected transcript slice.",
    )
    parser.add_argument(
        "--cross-thread",
        action="store_true",
        help="Run archive-wide ranking for the analysis terms instead of a single resolved thread.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Max rows for cross-thread analysis results (default: %(default)s).",
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
                "text": _truncate_text(row["text"] or "", max_text_chars),
            }
        )
    return turns


def _parse_terms(values: list[str]) -> list[str]:
    terms: list[str] = []
    seen: set[str] = set()
    for raw in values:
        for chunk in str(raw or "").split(","):
            term = chunk.strip()
            if not term:
                continue
            key = term.casefold()
            if key in seen:
                continue
            seen.add(key)
            terms.append(term)
    return terms


def _compile_pattern(term: str, *, regex: bool, case_sensitive: bool) -> re.Pattern[str]:
    flags = 0 if case_sensitive else re.IGNORECASE
    return re.compile(term if regex else re.escape(term), flags)


def _parse_range_spec(spec: str, label: str) -> tuple[int, int]:
    match = re.fullmatch(r"\s*(\d+)\s*:\s*(\d+)\s*", spec or "")
    if not match:
        raise ValueError(f"Invalid {label}: expected START:END")
    start = int(match.group(1))
    end = int(match.group(2))
    if start <= 0 or end <= 0:
        raise ValueError(f"Invalid {label}: values must be >= 1")
    if start > end:
        raise ValueError(f"Invalid {label}: start must be <= end")
    return start, end


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


def _build_stitched_transcript(rows: list[dict], *, max_text_chars: int = 0) -> list[TranscriptLine]:
    transcript: list[TranscriptLine] = []
    thread_line = 0
    for message_index, row in enumerate(rows, start=1):
        raw_text = str(row.get("text") or "")
        lines = raw_text.splitlines() or [raw_text]
        parsed_ts = _parse_message_ts(row.get("ts"))
        for message_line, line_text in enumerate(lines, start=1):
            thread_line += 1
            transcript.append(
                TranscriptLine(
                    thread_line=thread_line,
                    message_index=message_index,
                    message_id=str(row.get("message_id") or f"thread-msg-{message_index}"),
                    role=str(row.get("role") or ""),
                    ts=str(row.get("ts") or ""),
                    ts_utc=_iso_utc_precise(parsed_ts),
                    message_line=message_line,
                    text=_truncate_text(line_text, max_text_chars) if max_text_chars else line_text,
                )
            )
    return transcript


def _filter_transcript_lines(
    transcript: list[TranscriptLine],
    *,
    thread_range: tuple[int, int] | None,
    message_range: tuple[int, int] | None,
) -> list[TranscriptLine]:
    out: list[TranscriptLine] = []
    for line in transcript:
        if thread_range and not (thread_range[0] <= line.thread_line <= thread_range[1]):
            continue
        if message_range and not (message_range[0] <= line.message_index <= message_range[1]):
            continue
        out.append(line)
    return out


def _window_excerpt(
    transcript: list[TranscriptLine],
    line: TranscriptLine,
    before: int,
    after: int,
) -> list[dict]:
    start = max(1, line.thread_line - before)
    end = min(len(transcript), line.thread_line + after)
    return [
        {
            "thread_line": item.thread_line,
            "message_index": item.message_index,
            "message_line": item.message_line,
            "role": item.role,
            "ts": item.ts,
            "text": item.text,
        }
        for item in transcript[start - 1 : end]
    ]


def _analyze_thread_terms(
    transcript: list[TranscriptLine],
    *,
    terms: list[str],
    regex: bool,
    case_sensitive: bool,
    show_line_context: int,
) -> dict:
    text_joined = "\n".join(line.text for line in transcript)
    message_ids = {line.message_id for line in transcript}
    message_count = len({line.message_index for line in transcript})
    line_count = len(transcript)
    char_count = len(text_joined)
    term_stats: list[dict] = []
    mentions: list[dict] = []
    for term in terms:
        pattern = _compile_pattern(term, regex=regex, case_sensitive=case_sensitive)
        raw_count = 0
        line_hits: set[int] = set()
        message_hits: set[int] = set()
        for line in transcript:
            matches = list(pattern.finditer(line.text))
            if not matches:
                continue
            raw_count += len(matches)
            line_hits.add(line.thread_line)
            message_hits.add(line.message_index)
            for match in matches:
                mention = {
                    "term": term,
                    "thread_line_start": line.thread_line,
                    "thread_line_end": line.thread_line,
                    "message_index": line.message_index,
                    "message_id": line.message_id,
                    "message_line_start": line.message_line,
                    "message_line_end": line.message_line,
                    "role": line.role,
                    "ts": line.ts,
                    "ts_utc": line.ts_utc,
                    "matched_text": match.group(0),
                    "line_text": line.text,
                }
                if show_line_context > 0:
                    mention["line_context"] = _window_excerpt(
                        transcript,
                        line,
                        before=show_line_context,
                        after=show_line_context,
                    )
                mentions.append(mention)
        term_stats.append(
            {
                "term": term,
                "raw_count": raw_count,
                "line_hit_count": len(line_hits),
                "message_hit_count": len(message_hits),
                "density_per_100_lines": round((raw_count / line_count) * 100, 3) if line_count else 0.0,
                "density_per_1000_chars": round((raw_count / char_count) * 1000, 3) if char_count else 0.0,
                "density_per_100_messages": round((raw_count / message_count) * 100, 3) if message_count else 0.0,
            }
        )
    return {
        "transcript_stats": {
            "message_count": message_count,
            "stitched_line_count": line_count,
            "character_count": char_count,
            "message_id_count": len(message_ids),
        },
        "term_stats": term_stats,
        "mentions": mentions,
    }


def _top_terms(transcript: list[TranscriptLine], limit: int) -> list[dict]:
    counts: dict[str, int] = {}
    for line in transcript:
        for token in _TOKEN_RE.findall(line.text.casefold()):
            if token in _DEFAULT_STOPWORDS:
                continue
            counts[token] = counts.get(token, 0) + 1
    ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:limit]
    return [{"term": term, "count": count} for term, count in ranked]


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
    transcript_full = _build_stitched_transcript(rows, max_text_chars=max_text_chars)
    transcript = _filter_transcript_lines(
        transcript_full,
        thread_range=thread_range,
        message_range=message_range,
    )
    analysis = _analyze_thread_terms(
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
        analysis = _analyze_thread_terms(
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


def _db_payload(
    match: DbMatch,
    max_text_chars: int,
    latest_paragraphs: bool = False,
    recent_turns: Optional[list[dict]] = None,
) -> dict:
    latest_text_full = match.latest_text or ""
    payload = {
        **asdict(match),
        "earliest_ts_utc": _iso_utc(match.earliest_datetime),
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
        analysis = payload.get("analysis") or {}

        if db:
            print(f"match_type: {db.get('match_type')}")
            print(f"title: {db.get('title')}")
            print(f"online_thread_id: {db.get('online_thread_id')}")
            print(f"canonical_thread_id: {db.get('canonical_thread_id')}")
            print(f"earliest_ts_utc: {db.get('earliest_ts_utc')}")
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
        if analysis:
            print(f"analysis_scope: {analysis.get('analysis_scope')}")
            if analysis.get("analysis_scope") == "thread_local":
                stats = analysis.get("transcript_stats") or {}
                print(
                    "transcript_stats: "
                    f"messages={stats.get('message_count', 0)} "
                    f"lines={stats.get('stitched_line_count', 0)} "
                    f"chars={stats.get('character_count', 0)}"
                )
                for item in analysis.get("term_stats") or []:
                    print(
                        "term_stat: "
                        f"term={item.get('term')} raw={item.get('raw_count')} "
                        f"line_hits={item.get('line_hit_count')} "
                        f"message_hits={item.get('message_hit_count')} "
                        f"density_100_lines={item.get('density_per_100_lines')}"
                    )
                if analysis.get("top_terms"):
                    print("top_terms:")
                    for item in analysis["top_terms"]:
                        print(f"  {item.get('term')}: {item.get('count')}")
                if analysis.get("mentions"):
                    print("mentions:")
                    for mention in analysis["mentions"]:
                        print(
                            f"  term={mention.get('term')} "
                            f"thread_line={mention.get('thread_line_start')} "
                            f"message={mention.get('message_index')}:{mention.get('message_line_start')} "
                            f"role={mention.get('role')} text={mention.get('line_text')}"
                        )
            elif analysis.get("analysis_scope") == "cross_thread":
                print("cross_thread_results:")
                for item in analysis.get("results") or []:
                    print(
                        f"  raw={item.get('raw_count')} lines={item.get('line_hit_count')} "
                        f"density={item.get('density_per_100_lines')} "
                        f"id={item.get('canonical_thread_id')} title={item.get('title')}"
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
