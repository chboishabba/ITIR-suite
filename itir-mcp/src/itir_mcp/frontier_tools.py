"""Read-only AO frontier proposal MCP surface; optional separate roster receipt writes."""
from __future__ import annotations

from typing import Any, Mapping

from .contracts import ToolInputError, ToolSpec
from .frontier_evidence import build_frontier


def frontier_evidence_tool(payload: Mapping[str, Any]) -> dict[str, Any]:
    allowed = {"archive_db", "evidence", "roster_db", "max_evaluated", "max_proposals"}
    if set(payload) - allowed:
        raise ToolInputError("unknown frontier evidence argument")
    evidence = payload.get("evidence", [])
    if not isinstance(evidence, list) or any(not isinstance(row, dict) for row in evidence):
        raise ToolInputError("evidence must be an array of objects")
    return build_frontier(
        archive_db=payload.get("archive_db"), evidence=evidence,
        roster_db=payload.get("roster_db"),
        max_evaluated=payload.get("max_evaluated", 24),
        max_proposals=payload.get("max_proposals", 4),
    )


def get_frontier_tools() -> list[tuple[ToolSpec, Any]]:
    return [(
        ToolSpec(
            name="itir.ao.frontier_evidence",
            title="AO canonical frontier evidence",
            description="Metadata-only canonical frontier with explicit receipts; never dispatches.",
            input_schema={
                "type": "object", "additionalProperties": False,
                "properties": {
                    "archive_db": {"type": "string"},
                    "roster_db": {"type": "string"},
                    "max_evaluated": {"type": "integer", "minimum": 1, "maximum": 64},
                    "max_proposals": {"type": "integer", "minimum": 1, "maximum": 4},
                    "evidence": {"type": "array", "maxItems": 64, "items": {"type": "object"}},
                },
            },
        ),
        frontier_evidence_tool,
    )]
