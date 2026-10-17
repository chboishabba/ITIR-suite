from __future__ import annotations

from itir_mcp.shard_transport import route_selector, validate_shared_shard_artifact


def _artifact() -> dict:
    return {
        "contractVersion": "shared-shard-artifact/v1",
        "artifactId": "xpollenation:bh4:RHEA-19897",
        "artifactRevision": "rev-1",
        "artifactClass": "xpollenation-neighbourhood",
        "createdAtUtc": "2026-10-17T00:00:00Z",
        "buildProvenance": {"builder": "fixture"},
        "shards": [
            {
                "shardId": "neighbourhood",
                "section": "neighbourhood",
                "logicalKind": "xpollenation-neighbourhood",
                "encoding": "json",
                "sizeBytes": 2,
                "contentDigest": "sha256:" + "a" * 64,
                "routingKeys": ["route-external=rhea:RHEA:19897"],
                "objectRefs": [],
            }
        ],
    }


def test_route_external_resolves_logical_shard_before_sink() -> None:
    artifact = validate_shared_shard_artifact(_artifact())
    assert artifact["shards"][0]["objectRefs"] == []
    assert route_selector(artifact, "route-external=rhea:RHEA:19897") == ["neighbourhood"]


def test_unmatched_external_coordinate_returns_no_shard() -> None:
    assert route_selector(_artifact(), "route-external=rhea:RHEA:11920") == []
