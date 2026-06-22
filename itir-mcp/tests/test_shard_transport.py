from __future__ import annotations

import pytest

from itir_mcp.shard_transport import (
    build_partial_graph_view,
    route_selector,
    validate_shared_shard_artifact,
)


def _tiny_manifest() -> dict[str, object]:
    return {
        "contractVersion": "shared-shard-artifact/v1",
        "artifactId": "demo-artifact",
        "artifactRevision": "2026-03-27T12:00:00Z+build-1",
        "artifactClass": "zelph-graph",
        "createdAtUtc": "2026-03-27T12:00:00Z",
        "buildProvenance": {
            "builder": "tests",
            "sourceInputs": ["fixture.json"],
        },
        "shards": [
            {
                "shardId": "left-0001",
                "section": "left",
                "logicalKind": "adjacency-bucket",
                "encoding": "json",
                "sizeBytes": 12,
                "contentDigest": "sha256:aaa",
                "routingKeys": ["direct-shard=left-0001", "route-left-node=Q1", "route-node=Q1"],
                "objectRefs": [
                    {
                        "sink": "hf",
                        "uri": "hf://datasets/example/demo/left-0001.json",
                        "sizeBytes": 12,
                        "contentDigest": "sha256:aaa",
                    }
                ],
            },
            {
                "shardId": "name-0001",
                "section": "nameOfNode",
                "logicalKind": "name-bucket",
                "encoding": "cbor",
                "sizeBytes": 14,
                "contentDigest": "sha256:bbb",
                "routingKeys": ["route-name=Alice", "route-lang=en"],
                "objectRefs": [
                    {
                        "sink": "ipfs",
                        "uri": "ipfs://bafyexample",
                        "sizeBytes": 14,
                        "contentDigest": "sha256:bbb",
                    }
                ],
            },
        ],
    }


def test_validate_shared_shard_artifact_accepts_tiny_manifest() -> None:
    normalized = validate_shared_shard_artifact(_tiny_manifest())
    assert normalized["contractVersion"] == "shared-shard-artifact/v1"
    assert [shard["shardId"] for shard in normalized["shards"]] == ["left-0001", "name-0001"]
    assert normalized["shards"][0]["objectRefs"][0]["sink"] == "hf"


def test_validate_shared_shard_artifact_rejects_missing_required_field() -> None:
    payload = _tiny_manifest()
    del payload["artifactRevision"]
    with pytest.raises(ValueError, match="artifactRevision is required"):
        validate_shared_shard_artifact(payload)


def test_route_selector_returns_logical_ids_only() -> None:
    ids = route_selector(_tiny_manifest(), "route-node=Q1")
    assert ids == ["left-0001"]
    assert all(not item.startswith("hf://") and not item.startswith("ipfs://") for item in ids)


def test_route_selector_accepts_generic_builder_routing_keys() -> None:
    payload = _tiny_manifest()
    payload["shards"][0]["routingKeys"] = ["section:left", "route-left-node"]
    ids = route_selector(payload, "route-left-node=Q1")
    assert ids == ["left-0001"]


def test_build_partial_graph_view_marks_non_authority() -> None:
    view = build_partial_graph_view(_tiny_manifest(), ["route-node=Q1", "route-name=Alice"])
    assert view["completeness"] == "partial"
    assert view["subset_of_artifact"] is True
    assert view["candidate_only"] is True
    assert view["diagnostic_only"] is True
    assert view["truth_authority"] is False
    assert view["support_authority"] is False
    assert view["admissibility_authority"] is False
    assert view["promotion_authority"] is False
    assert view["selected_shard_ids"] == ["left-0001", "name-0001"]
    assert view["selected_sections"] == ["left", "nameOfNode"]
    assert view["artifact_identity"]["artifactId"] == "demo-artifact"
    assert all("objectRefs" not in shard for shard in view["selected_shards"])


def test_validate_shared_shard_artifact_rejects_invalid_sink() -> None:
    payload = _tiny_manifest()
    payload["shards"][0]["objectRefs"][0]["sink"] = "s3"
    with pytest.raises(ValueError, match="sink must be one of hf, ipfs, file"):
        validate_shared_shard_artifact(payload)
