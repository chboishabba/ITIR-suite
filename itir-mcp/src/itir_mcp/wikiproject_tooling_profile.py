from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Mapping, Sequence, TypedDict

from .tool_authority_profiles import AuthorityStatus


WIKIPROJECT_TOOLING_PROFILE_VERSION = "itir.wikiproject.tooling_profile.v1"

_TOOL_KIND_VALUES = frozenset(
    {
        "batch_transport",
        "repair",
        "schema",
        "bot",
        "ingestion",
        "constraints",
    }
)
_DIAGNOSTIC_OUTPUT_VALUES = frozenset(
    {
        AuthorityStatus.CANDIDATE.value,
        AuthorityStatus.DIAGNOSTIC.value,
    }
)


class WikiProjectToolingEntryDict(TypedDict):
    tool_id: str
    label: str
    kind: str
    outputs: list[str]
    candidate_only: bool
    non_authoritative: bool
    promotion_enabled: bool
    self_promotes: bool
    notes: dict[str, Any]


class WikiProjectToolingProfileDict(TypedDict):
    version: str
    profile_id: str
    candidate_only: bool
    non_authoritative: bool
    promotion_enabled: bool
    W: dict[str, Any]


@dataclass(frozen=True, slots=True)
class WikiProjectToolingEntry:
    tool_id: str
    label: str
    kind: str
    outputs: tuple[str, ...]
    candidate_only: bool = True
    non_authoritative: bool = True
    promotion_enabled: bool = False
    self_promotes: bool = False
    notes: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class WikiProjectToolingProfile:
    profile_id: str
    candidate_only: bool
    non_authoritative: bool
    promotion_enabled: bool
    tools: tuple[WikiProjectToolingEntry, ...]
    sigma: Mapping[str, Any] = field(default_factory=dict)
    kappa: Mapping[str, Any] = field(default_factory=dict)
    boundary: Mapping[str, Any] = field(default_factory=dict)
    promotion_rules: Mapping[str, Any] = field(default_factory=dict)
    report: Mapping[str, Any] = field(default_factory=dict)
    governance: Mapping[str, Any] = field(default_factory=dict)


def build_default_wikiproject_tooling_profile() -> WikiProjectToolingProfileDict:
    profile = WikiProjectToolingProfile(
        profile_id="wikiproject-tooling",
        candidate_only=True,
        non_authoritative=True,
        promotion_enabled=False,
        tools=_default_tools(),
        sigma={
            "taxonomy_source": "etherpad",
            "candidate_only": True,
            "authority_label": "candidate-only",
            "non_authoritative": True,
        },
        kappa={
            "tool_capabilities": _default_capabilities(),
        },
        boundary={
            "read_only": True,
            "non_authoritative": True,
            "canonical_truth_mutated": False,
        },
        promotion_rules={
            "promotion_enabled": False,
            "requires_gate": False,
            "self_promotes": False,
            "promotion_targets": [],
        },
        report={
            "diagnostic_only": True,
            "authority_label": "candidate-only",
            "tool_count": 0,
        },
        governance={
            "profile_class": "wiki-project-tooling",
            "governance_contract": WIKIPROJECT_TOOLING_PROFILE_VERSION,
        },
    )
    return validate_wikiproject_tooling_profile(profile)


def validate_wikiproject_tooling_profile(
    profile: WikiProjectToolingProfile | Mapping[str, Any],
) -> WikiProjectToolingProfileDict:
    data = _profile_mapping(profile)
    profile_id = _non_empty_text(data.get("profile_id"), "profile_id")
    candidate_only = _require_bool(data.get("candidate_only"), "candidate_only")
    non_authoritative = _require_bool(data.get("non_authoritative"), "non_authoritative")
    promotion_enabled = _require_bool(data.get("promotion_enabled"), "promotion_enabled")
    tools = _normalize_tools(data.get("tools"))
    sigma = _normalize_notes(data.get("sigma"), "sigma")
    kappa = _normalize_notes(data.get("kappa"), "kappa")
    boundary = _normalize_notes(data.get("boundary"), "boundary")
    promotion_rules = _normalize_notes(data.get("promotion_rules"), "promotion_rules")
    report = _normalize_notes(data.get("report"), "report")
    governance = _normalize_notes(data.get("governance"), "governance")

    if not candidate_only:
        raise ValueError("wiki project tooling profiles must be candidate_only")
    if not non_authoritative:
        raise ValueError("wiki project tooling profiles must be non_authoritative")
    if promotion_enabled:
        raise ValueError("wiki project tooling profiles must disable promotion")

    if boundary.get("non_authoritative") is not True or boundary.get("read_only") is not True:
        raise ValueError("boundary must remain non-authoritative and read-only")
    if boundary.get("canonical_truth_mutated") is not False:
        raise ValueError("boundary must not mutate canonical truth")

    if promotion_rules.get("promotion_enabled") is not False:
        raise ValueError("promotion rules must disable promotion")
    if promotion_rules.get("self_promotes") is not False:
        raise ValueError("promotion rules must not self-promote")

    normalized_tools = [_normalize_tool(tool) for tool in tools]
    tool_ids = [tool["tool_id"] for tool in normalized_tools]
    if len(tool_ids) != len(set(tool_ids)):
        raise ValueError("tool_id values must be unique")

    kinds = _unique_preserving_order(tool["kind"] for tool in normalized_tools)
    outputs = _unique_preserving_order(output for tool in normalized_tools for output in tool["outputs"])

    if any(output not in _DIAGNOSTIC_OUTPUT_VALUES for output in outputs):
        raise ValueError("wiki project tooling profiles may only emit candidate or diagnostic outputs")
    if any(tool["self_promotes"] for tool in normalized_tools):
        raise ValueError("no wiki project tooling tool may self-promote")
    if any(tool["promotion_enabled"] for tool in normalized_tools):
        raise ValueError("no wiki project tooling tool may enable promotion")
    if any(tool["non_authoritative"] is not True for tool in normalized_tools):
        raise ValueError("all tools must be non-authoritative")
    if any(tool["candidate_only"] is not True for tool in normalized_tools):
        raise ValueError("all tools must be candidate_only")
    if any(AuthorityStatus.PROMOTED.value in tool["outputs"] for tool in normalized_tools):
        raise ValueError("no tool may self-promote to promoted output")

    expected_capabilities = _default_capabilities()
    provided_capabilities = kappa.get("tool_capabilities", {})
    if not isinstance(provided_capabilities, Mapping):
        raise ValueError("kappa.tool_capabilities must be an object")
    normalized_capabilities = {
        str(tool_id): _normalize_string_sequence(capabilities, f"kappa.tool_capabilities.{tool_id}")
        for tool_id, capabilities in provided_capabilities.items()
    }
    if normalized_capabilities and normalized_capabilities != expected_capabilities:
        raise ValueError("kappa.tool_capabilities does not match the default taxonomy")
    if not normalized_capabilities:
        normalized_capabilities = expected_capabilities

    normalized_sigma = dict(sigma)
    normalized_sigma.setdefault("taxonomy_source", "etherpad")
    normalized_sigma["candidate_only"] = True
    normalized_sigma["non_authoritative"] = True
    normalized_sigma["authority_label"] = "candidate-only"

    normalized_boundary = dict(boundary)
    normalized_boundary["read_only"] = True
    normalized_boundary["non_authoritative"] = True
    normalized_boundary["canonical_truth_mutated"] = False

    normalized_promotion_rules = dict(promotion_rules)
    normalized_promotion_rules["promotion_enabled"] = False
    normalized_promotion_rules["self_promotes"] = False

    normalized_report = dict(report)
    normalized_report["authority_label"] = "candidate-only"
    normalized_report["diagnostic_only"] = True
    normalized_report["tool_count"] = len(normalized_tools)

    normalized_governance = dict(governance)
    normalized_governance.setdefault("profile_class", "wiki-project-tooling")
    normalized_governance["governance_contract"] = WIKIPROJECT_TOOLING_PROFILE_VERSION

    return {
        "version": WIKIPROJECT_TOOLING_PROFILE_VERSION,
        "profile_id": profile_id,
        "candidate_only": True,
        "non_authoritative": True,
        "promotion_enabled": False,
        "W": {
            "T": normalized_tools,
            "K": kinds,
            "O": outputs,
            "Sigma": normalized_sigma,
            "Kappa": {"tool_capabilities": normalized_capabilities},
            "B": normalized_boundary,
            "Pr": normalized_promotion_rules,
            "Rpt": normalized_report,
            "Gv": normalized_governance,
        },
    }


def _default_tools() -> tuple[WikiProjectToolingEntry, ...]:
    return (
        WikiProjectToolingEntry(
            tool_id="quickstatements",
            label="QuickStatements",
            kind="batch_transport",
            outputs=(AuthorityStatus.CANDIDATE.value, AuthorityStatus.DIAGNOSTIC.value),
            notes={"taxonomy_group": "batch", "source": "etherpad"},
        ),
        WikiProjectToolingEntry(
            tool_id="openrefine",
            label="OpenRefine",
            kind="repair",
            outputs=(AuthorityStatus.CANDIDATE.value, AuthorityStatus.DIAGNOSTIC.value),
            notes={"taxonomy_group": "cleanup", "source": "etherpad"},
        ),
        WikiProjectToolingEntry(
            tool_id="entityschemas",
            label="EntitySchemas",
            kind="schema",
            outputs=(AuthorityStatus.CANDIDATE.value, AuthorityStatus.DIAGNOSTIC.value),
            notes={"taxonomy_group": "schema", "source": "etherpad"},
        ),
        WikiProjectToolingEntry(
            tool_id="krbot",
            label="KrBot",
            kind="bot",
            outputs=(AuthorityStatus.CANDIDATE.value, AuthorityStatus.DIAGNOSTIC.value),
            notes={"taxonomy_group": "bot", "source": "etherpad"},
        ),
        WikiProjectToolingEntry(
            tool_id="listeria",
            label="Listeria",
            kind="ingestion",
            outputs=(AuthorityStatus.CANDIDATE.value, AuthorityStatus.DIAGNOSTIC.value),
            notes={"taxonomy_group": "ingestion", "source": "etherpad"},
        ),
        WikiProjectToolingEntry(
            tool_id="property_constraints",
            label="Property constraints",
            kind="constraints",
            outputs=(AuthorityStatus.CANDIDATE.value, AuthorityStatus.DIAGNOSTIC.value),
            notes={"taxonomy_group": "constraints", "source": "etherpad"},
        ),
    )


def _default_capabilities() -> dict[str, list[str]]:
    return {
        "quickstatements": ["batch transport", "candidate staging"],
        "openrefine": ["cleanup", "repair"],
        "entityschemas": ["schema drafting", "constraint modeling"],
        "krbot": ["bot transport", "candidate staging"],
        "listeria": ["ingestion", "receipt mirroring"],
        "property_constraints": ["property constraint diagnostics"],
    }


def _profile_mapping(profile: WikiProjectToolingProfile | Mapping[str, Any]) -> dict[str, Any]:
    if isinstance(profile, WikiProjectToolingProfile):
        return asdict(profile)
    if isinstance(profile, Mapping):
        return dict(profile)
    raise ValueError("profile must be a WikiProjectToolingProfile or mapping")


def _normalize_tool(tool: Any) -> WikiProjectToolingEntryDict:
    data = _normalize_notes(tool, "tools entry")
    tool_id = _non_empty_text(data.get("tool_id"), "tool_id")
    label = _non_empty_text(data.get("label"), "label")
    kind = _non_empty_text(data.get("kind"), "kind")
    if kind not in _TOOL_KIND_VALUES:
        raise ValueError(f"unknown kind: {kind}")
    outputs = _normalize_outputs(data.get("outputs"))
    candidate_only = _require_bool(data.get("candidate_only"), "candidate_only")
    non_authoritative = _require_bool(data.get("non_authoritative"), "non_authoritative")
    promotion_enabled = _require_bool(data.get("promotion_enabled"), "promotion_enabled")
    self_promotes = _require_bool(data.get("self_promotes"), "self_promotes")
    notes = _normalize_notes(data.get("notes"), f"notes for {tool_id}")

    if candidate_only is not True:
        raise ValueError(f"{tool_id} must be candidate_only")
    if non_authoritative is not True:
        raise ValueError(f"{tool_id} must be non_authoritative")
    if promotion_enabled is not False:
        raise ValueError(f"{tool_id} must not enable promotion")
    if self_promotes is not False:
        raise ValueError(f"{tool_id} must not self-promote")
    if AuthorityStatus.PROMOTED.value in outputs:
        raise ValueError(f"{tool_id} may not output promoted")

    return {
        "tool_id": tool_id,
        "label": label,
        "kind": kind,
        "outputs": outputs,
        "candidate_only": candidate_only,
        "non_authoritative": non_authoritative,
        "promotion_enabled": promotion_enabled,
        "self_promotes": self_promotes,
        "notes": notes,
    }


def _normalize_tools(value: Any) -> list[WikiProjectToolingEntryDict]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        raise ValueError("tools must be a sequence")
    tools = [_normalize_tool(tool) for tool in value]
    if not tools:
        raise ValueError("tools must not be empty")
    return tools


def _normalize_outputs(value: Any) -> list[str]:
    outputs = _normalize_string_sequence(value, "outputs")
    normalized: list[str] = []
    seen: set[str] = set()
    for output in outputs:
        if output not in _DIAGNOSTIC_OUTPUT_VALUES:
            raise ValueError(f"unknown output status: {output}")
        if output not in seen:
            seen.add(output)
            normalized.append(output)
    return normalized


def _normalize_notes(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{label} must be an object")
    return dict(value)


def _normalize_string_sequence(value: Any, label: str) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        raise ValueError(f"{label} must be a sequence")
    result: list[str] = []
    seen: set[str] = set()
    for item in value:
        text = _non_empty_text(item, label)
        if text not in seen:
            seen.add(text)
            result.append(text)
    if not result:
        raise ValueError(f"{label} must not be empty")
    return result


def _non_empty_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty string")
    return value.strip()


def _require_bool(value: Any, label: str) -> bool:
    if isinstance(value, bool):
        return value
    raise ValueError(f"{label} must be a boolean")


def _unique_preserving_order(values: Sequence[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


DEFAULT_WIKIPROJECT_TOOLING_PROFILE = build_default_wikiproject_tooling_profile()
