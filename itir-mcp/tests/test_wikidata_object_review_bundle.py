from __future__ import annotations

from typing import Any, Mapping, Sequence

import pytest

from itir_mcp import ToolInputError, ToolRegistry, ToolSpec
from itir_mcp.domain_tools import climate_claim_review, gwb_follow_graph, wikidata_migration_candidate, wikidata_review_packet


def _registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(
        ToolSpec(
            name="itir.wikidata.object_review_bundle",
            title="ITIR Wikidata object review bundle",
            description="Compile a candidate-only review bundle from a Wikidata object, list, or dict input.",
            input_schema={
                "type": "object",
                "properties": {
                    "wikidata_object": {},
                    "lanes": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["wikidata_object"],
                "additionalProperties": True,
            },
            response_version="itir.wikidata.object_review_bundle.v1",
            read_only=True,
        ),
        _object_review_bundle,
    )
    return registry


def _object_review_bundle(payload: Mapping[str, Any]) -> dict[str, Any]:
    lanes = payload.get("lanes") or []
    if not isinstance(lanes, Sequence) or isinstance(lanes, (str, bytes, bytearray)):
        raise ToolInputError("lanes must be an array of strings")
    lane_names = [str(item).strip() for item in lanes if str(item).strip()]
    allowed_lanes = {"migration_candidate", "climate_claim_review", "gwb_follow_graph"}
    unknown = sorted(set(lane_names) - allowed_lanes)
    if unknown:
        raise ToolInputError(f"unknown lanes: {', '.join(unknown)}")

    objects = _normalize_wikidata_objects(payload.get("wikidata_object"))
    statements = _normalize_statements(objects)
    statement_refs = [statement["statement_id"] for statement in statements]
    object_ids = [item["id"] for item in objects]

    review_packet = wikidata_review_packet(
        {
            "statements": statements,
            "constraints": [
                {
                    "id": "bundle-candidate-only",
                    "status": "satisfied",
                    "severity": "info",
                    "message": "Candidate-only review bundle without truth or promotion authority.",
                    "candidate_refs": statement_refs,
                }
            ],
            "tooling_profile": {
                "tool_id": "itir.wikidata.object_review_bundle",
                "kind": "validation",
                "max_authority": "reviewed",
                "promotion_requires_gate": False,
                "candidate_only": True,
                "non_authoritative": True,
                "read_only": True,
                "authority_notes": {
                    "candidate_only": True,
                    "non_authoritative": True,
                    "no_truth": True,
                    "no_promoted": True,
                },
            },
        }
    )

    bundle: dict[str, Any] = {
        "version": "itir.wikidata.object_review_bundle.v1",
        "candidate_only": True,
        "non_authoritative": True,
        "truth_claims": False,
        "promoted_claims": False,
        "wikidata_review_packet": review_packet,
        "normalized_objects": objects,
        "normalized_statements": statements,
    }

    if "migration_candidate" in lane_names:
        bundle["migration_candidate"] = wikidata_migration_candidate(
            {
                "statement_refs": statement_refs,
                "property_hints": sorted({statement["property_ref"] for statement in statements}),
                "authority_label": "candidate-only",
            }
        )
    if "climate_claim_review" in lane_names:
        bundle["climate_claim_review"] = climate_claim_review(
            {
                "authority_label": "candidate-only",
                "claims": [
                    {
                        "claim_id": f"{object_ids[0]}#claim-1",
                        "normal_form": f"{object_ids[0]}:claims(candidate-only)",
                        "rendered_claim": f"{object_ids[0]} remains candidate-only in the bundle review.",
                        "candidate_status": "candidate",
                        "support_count": len(statements),
                        "contradiction_count": 0,
                    }
                ],
            }
        )
    if "gwb_follow_graph" in lane_names:
        bundle["gwb_follow_graph"] = gwb_follow_graph(
            {
                "authority_label": "candidate-only",
                "source_refs": statement_refs,
                "authority_refs": object_ids,
                "follow_edges": [
                    {
                        "edge_ref": f"{object_ids[0]}->bundle",
                        "source_ref": statement_refs[0],
                        "authority_ref": object_ids[0],
                        "relation": "follows",
                    }
                ],
            }
        )

    return bundle


def _normalize_wikidata_objects(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, Mapping):
        if "id" in value or "claims" in value:
            objects = [dict(value)]
        else:
            objects = []
            for key, item in value.items():
                if not isinstance(item, Mapping):
                    raise ToolInputError("dict inputs must contain Wikidata objects")
                candidate = dict(item)
                candidate.setdefault("id", str(key))
                objects.append(candidate)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        objects = [dict(item) for item in value if isinstance(item, Mapping)]
        if len(objects) != len(list(value)):
            raise ToolInputError("list inputs must contain Wikidata objects")
    else:
        raise ToolInputError("wikidata_object must be an object, list, or dict")

    if not objects:
        raise ToolInputError("wikidata_object must not be empty")

    normalized: list[dict[str, Any]] = []
    for item in objects:
        item_id = item.get("id")
        if not isinstance(item_id, str) or not item_id.strip():
            raise ToolInputError("each Wikidata object must include a non-empty id")
        claims = item.get("claims")
        if not isinstance(claims, Mapping) or not claims:
            raise ToolInputError("each Wikidata object must include claims")
        normalized.append({"id": item_id.strip(), "claims": dict(claims)})
    return normalized


def _normalize_statements(objects: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    statements: list[dict[str, Any]] = []
    for obj in objects:
        object_id = str(obj["id"]).strip()
        claims = obj["claims"]
        assert isinstance(claims, Mapping)
        for property_ref, claim_values in claims.items():
            items = claim_values if isinstance(claim_values, Sequence) and not isinstance(claim_values, (str, bytes, bytearray)) else [claim_values]
            for index, claim_value in enumerate(items, start=1):
                if isinstance(claim_value, Mapping):
                    fact = _claim_fact(object_id, property_ref, claim_value)
                    provenance_refs = [
                        ref
                        for ref in (
                            claim_value.get("provenance_ref"),
                            claim_value.get("provenance"),
                            claim_value.get("citation_ref"),
                        )
                        if isinstance(ref, str) and ref.strip()
                    ]
                else:
                    fact = f"{object_id} has {property_ref} {claim_value}"
                    provenance_refs = []
                statements.append(
                    {
                        "statement_id": f"{object_id}#{property_ref}#{index}",
                        "property_ref": str(property_ref).strip(),
                        "candidate_ref": object_id,
                        "fact": fact,
                        "provenance_refs": provenance_refs,
                    }
                )
    if not statements:
        raise ToolInputError("wikidata_object claims must yield at least one statement")
    return statements


def _claim_fact(object_id: str, property_ref: Any, claim_value: Mapping[str, Any]) -> str:
    for key in ("value", "label", "text", "rendered_claim", "summary", "mainsnak"):
        value = claim_value.get(key)
        if isinstance(value, str) and value.strip():
            return f"{object_id} has {property_ref} {value.strip()}"
        if isinstance(value, Mapping):
            nested = value.get("value")
            if isinstance(nested, str) and nested.strip():
                return f"{object_id} has {property_ref} {nested.strip()}"
    return f"{object_id} has {property_ref} candidate statement"


def _assert_candidate_only_bundle(bundle: Mapping[str, Any]) -> None:
    assert bundle["candidate_only"] is True
    assert bundle["non_authoritative"] is True
    assert bundle["truth_claims"] is False
    assert bundle["promoted_claims"] is False
    assert bundle["wikidata_review_packet"]["candidate_only"] is True
    assert bundle["wikidata_review_packet"]["truth_claims"] is False
    assert bundle["wikidata_review_packet"]["promoted_claims"] is False
    assert bundle["wikidata_review_packet"]["authority_boundary"]["promotion_authority"] is False
    assert bundle["wikidata_review_packet"]["authority_boundary"]["candidate_only"] is True
    assert bundle["wikidata_review_packet"]["authority_boundary"]["non_authoritative"] is True
    assert bundle["wikidata_review_packet"]["authority_boundary"]["read_only"] is True
    assert bundle["wikidata_review_packet"]["tooling_profile"]["authority_notes"]["no_truth"] is True
    assert bundle["wikidata_review_packet"]["tooling_profile"]["authority_notes"]["no_promoted"] is True


def test_object_review_bundle_normalizes_single_object_claims_into_review_packet() -> None:
    registry = _registry()

    result = registry.invoke(
        "itir.wikidata.object_review_bundle",
        {
            "wikidata_object": {
                "id": "Q42",
                "claims": {
                    "P31": [{"value": "human"}],
                    "P106": [{"label": "writer"}],
                },
            }
        },
    )

    assert result["ok"] is True
    bundle = result["result"]
    _assert_candidate_only_bundle(bundle)
    assert [item["statement_id"] for item in bundle["normalized_statements"]] == ["Q42#P31#1", "Q42#P106#1"]
    assert bundle["wikidata_review_packet"]["facts"][0]["candidate_ref"] == "Q42#P31#1"
    assert bundle["wikidata_review_packet"]["facts"][0]["fact"] == "Q42 has P31 human"
    assert bundle["wikidata_review_packet"]["constraint_diagnostics"][0]["candidate_refs"] == ["Q42#P31#1", "Q42#P106#1"]
    assert "migration_candidate" not in bundle
    assert "climate_claim_review" not in bundle
    assert "gwb_follow_graph" not in bundle


def test_object_review_bundle_accepts_list_and_dict_inputs_and_expands_requested_lanes() -> None:
    registry = _registry()

    list_result = registry.invoke(
        "itir.wikidata.object_review_bundle",
        {
            "wikidata_object": [
                {"id": "Q1", "claims": {"P31": [{"value": "thing"}]}},
                {"id": "Q2", "claims": {"P279": [{"label": "class"}]}},
            ],
            "lanes": ["migration_candidate", "climate_claim_review", "gwb_follow_graph"],
        },
    )
    dict_result = registry.invoke(
        "itir.wikidata.object_review_bundle",
        {
            "wikidata_object": {
                "Q3": {"claims": {"P31": [{"value": "item"}]}},
                "Q4": {"claims": {"P279": [{"label": "concept"}]}},
            },
            "lanes": ["migration_candidate"],
        },
    )

    for result in (list_result, dict_result):
        assert result["ok"] is True
        bundle = result["result"]
        _assert_candidate_only_bundle(bundle)
        assert bundle["wikidata_review_packet"]["packet_kind"] == "candidate_review_packet"
        assert bundle["wikidata_review_packet"]["authority_boundary"]["promotion_authority"] is False

    list_bundle = list_result["result"]
    assert set(list_bundle) >= {
        "version",
        "candidate_only",
        "non_authoritative",
        "wikidata_review_packet",
        "normalized_objects",
        "normalized_statements",
        "migration_candidate",
        "climate_claim_review",
        "gwb_follow_graph",
    }
    assert list_bundle["migration_candidate"]["candidate_only"] is True
    assert list_bundle["migration_candidate"]["promoted_claims"] is False
    assert list_bundle["migration_candidate"]["authority_boundary"]["promotion_authority"] is False
    assert list_bundle["climate_claim_review"]["candidate_only"] is True
    assert list_bundle["climate_claim_review"]["promoted_claims"] is False
    assert list_bundle["gwb_follow_graph"]["candidate_only"] is True
    assert list_bundle["gwb_follow_graph"]["promoted_claims"] is False

    dict_bundle = dict_result["result"]
    assert dict_bundle["migration_candidate"]["statement_refs"] == ["Q3#P31#1", "Q4#P279#1"]
    assert "climate_claim_review" not in dict_bundle
    assert "gwb_follow_graph" not in dict_bundle


def test_object_review_bundle_rejects_non_object_and_non_candidate_authority_creep() -> None:
    registry = _registry()

    invalid_shape = registry.invoke("itir.wikidata.object_review_bundle", {"wikidata_object": "Q42"})
    invalid_lanes = registry.invoke(
        "itir.wikidata.object_review_bundle",
        {"wikidata_object": {"id": "Q42", "claims": {"P31": [1]}}, "lanes": "migration_candidate"},
    )
    invalid_lane_name = registry.invoke(
        "itir.wikidata.object_review_bundle",
        {
            "wikidata_object": {"id": "Q42", "claims": {"P31": [{"value": "human"}]}},
            "lanes": ["truth"],
        },
    )

    assert invalid_shape["ok"] is False
    assert invalid_shape["error"]["message"] == "wikidata_object must be an object, list, or dict"
    assert invalid_lanes["ok"] is False
    assert invalid_lanes["error"]["message"] == "lanes must be an array of strings"
    assert invalid_lane_name["ok"] is False
    assert invalid_lane_name["error"]["message"] == "unknown lanes: truth"
