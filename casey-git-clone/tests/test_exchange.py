from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from casey_git_clone.exchange import CaseyOverlayRefs, casey_to_sb_overlay_record  # noqa: E402


def test_casey_overlay_record_is_reference_only() -> None:
    refs = CaseyOverlayRefs(
        workspace_refs=[{"ws_id": "ws-1", "head_tree_id": "tree-1", "selected_path_count": 1}],
        operation_refs=[{"operation_kind": "sync", "receipt_hash": "a" * 64}],
        build_refs=[{"build_id": "build-1", "tree_id": "tree-1", "selection_digest": "b" * 64}],
    )

    overlay = casey_to_sb_overlay_record(
        activity_event_id="evt-1",
        annotation_id="obs:casey:evt-1",
        state_date="2026-03-09",
        provenance={"source": "casey-git-clone"},
        refs=refs,
        operation_ledger_id="op-1",
        build_ledger_id="build-1",
    )

    assert overlay["observer_kind"] == "casey_workspace_v1"
    assert "candidate_graph" not in overlay
    assert "workspace" not in overlay
    assert overlay["workspace_refs"][0]["ws_id"] == "ws-1"
    assert overlay["operation_refs"][0]["operation_ledger_locator"] == "casey_operation_ledger:op-1"
    assert overlay["build_refs"][0]["build_ledger_locator"] == "casey_build_ledger:build-1"
