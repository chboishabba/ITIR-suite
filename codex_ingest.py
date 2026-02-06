#!/usr/bin/env python3
"""
Ingest Codex local history into a chat-export-structurer compatible SQLite DB.

Sources:
  - ~/.codex/history.jsonl (user messages)
  - ~/.codex/log/codex-tui.log (tool usage)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Tuple

ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")
TOOLCALL_RE = re.compile(r"ToolCall:\s*(\w+)\s+(\{.*\})")
THREAD_RE = re.compile(r"thread_id=([0-9a-f-]{36})")
TS_RE = re.compile(r"^(\d{4}-\d{2}-\d{2}T[0-9:.]+Z?)\s+")


def sha1(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8", errors="ignore")).hexdigest()


def ensure_schema(db_path: str) -> None:
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.executescript(
        """
        PRAGMA journal_mode=WAL;
        CREATE TABLE IF NOT EXISTS messages (
          message_id TEXT PRIMARY KEY,
          canonical_thread_id TEXT NOT NULL,
          platform TEXT NOT NULL,
          account_id TEXT NOT NULL,
          ts TEXT NOT NULL,
          role TEXT NOT NULL,
          text TEXT NOT NULL,
          title TEXT,
          source_id TEXT NOT NULL
        );
        CREATE VIRTUAL TABLE IF NOT EXISTS messages_fts
        USING fts5(text, content='');
        CREATE TABLE IF NOT EXISTS messages_fts_docids (
          rowid INTEGER PRIMARY KEY,
          message_id TEXT NOT NULL
        );
        """
    )
    con.commit()
    con.close()


def to_iso_utc(ts: str | int | float | None) -> Optional[str]:
    if ts is None:
        return None
    if isinstance(ts, (int, float)):
        try:
            return datetime.fromtimestamp(float(ts), timezone.utc).replace(microsecond=0).isoformat()
        except Exception:
            return None
    if isinstance(ts, str):
        s = ts.strip()
        if not s:
            return None
        if s.endswith("Z"):
            s = s[:-1]
        try:
            dt = datetime.fromisoformat(s)
        except Exception:
            return None
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        else:
            dt = dt.astimezone(timezone.utc)
        return dt.replace(microsecond=0).isoformat()
    return None


def insert_message(
    cur: sqlite3.Cursor,
    message_id: str,
    canonical_thread_id: str,
    platform: str,
    account_id: str,
    ts_iso: str,
    role: str,
    text: str,
    title: Optional[str],
    source_id: str,
) -> None:
    cur.execute(
        """
        INSERT OR IGNORE INTO messages
        (message_id, canonical_thread_id, platform, account_id, ts, role, text, title, source_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            message_id,
            canonical_thread_id,
            platform,
            account_id,
            ts_iso,
            role,
            text,
            title,
            source_id,
        ),
    )
    if cur.rowcount == 0:
        return
    cur.execute("INSERT INTO messages_fts (text) VALUES (?)", (text,))
    fts_rowid = cur.execute("SELECT max(rowid) FROM messages_fts").fetchone()[0]
    cur.execute(
        "INSERT INTO messages_fts_docids (rowid, message_id) VALUES (?, ?)",
        (fts_rowid, message_id),
    )


def ingest_history_jsonl(
    cur: sqlite3.Cursor,
    path: Path,
    platform: str,
    account_id: str,
    source_id: str,
) -> int:
    inserted = 0
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                continue
            session_id = obj.get("session_id") or "unknown_session"
            ts_iso = to_iso_utc(obj.get("ts"))
            text = obj.get("text") or ""
            if not ts_iso or not text:
                continue
            message_id = sha1("|".join([platform, account_id, session_id, "user", ts_iso, text]))
            insert_message(
                cur,
                message_id,
                session_id,
                platform,
                account_id,
                ts_iso,
                "user",
                text,
                None,
                source_id,
            )
            inserted += 1
    return inserted


def parse_toolcall(line: str) -> Optional[Tuple[str, Optional[str], Optional[str]]]:
    line = ANSI_RE.sub("", line).rstrip()
    m = TOOLCALL_RE.search(line)
    if not m:
        return None
    tool = m.group(1)
    payload = m.group(2)
    ts_match = TS_RE.match(line)
    ts = ts_match.group(1) if ts_match else None
    thread_match = THREAD_RE.search(line)
    thread_id = thread_match.group(1) if thread_match else None
    text = f"{tool} {payload}"
    return text, ts, thread_id


def ingest_tool_log(
    cur: sqlite3.Cursor,
    path: Path,
    platform: str,
    account_id: str,
    source_id: str,
) -> int:
    inserted = 0
    with path.open("r", encoding="utf-8", errors="replace") as f:
        for line in f:
            parsed = parse_toolcall(line)
            if not parsed:
                continue
            text, ts_raw, thread_id = parsed
            ts_iso = to_iso_utc(ts_raw)
            if not ts_iso:
                continue
            canonical_thread_id = thread_id or "codex_tooling"
            message_id = sha1("|".join([platform, account_id, canonical_thread_id, "tool", ts_iso, text]))
            insert_message(
                cur,
                message_id,
                canonical_thread_id,
                platform,
                account_id,
                ts_iso,
                "tool",
                text,
                None,
                source_id,
            )
            inserted += 1
    return inserted


def main() -> int:
    ap = argparse.ArgumentParser(description="Ingest Codex local history into SQLite")
    ap.add_argument("--history", default=str(Path.home() / ".codex/history.jsonl"))
    ap.add_argument("--log", default=str(Path.home() / ".codex/log/codex-tui.log"))
    ap.add_argument("--db", default="codex_history.sqlite")
    ap.add_argument("--account", default="local")
    ap.add_argument("--platform", default="codex")
    ap.add_argument("--source-id", default="codex_0001")
    args = ap.parse_args()

    db_path = Path(args.db).expanduser()
    ensure_schema(str(db_path))
    con = sqlite3.connect(str(db_path))
    cur = con.cursor()

    total_inserted = 0

    history_path = Path(args.history).expanduser()
    if history_path.exists():
        cur.execute("BEGIN")
        total_inserted += ingest_history_jsonl(
            cur, history_path, args.platform, args.account, args.source_id
        )
        con.commit()

    log_path = Path(args.log).expanduser()
    if log_path.exists():
        cur.execute("BEGIN")
        total_inserted += ingest_tool_log(
            cur, log_path, args.platform, args.account, args.source_id
        )
        con.commit()

    con.close()
    print(f"Inserted {total_inserted} messages into {db_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
