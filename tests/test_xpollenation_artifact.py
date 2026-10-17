from __future__ import annotations

import json

import pytest

from itir_jmd_bridge.xpollenation_artifact import build_xpollenation_artifact


def _neighbourhood() -> dict:
    return {
        "schema": "dashi.xpollenation-neighbourhood/v1",
        "subject": {"namespace": "rhea", "identifier": "RHEA:19897"},
        "edges": [
            {
                "edgeId": "edge:b",
                "subject": {"namespace": "uniprot", "identifier": "P35228"},
                "relation": "candidate-neighbour",
                "object": {"namespace": "wikidata-qid", "identifier": "Q2"},
                "sourceRef": "qid",
                "sourceRevision": "rev",
                "acquisitionReceipt": "receipt:q",
                "status": "discovered",
                "sameObjectClaimed": False,
                "sameObjectVerified": False,
                "contextEquivalent": False,
                "promotionAllowed": False,
            },
            {
                "edgeId": "edge:a",
                "subject": {"namespace": "rhea", "identifier": "RHEA:19897"},
                "relation": "catalysed-by",
                "object": {"namespace": "uniprot", "identifier": "P35228"},
                "sourceRef": "rhea",
                "sourceRevision": "rev",
                "acquisitionReceipt": "receipt:u",
                "status": "identity-paid",
                "sameObjectClaimed": False,
                "sameObjectVerified": False,
                "contextEquivalent": False,
                "promotionAllowed": False,
            },
        ],
        "authority": "navigation-enrichment-only",
        "establishesProof": False,
        "establishesPayment": False,
    }


def test_build_xpollenation_artifact_is_logical_first_and_deterministic() -> None:
    first = build_xpollenation_artifact(_neighbourhood(), artifact_id="xpollenation:bh4:RHEA-19897")
    second = build_xpollenation_artifact(_neighbourhood(), artifact_id="xpollenation:bh4:RHEA-19897")

    assert first == second
    assert first["contractVersion"] == "shared-shard-artifact/v1"
    assert first["artifactClass"] == "xpollenation-neighbourhood"
    assert first["nonAuthority"]["promotionAuthority"] is False
    assert first["nonAuthority"]["proofAuthority"] is False
    shard = first["shards"][0]
    assert shard["shardId"] == "neighbourhood"
    assert shard["routingKeys"] == ["route-external=rhea:RHEA:19897"]
    assert shard["objectRefs"] == []
    payload = json.loads(first["embeddedPayloads"]["neighbourhood"])
    assert [edge["edgeId"] for edge in payload["edges"]] == ["edge:a", "edge:b"]
    assert payload["edges"][1]["subject"] == {"namespace": "uniprot", "identifier": "P35228"}
    assert shard["contentDigest"].startswith("sha256:")
    assert first["artifactRevision"] == shard["contentDigest"].split(":", 1)[1]


def test_build_xpollenation_artifact_rejects_authority_escalation() -> None:
    item = _neighbourhood()
    item["establishesProof"] = True
    with pytest.raises(ValueError, match="authority"):
        build_xpollenation_artifact(item, artifact_id="xpollenation:bad")


def test_build_xpollenation_artifact_rejects_edge_promotion() -> None:
    item = _neighbourhood()
    item["edges"][0]["promotionAllowed"] = True
    with pytest.raises(ValueError, match="promotion"):
        build_xpollenation_artifact(item, artifact_id="xpollenation:bad")
