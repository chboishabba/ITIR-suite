from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Mapping

from .contracts import JsonDict, ToolInputError, ToolSpec

PROJECTION_HANDLERS = ("actor", "action", "clause", "timeline")
JOB_STATES = {"queued", "running", "partial", "completed", "failed", "cancelled"}
WORK_UNITS = {"words", "sentences", "pages", "atoms", "units"}


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _sensiblaw_root() -> Path:
    return _repo_root() / "SensibLaw"


def _ensure_sensiblaw_on_path() -> None:
    for candidate in (_sensiblaw_root(), _sensiblaw_root() / "src"):
        text = str(candidate)
        if text not in sys.path:
            sys.path.insert(0, text)


def _require_str(payload: Mapping[str, Any], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ToolInputError(f"Expected non-empty string field: {key}")
    return value


def _optional_bool(payload: Mapping[str, Any], key: str) -> bool | None:
    value = payload.get(key)
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    raise ToolInputError(f"Expected boolean field: {key}")


def _optional_mapping(payload: Mapping[str, Any], key: str) -> Mapping[str, Any] | None:
    value = payload.get(key)
    if value is None:
        return None
    if isinstance(value, Mapping):
        return value
    raise ToolInputError(f"Expected object field: {key}")


def _optional_str(payload: Mapping[str, Any], key: str) -> str | None:
    value = payload.get(key)
    if value is None:
        return None
    if isinstance(value, str):
        stripped = value.strip()
        return stripped or None
    raise ToolInputError(f"Expected string field: {key}")


def _coerce_float(value: object) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    return None


def _coerce_int(value: object) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return None


def _coerce_text(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    stripped = value.strip()
    return stripped or None


def _load_run_state(payload: Mapping[str, Any]) -> tuple[dict[str, Any], str | None]:
    state_path = _optional_str(payload, "state_path")
    run_state = _optional_mapping(payload, "run_state")
    if state_path is not None and run_state is not None:
        raise ToolInputError("Provide either state_path or run_state, not both")
    if state_path is None and run_state is None:
        raise ToolInputError("Expected one of: state_path or run_state")
    if state_path is not None:
        state_file = Path(state_path)
        if not state_file.exists():
            raise ToolInputError(f"State path does not exist: {state_path}")
        loaded = json.loads(state_file.read_text(encoding="utf-8"))
        if not isinstance(loaded, dict):
            raise ToolInputError("State path JSON must be an object")
        return loaded, str(state_file)
    return dict(run_state or {}), _optional_str(payload, "last_partial_ref")


def _normalize_job_state(
    raw_status: str,
    *,
    has_resume_refs: bool,
    has_last_event: bool,
) -> str:
    normalized = raw_status.strip().lower()
    if normalized in JOB_STATES:
        return normalized
    if normalized == "starting":
        return "queued"
    if normalized in {"preflighting", "running"}:
        return "running"
    if normalized == "complete":
        return "completed"
    if normalized == "interrupted":
        if has_resume_refs or has_last_event:
            return "partial"
        return "cancelled"
    if normalized in {"cancelled", "canceled"}:
        return "cancelled"
    return "failed"


def _derive_work_progress(details: Mapping[str, Any]) -> tuple[str, int, int | None]:
    work_unit = _coerce_text(details.get("work_unit"))
    work_completed = _coerce_int(details.get("work_completed"))
    work_total = _coerce_int(details.get("work_total"))
    if work_unit in WORK_UNITS and work_completed is not None:
        return work_unit, work_completed, work_total

    overall_words_seen = _coerce_int(details.get("overall_words_seen"))
    overall_total_words = _coerce_int(details.get("overall_total_words"))
    if overall_words_seen is not None:
        return "words", overall_words_seen, overall_total_words

    words_done = _coerce_int(details.get("words_done"))
    total_words = _coerce_int(details.get("total_words"))
    if words_done is not None:
        return "words", words_done, total_words

    sentences_done = _coerce_int(details.get("sentences_done"))
    total_sentences = _coerce_int(details.get("total_sentences"))
    if sentences_done is not None:
        return "sentences", sentences_done, total_sentences

    pages_seen = _coerce_int(details.get("pages_seen"))
    total_pages = _coerce_int(details.get("total_pages"))
    if pages_seen is not None:
        return "pages", pages_seen, total_pages

    page = _coerce_int(details.get("page"))
    pdf_page_total = _coerce_int(details.get("pdf_page_total"))
    if page is not None:
        return "pages", page, pdf_page_total or total_pages

    completed = _coerce_int(details.get("completed"))
    total = _coerce_int(details.get("total"))
    if completed is not None:
        return "units", completed, total

    return "units", 0, None


def itir_job_status(payload: Mapping[str, Any]) -> JsonDict:
    run_state, inferred_partial_ref = _load_run_state(payload)
    job_id = _require_str(payload, "job_id")
    raw_status = _coerce_text(run_state.get("status")) or "failed"
    last_event = run_state.get("last_event")
    details = {}
    if isinstance(last_event, Mapping):
        last_details = last_event.get("details")
        if isinstance(last_details, Mapping):
            details = dict(last_details)

    checkpoint_ref = _optional_str(payload, "checkpoint_ref") or _coerce_text(run_state.get("checkpoint_ref")) or _coerce_text(details.get("checkpoint_ref"))
    last_partial_ref = inferred_partial_ref or _coerce_text(run_state.get("partial_path")) or _coerce_text(run_state.get("last_partial_ref")) or _coerce_text(details.get("last_partial_ref"))
    state = _normalize_job_state(
        raw_status,
        has_resume_refs=checkpoint_ref is not None or last_partial_ref is not None,
        has_last_event=isinstance(last_event, Mapping),
    )
    elapsed_seconds = (
        _coerce_float(details.get("overall_elapsed_seconds"))
        or _coerce_float(details.get("feed_elapsed_seconds"))
        or _coerce_float(details.get("elapsed_seconds"))
        or 0.0
    )
    eta_seconds = _coerce_float(details.get("overall_eta_seconds"))
    if eta_seconds is None:
        eta_seconds = _coerce_float(details.get("eta_seconds"))
    work_unit, work_completed, work_total = _derive_work_progress(details)
    predicate_atom_count = _coerce_int(details.get("predicate_atom_count")) or 0
    signal_atom_count = _coerce_int(details.get("signal_atom_count")) or 0
    provenance_ref_count = _coerce_int(details.get("provenance_ref_count")) or 0
    can_resume = state in {"queued", "running", "partial", "failed", "cancelled"} and (
        checkpoint_ref is not None or last_partial_ref is not None
    )
    return {
        "version": "itir.job_status.v1",
        "job_id": job_id,
        "state": state,
        "elapsed_seconds": elapsed_seconds,
        "eta_seconds": eta_seconds,
        "work_unit": work_unit,
        "work_completed": work_completed,
        "work_total": work_total,
        "predicate_atom_count": predicate_atom_count,
        "signal_atom_count": signal_atom_count,
        "provenance_ref_count": provenance_ref_count,
        "checkpoint_ref": checkpoint_ref,
        "last_partial_ref": last_partial_ref,
        "can_resume": can_resume,
    }


def _extract_obligations(
    text: str,
    *,
    source_id: str,
    enable_actor_binding: bool | None,
    enable_action_binding: bool | None,
):
    _ensure_sensiblaw_on_path()
    from src.obligations import extract_obligations_from_text

    return extract_obligations_from_text(
        text,
        source_id=source_id,
        enable_actor_binding=enable_actor_binding,
        enable_action_binding=enable_action_binding,
    )


def obligations_query(payload: Mapping[str, Any]) -> JsonDict:
    _ensure_sensiblaw_on_path()
    from src.obligation_views import obligations_to_query_payload, query_obligations

    text = _require_str(payload, "text")
    source_id = str(payload.get("source_id") or "document")
    filters = _optional_mapping(payload, "filters") or {}
    obligations = _extract_obligations(
        text,
        source_id=source_id,
        enable_actor_binding=_optional_bool(payload, "enable_actor_binding"),
        enable_action_binding=_optional_bool(payload, "enable_action_binding"),
    )
    filtered = query_obligations(
        obligations,
        actor=filters.get("actor"),
        action=filters.get("action"),
        obj=filters.get("object"),
        scope_category=filters.get("scope_category"),
        scope_text=filters.get("scope_text"),
        lifecycle_kind=filters.get("lifecycle_kind"),
        clause_id=filters.get("clause_id"),
        modality=filters.get("modality"),
        reference_id=filters.get("reference_id"),
    )
    return obligations_to_query_payload(filtered)


def obligations_explain(payload: Mapping[str, Any]) -> JsonDict:
    _ensure_sensiblaw_on_path()
    from src.obligation_views import build_explanations, explanations_to_payload

    text = _require_str(payload, "text")
    source_id = str(payload.get("source_id") or "document")
    obligations = _extract_obligations(
        text,
        source_id=source_id,
        enable_actor_binding=_optional_bool(payload, "enable_actor_binding"),
        enable_action_binding=_optional_bool(payload, "enable_action_binding"),
    )
    return explanations_to_payload(build_explanations(text, obligations, source_id=source_id))


def obligations_alignment(payload: Mapping[str, Any]) -> JsonDict:
    _ensure_sensiblaw_on_path()
    from src.obligation_alignment import ALIGNMENT_SCHEMA_VERSION, align_obligations, alignment_to_payload

    old_text = _require_str(payload, "old_text")
    new_text = _require_str(payload, "new_text")
    source_id = str(payload.get("source_id") or "document")
    old_obligations = _extract_obligations(
        old_text,
        source_id=source_id,
        enable_actor_binding=_optional_bool(payload, "enable_actor_binding"),
        enable_action_binding=_optional_bool(payload, "enable_action_binding"),
    )
    new_obligations = _extract_obligations(
        new_text,
        source_id=source_id,
        enable_actor_binding=_optional_bool(payload, "enable_actor_binding"),
        enable_action_binding=_optional_bool(payload, "enable_action_binding"),
    )
    out = alignment_to_payload(align_obligations(old_obligations, new_obligations))
    out["version"] = ALIGNMENT_SCHEMA_VERSION
    return out


def obligations_projection(payload: Mapping[str, Any]) -> JsonDict:
    _ensure_sensiblaw_on_path()
    from src.obligation_projections import (
        PROJECTION_SCHEMA_VERSION,
        action_view,
        actor_view,
        clause_view,
        timeline_view,
    )

    view = _require_str(payload, "view")
    handlers = {
        "actor": actor_view,
        "action": action_view,
        "clause": clause_view,
        "timeline": timeline_view,
    }
    try:
        handler = handlers[view]
    except KeyError as exc:
        raise ToolInputError(f"Unknown projection view: {view}") from exc

    obligations = _extract_obligations(
        _require_str(payload, "text"),
        source_id=str(payload.get("source_id") or "document"),
        enable_actor_binding=_optional_bool(payload, "enable_actor_binding"),
        enable_action_binding=_optional_bool(payload, "enable_action_binding"),
    )
    return {"version": PROJECTION_SCHEMA_VERSION, "view": view, "results": handler(obligations)}


def obligations_activate(payload: Mapping[str, Any]) -> JsonDict:
    _ensure_sensiblaw_on_path()
    from src.activation import ACTIVATION_VERSION, FACT_ENVELOPE_VERSION, Fact, FactEnvelope, activation_to_payload, simulate_activation
    from src.obligation_views import obligations_to_query_payload

    text = _require_str(payload, "text")
    facts_payload = _optional_mapping(payload, "facts")
    if facts_payload is None:
        raise ToolInputError("Expected object field: facts")

    version = str(facts_payload.get("version") or FACT_ENVELOPE_VERSION)
    if version != FACT_ENVELOPE_VERSION:
        raise ToolInputError(f"Unsupported fact envelope version: {version}")

    raw_facts = facts_payload.get("facts")
    if not isinstance(raw_facts, list):
        raise ToolInputError("Expected list field: facts.facts")

    facts = []
    for item in raw_facts:
        if not isinstance(item, Mapping):
            raise ToolInputError("Each facts entry must be an object")
        facts.append(
            Fact(
                key=_require_str(item, "key"),
                value=item.get("value"),
                at=item.get("at"),
                source=item.get("source"),
            )
        )

    obligations = _extract_obligations(
        text,
        source_id=str(payload.get("source_id") or "document"),
        enable_actor_binding=_optional_bool(payload, "enable_actor_binding"),
        enable_action_binding=_optional_bool(payload, "enable_action_binding"),
    )
    envelope = FactEnvelope(version=version, issued_at=facts_payload.get("issued_at"), facts=facts)
    activation = activation_to_payload(simulate_activation(obligations, envelope))
    return {
        "version": ACTIVATION_VERSION,
        "obligations": obligations_to_query_payload(obligations)["results"],
        "activation": activation,
    }


def get_sensiblaw_tools():
    return [
        (
            ToolSpec(
                name="sensiblaw.itir_job_status",
                title="SensibLaw ITIR job status",
                description="Project existing ITIR progress/checkpoint state into a stable execution-status payload.",
                input_schema={
                    "type": "object",
                    "required": ["job_id"],
                    "properties": {
                        "job_id": {"type": "string"},
                        "state_path": {"type": "string"},
                        "run_state": {"type": "object"},
                        "checkpoint_ref": {"type": "string"},
                        "last_partial_ref": {"type": "string"},
                    },
                    "oneOf": [
                        {"required": ["job_id", "state_path"]},
                        {"required": ["job_id", "run_state"]},
                    ],
                },
                response_version="itir.job_status.v1",
            ),
            itir_job_status,
        ),
        (
            ToolSpec(
                name="sensiblaw.obligations_query",
                title="SensibLaw obligations query",
                description="Filter extracted obligations using deterministic read-only criteria.",
                input_schema={
                    "type": "object",
                    "required": ["text"],
                    "properties": {
                        "text": {"type": "string"},
                        "source_id": {"type": "string"},
                        "enable_actor_binding": {"type": "boolean"},
                        "enable_action_binding": {"type": "boolean"},
                        "filters": {"type": "object"},
                    },
                },
            ),
            obligations_query,
        ),
        (
            ToolSpec(
                name="sensiblaw.obligations_explain",
                title="SensibLaw obligations explain",
                description="Return clause-local explanations for extracted obligations.",
                input_schema={
                    "type": "object",
                    "required": ["text"],
                    "properties": {
                        "text": {"type": "string"},
                        "source_id": {"type": "string"},
                        "enable_actor_binding": {"type": "boolean"},
                        "enable_action_binding": {"type": "boolean"},
                    },
                },
            ),
            obligations_explain,
        ),
        (
            ToolSpec(
                name="sensiblaw.obligations_alignment",
                title="SensibLaw obligations alignment",
                description="Compute metadata-only alignment between old and new texts.",
                input_schema={
                    "type": "object",
                    "required": ["old_text", "new_text"],
                    "properties": {
                        "old_text": {"type": "string"},
                        "new_text": {"type": "string"},
                        "source_id": {"type": "string"},
                        "enable_actor_binding": {"type": "boolean"},
                        "enable_action_binding": {"type": "boolean"},
                    },
                },
            ),
            obligations_alignment,
        ),
        (
            ToolSpec(
                name="sensiblaw.obligations_projection",
                title="SensibLaw obligations projection",
                description="Return one deterministic projection view over extracted obligations.",
                input_schema={
                    "type": "object",
                    "required": ["text", "view"],
                    "properties": {
                        "text": {"type": "string"},
                        "view": {"type": "string", "enum": list(PROJECTION_HANDLERS)},
                        "source_id": {"type": "string"},
                        "enable_actor_binding": {"type": "boolean"},
                        "enable_action_binding": {"type": "boolean"},
                    },
                },
            ),
            obligations_projection,
        ),
        (
            ToolSpec(
                name="sensiblaw.obligations_activate",
                title="SensibLaw obligations activate",
                description="Simulate obligation activation using a declared fact envelope.",
                input_schema={
                    "type": "object",
                    "required": ["text", "facts"],
                    "properties": {
                        "text": {"type": "string"},
                        "source_id": {"type": "string"},
                        "enable_actor_binding": {"type": "boolean"},
                        "enable_action_binding": {"type": "boolean"},
                        "facts": {"type": "object"},
                    },
                },
            ),
            obligations_activate,
        ),
    ]
