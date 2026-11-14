"""Regression for the observed 2026 acrion/zelph HF v2 manifest ABI.

These are synthetic, shape-faithful fixtures based on the operator's manifest
readback, not an execution of the published HF blob.
"""
from __future__ import annotations

import pytest

from itir_mcp.shard_transport import (
    build_shared_shard_contract_from_zelph_manifest,
    validate_shared_shard_artifact,
)


def _manifest() -> dict:
    return {
        "manifestVersion": 2,
        "storageMode": "split-by-direction-and-section",
        "createdAtUtc": "2026-11-14T00:00:00Z",
        "source": {"artifactName": "wikidata-20260309-all"},
        "hfObjects": {"manifest": {"path": "hf://datasets/acrion/zelph/wikidata-20260309-all/wikidata-20260309-all.hf-v2.json"}},
        "selectorModel": {"unit": "section-chunk"},
        "sections": {"nodeOfName": {"chunks": [
            {
                "chunkIndex": 1,
                "lang": "wikidata",
                "length": 256,
                "objectPath": "hf://datasets/acrion/zelph/wikidata-20260309-all/shards/nodeOfName/chunk-000001-wikidata.capnp-packed",
            },
        ]}},
    }


def test_published_numeric_v2_manifest_normalises_to_existing_shared_shard_abi() -> None:
    manifest = _manifest()
    out = build_shared_shard_contract_from_zelph_manifest(
        manifest,
        artifact_revision="0d4bd670959ebddae72f70d973410fdea8917ec1",
    )
    validated = validate_shared_shard_artifact(out)
    assert validated["artifactRevision"] == "0d4bd670959ebddae72f70d973410fdea8917ec1"
    assert validated["buildProvenance"]["sourceManifestVersion"] == "zelph-hf-layout/v2"
    assert validated["shards"][0]["shardId"] == "nodeOfName-chunk-000001-wikidata"
    assert validated["shards"][0]["encoding"] == "capnp-packed"
    assert validated["shards"][0]["sizeBytes"] == 256
    assert validated["shards"][0]["objectRefs"][0]["sink"] == "hf"
    assert validated["shards"][0]["routingKeys"] == [
        "section:nodeOfName", "lang:wikidata", "route-name",
    ]


def test_itir_historical_string_version_still_normalises() -> None:
    manifest = _manifest()
    manifest["manifestVersion"] = "zelph-hf-layout/v2"
    out = build_shared_shard_contract_from_zelph_manifest(manifest)
    assert out["buildProvenance"]["sourceManifestVersion"] == "zelph-hf-layout/v2"


@pytest.mark.parametrize(
    ("version", "storage_mode"),
    [
        (2, None),
        (2, "single-file-offset-sidecar"),
        (3, "split-by-direction-and-section"),
        ("unexpected-version", "split-by-direction-and-section"),
        (True, "split-by-direction-and-section"),
    ],
)
def test_unknown_numeric_or_layout_contract_does_not_silently_normalise(
    version: object, storage_mode: str | None,
) -> None:
    manifest = _manifest()
    manifest["manifestVersion"] = version
    if storage_mode is None:
        del manifest["storageMode"]
    else:
        manifest["storageMode"] = storage_mode
    with pytest.raises(ValueError, match="unsupported Zelph manifestVersion"):
        build_shared_shard_contract_from_zelph_manifest(manifest)
