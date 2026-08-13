"""SQLite ledgers for Casey operations and builds.

Observer-only: downstream systems may reference operation/build ids and hashes,
not materialize mutable candidate graphs as canonical state.

Implements Path 2 of `docs/planning/casey_git_clone_statiBaker_interface_20260309.md`.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping


@dataclass(frozen=True)
class OperationRecord:
    operation_id: str
    operation_kind: str
    ws_id: str | None
    path: str | None
    tree_id_before: str | None
    tree_id_after: str | None
    chosen_fv_id: str | None
    resolved_fv_id: str | None
    actor: str | None
    created_at: str
    receipt_hash: str


@dataclass(frozen=True)
class BuildRecord:
    build_id: str
    tree_id: str
    selection_digest: str
    created_at: str
    source_operation_id: str | None = None


def _connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON;")
    conn.execute("PRAGMA journal_mode=DELETE;")
    return conn


def ensure_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS casey_operation_ledger (
          operation_id TEXT PRIMARY KEY,
          operation_kind TEXT NOT NULL,
          ws_id TEXT,
          path TEXT,
          tree_id_before TEXT,
          tree_id_after TEXT,
          chosen_fv_id TEXT,
          resolved_fv_id TEXT,
          actor TEXT,
          created_at TEXT NOT NULL,
          receipt_hash TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS casey_build_ledger (
          build_id TEXT PRIMARY KEY,
          tree_id TEXT NOT NULL,
          selection_digest TEXT NOT NULL,
          created_at TEXT NOT NULL,
          source_operation_id TEXT
        );

        CREATE TABLE IF NOT EXISTS casey_build_selection_refs (
          build_id TEXT NOT NULL REFERENCES casey_build_ledger(build_id) ON DELETE CASCADE,
          path TEXT NOT NULL,
          fv_id TEXT NOT NULL,
          PRIMARY KEY (build_id, path)
        );
        """
    )


def upsert_operation(*, db_path: Path, record: OperationRecord) -> None:
    with _connect(db_path) as conn:
        ensure_schema(conn)
        conn.execute(
            """
            INSERT OR REPLACE INTO casey_operation_ledger(
              operation_id, operation_kind, ws_id, path, tree_id_before, tree_id_after,
              chosen_fv_id, resolved_fv_id, actor, created_at, receipt_hash
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                record.operation_id,
                record.operation_kind,
                record.ws_id,
                record.path,
                record.tree_id_before,
                record.tree_id_after,
                record.chosen_fv_id,
                record.resolved_fv_id,
                record.actor,
                record.created_at,
                record.receipt_hash,
            ),
        )
        conn.commit()


def upsert_build(
    *,
    db_path: Path,
    record: BuildRecord,
    selection_refs: Iterable[Mapping[str, Any]] = (),
) -> None:
    with _connect(db_path) as conn:
        ensure_schema(conn)
        conn.execute(
            """
            INSERT OR REPLACE INTO casey_build_ledger(
              build_id, tree_id, selection_digest, created_at, source_operation_id
            ) VALUES (?,?,?,?,?)
            """,
            (
                record.build_id,
                record.tree_id,
                record.selection_digest,
                record.created_at,
                record.source_operation_id,
            ),
        )
        conn.execute("DELETE FROM casey_build_selection_refs WHERE build_id = ?", (record.build_id,))
        for payload in selection_refs:
            if not isinstance(payload, Mapping):
                continue
            conn.execute(
                """
                INSERT INTO casey_build_selection_refs(build_id, path, fv_id)
                VALUES (?,?,?)
                """,
                (
                    record.build_id,
                    str(payload.get("path") or ""),
                    str(payload.get("fv_id") or ""),
                ),
            )
        conn.commit()


def load_operation(*, db_path: Path, operation_id: str) -> dict[str, Any] | None:
    with _connect(db_path) as conn:
        ensure_schema(conn)
        row = conn.execute(
            "SELECT * FROM casey_operation_ledger WHERE operation_id = ?",
            (operation_id,),
        ).fetchone()
        return dict(row) if row is not None else None


def load_build(*, db_path: Path, build_id: str) -> dict[str, Any] | None:
    with _connect(db_path) as conn:
        ensure_schema(conn)
        row = conn.execute(
            "SELECT * FROM casey_build_ledger WHERE build_id = ?",
            (build_id,),
        ).fetchone()
        if row is None:
            return None
        selection = [
            dict(r)
            for r in conn.execute(
                "SELECT path, fv_id FROM casey_build_selection_refs WHERE build_id = ? ORDER BY path",
                (build_id,),
            ).fetchall()
        ]
        out = dict(row)
        out["selection_refs"] = selection
        return out
