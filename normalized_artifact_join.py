from __future__ import annotations

from enum import Enum
from typing import Any, Iterable, Mapping, Sequence


SCHEMA_VERSION = "itir.normalized.artifact.join.v1"
UNCERTAINTY_PRIORITY_RANK = {
    "follow_needed": 3,
    "hold": 2,
    "abstain": 2,
    "unknown": 1,
}

FOLLOW_STATUS_SET = {"follow_needed", "hold", "abstain"}


class JoinRelation(Enum):
    MATCH = "MATCH"
    LEFT_ONLY = "LEFT_ONLY"
    RIGHT_ONLY = "RIGHT_ONLY"
    CONFLICT = "CONFLICT"
    OVERRIDE = "OVERRIDE"
    EXCEPTION = "EXCEPTION"
    SUBSUMES = "SUBSUMES"
    OVERLAP = "OVERLAP"
    GAP = "GAP"
    UNRESOLVED = "UNRESOLVED"


MODALITY_ALIAS_MAP = {
    "allowed": "PERMIT",
    "allow": "PERMIT",
    "assert": "ASSERT",
    "asserted": "ASSERT",
    "forbid": "PROHIBIT",
    "forbidden": "PROHIBIT",
    "may": "PERMIT",
    "may_not": "PROHIBIT",
    "must": "REQUIRE",
    "must_not": "PROHIBIT",
    "must not": "PROHIBIT",
    "permit": "PERMIT",
    "permitted": "PERMIT",
    "prohibit": "PROHIBIT",
    "prohibited": "PROHIBIT",
    "require": "REQUIRE",
    "required": "REQUIRE",
    "shall": "REQUIRE",
    "shall_not": "PROHIBIT",
    "shall not": "PROHIBIT",
    "will": "ASSERT",
}
CONFLICTING_MODALITY_PAIRS = {
    ("ASSERT", "PROHIBIT"),
    ("PERMIT", "PROHIBIT"),
    ("PROHIBIT", "ASSERT"),
    ("PROHIBIT", "PERMIT"),
    ("PROHIBIT", "REQUIRE"),
    ("REQUIRE", "PROHIBIT"),
}


def _iter_mapping_surfaces(root: Mapping[str, Any]) -> Iterable[Mapping[str, Any]]:
    pending: list[Any] = [root]
    seen: set[int] = set()
    while pending:
        current = pending.pop()
        if not isinstance(current, Mapping):
            continue
        current_id = id(current)
        if current_id in seen:
            continue
        seen.add(current_id)
        yield current
        for value in current.values():
            if isinstance(value, Mapping):
                pending.append(value)
            elif isinstance(value, list):
                pending.extend(item for item in value if isinstance(item, Mapping))


def _first_string_value(artifact: Mapping[str, Any], keys: Sequence[str]) -> str:
    for surface in _iter_mapping_surfaces(artifact):
        for key in keys:
            value = surface.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return ""


def _first_int_value(artifact: Mapping[str, Any], keys: Sequence[str]) -> int | None:
    for surface in _iter_mapping_surfaces(artifact):
        for key in keys:
            value = surface.get(key)
            if isinstance(value, bool):
                continue
            if isinstance(value, int):
                return value
            if isinstance(value, str):
                stripped = value.strip()
                if stripped.lstrip("-").isdigit():
                    return int(stripped)
    return None


def _first_bool_value(artifact: Mapping[str, Any], keys: Sequence[str]) -> bool | None:
    for surface in _iter_mapping_surfaces(artifact):
        for key in keys:
            value = surface.get(key)
            if isinstance(value, bool):
                return value
            if isinstance(value, str):
                lowered = value.strip().lower()
                if lowered in {"true", "yes", "1"}:
                    return True
                if lowered in {"false", "no", "0"}:
                    return False
    return None


def _normalize_modality(raw: str) -> str:
    lowered = raw.strip().lower().replace("-", "_")
    return MODALITY_ALIAS_MAP.get(lowered, raw.strip().upper())


def _join_semantics_surface(artifact: Mapping[str, Any]) -> Mapping[str, Any]:
    surface = artifact.get("join_semantics")
    if isinstance(surface, Mapping):
        return surface
    return {}


def _append_evidence(evidence_ids: list[str], *items: str) -> None:
    for item in items:
        if item and item not in evidence_ids:
            evidence_ids.append(item)


def _preferred_string_value(
    artifact: Mapping[str, Any],
    semantic_keys: Sequence[str],
    legacy_keys: Sequence[str],
) -> tuple[str, str]:
    join_semantics = _join_semantics_surface(artifact)
    for key in semantic_keys:
        value = join_semantics.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip(), "join_semantics"
    for key in legacy_keys:
        value = artifact.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip(), "artifact"
    fallback = _first_string_value(artifact, legacy_keys)
    if fallback:
        return fallback, "fallback"
    return "", ""


def _preferred_int_value(
    artifact: Mapping[str, Any],
    semantic_keys: Sequence[str],
    legacy_keys: Sequence[str],
) -> tuple[int | None, str]:
    join_semantics = _join_semantics_surface(artifact)
    for key in semantic_keys:
        value = join_semantics.get(key)
        if isinstance(value, bool):
            continue
        if isinstance(value, int):
            return value, "join_semantics"
        if isinstance(value, str):
            stripped = value.strip()
            if stripped.lstrip("-").isdigit():
                return int(stripped), "join_semantics"
    for key in legacy_keys:
        value = artifact.get(key)
        if isinstance(value, bool):
            continue
        if isinstance(value, int):
            return value, "artifact"
        if isinstance(value, str):
            stripped = value.strip()
            if stripped.lstrip("-").isdigit():
                return int(stripped), "artifact"
    fallback = _first_int_value(artifact, legacy_keys)
    if fallback is not None:
        return fallback, "fallback"
    return None, ""


def _preferred_bool_value(
    artifact: Mapping[str, Any],
    semantic_keys: Sequence[str],
    legacy_keys: Sequence[str],
) -> tuple[bool | None, str]:
    join_semantics = _join_semantics_surface(artifact)
    for key in semantic_keys:
        value = join_semantics.get(key)
        if isinstance(value, bool):
            return value, "join_semantics"
        if isinstance(value, str):
            lowered = value.strip().lower()
            if lowered in {"true", "yes", "1"}:
                return True, "join_semantics"
            if lowered in {"false", "no", "0"}:
                return False, "join_semantics"
    for key in legacy_keys:
        value = artifact.get(key)
        if isinstance(value, bool):
            return value, "artifact"
        if isinstance(value, str):
            lowered = value.strip().lower()
            if lowered in {"true", "yes", "1"}:
                return True, "artifact"
            if lowered in {"false", "no", "0"}:
                return False, "artifact"
    fallback = _first_bool_value(artifact, legacy_keys)
    if fallback is not None:
        return fallback, "fallback"
    return None, ""


def _artifact_identity(artifact: Mapping[str, Any]) -> dict[str, str]:
    provenance_anchor = artifact.get("provenance_anchor")
    if not isinstance(provenance_anchor, Mapping):
        provenance_anchor = {}
    follow_obligation_present = artifact.get("follow_obligation") is not None
    raw_modality, modality_source = _preferred_string_value(
        artifact,
        ("modality",),
        ("modality", "mode", "obligation_modality"),
    )
    modality = _normalize_modality(raw_modality)
    priority_rank, priority_source = _preferred_int_value(
        artifact,
        ("priority_rank",),
        ("priority_rank", "priority_score", "priority", "precedence_rank"),
    )
    exception_active, exception_source = _preferred_bool_value(
        artifact,
        ("exception_active",),
        ("exception_active", "exception_applies", "exception_triggered", "is_exception"),
    )
    override_active, override_source = _preferred_bool_value(
        artifact,
        ("override_active",),
        ("override_active", "override_applies", "is_override"),
    )
    derived_flag = artifact.get("authority", {}).get("derived")
    follow_obligation = bool(artifact.get("follow_obligation"))
    return {
        "artifact_id": str(artifact.get("artifact_id") or ""),
        "artifact_role": str(artifact.get("artifact_role") or ""),
        "identity_class": str(
            artifact.get("canonical_identity", {}).get("identity_class") or ""
        ).strip(),
        "authority_class": str(artifact.get("authority", {}).get("authority_class") or "").strip(),
        "identity_key": str(
            artifact.get("canonical_identity", {}).get("identity_key") or ""
        ).strip(),
        "unresolved_pressure_status": str(
            artifact.get("unresolved_pressure_status") or "unknown"
        ).strip(),
        "lineage_key": "|".join(
            upstream
            for upstream in artifact.get("lineage", {}).get("upstream_artifact_ids") or []
            if isinstance(upstream, str)
        ),
        "derived_flag": "true" if derived_flag is True else "false" if derived_flag is False else "",
        "follow_obligation": "true" if follow_obligation else "false",
        "follow_obligation_present": "true" if follow_obligation_present else "false",
        "provenance_source_system": str(
            provenance_anchor.get("source_system") or ""
        ).strip(),
        "provenance_source_artifact_id": str(
            provenance_anchor.get("source_artifact_id") or ""
        ).strip(),
        "provenance_anchor_kind": str(provenance_anchor.get("anchor_kind") or "").strip(),
        "modality": modality if modality not in {"", "UNKNOWN"} else "",
        "modality_source": modality_source,
        "priority_rank": "" if priority_rank is None else str(priority_rank),
        "priority_source": priority_source,
        "exception_active": "true" if exception_active is True else "false",
        "exception_source": exception_source,
        "override_active": "true" if override_active is True else "false",
        "override_source": override_source,
    }


def _same_join_space(left: Mapping[str, str], right: Mapping[str, str]) -> bool:
    left_identity = left["identity_key"]
    right_identity = right["identity_key"]
    if left_identity and right_identity:
        return left_identity == right_identity
    return False


def _priority_rank(identity: Mapping[str, str]) -> int | None:
    raw = identity.get("priority_rank") or ""
    if raw.lstrip("-").isdigit():
        return int(raw)
    return None


def _override_by_priority_signal(left: Mapping[str, str], right: Mapping[str, str]) -> bool:
    if left["override_active"] == "true" or right["override_active"] == "true":
        return True
    left_priority = _priority_rank(left)
    right_priority = _priority_rank(right)
    if (
        left_priority is not None
        and right_priority is not None
        and left_priority != right_priority
    ):
        return True
    return False


def _exception_signal(left: Mapping[str, str], right: Mapping[str, str]) -> bool:
    if left["exception_active"] == "true" or right["exception_active"] == "true":
        return True
    if left["follow_obligation_present"] != right["follow_obligation_present"]:
        return True
    left_status = left["unresolved_pressure_status"]
    right_status = right["unresolved_pressure_status"]
    if (
        left_status in FOLLOW_STATUS_SET
        and right_status in FOLLOW_STATUS_SET
        and left_status != right_status
    ):
        return True
    return False


def _modality_conflicts(left: Mapping[str, str], right: Mapping[str, str]) -> bool:
    left_modality = left["modality"]
    right_modality = right["modality"]
    if not left_modality or not right_modality:
        return False
    return (left_modality, right_modality) in CONFLICTING_MODALITY_PAIRS


def _classify_join_relation(left: Mapping[str, str], right: Mapping[str, str]) -> JoinRelation:
    left_status = left["unresolved_pressure_status"]
    right_status = right["unresolved_pressure_status"]
    same_join_space = _same_join_space(left, right)
    conflict_candidate = (
        same_join_space
        and (
            left["authority_class"] != right["authority_class"]
            or (
                left_status in FOLLOW_STATUS_SET
                and right_status in FOLLOW_STATUS_SET
            )
        )
    )

    if same_join_space and _exception_signal(left, right):
        return JoinRelation.EXCEPTION
    if same_join_space and _modality_conflicts(left, right):
        left_priority = _priority_rank(left)
        right_priority = _priority_rank(right)
        if (
            left["override_active"] == "true"
            or right["override_active"] == "true"
            or (
                left_priority is not None
                and right_priority is not None
                and left_priority != right_priority
            )
        ):
            return JoinRelation.OVERRIDE
        return JoinRelation.CONFLICT
    if conflict_candidate:
        if _override_by_priority_signal(left, right):
            return JoinRelation.OVERRIDE
        return JoinRelation.CONFLICT
    if (
        left_status in {"hold", "abstain"}
        and right_status not in {"hold", "abstain", "follow_needed"}
    ):
        return JoinRelation.LEFT_ONLY
    if (
        right_status in {"hold", "abstain"}
        and left_status not in {"hold", "abstain", "follow_needed"}
    ):
        return JoinRelation.RIGHT_ONLY
    if bool(left["lineage_key"]) != bool(right["lineage_key"]):
        return JoinRelation.GAP
    if same_join_space and left["authority_class"] == right["authority_class"]:
        return JoinRelation.MATCH
    if (
        left["artifact_id"]
        and right["artifact_id"]
        and left["artifact_id"] == right["artifact_id"]
    ):
        return JoinRelation.MATCH
    if (
        left["artifact_role"]
        and right["artifact_role"]
        and left["artifact_role"] == right["artifact_role"]
        and left["authority_class"]
        and left["authority_class"] == right["authority_class"]
    ):
        return JoinRelation.MATCH
    return JoinRelation.UNRESOLVED


def _build_edge_relations(artifacts: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    edges: list[dict[str, Any]] = []
    identities = [_artifact_identity(artifact) for artifact in artifacts]
    for index, left_identity in enumerate(identities):
        for right_identity in identities[index + 1 :]:
            relation = _classify_join_relation(left_identity, right_identity)
            evidence_ids: list[str] = []
            _append_evidence(
                evidence_ids,
                f"left_artifact_id:{left_identity['artifact_id']}" if left_identity["artifact_id"] else "",
                f"right_artifact_id:{right_identity['artifact_id']}" if right_identity["artifact_id"] else "",
                f"left_artifact_role:{left_identity['artifact_role']}" if left_identity["artifact_role"] else "",
                f"right_artifact_role:{right_identity['artifact_role']}" if right_identity["artifact_role"] else "",
                f"left_identity_key:{left_identity['identity_key']}" if left_identity["identity_key"] else "",
                f"right_identity_key:{right_identity['identity_key']}" if right_identity["identity_key"] else "",
                f"left_identity_class:{left_identity['identity_class']}" if left_identity["identity_class"] else "",
                f"right_identity_class:{right_identity['identity_class']}" if right_identity["identity_class"] else "",
                f"left_authority_class:{left_identity['authority_class']}" if left_identity["authority_class"] else "",
                f"right_authority_class:{right_identity['authority_class']}" if right_identity["authority_class"] else "",
                f"left_lineage_key:{left_identity['lineage_key']}" if left_identity["lineage_key"] else "",
                f"right_lineage_key:{right_identity['lineage_key']}" if right_identity["lineage_key"] else "",
                f"left_pressure_status:{left_identity['unresolved_pressure_status']}" if left_identity["unresolved_pressure_status"] else "",
                f"right_pressure_status:{right_identity['unresolved_pressure_status']}" if right_identity["unresolved_pressure_status"] else "",
                f"left_follow_obligation:{left_identity['follow_obligation_present']}",
                f"right_follow_obligation:{right_identity['follow_obligation_present']}",
                f"left_derived_flag:{left_identity['derived_flag']}" if left_identity["derived_flag"] else "",
                f"right_derived_flag:{right_identity['derived_flag']}" if right_identity["derived_flag"] else "",
                f"left_provenance_source_system:{left_identity['provenance_source_system']}" if left_identity["provenance_source_system"] else "",
                f"right_provenance_source_system:{right_identity['provenance_source_system']}" if right_identity["provenance_source_system"] else "",
                f"left_provenance_source_artifact_id:{left_identity['provenance_source_artifact_id']}" if left_identity["provenance_source_artifact_id"] else "",
                f"right_provenance_source_artifact_id:{right_identity['provenance_source_artifact_id']}" if right_identity["provenance_source_artifact_id"] else "",
                f"left_provenance_anchor_kind:{left_identity['provenance_anchor_kind']}" if left_identity["provenance_anchor_kind"] else "",
                f"right_provenance_anchor_kind:{right_identity['provenance_anchor_kind']}" if right_identity["provenance_anchor_kind"] else "",
            )
            if (
                left_identity["identity_key"]
                and left_identity["identity_key"] == right_identity["identity_key"]
            ):
                _append_evidence(evidence_ids, f"same_identity:{left_identity['identity_key']}")
            if left_identity["modality"]:
                _append_evidence(evidence_ids, f"left_modality:{left_identity['modality']}")
            if left_identity["modality_source"]:
                _append_evidence(evidence_ids, f"left_modality_source:{left_identity['modality_source']}")
            if right_identity["modality"]:
                _append_evidence(evidence_ids, f"right_modality:{right_identity['modality']}")
            if right_identity["modality_source"]:
                _append_evidence(evidence_ids, f"right_modality_source:{right_identity['modality_source']}")
            if (
                left_identity["exception_active"] == "true"
                or right_identity["exception_active"] == "true"
            ):
                _append_evidence(evidence_ids, "exception_active")
            if left_identity["exception_source"]:
                _append_evidence(evidence_ids, f"left_exception_source:{left_identity['exception_source']}")
            if right_identity["exception_source"]:
                _append_evidence(evidence_ids, f"right_exception_source:{right_identity['exception_source']}")
            if left_identity["override_active"] == "true" or right_identity["override_active"] == "true":
                _append_evidence(evidence_ids, "override_active")
            if left_identity["override_source"]:
                _append_evidence(evidence_ids, f"left_override_source:{left_identity['override_source']}")
            if right_identity["override_source"]:
                _append_evidence(evidence_ids, f"right_override_source:{right_identity['override_source']}")
            if left_identity["priority_rank"]:
                _append_evidence(evidence_ids, f"left_priority:{left_identity['priority_rank']}")
            if left_identity["priority_source"]:
                _append_evidence(evidence_ids, f"left_priority_source:{left_identity['priority_source']}")
            if right_identity["priority_rank"]:
                _append_evidence(evidence_ids, f"right_priority:{right_identity['priority_rank']}")
            if right_identity["priority_source"]:
                _append_evidence(evidence_ids, f"right_priority_source:{right_identity['priority_source']}")
            edges.append(
                {
                    "left_artifact_id": left_identity["artifact_id"],
                    "right_artifact_id": right_identity["artifact_id"],
                    "relation": relation.value,
                    "evidence_ids": evidence_ids,
                }
            )
    return edges


def join_suite_normalized_artifacts(
    artifacts: Sequence[Mapping[str, Any]]
) -> dict[str, Any]:
    """
    Compose multiple suite-normalized artifacts into one read-only join view.

    The join preserves each artifact's identity, role, lineage, and unresolved pressure
    so callers can inspect multi-family provenance without reinterpretation.
    """
    artifact_ids = []
    artifact_roles = []
    authority_classes: list[str] = []
    lineage_ids: list[str] = []
    unresolved_status_counts: dict[str, int] = {}
    role_counts: dict[str, int] = {}
    incompatibility_flags: list[str] = []
    named_incompatibilities: list[dict[str, Any]] = []
    policy_summary: dict[str, int] = {}
    severity_summary: dict[str, int] = {}
    policy_guidance: dict[str, str] = {
        "non_derived_authority": "Review non-derived authority artifacts before trust.",
        "role_authority_mismatch": "Inspect role/authority mismatch before promoting."
    }
    dominant_disposition = "inspect"
    highest_severity = "info"
    severity_rank = {"info": 0, "warn": 1, "block": 2}

    def register_named_incompatibility(entry: dict[str, Any]) -> None:
        named_incompatibilities.append(entry)
        disposition = entry.get("disposition")
        if isinstance(disposition, str):
            policy_summary[disposition] = policy_summary.get(disposition, 0) + 1
        severity = entry.get("severity")
        if isinstance(severity, str):
            severity_summary[severity] = severity_summary.get(severity, 0) + 1

    for artifact in artifacts:
        artifact_id = str(artifact.get("artifact_id") or "")
        if artifact_id:
            artifact_ids.append(artifact_id)
        role = str(artifact.get("artifact_role") or "")
        if role:
            artifact_roles.append(role)
            role_counts[role] = role_counts.get(role, 0) + 1
        authority_class = str(artifact.get("authority", {}).get("authority_class") or "").strip()
        if authority_class:
            authority_classes.append(authority_class)
        upstream = artifact.get("lineage", {}).get("upstream_artifact_ids") or []
        for upstream_artifact in upstream:
            if isinstance(upstream_artifact, str) and upstream_artifact not in lineage_ids:
                lineage_ids.append(upstream_artifact)
        unresolved_status = str(artifact.get("unresolved_pressure_status") or "unknown")
        unresolved_status_counts[unresolved_status] = unresolved_status_counts.get(unresolved_status, 0) + 1
        derived_flag = artifact.get("authority", {}).get("derived")
        if derived_flag is False:
            incompatibility_flags.append(f"non_derived_authority:{artifact_id or role or 'unknown'}")
            named_incompatibilities.append(
                {
                    "code": "non_derived_authority",
                    "severity": "warn",
                    "artifacts": [artifact_id or role or "unknown"],
                    "reason": "Producer emitted a non-derived authority within a derived join.",
                    "disposition": "inspect",
                }
            )
            register_named_incompatibility(named_incompatibilities[-1])
        if role and authority_class and artifact.get("artifact_role") and not authority_class.startswith("derived"):
            incompatibility_flags.append(f"role_authority_mismatch:{role}")
            named_incompatibilities.append(
                {
                    "code": "role_authority_mismatch",
                    "severity": "warn",
                    "artifacts": [artifact_id or role],
                    "reason": "Artifact role does not align with authority classification.",
                    "disposition": "inspect",
                }
            )
            register_named_incompatibility(named_incompatibilities[-1])
    distinct_roles = sorted(set(artifact_roles))
    distinct_authority_classes = sorted(set(authority_classes))
    if len(distinct_roles) > 1:
        incompatibility_flags.append("mixed_roles")
    if len(distinct_authority_classes) > 1:
        incompatibility_flags.append("mixed_authority_classes")
    if unresolved_status_counts.get("follow_needed", 0) or unresolved_status_counts.get("hold", 0) or unresolved_status_counts.get("abstain", 0):
        incompatibility_flags.append("unresolved_pressure_present")
    if policy_summary:
        dominant_disposition = max(policy_summary, key=policy_summary.get)
    if severity_summary:
        highest_severity = max(
            severity_summary,
            key=lambda key: severity_rank.get(key, -1),
        )

    highest_uncertainty_status = max(
        unresolved_status_counts,
        key=lambda status: UNCERTAINTY_PRIORITY_RANK.get(status, 0),
        default=None,
    )
    highest_uncertainty_rank = UNCERTAINTY_PRIORITY_RANK.get(highest_uncertainty_status, 0)
    bounded_search_recommended = highest_uncertainty_rank >= 2

    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_role": "normalized_artifact_join",
        "artifact_id": f"normalized_join:{'-'.join(artifact_ids)}",
        "artifact_ids": artifact_ids,
        "roles": artifact_roles,
        "role_counts": role_counts,
        "authority_classes": authority_classes,
        "lineage": {"upstream_artifact_ids": lineage_ids},
        "unresolved_pressure_counts": unresolved_status_counts,
        "compatibility": {
            "distinct_roles": distinct_roles,
            "distinct_authority_classes": distinct_authority_classes,
            "contains_promoted_truth": "promoted_truth" in distinct_authority_classes,
            "contains_derived_artifacts": any(
                authority_class == "derived_inspection"
                for authority_class in distinct_authority_classes
            ),
            "incompatibility_flags": incompatibility_flags,
            "policy_summary": policy_summary,
            "severity_summary": severity_summary,
            "policy_guidance": policy_guidance,
            "named_incompatibilities": named_incompatibilities,
            "edge_relations": _build_edge_relations(artifacts),
            "dominant_disposition": dominant_disposition,
            "highest_severity": highest_severity,
            "uncertainty_surface": {
                "highest_status": highest_uncertainty_status,
                "priority_rank": highest_uncertainty_rank,
                "bounded_search_recommended": bounded_search_recommended,
            },
        },
        "artifacts": [dict(artifact) for artifact in artifacts],
    }
