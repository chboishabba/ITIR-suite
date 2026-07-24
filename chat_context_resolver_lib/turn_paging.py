from __future__ import annotations

import os
import re
import secrets
import sqlite3
import tempfile
import time
from pathlib import Path
from typing import Callable, Optional


TOKEN_RE = re.compile(r"^[A-Za-z0-9]{4,8}$")
DEFAULT_TOKEN_LENGTH = 6


def default_cursor_store_path() -> Path:
    uid = os.getuid() if hasattr(os, "getuid") else 0
    return Path(tempfile.gettempdir()) / f"robust-context-fetch-cursors-{uid}.sqlite"


def validate_cursor_token(token: str) -> str:
    normalized = token.strip()
    if not TOKEN_RE.fullmatch(normalized):
        raise ValueError("Cursor token must be 4-8 ASCII alphanumeric characters.")
    return normalized


def _connect_cursor_store(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path)
    con.row_factory = sqlite3.Row
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS turn_cursors (
          token TEXT PRIMARY KEY,
          db_path TEXT NOT NULL,
          canonical_thread_id TEXT NOT NULL,
          page_size INTEGER NOT NULL,
          next_message_index INTEGER NOT NULL,
          total_count INTEGER NOT NULL,
          source_id TEXT,
          created_at REAL NOT NULL,
          updated_at REAL NOT NULL
        )
        """
    )
    columns = {
        row["name"]
        for row in con.execute("PRAGMA table_info(turn_cursors)").fetchall()
    }
    if "source_id" not in columns:
        con.execute("ALTER TABLE turn_cursors ADD COLUMN source_id TEXT")
    con.commit()
    return con


def _make_token(length: int = DEFAULT_TOKEN_LENGTH) -> str:
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    return "".join(secrets.choice(alphabet) for _ in range(length))


def _insert_cursor(
    store_path: Path,
    *,
    db_path: Path,
    thread_id: str,
    page_size: int,
    next_message_index: int,
    total_count: int,
    source_id: Optional[str],
) -> str:
    con = _connect_cursor_store(store_path)
    now = time.time()
    try:
        for _ in range(32):
            token = _make_token()
            try:
                con.execute(
                    """
                    INSERT INTO turn_cursors (
                      token, db_path, canonical_thread_id, page_size,
                      next_message_index, total_count, source_id, created_at, updated_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        token,
                        str(db_path.expanduser().resolve()),
                        thread_id,
                        page_size,
                        next_message_index,
                        total_count,
                        source_id,
                        now,
                        now,
                    ),
                )
                con.commit()
                return token
            except sqlite3.IntegrityError:
                continue
    finally:
        con.close()
    raise RuntimeError("Unable to allocate a unique cursor token.")


def _load_cursor(
    store_path: Path,
    *,
    token: str,
    db_path: Path,
    thread_id: str,
    page_size: int,
    source_id: Optional[str],
) -> int:
    normalized = validate_cursor_token(token)
    if not store_path.exists():
        raise ValueError("Cursor token was not found.")

    con = _connect_cursor_store(store_path)
    try:
        row = con.execute(
            """
            SELECT db_path, canonical_thread_id, page_size, next_message_index, source_id
            FROM turn_cursors
            WHERE token = ?
            """,
            (normalized,),
        ).fetchone()
        if row is None:
            raise ValueError("Cursor token was not found.")
        if row["db_path"] != str(db_path.expanduser().resolve()):
            raise ValueError("Cursor token belongs to a different DB.")
        if str(row["canonical_thread_id"]).lower() != thread_id.lower():
            raise ValueError("Cursor token belongs to a different thread.")
        if int(row["page_size"]) != page_size:
            raise ValueError("Cursor token belongs to a different page size.")
        stored_source_id = row["source_id"]
        if (stored_source_id or None) != (source_id or None):
            raise ValueError("Cursor token belongs to a different source snapshot.")
        next_index = int(row["next_message_index"])
        if next_index < 1:
            raise ValueError("Cursor token has invalid state.")
        return next_index
    finally:
        con.close()


def _count_thread_turns(
    cur: sqlite3.Cursor,
    thread_id: str,
    *,
    source_id: Optional[str],
) -> int:
    source_clause = ""
    params: list[object] = [thread_id]
    if source_id:
        source_clause = "AND source_id = ?"
        params.append(source_id)
    row = cur.execute(
        f"""
        SELECT COUNT(*) AS message_count
        FROM messages
        WHERE LOWER(canonical_thread_id) = LOWER(?)
          {source_clause}
          AND text IS NOT NULL
          AND TRIM(text) <> ''
        """,
        tuple(params),
    ).fetchone()
    return int(row["message_count"] or 0)


def _query_thread_turn_page(
    cur: sqlite3.Cursor,
    thread_id: str,
    *,
    start_index: int,
    page_size: int,
    source_id: Optional[str],
    max_text_chars: int,
    parse_message_ts: Callable[[object], object],
    iso_utc_precise: Callable[[object], Optional[str]],
    truncate_text: Callable[[str, int], str],
) -> list[dict]:
    offset = max(0, start_index - 1)
    source_clause = ""
    params: list[object] = [thread_id]
    if source_id:
        source_clause = "AND source_id = ?"
        params.append(source_id)
    params.extend([page_size, offset])
    rows = cur.execute(
        f"""
        SELECT message_id, ts, role, text
        FROM messages
        WHERE LOWER(canonical_thread_id) = LOWER(?)
          {source_clause}
          AND text IS NOT NULL
          AND TRIM(text) <> ''
        ORDER BY ts ASC, rowid ASC
        LIMIT ? OFFSET ?
        """,
        tuple(params),
    ).fetchall()

    items: list[dict] = []
    for ordinal, row in enumerate(rows, start=start_index):
        parsed_ts = parse_message_ts(row["ts"])
        items.append(
            {
                "message_index": ordinal,
                "message_id": row["message_id"],
                "ts": row["ts"],
                "ts_utc": iso_utc_precise(parsed_ts),
                "role": row["role"],
                "text": truncate_text(row["text"] or "", max_text_chars),
            }
        )
    return items


def build_turn_page(
    db_path: Path,
    thread_id: str,
    *,
    page_size: int,
    cursor_token: Optional[str],
    cursor_store_path: Path,
    source_id: Optional[str],
    max_text_chars: int,
    parse_message_ts: Callable[[object], object],
    iso_utc_precise: Callable[[object], Optional[str]],
    truncate_text: Callable[[str, int], str],
) -> dict:
    if page_size <= 0:
        raise ValueError("--turn-page-size must be greater than zero.")

    if cursor_token:
        start_index = _load_cursor(
            cursor_store_path,
            token=cursor_token,
            db_path=db_path,
            thread_id=thread_id,
            page_size=page_size,
            source_id=source_id,
        )
    else:
        start_index = 1

    con = sqlite3.connect(f"file:{db_path.expanduser().resolve()}?mode=ro&immutable=1", uri=True)
    con.row_factory = sqlite3.Row
    try:
        total_count = _count_thread_turns(con.cursor(), thread_id, source_id=source_id)
        items = _query_thread_turn_page(
            con.cursor(),
            thread_id,
            start_index=start_index,
            page_size=page_size,
            source_id=source_id,
            max_text_chars=max_text_chars,
            parse_message_ts=parse_message_ts,
            iso_utc_precise=iso_utc_precise,
            truncate_text=truncate_text,
        )
    finally:
        con.close()

    returned_count = len(items)
    end_index = start_index + returned_count - 1 if returned_count else start_index - 1
    next_index = end_index + 1
    exhausted = next_index > total_count
    next_cursor = None
    if not exhausted:
        next_cursor = _insert_cursor(
            cursor_store_path,
            db_path=db_path,
            thread_id=thread_id,
            page_size=page_size,
            next_message_index=next_index,
            total_count=total_count,
            source_id=source_id,
        )

    return {
        "items": items,
        "page_size": page_size,
        "start_index": start_index,
        "end_index": end_index,
        "returned_count": returned_count,
        "total_count": total_count,
        "next_cursor": next_cursor,
        "exhausted": exhausted,
        "source_id": source_id,
    }
