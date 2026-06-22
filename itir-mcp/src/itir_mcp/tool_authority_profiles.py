from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Mapping, Sequence, TypedDict


class ToolKind(str, Enum):
    INGESTION = "ingestion"
    VALIDATION = "validation"
    REPAIR = "repair"
    REPORTING = "reporting"
    GOVERNANCE = "governance"
    ARTIFACT_TRANSPORT = "artifact_transport"
    CANDIDATE_CLOSURE = "candidate_closure"
    RESIDUAL_GEOMETRY = "residual_geometry"


TOOL_KIND_VALUES = frozenset(kind.value for kind in ToolKind)


class AuthorityStatus(str, Enum):
    BOTTOM = "bottom"
    OBSERVED = "observed"
    CANDIDATE = "candidate"
    DIAGNOSTIC = "diagnostic"
    PROPOSAL = "proposal"
    RECEIPT = "receipt"
    REVIEWED = "reviewed"
    DELEGATED = "delegated"
    PROMOTED = "promoted"


AUTHORITY_STATUS_VALUES = frozenset(status.value for status in AuthorityStatus)
AUTHORITY_STATUS_ORDER = {status.value: index for index, status in enumerate(AuthorityStatus)}
PROMOTING_OUTPUT_STATUSES = frozenset(
    {
        AuthorityStatus.CANDIDATE.value,
        AuthorityStatus.DIAGNOSTIC.value,
        AuthorityStatus.PROPOSAL.value,
        AuthorityStatus.DELEGATED.value,
        AuthorityStatus.PROMOTED.value,
    }
)

VALIDATION_MODES = frozenset({"none", "advisory", "gate", "strict"})
REPAIR_MODES = frozenset({"none", "advisory", "gate", "strict"})
_GATE_NOTE_KEYS = frozenset({"gate", "gate_id", "gate_kind", "gate_process", "promotion_gate"})


class ToolAuthorityProfileDict(TypedDict):
    tool_id: str
    kind: str
    inputs: list[str]
    outputs: list[str]
    mutates: bool
    validation_mode: str
    repair_mode: str
    max_authority: str
    promotion_requires_gate: bool
    authority_notes: dict[str, Any]


@dataclass(frozen=True, slots=True)
class ToolAuthorityProfile:
    tool_id: str
    kind: str
    inputs: tuple[str, ...]
    outputs: tuple[str, ...]
    mutates: bool
    validation_mode: str
    repair_mode: str
    max_authority: str
    promotion_requires_gate: bool
    authority_notes: Mapping[str, Any] = field(default_factory=dict)


def validate_tool_authority_profile(profile: ToolAuthorityProfile | Mapping[str, Any]) -> ToolAuthorityProfileDict:
    data = _profile_mapping(profile)
    tool_id = _non_empty_text(data.get("tool_id"), "tool_id")
    kind = _normalize_kind(data.get("kind"))
    inputs = _normalize_statuses(data.get("inputs"), "inputs")
    outputs = _normalize_statuses(data.get("outputs"), "outputs")
    mutates = _require_bool(data.get("mutates"), "mutates")
    validation_mode = _normalize_mode(data.get("validation_mode"), "validation_mode", VALIDATION_MODES)
    repair_mode = _normalize_mode(data.get("repair_mode"), "repair_mode", REPAIR_MODES)
    max_authority = _normalize_status(data.get("max_authority"), "max_authority")
    promotion_requires_gate = _require_bool(data.get("promotion_requires_gate"), "promotion_requires_gate")
    authority_notes = _normalize_notes(data.get("authority_notes"))

    if mutates and max_authority == AuthorityStatus.PROMOTED.value and not promotion_requires_gate:
        raise ValueError("mutating tools cannot claim max_authority promoted without promotion_requires_gate")

    promoting_outputs = [status for status in outputs if status in PROMOTING_OUTPUT_STATUSES]
    if promoting_outputs:
        if not promotion_requires_gate:
            raise ValueError("self-promoting outputs require promotion_requires_gate")
        if not _has_gate_metadata(authority_notes):
            raise ValueError("self-promoting outputs require explicit gate metadata in authority_notes")

    if any(_authority_order(status) > _authority_order(max_authority) for status in outputs):
        raise ValueError("output authority exceeds max_authority")

    return {
        "tool_id": tool_id,
        "kind": kind,
        "inputs": inputs,
        "outputs": outputs,
        "mutates": mutates,
        "validation_mode": validation_mode,
        "repair_mode": repair_mode,
        "max_authority": max_authority,
        "promotion_requires_gate": promotion_requires_gate,
        "authority_notes": authority_notes,
    }


def get_default_tool_authority_profiles() -> dict[str, ToolAuthorityProfileDict]:
    return {profile.tool_id: validate_tool_authority_profile(profile) for profile in DEFAULT_TOOL_AUTHORITY_PROFILE_SPECS}


def _profile_mapping(profile: ToolAuthorityProfile | Mapping[str, Any]) -> dict[str, Any]:
    if isinstance(profile, ToolAuthorityProfile):
        return asdict(profile)
    if isinstance(profile, Mapping):
        return dict(profile)
    raise ValueError("profile must be a ToolAuthorityProfile or mapping")


def _normalize_kind(value: Any) -> str:
    kind = _normalize_text(value, "kind")
    if kind not in TOOL_KIND_VALUES:
        raise ValueError(f"unknown kind: {kind}")
    return kind


def _normalize_status(value: Any, label: str) -> str:
    status = _normalize_text(value, label)
    if status not in AUTHORITY_STATUS_VALUES:
        raise ValueError(f"unknown status for {label}: {status}")
    return status


def _normalize_statuses(value: Any, label: str) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        raise ValueError(f"{label} must be a sequence")
    statuses: list[str] = []
    seen: set[str] = set()
    for item in value:
        status = _normalize_status(item, label)
        if status not in seen:
            seen.add(status)
            statuses.append(status)
    if not statuses:
        raise ValueError(f"{label} must not be empty")
    return statuses


def _normalize_mode(value: Any, label: str, allowed: frozenset[str]) -> str:
    mode = _normalize_text(value, label)
    if mode not in allowed:
        raise ValueError(f"unknown mode for {label}: {mode}")
    return mode


def _normalize_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty string")
    return value.strip().lower()


def _non_empty_text(value: Any, label: str) -> str:
    return _normalize_text(value, label)


def _normalize_notes(value: Any) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError("authority_notes must be an object")
    return dict(value)


def _has_gate_metadata(authority_notes: Mapping[str, Any]) -> bool:
    for key in _GATE_NOTE_KEYS:
        value = authority_notes.get(key)
        if isinstance(value, str) and value.strip():
            return True
        if isinstance(value, Mapping) and value:
            return True
        if value is True:
            return True
    return False


def _require_bool(value: Any, label: str) -> bool:
    if isinstance(value, bool):
        return value
    raise ValueError(f"{label} must be a boolean")


def _authority_order(status: str) -> int:
    try:
        return AUTHORITY_STATUS_ORDER[status]
    except KeyError as exc:
        raise ValueError(f"unknown status: {status}") from exc


DEFAULT_TOOL_AUTHORITY_PROFILE_SPECS: tuple[ToolAuthorityProfile, ...] = (
    ToolAuthorityProfile(
        tool_id="zelph",
        kind=ToolKind.INGESTION.value,
        inputs=(AuthorityStatus.OBSERVED.value,),
        outputs=(AuthorityStatus.OBSERVED.value, AuthorityStatus.RECEIPT.value),
        mutates=False,
        validation_mode="strict",
        repair_mode="none",
        max_authority=AuthorityStatus.RECEIPT.value,
        promotion_requires_gate=False,
        authority_notes={"authority_class": "observer", "note": "Zelph defaults to non-authoritative receipt output."},
    ),
    ToolAuthorityProfile(
        tool_id="zelph_hf_shared_shards",
        kind=ToolKind.INGESTION.value,
        inputs=(AuthorityStatus.OBSERVED.value,),
        outputs=(AuthorityStatus.RECEIPT.value,),
        mutates=False,
        validation_mode="strict",
        repair_mode="none",
        max_authority=AuthorityStatus.RECEIPT.value,
        promotion_requires_gate=False,
        authority_notes={"authority_class": "observer", "note": "Shared shards stay at receipt authority."},
    ),
    ToolAuthorityProfile(
        tool_id="sensiblaw_review_packets",
        kind=ToolKind.VALIDATION.value,
        inputs=(AuthorityStatus.OBSERVED.value, AuthorityStatus.CANDIDATE.value),
        outputs=(AuthorityStatus.REVIEWED.value, AuthorityStatus.RECEIPT.value),
        mutates=False,
        validation_mode="strict",
        repair_mode="none",
        max_authority=AuthorityStatus.REVIEWED.value,
        promotion_requires_gate=False,
        authority_notes={"authority_class": "review", "note": "Review packets are receipts, not canonical truth."},
    ),
    ToolAuthorityProfile(
        tool_id="pnf_spectral_abi",
        kind=ToolKind.RESIDUAL_GEOMETRY.value,
        inputs=(AuthorityStatus.CANDIDATE.value, AuthorityStatus.DIAGNOSTIC.value),
        outputs=(AuthorityStatus.DIAGNOSTIC.value, AuthorityStatus.RECEIPT.value),
        mutates=False,
        validation_mode="strict",
        repair_mode="none",
        max_authority=AuthorityStatus.RECEIPT.value,
        promotion_requires_gate=True,
        authority_notes={
            "authority_class": "diagnostic",
            "gate": "external review receipt",
            "note": "Spectral ABI remains diagnostic unless a separate gate-backed review promotes it.",
        },
    ),
    ToolAuthorityProfile(
        tool_id="climate_nat",
        kind=ToolKind.REPORTING.value,
        inputs=(AuthorityStatus.OBSERVED.value,),
        outputs=(AuthorityStatus.OBSERVED.value, AuthorityStatus.RECEIPT.value),
        mutates=False,
        validation_mode="advisory",
        repair_mode="none",
        max_authority=AuthorityStatus.RECEIPT.value,
        promotion_requires_gate=False,
        authority_notes={"authority_class": "reporting", "note": "Climate NAT reports stay non-authoritative by default."},
    ),
    ToolAuthorityProfile(
        tool_id="gwb_brexit_follow_graph",
        kind=ToolKind.CANDIDATE_CLOSURE.value,
        inputs=(AuthorityStatus.OBSERVED.value, AuthorityStatus.CANDIDATE.value),
        outputs=(AuthorityStatus.CANDIDATE.value, AuthorityStatus.RECEIPT.value),
        mutates=False,
        validation_mode="strict",
        repair_mode="none",
        max_authority=AuthorityStatus.RECEIPT.value,
        promotion_requires_gate=True,
        authority_notes={
            "authority_class": "candidate_closure",
            "gate": "human follow-graph review",
            "note": "Brexit follow-graph closure is candidate-only until an explicit review gate accepts it.",
        },
    ),
    ToolAuthorityProfile(
        tool_id="itir_mcp",
        kind=ToolKind.GOVERNANCE.value,
        inputs=(AuthorityStatus.RECEIPT.value,),
        outputs=(AuthorityStatus.RECEIPT.value,),
        mutates=False,
        validation_mode="strict",
        repair_mode="none",
        max_authority=AuthorityStatus.RECEIPT.value,
        promotion_requires_gate=False,
        authority_notes={"authority_class": "governance", "note": "Core MCP governance stays at receipt authority."},
    ),
    ToolAuthorityProfile(
        tool_id="quickstatements",
        kind=ToolKind.ARTIFACT_TRANSPORT.value,
        inputs=(AuthorityStatus.RECEIPT.value,),
        outputs=(AuthorityStatus.RECEIPT.value,),
        mutates=True,
        validation_mode="gate",
        repair_mode="gate",
        max_authority=AuthorityStatus.RECEIPT.value,
        promotion_requires_gate=True,
        authority_notes={"gate": "explicit batch approval", "note": "QuickStatements mutates transport but does not truth-promote."},
    ),
    ToolAuthorityProfile(
        tool_id="openrefine",
        kind=ToolKind.REPAIR.value,
        inputs=(AuthorityStatus.OBSERVED.value, AuthorityStatus.RECEIPT.value),
        outputs=(AuthorityStatus.RECEIPT.value,),
        mutates=True,
        validation_mode="strict",
        repair_mode="gate",
        max_authority=AuthorityStatus.RECEIPT.value,
        promotion_requires_gate=True,
        authority_notes={"gate": "repair review", "note": "OpenRefine repairs are gated and remain non-authoritative by default."},
    ),
    ToolAuthorityProfile(
        tool_id="entityschema",
        kind=ToolKind.GOVERNANCE.value,
        inputs=(AuthorityStatus.REVIEWED.value,),
        outputs=(AuthorityStatus.REVIEWED.value, AuthorityStatus.RECEIPT.value),
        mutates=False,
        validation_mode="strict",
        repair_mode="none",
        max_authority=AuthorityStatus.REVIEWED.value,
        promotion_requires_gate=False,
        authority_notes={"authority_class": "governance", "note": "EntitySchema emits reviewed receipts, not promoted truth."},
    ),
    ToolAuthorityProfile(
        tool_id="krbot",
        kind=ToolKind.ARTIFACT_TRANSPORT.value,
        inputs=(AuthorityStatus.OBSERVED.value,),
        outputs=(AuthorityStatus.OBSERVED.value, AuthorityStatus.RECEIPT.value),
        mutates=True,
        validation_mode="advisory",
        repair_mode="none",
        max_authority=AuthorityStatus.RECEIPT.value,
        promotion_requires_gate=False,
        authority_notes={"authority_class": "bot_transport", "note": "KrBot operates as transport and stays below promotion."},
    ),
    ToolAuthorityProfile(
        tool_id="listeria",
        kind=ToolKind.INGESTION.value,
        inputs=(AuthorityStatus.OBSERVED.value,),
        outputs=(AuthorityStatus.OBSERVED.value, AuthorityStatus.RECEIPT.value),
        mutates=False,
        validation_mode="strict",
        repair_mode="none",
        max_authority=AuthorityStatus.RECEIPT.value,
        promotion_requires_gate=False,
        authority_notes={"authority_class": "ingestion", "note": "Listeria defaults to receipt-bound ingestion."},
    ),
)


DEFAULT_TOOL_AUTHORITY_PROFILES = get_default_tool_authority_profiles()


REGISTRY_TOOL_AUTHORITY_PROFILE_SPECS: tuple[ToolAuthorityProfile, ...] = (
    ToolAuthorityProfile(
        tool_id="itir.governance.tool_profiles",
        kind=ToolKind.GOVERNANCE.value,
        inputs=(AuthorityStatus.RECEIPT.value,),
        outputs=(AuthorityStatus.RECEIPT.value,),
        mutates=False,
        validation_mode="strict",
        repair_mode="none",
        max_authority=AuthorityStatus.RECEIPT.value,
        promotion_requires_gate=False,
        authority_notes={
            "authority_class": "registry_governance",
            "non_authoritative": True,
            "note": "Registry governance surfaces are read-only profile views.",
        },
    ),
    ToolAuthorityProfile(
        tool_id="itir.governance.validate_tool_profile",
        kind=ToolKind.GOVERNANCE.value,
        inputs=(AuthorityStatus.RECEIPT.value,),
        outputs=(AuthorityStatus.RECEIPT.value,),
        mutates=False,
        validation_mode="strict",
        repair_mode="none",
        max_authority=AuthorityStatus.RECEIPT.value,
        promotion_requires_gate=False,
        authority_notes={
            "authority_class": "registry_governance",
            "non_authoritative": True,
            "note": "Registry validation surfaces are read-only profile checks.",
        },
    ),
    ToolAuthorityProfile(
        tool_id="itir.wikidata.tooling_profile",
        kind=ToolKind.GOVERNANCE.value,
        inputs=(AuthorityStatus.OBSERVED.value, AuthorityStatus.RECEIPT.value),
        outputs=(AuthorityStatus.RECEIPT.value,),
        mutates=False,
        validation_mode="strict",
        repair_mode="none",
        max_authority=AuthorityStatus.RECEIPT.value,
        promotion_requires_gate=False,
        authority_notes={
            "authority_class": "domain_governance",
            "non_authoritative": True,
            "note": "Wikidata tooling profiles classify candidate/review surfaces without promotion.",
        },
    ),
    ToolAuthorityProfile(
        tool_id="itir.wikidata.review_packet",
        kind=ToolKind.VALIDATION.value,
        inputs=(AuthorityStatus.OBSERVED.value, AuthorityStatus.CANDIDATE.value, AuthorityStatus.RECEIPT.value),
        outputs=(AuthorityStatus.RECEIPT.value,),
        mutates=False,
        validation_mode="strict",
        repair_mode="none",
        max_authority=AuthorityStatus.RECEIPT.value,
        promotion_requires_gate=False,
        authority_notes={
            "authority_class": "domain_review_packet",
            "candidate_only": True,
            "non_authoritative": True,
            "note": "Wikidata review packets compile candidate review state only and cannot promote statements.",
        },
    ),
    ToolAuthorityProfile(
        tool_id="itir.wikiproject.tooling_profile",
        kind=ToolKind.GOVERNANCE.value,
        inputs=(AuthorityStatus.OBSERVED.value, AuthorityStatus.RECEIPT.value),
        outputs=(AuthorityStatus.RECEIPT.value,),
        mutates=False,
        validation_mode="strict",
        repair_mode="none",
        max_authority=AuthorityStatus.RECEIPT.value,
        promotion_requires_gate=False,
        authority_notes={
            "authority_class": "domain_governance",
            "non_authoritative": True,
            "note": "WikiProject tooling objects are diagnostic ontology-governance maps only.",
        },
    ),
    ToolAuthorityProfile(
        tool_id="itir.zelph.transport_boundary",
        kind=ToolKind.ARTIFACT_TRANSPORT.value,
        inputs=(AuthorityStatus.OBSERVED.value, AuthorityStatus.RECEIPT.value),
        outputs=(AuthorityStatus.RECEIPT.value,),
        mutates=False,
        validation_mode="strict",
        repair_mode="none",
        max_authority=AuthorityStatus.RECEIPT.value,
        promotion_requires_gate=False,
        authority_notes={
            "authority_class": "transport_boundary",
            "non_authoritative": True,
            "note": "Zelph transport boundary tools expose artifact logistics, not reasoning authority.",
        },
    ),
    ToolAuthorityProfile(
        tool_id="itir.zelph.partial_closure",
        kind=ToolKind.CANDIDATE_CLOSURE.value,
        inputs=(AuthorityStatus.OBSERVED.value, AuthorityStatus.CANDIDATE.value, AuthorityStatus.RECEIPT.value),
        outputs=(AuthorityStatus.RECEIPT.value,),
        mutates=False,
        validation_mode="strict",
        repair_mode="none",
        max_authority=AuthorityStatus.RECEIPT.value,
        promotion_requires_gate=False,
        authority_notes={
            "authority_class": "partial_candidate_closure",
            "candidate_only": True,
            "non_authoritative": True,
            "note": "Partial Zelph closure exposes incomplete candidate views and cannot claim truth or promotion.",
        },
    ),
    ToolAuthorityProfile(
        tool_id="itir.shard.validate_artifact",
        kind=ToolKind.RESIDUAL_GEOMETRY.value,
        inputs=(AuthorityStatus.OBSERVED.value, AuthorityStatus.RECEIPT.value),
        outputs=(AuthorityStatus.RECEIPT.value,),
        mutates=False,
        validation_mode="strict",
        repair_mode="none",
        max_authority=AuthorityStatus.RECEIPT.value,
        promotion_requires_gate=False,
        authority_notes={
            "authority_class": "registry_shard",
            "non_authoritative": True,
            "note": "Shard validation surfaces only produce logical receipt views.",
        },
    ),
    ToolAuthorityProfile(
        tool_id="itir.shard.route_selector",
        kind=ToolKind.RESIDUAL_GEOMETRY.value,
        inputs=(AuthorityStatus.OBSERVED.value, AuthorityStatus.RECEIPT.value),
        outputs=(AuthorityStatus.RECEIPT.value,),
        mutates=False,
        validation_mode="strict",
        repair_mode="none",
        max_authority=AuthorityStatus.RECEIPT.value,
        promotion_requires_gate=False,
        authority_notes={
            "authority_class": "registry_shard",
            "non_authoritative": True,
            "note": "Shard route selectors resolve logical ids only.",
        },
    ),
    ToolAuthorityProfile(
        tool_id="itir.shard.partial_graph_view",
        kind=ToolKind.RESIDUAL_GEOMETRY.value,
        inputs=(AuthorityStatus.OBSERVED.value, AuthorityStatus.RECEIPT.value),
        outputs=(AuthorityStatus.RECEIPT.value,),
        mutates=False,
        validation_mode="strict",
        repair_mode="none",
        max_authority=AuthorityStatus.RECEIPT.value,
        promotion_requires_gate=False,
        authority_notes={
            "authority_class": "registry_shard",
            "non_authoritative": True,
            "note": "Shard partial graph views remain non-authoritative.",
        },
    ),
)


DEFAULT_REGISTRY_TOOL_AUTHORITY_PROFILES = {
    profile.tool_id: validate_tool_authority_profile(profile) for profile in REGISTRY_TOOL_AUTHORITY_PROFILE_SPECS
}
