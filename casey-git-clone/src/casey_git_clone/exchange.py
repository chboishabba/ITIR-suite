"""Exchange-channel helpers for casey-git-clone.

v0.1: in-process structures only.

This adapter turns Casey operation/build artifacts into reference-heavy overlay
records suitable for StatiBaker ingestion, without transferring mutable workspace
or candidate-graph authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class CaseyOverlayRefs:
    workspace_refs: list[dict[str, Any]]
    operation_refs: list[dict[str, Any]]
    build_refs: list[dict[str, Any]]


def operation_ledger_locator(operation_id: str) -> str:
    return f"casey_operation_ledger:{operation_id}"


def build_ledger_locator(build_id: str) -> str:
    return f"casey_build_ledger:{build_id}"


def casey_to_sb_overlay_record(
    *,
    activity_event_id: str,
    annotation_id: str,
    state_date: str,
    provenance: Mapping[str, Any],
    refs: CaseyOverlayRefs,
    status: str | None = None,
    confidence: str | None = None,
    operation_ledger_id: str | None = None,
    build_ledger_id: str | None = None,
) -> dict[str, Any]:
    return {
        "activity_event_id": str(activity_event_id),
        "annotation_id": str(annotation_id),
        "provenance": dict(provenance),
        "state_date": str(state_date),
        "observer_kind": "casey_workspace_v1",
        "status": status,
        "confidence": confidence,
        "workspace_refs": list(refs.workspace_refs),
        "operation_refs": list(refs.operation_refs),
        "build_refs": list(refs.build_refs),
    }
