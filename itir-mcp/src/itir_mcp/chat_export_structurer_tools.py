from __future__ import annotations
import sys
from pathlib import Path
from typing import Any, Mapping

from .contracts import JsonDict, ToolInputError, ToolSpec


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _default_archive_path() -> Path:
    return _repo_root() / "chat-export-structurer" / "my_archive.sqlite"


def _ensure_repo_root_on_path() -> None:
    text = str(_repo_root())
    if text not in sys.path:
        sys.path.insert(0, text)


def _require_str(payload: Mapping[str, Any], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ToolInputError(f"Expected non-empty string field: {key}")
    return value.strip()


def _optional_str(payload: Mapping[str, Any], key: str) -> str | None:
    value = payload.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        raise ToolInputError(f"Expected string field: {key}")
    text = value.strip()
    return text or None


def _optional_bool(payload: Mapping[str, Any], key: str) -> bool | None:
    value = payload.get(key)
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    raise ToolInputError(f"Expected boolean field: {key}")


def _optional_int(payload: Mapping[str, Any], key: str, *, minimum: int = 1, maximum: int | None = None) -> int | None:
    value = payload.get(key)
    if value is None:
        return None
    if not isinstance(value, int):
        raise ToolInputError(f"Expected integer field: {key}")
    if value < minimum:
        raise ToolInputError(f"Expected {key} >= {minimum}")
    if maximum is not None and value > maximum:
        raise ToolInputError(f"Expected {key} <= {maximum}")
    return value


def _optional_platform(payload: Mapping[str, Any]) -> str | None:
    return _optional_str(payload, "platform")


def _resolve_db_path(payload: Mapping[str, Any]) -> Path:
    raw = _optional_str(payload, "db_path")
    return Path(raw).expanduser().resolve() if raw else _default_archive_path().resolve()


def _message_columns(cur) -> set[str]:
    cur.execute("PRAGMA table_info(messages)")
    return {str(row["name"]) for row in cur.fetchall()}


def _source_column(columns: set[str], name: str) -> str:
    return name if name in columns else f"NULL AS {name}"


def _query_thread_span(
    cur,
    canonical_thread_id: str,
    *,
    platform: str | None = None,
) -> tuple[int, str | None, str | None]:
    where = "WHERE LOWER(canonical_thread_id) = LOWER(?)"
    params: list[Any] = [canonical_thread_id]
    if platform:
        where += " AND LOWER(platform) = LOWER(?)"
        params.append(platform)
    cur.execute(
        f"""
        SELECT COUNT(*) AS message_count, MIN(ts) AS earliest_ts, MAX(ts) AS latest_ts
        FROM messages
        {where}
        """,
        tuple(params),
    )
    row = cur.fetchone()
    if row is None:
        return 0, None, None
    return int(row["message_count"] or 0), row["earliest_ts"], row["latest_ts"]


def _fetch_latest_for_thread(
    cur,
    canonical_thread_id: str,
    columns: set[str],
    *,
    platform: str | None = None,
):
    where = """
        WHERE LOWER(canonical_thread_id) = LOWER(?)
          AND text IS NOT NULL
          AND TRIM(text) <> ''
    """
    params: list[Any] = [canonical_thread_id]
    if platform:
        where += " AND LOWER(platform) = LOWER(?)"
        params.append(platform)
    cur.execute(
        f"""
        SELECT
          canonical_thread_id,
          platform,
          {_source_column(columns, "source_thread_id")},
          COALESCE(NULLIF(title, ''), '(no title)') AS title,
          ts,
          role,
          text
        FROM messages
        {where}
        ORDER BY ts DESC, rowid DESC
        LIMIT 1
        """,
        tuple(params),
    )
    return cur.fetchone()


def _match_from_row(row, *, match_type: str, matched_thread_count: int, db_path: Path, count: int, earliest_ts: str | None, latest_ts: str | None) -> JsonDict:
    return {
        "match_type": match_type,
        "canonical_thread_id": row["canonical_thread_id"],
        "platform": row["platform"],
        "online_thread_id": row["source_thread_id"],
        "title": row["title"],
        "earliest_ts": earliest_ts,
        "latest_ts": latest_ts or row["ts"],
        "latest_role": row["role"],
        "latest_text": row["text"],
        "thread_message_count": count,
        "matched_thread_count": matched_thread_count,
        "db_path": str(db_path),
    }


def resolve_thread(payload: Mapping[str, Any]) -> JsonDict:
    _ensure_repo_root_on_path()
    from chat_context_resolver_lib.db_lookup import connect_sqlite_ro, looks_like_online_thread_id

    selector = _require_str(payload, "selector")
    db_path = _resolve_db_path(payload)
    allow_canonical_match = bool(_optional_bool(payload, "allow_canonical_match"))
    platform = _optional_platform(payload)
    match = None
    if db_path.exists():
        con = connect_sqlite_ro(db_path)
        try:
            cur = con.cursor()
            columns = _message_columns(cur)

            if "source_thread_id" in columns and looks_like_online_thread_id(selector):
                cur.execute(
                    """
                    SELECT
                      canonical_thread_id,
                      platform,
                      source_thread_id,
                      COALESCE(NULLIF(title, ''), '(no title)') AS title,
                      ts,
                      role,
                      text
                    FROM messages
                    WHERE LOWER(source_thread_id) = LOWER(?)
                      AND (? IS NULL OR LOWER(platform) = LOWER(?))
                      AND text IS NOT NULL
                      AND TRIM(text) <> ''
                    ORDER BY ts DESC, rowid DESC
                    LIMIT 1
                    """,
                    (selector, platform, platform),
                )
                row = cur.fetchone()
                if row is not None:
                    cur.execute(
                        """
                        SELECT COUNT(*) AS message_count, MIN(ts) AS earliest_ts, MAX(ts) AS latest_ts
                        FROM messages
                        WHERE LOWER(source_thread_id) = LOWER(?)
                          AND (? IS NULL OR LOWER(platform) = LOWER(?))
                        """,
                        (selector, platform, platform),
                    )
                    span = cur.fetchone()
                    match = _match_from_row(
                        row,
                        match_type="online_thread_id_exact",
                        matched_thread_count=1,
                        db_path=db_path,
                        count=int(span["message_count"] or 0) if span else 0,
                        earliest_ts=span["earliest_ts"] if span else None,
                        latest_ts=span["latest_ts"] if span else None,
                    )

            if match is None and allow_canonical_match:
                row = _fetch_latest_for_thread(cur, selector, columns, platform=platform)
                if row is not None:
                    count, earliest_ts, latest_ts = _query_thread_span(
                        cur, row["canonical_thread_id"], platform=platform
                    )
                    match = _match_from_row(
                        row,
                        match_type="canonical_thread_id_exact",
                        matched_thread_count=1,
                        db_path=db_path,
                        count=count,
                        earliest_ts=earliest_ts,
                        latest_ts=latest_ts,
                    )

            if match is None:
                cur.execute(
                    f"""
                    SELECT
                      canonical_thread_id,
                      platform,
                      {_source_column(columns, "source_thread_id")},
                      COALESCE(NULLIF(title, ''), '(no title)') AS title,
                      ts,
                      role,
                      text
                    FROM messages
                    WHERE LOWER(title) = LOWER(?)
                      AND (? IS NULL OR LOWER(platform) = LOWER(?))
                      AND text IS NOT NULL
                      AND TRIM(text) <> ''
                    ORDER BY ts DESC, rowid DESC
                    LIMIT 1
                    """,
                    (selector, platform, platform),
                )
                row = cur.fetchone()
                if row is not None:
                    cur.execute(
                        """
                        SELECT COUNT(DISTINCT canonical_thread_id) AS matched_count
                        FROM messages
                        WHERE LOWER(title) = LOWER(?)
                          AND (? IS NULL OR LOWER(platform) = LOWER(?))
                        """,
                        (selector, platform, platform),
                    )
                    matched = cur.fetchone()
                    count, earliest_ts, latest_ts = _query_thread_span(
                        cur, row["canonical_thread_id"], platform=platform
                    )
                    match = _match_from_row(
                        row,
                        match_type="title_exact",
                        matched_thread_count=int(matched["matched_count"] or 0) if matched else 0,
                        db_path=db_path,
                        count=count,
                        earliest_ts=earliest_ts,
                        latest_ts=latest_ts,
                    )

            if match is None and len(selector) >= 3:
                like = f"%{selector.lower()}%"
                cur.execute(
                    f"""
                    SELECT
                      canonical_thread_id,
                      platform,
                      {_source_column(columns, "source_thread_id")},
                      COALESCE(NULLIF(title, ''), '(no title)') AS title,
                      ts,
                      role,
                      text
                    FROM messages
                    WHERE LOWER(title) LIKE ?
                      AND (? IS NULL OR LOWER(platform) = LOWER(?))
                      AND text IS NOT NULL
                      AND TRIM(text) <> ''
                    ORDER BY ts DESC, rowid DESC
                    LIMIT 1
                    """,
                    (like, platform, platform),
                )
                row = cur.fetchone()
                if row is not None:
                    cur.execute(
                        """
                        SELECT COUNT(DISTINCT canonical_thread_id) AS matched_count
                        FROM messages
                        WHERE LOWER(title) LIKE ?
                          AND (? IS NULL OR LOWER(platform) = LOWER(?))
                        """,
                        (like, platform, platform),
                    )
                    matched = cur.fetchone()
                    count, earliest_ts, latest_ts = _query_thread_span(
                        cur, row["canonical_thread_id"], platform=platform
                    )
                    match = _match_from_row(
                        row,
                        match_type="title_contains",
                        matched_thread_count=int(matched["matched_count"] or 0) if matched else 0,
                        db_path=db_path,
                        count=count,
                        earliest_ts=earliest_ts,
                        latest_ts=latest_ts,
                    )
        finally:
            con.close()

    return {
        "version": "chat_export_structurer.resolve_thread.v1",
        "db_path": str(db_path),
        "selector": selector,
        "platform": platform,
        "match": match,
    }


def search_threads(payload: Mapping[str, Any]) -> JsonDict:
    _ensure_repo_root_on_path()
    from chat_context_resolver_lib.db_lookup import connect_sqlite_ro, fts_query

    selector = _require_str(payload, "selector")
    limit = _optional_int(payload, "limit", minimum=1, maximum=100) or 10
    db_path = _resolve_db_path(payload)
    platform = _optional_platform(payload)

    if not db_path.exists():
        return {
            "version": "chat_export_structurer.search_threads.v1",
            "db_path": str(db_path),
            "selector": selector,
            "platform": platform,
            "results": [],
        }

    con = connect_sqlite_ro(db_path)
    try:
        cur = con.cursor()
        query = fts_query(selector)
        if not query:
            rows = []
        else:
            cur.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'messages_fts'"
            )
            if cur.fetchone() is None:
                rows = []
            else:
                cur.execute(
                    """
                    SELECT
                        m.canonical_thread_id AS canonical_thread_id,
                        m.platform AS platform,
                        COALESCE(NULLIF(m.title, ''), '(no title)') AS title,
                        MAX(m.ts) AS latest_ts,
                        COUNT(*) AS hit_count
                    FROM messages_fts
                    JOIN messages m ON m.rowid = messages_fts.rowid
                    WHERE messages_fts MATCH ?
                      AND (? IS NULL OR LOWER(m.platform) = LOWER(?))
                    GROUP BY m.canonical_thread_id, m.platform, m.title
                    ORDER BY hit_count DESC, latest_ts DESC
                    LIMIT ?
                    """,
                    (query, platform, platform, limit),
                )
                rows = [
                    {
                        "canonical_thread_id": row["canonical_thread_id"],
                        "platform": row["platform"],
                        "title": row["title"],
                        "latest_ts": row["latest_ts"],
                        "hit_count": int(row["hit_count"] or 0),
                    }
                    for row in cur.fetchall()
                ]
    finally:
        con.close()

    return {
        "version": "chat_export_structurer.search_threads.v1",
        "db_path": str(db_path),
        "selector": selector,
        "platform": platform,
        "results": rows,
    }


def thread_messages(payload: Mapping[str, Any]) -> JsonDict:
    _ensure_repo_root_on_path()
    from chat_context_resolver_lib.db_lookup import connect_sqlite_ro

    canonical_thread_id = _require_str(payload, "canonical_thread_id")
    limit = _optional_int(payload, "limit", minimum=1, maximum=500) or 200
    db_path = _resolve_db_path(payload)
    platform = _optional_platform(payload)

    if not db_path.exists():
        return {
            "version": "chat_export_structurer.thread_messages.v1",
            "db_path": str(db_path),
            "canonical_thread_id": canonical_thread_id,
            "platform": platform,
            "message_count": 0,
            "messages": [],
        }

    con = connect_sqlite_ro(db_path)
    try:
        cur = con.cursor()
        columns = _message_columns(cur)
        cur.execute(
            f"""
            SELECT
              message_id,
              platform,
              ts,
              role,
              text,
              COALESCE(NULLIF(title, ''), '(no title)') AS title,
              {_source_column(columns, "source_thread_id")},
              {_source_column(columns, "source_message_id")}
            FROM messages
            WHERE LOWER(canonical_thread_id) = LOWER(?)
              AND (? IS NULL OR LOWER(platform) = LOWER(?))
            ORDER BY ts ASC, rowid ASC
            LIMIT ?
            """,
            (canonical_thread_id, platform, platform, limit),
        )
        rows = cur.fetchall()
        cur.execute(
            """
            SELECT COUNT(*) AS message_count
            FROM messages
            WHERE LOWER(canonical_thread_id) = LOWER(?)
              AND (? IS NULL OR LOWER(platform) = LOWER(?))
            """,
            (canonical_thread_id, platform, platform),
        )
        count_row = cur.fetchone()
    finally:
        con.close()

    messages = [
        {
            "message_id": row["message_id"],
            "platform": row["platform"],
            "ts": row["ts"],
            "role": row["role"],
            "text": row["text"],
            "title": row["title"],
            "source_thread_id": row["source_thread_id"],
            "source_message_id": row["source_message_id"],
        }
        for row in rows
    ]
    return {
        "version": "chat_export_structurer.thread_messages.v1",
        "db_path": str(db_path),
        "canonical_thread_id": canonical_thread_id,
        "platform": platform,
        "message_count": int(count_row["message_count"] or 0) if count_row else 0,
        "messages": messages,
    }


def get_chat_export_structurer_tools():
    return [
        (
            ToolSpec(
                name="chat_export_structurer.resolve_thread",
                title="Chat export structurer resolve thread",
                description="Resolve a thread selector against the canonical chat archive.",
                input_schema={
                    "type": "object",
                    "required": ["selector"],
                    "properties": {
                        "selector": {"type": "string"},
                        "db_path": {"type": "string"},
                        "platform": {"type": "string"},
                        "allow_canonical_match": {"type": "boolean"},
                    },
                },
            ),
            resolve_thread,
        ),
        (
            ToolSpec(
                name="chat_export_structurer.search_threads",
                title="Chat export structurer search threads",
                description="Return FTS-backed candidate threads from the canonical chat archive.",
                input_schema={
                    "type": "object",
                    "required": ["selector"],
                    "properties": {
                        "selector": {"type": "string"},
                        "db_path": {"type": "string"},
                        "platform": {"type": "string"},
                        "limit": {"type": "integer", "minimum": 1, "maximum": 100},
                    },
                },
            ),
            search_threads,
        ),
        (
            ToolSpec(
                name="chat_export_structurer.thread_messages",
                title="Chat export structurer thread messages",
                description="Fetch ordered messages for a canonical thread identifier.",
                input_schema={
                    "type": "object",
                    "required": ["canonical_thread_id"],
                    "properties": {
                        "canonical_thread_id": {"type": "string"},
                        "db_path": {"type": "string"},
                        "platform": {"type": "string"},
                        "limit": {"type": "integer", "minimum": 1, "maximum": 500},
                    },
                },
            ),
            thread_messages,
        ),
    ]
