"""Convenience adapters (glue).

Single-call helpers that persist Casey ledgers and emit SB overlay records.

Library-only: does not write to StatiBaker DB.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from .exchange import CaseyOverlayRefs, casey_to_sb_overlay_record
from .ledger_sqlite import BuildLedgerRecord, OperationLedgerRecord, upsert_build, upsert_operation


def emit_casey_observer_artifacts(
    *,
    ledger_db_path: Path,
    operation: OperationLedgerRecord | None,
    build: BuildLedgerRecord | None,
    build_selection_refs: list[Mapping[str, Any]] | None,
    activity_event_id: str,
    annotation_id: str,
    state_date: str,
    provenance: Mapping[str, Any],
    workspace_refs: list[dict[str, Any]],
    operation_refs: list[dict[str, Any]],
    build_refs: list[dict[str, Any]],
) -> dict[str, Any]:
    """Persist ledgers and return SB overlay record (reference-only)."""

    if operation is not None:
        upsert_operation(db_path=ledger_db_path, record=operation)

    if build is not None:
        upsert_build(
            db_path=ledger_db_path,
            record=build,
            selection_refs=build_selection_refs or [],
        )

    refs = CaseyOverlayRefs(
        workspace_refs=workspace_refs,
        operation_refs=operation_refs,
        build_refs=build_refs,
    )

    overlay = casey_to_sb_overlay_record(
        activity_event_id=activity_event_id,
        annotation_id=annotation_id,
        state_date=state_date,
        provenance=provenance,
        refs=refs,
        operation_ledger_id=operation.operation_id if operation is not None else None,
        build_ledger_id=build.build_id if build is not None else None,
    )

    return overlay
