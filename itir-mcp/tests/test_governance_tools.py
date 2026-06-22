from __future__ import annotations

from itir_mcp import build_default_registry


def _shared_shard_artifact() -> dict:
    return {
        "contractVersion": "shared-shard-artifact/v1",
        "artifactId": "artifact:demo",
        "artifactRevision": "rev-1",
        "artifactClass": "zelph-graph",
        "createdAtUtc": "2026-06-22T00:00:00Z",
        "buildProvenance": {
            "builderId": "worker-3",
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
                    "route-node=node-a",
                ],
                "objectRefs": [
                    {
                        "sink": "hf",
                        "uri": "hf://datasets/demo/logical-left.json",
                        "sizeBytes": 12,
                        "contentDigest": "sha256:left",
                    }
                ],
            },
            {
                "shardId": "logical:right",
                "section": "right",
                "logicalKind": "content-shard",
                "encoding": "json",
                "sizeBytes": 24,
                "contentDigest": "sha256:right",
                "routingKeys": [
                    "route-name=right-name",
                ],
                "objectRefs": [
                    {
                        "sink": "ipfs",
                        "uri": "ipfs://bafybeigdemo",
                        "sizeBytes": 24,
                        "contentDigest": "sha256:right",
                    }
                ],
            },
        ],
    }


def test_default_registry_exposes_governance_and_shard_tools() -> None:
    registry = build_default_registry()
    names = {tool.name for tool in registry.list_tools()}

    assert {
        "itir.governance.tool_profiles",
        "itir.governance.validate_tool_profile",
        "itir.wikidata.tooling_profile",
        "itir.wikiproject.tooling_profile",
        "itir.zelph.transport_boundary",
        "itir.shard.validate_artifact",
        "itir.shard.route_selector",
        "itir.shard.partial_graph_view",
    }.issubset(names)


def test_governance_and_shard_tools_return_non_authoritative_logical_views() -> None:
    registry = build_default_registry()
    artifact = _shared_shard_artifact()

    profiles_result = registry.invoke("itir.governance.tool_profiles", {"tool_id": "itir_mcp"})
    assert profiles_result["ok"] is True
    profiles = profiles_result["result"]
    assert profiles["authority_boundary"]["non_authoritative"] is True
    assert [profile["tool_id"] for profile in profiles["profiles"]] == ["itir_mcp"]

    profile_result = registry.invoke(
        "itir.governance.validate_tool_profile",
        {"profile": profiles["profiles"][0]},
    )
    assert profile_result["ok"] is True
    validated_profile = profile_result["result"]
    assert validated_profile["authority_boundary"]["non_authoritative"] is True
    assert validated_profile["profile"]["tool_id"] == "itir_mcp"

    artifact_result = registry.invoke("itir.shard.validate_artifact", artifact)
    assert artifact_result["ok"] is True
    validated_artifact = artifact_result["result"]
    assert validated_artifact["authority_boundary"]["non_authoritative"] is True
    assert validated_artifact["logical_shard_ids"] == ["logical:left", "logical:right"]
    assert all("objectRefs" not in shard for shard in validated_artifact["logical_shards"])

    routed_result = registry.invoke("itir.shard.route_selector", {**artifact, "selector": "route-node=node-a"})
    assert routed_result["ok"] is True
    routed = routed_result["result"]
    assert routed["authority_boundary"]["non_authoritative"] is True
    assert routed["logical_shard_ids"] == ["logical:left"]

    partial_result = registry.invoke(
        "itir.shard.partial_graph_view",
        {**artifact, "selectors": ["direct-shard=logical:left", "route-name=right-name"]},
    )
    assert partial_result["ok"] is True
    partial = partial_result["result"]
    assert partial["authority_boundary"]["non_authoritative"] is True
    assert partial["selected_shard_ids"] == ["logical:left", "logical:right"]
    assert all("objectRefs" not in shard for shard in partial["selected_shards"])


def test_domain_governance_tools_return_candidate_only_read_only_summaries() -> None:
    registry = build_default_registry()

    wikidata_result = registry.invoke("itir.wikidata.tooling_profile", {})
    assert wikidata_result["ok"] is True
    wikidata = wikidata_result["result"]
    assert wikidata["version"] == "itir.wikidata.tooling_profile.v1"
    assert wikidata["domain"] == "wikidata"
    assert wikidata["candidate_only"] is True
    assert wikidata["non_authoritative"] is True
    assert wikidata["profile_ids"] == [
        "sensiblaw_review_packets",
        "entityschema",
        "listeria",
    ]
    assert wikidata["tooling_profile"]["kind"] == "tooling_profile"
    assert wikidata["tooling_profile"]["read_only"] is True
    assert wikidata["tooling_profile"]["non_authoritative"] is True
    assert wikidata["tooling_profile"]["candidate_only"] is True
    assert wikidata["tooling_profile"]["profiles"][0]["tool_id"] == "sensiblaw_review_packets"
    assert wikidata["tooling_profile"]["profiles"][1]["max_authority"] == "reviewed"

    wikiproject_result = registry.invoke("itir.wikiproject.tooling_profile", {})
    assert wikiproject_result["ok"] is True
    wikiproject = wikiproject_result["result"]
    assert wikiproject["version"] == "itir.wikiproject.tooling_profile.v1"
    assert wikiproject["domain"] == "wikiproject"
    assert wikiproject["candidate_only"] is True
    assert wikiproject["non_authoritative"] is True
    assert wikiproject["promotion_enabled"] is False
    assert wikiproject["authority_boundary"]["non_authoritative"] is True
    assert wikiproject["profile"]["W"]["B"]["canonical_truth_mutated"] is False
    assert wikiproject["profile"]["W"]["Pr"]["self_promotes"] is False
    assert "QuickStatements" in [tool["label"] for tool in wikiproject["profile"]["W"]["T"]]

    zelph_result = registry.invoke("itir.zelph.transport_boundary", {})
    assert zelph_result["ok"] is True
    zelph = zelph_result["result"]
    assert zelph["version"] == "itir.zelph.transport_boundary.v1"
    assert zelph["domain"] == "zelph"
    assert zelph["candidate_only"] is True
    assert zelph["non_authoritative"] is True
    assert zelph["profile_ids"] == ["zelph", "zelph_hf_shared_shards"]
    assert zelph["transport_boundary"]["kind"] == "transport_boundary"
    assert zelph["transport_boundary"]["read_only"] is True
    assert zelph["transport_boundary"]["mutates"] is False
    assert zelph["transport_boundary"]["max_authority"] == "receipt"
    assert [profile["tool_id"] for profile in zelph["transport_boundary"]["profiles"]] == [
        "zelph",
        "zelph_hf_shared_shards",
    ]
