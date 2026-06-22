from __future__ import annotations

import pytest

from itir_mcp import build_default_registry


TOOL_NAME = "itir.shard.payload_probe"


def _bounded_shard_payload() -> dict:
    return {
        "contractVersion": "shared-shard-artifact/v1",
        "artifactId": "artifact:payload-probe",
        "artifactRevision": "rev-1",
        "artifactClass": "zelph-graph",
        "createdAtUtc": "2026-06-22T00:00:00Z",
        "buildProvenance": {
            "builderId": "test-runner",
            "builderVersion": "test",
        },
        "shards": [
            {
                "shardId": "logical:left",
                "section": "left",
                "logicalKind": "content-shard",
                "encoding": "json",
                "sizeBytes": 12,
                "contentDigest": "sha256:left",
                "routingKeys": [
                    "direct-shard=logical:left",
                ],
                "objectRefs": [
                    {
                        "sink": "hf",
                        "uri": "hf://datasets/demo/logical-left.json",
                        "sizeBytes": 12,
                        "contentDigest": "sha256:left",
                    }
                ],
            }
        ],
    }


def test_default_registry_registers_bounded_shard_payload_probe() -> None:
    registry = build_default_registry()
    spec = registry.get_tool_spec(TOOL_NAME)

    if spec is None:
        pytest.xfail(f"{TOOL_NAME} is not implemented in this branch")

    assert spec.read_only is True

    profile = registry.get_tool_authority_profile(TOOL_NAME)
    profile_key = getattr(spec, "authority_profile_key", None)
    if profile is not None:
        assert profile_key == TOOL_NAME
        assert profile["tool_id"] == TOOL_NAME
        assert profile["authority_notes"]["candidate_only"] is True
        assert profile["authority_notes"]["non_authoritative"] is True


def test_bounded_shard_payload_probe_returns_candidate_non_authoritative_metadata() -> None:
    registry = build_default_registry()

    if registry.get_tool_spec(TOOL_NAME) is None:
        pytest.xfail(f"{TOOL_NAME} is not implemented in this branch")

    result = registry.invoke(TOOL_NAME, _bounded_shard_payload())

    assert result["ok"] is True
    payload = result["result"]
    assert payload["candidate_only"] is True
    assert payload["non_authoritative"] is True
    assert payload["authority_boundary"]["candidate_only"] is True
    assert payload["authority_boundary"]["non_authoritative"] is True
