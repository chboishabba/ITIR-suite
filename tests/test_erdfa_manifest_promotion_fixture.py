from __future__ import annotations

import json
from pathlib import Path


FIXTURE = Path("docs/planning/jmd_fixtures/erdfa_manifest_promotion_v1.example.json")


def test_erdfa_manifest_promotion_fixture_has_required_artifact_fields() -> None:
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))

    assert payload["contractVersion"] == "erdfa-manifest-promotion/v1"
    assert payload["artifactId"] == "wikidata-2026-demo"
    assert payload["artifactRevision"] == "rev-20260329-a"
    assert payload["artifactClass"] == "erdfa-shard-set"
    assert payload["buildProvenance"]["builder"] == "erdfa-publish-rs"


def test_erdfa_manifest_promotion_fixture_enriches_shard_refs() -> None:
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))

    first = payload["shards"][0]
    assert first["id"] == "left-bucket-001"
    assert first["logicalKind"] == "adjacency-bucket"
    assert first["encoding"] == "cbor"
    assert first["sizeBytes"] == 2048
    assert first["objectRefs"][0]["sink"] == "ipfs"
    assert "route-left-node=Q123" in first["routingKeys"]

    second = payload["shards"][1]
    assert second["id"] == "nodeOfName-en-017"
    assert "route-name=tenant" in second["routingKeys"]
    assert "route-lang=en" in second["routingKeys"]
