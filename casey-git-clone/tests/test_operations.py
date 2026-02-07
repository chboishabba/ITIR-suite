from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from casey_git_clone.models import (  # noqa: E402
    FileVersion,
    PathState,
    TreeState,
    WorkspacePolicy,
    WorkspaceView,
)
from casey_git_clone.operations import (  # noqa: E402
    build_snapshot,
    collapse_conflict,
    publish_edits,
    sync_workspace,
)


def _tree_single(path: str, fv_id: str) -> TreeState:
    return TreeState.from_paths({path: PathState(path=path, candidates=[fv_id])})


def test_publish_replaces_singleton_when_no_divergence() -> None:
    tree = _tree_single("src/main.c", "fv-base")
    ws = WorkspaceView(
        ws_id="ws-1",
        user="alice",
        head=tree.tree_id,
        selection={"src/main.c": "fv-base"},
    )

    result = publish_edits(
        tree_state=tree,
        workspace=ws,
        edits={"src/main.c": "new-content"},
        author="alice",
        created_at="2026-02-07T00:00:00+00:00",
    )
    candidates = result.tree_state.paths["src/main.c"].candidates
    assert candidates != ["fv-base"]
    assert len(candidates) == 1


def test_publish_appends_when_conflict_already_exists() -> None:
    tree = TreeState.from_paths(
        {
            "src/main.c": PathState(path="src/main.c", candidates=["fv-a", "fv-b"]),
        }
    )
    ws = WorkspaceView(
        ws_id="ws-1",
        user="alice",
        head=tree.tree_id,
        selection={"src/main.c": "fv-a"},
    )
    result = publish_edits(
        tree_state=tree,
        workspace=ws,
        edits={"src/main.c": "alice-version"},
        author="alice",
        created_at="2026-02-07T00:00:01+00:00",
    )
    assert len(result.tree_state.paths["src/main.c"].candidates) == 3


def test_sync_preserves_selection_when_candidate_still_exists() -> None:
    tree = TreeState.from_paths(
        {
            "src/main.c": PathState(path="src/main.c", candidates=["fv-a", "fv-b"]),
        }
    )
    ws = WorkspaceView(
        ws_id="ws-1",
        user="alice",
        head="old-tree",
        selection={"src/main.c": "fv-b"},
    )
    synced = sync_workspace(workspace=ws, tree_state=tree, file_versions={})
    assert synced.selection["src/main.c"] == "fv-b"
    assert synced.head == tree.tree_id


def test_sync_reselects_when_selection_missing() -> None:
    tree = TreeState.from_paths(
        {
            "src/main.c": PathState(path="src/main.c", candidates=["fv-a", "fv-b"]),
        }
    )
    versions = {
        "fv-a": FileVersion(
            fv_id="fv-a",
            blob_id="blob-a",
            author="alice",
            created_at="2026-02-07T00:00:00+00:00",
        ),
        "fv-b": FileVersion(
            fv_id="fv-b",
            blob_id="blob-b",
            author="bob",
            created_at="2026-02-07T00:00:01+00:00",
        ),
    }
    ws = WorkspaceView(
        ws_id="ws-1",
        user="alice",
        head="old-tree",
        selection={"src/main.c": "fv-missing"},
        policy=WorkspacePolicy(prefer_author="alice", tie_break="newest"),
    )
    synced = sync_workspace(workspace=ws, tree_state=tree, file_versions=versions)
    assert synced.selection["src/main.c"] == "fv-a"


def test_collapse_conflict_to_existing_candidate() -> None:
    tree = TreeState.from_paths(
        {
            "src/main.c": PathState(path="src/main.c", candidates=["fv-a", "fv-b"]),
        }
    )
    collapsed = collapse_conflict(
        tree_state=tree,
        path="src/main.c",
        author="alice",
        file_versions={},
        chosen_fv_id="fv-b",
    )
    assert collapsed.tree_state.paths["src/main.c"].candidates == ["fv-b"]


def test_build_snapshot_freezes_complete_selection() -> None:
    tree = TreeState.from_paths(
        {
            "src/main.c": PathState(path="src/main.c", candidates=["fv-a", "fv-b"]),
            "README.md": PathState(path="README.md", candidates=["fv-readme"]),
        }
    )
    ws = WorkspaceView(
        ws_id="ws-1",
        user="alice",
        head="old-tree",
        selection={"src/main.c": "fv-a"},
    )
    snap = build_snapshot(workspace=ws, tree_state=tree, file_versions={})
    assert set(snap.selection) == {"src/main.c", "README.md"}
    assert snap.selection["src/main.c"] == "fv-a"
    assert snap.selection["README.md"] == "fv-readme"

