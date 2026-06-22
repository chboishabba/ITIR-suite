from __future__ import annotations

from typing import Any, Mapping, Sequence

from .contracts import JsonDict, ToolHandler, ToolInputError, ToolSpec
from .domain_tools import (
    CLIMATE_CLAIM_REVIEW_VERSION,
    GWB_FOLLOW_GRAPH_VERSION,
    WIKIDATA_MIGRATION_CANDIDATE_VERSION,
    WIKIDATA_REVIEW_PACKET_VERSION,
    ZELPH_PARTIAL_CLOSURE_VERSION,
    climate_claim_review,
    gwb_follow_graph,
    wikidata_migration_candidate,
    wikidata_review_packet,
    zelph_partial_closure,
)
from .pnf_spectral_packet import VERSION as SPECTRAL_CANDIDATE_PACKET_VERSION, build_candidate_spectral_packet
from .shard_transport import (
    build_partial_graph_view,
    route_selector as _route_selector,
    validate_shared_shard_artifact,
)
from .tool_authority_profiles import DEFAULT_TOOL_AUTHORITY_PROFILES, validate_tool_authority_profile
from .wikiproject_tooling_profile import (
    WIKIPROJECT_TOOLING_PROFILE_VERSION,
    build_default_wikiproject_tooling_profile,
)
from .zelph_pack_loader import PACK_LOADER_VERSION, load_zelph_pack_source_descriptor


GOVERNANCE_TOOL_PROFILES_VERSION = "itir.governance.tool_profiles.v1"
GOVERNANCE_VALIDATE_TOOL_PROFILE_VERSION = "itir.governance.validate_tool_profile.v1"
WIKIDATA_TOOLING_PROFILE_VERSION = "itir.wikidata.tooling_profile.v1"
ZELPH_TRANSPORT_BOUNDARY_VERSION = "itir.zelph.transport_boundary.v1"
SHARD_VALIDATE_ARTIFACT_VERSION = "itir.shard.validate_artifact.v1"
SHARD_ROUTE_SELECTOR_VERSION = "itir.shard.route_selector.v1"
SHARD_PARTIAL_GRAPH_VIEW_VERSION = "itir.shard.partial_graph_view.v1"

_AUTHORITY_BOUNDARY: JsonDict = {
    "read_only": True,
    "non_authoritative": True,
    "canonical_truth_mutated": False,
}

_WIKIDATA_TOOLING_PROFILE_IDS: tuple[str, ...] = (
    "sensiblaw_review_packets",
    "entityschema",
    "listeria",
)

_ZELPH_TRANSPORT_PROFILE_IDS: tuple[str, ...] = (
    "zelph",
    "zelph_hf_shared_shards",
)


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
                name="itir.wikidata.tooling_profile",
                title="ITIR Wikidata tooling profile",
                description="Summarize the candidate-only Wikidata tooling boundary from default authority profiles.",
                input_schema={
                    "type": "object",
                    "additionalProperties": True,
                },
                response_version=WIKIDATA_TOOLING_PROFILE_VERSION,
                read_only=True,
            ),
            wikidata_tooling_profile_tool,
        ),
        (
            ToolSpec(
                name="itir.wikiproject.tooling_profile",
                title="ITIR WikiProject tooling profile",
                description="Materialize the candidate-only WikiProject tooling object W=(T,K,O,Sigma,Kappa,B,Pr,Rpt,Gv).",
                input_schema={
                    "type": "object",
                    "additionalProperties": True,
                },
                response_version=WIKIPROJECT_TOOLING_PROFILE_VERSION,
                read_only=True,
            ),
            wikiproject_tooling_profile_tool,
        ),
        (
            ToolSpec(
                name="itir.zelph.transport_boundary",
                title="ITIR Zelph transport boundary",
                description="Summarize the read-only Zelph transport boundary from default authority profiles.",
                input_schema={
                    "type": "object",
                    "additionalProperties": True,
                },
                response_version=ZELPH_TRANSPORT_BOUNDARY_VERSION,
                read_only=True,
            ),
            zelph_transport_boundary_tool,
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
        (
            ToolSpec(
                name="itir.wikidata.review_packet",
                title="ITIR Wikidata review packet",
                description="Compile a candidate-only review packet from statements, constraints, and tooling metadata.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "statements": {"type": "array", "items": {"type": "object"}},
                        "constraints": {"type": "array", "items": {"type": "object"}},
                        "tooling_profile": {"type": "object"},
                        "provenance_refs": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["statements", "constraints", "tooling_profile"],
                    "additionalProperties": True,
                },
                response_version=WIKIDATA_REVIEW_PACKET_VERSION,
                read_only=True,
            ),
            wikidata_review_packet,
        ),
        (
            ToolSpec(
                name="itir.wikidata.migration_candidate",
                title="ITIR Wikidata migration candidate",
                description="Compile a candidate-only Wikidata migration packet from structural refs and hints.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "statement_refs": {"type": "array", "items": {"type": "string"}},
                        "property_hints": {"type": "array", "items": {"type": "string"}},
                        "class_hints": {"type": "array", "items": {"type": "string"}},
                        "expected_fields": {"type": "array", "items": {"type": "string"}},
                        "characteristic_fields": {"type": "array", "items": {"type": "string"}},
                        "authority_label": {"type": "string"},
                    },
                    "required": ["authority_label"],
                    "additionalProperties": True,
                },
                response_version=WIKIDATA_MIGRATION_CANDIDATE_VERSION,
                read_only=True,
            ),
            wikidata_migration_candidate,
        ),
        (
            ToolSpec(
                name="itir.climate.claim_review",
                title="ITIR Climate claim review",
                description="Compile a candidate-only Climate NAT claim review packet without promotion authority.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "claims": {"type": "array", "items": {"type": "object"}},
                        "authority_label": {"type": "string"},
                        "gate_requirements": {"type": "object"},
                    },
                    "required": ["claims"],
                    "additionalProperties": True,
                },
                response_version=CLIMATE_CLAIM_REVIEW_VERSION,
                read_only=True,
            ),
            climate_claim_review,
        ),
        (
            ToolSpec(
                name="itir.gwb.follow_graph",
                title="ITIR GWB follow graph",
                description="Compile a candidate-only GWB/Brexit external authority follow graph.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "source_refs": {"type": "array", "items": {"type": "string"}},
                        "authority_refs": {"type": "array", "items": {"type": "string"}},
                        "follow_edges": {"type": "array", "items": {"type": "object"}},
                        "unresolved_obligations": {"type": "array", "items": {"type": "object"}},
                        "authority_label": {"type": "string"},
                    },
                    "required": ["follow_edges", "authority_label"],
                    "additionalProperties": True,
                },
                response_version=GWB_FOLLOW_GRAPH_VERSION,
                read_only=True,
            ),
            gwb_follow_graph,
        ),
        (
            ToolSpec(
                name="itir.spectral.candidate_packet",
                title="ITIR spectral candidate packet",
                description="Compile a candidate-only spectral packet projection from a partial view and spectral payload.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "partial_view": {"type": "object"},
                        "spectral_payload_summary_or_payload": {"type": "object"},
                    },
                    "required": ["partial_view", "spectral_payload_summary_or_payload"],
                    "additionalProperties": True,
                },
                response_version=SPECTRAL_CANDIDATE_PACKET_VERSION,
                read_only=True,
            ),
            spectral_candidate_packet_tool,
        ),
        (
            ToolSpec(
                name="itir.zelph.pack_sources",
                title="ITIR Zelph pack sources",
                description="Load local Zelph real-world pack manifests into a candidate-only source descriptor without network fetches.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "repo_root": {"type": "string"},
                        "manifest_paths": {"type": "array", "items": {"type": "string"}},
                        "hf_dataset_urls": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": [],
                    "additionalProperties": True,
                },
                response_version=PACK_LOADER_VERSION,
                read_only=True,
            ),
            zelph_pack_sources_tool,
        ),
        (
            ToolSpec(
                name="itir.zelph.partial_closure",
                title="ITIR Zelph partial closure",
                description="Compile a candidate-only partial closure summary from a shard view without authority claims.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "partial_graph_view": {"type": "object"},
                        "candidate_refs": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["partial_graph_view"],
                    "additionalProperties": True,
                },
                response_version=ZELPH_PARTIAL_CLOSURE_VERSION,
                read_only=True,
            ),
            zelph_partial_closure,
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


def wikidata_tooling_profile_tool(payload: Mapping[str, Any]) -> JsonDict:
    _ = payload
    profiles = _default_profiles_for_ids(_WIKIDATA_TOOLING_PROFILE_IDS)
    authority_boundary = dict(_AUTHORITY_BOUNDARY)
    authority_boundary["candidate_only"] = True
    return {
        "version": WIKIDATA_TOOLING_PROFILE_VERSION,
        "domain": "wikidata",
        "profile_ids": list(_WIKIDATA_TOOLING_PROFILE_IDS),
        "profile_count": len(profiles),
        "candidate_only": True,
        "non_authoritative": True,
        "tooling_profile": _profile_summary(
            profiles,
            authority_class="review_surface",
            summary_kind="tooling_profile",
        ),
        "authority_boundary": authority_boundary,
    }


def wikiproject_tooling_profile_tool(payload: Mapping[str, Any]) -> JsonDict:
    _ = payload
    profile = build_default_wikiproject_tooling_profile()
    return {
        "version": WIKIPROJECT_TOOLING_PROFILE_VERSION,
        "domain": "wikiproject",
        "candidate_only": profile["candidate_only"],
        "non_authoritative": profile["non_authoritative"],
        "promotion_enabled": profile["promotion_enabled"],
        "profile": profile,
        "authority_boundary": {
            **_AUTHORITY_BOUNDARY,
            "candidate_only": True,
            "promotion_enabled": False,
        },
    }


def zelph_transport_boundary_tool(payload: Mapping[str, Any]) -> JsonDict:
    _ = payload
    profiles = _default_profiles_for_ids(_ZELPH_TRANSPORT_PROFILE_IDS)
    authority_boundary = dict(_AUTHORITY_BOUNDARY)
    authority_boundary["candidate_only"] = True
    return {
        "version": ZELPH_TRANSPORT_BOUNDARY_VERSION,
        "domain": "zelph",
        "profile_ids": list(_ZELPH_TRANSPORT_PROFILE_IDS),
        "profile_count": len(profiles),
        "candidate_only": True,
        "non_authoritative": True,
        "transport_boundary": _profile_summary(
            profiles,
            authority_class="transport_boundary",
            summary_kind="transport_boundary",
        ),
        "authority_boundary": authority_boundary,
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


def spectral_candidate_packet_tool(payload: Mapping[str, Any]) -> JsonDict:
    partial_view = _require_mapping(payload, "partial_view")
    spectral_payload_summary_or_payload = _require_mapping(payload, "spectral_payload_summary_or_payload")
    return build_candidate_spectral_packet(partial_view, spectral_payload_summary_or_payload)


def zelph_pack_sources_tool(payload: Mapping[str, Any]) -> JsonDict:
    repo_root = _optional_str(payload, "repo_root")
    manifest_paths = payload.get("manifest_paths")
    if manifest_paths is not None:
        manifest_path_list = _require_string_sequence(payload, "manifest_paths")
    else:
        manifest_path_list = None
    hf_dataset_urls = payload.get("hf_dataset_urls")
    if hf_dataset_urls is not None:
        hf_dataset_url_list = _require_string_sequence(payload, "hf_dataset_urls")
    else:
        hf_dataset_url_list = None
    return _wrap_value_error(
        load_zelph_pack_source_descriptor,
        repo_root,
        manifest_paths=manifest_path_list,
        hf_dataset_urls=hf_dataset_url_list,
    )


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


def _default_profiles_for_ids(profile_ids: Sequence[str]) -> list[JsonDict]:
    profiles: list[JsonDict] = []
    for profile_id in profile_ids:
        try:
            profile = DEFAULT_TOOL_AUTHORITY_PROFILES[profile_id]
        except KeyError as exc:
            raise ToolInputError(f"Unknown default authority profile: {profile_id}") from exc
        profiles.append(profile)
    return profiles


def _profile_summary(
    profiles: Sequence[Mapping[str, Any]],
    *,
    authority_class: str,
    summary_kind: str,
) -> JsonDict:
    profile_list = [dict(profile) for profile in profiles]
    mutates = any(bool(profile["mutates"]) for profile in profile_list)
    max_authority = _least_authoritative(profile["max_authority"] for profile in profile_list)
    return {
        "kind": summary_kind,
        "authority_class": authority_class,
        "read_only": True,
        "non_authoritative": True,
        "canonical_truth_mutated": False,
        "candidate_only": True,
        "mutates": mutates,
        "max_authority": max_authority,
        "profiles": profile_list,
    }


def _least_authoritative(statuses: Sequence[str] | Any) -> str:
    lowest: str | None = None
    for status in statuses:
        status_text = str(status)
        if lowest is None or _authority_rank(status_text) > _authority_rank(lowest):
            lowest = status_text
    if lowest is None:
        raise ToolInputError("Expected at least one profile to summarize")
    return lowest


def _authority_rank(status: str) -> int:
    ordering = {
        "bottom": 0,
        "observed": 1,
        "candidate": 2,
        "diagnostic": 3,
        "proposal": 4,
        "receipt": 5,
        "reviewed": 6,
        "delegated": 7,
        "promoted": 8,
    }
    try:
        return ordering[status]
    except KeyError as exc:
        raise ToolInputError(f"Unknown authority status: {status}") from exc
