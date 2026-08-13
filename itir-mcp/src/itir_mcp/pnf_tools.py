from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

from .contracts import JsonDict, ToolHandler, ToolInputError, ToolSpec


PNF_CONTEXT_INDEX_VERSION = "itir.pnf.context_index.v1"
PNF_TASK_MEMORY_PREVIEW_VERSION = "itir.pnf.task_memory_preview.v1"
PNF_OBSERVER_EVIDENCE_VERSION = "itir.pnf.observer_evidence.v1"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _sensiblaw_root() -> Path:
    return _repo_root() / "SensibLaw"


def _ensure_sensiblaw_on_path() -> None:
    for candidate in (_sensiblaw_root(), _sensiblaw_root() / "src"):
        text = str(candidate)
        if text not in sys.path:
            sys.path.insert(0, text)


def _mapping(payload: Mapping[str, Any], key: str) -> dict[str, Any]:
    value = payload.get(key)
    if not isinstance(value, Mapping):
        raise ToolInputError(f"Expected object field: {key}")
    return dict(value)


def _optional_mapping(payload: Mapping[str, Any], key: str) -> dict[str, Any] | None:
    value = payload.get(key)
    if value is None:
        return None
    if not isinstance(value, Mapping):
        raise ToolInputError(f"Expected object field: {key}")
    return dict(value)


def _sequence(payload: Mapping[str, Any], key: str) -> list[Any]:
    value = payload.get(key)
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        raise ToolInputError(f"Expected array field: {key}")
    return list(value)


def _mapping_sequence(payload: Mapping[str, Any], key: str) -> list[dict[str, Any]]:
    values = _sequence(payload, key)
    if not values:
        raise ToolInputError(f"{key} must not be empty")
    rows: list[dict[str, Any]] = []
    for item in values:
        if not isinstance(item, Mapping):
            raise ToolInputError(f"Expected object entries in {key}")
        rows.append(dict(item))
    return rows


def _optional_mapping_sequence(payload: Mapping[str, Any], key: str) -> list[dict[str, Any]]:
    if key not in payload:
        return []
    values = _sequence(payload, key)
    rows: list[dict[str, Any]] = []
    for item in values:
        if not isinstance(item, Mapping):
            raise ToolInputError(f"Expected object entries in {key}")
        rows.append(dict(item))
    return rows


def _required_str(payload: Mapping[str, Any], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ToolInputError(f"Expected non-empty string field: {key}")
    return value.strip()


def _optional_bool(payload: Mapping[str, Any], key: str) -> bool:
    value = payload.get(key, False)
    if isinstance(value, bool):
        return value
    raise ToolInputError(f"Expected boolean field: {key}")


def pnf_context_index(payload: Mapping[str, Any]) -> JsonDict:
    _ensure_sensiblaw_on_path()
    from src.statibaker_kanban import build_project_context_pnf_index

    project_context = _mapping(payload, "project_context")
    index = build_project_context_pnf_index(project_context)
    return {
        "version": PNF_CONTEXT_INDEX_VERSION,
        "context_index": index,
        "authority_boundary": {
            "read_only": True,
            "non_authoritative": True,
            "canonical_truth_mutated": False,
            "producer_schema_authority": "SensibLaw",
        },
    }


def pnf_task_memory_preview(payload: Mapping[str, Any]) -> JsonDict:
    _ensure_sensiblaw_on_path()
    from src.statibaker_kanban import build_task_memory_index, project_kanban

    documents = _mapping_sequence(payload, "documents")
    grounding_catalog = _mapping(payload, "grounding_catalog")
    ontology_snapshot_id = _required_str(payload, "ontology_snapshot_id")
    project_context = _optional_mapping(payload, "project_context")
    include_kanban_projection = _optional_bool(payload, "include_kanban_projection")

    task_memory = build_task_memory_index(
        documents=documents,
        grounding_catalog=grounding_catalog,
        ontology_snapshot_id=ontology_snapshot_id,
        project_context=project_context,
    )
    result: JsonDict = {
        "version": PNF_TASK_MEMORY_PREVIEW_VERSION,
        "task_memory": task_memory,
        "authority_boundary": {
            "read_only": True,
            "non_authoritative": True,
            "canonical_truth_mutated": False,
            "raw_keyword_tasking": False,
            "kanboard_apply_requires_opt_in": True,
            "producer_schema_authority": "SensibLaw",
        },
    }
    if include_kanban_projection:
        result["kanban_projection"] = project_kanban(task_memory)
    return result


def pnf_observer_evidence(payload: Mapping[str, Any]) -> JsonDict:
    browser_assist_records = _optional_mapping_sequence(payload, "browser_assist_records")
    openrecall_activity_rows = _optional_mapping_sequence(payload, "openrecall_activity_rows")
    if not browser_assist_records and not openrecall_activity_rows:
        raise ToolInputError("Expected browser_assist_records or openrecall_activity_rows")

    records: list[JsonDict] = []
    for index, record in enumerate(browser_assist_records, start=1):
        records.append(_browser_assist_observer_record(record, index))
    offset = len(records)
    for index, row in enumerate(openrecall_activity_rows, start=1):
        records.append(_openrecall_observer_record(row, offset + index))

    return {
        "version": PNF_OBSERVER_EVIDENCE_VERSION,
        "observer_record_count": len(records),
        "observer_records": records,
        "authority_boundary": {
            "read_only": True,
            "non_authoritative": True,
            "canonical_truth_mutated": False,
            "observer_evidence_does_not_create_tasks": True,
            "kanboard_apply_requires_opt_in": True,
        },
    }


def _browser_assist_observer_record(record: Mapping[str, Any], index: int) -> JsonDict:
    return {
        "observer_record_id": _record_id(record, "browser_assist", index),
        "source_system": "browser_assist",
        "source_ref": _text(record.get("session_id")) or f"browser_assist:{index}",
        "ts": record.get("ts") or record.get("started_at"),
        "signal": _text(record.get("signal")) or "browser_assist_activity",
        "task_label": record.get("task_label"),
        "text_preview": record.get("text_preview"),
        "text_hash": record.get("text_hash"),
        "openrecall_entry_refs": _string_list(record.get("openrecall_entry_refs")),
        "playwright_snapshot_refs": _string_list(record.get("playwright_snapshot_refs")),
        "screenshot_refs": _string_list(record.get("screenshot_refs")),
        "transcript_refs": _string_list(record.get("transcript_refs")),
        "pnf_candidates": _pnf_candidates(record.get("pnf_candidates")),
        "task_identity_residual": record.get("task_identity_residual"),
        "lifecycle_residual": record.get("lifecycle_residual"),
        "kanban_projection_policy": _text(record.get("kanban_projection_policy")) or "observer_only",
        "provenance": dict(record.get("provenance")) if isinstance(record.get("provenance"), Mapping) else {},
        "non_authoritative": True,
    }


def _openrecall_observer_record(row: Mapping[str, Any], index: int) -> JsonDict:
    return {
        "observer_record_id": _record_id(row, "openrecall", index),
        "source_system": "openrecall",
        "source_ref": _text(row.get("source_ref")) or f"openrecall:{index}",
        "ts": row.get("ts") or row.get("timestamp"),
        "signal": _text(row.get("signal")) or "openrecall_activity",
        "activity_kind": row.get("activity_kind"),
        "ocr_preview": row.get("ocr_preview"),
        "deep_link": row.get("deep_link"),
        "screenshot_present": bool(row.get("screenshot_present")),
        "capture_count": row.get("capture_count"),
        "pnf_candidates": _pnf_candidates(row.get("pnf_candidates")),
        "task_identity_residual": row.get("task_identity_residual"),
        "lifecycle_residual": row.get("lifecycle_residual"),
        "kanban_projection_policy": _text(row.get("kanban_projection_policy")) or "observer_only",
        "provenance": dict(row.get("provenance")) if isinstance(row.get("provenance"), Mapping) else {},
        "non_authoritative": True,
    }


def _record_id(record: Mapping[str, Any], prefix: str, index: int) -> str:
    for key in ("observer_record_id", "artifact_id", "session_id", "source_ref"):
        value = _text(record.get(key))
        if value:
            return value
    return f"{prefix}:{index}"


def _pnf_candidates(value: Any) -> list[JsonDict]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return []
    return [dict(item) for item in value if isinstance(item, Mapping)]


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return []
    return [str(item) for item in value if str(item).strip()]


def _text(value: Any) -> str:
    return str(value or "").strip()


def get_pnf_tools() -> list[tuple[ToolSpec, ToolHandler]]:
    return [
        (
            ToolSpec(
                name="itir.pnf.context_index",
                title="ITIR PNF context index",
                description="Project supplied project context into the SensibLaw PNF gamma index without mutating producer truth.",
                input_schema={
                    "type": "object",
                    "required": ["project_context"],
                    "properties": {"project_context": {"type": "object"}},
                },
                response_version=PNF_CONTEXT_INDEX_VERSION,
                read_only=True,
            ),
            pnf_context_index,
        ),
        (
            ToolSpec(
                name="itir.pnf.task_memory_preview",
                title="ITIR PNF task memory preview",
                description="Build a read-only SensibLaw/StatiBaker task-memory preview from supplied PNF atoms and groundings.",
                input_schema={
                    "type": "object",
                    "required": ["documents", "grounding_catalog", "ontology_snapshot_id"],
                    "properties": {
                        "documents": {"type": "array", "items": {"type": "object"}},
                        "grounding_catalog": {"type": "object"},
                        "ontology_snapshot_id": {"type": "string"},
                        "project_context": {"type": "object"},
                        "include_kanban_projection": {"type": "boolean"},
                    },
                },
                response_version=PNF_TASK_MEMORY_PREVIEW_VERSION,
                read_only=True,
            ),
            pnf_task_memory_preview,
        ),
        (
            ToolSpec(
                name="itir.pnf.observer_evidence",
                title="ITIR PNF observer evidence",
                description="Normalize OpenRecall and browser-assist observer rows with PNF residuals for later review-only task identity meet.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "browser_assist_records": {"type": "array", "items": {"type": "object"}},
                        "openrecall_activity_rows": {"type": "array", "items": {"type": "object"}},
                    },
                },
                response_version=PNF_OBSERVER_EVIDENCE_VERSION,
                read_only=True,
            ),
            pnf_observer_evidence,
        ),
    ]
