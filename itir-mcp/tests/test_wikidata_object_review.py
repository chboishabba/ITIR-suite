from __future__ import annotations

import json

from itir_mcp import build_default_registry
from itir_mcp.wikidata_object_review import normalize_wikidata_objects, wikidata_object_review_bundle


def _simple_object() -> dict:
    return {
        "id": "Q42",
        "label": "Douglas Adams",
        "claims": {
            "P31": ["Q5"],
            "P106": [{"id": "Q36180", "label": "writer"}],
        },
    }


def _realish_object() -> dict:
    return {
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


def _assert_non_authority(payload: dict) -> None:
    assert payload["candidate_only"] is True
    assert payload["non_authoritative"] is True
    assert payload["promoted_claims"] is False
    assert payload["truth_claims"] is False
    assert payload["authority_boundary"]["promotion_authority"] is False


def test_normalize_wikidata_objects_accepts_single_list_and_dict_inputs() -> None:
    single = normalize_wikidata_objects(_simple_object())
    listed = normalize_wikidata_objects([_simple_object(), _realish_object()])
    keyed = normalize_wikidata_objects({"Q42": {"claims": {"P31": ["Q5"]}}})

    assert single["object_count"] == 1
    assert single["statement_count"] == 2
    assert single["objects"][0]["entity_id"] == "Q42"
    assert single["property_hints"] == ["P31", "P106"]
    assert single["class_hints"] == ["Q5"]
    assert single["statements"][0]["statement_id"] == "wikidata:Q42#P31:1"
    assert listed["object_count"] == 2
    assert "P14143" in listed["property_hints"]
    assert keyed["objects"][0]["entity_id"] == "Q42"


def test_normalize_wikidata_objects_compacts_real_wikidata_claim_shape() -> None:
    normalized = normalize_wikidata_objects(_realish_object())

    assert normalized["statement_count"] == 1
    statement = normalized["statements"][0]
    assert statement["statement_id"] == "wikidata:Q10403939$abc"
    assert "Climate change" in statement["fact"]
    assert "P14143" in statement["fact"]
    assert "Q123" in statement["fact"]
    assert statement["provenance_refs"] == ["wikidata:Q10403939$abc", "wikidata:ref:refhash1"]
    serialized = json.dumps(normalized, sort_keys=True)
    assert "mainsnak" not in serialized
    assert "datavalue" not in serialized


def test_wikidata_object_review_bundle_runs_requested_domain_lanes() -> None:
    bundle = wikidata_object_review_bundle(
        {
            "objects": [_realish_object()],
            "lanes": ["wikidata", "migration", "climate", "gwb"],
            "domain": "climate_nat",
        }
    )

    _assert_non_authority(bundle)
    assert bundle["version"] == "itir.wikidata.object_review_bundle.v1"
    assert bundle["object_count"] == 1
    assert bundle["statement_count"] == 1
    assert bundle["requested_lanes"] == ["wikidata", "migration", "climate", "gwb"]
    assert set(bundle["outputs"]) == {
        "wikidata_review_packet",
        "migration_candidate",
        "climate_claim_review",
        "gwb_follow_graph",
    }
    _assert_non_authority(bundle["outputs"]["wikidata_review_packet"])
    _assert_non_authority(bundle["outputs"]["migration_candidate"])
    _assert_non_authority(bundle["outputs"]["climate_claim_review"])
    _assert_non_authority(bundle["outputs"]["gwb_follow_graph"])
    assert bundle["outputs"]["climate_claim_review"]["claim_count"] == 1
    assert bundle["outputs"]["gwb_follow_graph"]["graph_kind"] == "candidate_follow_graph"
    assert "raw_text" not in json.dumps(bundle, sort_keys=True)


def test_wikidata_object_review_bundle_auto_selects_climate_lane_from_property_hint() -> None:
    bundle = wikidata_object_review_bundle({"object": _realish_object(), "lanes": "auto"})

    assert bundle["requested_lanes"] == ["wikidata", "migration", "climate"]
    assert "climate_claim_review" in bundle["outputs"]
    assert "gwb_follow_graph" not in bundle["outputs"]


def test_wikidata_object_review_bundle_registers_and_invokes_through_mcp_registry() -> None:
    registry = build_default_registry()
    result = registry.invoke("itir.wikidata.object_review_bundle", {"object": _simple_object()})

    assert result["ok"] is True
    bundle = result["result"]
    _assert_non_authority(bundle)
    assert bundle["outputs"]["wikidata_review_packet"]["fact_count"] == 2

    guarded = registry.safe_invoke("itir.wikidata.object_review_bundle", {"object": _simple_object()})
    assert guarded["ok"] is True
    assert guarded["result"]["decision"] == "abstained"
    assert guarded["result"]["authority_profile"]["tool_id"] == "itir.wikidata.object_review_bundle"
