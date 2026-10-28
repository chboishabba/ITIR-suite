from __future__ import annotations

import sqlite3
from pathlib import Path

from itir_mcp.pg_semantic_spine import (
    PostgresSemanticSpineUnavailable,
    load_postgres_semantic_corpus,
    load_preferred_semantic_corpus,
    register_sqlite_chat_coordinates,
)


class _FakeCursor:
    def __init__(self, tables):
        self.tables = tables
        self.rows = []
        self.index = 0

    def execute(self, sql, params=None):
        self.index = 0
        if "to_regclass" in sql:
            table = params[0]
            self.rows = [(table if table in self.tables else None,)]
            return
        if "pnf.statement_candidate_factor" in sql:
            self.rows = [(row,) for row in self.tables["pnf.statement_candidate_factor"]]
            return
        if "pnf.graph" in sql:
            self.rows = [(row,) for row in self.tables["pnf.graph"]]
            return
        raise AssertionError(sql)

    def fetchone(self):
        if not self.rows:
            return None
        row = self.rows[0]
        self.rows = self.rows[1:]
        return row

    def fetchmany(self, size):
        if not self.rows:
            return []
        rows = self.rows[:size]
        self.rows = self.rows[size:]
        return rows

    def close(self):
        pass


class _FakeConnection:
    def __init__(self, tables):
        self.tables = tables
        self.closed = False

    def cursor(self):
        return _FakeCursor(self.tables)

    def close(self):
        self.closed = True


def test_postgres_semantic_loader_builds_relational_frames_directly() -> None:
    tables = {
        "pnf.statement_candidate_factor": [
            {
                "conversation_ref": "chat:c1",
                "sentence_id": 1,
                "head_lemma": "prove",
                "argument_role": "actor",
                "lemma": "system",
            },
            {
                "conversation_ref": "chat:c1",
                "sentence_id": 1,
                "head_lemma": "prove",
                "argument_role": "theme",
                "lemma": "consistency",
            },
            {
                "conversation_ref": "chat:c2",
                "sentence_id": 2,
                "head_lemma": "measure",
                "argument_role": "actor",
                "lemma": "sensor",
            },
            {
                "conversation_ref": "chat:c2",
                "sentence_id": 2,
                "head_lemma": "measure",
                "argument_role": "theme",
                "lemma": "metric",
            },
        ],
        "pnf.graph": [
            {
                "conversation_ref": "chat:c2",
                "label": "Riemannian metric tensor",
                "weight": 1.5,
                "graph_revision": "g:1",
            }
        ],
    }

    result = load_postgres_semantic_corpus(
        "postgresql://example",
        connect=lambda _url: _FakeConnection(tables),
    )

    assert result["source"] == "postgresql_semantic_spine"
    assert result["conversation_count"] == 2
    assert result["conversations"]["c1"]["frame_counts"] == {
        "prove(actor:system,theme:consistency)": 1
    }
    assert result["conversations"]["c2"]["factor_counts"]["measure|theme|metric"] == 1
    assert result["ontology_edges"][0]["label"] == "Riemannian metric tensor"
    assert result["source_contract"]["raw_chat_body_persisted"] is False


def test_preferred_loader_falls_back_to_slrw_when_postgres_is_offline(tmp_path: Path) -> None:
    slrw = tmp_path / "fleet_top500_iter1.slrw"
    slrw.write_bytes(b"placeholder")

    def unavailable(_url):
        raise OSError("postgres offline")

    expected = {
        "schema": "itir.pnf.slrw_corpus_factors.v1",
        "conversation_count": 1,
        "conversations": {
            "fallback": {
                "conversation_id": "fallback",
                "factor_counts": {"prove|actor|system": 1},
                "frame_counts": {"prove(actor:system)": 1},
                "pnf_candidate_count": 1,
            }
        },
    }

    result = load_preferred_semantic_corpus(
        database_url="postgresql://offline",
        slrw_path=slrw,
        connect=unavailable,
        slrw_loader=lambda _path: expected,
    )

    assert result["source"] == "slrw"
    assert result["fallback_used"] is True
    assert result["corpus"] == expected
    assert "postgres offline" in result["postgres_error"]


def test_reference_registrar_abstains_without_canonical_node_identity(tmp_path: Path) -> None:
    sqlite_path = tmp_path / "history.sqlite3"
    with sqlite3.connect(sqlite_path) as db:
        db.execute(
            """
            CREATE TABLE conversations (
                conversation_id TEXT PRIMARY KEY,
                title TEXT
            )
            """
        )
        db.execute(
            """
            CREATE TABLE messages (
                conversation_id TEXT,
                message_index INTEGER,
                author TEXT,
                content TEXT,
                message_key TEXT
            )
            """
        )
        db.execute(
            "INSERT INTO conversations VALUES ('c1', 'Thread')"
        )
        db.execute(
            "INSERT INTO messages VALUES ('c1', 0, 'user', 'secret body', 'cache.user.0000')"
        )

    class _NeverConnect:
        def __call__(self, _url):
            raise AssertionError("PostgreSQL must not be contacted before node identity validation")

    # The registrar opens PG before SQLite schema validation by design, so use a
    # benign fake connection; no cursor must be requested on the abstention path.
    class _UnusedConnection:
        def cursor(self):
            raise AssertionError("no PG query expected")
        def close(self):
            pass

    result = register_sqlite_chat_coordinates(
        "postgresql://example",
        sqlite_path=sqlite_path,
        connect=lambda _url: _UnusedConnection(),
    )

    assert result["status"] == "abstained_no_canonical_node_id"
    assert result["inserted"] == 0
    assert result["raw_body_persisted"] is False
