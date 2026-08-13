"""Casey-owned SQLite runtime store for the local testbed.

This runtime is distinct from the observer ledgers. It persists the mutable
Casey state needed to exercise publish/sync/collapse/build semantics locally.
"""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterable, Iterator, Mapping

from .models import Blob, BuildView, FileVersion, PathState, TreeState, WorkspacePolicy, WorkspaceView, utc_now_iso


def _connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON;")
    conn.execute("PRAGMA journal_mode=DELETE;")
    return conn


@contextmanager
def runtime_transaction(*, db_path: Path) -> Iterator[sqlite3.Connection]:
    conn = _connect(db_path)
    try:
        ensure_schema(conn)
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def ensure_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS casey_runtime_meta (
          key TEXT PRIMARY KEY,
          value TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS casey_runtime_blobs (
          blob_id TEXT PRIMARY KEY,
          size INTEGER NOT NULL,
          bytes BLOB NOT NULL
        );

        CREATE TABLE IF NOT EXISTS casey_runtime_file_versions (
          fv_id TEXT PRIMARY KEY,
          blob_id TEXT NOT NULL REFERENCES casey_runtime_blobs(blob_id),
          author TEXT NOT NULL,
          created_at TEXT NOT NULL,
          base_fv_id TEXT,
          summary TEXT
        );

        CREATE TABLE IF NOT EXISTS casey_runtime_trees (
          tree_id TEXT PRIMARY KEY,
          created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS casey_runtime_tree_candidates (
          tree_id TEXT NOT NULL REFERENCES casey_runtime_trees(tree_id) ON DELETE CASCADE,
          path TEXT NOT NULL,
          fv_id TEXT NOT NULL,
          PRIMARY KEY (tree_id, path, fv_id)
        );

        CREATE TABLE IF NOT EXISTS casey_runtime_workspaces (
          ws_id TEXT PRIMARY KEY,
          user TEXT NOT NULL,
          head_tree_id TEXT NOT NULL REFERENCES casey_runtime_trees(tree_id),
          prefer_author TEXT,
          tie_break TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS casey_runtime_workspace_selections (
          ws_id TEXT NOT NULL REFERENCES casey_runtime_workspaces(ws_id) ON DELETE CASCADE,
          path TEXT NOT NULL,
          fv_id TEXT NOT NULL,
          PRIMARY KEY (ws_id, path)
        );

        CREATE TABLE IF NOT EXISTS casey_runtime_builds (
          build_id TEXT PRIMARY KEY,
          tree_id TEXT NOT NULL REFERENCES casey_runtime_trees(tree_id),
          created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS casey_runtime_build_selections (
          build_id TEXT NOT NULL REFERENCES casey_runtime_builds(build_id) ON DELETE CASCADE,
          path TEXT NOT NULL,
          fv_id TEXT NOT NULL,
          PRIMARY KEY (build_id, path)
        );
        """
    )


def _require_value(conn: sqlite3.Connection, key: str) -> str:
    row = conn.execute(
        "SELECT value FROM casey_runtime_meta WHERE key = ?",
        (key,),
    ).fetchone()
    if row is None:
        raise ValueError(f"Runtime metadata missing: {key}")
    return str(row["value"])


def initialize_runtime(
    *,
    db_path: Path,
    ws_id: str,
    user: str,
    prefer_author: str | None = None,
    tie_break: str = "stable_hash",
) -> WorkspaceView:
    with runtime_transaction(db_path=db_path) as conn:
        return initialize_runtime_conn(
            conn=conn,
            ws_id=ws_id,
            user=user,
            prefer_author=prefer_author,
            tie_break=tie_break,
        )


def initialize_runtime_conn(
    *,
    conn: sqlite3.Connection,
    ws_id: str,
    user: str,
    prefer_author: str | None = None,
    tie_break: str = "stable_hash",
) -> WorkspaceView:
    empty_tree = TreeState.from_paths({})
    policy = WorkspacePolicy(prefer_author=prefer_author or user, tie_break=tie_break)
    policy.validate()
    workspace = WorkspaceView(
        ws_id=ws_id,
        user=user,
        head=empty_tree.tree_id,
        selection={},
        policy=policy,
    )
    existing = conn.execute(
        "SELECT value FROM casey_runtime_meta WHERE key = 'current_tree_id'"
    ).fetchone()
    if existing is not None:
        raise ValueError("Runtime already initialized")
    _upsert_tree(conn, empty_tree, created_at=utc_now_iso())
    _set_meta(conn, "current_tree_id", empty_tree.tree_id)
    _upsert_workspace(conn, workspace)
    return workspace


def create_workspace(
    *,
    db_path: Path,
    ws_id: str,
    user: str,
    prefer_author: str | None = None,
    tie_break: str = "stable_hash",
    head_tree_id: str | None = None,
) -> WorkspaceView:
    with runtime_transaction(db_path=db_path) as conn:
        return create_workspace_conn(
            conn=conn,
            ws_id=ws_id,
            user=user,
            prefer_author=prefer_author,
            tie_break=tie_break,
            head_tree_id=head_tree_id,
        )


def create_workspace_conn(
    *,
    conn: sqlite3.Connection,
    ws_id: str,
    user: str,
    prefer_author: str | None = None,
    tie_break: str = "stable_hash",
    head_tree_id: str | None = None,
) -> WorkspaceView:
    if head_tree_id is None:
        head_tree_id = _require_value(conn, "current_tree_id")
    tree = _load_tree(conn, head_tree_id)
    policy = WorkspacePolicy(prefer_author=prefer_author or user, tie_break=tie_break)
    policy.validate()
    selection = {
        path: state.candidates[0]
        for path, state in tree.paths.items()
        if len(state.candidates) == 1
    }
    workspace = WorkspaceView(
        ws_id=ws_id,
        user=user,
        head=head_tree_id,
        selection=selection,
        policy=policy,
    )
    workspace.validate_against(tree.paths)
    _upsert_workspace(conn, workspace)
    return workspace


def store_publish_result(
    *,
    db_path: Path,
    blobs: Mapping[str, Blob],
    file_versions: Mapping[str, FileVersion],
    tree_state: TreeState,
    created_at: str | None = None,
) -> None:
    with runtime_transaction(db_path=db_path) as conn:
        store_publish_result_conn(
            conn=conn,
            blobs=blobs,
            file_versions=file_versions,
            tree_state=tree_state,
            created_at=created_at,
        )


def store_publish_result_conn(
    *,
    conn: sqlite3.Connection,
    blobs: Mapping[str, Blob],
    file_versions: Mapping[str, FileVersion],
    tree_state: TreeState,
    created_at: str | None = None,
) -> None:
    for blob in blobs.values():
        conn.execute(
            """
            INSERT OR REPLACE INTO casey_runtime_blobs(blob_id, size, bytes)
            VALUES (?,?,?)
            """,
            (blob.blob_id, blob.size, sqlite3.Binary(blob.bytes)),
        )
    for fv in file_versions.values():
        conn.execute(
            """
            INSERT OR REPLACE INTO casey_runtime_file_versions(
              fv_id, blob_id, author, created_at, base_fv_id, summary
            ) VALUES (?,?,?,?,?,?)
            """,
            (
                fv.fv_id,
                fv.blob_id,
                fv.author,
                fv.created_at,
                fv.base_fv_id,
                fv.summary,
            ),
        )
    _upsert_tree(conn, tree_state, created_at=created_at or utc_now_iso())


def save_workspace(*, db_path: Path, workspace: WorkspaceView) -> None:
    with runtime_transaction(db_path=db_path) as conn:
        save_workspace_conn(conn=conn, workspace=workspace)


def save_workspace_conn(*, conn: sqlite3.Connection, workspace: WorkspaceView) -> None:
    _upsert_workspace(conn, workspace)


def save_build(*, db_path: Path, build: BuildView) -> None:
    with runtime_transaction(db_path=db_path) as conn:
        save_build_conn(conn=conn, build=build)


def save_build_conn(*, conn: sqlite3.Connection, build: BuildView) -> None:
    conn.execute(
        """
        INSERT OR REPLACE INTO casey_runtime_builds(build_id, tree_id, created_at)
        VALUES (?,?,?)
        """,
        (build.build_id, build.tree_id, build.created_at),
    )
    conn.execute(
        "DELETE FROM casey_runtime_build_selections WHERE build_id = ?",
        (build.build_id,),
    )
    for path, fv_id in sorted(build.selection.items()):
        conn.execute(
            """
            INSERT INTO casey_runtime_build_selections(build_id, path, fv_id)
            VALUES (?,?,?)
            """,
            (build.build_id, path, fv_id),
        )


def set_current_tree_id(*, db_path: Path, tree_id: str) -> None:
    with runtime_transaction(db_path=db_path) as conn:
        set_current_tree_id_conn(conn=conn, tree_id=tree_id)


def set_current_tree_id_conn(*, conn: sqlite3.Connection, tree_id: str) -> None:
    _load_tree(conn, tree_id)
    _set_meta(conn, "current_tree_id", tree_id)


def load_current_tree_id(*, db_path: Path) -> str:
    with runtime_transaction(db_path=db_path) as conn:
        return load_current_tree_id_conn(conn=conn)


def load_current_tree_id_conn(*, conn: sqlite3.Connection) -> str:
    return _require_value(conn, "current_tree_id")


def load_tree(*, db_path: Path, tree_id: str) -> TreeState:
    with runtime_transaction(db_path=db_path) as conn:
        return load_tree_conn(conn=conn, tree_id=tree_id)


def load_tree_conn(*, conn: sqlite3.Connection, tree_id: str) -> TreeState:
    return _load_tree(conn, tree_id)


def load_current_tree(*, db_path: Path) -> TreeState:
    with runtime_transaction(db_path=db_path) as conn:
        return load_current_tree_conn(conn=conn)


def load_current_tree_conn(*, conn: sqlite3.Connection) -> TreeState:
    return load_tree_conn(conn=conn, tree_id=load_current_tree_id_conn(conn=conn))


def load_workspace(*, db_path: Path, ws_id: str) -> WorkspaceView:
    with runtime_transaction(db_path=db_path) as conn:
        return load_workspace_conn(conn=conn, ws_id=ws_id)


def load_workspace_conn(*, conn: sqlite3.Connection, ws_id: str) -> WorkspaceView:
    row = conn.execute(
        """
        SELECT ws_id, user, head_tree_id, prefer_author, tie_break
        FROM casey_runtime_workspaces
        WHERE ws_id = ?
        """,
        (ws_id,),
    ).fetchone()
    if row is None:
        raise ValueError(f"Workspace missing: {ws_id}")
    selections = {
        str(r["path"]): str(r["fv_id"])
        for r in conn.execute(
            """
            SELECT path, fv_id
            FROM casey_runtime_workspace_selections
            WHERE ws_id = ?
            ORDER BY path
            """,
            (ws_id,),
        ).fetchall()
    }
    workspace = WorkspaceView(
        ws_id=str(row["ws_id"]),
        user=str(row["user"]),
        head=str(row["head_tree_id"]),
        selection=selections,
        policy=WorkspacePolicy(
            prefer_author=row["prefer_author"],
            tie_break=str(row["tie_break"]),
        ),
    )
    tree = _load_tree(conn, workspace.head)
    workspace.validate_against(tree.paths)
    return workspace


def load_file_versions(*, db_path: Path, fv_ids: Iterable[str]) -> dict[str, FileVersion]:
    with runtime_transaction(db_path=db_path) as conn:
        return load_file_versions_conn(conn=conn, fv_ids=fv_ids)


def load_file_versions_conn(
    *, conn: sqlite3.Connection, fv_ids: Iterable[str]
) -> dict[str, FileVersion]:
    ids = sorted({fv_id for fv_id in fv_ids})
    if not ids:
        return {}
    placeholders = ",".join("?" for _ in ids)
    rows = conn.execute(
        f"""
        SELECT fv_id, blob_id, author, created_at, base_fv_id, summary
        FROM casey_runtime_file_versions
        WHERE fv_id IN ({placeholders})
        """,
        tuple(ids),
    ).fetchall()
    return {
        str(row["fv_id"]): FileVersion(
            fv_id=str(row["fv_id"]),
            blob_id=str(row["blob_id"]),
            author=str(row["author"]),
            created_at=str(row["created_at"]),
            base_fv_id=row["base_fv_id"],
            summary=row["summary"],
        )
        for row in rows
    }


def load_build(*, db_path: Path, build_id: str) -> BuildView:
    with runtime_transaction(db_path=db_path) as conn:
        return load_build_conn(conn=conn, build_id=build_id)


def load_build_conn(*, conn: sqlite3.Connection, build_id: str) -> BuildView:
    row = conn.execute(
        "SELECT build_id, tree_id, created_at FROM casey_runtime_builds WHERE build_id = ?",
        (build_id,),
    ).fetchone()
    if row is None:
        raise ValueError(f"Build missing: {build_id}")
    selection = {
        str(r["path"]): str(r["fv_id"])
        for r in conn.execute(
            """
            SELECT path, fv_id
            FROM casey_runtime_build_selections
            WHERE build_id = ?
            ORDER BY path
            """,
            (build_id,),
        ).fetchall()
    }
    return BuildView(
        build_id=str(row["build_id"]),
        tree_id=str(row["tree_id"]),
        selection=selection,
        created_at=str(row["created_at"]),
    )


def _set_meta(conn: sqlite3.Connection, key: str, value: str) -> None:
    conn.execute(
        """
        INSERT OR REPLACE INTO casey_runtime_meta(key, value)
        VALUES (?,?)
        """,
        (key, value),
    )


def _upsert_tree(conn: sqlite3.Connection, tree: TreeState, *, created_at: str) -> None:
    conn.execute(
        """
        INSERT OR REPLACE INTO casey_runtime_trees(tree_id, created_at)
        VALUES (?,?)
        """,
        (tree.tree_id, created_at),
    )
    conn.execute(
        "DELETE FROM casey_runtime_tree_candidates WHERE tree_id = ?",
        (tree.tree_id,),
    )
    for path in sorted(tree.paths):
        state = tree.paths[path]
        for fv_id in state.candidates:
            conn.execute(
                """
                INSERT INTO casey_runtime_tree_candidates(tree_id, path, fv_id)
                VALUES (?,?,?)
                """,
                (tree.tree_id, path, fv_id),
            )


def _upsert_workspace(conn: sqlite3.Connection, workspace: WorkspaceView) -> None:
    conn.execute(
        """
        INSERT OR REPLACE INTO casey_runtime_workspaces(
          ws_id, user, head_tree_id, prefer_author, tie_break
        ) VALUES (?,?,?,?,?)
        """,
        (
            workspace.ws_id,
            workspace.user,
            workspace.head,
            workspace.policy.prefer_author,
            workspace.policy.tie_break,
        ),
    )
    conn.execute(
        "DELETE FROM casey_runtime_workspace_selections WHERE ws_id = ?",
        (workspace.ws_id,),
    )
    for path, fv_id in sorted(workspace.selection.items()):
        conn.execute(
            """
            INSERT INTO casey_runtime_workspace_selections(ws_id, path, fv_id)
            VALUES (?,?,?)
            """,
            (workspace.ws_id, path, fv_id),
        )


def _load_tree(conn: sqlite3.Connection, tree_id: str) -> TreeState:
    row = conn.execute(
        "SELECT tree_id FROM casey_runtime_trees WHERE tree_id = ?",
        (tree_id,),
    ).fetchone()
    if row is None:
        raise ValueError(f"Tree missing: {tree_id}")
    candidates = conn.execute(
        """
        SELECT path, fv_id
        FROM casey_runtime_tree_candidates
        WHERE tree_id = ?
        ORDER BY path, fv_id
        """,
        (tree_id,),
    ).fetchall()
    paths: dict[str, PathState] = {}
    for record in candidates:
        path = str(record["path"])
        paths.setdefault(path, PathState(path=path, candidates=[])).candidates.append(
            str(record["fv_id"])
        )
    return TreeState(tree_id=str(row["tree_id"]), paths=paths)
