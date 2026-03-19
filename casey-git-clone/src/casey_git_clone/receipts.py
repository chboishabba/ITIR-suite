"""Receipt builders for the Casey -> StatiBaker observer seam."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from .adapters import emit_casey_observer_artifacts
from .ledger_sqlite import BuildLedgerRecord, OperationLedgerRecord
from .models import BuildView, WorkspaceView, stable_hash, utc_now_iso


def workspace_ref_from_view(workspace: WorkspaceView) -> dict[str, Any]:
    return {
        "ws_id": workspace.ws_id,
        "head_tree_id": workspace.head,
        "selected_path_count": len(workspace.selection),
        "policy_tie_break": workspace.policy.tie_break,
        "policy_prefer_author": workspace.policy.prefer_author,
    }


def operation_record(
    *,
    operation_kind: str,
    workspace: WorkspaceView | None,
    tree_id_before: str | None,
    tree_id_after: str | None,
    actor: str | None,
    path: str | None = None,
    chosen_fv_id: str | None = None,
    resolved_fv_id: str | None = None,
    created_at: str | None = None,
) -> OperationLedgerRecord:
    created = created_at or utc_now_iso()
    ws_id = workspace.ws_id if workspace is not None else None
    receipt_payload = {
        "operation_kind": operation_kind,
        "ws_id": ws_id,
        "path": path,
        "tree_id_before": tree_id_before,
        "tree_id_after": tree_id_after,
        "chosen_fv_id": chosen_fv_id,
        "resolved_fv_id": resolved_fv_id,
        "actor": actor,
        "created_at": created,
    }
    return OperationLedgerRecord(
        operation_id=stable_hash({"casey_operation_receipt": receipt_payload}),
        operation_kind=operation_kind,
        ws_id=ws_id,
        path=path,
        tree_id_before=tree_id_before,
        tree_id_after=tree_id_after,
        chosen_fv_id=chosen_fv_id,
        resolved_fv_id=resolved_fv_id,
        actor=actor,
        created_at=created,
        receipt_hash=stable_hash(receipt_payload),
    )


def operation_ref_from_record(record: OperationLedgerRecord) -> dict[str, Any]:
    return {
        "operation_id": record.operation_id,
        "operation_kind": record.operation_kind,
        "ws_id": record.ws_id,
        "path": record.path,
        "tree_id_before": record.tree_id_before,
        "tree_id_after": record.tree_id_after,
        "chosen_fv_id": record.chosen_fv_id,
        "resolved_fv_id": record.resolved_fv_id,
        "actor": record.actor,
        "created_at": record.created_at,
        "receipt_hash": record.receipt_hash,
    }


def build_record(
    *,
    build: BuildView,
    source_operation_id: str | None = None,
) -> BuildLedgerRecord:
    return BuildLedgerRecord(
        build_id=build.build_id,
        tree_id=build.tree_id,
        selection_digest=stable_hash(
            [{"path": path, "fv_id": fv_id} for path, fv_id in sorted(build.selection.items())]
        ),
        created_at=build.created_at,
        source_operation_id=source_operation_id,
    )


def build_selection_refs_from_build(build: BuildView) -> list[dict[str, str]]:
    return [{"path": path, "fv_id": fv_id} for path, fv_id in sorted(build.selection.items())]


def build_ref_from_record(record: BuildLedgerRecord) -> dict[str, Any]:
    return {
        "build_id": record.build_id,
        "tree_id": record.tree_id,
        "selection_digest": record.selection_digest,
        "created_at": record.created_at,
    }


def emit_runtime_receipts(
    *,
    ledger_db_path: Path,
    workspace: WorkspaceView | None,
    operation: OperationLedgerRecord | None,
    build: BuildView | None,
    activity_event_id: str,
    annotation_id: str,
    state_date: str,
    provenance: Mapping[str, Any],
) -> dict[str, Any]:
    build_ledger_record = None
    build_selection_refs = None
    build_refs: list[dict[str, Any]] = []
    if build is not None:
        build_ledger_record = build_record(
            build=build,
            source_operation_id=operation.operation_id if operation is not None else None,
        )
        build_selection_refs = build_selection_refs_from_build(build)
        build_refs.append(build_ref_from_record(build_ledger_record))

    return emit_casey_observer_artifacts(
        ledger_db_path=ledger_db_path,
        operation=operation,
        build=build_ledger_record,
        build_selection_refs=build_selection_refs,
        activity_event_id=activity_event_id,
        annotation_id=annotation_id,
        state_date=state_date,
        provenance=provenance,
        workspace_refs=[workspace_ref_from_view(workspace)] if workspace is not None else [],
        operation_refs=[operation_ref_from_record(operation)] if operation is not None else [],
        build_refs=build_refs,
    )
