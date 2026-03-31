from __future__ import annotations

import sqlite3
from pathlib import Path

from itir_mcp import build_default_registry


def _fixture_db() -> str:
    return str(
        (
            Path(__file__).resolve().parents[2]
            / "chat-export-structurer"
            / "examples"
            / "sample_archive.sqlite"
        ).resolve()
    )


def test_search_threads_returns_candidates() -> None:
    registry = build_default_registry()
    result = registry.invoke(
        "chat_export_structurer.search_threads",
        {
            "selector": "python",
            "db_path": _fixture_db(),
            "limit": 5,
        },
    )

    assert result["ok"] is True
    payload = result["result"]
    assert payload["version"] == "chat_export_structurer.search_threads.v1"
    assert payload["results"]


def test_resolve_thread_accepts_canonical_id() -> None:
    registry = build_default_registry()
    search = registry.invoke(
        "chat_export_structurer.search_threads",
        {
            "selector": "python",
            "db_path": _fixture_db(),
            "limit": 1,
        },
    )
    assert search["ok"] is True
    candidate = search["result"]["results"][0]["canonical_thread_id"]

    result = registry.invoke(
        "chat_export_structurer.resolve_thread",
        {
            "selector": candidate,
            "db_path": _fixture_db(),
            "allow_canonical_match": True,
        },
    )

    assert result["ok"] is True
    payload = result["result"]
    assert payload["version"] == "chat_export_structurer.resolve_thread.v1"
    assert payload["match"]["canonical_thread_id"] == candidate


def test_thread_messages_returns_ordered_messages() -> None:
    registry = build_default_registry()
    search = registry.invoke(
        "chat_export_structurer.search_threads",
        {
            "selector": "python",
            "db_path": _fixture_db(),
            "limit": 1,
        },
    )
    assert search["ok"] is True
    candidate = search["result"]["results"][0]["canonical_thread_id"]

    result = registry.invoke(
        "chat_export_structurer.thread_messages",
        {
            "canonical_thread_id": candidate,
            "db_path": _fixture_db(),
            "limit": 3,
        },
    )

    assert result["ok"] is True
    payload = result["result"]
    assert payload["version"] == "chat_export_structurer.thread_messages.v1"
    assert payload["message_count"] >= len(payload["messages"]) > 0
    timestamps = [message["ts"] for message in payload["messages"]]
    assert timestamps == sorted(timestamps)


def test_search_threads_handles_missing_db(tmp_path) -> None:
    registry = build_default_registry()
    missing_db = tmp_path / "missing.sqlite"
    result = registry.invoke(
        "chat_export_structurer.search_threads",
        {
            "selector": "python",
            "db_path": str(missing_db),
            "limit": 5,
        },
    )

    assert result["ok"] is True
    payload = result["result"]
    assert payload["results"] == []
    assert payload["db_path"] == str(missing_db)


def test_resolve_thread_handles_missing_db(tmp_path) -> None:
    registry = build_default_registry()
    missing_db = tmp_path / "missing.sqlite"

    result = registry.invoke(
        "chat_export_structurer.resolve_thread",
        {
            "selector": "python",
            "db_path": str(missing_db),
            "allow_canonical_match": True,
        },
    )

    assert result["ok"] is True
    payload = result["result"]
    assert payload["match"] is None
    assert payload["db_path"] == str(missing_db)


def test_thread_messages_handles_missing_db(tmp_path) -> None:
    registry = build_default_registry()
    missing_db = tmp_path / "missing.sqlite"

    result = registry.invoke(
        "chat_export_structurer.thread_messages",
        {
            "canonical_thread_id": "missing-thread",
            "db_path": str(missing_db),
        },
    )

    assert result["ok"] is True
    payload = result["result"]
    assert payload["message_count"] == 0
    assert payload["messages"] == []
    assert payload["db_path"] == str(missing_db)


def _write_platform_fixture(db_path: Path) -> None:
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.executescript(
        """
        CREATE TABLE messages (
          message_id TEXT PRIMARY KEY,
          canonical_thread_id TEXT NOT NULL,
          platform TEXT NOT NULL,
          account_id TEXT NOT NULL,
          ts TEXT NOT NULL,
          role TEXT NOT NULL,
          text TEXT NOT NULL,
          title TEXT,
          source_id TEXT NOT NULL,
          source_thread_id TEXT,
          source_message_id TEXT
        );
        CREATE VIRTUAL TABLE messages_fts USING fts5(text, content='');
        """
    )
    rows = [
        (
            1,
            "m_tg_1",
            "thread_tg",
            "telegram",
            "main",
            "2026-03-30T00:00:00+00:00",
            "alice",
            "ramanujan telegram note",
            "James Michael",
            "telegram_2026_03_30",
            "tg_1",
            "1",
        ),
        (
            2,
            "m_cg_1",
            "thread_cg",
            "chatgpt",
            "main",
            "2026-03-30T01:00:00+00:00",
            "user",
            "ramanujan chatgpt note",
            "James Michael",
            "chatgpt_src",
            "cg_1",
            "1",
        ),
    ]
    cur.executemany(
        """
        INSERT INTO messages (
          rowid, message_id, canonical_thread_id, platform, account_id, ts, role, text, title,
          source_id, source_thread_id, source_message_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        rows,
    )
    cur.executemany(
        "INSERT INTO messages_fts(rowid, text) VALUES (?, ?)",
        [(1, "ramanujan telegram note"), (2, "ramanujan chatgpt note")],
    )
    con.commit()
    con.close()


def test_search_threads_supports_platform_filter(tmp_path) -> None:
    db_path = tmp_path / "platform.sqlite"
    _write_platform_fixture(db_path)
    registry = build_default_registry()

    result = registry.invoke(
        "chat_export_structurer.search_threads",
        {
            "selector": "ramanujan",
            "db_path": str(db_path),
            "platform": "telegram",
            "limit": 5,
        },
    )

    assert result["ok"] is True
    payload = result["result"]
    assert payload["platform"] == "telegram"
    assert len(payload["results"]) == 1
    assert payload["results"][0]["platform"] == "telegram"
    assert payload["results"][0]["canonical_thread_id"] == "thread_tg"


def test_thread_messages_supports_platform_filter(tmp_path) -> None:
    db_path = tmp_path / "platform.sqlite"
    _write_platform_fixture(db_path)
    registry = build_default_registry()

    result = registry.invoke(
        "chat_export_structurer.thread_messages",
        {
            "canonical_thread_id": "thread_tg",
            "db_path": str(db_path),
            "platform": "telegram",
            "limit": 10,
        },
    )

    assert result["ok"] is True
    payload = result["result"]
    assert payload["platform"] == "telegram"
    assert payload["message_count"] == 1
    assert payload["messages"][0]["platform"] == "telegram"
    assert payload["messages"][0]["role"] == "alice"


def test_resolve_thread_supports_platform_filter(tmp_path) -> None:
    db_path = tmp_path / "platform.sqlite"
    _write_platform_fixture(db_path)
    registry = build_default_registry()

    result = registry.invoke(
        "chat_export_structurer.resolve_thread",
        {
            "selector": "James Michael",
            "db_path": str(db_path),
            "platform": "telegram",
        },
    )

    assert result["ok"] is True
    payload = result["result"]
    assert payload["platform"] == "telegram"
    assert payload["match"]["platform"] == "telegram"
    assert payload["match"]["canonical_thread_id"] == "thread_tg"
