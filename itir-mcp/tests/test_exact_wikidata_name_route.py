from __future__ import annotations

import pytest

from itir_mcp import build_default_registry
from itir_mcp.shard_transport import exact_wikidata_name_route, route_selector


def _contract() -> dict:
    return {
        "contractVersion": "shared-shard-artifact/v1",
        "artifactId": "wikidata-pinned-sample",
        "artifactRevision": "hf-commit-test-a",
        "artifactClass": "zelph-graph",
        "createdAtUtc": "2026-11-14T00:00:00Z",
        "buildProvenance": {"builderId": "test", "builderVersion": "v1"},
        "shards": [
            {
                "shardId": "nodeOfName-chunk-000001-wikidata",
                "section": "nodeOfName",
                "logicalKind": "name-chunk",
                "encoding": "capnp-packed",
                "sizeBytes": 1024,
                "contentDigest": "identity-sha256:fixture",
                "routingKeys": ["section:nodeOfName", "lang:wikidata", "route-name"],
                "objectRefs": [{"sink": "hf", "uri": "hf://datasets/acrion/zelph/fixture/shards/nodeOfName/chunk-000001-wikidata.capnp-packed", "sizeBytes": 1024, "contentDigest": "identity-sha256:fixture"}],
            },
            {
                "shardId": "nodeOfName-chunk-000002-en",
                "section": "nodeOfName",
                "logicalKind": "name-chunk",
                "encoding": "capnp-packed",
                "sizeBytes": 512,
                "contentDigest": "identity-sha256:fixture-en",
                "routingKeys": ["section:nodeOfName", "lang:en", "route-name"],
                "objectRefs": [{"sink": "hf", "uri": "hf://datasets/acrion/zelph/fixture/shards/nodeOfName/chunk-000002-en.capnp-packed", "sizeBytes": 512, "contentDigest": "identity-sha256:fixture-en"}],
            },
        ],
    }


def _route_index() -> dict:
    return {"routing": {"nodeOfName": [
        {"chunkIndex": 1, "lang": "wikidata", "names": ["Q207", "Q23505"]},
        {"chunkIndex": 2, "lang": "en", "names": ["Q207"]},
    ]}}


def test_strict_exact_wikidata_route_uses_language_and_artifact_local_chunk() -> None:
    r = exact_wikidata_name_route(_contract(), "Q207", route_index=_route_index())
    assert r["selected_shard_id"] == "nodeOfName-chunk-000001-wikidata"
    assert r["artifact_identity"]["artifactRevision"] == "hf-commit-test-a"
    assert r["chunkIndex"] == 1
    assert r["language"] == "wikidata"
    assert r["route_witness"] is True
    assert r["payload_fetch"] is False
    assert r["payload_decode"] is False
    assert r["query_coverage_complete"] is False
    assert not r["truth_authority"] and not r["promotion_authority"]


def test_exact_route_does_not_accept_generic_family_only_fallback() -> None:
    # Existing generic API is deliberately a broad planner.
    assert route_selector(_contract(), "route-name=Q99999")
    with pytest.raises(ValueError, match="unresolved or ambiguous"):
        exact_wikidata_name_route(_contract(), "Q99999", route_index=_route_index())


def test_exact_route_requires_external_pinned_sidecar() -> None:
    with pytest.raises(ValueError, match="explicit pinned route sidecar"):
        exact_wikidata_name_route(_contract(), "Q207", route_index=None)


def test_exact_route_cannot_misuse_english_language_entry() -> None:
    route = {"routing": {"nodeOfName": [{"chunkIndex": 2, "lang": "en", "names": ["Q207"]}]}}
    with pytest.raises(ValueError, match="unresolved or ambiguous"):
        exact_wikidata_name_route(_contract(), "Q207", route_index=route)


def test_exact_route_rejects_multiple_wikidata_matches() -> None:
    route = _route_index()
    route["routing"]["nodeOfName"].append({"chunkIndex": 1, "lang": "wikidata", "names": ["Q207"]})
    with pytest.raises(ValueError, match="unresolved or ambiguous"):
        exact_wikidata_name_route(_contract(), "Q207", route_index=route)


def test_exact_route_rejects_missing_physical_shard() -> None:
    route = {"routing": {"nodeOfName": [{"chunkIndex": 42, "lang": "wikidata", "names": ["Q207"]}]}}
    with pytest.raises(ValueError, match="missing indexed Wikidata name shard"):
        exact_wikidata_name_route(_contract(), "Q207", route_index=route)


@pytest.mark.parametrize("qid", ["Q0", "P207", "Q01", "Q-1", "Q207en", "Q２０７", ""])
def test_exact_route_validates_external_wikidata_qid(qid: str) -> None:
    with pytest.raises(ValueError, match="canonical nonzero Wikidata Q"):
        exact_wikidata_name_route(_contract(), qid, route_index=_route_index())


def test_exact_route_is_registered_read_only_mcp_tool() -> None:
    registry = build_default_registry()
    name = "itir.shard.exact_wikidata_name_route"
    spec = registry.get_tool_spec(name)
    assert spec is not None
    assert spec.read_only is True
    result = registry.invoke(name, {
        "contract": _contract(),
        "qid": "Q207",
        "route_index": _route_index(),
    })
    assert result["ok"] is True
    assert result["result"]["selected_shard_id"] == "nodeOfName-chunk-000001-wikidata"
    assert result["result"]["authority_boundary"]["non_authoritative"] is True
