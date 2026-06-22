from __future__ import annotations

from typing import Any, Mapping, Sequence

from .contracts import JsonDict, ToolHandler, ToolInputError, ToolSpec
from .shard_transport import (
    build_partial_graph_view,
    route_selector as _route_selector,
    validate_shared_shard_artifact,
)
from .tool_authority_profiles import DEFAULT_TOOL_AUTHORITY_PROFILES, validate_tool_authority_profile


GOVERNANCE_TOOL_PROFILES_VERSION = "itir.governance.tool_profiles.v1"
GOVERNANCE_VALIDATE_TOOL_PROFILE_VERSION = "itir.governance.validate_tool_profile.v1"
SHARD_VALIDATE_ARTIFACT_VERSION = "itir.shard.validate_artifact.v1"
SHARD_ROUTE_SELECTOR_VERSION = "itir.shard.route_selector.v1"
SHARD_PARTIAL_GRAPH_VIEW_VERSION = "itir.shard.partial_graph_view.v1"

_AUTHORITY_BOUNDARY: JsonDict = {
    "read_only": True,
    "non_authoritative": True,
    "canonical_truth_mutated": False,
}


def get_governance_tools() -> list[tuple[ToolSpec, ToolHandler]]:
    return [
        (
            ToolSpec(
                name="itir.governance.tool_profiles",
                title="ITIR governance tool profiles",
                description="List default tool authority profiles without mutating any authoritative state.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "tool_id": {"type": "string"},
                    },
                    "required": [],
                    "additionalProperties": True,
                },
                response_version=GOVERNANCE_TOOL_PROFILES_VERSION,
                read_only=True,
            ),
            governance_tool_profiles,
        ),
        (
            ToolSpec(
                name="itir.governance.validate_tool_profile",
                title="ITIR governance validate tool profile",
                description="Validate a single tool authority profile against the local authority contract.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "profile": {"type": "object"},
                    },
                    "required": ["profile"],
                    "additionalProperties": True,
                },
                response_version=GOVERNANCE_VALIDATE_TOOL_PROFILE_VERSION,
                read_only=True,
            ),
            validate_tool_profile_tool,
        ),
        (
            ToolSpec(
                name="itir.shard.validate_artifact",
                title="ITIR shard validate artifact",
                description="Validate a shared shard artifact payload and report logical shard identity only.",
                input_schema={
                    "type": "object",
                    "additionalProperties": True,
                },
                response_version=SHARD_VALIDATE_ARTIFACT_VERSION,
                read_only=True,
            ),
            validate_artifact_tool,
        ),
        (
            ToolSpec(
                name="itir.shard.route_selector",
                title="ITIR shard route selector",
                description="Resolve a selector to logical shard ids without exposing transport locations.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "selector": {"type": "string"},
                    },
                    "required": ["selector"],
                    "additionalProperties": True,
                },
                response_version=SHARD_ROUTE_SELECTOR_VERSION,
                read_only=True,
            ),
            route_selector_tool,
        ),
        (
            ToolSpec(
                name="itir.shard.partial_graph_view",
                title="ITIR shard partial graph view",
                description="Build a non-authoritative partial graph view for selectors using logical shard ids only.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "selectors": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["selectors"],
                    "additionalProperties": True,
                },
                response_version=SHARD_PARTIAL_GRAPH_VIEW_VERSION,
                read_only=True,
            ),
            partial_graph_view_tool,
        ),
    ]


def governance_tool_profiles(payload: Mapping[str, Any]) -> JsonDict:
    tool_id = _optional_str(payload, "tool_id")
    profiles = list(DEFAULT_TOOL_AUTHORITY_PROFILES.values())
    if tool_id is not None:
        profiles = [profile for profile in profiles if profile["tool_id"] == tool_id]
    return {
        "version": GOVERNANCE_TOOL_PROFILES_VERSION,
        "tool_id": tool_id,
        "profile_count": len(profiles),
        "profiles": profiles,
        "authority_boundary": dict(_AUTHORITY_BOUNDARY),
    }


def validate_tool_profile_tool(payload: Mapping[str, Any]) -> JsonDict:
    profile = _require_mapping(payload, "profile")
    validated = _wrap_value_error(validate_tool_authority_profile, profile, field="profile")
    return {
        "version": GOVERNANCE_VALIDATE_TOOL_PROFILE_VERSION,
        "profile": validated,
        "profile_valid": True,
        "authority_boundary": dict(_AUTHORITY_BOUNDARY),
    }


def validate_artifact_tool(payload: Mapping[str, Any]) -> JsonDict:
    normalized = _wrap_value_error(validate_shared_shard_artifact, payload)
    return {
        "version": SHARD_VALIDATE_ARTIFACT_VERSION,
        "artifact_identity": _artifact_identity(normalized),
        "logical_shard_ids": _logical_shard_ids(normalized),
        "logical_shards": [_logical_shard_view(shard) for shard in normalized["shards"]],
        "selector_families": _selector_families(normalized),
        "authority_boundary": dict(_AUTHORITY_BOUNDARY),
    }


def route_selector_tool(payload: Mapping[str, Any]) -> JsonDict:
    selector = _require_str(payload, "selector")
    logical_ids = _wrap_value_error(_route_selector, payload, selector)
    return {
        "version": SHARD_ROUTE_SELECTOR_VERSION,
        "selector": selector,
        "logical_shard_ids": logical_ids,
        "logical_shard_count": len(logical_ids),
        "authority_boundary": dict(_AUTHORITY_BOUNDARY),
    }


def partial_graph_view_tool(payload: Mapping[str, Any]) -> JsonDict:
    selectors = _require_string_sequence(payload, "selectors")
    view = _wrap_value_error(build_partial_graph_view, payload, selectors)
    selected_shards = [_logical_shard_view(shard) for shard in view["selected_shards"]]
    return {
        "version": SHARD_PARTIAL_GRAPH_VIEW_VERSION,
        "artifact_identity": view["artifact_identity"],
        "selectors": view["selectors"],
        "selected_shard_ids": view["selected_shard_ids"],
        "selected_sections": view["selected_sections"],
        "selected_shards": selected_shards,
        "completeness": view["completeness"],
        "subset_of_artifact": view["subset_of_artifact"],
        "candidate_only": view["candidate_only"],
        "diagnostic_only": view["diagnostic_only"],
        "authority_boundary": dict(_AUTHORITY_BOUNDARY),
    }


def _artifact_identity(artifact: Mapping[str, Any]) -> JsonDict:
    return {
        "contractVersion": artifact["contractVersion"],
        "artifactId": artifact["artifactId"],
        "artifactRevision": artifact["artifactRevision"],
        "artifactClass": artifact["artifactClass"],
        "createdAtUtc": artifact["createdAtUtc"],
    }


def _logical_shard_ids(artifact: Mapping[str, Any]) -> list[str]:
    return [str(shard["shardId"]) for shard in artifact["shards"]]


def _logical_shard_view(shard: Mapping[str, Any]) -> JsonDict:
    return {
        "shardId": shard["shardId"],
        "section": shard["section"],
        "logicalKind": shard["logicalKind"],
        "encoding": shard["encoding"],
        "sizeBytes": shard["sizeBytes"],
        "contentDigest": shard["contentDigest"],
        "routingKeys": list(shard["routingKeys"]),
    }


def _selector_families(artifact: Mapping[str, Any]) -> list[str]:
    families: list[str] = []
    for shard in artifact["shards"]:
        for routing_key in shard["routingKeys"]:
            family = routing_key.split("=", 1)[0]
            if family not in families:
                families.append(family)
    return families


def _require_mapping(payload: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    value = payload.get(key)
    if not isinstance(value, Mapping):
        raise ToolInputError(f"Expected object field: {key}")
    return value


def _require_str(payload: Mapping[str, Any], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ToolInputError(f"Expected non-empty string field: {key}")
    return value.strip()


def _optional_str(payload: Mapping[str, Any], key: str) -> str | None:
    value = payload.get(key)
    if value is None:
        return None
    if isinstance(value, str):
        stripped = value.strip()
        return stripped or None
    raise ToolInputError(f"Expected string field: {key}")


def _require_string_sequence(payload: Mapping[str, Any], key: str) -> list[str]:
    value = payload.get(key)
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        raise ToolInputError(f"Expected array field: {key}")
    selectors: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise ToolInputError(f"Expected string entries in {key}")
        selectors.append(item.strip())
    return selectors


def _wrap_value_error(func, *args, field: str | None = None, **kwargs):
    try:
        return func(*args, **kwargs)
    except (TypeError, ValueError) as exc:
        if field is None:
            raise ToolInputError(str(exc)) from exc
        raise ToolInputError(f"Invalid {field}: {exc}") from exc
