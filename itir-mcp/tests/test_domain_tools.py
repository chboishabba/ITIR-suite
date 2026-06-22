from __future__ import annotations

import pytest

from itir_mcp import build_default_registry, ToolInputError
from itir_mcp.domain_tools import wikidata_review_packet, zelph_partial_closure


def _wikidata_review_payload() -> dict:
    return {
        "statements": [
            {
                "statement_id": "stmt-1",
                "fact": "Q42 is an instance of human",
                "provenance_refs": ["wikidata:Q42#P31"],
                "confidence": 0.98,
            },
            {
                "ref": "stmt-2",
                "summary": "Q42 has occupation writer",
                "provenance_refs": [{"ref": "wikidata:Q42#P106"}],
            },
        ],
        "constraints": [
            {
                "constraint_id": "cons-1",
                "status": "satisfied",
                "severity": "info",
                "message": "Candidate refs remain inside the supplied review boundary.",
                "candidate_refs": ["stmt-1", "stmt-2"],
                "provenance_refs": ["constraint:1"],
            },
            {
                "id": "cons-2",
                "severity": "warning",
                "diagnostic": "One source remains incomplete.",
                "refs": [{"ref": "stmt-2"}],
            },
        ],
        "tooling_profile": {
            "tool_id": "sensiblaw_review_packets",
            "kind": "validation",
            "max_authority": "reviewed",
            "promotion_requires_gate": False,
            "authority_notes": {"note": "review surfaces are not truth promotion"},
        },
    }


def _partial_graph_view() -> dict:
    return {
        "artifact_identity": {
            "contractVersion": "shared-shard-artifact/v1",
            "artifactId": "artifact:demo",
            "artifactRevision": "rev-1",
            "artifactClass": "zelph-graph",
            "createdAtUtc": "2026-06-22T00:00:00Z",
        },
        "selected_shard_ids": ["logical:left", "logical:right"],
        "selected_sections": ["left", "right"],
        "selected_shards": [
            {
                "shardId": "logical:left",
                "section": "left",
                "logicalKind": "content-shard",
                "encoding": "json",
                "contentDigest": "sha256:left",
                "routingKeys": ["direct-shard=logical:left"],
            },
            {
                "shardId": "logical:right",
                "section": "right",
                "logicalKind": "content-shard",
                "encoding": "json",
                "contentDigest": "sha256:right",
                "routingKeys": ["route-name=right-name"],
            },
        ],
        "completeness": "partial",
        "subset_of_artifact": True,
        "candidate_only": True,
        "diagnostic_only": True,
    }


def test_wikidata_review_packet_compiles_candidate_only_summary() -> None:
    packet = wikidata_review_packet(_wikidata_review_payload())

    assert packet["version"] == "itir.wikidata.review_packet.v1"
    assert packet["domain"] == "wikidata"
    assert packet["candidate_only"] is True
    assert packet["non_authoritative"] is True
    assert packet["promoted_claims"] is False
    assert packet["truth_claims"] is False
    assert packet["authority_boundary"]["read_only"] is True
    assert packet["authority_boundary"]["promotion_authority"] is False
    assert packet["statement_count"] == 2
    assert packet["constraint_count"] == 2
    assert packet["facts"][0]["candidate_ref"] == "stmt-1"
    assert packet["facts"][0]["fact"] == "Q42 is an instance of human"
    assert packet["constraint_diagnostics"][0]["candidate_refs"] == ["stmt-1", "stmt-2"]
    assert packet["citations"] == [
        "wikidata:Q42#P31",
        "wikidata:Q42#P106",
        "constraint:1",
    ]
    assert packet["provenance_refs"] == packet["citations"]
    assert packet["constraint_diagnostics"][1]["candidate_refs"] == ["stmt-2"]
    assert "statements" not in packet
    assert "constraints" not in packet
    assert packet["summary"].startswith("Candidate-only Wikidata review packet")


def test_zelph_partial_closure_compiles_incomplete_candidate_summary() -> None:
    closure = zelph_partial_closure({"partial_graph_view": _partial_graph_view()})

    assert closure["version"] == "itir.zelph.partial_closure.v1"
    assert closure["domain"] == "zelph"
    assert closure["incomplete_closure"] is True
    assert closure["candidate_only"] is True
    assert closure["non_authoritative"] is True
    assert closure["promoted_claims"] is False
    assert closure["truth_claims"] is False
    assert closure["authority_boundary"]["read_only"] is True
    assert closure["authority_boundary"]["promotion_authority"] is False
    assert closure["candidate_refs"] == ["logical:left", "logical:right"]
    assert closure["selected_candidates"][0]["candidate_ref"] == "logical:left"
    assert "objectRefs" not in closure["selected_candidates"][0]
    assert closure["diagnostics"][0]["code"] == "incomplete_closure"
    assert closure["diagnostics"][1]["code"] == "non_authoritative"
    assert closure["closure_summary"].startswith("Partial Zelph closure remains incomplete")


def test_domain_tools_reject_malformed_and_authoritative_input() -> None:
    with pytest.raises(ToolInputError, match="Expected array field: statements"):
        wikidata_review_packet({"statements": {}, "constraints": [], "tooling_profile": {"tool_id": "x"}})

    with pytest.raises(ToolInputError, match="completeness must be partial"):
        zelph_partial_closure(
            {
                "partial_graph_view": {
                    **_partial_graph_view(),
                    "completeness": "complete",
                }
            }
        )


def test_domain_tools_register_through_default_registry() -> None:
    registry = build_default_registry()
    names = {tool.name for tool in registry.list_tools()}
    assert "itir.wikidata.review_packet" in names
    assert "itir.zelph.partial_closure" in names

    wikidata = registry.invoke("itir.wikidata.review_packet", _wikidata_review_payload())
    assert wikidata["ok"] is True
    assert wikidata["result"]["non_authoritative"] is True
    assert wikidata["result"]["truth_claims"] is False

    zelph = registry.invoke("itir.zelph.partial_closure", {"partial_graph_view": _partial_graph_view()})
    assert zelph["ok"] is True
    assert zelph["result"]["non_authoritative"] is True
    assert zelph["result"]["incomplete_closure"] is True
