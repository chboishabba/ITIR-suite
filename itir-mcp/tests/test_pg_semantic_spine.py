from __future__ import annotations

import sqlite3
from pathlib import Path

from itir_mcp.pg_semantic_spine import (
    PostgresSemanticSpineUnavailable,
    load_postgres_semantic_corpus,
    load_preferred_semantic_corpus,
    register_sqlite_chat_coordinates,
)
from itir_mcp.spectral_plot_tools import stream_preferred_corpus


class _FakeCursor:
    def __init__(self, tables):
        self.tables = tables
        self.rows = []

    def execute(self, sql, params=None):
        if "information_schema.columns" in sql:
            schema, table = params
            key = f"{schema}.{table}"
            columns = self.tables.get(f"{key}:columns", [])
            self.rows = [(column,) for column in columns]
            return
        if "to_regclass" in sql:
            table = params[0]
            self.rows = [(table if table in self.tables else None,)]
            return
        if "pnf.statement_candidate_factor" in sql:
            self.rows = [(row,) for row in self.tables["pnf.statement_candidate_factor"]]
            return
        if "pnf.graph" in sql:
            self.rows = [(row,) for row in self.tables.get("pnf.graph", [])]
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

    def fetchall(self):
        rows = list(self.rows)
        self.rows = []
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
    factor_columns = [
        "candidate_ref",
        "batch_ref",
        "statement_ref",
        "role_ref",
        "source_start_char",
        "source_end_char",
        "surface",
        "lemma",
        "dependency_ref",
        "candidate_only",
    ]
    tables = {
        "pnf.statement_candidate_factor:columns": factor_columns,
        "pnf.statement_candidate_factor": [
            {
                "candidate_ref": "cand-1",
                "batch_ref": "batch-1",
                "statement_ref": "statement:c1",
                "role_ref": "actor",
                "source_start_char": 0,
                "source_end_char": 6,
                "surface": "System",
                "lemma": "system",
                "dependency_ref": "prove",
                "candidate_only": True,
            },
            {
                "candidate_ref": "cand-2",
                "batch_ref": "batch-1",
                "statement_ref": "statement:c1",
                "role_ref": "theme",
                "source_start_char": 7,
                "source_end_char": 18,
                "surface": "consistency",
                "lemma": "consistency",
                "dependency_ref": "prove",
                "candidate_only": True,
            },
            {
                "candidate_ref": "cand-3",
                "batch_ref": "batch-2",
                "statement_ref": "statement:c2",
                "role_ref": "actor",
                "source_start_char": 0,
                "source_end_char": 6,
                "surface": "Sensor",
                "lemma": "sensor",
                "dependency_ref": "measure",
                "candidate_only": True,
            },
            {
                "candidate_ref": "cand-4",
                "batch_ref": "batch-2",
                "statement_ref": "statement:c2",
                "role_ref": "theme",
                "source_start_char": 7,
                "source_end_char": 13,
                "surface": "metric",
                "lemma": "metric",
                "dependency_ref": "measure",
                "candidate_only": True,
            },
        ],
        "pnf.graph": [
            {
                "statement_ref": "statement:c2",
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
    assert result["conversations"]["statement:c1"]["frame_counts"] == {
        "prove(actor:system,theme:consistency)": 1
    }
    assert (
        result["conversations"]["statement:c2"]["factor_counts"]["measure|theme|metric"]
        == 1
    )
    assert result["ontology_edges"][0]["label"] == "Riemannian metric tensor"
    assert result["source_contract"]["grouping_identity"] == "statement_ref"
    assert "head_lemma" in result["source_contract"]["unavailable_fields_not_inferred"]
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

    def never_connect(_url):
        raise AssertionError("PostgreSQL must not be contacted before node identity validation")

    result = register_sqlite_chat_coordinates(
        "postgresql://example",
        sqlite_path=sqlite_path,
        connect=never_connect,
    )

    assert result["status"] == "abstained_no_canonical_node_id"
    assert result["inserted"] == 0
    assert result["raw_body_persisted"] is False


class _RegistrarCursor:
    def __init__(self, owner):
        self.owner = owner
        self.rows = []

    def execute(self, sql, params=None):
        self.owner.statements.append((sql, params))
        if "to_regclass" in sql:
            table = params[0]
            present = table in {
                "corpus.chat_archive_message",
                "corpus.chat_archive_reference_conflict",
            }
            self.rows = [(table if present else None,)]
        elif "SELECT body_sha256" in sql:
            self.rows = []
        else:
            self.rows = []

    def fetchone(self):
        if not self.rows:
            return None
        row = self.rows[0]
        self.rows = self.rows[1:]
        return row

    def close(self):
        pass


class _RegistrarConnection:
    def __init__(self):
        self.statements = []
        self.committed = False

    def cursor(self):
        return _RegistrarCursor(self)

    def commit(self):
        self.committed = True

    def close(self):
        pass


def test_reference_registrar_inserts_only_coordinates_and_digest(tmp_path: Path) -> None:
    sqlite_path = tmp_path / "history-with-node.sqlite3"
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
                message_key TEXT,
                source_message_id TEXT,
                node_id TEXT,
                parent_node_id TEXT,
                create_time REAL
            )
            """
        )
        db.execute("INSERT INTO conversations VALUES ('c1', 'Thread')")
        db.execute(
            """
            INSERT INTO messages VALUES
            ('c1', 0, 'user', 'body stays in sqlite', 'cache.user.0000',
             'm1', 'node-1', NULL, 1760000000.0)
            """
        )

    pg = _RegistrarConnection()
    result = register_sqlite_chat_coordinates(
        "postgresql://example",
        sqlite_path=sqlite_path,
        connect=lambda _url: pg,
    )

    assert result["status"] == "complete"
    assert result["inserted"] == 1
    assert result["raw_body_persisted"] is False
    assert result["document_ref"] is None
    assert pg.committed is True

    inserts = [
        (sql, params)
        for sql, params in pg.statements
        if "INSERT INTO corpus.chat_archive_message" in sql
    ]
    assert len(inserts) == 1
    sql, params = inserts[0]
    assert "document_ref" in sql
    assert "NULL" in sql
    assert "body stays in sqlite" not in repr(params)
    assert "sqlite:canonical#node-1" in params
    assert any(
        isinstance(value, str)
        and len(value) == 64
        and all(ch in "0123456789abcdef" for ch in value)
        for value in params
    )


def test_postgres_graph_explicitly_maps_statement_to_conversation() -> None:
    columns = [
        "candidate_ref", "batch_ref", "statement_ref", "role_ref",
        "source_start_char", "source_end_char", "surface", "lemma",
        "dependency_ref", "candidate_only",
    ]
    tables = {
        "pnf.statement_candidate_factor:columns": columns,
        "pnf.statement_candidate_factor": [
            {
                "candidate_ref": "cand-1",
                "batch_ref": "batch-1",
                "statement_ref": "statement:s1",
                "role_ref": "actor",
                "source_start_char": 0,
                "source_end_char": 4,
                "surface": "node",
                "lemma": "node",
                "dependency_ref": "link",
                "candidate_only": True,
            }
        ],
        "pnf.graph": [
            {
                "statement_ref": "statement:s1",
                "conversation_ref": "chat:conversation-1",
                "label": "relational schema",
            }
        ],
    }

    result = load_postgres_semantic_corpus(
        "postgresql://example",
        connect=lambda _url: _FakeConnection(tables),
    )

    assert set(result["conversations"]) == {"conversation-1"}
    assert result["conversations"]["conversation-1"]["statement_ref"] == "statement:s1"
    assert result["ontology_edges"][0]["conversation_ids"] == ["conversation-1"]


def test_public_preferred_stream_uses_slrw_fallback(tmp_path: Path) -> None:
    slrw = tmp_path / "fallback.slrw"
    slrw.write_bytes(b"placeholder")

    def offline(_url):
        raise OSError("offline")

    from itir_mcp import pnf_spectral_packet

    original = pnf_spectral_packet.load_slrw_conversation_factors
    pnf_spectral_packet.load_slrw_conversation_factors = lambda _path: {
        "schema": "itir.pnf.slrw_corpus_factors.v1",
        "conversations": {
            "fallback": {
                "conversation_id": "fallback",
                "factor_counts": {"x|actor|y": 1},
                "frame_counts": {"x(actor:y)": 1},
                "pnf_candidate_count": 1,
            }
        },
    }
    try:
        result = stream_preferred_corpus(
            database_url="postgresql://offline",
            slrw_fallback_path=slrw,
            connect=offline,
        )
    finally:
        pnf_spectral_packet.load_slrw_conversation_factors = original

    assert result["source"] == "slrw"
    assert result["fallback_used"] is True
    assert "offline" in result["postgres_error"]


def test_reference_registrar_abstains_when_slr_reference_columns_are_missing(
    tmp_path: Path,
) -> None:
    sqlite_path = tmp_path / "canonical.sqlite3"
    with sqlite3.connect(sqlite_path) as db:
        db.execute("CREATE TABLE conversations (conversation_id TEXT PRIMARY KEY, title TEXT)")
        db.execute(
            """
            CREATE TABLE messages (
                conversation_id TEXT,
                message_index INTEGER,
                author TEXT,
                content TEXT,
                message_key TEXT,
                node_id TEXT,
                parent_node_id TEXT,
                source_message_id TEXT,
                create_time REAL
            )
            """
        )
        db.execute("INSERT INTO conversations VALUES ('c1', 'Thread')")
        db.execute(
            """
            INSERT INTO messages VALUES
            ('c1',0,'user','body','m1','node-1',NULL,'msg-1',1.0)
            """
        )

    class Cursor:
        def __init__(self):
            self.rows = []

        def execute(self, sql, params=None):
            if "to_regclass" in sql:
                self.rows = [("corpus.chat_archive_message",)]
            elif "information_schema.columns" in sql:
                self.rows = [
                    ("message_ref",), ("conversation_ref",), ("node_ref",),
                    ("document_ref",), ("source_revision_ref",),
                ]
            else:
                raise AssertionError(sql)

        def fetchone(self):
            return self.rows.pop(0) if self.rows else None

        def fetchall(self):
            rows = list(self.rows)
            self.rows = []
            return rows

        def close(self):
            pass

    class Connection:
        def cursor(self):
            return Cursor()

        def close(self):
            pass

    result = register_sqlite_chat_coordinates(
        "postgresql://example",
        sqlite_path=sqlite_path,
        connect=lambda _url: Connection(),
    )

    assert result["status"] == "abstained_reference_schema_not_installed"
    assert "body_sha256" in result["missing_columns"]
    assert result["raw_body_persisted"] is False
