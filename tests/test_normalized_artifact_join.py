from __future__ import annotations

import json
from pathlib import Path

import jsonschema

from normalized_artifact_join import join_suite_normalized_artifacts


def load_example_artifact(path: str) -> dict[str, object]:
    return json.loads(Path(path).read_text(encoding="utf-8"))  # type: ignore[no-any-return]


def load_join_schema() -> dict[str, object]:
    return json.loads(
        Path("schemas/itir.normalized.artifact.join.v1.schema.json").read_text(
            encoding="utf-8"
        )
    )


def find_edge(
    edges: list[dict[str, object]], left_id: str, right_id: str
) -> dict[str, object]:
    for edge in edges:
        if edge.get("left_artifact_id") == left_id and edge.get("right_artifact_id") == right_id:
            return edge
    raise AssertionError(f"missing edge {left_id} -> {right_id}")


def test_join_preserves_roles_and_lineage(tmp_path: Path) -> None:
    base = load_example_artifact("examples/itir.normalized_artifact.minimal.json")
    other = dict(base)
    other["artifact_id"] = "example:other"
    other["artifact_role"] = "example_secondary"
    other["lineage"] = {"upstream_artifact_ids": ["state.json"]}
    other["unresolved_pressure_status"] = "hold"
    other["authority"] = {"authority_class": "promoted_truth", "derived": True}

    joined = join_suite_normalized_artifacts([base, other])

    assert joined["schema_version"] == "itir.normalized.artifact.join.v1"
    assert joined["artifact_role"] == "normalized_artifact_join"
    assert joined["artifact_ids"] == [base["artifact_id"], other["artifact_id"]]
    assert joined["roles"] == [base["artifact_role"], other["artifact_role"]]
    assert joined["role_counts"][base["artifact_role"]] == 1
    assert joined["authority_classes"] == [base["authority"]["authority_class"], other["authority"]["authority_class"]]
    assert "state.json" in joined["lineage"]["upstream_artifact_ids"]
    assert joined["unresolved_pressure_counts"]["hold"] == 1
    assert "mixed_roles" in joined["compatibility"]["incompatibility_flags"]
    assert joined["compatibility"]["contains_promoted_truth"] is True
    assert joined["compatibility"]["contains_derived_artifacts"] is True
    assert any(flag.startswith("role_authority_mismatch") for flag in joined["compatibility"]["incompatibility_flags"])
    named = joined["compatibility"]["named_incompatibilities"]
    mismatch = next(item for item in named if item["code"] == "role_authority_mismatch")
    assert mismatch["severity"] == "warn"
    assert mismatch["disposition"] == "inspect"
    policy = joined["compatibility"]["policy_summary"]
    assert policy["inspect"] >= 1
    severity = joined["compatibility"]["severity_summary"]
    assert severity["warn"] >= 1
    guidance = joined["compatibility"]["policy_guidance"]
    assert guidance["role_authority_mismatch"].startswith("Inspect role")
    assert joined["compatibility"]["dominant_disposition"] == "inspect"
    assert joined["compatibility"]["highest_severity"] == "warn"
    assert isinstance(joined["artifacts"], list)
    uncertainty = joined["compatibility"]["uncertainty_surface"]
    assert uncertainty["highest_status"] == "follow_needed"
    assert uncertainty["priority_rank"] >= 2
    assert uncertainty["bounded_search_recommended"] is True
    jsonschema.validate(joined, load_join_schema())


def test_join_edge_classifications_are_exposed() -> None:
    base = load_example_artifact("examples/itir.normalized_artifact.minimal.json")
    base["artifact_id"] = "example:base"
    base["lineage"] = {"upstream_artifact_ids": []}
    base["unresolved_pressure_status"] = "none"
    variants = []

    match_variant = dict(base)
    match_variant["artifact_id"] = "example:match"
    variants.append(match_variant)

    conflict_variant = dict(base)
    conflict_variant["artifact_id"] = "example:conflict"
    conflict_variant["authority"] = {"authority_class": "promoted_truth", "derived": True}
    variants.append(conflict_variant)

    left_only_variant = dict(base)
    left_only_variant["artifact_id"] = "example:left_only"
    left_only_variant["unresolved_pressure_status"] = "hold"
    variants.append(left_only_variant)

    right_only_variant = dict(base)
    right_only_variant["artifact_id"] = "example:right_only"
    variants.append(right_only_variant)

    gap_variant = dict(base)
    gap_variant["artifact_id"] = "example:gap"
    gap_variant["lineage"] = {"upstream_artifact_ids": ["gap_state.json"]}
    variants.append(gap_variant)

    unresolved_variant = dict(base)
    unresolved_variant["artifact_id"] = "example:unresolved"
    unresolved_variant["canonical_identity"] = {
        "identity_class": "fact_review_run",
        "identity_key": "au-demo-run-unresolved",
    }
    variants.append(unresolved_variant)

    joined = join_suite_normalized_artifacts([base, *variants])

    edges = joined["compatibility"].get("edge_relations")
    assert isinstance(edges, list), "edge_relations must be present for relation-first joins"
    relation_names = {edge.get("relation") for edge in edges if edge}
    expected_relations = {"MATCH", "LEFT_ONLY", "RIGHT_ONLY", "CONFLICT", "GAP", "UNRESOLVED"}
    assert expected_relations.issubset(relation_names), "edge relations should cover the representative lattice cases"
    assert any(edge.get("left_artifact_id") for edge in edges), "at least one edge should record a left artifact identifier"
    assert any(edge.get("right_artifact_id") for edge in edges), "at least one edge should record a right artifact identifier"
    jsonschema.validate(joined, load_join_schema())


def test_join_edge_prefers_exception_then_override_then_conflict() -> None:
    prohibit = load_example_artifact("examples/itir.normalized_artifact.minimal.json")
    prohibit["artifact_id"] = "example:prohibit"
    prohibit["canonical_identity"] = {
        "identity_class": "fact_review_run",
        "identity_key": "au-demo-run-semantic",
    }
    prohibit["join_semantics"] = {
        "modality": "must not",
        "priority_rank": 1,
        "exception_active": False,
        "override_active": False,
    }
    prohibit["unresolved_pressure_status"] = "none"

    exception_variant = dict(prohibit)
    exception_variant["artifact_id"] = "example:exception"
    exception_variant["join_semantics"] = {
        "modality": "must",
        "priority_rank": 9,
        "exception_active": True,
        "override_active": True,
    }

    override_variant = dict(prohibit)
    override_variant["artifact_id"] = "example:override"
    override_variant["join_semantics"] = {
        "modality": "must",
        "priority_rank": 9,
        "exception_active": False,
        "override_active": True,
    }

    conflict_variant = dict(prohibit)
    conflict_variant["artifact_id"] = "example:conflict_modality"
    conflict_variant["join_semantics"] = {
        "modality": "must",
        "priority_rank": 1,
        "exception_active": False,
        "override_active": False,
    }

    joined = join_suite_normalized_artifacts(
        [prohibit, exception_variant, override_variant, conflict_variant]
    )

    edges = joined["compatibility"]["edge_relations"]
    assert isinstance(edges, list)

    exception_edge = find_edge(edges, "example:prohibit", "example:exception")
    assert exception_edge["relation"] == "EXCEPTION"
    assert "left_artifact_id:example:prohibit" in exception_edge["evidence_ids"]
    assert "right_artifact_id:example:exception" in exception_edge["evidence_ids"]
    assert "exception_active" in exception_edge["evidence_ids"]
    assert "override_active" in exception_edge["evidence_ids"]
    assert "right_exception_source:join_semantics" in exception_edge["evidence_ids"]
    assert "left_provenance_source_system:SensibLaw" in exception_edge["evidence_ids"]
    assert "right_provenance_source_artifact_id:au-fact-review-bundle-001" in exception_edge["evidence_ids"]

    override_edge = find_edge(edges, "example:prohibit", "example:override")
    assert override_edge["relation"] == "OVERRIDE"
    assert "left_priority:0" not in override_edge["evidence_ids"]
    assert "right_priority:9" in override_edge["evidence_ids"]
    assert "right_priority_source:join_semantics" in override_edge["evidence_ids"]
    assert "right_override_source:join_semantics" in override_edge["evidence_ids"]

    conflict_edge = find_edge(edges, "example:prohibit", "example:conflict_modality")
    assert conflict_edge["relation"] == "CONFLICT"
    assert "left_modality:PROHIBIT" in conflict_edge["evidence_ids"]
    assert "right_modality:REQUIRE" in conflict_edge["evidence_ids"]
    assert "left_modality_source:join_semantics" in conflict_edge["evidence_ids"]
    assert "right_modality_source:join_semantics" in conflict_edge["evidence_ids"]

    jsonschema.validate(joined, load_join_schema())


def test_join_semantics_takes_precedence_over_legacy_metadata() -> None:
    left = load_example_artifact("examples/itir.normalized_artifact.minimal.json")
    left["artifact_id"] = "example:left-preferred"
    left["canonical_identity"] = {
        "identity_class": "fact_review_run",
        "identity_key": "au-demo-run-preferred",
    }
    left["join_semantics"] = {
        "modality": "must not",
        "priority_rank": 3,
        "exception_active": False,
        "override_active": False,
    }
    left["modality"] = "must"
    left["priority_rank"] = 99
    left["exception_active"] = True
    left["unresolved_pressure_status"] = "none"

    right = dict(left)
    right["artifact_id"] = "example:right-preferred"
    right["join_semantics"] = {
        "modality": "must",
        "priority_rank": 3,
        "exception_active": False,
        "override_active": False,
    }
    right["modality"] = "must not"
    right["priority_rank"] = 1
    right["exception_active"] = False

    joined = join_suite_normalized_artifacts([left, right])
    edges = joined["compatibility"]["edge_relations"]
    assert isinstance(edges, list)

    edge = find_edge(edges, "example:left-preferred", "example:right-preferred")
    assert edge["relation"] == "CONFLICT"
    assert "left_artifact_id:example:left-preferred" in edge["evidence_ids"]
    assert "right_artifact_id:example:right-preferred" in edge["evidence_ids"]
    assert "same_identity:au-demo-run-preferred" in edge["evidence_ids"]
    assert "left_modality:PROHIBIT" in edge["evidence_ids"]
    assert "right_modality:REQUIRE" in edge["evidence_ids"]
    assert "left_modality_source:join_semantics" in edge["evidence_ids"]
    assert "right_modality_source:join_semantics" in edge["evidence_ids"]
    assert "left_priority:3" in edge["evidence_ids"]
    assert "right_priority:3" in edge["evidence_ids"]
    assert "left_priority_source:join_semantics" in edge["evidence_ids"]
    assert "right_priority_source:join_semantics" in edge["evidence_ids"]
    assert "exception_active" not in edge["evidence_ids"]


def _artifact_variant(
    base: dict[str, object],
    artifact_id: str,
    identity_key: str,
    authority_class: str,
    unresolved_pressure_status: str,
    derived: bool,
    lineage: list[str],
) -> dict[str, object]:
    variant = json.loads(json.dumps(base))
    variant["artifact_id"] = artifact_id
    variant.setdefault("authority", {})["authority_class"] = authority_class
    variant["authority"]["derived"] = derived
    variant["canonical_identity"] = {
        "identity_class": "fact_review_run",
        "identity_key": identity_key,
    }
    variant["unresolved_pressure_status"] = unresolved_pressure_status
    variant["lineage"] = {"upstream_artifact_ids": lineage}
    return variant


def test_edge_relations_document_conflict_override_exception_scenarios() -> None:
    base = load_example_artifact("examples/itir.normalized_artifact.minimal.json")
    base["artifacts"] = base.get("artifacts", [])

    conflict_a = _artifact_variant(
        base,
        "example:conflict_primary",
        "shared-identity-1",
        "promoted_truth",
        "follow_needed",
        derived=False,
        lineage=["conflict.bundle"],
    )
    conflict_b = _artifact_variant(
        base,
        "example:conflict_secondary",
        "shared-identity-1",
        "derived_inspection",
        "follow_needed",
        derived=True,
        lineage=["conflict.bundle"],
    )

    override_primary = _artifact_variant(
        base,
        "example:override_primary",
        "shared-identity-override",
        "promoted_truth",
        "follow_needed",
        derived=False,
        lineage=["override.bundle"],
    )
    override_secondary = _artifact_variant(
        base,
        "example:override_secondary",
        "shared-identity-override",
        "derived_inspection",
        "follow_needed",
        derived=True,
        lineage=["override.bundle"],
    )
    override_primary["join_semantics"] = {
        "modality": "must not",
        "priority_rank": 9,
        "exception_active": False,
        "override_active": True,
    }
    override_secondary["join_semantics"] = {
        "modality": "must",
        "priority_rank": 1,
        "exception_active": False,
        "override_active": False,
    }

    exception_primary = _artifact_variant(
        base,
        "example:exception_primary",
        "shared-identity-exception",
        "derived_inspection",
        "abstain",
        derived=True,
        lineage=["exception.bundle-a"],
    )
    exception_secondary = _artifact_variant(
        base,
        "example:exception_secondary",
        "shared-identity-exception",
        "derived_inspection",
        "follow_needed",
        derived=True,
        lineage=["exception.bundle-b"],
    )

    joined = join_suite_normalized_artifacts(
        [
            conflict_a,
            conflict_b,
            override_primary,
            override_secondary,
            exception_primary,
            exception_secondary,
        ]
    )

    edges = joined["compatibility"].get("edge_relations", [])
    assert isinstance(edges, list)
    edge_map: dict[frozenset[str], dict[str, object]] = {}
    for edge in edges:
        left = edge.get("left_artifact_id")
        right = edge.get("right_artifact_id")
        if left and right:
            edge_map[frozenset({left, right})] = edge

    conflict_relation = edge_map.get(frozenset({conflict_a["artifact_id"], conflict_b["artifact_id"]}))
    assert conflict_relation is not None
    assert conflict_relation["relation"] == "CONFLICT"
    assert "left_authority_class:promoted_truth" in conflict_relation["evidence_ids"]
    assert "right_authority_class:derived_inspection" in conflict_relation["evidence_ids"]

    override_edge = edge_map.get(frozenset({override_primary["artifact_id"], override_secondary["artifact_id"]}))
    assert override_edge is not None
    assert override_edge["relation"] == "OVERRIDE"
    assert "override_active" in override_edge["evidence_ids"]
    assert override_primary["authority"]["authority_class"] == "promoted_truth"
    assert override_secondary["authority"]["authority_class"] == "derived_inspection"

    exception_edge = edge_map.get(frozenset({exception_primary["artifact_id"], exception_secondary["artifact_id"]}))
    assert exception_edge is not None
    assert exception_edge["relation"] == "EXCEPTION"
    assert "left_pressure_status:abstain" in exception_edge["evidence_ids"]
    assert "right_pressure_status:follow_needed" in exception_edge["evidence_ids"]
    assert exception_primary["unresolved_pressure_status"] == "abstain"
    assert exception_secondary["unresolved_pressure_status"] == "follow_needed"

    jsonschema.validate(joined, load_join_schema())
