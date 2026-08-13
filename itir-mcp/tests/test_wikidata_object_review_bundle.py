from __future__ import annotations

import json
from typing import Any, Mapping

from itir_mcp import build_default_registry


def _registry_result(payload: Mapping[str, Any]) -> dict[str, Any]:
    registry = build_default_registry()
    result = registry.invoke("itir.wikidata.object_review_bundle", dict(payload))
    assert result["ok"] is True
    return result["result"]


def _assert_candidate_only_bundle(bundle: Mapping[str, Any]) -> None:
    assert bundle["version"] == "itir.wikidata.object_review_bundle.v2"
    assert bundle["authority_boundary"]["read_only"] is True
    assert bundle["authority_boundary"]["candidate_only"] is True
    assert bundle["authority_boundary"]["non_authoritative"] is True
    assert bundle["authority_boundary"]["promotion_authority"] is False
    assert bundle["review_packet"]["candidate_only"] is True
    assert bundle["review_packet"]["truth_claims"] is False
    assert bundle["review_packet"]["promoted_claims"] is False
    assert bundle["migration_candidates"][0]["candidate_only"] is True
    assert bundle["migration_candidates"][0]["truth_claims"] is False
    assert bundle["migration_candidates"][0]["promoted_claims"] is False


def test_object_review_bundle_normalizes_single_object_claims_into_review_packet() -> None:
    bundle = _registry_result(
        {
            "wikidata_object": {
                "id": "Q42",
                "claims": {
                    "P31": [{"value": "human"}],
                    "P106": [{"label": "writer"}],
                },
            }
        }
    )

    _assert_candidate_only_bundle(bundle)
    assert [item["statement_id"] for item in bundle["candidate_statements"]] == [
        "wikidata:Q42#P31:1",
        "wikidata:Q42#P106:1",
    ]
    assert bundle["review_packet"]["facts"][0]["candidate_ref"] == "wikidata:Q42#P31:1"
    assert bundle["review_packet"]["facts"][0]["fact"] == "Q42 has P31 human"
    assert bundle["constraint_diagnostics"][0]["candidate_refs"] == [
        "wikidata:Q42#P31:1",
        "wikidata:Q42#P106:1",
    ]


def test_object_review_bundle_accepts_list_and_qid_keyed_dict_inputs() -> None:
    list_bundle = _registry_result(
        {
            "wikidata_objects": [
                {"id": "Q1", "claims": {"P31": ["Q35120"]}},
                {"id": "Q2", "claims": {"P279": [{"id": "Q16889133", "label": "class"}]}},
            ]
        }
    )
    dict_bundle = _registry_result(
        {
            "entities": {
                "Q3": {"claims": {"P31": ["Q5"]}},
                "Q4": {"claims": {"P279": [{"id": "Q7184903", "label": "abstract object"}]}},
            }
        }
    )

    _assert_candidate_only_bundle(list_bundle)
    _assert_candidate_only_bundle(dict_bundle)
    assert list_bundle["shape_hints"]["input_shape"] == "list"
    assert list_bundle["shape_hints"]["object_count"] == 2
    assert dict_bundle["shape_hints"]["input_shape"] == "dict"
    assert [item["entity_id"] for item in dict_bundle["normalized_objects"]] == ["Q3", "Q4"]
    assert dict_bundle["migration_candidates"][0]["statement_refs"] == [
        "wikidata:Q3#P31:1",
        "wikidata:Q4#P279:1",
    ]


def test_object_review_bundle_keeps_realish_claim_shapes_compact_and_generic() -> None:
    bundle = _registry_result(
        {
            "object": {
                "id": "Q10403939",
                "labels": {"en": {"language": "en", "value": "Climate change"}},
                "claims": {
                    "P14143": [
                        {
                            "id": "Q10403939$abc",
                            "mainsnak": {
                                "snaktype": "value",
                                "property": "P14143",
                                "datavalue": {
                                    "type": "wikibase-entityid",
                                    "value": {"entity-type": "item", "numeric-id": 123, "id": "Q123"},
                                },
                            },
                            "references": [{"hash": "refhash1"}],
                        }
                    ]
                },
            }
        }
    )

    _assert_candidate_only_bundle(bundle)
    assert bundle["candidate_statements"][0]["statement_id"] == "wikidata:Q10403939$abc"
    assert bundle["provenance_refs"] == ["wikidata:Q10403939$abc", "wikidata:ref:refhash1"]
    serialized = json.dumps(bundle, sort_keys=True)
    assert "mainsnak" not in serialized
    assert "datavalue" not in serialized
    assert "lanes" not in serialized
    assert "requested_lanes" not in serialized
    assert "outputs" not in serialized
    assert "climate_claim_review" not in serialized
    assert "gwb_follow_graph" not in serialized


def test_object_review_bundle_rejects_non_object_input_without_lane_validation() -> None:
    registry = build_default_registry()

    invalid_shape = registry.invoke("itir.wikidata.object_review_bundle", {"wikidata_object": "Q42"})
    with_legacy_lane_property = registry.invoke(
        "itir.wikidata.object_review_bundle",
        {"wikidata_object": {"id": "Q42", "claims": {"P31": [1]}}, "lanes": ["truth"], "domain": "gwb"},
    )

    assert invalid_shape["ok"] is False
    assert invalid_shape["error"]["message"] == "Wikidata object input must be an object, list, or dict of objects"
    assert with_legacy_lane_property["ok"] is True
    assert "lanes" not in json.dumps(with_legacy_lane_property["result"], sort_keys=True)
    assert "gwb_follow_graph" not in json.dumps(with_legacy_lane_property["result"], sort_keys=True)
