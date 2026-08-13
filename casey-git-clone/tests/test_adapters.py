from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from casey_git_clone.adapters import emit_casey_observer_artifacts  # noqa: E402
from casey_git_clone.ledger_sqlite import BuildLedgerRecord, OperationLedgerRecord  # noqa: E402


def test_emit_casey_observer_artifacts_smoke() -> None:
    op = OperationLedgerRecord(
        operation_id="op-1",
        operation_kind="collapse",
        ws_id="ws-1",
        path="src/main.c",
        tree_id_before="tree-1",
        tree_id_after="tree-2",
        chosen_fv_id="fv-a",
        resolved_fv_id="fv-b",
        actor="alice",
        created_at="2026-03-09T00:00:00Z",
        receipt_hash="a" * 64,
    )
    build = BuildLedgerRecord(
        build_id="build-1",
        tree_id="tree-2",
        selection_digest="b" * 64,
        created_at="2026-03-09T00:00:01Z",
        source_operation_id="op-1",
    )

    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "casey.sqlite"
        overlay = emit_casey_observer_artifacts(
            ledger_db_path=db_path,
            operation=op,
            build=build,
            build_selection_refs=[{"path": "src/main.c", "fv_id": "fv-b"}],
            activity_event_id="evt-1",
            annotation_id="obs:casey:evt-1",
            state_date="2026-03-09",
            provenance={"source": "casey-git-clone", "run_id": "unit"},
            workspace_refs=[{"ws_id": "ws-1"}],
            operation_refs=[{"operation_kind": "collapse", "receipt_hash": "a" * 64}],
            build_refs=[{"build_id": "build-1", "tree_id": "tree-2", "selection_digest": "b" * 64}],
        )

        assert overlay["observer_kind"] == "casey_workspace_v1"
        assert overlay["operation_refs"][0]["operation_ledger_locator"] == "casey_operation_ledger:op-1"
        assert overlay["build_refs"][0]["build_ledger_locator"] == "casey_build_ledger:build-1"
