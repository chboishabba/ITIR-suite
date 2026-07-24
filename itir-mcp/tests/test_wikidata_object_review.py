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
    assert payload["authority_boundary"]["promotion_authority"] is False
    assert payload["authority_boundary"]["candidate_only"] is True
    assert payload["authority_boundary"]["non_authoritative"] is True


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


def test_wikidata_object_review_bundle_emits_generic_candidate_packet_only() -> None:
    bundle = wikidata_object_review_bundle(
        {
            "objects": [_realish_object()],
        }
    )

    _assert_non_authority(bundle)
    assert bundle["version"] == "itir.wikidata.object_review_bundle.v2"
    assert set(bundle) == {
        "version",
        "normalized_objects",
        "candidate_statements",
        "provenance_refs",
        "constraint_diagnostics",
        "shape_hints",
        "migration_candidates",
        "review_packet",
        "authority_boundary",
    }
    assert bundle["shape_hints"]["object_count"] == 1
    assert bundle["shape_hints"]["statement_count"] == 1
    assert bundle["review_packet"]["fact_count"] == 1
    assert bundle["migration_candidates"][0]["candidate_only"] is True
    assert bundle["migration_candidates"][0]["promoted_claims"] is False
    assert bundle["migration_candidates"][0]["truth_claims"] is False
    assert bundle["migration_candidates"][0]["authority_boundary"]["promotion_authority"] is False
    assert "raw_text" not in json.dumps(bundle, sort_keys=True)
    serialized = json.dumps(bundle, sort_keys=True)
    assert "requested_lanes" not in serialized
    assert "outputs" not in serialized
    assert "climate_claim_review" not in serialized
    assert "gwb_follow_graph" not in serialized


def test_wikidata_object_review_bundle_registers_and_invokes_through_mcp_registry() -> None:
    registry = build_default_registry()
    result = registry.invoke("itir.wikidata.object_review_bundle", {"object": _simple_object()})

    assert result["ok"] is True
    bundle = result["result"]
    _assert_non_authority(bundle)
    assert bundle["review_packet"]["fact_count"] == 2

    guarded = registry.safe_invoke("itir.wikidata.object_review_bundle", {"object": _simple_object()})
    assert guarded["ok"] is True
    assert guarded["result"]["decision"] == "abstained"
    assert guarded["result"]["authority_profile"]["tool_id"] == "itir.wikidata.object_review_bundle"
