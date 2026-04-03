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
