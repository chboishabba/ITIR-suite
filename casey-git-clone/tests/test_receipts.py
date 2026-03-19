from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
SB_ROOT = ROOT.parent / "StatiBaker"
sys.path.insert(0, str(SB_ROOT))

from casey_git_clone.ledger_sqlite import load_build, load_operation  # noqa: E402
from casey_git_clone.models import BuildView, WorkspacePolicy, WorkspaceView  # noqa: E402
from casey_git_clone.receipts import (  # noqa: E402
    build_record,
    emit_runtime_observer_artifacts,
    emit_runtime_receipts,
    operation_record,
    workspace_ref_from_view,
)
from sb.dashboard_store_sqlite import load_itir_overlay_records  # noqa: E402


def test_workspace_ref_from_view_exposes_only_summary_fields() -> None:
    workspace = WorkspaceView(
        ws_id="alice",
        user="alice",
        head="tree-2",
        selection={"src/main.c": "fv-a"},
        policy=WorkspacePolicy(prefer_author="alice", tie_break="stable_hash"),
    )

    ref = workspace_ref_from_view(workspace)

    assert ref["ws_id"] == "alice"
    assert ref["head_tree_id"] == "tree-2"
    assert ref["selected_path_count"] == 1
    assert "selection" not in ref


def test_emit_runtime_receipts_persists_operation_and_build_refs() -> None:
    workspace = WorkspaceView(
        ws_id="alice",
        user="alice",
        head="tree-2",
        selection={"src/main.c": "fv-a"},
        policy=WorkspacePolicy(prefer_author="alice", tie_break="stable_hash"),
    )
    operation = operation_record(
        operation_kind="collapse",
        workspace=workspace,
        path="src/main.c",
        tree_id_before="tree-1",
        tree_id_after="tree-2",
        chosen_fv_id="fv-a",
        resolved_fv_id="fv-a",
        actor="alice",
        created_at="2026-03-19T13:00:00Z",
    )
    build = BuildView(
        build_id="build-1",
        tree_id="tree-2",
        selection={"src/main.c": "fv-a"},
        created_at="2026-03-19T13:00:01Z",
    )

    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "casey_receipts.sqlite"
        overlay = emit_runtime_receipts(
            ledger_db_path=db_path,
            workspace=workspace,
            operation=operation,
            build=build,
            activity_event_id="evt-1",
            annotation_id="obs:casey:evt-1",
            state_date="2026-03-19",
            provenance={"source": "casey-git-clone", "run_id": "unit"},
        )
        stored_operation = load_operation(db_path=db_path, operation_id=operation.operation_id)
        stored_build = load_build(db_path=db_path, build_id="build-1")

    expected_build_record = build_record(build=build, source_operation_id=operation.operation_id)
    assert stored_operation is not None
    assert stored_operation["operation_kind"] == "collapse"
    assert stored_operation["receipt_hash"] == operation.receipt_hash
    assert stored_build is not None
    assert stored_build["selection_digest"] == expected_build_record.selection_digest
    assert stored_build["selection_refs"] == [{"path": "src/main.c", "fv_id": "fv-a"}]
    assert overlay["observer_kind"] == "casey_workspace_v1"
    assert overlay["workspace_refs"][0]["ws_id"] == "alice"
    assert overlay["operation_refs"][0]["operation_ledger_locator"] == f"casey_operation_ledger:{operation.operation_id}"
    assert overlay["build_refs"][0]["build_ledger_locator"] == "casey_build_ledger:build-1"


def test_emit_runtime_observer_artifacts_writes_bundle_and_optionally_ingests_sb() -> None:
    workspace = WorkspaceView(
        ws_id="alice",
        user="alice",
        head="tree-2",
        selection={"src/main.c": "fv-a"},
        policy=WorkspacePolicy(prefer_author="alice", tie_break="stable_hash"),
    )
    operation = operation_record(
        operation_kind="publish",
        workspace=workspace,
        path="src/main.c",
        tree_id_before="tree-1",
        tree_id_after="tree-2",
        chosen_fv_id="fv-prev",
        resolved_fv_id="fv-a",
        actor="alice",
        created_at="2026-03-19T13:10:00Z",
    )

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        ledger_db = tmp_path / "casey_ledgers.sqlite"
        sb_db = tmp_path / "sb.sqlite"
        out_root = tmp_path / "artifacts"
        result = emit_runtime_observer_artifacts(
            ledger_db_path=ledger_db,
            workspace=workspace,
            operation=operation,
            build=None,
            provenance={"source": "casey-git-clone", "run_id": "unit"},
            bundle_out_root=out_root,
            sb_db_path=sb_db,
        )
        overlays = load_itir_overlay_records(db_path=sb_db)
        bundle_dir = Path(result["bundle_dir"])
        bundle_exists = bundle_dir.exists()
        overlay_exists = (bundle_dir / "overlay.json").exists()
        operation_exists = (bundle_dir / "operation.json").exists()
        meta_exists = (bundle_dir / "meta.json").exists()

    assert result["sb_ingested"] is True
    assert bundle_exists is True
    assert overlay_exists is True
    assert operation_exists is True
    assert meta_exists is True
    assert len(overlays) == 1
    assert overlays[0]["annotation_id"] == result["annotation_id"]
