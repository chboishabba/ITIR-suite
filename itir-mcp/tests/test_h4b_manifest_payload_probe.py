from __future__ import annotations

from pathlib import Path

import pytest

from itir_mcp import build_default_registry
from itir_mcp.shard_transport import (
    build_bounded_payload_probe,
    build_shared_shard_contract_from_zelph_manifest,
    route_selector,
)


def _manifest(tmp_path: Path) -> dict:
    left = tmp_path / "left.capnp-packed"
    right = tmp_path / "right.capnp-packed"
    left.write_bytes(b"left-node-42-payload")
    right.write_bytes(b"right-node-99-payload")
    return {
        "manifestVersion": "zelph-hf-layout/v2",
        "createdAtUtc": "2026-06-22T00:00:00Z",
        "storageMode": "multi-object-shards",
        "source": {"artifactName": "zelph-h4b-proof", "binPath": "zelph-h4b-proof.bin"},
        "hfObjects": {
            "manifest": {"path": "hf://datasets/chbwa/zelph-sharded/minimal-proof/manifest.json"},
            "nodeRouteIndex": {
                "path": "hf://datasets/chbwa/zelph-sharded/minimal-proof/artifact.route.json",
                "sizeBytes": 128,
            },
        },
        "selectorModel": {
            "unit": "section-chunk",
            "supportedSections": ["left", "right"],
            "supportedOperations": ["headerProbe", "selectedChunkRead", "nodeRouteIndex"],
        },
        "sections": {
            "left": {
                "chunks": [
                    {
                        "chunkIndex": 0,
                        "length": left.stat().st_size,
                        "sourceOffset": 0,
                        "objectPath": str(left),
                    }
                ]
            },
            "right": {
                "chunks": [
                    {
                        "chunkIndex": 0,
                        "length": right.stat().st_size,
                        "sourceOffset": left.stat().st_size,
                        "objectPath": str(right),
                    }
                ]
            },
        },
    }


def test_h4b_manifest_contract_routes_sidecar_and_bounded_file_probe(tmp_path: Path) -> None:
    contract = build_shared_shard_contract_from_zelph_manifest(_manifest(tmp_path))
    route_index = {
        "routeVersion": "zelph-node-route/v1",
        "routing": {
            "left": [{"chunkIndex": 0, "which": "left", "entryCount": 1, "nodes": [42]}],
            "right": [{"chunkIndex": 0, "which": "right", "entryCount": 1, "nodes": [99]}],
        },
    }

    assert contract["contractVersion"] == "shared-shard-artifact/v1"
    assert contract["nonAuthority"]["promotion_authority"] is False
    assert contract["routingIndex"]["format"] == "zelph-node-route/v1"
    assert route_selector(contract, "route-left-node=42", route_index=route_index) == ["left-chunk-000000"]

    with pytest.raises(ValueError, match="exceeds max_bytes"):
        build_bounded_payload_probe(contract, selector="route-left-node=42", route_index=route_index, max_bytes=4)

    probe = build_bounded_payload_probe(
        contract,
        selector="route-left-node=42",
        route_index=route_index,
        max_bytes=4,
        allow_truncate=True,
    )
    assert probe["version"] == "itir.shard.payload_probe.v1"
    assert probe["shard_id"] == "left-chunk-000000"
    assert probe["bytes_read"] == 4
    assert probe["truncated"] is True
    assert probe["sample_preview_hex"] == b"left".hex()
    assert probe["candidate_only"] is True
    assert probe["non_authoritative"] is True
    assert probe["promotion_authority"] is False


def test_hf_manifest_contract_tool_accepts_supplied_manifest(tmp_path: Path) -> None:
    registry = build_default_registry()
    result = registry.invoke("itir.zelph.hf_manifest_contract", {"manifest": _manifest(tmp_path)})

    assert result["ok"] is True
    payload = result["result"]
    assert payload["version"] == "itir.zelph.hf_manifest_contract.v1"
    assert payload["contract"]["artifactId"] == "zelph-h4b-proof"
    assert payload["contract"]["nonAuthority"]["truth_authority"] is False
    assert payload["authority_boundary"]["non_authoritative"] is True
