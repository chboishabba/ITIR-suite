from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from chat_context_resolver_lib.db_lookup import resolve_db_lookup


def _build_archive(db_path: Path) -> None:
    con = sqlite3.connect(db_path)
    con.executescript(
        """
        CREATE TABLE messages (
            message_id TEXT,
            canonical_thread_id TEXT,
            source_thread_id TEXT,
            title TEXT,
            ts TEXT,
            role TEXT,
            text TEXT
        );

        CREATE VIRTUAL TABLE messages_fts USING fts5(
            title,
            text,
            content='messages',
            content_rowid='rowid'
        );
        """
    )
    rows = [
        (
            "m1",
            "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            "11111111-1111-1111-1111-111111111111",
            "Python thread",
            "2026-03-28T01:00:00Z",
            "user",
            "python alpha",
        ),
        (
            "m2",
            "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            "11111111-1111-1111-1111-111111111111",
            "Python thread",
            "2026-03-28T01:05:00Z",
            "assistant",
            "python beta",
        ),
        (
            "m3",
            "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
            "22222222-2222-2222-2222-222222222222",
            "SQL thread",
            "2026-03-28T02:00:00Z",
            "user",
            "sqlite gamma",
        ),
    ]
    con.executemany(
        """
        INSERT INTO messages (
            message_id,
            canonical_thread_id,
            source_thread_id,
            title,
            ts,
            role,
            text
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        rows,
    )
    con.execute("INSERT INTO messages_fts(messages_fts) VALUES ('rebuild')")
    con.commit()
    con.close()


def test_resolve_db_lookup_matches_canonical_thread_id(tmp_path: Path) -> None:
    db_path = tmp_path / "archive.sqlite"
    _build_archive(db_path)

    result = resolve_db_lookup(
        db_path,
        "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        allow_canonical_match=True,
    )

    assert result.warning is None
    assert result.candidates == []
    assert result.match is not None
    assert result.match.match_type == "canonical_thread_id_exact"
    assert result.match.canonical_thread_id == "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    assert result.match.thread_message_count == 2


def test_resolve_db_lookup_returns_fts_candidates_when_no_match(tmp_path: Path) -> None:
    db_path = tmp_path / "archive.sqlite"
    _build_archive(db_path)

    result = resolve_db_lookup(db_path, "alpha", candidate_limit=5)

    assert result.warning is None
    assert result.match is None
    assert result.candidates
    assert result.candidates[0]["canonical_thread_id"] == "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    assert result.candidates[0]["hit_count"] >= 1


def test_resolve_db_lookup_reports_missing_db(tmp_path: Path) -> None:
    db_path = tmp_path / "missing.sqlite"

    result = resolve_db_lookup(db_path, "python", candidate_limit=5)

    assert result.match is None
    assert result.candidates == []
    assert result.warning == f"DB path does not exist: {db_path}"
