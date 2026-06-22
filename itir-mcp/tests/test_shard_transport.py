from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

import itir_mcp.shard_transport as shard_transport
from itir_mcp.shard_transport import (
    build_partial_graph_view,
    route_selector,
    validate_shared_shard_artifact,
)


FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures" / "shard_transport" / "shared_shard_artifact_v1.json"


def _fixture_manifest() -> dict[str, object]:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def _build_payload_probe(*args, **kwargs):
    probe_builder = getattr(shard_transport, "build_payload_probe", None)
    assert probe_builder is not None, "itir_mcp.shard_transport.build_payload_probe is not implemented"
    return probe_builder(*args, **kwargs)


def test_validate_shared_shard_artifact_accepts_tiny_manifest() -> None:
    normalized = validate_shared_shard_artifact(_fixture_manifest())
    assert normalized["contractVersion"] == "shared-shard-artifact/v1"
    assert [shard["shardId"] for shard in normalized["shards"]] == ["left-0001", "name-0001"]
    assert normalized["shards"][0]["objectRefs"][0]["sink"] == "hf"


def test_validate_shared_shard_artifact_rejects_missing_required_field() -> None:
    payload = _fixture_manifest()
    del payload["artifactRevision"]
    with pytest.raises(ValueError, match="artifactRevision is required"):
        validate_shared_shard_artifact(payload)


def test_route_selector_returns_logical_ids_only() -> None:
    ids = route_selector(_fixture_manifest(), "route-node=Q1")
    assert ids == ["left-0001"]
    assert all(not item.startswith("hf://") and not item.startswith("ipfs://") for item in ids)


def test_route_selector_accepts_generic_builder_routing_keys() -> None:
    payload = _fixture_manifest()
    payload["shards"][0]["routingKeys"] = ["section:left", "route-left-node"]
    ids = route_selector(payload, "route-left-node=Q1")
    assert ids == ["left-0001"]


def test_build_partial_graph_view_marks_non_authority() -> None:
    view = build_partial_graph_view(_fixture_manifest(), ["route-node=Q1", "route-name=Alice"])
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
    payload = _fixture_manifest()
    payload["shards"][0]["objectRefs"][0]["sink"] = "s3"
    with pytest.raises(ValueError, match="sink must be one of hf, ipfs, file"):
        validate_shared_shard_artifact(payload)


def test_build_payload_probe_returns_metadata_digest_and_sample_only() -> None:
    manifest = _fixture_manifest()
    selected_shard = build_partial_graph_view(manifest, ["direct-shard=left-0001"])["selected_shards"][0]
    payload_text = "probe-body-left-0001"

    probe = _build_payload_probe(
        selected_shard,
        payload_text,
        byte_cap=64,
        non_authority=dict(manifest["nonAuthority"]),
    )

    assert probe["version"] == "itir.shard.payload_probe.v1"
    assert probe["selected_shard_id"] == "left-0001"
    assert probe["byte_cap"] == 64
    assert probe["nonAuthority"] == manifest["nonAuthority"]
    assert probe["payload_metadata"] == {
        "byte_length": len(payload_text.encode("utf-8")),
        "truncated": False,
    }
    assert probe["payload_digest"] == "sha256:" + hashlib.sha256(payload_text.encode("utf-8")).hexdigest()
    assert probe["payload_sample"] == payload_text
    assert "payload" not in probe
    assert "objectRefs" not in json.dumps(probe, sort_keys=True)


def test_build_payload_probe_rejects_over_cap_unless_explicitly_truncated() -> None:
    manifest = _fixture_manifest()
    selected_shard = build_partial_graph_view(manifest, ["direct-shard=left-0001"])["selected_shards"][0]
    payload_text = "payload-body-that-exceeds-the-cap"

    with pytest.raises(ValueError, match="cap|truncate"):
        _build_payload_probe(
            selected_shard,
            payload_text,
            byte_cap=8,
            non_authority=dict(manifest["nonAuthority"]),
        )

    truncated = _build_payload_probe(
        selected_shard,
        payload_text,
        byte_cap=8,
        truncate=True,
        non_authority=dict(manifest["nonAuthority"]),
    )

    assert truncated["payload_metadata"] == {
        "byte_length": len(payload_text.encode("utf-8")),
        "truncated": True,
    }
    assert truncated["payload_sample"] == payload_text[:8]
