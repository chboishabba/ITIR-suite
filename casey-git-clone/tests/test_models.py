from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from casey_git_clone.models import (  # noqa: E402
    Blob,
    BuildView,
    PathState,
    TreeState,
    WorkspacePolicy,
    WorkspaceView,
    stable_hash,
)


def test_path_state_requires_candidates() -> None:
    state = PathState(path="src/main.c", candidates=[])
    with pytest.raises(ValueError):
        state.validate()


def test_tree_id_is_stable_for_equivalent_candidate_sets() -> None:
    left = TreeState.from_paths(
        {
            "src/main.c": PathState(path="src/main.c", candidates=["fv-b", "fv-a"]),
        }
    )
    right = TreeState.from_paths(
        {
            "src/main.c": PathState(path="src/main.c", candidates=["fv-a", "fv-b"]),
        }
    )
    assert left.tree_id == right.tree_id


def test_workspace_selection_must_exist_in_candidates() -> None:
    states = {
        "src/main.c": PathState(path="src/main.c", candidates=["fv-a"]),
    }
    view = WorkspaceView(
        ws_id="ws-1",
        user="alice",
        head="tree-1",
        selection={"src/main.c": "fv-missing"},
    )
    with pytest.raises(ValueError):
        view.validate_against(states)


def test_workspace_policy_rejects_unknown_tiebreak() -> None:
    policy = WorkspacePolicy(tie_break="random")
    with pytest.raises(ValueError):
        policy.validate()


def test_blob_and_hash_are_deterministic() -> None:
    blob_a = Blob.from_bytes(b"hello")
    blob_b = Blob.from_bytes(b"hello")
    assert blob_a.blob_id == blob_b.blob_id
    assert len(blob_a.blob_id) == 64
    assert stable_hash({"k": 1, "v": "x"}) == stable_hash({"v": "x", "k": 1})


def test_build_view_selection_is_immutable() -> None:
    view = BuildView(
        build_id="build-1",
        tree_id="tree-1",
        selection={"src/main.c": "fv-a"},
        created_at="2026-02-07T00:00:00+00:00",
    )
    with pytest.raises(TypeError):
        view.selection["src/main.c"] = "fv-b"  # type: ignore[index]
