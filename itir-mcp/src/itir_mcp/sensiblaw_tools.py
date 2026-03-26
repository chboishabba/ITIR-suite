from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Mapping

from .contracts import JsonDict, ToolInputError, ToolSpec

PROJECTION_HANDLERS = ("actor", "action", "clause", "timeline")


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
