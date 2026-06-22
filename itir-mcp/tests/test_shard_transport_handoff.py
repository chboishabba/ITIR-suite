from __future__ import annotations

import json
from pathlib import Path

from itir_mcp.shard_transport import build_partial_graph_view, route_selector, validate_shared_shard_artifact


FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures" / "shard_transport" / "shared_shard_artifact_v1.json"


def _fixture() -> dict[str, object]:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def _normalized_transport_view(manifest: dict[str, object], selectors: list[str]) -> dict[str, object]:
    artifact = validate_shared_shard_artifact(manifest)
    view = build_partial_graph_view(manifest, selectors)
    return {
        "schema_version": "itir.normalized.artifact.v1",
        "artifact_role": "transport_view",
        "artifact_id": view["artifact_identity"]["artifactId"],
        "canonical_identity": {
            "identity_class": "zelph_shard_transport",
            "identity_key": f'{artifact["artifactClass"]}:{artifact["artifactId"]}:{artifact["artifactRevision"]}',
            "aliases": [
                artifact["artifactId"],
                artifact["artifactRevision"],
                artifact["artifactClass"],
            ],
        },
        "provenance_anchor": {
            "source_system": artifact["buildProvenance"]["sourceSystem"],
            "source_artifact_id": artifact["artifactId"],
            "anchor_kind": "zelph_shard_transport",
            "anchor_ref": "semantic_context.suite_normalized_artifact",
        },
        "context_envelope_ref": {
            "envelope_id": artifact["artifactId"],
            "envelope_kind": "zelph_shard_transport",
        },
        "authority": {
            "authority_class": "transport_view",
            "candidate": True,
            "derived": True,
            "transport_only": True,
            "promotion_receipt_ref": None,
        },
        "nonAuthority": dict(manifest["nonAuthority"]),
        "lineage": {
            "upstream_artifact_ids": ["wikidata:Q1", "wikidata:P31"],
            "build_provenance": dict(artifact["buildProvenance"]),
            "artifact_revision": artifact["artifactRevision"],
            "artifact_class": artifact["artifactClass"],
        },
        "invariants": {
            "partial_view": True,
            "subset_of_artifact": True,
            "complete_closure": False,
            "truth_authority": False,
            "promotion_authority": False,
        },
        "selectors": list(view["selectors"]),
        "route_selectors": list(view["selectors"]),
        "selected_shard_ids": list(view["selected_shard_ids"]),
        "selected_sections": list(view["selected_sections"]),
        "summary": {
            "artifact_class": artifact["artifactClass"],
            "artifact_revision": artifact["artifactRevision"],
            "source_system": artifact["buildProvenance"]["sourceSystem"],
            "partial_view": True,
            "partial_load": True,
            "candidate_only": True,
            "selector_count": len(view["selectors"]),
            "route_selector_count": len(view["selectors"]),
            "selected_shard_count": len(view["selected_shard_ids"]),
            "selected_section_count": len(view["selected_sections"]),
        },
    }


def test_wikidata_zelph_handoff_fixture_round_trips_through_shard_transport() -> None:
    manifest = _fixture()

    normalized = validate_shared_shard_artifact(manifest)
    assert normalized["artifactClass"] == "zelph-graph"
    assert normalized["artifactId"] == "demo-artifact"
    assert normalized["shards"][0]["routingKeys"] == [
        "direct-shard=left-0001",
        "route-left-node=Q1",
        "route-node=Q1",
        "route-property=P31",
        "route-class=Q5",
    ]

    left_ids = route_selector(manifest, "route-node=Q1")
    name_ids = route_selector(manifest, "route-name=Alice")
    assert left_ids == ["left-0001"]
    assert name_ids == ["name-0001"]

    view = build_partial_graph_view(manifest, ["route-node=Q1", "route-name=Alice"])
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
    assert all("objectRefs" not in shard for shard in view["selected_shards"])
    assert all(set(shard) == {"shardId", "section", "logicalKind", "encoding", "sizeBytes", "contentDigest", "routingKeys"} for shard in view["selected_shards"])

    normalized_transport_view = _normalized_transport_view(manifest, ["route-node=Q1", "route-name=Alice"])
    assert normalized_transport_view == manifest["transportView"]

    serialized = json.dumps(normalized_transport_view, sort_keys=True)
    assert "hf://" not in serialized
    assert "ipfs://" not in serialized
    assert "objectRefs" not in serialized
    assert normalized_transport_view["nonAuthority"] == {
        "truth": False,
        "support": False,
        "admissibility": False,
        "promotion": False,
        "candidate_only": True,
        "diagnostic_only": True,
    }
    assert normalized_transport_view["invariants"]["partial_view"] is True
    assert normalized_transport_view["invariants"]["complete_closure"] is False
