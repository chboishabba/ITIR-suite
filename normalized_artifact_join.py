from __future__ import annotations

from typing import Any, Mapping, Sequence


SCHEMA_VERSION = "itir.normalized.artifact.join.v1"
UNCERTAINTY_PRIORITY_RANK = {
    "follow_needed": 3,
    "hold": 2,
    "abstain": 2,
    "unknown": 1,
}


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
