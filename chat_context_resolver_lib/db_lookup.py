from __future__ import annotations

import datetime as dt
import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


def _sqlite_ro_uri(path: Path) -> str:
    resolved = path.expanduser().resolve()
    return f"file:{resolved}?mode=ro&immutable=1"


def connect_sqlite_ro(db_path: Path) -> sqlite3.Connection:
    """Open an immutable read-only connection with temp-store hardening."""
    con = sqlite3.connect(_sqlite_ro_uri(db_path), uri=True)
    con.row_factory = sqlite3.Row
    try:
        con.execute("PRAGMA temp_store=MEMORY")
        con.execute("PRAGMA query_only=ON")
    except sqlite3.Error:
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
class DbLookupResult:
    match: Optional[DbMatch]
    candidates: list[dict]
    warning: Optional[str]


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


def looks_like_online_thread_id(selector: str) -> bool:
    return bool(
        re.fullmatch(
            r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}",
            selector.strip(),
        )
    )


def looks_like_canonical_thread_id(selector: str) -> bool:
    return bool(re.fullmatch(r"[0-9a-f]{40}", selector.strip().lower()))


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
    return int(row["message_count"] or 0), row["earliest_ts"], row["latest_ts"]


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
    return int(row["message_count"] or 0), row["earliest_ts"], row["latest_ts"]


def fts_query(selector: str) -> Optional[str]:
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


def query_db_fts_candidates(
    cur: sqlite3.Cursor,
    selector: str,
    *,
    limit: int = 10,
) -> list[dict]:
    query = fts_query(selector)
    if not query:
        return []

    cur.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'messages_fts'"
    )
    if cur.fetchone() is None:
        return []

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
        GROUP BY m.canonical_thread_id, m.title
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


def query_db_match(
    db_path: Path, selector: str, *, allow_canonical_match: bool = False
) -> Optional[DbMatch]:
    if not db_path.exists():
        return None

    con = connect_sqlite_ro(db_path)
    cur = con.cursor()

    cur.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'messages'"
    )
    if cur.fetchone() is None:
        con.close()
        return None

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


def resolve_db_lookup(
    db_path: Path,
    selector: str,
    *,
    candidate_limit: int = 10,
    allow_canonical_match: bool = False,
) -> DbLookupResult:
    warning: Optional[str] = None
    match: Optional[DbMatch] = None
    candidates: list[dict] = []

    if not db_path.exists():
        return DbLookupResult(
            match=None,
            candidates=[],
            warning=f"DB path does not exist: {db_path}",
        )

    try:
        match = query_db_match(
            db_path,
            selector,
            allow_canonical_match=allow_canonical_match,
        )
    except sqlite3.Error as exc:
        warning = f"DB lookup failed: {exc}"

    normalized_selector = selector.strip()
    should_query_candidates = (
        match is None
        and len(normalized_selector) >= 3
        and not looks_like_online_thread_id(normalized_selector)
        and not looks_like_canonical_thread_id(normalized_selector)
    )
    if should_query_candidates:
        try:
            con = connect_sqlite_ro(db_path)
            try:
                candidates = query_db_fts_candidates(
                    con.cursor(),
                    normalized_selector,
                    limit=candidate_limit,
                )
            finally:
                con.close()
        except sqlite3.Error as exc:
            extra = f"DB FTS lookup failed: {exc}"
            warning = f"{warning}; {extra}" if warning else extra

    return DbLookupResult(match=match, candidates=candidates, warning=warning)
