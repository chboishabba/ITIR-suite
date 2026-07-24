from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from itir_mcp.domain_tools import zelph_partial_closure
from itir_mcp.pnf_spectral_packet import build_candidate_spectral_packet
from itir_mcp.shard_transport import build_partial_graph_view, route_selector, validate_shared_shard_artifact


FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures" / "shard_transport" / "shared_shard_artifact_v1.json"


def _fixture_manifest() -> dict[str, Any]:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def _sanitized_uri_metadata(uri: str) -> dict[str, str]:
    parsed = urlsplit(uri)
    resource = parsed.netloc + parsed.path
    return {
        "scheme": parsed.scheme,
        "resource": resource.lstrip("/"),
    }


def _bounded_probe_output(manifest: dict[str, Any], partial_view: dict[str, Any]) -> dict[str, Any]:
    shard_index = {shard["shardId"]: shard for shard in manifest["shards"]}
    probes: list[dict[str, Any]] = []

    for index, shard_id in enumerate(partial_view["selected_shard_ids"]):
        shard = shard_index[shard_id]
        probe: dict[str, Any] = {
            "probe_id": f"probe:{shard_id}",
            "candidate_ref": shard_id,
            "row": index,
            "object_id": shard_id,
            "rank": index,
            "authorized": index == 0,
        }
        if probe["authorized"]:
            probe["uri_metadata"] = _sanitized_uri_metadata(shard["objectRefs"][0]["uri"])
        probes.append(probe)

    return {
        "probe_kind": "bounded_probe",
        "candidate_only": True,
        "non_authoritative": True,
        "probes": probes,
    }


def _spectral_summary_payload(probe_output: dict[str, Any], closure: dict[str, Any]) -> dict[str, Any]:
    candidate_refs = [
        {
            "probe_id": probe["probe_id"],
            "candidate_ref": probe["candidate_ref"],
            "row": index + 1,
            "object_id": probe["candidate_ref"],
            "rank": index,
        }
        for index, probe in enumerate(probe_output["probes"])
    ]

    return {
        "summary": {
            "schema": "itir.pnf.spectral_numeric_abi.summary.v0_1",
            "graph_version": "graph:h4b:shared-shard-fixture:v1",
            "operator_profile": "h4b-bounded-probe",
            "objects": len(candidate_refs),
            "rows": len(candidate_refs),
            "spectral_dimensions": 2,
            "probe_rows": len(probe_output["probes"]),
            "edge_kinds": ["noTypedMeetEdge"],
            "gemv_rows": len(candidate_refs),
            "candidate_only": True,
            "diagnostic_only": True,
        },
        "candidate_refs": candidate_refs,
        "parity_hash": f"sha256:h4b:{closure['selected_candidate_count']}",
    }


def _assert_logical_only(payload: dict[str, Any]) -> None:
    serialized = json.dumps(payload, sort_keys=True)
    assert "hf://" not in serialized
    assert "ipfs://" not in serialized
    assert "objectRefs" not in serialized


def test_h4b_fixture_flow_keeps_transport_refs_out_of_logical_surfaces() -> None:
    manifest = _fixture_manifest()

    normalized = validate_shared_shard_artifact(manifest)
    assert normalized["contractVersion"] == "shared-shard-artifact/v1"
    assert normalized["artifactClass"] == "zelph-graph"
    assert [shard["shardId"] for shard in normalized["shards"]] == ["left-0001", "name-0001"]

    route_ids = route_selector(manifest, "route-node=Q1")
    assert route_ids == ["left-0001"]

    partial_view = build_partial_graph_view(manifest, ["route-node=Q1", "route-name=Alice"])
    assert partial_view["completeness"] == "partial"
    assert partial_view["subset_of_artifact"] is True
    assert partial_view["candidate_only"] is True
    assert partial_view["diagnostic_only"] is True
    assert partial_view["truth_authority"] is False
    assert partial_view["support_authority"] is False
    assert partial_view["admissibility_authority"] is False
    assert partial_view["promotion_authority"] is False
    assert partial_view["selected_shard_ids"] == ["left-0001", "name-0001"]
    assert partial_view["selected_sections"] == ["left", "nameOfNode"]
    assert all(set(shard) == {"shardId", "section", "logicalKind", "encoding", "sizeBytes", "contentDigest", "routingKeys"} for shard in partial_view["selected_shards"])
    assert all("objectRefs" not in shard for shard in partial_view["selected_shards"])

    probe_output = _bounded_probe_output(manifest, partial_view)
    assert probe_output["candidate_only"] is True
    assert probe_output["non_authoritative"] is True
    assert probe_output["probes"][0]["authorized"] is True
    assert probe_output["probes"][0]["uri_metadata"] == {
        "scheme": "hf",
        "resource": "datasets/example/demo/left-0001.json",
    }
    assert probe_output["probes"][1]["authorized"] is False
    assert "uri_metadata" not in probe_output["probes"][1]

    closure = zelph_partial_closure(
        {
            "partial_graph_view": partial_view,
            "candidate_refs": [probe["candidate_ref"] for probe in probe_output["probes"]],
        }
    )
    assert closure["closure_kind"] == "candidate_partial_closure"
    assert closure["incomplete_closure"] is True
    assert closure["candidate_only"] is True
    assert closure["non_authoritative"] is True
    assert closure["promoted_claims"] is False
    assert closure["truth_claims"] is False
    assert closure["authority_boundary"]["promotion_authority"] is False
    assert closure["candidate_refs"] == ["left-0001", "name-0001"]
    assert closure["selected_candidates"][0]["candidate_ref"] == "left-0001"
    assert "objectRefs" not in closure["selected_candidates"][0]
    assert "uri_metadata" not in closure["selected_candidates"][0]

    spectral_packet = build_candidate_spectral_packet(partial_view, _spectral_summary_payload(probe_output, closure))
    assert spectral_packet["candidate_only"] is True
    assert spectral_packet["non_authoritative"] is True
    assert spectral_packet["validation"]["status"] == "not_performed"
    assert spectral_packet["validation"]["summary"]["candidate_only"] is True
    assert spectral_packet["validation"]["summary"]["diagnostic_only"] is True
    assert spectral_packet["graph_refs"]["selected_shard_ids"] == ["left-0001", "name-0001"]
    assert spectral_packet["candidate_refs"][0]["probe_id"] == "probe:left-0001"
    assert spectral_packet["authority_boundary"]["truth"] is False
    assert spectral_packet["authority_boundary"]["promoted"] is False

    _assert_logical_only(partial_view)
    _assert_logical_only(probe_output)
    _assert_logical_only(closure)
    _assert_logical_only(spectral_packet)
