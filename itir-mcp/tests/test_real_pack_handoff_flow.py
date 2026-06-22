from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from itir_mcp.domain_tools import wikidata_review_packet, zelph_partial_closure
from itir_mcp.pnf_spectral_packet import build_candidate_spectral_packet
from itir_mcp.shard_transport import build_partial_graph_view, route_selector, validate_shared_shard_artifact


FIXTURE_PATH = (
    Path(__file__).resolve().parent / "fixtures" / "real_pack_handoff" / "wikidata_structural_handoff_real_pack_v1.json"
)


def _fixture() -> dict[str, Any]:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def _review_packet_payload(manifest: dict[str, Any], partial_view: dict[str, Any]) -> dict[str, Any]:
    shard_ids = list(partial_view["selected_shard_ids"])
    source_inputs = list(manifest["buildProvenance"]["sourceInputs"])

    return {
        "statements": [
            {
                "statement_id": shard_id,
                "fact": (
                    f"{shard_id} stays candidate-only inside the checked Zelph handoff "
                    f"for {partial_view['artifact_identity']['artifactId']}."
                ),
                "provenance_refs": source_inputs,
                "confidence": 0.99,
            }
            for shard_id in shard_ids
        ],
        "constraints": [
            {
                "constraint_id": "real-pack-handoff-boundary",
                "status": "satisfied",
                "severity": "info",
                "message": "The review packet stays candidate-only and carries no promotion authority.",
                "candidate_refs": shard_ids,
                "provenance_refs": source_inputs,
            }
        ],
        "tooling_profile": {
            "tool_id": "sensiblaw_review_packets",
            "kind": "validation",
            "max_authority": "reviewed",
            "promotion_requires_gate": False,
            "candidate_only": True,
            "non_authoritative": True,
            "read_only": True,
            "authority_notes": {
                "note": "Derived from the checked Zelph handoff fixture and kept review-only."
            },
            "authority_boundary": {
                "read_only": True,
                "non_authoritative": True,
                "candidate_only": True,
                "promotion_authority": False,
                "canonical_truth_mutated": False,
            },
        },
        "provenance_refs": source_inputs,
    }


def _spectral_summary_payload(review_packet: dict[str, Any], closure: dict[str, Any]) -> dict[str, Any]:
    candidate_refs = [
        {
            "probe_id": f"probe:{candidate['candidate_ref']}",
            "candidate_ref": candidate["candidate_ref"],
            "row": index + 1,
            "object_id": candidate["candidate_ref"],
            "rank": index,
        }
        for index, candidate in enumerate(closure["selected_candidates"])
    ]
    return {
        "summary": {
            "schema": "itir.pnf.spectral_numeric_abi.summary.v0_1",
            "graph_version": "graph:real-pack-handoff:q10403939-p5991",
            "operator_profile": review_packet["tooling_profile"]["tool_id"],
            "objects": len(candidate_refs),
            "rows": len(candidate_refs),
            "spectral_dimensions": 2,
            "probe_rows": 1,
            "edge_kinds": ["noTypedMeetEdge"],
            "gemv_rows": len(candidate_refs),
            "candidate_only": True,
            "diagnostic_only": True,
        },
        "candidate_refs": candidate_refs,
        "parity_hash": "sha256:real-pack-handoff-candidate-summary",
    }


def _assert_sanitized(payload: dict[str, Any]) -> None:
    serialized = json.dumps(payload, sort_keys=True)
    assert "hf://" not in serialized
    assert "ipfs://" not in serialized
    assert "objectRefs" not in serialized

    def _walk(value: Any) -> None:
        if isinstance(value, dict):
            if "promotion_authority" in value:
                assert value["promotion_authority"] is False
            for item in value.values():
                _walk(item)
        elif isinstance(value, list):
            for item in value:
                _walk(item)

    _walk(payload)


def test_real_pack_handoff_flows_through_candidate_only_surfaces() -> None:
    manifest = _fixture()

    normalized = validate_shared_shard_artifact(manifest)
    assert normalized["contractVersion"] == "shared-shard-artifact/v1"
    assert normalized["artifactClass"] == "zelph-graph"
    assert [shard["shardId"] for shard in normalized["shards"]] == ["review-0001", "review-0002"]
    assert normalized["shards"][0]["objectRefs"][0]["sink"] == "hf"

    route_ids = route_selector(manifest, "route-node=Q10403939")
    assert route_ids == ["review-0001", "review-0002"]
    assert all(not item.startswith("hf://") and not item.startswith("ipfs://") for item in route_ids)

    partial_view = build_partial_graph_view(manifest, ["route-node=Q10403939", "route-name=checked-handoff"])
    assert partial_view["completeness"] == "partial"
    assert partial_view["subset_of_artifact"] is True
    assert partial_view["candidate_only"] is True
    assert partial_view["diagnostic_only"] is True
    assert partial_view["truth_authority"] is False
    assert partial_view["support_authority"] is False
    assert partial_view["admissibility_authority"] is False
    assert partial_view["promotion_authority"] is False
    assert partial_view["selected_shard_ids"] == ["review-0001", "review-0002"]
    assert partial_view["selected_sections"] == ["review_packet", "partial_closure"]
    assert all("objectRefs" not in shard for shard in partial_view["selected_shards"])

    review_packet = wikidata_review_packet(_review_packet_payload(manifest, partial_view))
    assert review_packet["packet_kind"] == "candidate_review_packet"
    assert review_packet["candidate_only"] is True
    assert review_packet["non_authoritative"] is True
    assert review_packet["promoted_claims"] is False
    assert review_packet["truth_claims"] is False
    assert review_packet["authority_boundary"]["promotion_authority"] is False
    assert review_packet["facts"][0]["candidate_ref"] == "review-0001"
    assert review_packet["constraint_diagnostics"][0]["candidate_refs"] == ["review-0001", "review-0002"]

    closure = zelph_partial_closure(
        {
            "partial_graph_view": partial_view,
            "candidate_refs": ["review-0001", "review-0002"],
        }
    )
    assert closure["closure_kind"] == "candidate_partial_closure"
    assert closure["incomplete_closure"] is True
    assert closure["candidate_only"] is True
    assert closure["non_authoritative"] is True
    assert closure["promoted_claims"] is False
    assert closure["truth_claims"] is False
    assert closure["authority_boundary"]["promotion_authority"] is False
    assert closure["candidate_refs"] == ["review-0001", "review-0002"]
    assert closure["selected_candidates"][0]["candidate_ref"] == "review-0001"

    spectral_packet = build_candidate_spectral_packet(partial_view, _spectral_summary_payload(review_packet, closure))
    assert spectral_packet["candidate_only"] is True
    assert spectral_packet["non_authoritative"] is True
    assert spectral_packet["validation"]["status"] == "not_performed"
    assert spectral_packet["validation"]["summary"]["candidate_only"] is True
    assert spectral_packet["validation"]["summary"]["diagnostic_only"] is True
    assert spectral_packet["candidate_refs"][0]["candidate_ref"] == "review-0001"
    assert spectral_packet["authority_boundary"]["promoted"] is False

    _assert_sanitized(partial_view)
    _assert_sanitized(review_packet)
    _assert_sanitized(closure)
    _assert_sanitized(spectral_packet)
