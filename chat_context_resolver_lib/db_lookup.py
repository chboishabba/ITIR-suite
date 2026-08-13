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
    selected_source_id: Optional[str] = None
    source_snapshot_count: int = 0
    source_snapshot_diagnostics: Optional[dict] = None

    @property
    def latest_datetime(self) -> Optional[dt.datetime]:
        return _parse_message_ts(self.latest_ts)

    @property
    def earliest_datetime(self) -> Optional[dt.datetime]:
        return _parse_message_ts(self.earliest_ts)


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
    cur: sqlite3.Cursor,
    online_thread_id: str,
    *,
    require_text: bool = False,
    source_id: Optional[str] = None,
) -> Optional[tuple]:
    text_clause = ""
    if require_text:
        text_clause = "AND text IS NOT NULL AND TRIM(text) <> ''"
    source_clause = ""
    params: list[object] = [online_thread_id]
    if source_id:
        source_clause = "AND source_id = ?"
        params.append(source_id)

    cur.execute(
        f"""
        SELECT canonical_thread_id, source_id, source_thread_id, COALESCE(NULLIF(title, ''), '(no title)') AS title, ts, role, text
        FROM messages
        WHERE LOWER(source_thread_id) = LOWER(?)
          {source_clause}
          {text_clause}
        ORDER BY ts DESC, rowid DESC
        LIMIT 1
        """,
        tuple(params),
    )
    row = cur.fetchone()
    if row or not require_text:
        return row
    return _fetch_latest_for_online_thread_id(
        cur,
        online_thread_id,
        require_text=False,
        source_id=source_id,
    )


def _query_online_thread_span(
    cur: sqlite3.Cursor,
    online_thread_id: str,
    *,
    source_id: Optional[str] = None,
) -> tuple[int, Optional[str], Optional[str]]:
    source_clause = ""
    params: list[object] = [online_thread_id]
    if source_id:
        source_clause = "AND source_id = ?"
        params.append(source_id)
    cur.execute(
        f"""
        SELECT COUNT(*) AS message_count, MIN(ts) AS earliest_ts, MAX(ts) AS latest_ts
        FROM messages
        WHERE LOWER(source_thread_id) = LOWER(?)
          {source_clause}
        """,
        tuple(params),
    )
    row = cur.fetchone()
    if not row:
        return 0, None, None
    return int(row["message_count"] or 0), row["earliest_ts"], row["latest_ts"]


def _source_snapshot_diagnostics(cur: sqlite3.Cursor, online_thread_id: str) -> tuple[Optional[str], int, Optional[dict]]:
    cur.execute(
        """
        SELECT
            source_id,
            COUNT(*) AS row_count,
            MIN(ts) AS earliest_ts,
            MAX(ts) AS latest_ts,
            COUNT(DISTINCT source_message_id) AS distinct_source_message_count
        FROM messages
        WHERE LOWER(source_thread_id) = LOWER(?)
          AND source_id IS NOT NULL
          AND TRIM(source_id) <> ''
        GROUP BY source_id
        ORDER BY latest_ts DESC, row_count DESC, source_id DESC
        """,
        (online_thread_id,),
    )
    rows = cur.fetchall()
    if not rows:
        return None, 0, None

    snapshots = [
        {
            "source_id": row["source_id"],
            "row_count": int(row["row_count"] or 0),
            "earliest_ts": row["earliest_ts"],
            "latest_ts": row["latest_ts"],
            "distinct_source_message_count": int(row["distinct_source_message_count"] or 0),
        }
        for row in rows
    ]
    selected_source_id = str(snapshots[0]["source_id"])
    row_counts = [int(item["row_count"]) for item in snapshots]
    max_count = max(row_counts) if row_counts else 0
    min_count = min(row_counts) if row_counts else 0
    diagnostics: dict = {
        "warning": (
            "multiple source_id snapshots exist for this source_thread_id; "
            "resolver paging is scoped to selected_source_id"
        )
        if len(snapshots) > 1
        else None,
        "snapshots": snapshots[:10],
        "snapshot_count": len(snapshots),
        "row_count_skew": max_count - min_count,
        "high_row_count_skew": len(snapshots) > 1 and min_count > 0 and max_count >= (min_count * 2),
    }

    if len(snapshots) > 1:
        cur.execute(
            """
            SELECT source_message_id, COUNT(DISTINCT source_id) AS source_count
            FROM messages
            WHERE LOWER(source_thread_id) = LOWER(?)
              AND source_id IS NOT NULL
              AND TRIM(source_id) <> ''
              AND source_message_id IS NOT NULL
              AND TRIM(source_message_id) <> ''
            GROUP BY source_message_id
            HAVING source_count > 1
            LIMIT 1
            """,
            (online_thread_id,),
        )
        diagnostics["disjoint_source_message_sets"] = cur.fetchone() is None

    return selected_source_id, len(snapshots), diagnostics


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
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'messages_fts_docids'"
    )
    has_docids = cur.fetchone() is not None
    if has_docids:
        sql = """
            SELECT
                m.canonical_thread_id AS canonical_thread_id,
                COALESCE(NULLIF(m.title, ''), '(no title)') AS title,
                MAX(m.ts) AS latest_ts,
                COUNT(*) AS hit_count
            FROM messages_fts
            JOIN messages_fts_docids d ON d.rowid = messages_fts.rowid
            JOIN messages m ON m.message_id = d.message_id
            WHERE messages_fts MATCH ?
            GROUP BY m.canonical_thread_id, title
            ORDER BY hit_count DESC, latest_ts DESC
            LIMIT ?
            """
    else:
        sql = """
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
            """

    cur.execute(sql, (query, limit))
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
    db_path: Path,
    selector: str,
    *,
    allow_canonical_match: bool = False,
    selected_source_id: Optional[str] = None,
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

    snapshot_source_id, snapshot_count, snapshot_diagnostics = _source_snapshot_diagnostics(cur, selector)
    effective_source_id = selected_source_id or snapshot_source_id
    online_row = _fetch_latest_for_online_thread_id(
        cur,
        selector,
        require_text=True,
        source_id=effective_source_id,
    )
    if online_row:
        count, earliest_ts, latest_ts = _query_online_thread_span(
            cur,
            str(online_row["source_thread_id"]),
            source_id=effective_source_id,
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
            selected_source_id=effective_source_id,
            source_snapshot_count=snapshot_count,
            source_snapshot_diagnostics=snapshot_diagnostics,
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
