"""Governed multi-parent revival MCP contract; candidate projection plus explicit attachment."""
from __future__ import annotations

from typing import Any, Mapping

from .contracts import JsonDict, ToolInputError, ToolSpec


def multi_parent_handoff(payload: Mapping[str, Any]) -> JsonDict:
    from .governed_revival import governed_multi_parent_handoff

    allowed = {"proposals", "archive_db", "max_selected_per_parent", "max_total_selected",
               "max_packet_chars", "child_thread_id", "operation_status"}
    if set(payload) - allowed or "proposals" not in payload:
        raise ToolInputError("explicit proposals and known fields required")
    try:
        return governed_multi_parent_handoff(
            payload["proposals"], archive_db=payload.get("archive_db"),
            max_selected_per_parent=payload.get("max_selected_per_parent", 8),
            max_total_selected=payload.get("max_total_selected", 80),
            max_packet_chars=payload.get("max_packet_chars", 48000),
            child_thread_id=payload.get("child_thread_id"),
            operation_status=payload.get("operation_status", "not_requested"),
        )
    except (ValueError, RuntimeError, FileNotFoundError, TypeError) as exc:
        raise ToolInputError(str(exc)) from exc


def get_multi_parent_revival_tools() -> list[tuple[ToolSpec, Any]]:
    return [
        (
            ToolSpec(
                name="itir.pnf.multi_parent_handoff",
                title="Governed multi-parent candidate handoff",
                description="Build a bounded candidate-only handoff from 2..10 independent canonical archive threads; never merges parent authority or dispatches.",
                input_schema={
                    "type": "object", "required": ["proposals"], "additionalProperties": False,
                    "properties": {
                        "proposals": {"type": "array", "minItems": 2, "maxItems": 10,
                            "items": {"type": "object", "additionalProperties": False,
                                "required": ["canonical_thread_id", "task_atom"],
                                "properties": {
                                    "canonical_thread_id": {"type": "string", "minLength": 1},
                                    "task_atom": {"type": "string", "minLength": 1},
                                    **{key: {"type": "array", "items": {"type": "string"}}
                                       for key in ("formal_gap_receipts", "repo_receipts",
                                                   "pnf_receipts", "evidence_refs")},
                                }}},
                        "archive_db": {"type": "string", "minLength": 1},
                        "max_selected_per_parent": {"type": "integer", "minimum": 2, "maximum": 80},
                        "max_total_selected": {"type": "integer", "minimum": 2, "maximum": 80},
                        "max_packet_chars": {"type": "integer", "minimum": 2000, "maximum": 100000},
                        "child_thread_id": {"type": "string", "minLength": 1},
                        "operation_status": {"type": "string", "minLength": 1},
                    },
                },
                response_version="itir.pnf.multi_parent_handoff.v1", read_only=True,
            ),
            multi_parent_handoff,
        ),
    ]
