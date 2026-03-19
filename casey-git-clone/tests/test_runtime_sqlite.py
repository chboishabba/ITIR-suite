from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from casey_git_clone.models import Blob, BuildView, FileVersion, PathState, TreeState, WorkspaceView  # noqa: E402
from casey_git_clone.runtime_sqlite import (  # noqa: E402
    create_workspace,
    initialize_runtime,
    load_build,
    load_current_tree,
    load_current_tree_id,
    load_file_versions,
    load_tree,
    load_workspace,
    save_build,
    save_workspace,
    set_current_tree_id,
    store_publish_result,
)


def test_runtime_initialize_and_workspace_roundtrip() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "casey_runtime.sqlite"
        initialize_runtime(db_path=db_path, ws_id="alice", user="alice")
        create_workspace(db_path=db_path, ws_id="bob", user="bob")

        current_tree = load_current_tree(db_path=db_path)
        alice = load_workspace(db_path=db_path, ws_id="alice")
        bob = load_workspace(db_path=db_path, ws_id="bob")

    assert current_tree.paths == {}
    assert alice.head == current_tree.tree_id
    assert bob.head == current_tree.tree_id
    assert alice.policy.prefer_author == "alice"
    assert bob.policy.prefer_author == "bob"


def test_runtime_persists_tree_versions_and_builds() -> None:
    blob = Blob.from_bytes(b"hello")
    fv = FileVersion.create(
        blob_id=blob.blob_id,
        author="alice",
        created_at="2026-03-19T00:00:00+00:00",
    )
    tree = TreeState.from_paths(
        {"src/main.c": PathState(path="src/main.c", candidates=[fv.fv_id])}
    )
    build = BuildView(
        build_id="build-1",
        tree_id=tree.tree_id,
        selection={"src/main.c": fv.fv_id},
        created_at="2026-03-19T00:00:02+00:00",
    )

    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "casey_runtime.sqlite"
        initialize_runtime(db_path=db_path, ws_id="alice", user="alice")
        store_publish_result(
            db_path=db_path,
            blobs={blob.blob_id: blob},
            file_versions={fv.fv_id: fv},
            tree_state=tree,
            created_at="2026-03-19T00:00:01+00:00",
        )
        set_current_tree_id(db_path=db_path, tree_id=tree.tree_id)
        alice = WorkspaceView(
            ws_id="alice",
            user="alice",
            head=tree.tree_id,
            selection={"src/main.c": fv.fv_id},
        )
        save_workspace(db_path=db_path, workspace=alice)
        save_build(db_path=db_path, build=build)

        loaded_tree = load_tree(db_path=db_path, tree_id=tree.tree_id)
        loaded_versions = load_file_versions(db_path=db_path, fv_ids=[fv.fv_id])
        loaded_build = load_build(db_path=db_path, build_id="build-1")
        current_tree_id = load_current_tree_id(db_path=db_path)

    assert loaded_tree.paths["src/main.c"].candidates == [fv.fv_id]
    assert loaded_versions[fv.fv_id].blob_id == blob.blob_id
    assert loaded_build.selection["src/main.c"] == fv.fv_id
    assert current_tree_id == tree.tree_id
