from __future__ import annotations

import hashlib
import json
import os
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence


DEFAULT_SQLITE_HISTORY = Path.home() / ".chatgpt_history.sqlite3"


class PostgresSemanticSpineUnavailable(RuntimeError):
    pass


class PostgresSemanticSpineIncompatible(RuntimeError):
    pass


def _default_connect(database_url: str | None):
    try:
        import psycopg  # type: ignore

        return psycopg.connect(database_url) if database_url else psycopg.connect()
    except ImportError:
        try:
            import psycopg2  # type: ignore

            return psycopg2.connect(database_url) if database_url else psycopg2.connect("")
        except ImportError as exc:
            raise PostgresSemanticSpineUnavailable(
                "psycopg/psycopg2 is unavailable"
            ) from exc


def _json_object(value: Any) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)
    if isinstance(value, str):
        parsed = json.loads(value)
        if isinstance(parsed, Mapping):
            return dict(parsed)
    raise PostgresSemanticSpineIncompatible("semantic row is not a JSON object")


def _table_present(connection: Any, table_name: str) -> bool:
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT to_regclass(%s)::text", (table_name,))
        row = cursor.fetchone()
        return bool(row and row[0])
    finally:
        cursor.close()


def _stream_json_rows(connection: Any, table_name: str, *, batch_size: int = 4096):
    if not _table_present(connection, table_name):
        raise PostgresSemanticSpineIncompatible(f"missing PostgreSQL semantic table: {table_name}")
    cursor = connection.cursor()
    try:
        cursor.execute(f"SELECT to_jsonb(row_data) FROM {table_name} AS row_data")
        while True:
            rows = cursor.fetchmany(batch_size)
            if not rows:
                break
            for row in rows:
                yield _json_object(row[0])
    finally:
        cursor.close()


def load_postgres_semantic_corpus(
    database_url: str | None = None,
    *,
    connect: Callable[[str | None], Any] | None = None,
) -> dict[str, Any]:
    """Stream the canonical semantic PNF spine into hierarchy-ready counters.

    The adapter consumes semantic fields already produced by the PG compiler.
    It does not infer roles, predicates, or conversation identity from strings.
    """
    connector = connect or _default_connect
    try:
        connection = connector(database_url)
    except Exception as exc:
        if isinstance(exc, (PostgresSemanticSpineUnavailable, PostgresSemanticSpineIncompatible)):
            raise
        raise PostgresSemanticSpineUnavailable(str(exc)) from exc

    conversations: dict[str, dict[str, Any]] = {}
    frame_groups: dict[str, dict[tuple[str, str], list[tuple[str, str]]]] = defaultdict(dict)
    factor_rows = 0
    graph_rows = 0
    ontology_edges: list[dict[str, Any]] = []

    required_factor_fields = {
        "conversation_ref",
        "sentence_id",
        "head_lemma",
        "argument_role",
        "lemma",
    }

    try:
        for row in _stream_json_rows(connection, "pnf.statement_candidate_factor"):
            missing = required_factor_fields.difference(row)
            if missing:
                raise PostgresSemanticSpineIncompatible(
                    "pnf.statement_candidate_factor missing required semantic fields: "
                    + ",".join(sorted(missing))
                )
            conversation_ref = str(row["conversation_ref"] or "").strip()
            head_lemma = str(row["head_lemma"] or "").strip().casefold()
            role = str(row["argument_role"] or "").strip()
            lemma = str(row["lemma"] or "").strip().casefold()
            sentence_id = str(row["sentence_id"])
            if not conversation_ref or not head_lemma or not role or not lemma:
                continue
            conversation_id = (
                conversation_ref[5:]
                if conversation_ref.startswith("chat:")
                else conversation_ref
            )
            entry = conversations.setdefault(
                conversation_id,
                {
                    "conversation_id": conversation_id,
                    "document_ref": conversation_ref,
                    "factor_counts": Counter(),
                    "frame_counts": Counter(),
                    "pnf_candidate_count": 0,
                },
            )
            factor_key = f"{head_lemma}|{role}|{lemma}"
            entry["factor_counts"][factor_key] += 1
            entry["pnf_candidate_count"] += 1
            factor_rows += 1
            key = (sentence_id, head_lemma)
            frame_groups[conversation_id].setdefault(key, []).append((role, lemma))

        for conversation_id, groups in frame_groups.items():
            target = conversations[conversation_id]["frame_counts"]
            for (_sentence_id, predicate), members in groups.items():
                typed_members = sorted(set(members))
                args = ",".join(f"{role}:{lemma}" for role, lemma in typed_members)
                target[f"{predicate}({args})"] += 1

        for row in _stream_json_rows(connection, "pnf.graph"):
            graph_rows += 1
            conversation_ref = str(row.get("conversation_ref") or "").strip()
            label = str(
                row.get("label")
                or row.get("edge_label")
                or row.get("target_label")
                or ""
            ).strip()
            if not conversation_ref or not label:
                continue
            conversation_id = (
                conversation_ref[5:]
                if conversation_ref.startswith("chat:")
                else conversation_ref
            )
            if conversation_id not in conversations:
                continue
            weight = row.get("weight", 1.0)
            if isinstance(weight, bool) or not isinstance(weight, (int, float)):
                weight = 1.0
            ontology_edges.append(
                {
                    "conversation_ids": [conversation_id],
                    "label": label,
                    "weight": float(weight),
                    "provenance_ref": str(
                        row.get("provenance_ref")
                        or row.get("graph_revision")
                        or "pnf.graph"
                    ),
                }
            )
    finally:
        try:
            connection.close()
        except Exception:
            pass

    if not conversations:
        raise PostgresSemanticSpineIncompatible(
            "PostgreSQL semantic spine returned no conversation-bound PNF factors"
        )

    normalized = {
        conversation_id: {
            **{
                key: value
                for key, value in entry.items()
                if key not in {"factor_counts", "frame_counts"}
            },
            "factor_counts": dict(sorted(entry["factor_counts"].items())),
            "frame_counts": dict(sorted(entry["frame_counts"].items())),
        }
        for conversation_id, entry in sorted(conversations.items())
    }
    return {
        "schema": "itir.pnf.postgres_semantic_corpus.v1",
        "source": "postgresql_semantic_spine",
        "conversation_count": len(normalized),
        "pnf_candidate_count": factor_rows,
        "graph_row_count": graph_rows,
        "conversations": normalized,
        "ontology_edges": ontology_edges,
        "source_contract": {
            "factor_table": "pnf.statement_candidate_factor",
            "graph_table": "pnf.graph",
            "semantic_fields": [
                "conversation_ref",
                "sentence_id",
                "head_lemma",
                "argument_role",
                "lemma",
            ],
            "raw_chat_body_persisted": False,
        },
    }


def load_preferred_semantic_corpus(
    *,
    database_url: str | None = None,
    slrw_path: str | Path | None = None,
    connect: Callable[[str | None], Any] | None = None,
    slrw_loader: Callable[[str | Path], Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """Prefer PostgreSQL semantic truth; fall back to SLRW when PG is offline."""
    resolved_url = database_url or os.environ.get("DATABASE_URL") or None
    pg_error: str | None = None
    try:
        payload = load_postgres_semantic_corpus(
            resolved_url,
            connect=connect,
        )
        return {
            "source": "postgresql",
            "corpus": payload,
            "ontology_edges": payload.get("ontology_edges", []),
            "fallback_used": False,
            "postgres_error": None,
        }
    except (PostgresSemanticSpineUnavailable, PostgresSemanticSpineIncompatible) as exc:
        pg_error = str(exc)

    if slrw_path is None:
        raise PostgresSemanticSpineUnavailable(
            f"PostgreSQL semantic spine unavailable and no SLRW fallback supplied: {pg_error}"
        )
    path = Path(slrw_path).expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError(
            f"PostgreSQL semantic spine unavailable and SLRW fallback is missing: {path}"
        )
    if slrw_loader is None:
        from .pnf_spectral_packet import load_slrw_conversation_factors

        slrw_loader = load_slrw_conversation_factors
    corpus = dict(slrw_loader(path))
    return {
        "source": "slrw",
        "corpus": corpus,
        "ontology_edges": [],
        "fallback_used": True,
        "postgres_error": pg_error,
    }


def _sqlite_columns(connection: sqlite3.Connection, table: str) -> set[str]:
    return {
        str(row[1])
        for row in connection.execute(f"PRAGMA table_info({table})").fetchall()
    }


def register_sqlite_chat_coordinates(
    database_url: str | None = None,
    *,
    sqlite_path: str | Path = DEFAULT_SQLITE_HISTORY,
    connect: Callable[[str | None], Any] | None = None,
    limit: int | None = None,
) -> dict[str, Any]:
    """Register immutable SQLite chat coordinates in PG without copying bodies."""
    path = Path(sqlite_path).expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError(path)

    connector = connect or _default_connect
    pg = connector(database_url or os.environ.get("DATABASE_URL") or None)
    inserted = replayed = conflicts = 0

    with sqlite3.connect(path) as sqlite:
        message_columns = _sqlite_columns(sqlite, "messages")
        if "node_id" not in message_columns:
            return {
                "schema": "itir.pg.chat_coordinate_registration.v1",
                "sqlite_path": str(path),
                "inserted": 0,
                "replayed": 0,
                "conflicts": 0,
                "status": "abstained_no_canonical_node_id",
                "raw_body_persisted": False,
            }

        optional = {
            "parent_node_id": "parent_node_id" if "parent_node_id" in message_columns else "NULL",
            "create_time": "create_time" if "create_time" in message_columns else "NULL",
            "message_ref": "source_message_id" if "source_message_id" in message_columns else "message_key",
        }
        sql = f"""
            SELECT m.conversation_id,
                   {optional['message_ref']} AS message_ref,
                   m.node_id,
                   {optional['parent_node_id']} AS parent_node_id,
                   {optional['create_time']} AS create_time,
                   m.author,
                   m.content,
                   COALESCE(c.title, '') AS thread_title
            FROM messages m
            LEFT JOIN conversations c ON c.conversation_id=m.conversation_id
            WHERE m.node_id IS NOT NULL AND TRIM(m.node_id) != ''
            ORDER BY m.conversation_id, m.message_index
        """
        params: tuple[Any, ...] = ()
        if limit is not None:
            sql += " LIMIT ?"
            params = (max(0, int(limit)),)
        rows = sqlite.execute(sql, params).fetchall()

    try:
        if not _table_present(pg, "corpus.chat_archive_message"):
            raise PostgresSemanticSpineIncompatible(
                "missing corpus.chat_archive_message; install the slr reference-only schema first"
            )
        cursor = pg.cursor()
        try:
            for (
                conversation_ref,
                message_ref,
                node_ref,
                parent_node_ref,
                create_time,
                role_ref,
                content,
                thread_title,
            ) in rows:
                message_ref = str(message_ref or node_ref)
                node_ref = str(node_ref)
                body_sha256 = hashlib.sha256(str(content or "").encode("utf-8")).hexdigest()
                archive_locator = f"sqlite:canonical#{node_ref}"
                cursor.execute(
                    """
                    SELECT body_sha256, archive_locator, source_thread_ref
                    FROM corpus.chat_archive_message
                    WHERE message_ref=%s
                    """,
                    (message_ref,),
                )
                prior = cursor.fetchone()
                if prior:
                    if (
                        prior[0] == body_sha256
                        and prior[1] == archive_locator
                        and prior[2] == str(conversation_ref)
                    ):
                        replayed += 1
                    else:
                        conflicts += 1
                    continue
                cursor.execute(
                    """
                    INSERT INTO corpus.chat_archive_message
                    (message_ref,conversation_ref,node_ref,parent_node_ref,
                     branch_membership_ref,message_time_ref,role_ref,thread_title,
                     content_kind_ref,document_ref,source_revision_ref,full_message_span_ref,
                     identity_verified,candidate_only,creates_semantic_authority,
                     applicability_promoted,claim_truth_promoted,
                     source_thread_ref,archive_locator,body_sha256,
                     attachment_refs_json,provenance_ref)
                    VALUES (%s,%s,%s,%s,'active',%s,%s,%s,'message',
                            NULL,%s,NULL,TRUE,TRUE,FALSE,FALSE,FALSE,
                            %s,%s,%s,'[]','re-gpt:sqlite-coordinate:v1')
                    """,
                    (
                        message_ref,
                        str(conversation_ref),
                        node_ref,
                        str(parent_node_ref) if parent_node_ref else None,
                        str(create_time or ""),
                        str(role_ref or "unknown"),
                        str(thread_title or ""),
                        f"chat-reference:sha256:{body_sha256}",
                        str(conversation_ref),
                        archive_locator,
                        body_sha256,
                    ),
                )
                inserted += 1
            pg.commit()
        finally:
            cursor.close()
    finally:
        try:
            pg.close()
        except Exception:
            pass

    return {
        "schema": "itir.pg.chat_coordinate_registration.v1",
        "sqlite_path": str(path),
        "inserted": inserted,
        "replayed": replayed,
        "conflicts": conflicts,
        "status": "complete",
        "raw_body_persisted": False,
        "document_ref": None,
        "archive_locator_shape": "sqlite:canonical#<node_id>",
    }
