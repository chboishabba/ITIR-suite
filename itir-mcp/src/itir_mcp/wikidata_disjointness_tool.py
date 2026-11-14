"""Candidate-only Wikidata ontology disjointness report projector."""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Any, Mapping

from .contracts import JsonDict, ToolInputError, ToolSpec

VERSION = "itir.wikidata.disjointness_report.v1"

_AUTHORITY_BOUNDARY: JsonDict = {
    "read_only": True,
    "non_authoritative": True,
    "canonical_truth_mutated": False,
    "candidate_only": True,
    "promotion_authority": False,
}


def _ensure_sensiblaw_on_path() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    sensiblaw_root = repo_root / "SensibLaw"
    for candidate in (sensiblaw_root, sensiblaw_root / "src"):
        text = str(candidate)
        if text not in sys.path:
            sys.path.insert(0, text)


def wikidata_disjointness_report(payload: Mapping[str, Any]) -> JsonDict:
    """Project a Wikidata slice into a candidate-only disjointness report."""
    _ensure_sensiblaw_on_path()
    try:
        from ontology.wikidata_disjointness import (
            load_disjointness_slice,
            project_wikidata_disjointness_payload,
        )
    except ImportError as exc:
        raise ToolInputError(f"Could not import SensibLaw disjointness projector: {exc}") from exc

    slice_data: Mapping[str, Any] | None = None
    source_identifier: str = "inline_mapping"

    if "slice_data" in payload and isinstance(payload["slice_data"], Mapping):
        slice_data = payload["slice_data"]
    elif "slice_path" in payload and isinstance(payload["slice_path"], str):
        path = Path(payload["slice_path"]).expanduser().resolve()
        if not path.is_file():
            raise ToolInputError(f"Slice file not found: {path}")
        slice_data = load_disjointness_slice(path)
        source_identifier = str(path)
    elif "windows" in payload or "statement_bundles" in payload:
        slice_data = payload
    else:
        raise ToolInputError("Expected 'slice_path', 'slice_data', or direct slice mapping with 'windows'")

    report = project_wikidata_disjointness_payload(slice_data)

    disjoint_pairs = report.get("disjoint_pairs") or []
    subclass_violations = report.get("subclass_violations") or []
    culprit_classes = report.get("culprit_classes") or []
    instance_violations = report.get("instance_violations") or []

    return {
        "version": VERSION,
        "authority_boundary": dict(_AUTHORITY_BOUNDARY),
        "source": source_identifier,
        "report": report,
        "summary": {
            "disjoint_pairs_count": len(disjoint_pairs),
            "subclass_violations_count": len(subclass_violations),
            "culprit_classes_count": len(culprit_classes),
            "instance_violations_count": len(instance_violations),
            "window_id": report.get("window_id"),
        },
    }


def get_wikidata_disjointness_tools() -> list[tuple[ToolSpec, Any]]:
    return [
        (
            ToolSpec(
                name="itir.wikidata.disjointness_report",
                title="Wikidata ontology disjointness report",
                description="Project Wikidata subclass and instance ontology slices into candidate-only disjointness violation reports.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "slice_path": {
                            "type": "string",
                            "description": "Path to Wikidata disjointness slice JSON file",
                        },
                        "slice_data": {
                            "type": "object",
                            "description": "In-memory Wikidata disjointness slice mapping with windows/statements",
                        },
                    },
                },
                read_only=True,
            ),
            wikidata_disjointness_report,
        ),
    ]
