from __future__ import annotations

import pytest

from itir_mcp import build_default_registry, ToolInputError
from itir_mcp.domain_tools import (
    climate_claim_review,
    gwb_follow_graph,
    wikidata_migration_candidate,
    wikidata_review_packet,
    zelph_partial_closure,
)


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


def _wikidata_migration_candidate_payload() -> dict:
    return {
        "statement_refs": ["stmt-1", {"ref": "stmt-2"}],
        "property_hints": [{"ref": "wikidata:P31"}, "wikidata:P106"],
        "class_hints": [{"id": "wikidata:Q5"}],
        "expected_fields": ["property", {"field_name": "class"}],
        "characteristic_fields": [{"name": "label"}, "description"],
        "constraint_refs": ["constraint:1"],
        "repair_refs": [{"value": "repair:1"}],
        "report_refs": ["report:1"],
        "citations": [{"uri": "citation:1"}],
        "provenance_refs": [{"ref": "prov:1"}],
        "authority_label": "candidate-only",
        "raw_text": "this should be stripped",
        "full_receipts": [{"receipt_id": "receipt:1", "body": "this should be stripped"}],
        "span_refs": [{"ref": "span:1"}],
        "spans": [{"start": 0, "end": 10}],
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


def _climate_claim_review_payload() -> dict:
    return {
        "authority_label": "candidate-only",
        "gate_requirements": {
            "promotion_requires_gate": True,
            "review_gate": "climate_nat_review",
        },
        "citations": ["climate:packet:source"],
        "provenance_refs": [{"ref": "climate:packet:prov"}],
        "claims": [
            {
                "claim_id": "claim-1",
                "normal_form": "climate_nat:temperature_anomaly(gt,threshold)",
                "rendered_claim": "Observed temperature anomaly exceeds the NAT threshold.",
                "candidate_status": "candidate",
                "support_count": 2,
                "contradiction_count": 1,
                "citations": ["climate:claim:1"],
                "provenance_refs": ["climate:prov:1"],
                "authority_label": "candidate-only",
                "gate_requirements": {
                    "promotion_requires_gate": True,
                    "review_gate": "climate_nat_review",
                },
                "raw_text": "full raw claim text that must not surface",
                "full_receipts": ["receipt:1"],
                "spans": [{"start": 0, "end": 10}],
            }
        ],
    }


def _gwb_follow_graph_payload() -> dict:
    return {
        "authority_label": "external authority follow graph",
        "source_refs": [
            {
                "ref": "source:gwb-1",
                "label": "Cabinet note",
                "raw_text": "full note text that must not leak",
                "full_receipt": {"text": "receipt body"},
                "spans": [{"start": 0, "end": 4}],
            },
            {"ref": "source:gwb-2", "text": "another source text"},
        ],
        "authority_refs": [
            {
                "id": "authority:uk-parliament",
                "label": "UK Parliament",
                "full_receipt": {"body": "authority receipt"},
            },
            {"ref": "authority:eu-council", "spans": [{"start": 9, "end": 12}]},
        ],
        "follow_edges": [
            {
                "edge_ref": "edge-1",
                "source_ref": "source:gwb-1",
                "authority_ref": "authority:uk-parliament",
                "relation": "follows",
                "citations": [{"ref": "cite-1", "text": "raw citation text"}],
                "provenance_refs": ["prov-1"],
                "full_receipt": {"body": "edge receipt"},
                "spans": [{"start": 1, "end": 2}],
            },
            {
                "id": "edge-2",
                "source": "source:gwb-2",
                "target": "authority:eu-council",
                "kind": "depends_on",
                "citations": ["cite-2"],
                "provenance": [{"id": "prov-2"}],
            },
        ],
        "unresolved_obligations": [
            {
                "obligation_id": "obligation-1",
                "source_refs": ["source:gwb-1"],
                "authority_refs": [{"ref": "authority:eu-council"}],
                "citations": ["cite-2"],
                "provenance_refs": [{"ref": "prov-2"}],
                "status": "open",
                "text": "must remain open",
            }
        ],
        "citations": [{"ref": "cite-0", "text": "top level citation"}],
        "provenance_refs": ["prov-0"],
        "raw_text": "full follow narrative",
        "full_receipts": [{"text": "receipt bundle"}],
        "spans": [{"start": 10, "end": 20}],
    }


def _assert_no_bulky_fields(value: object) -> None:
    if isinstance(value, dict):
        forbidden = {
            "raw_text",
            "receipts",
            "full_receipt",
            "full_receipts",
            "span_refs",
            "span_arrays",
            "spans",
            "text",
        }
        assert forbidden.isdisjoint(value.keys())
        for item in value.values():
            _assert_no_bulky_fields(item)
    elif isinstance(value, list):
        for item in value:
            _assert_no_bulky_fields(item)


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


def test_climate_claim_review_compiles_candidate_only_packet() -> None:
    packet = climate_claim_review(_climate_claim_review_payload())

    assert packet["version"] == "itir.climate.claim_review.v1"
    assert packet["domain"] == "climate_nat"
    assert packet["packet_kind"] == "candidate_claim_review_packet"
    assert packet["candidate_only"] is True
    assert packet["non_authoritative"] is True
    assert packet["promoted_claims"] is False
    assert packet["truth_claims"] is False
    assert packet["authority_label"] == "candidate-only"
    assert packet["gate_requirements"]["promotion_requires_gate"] is True
    assert packet["gate_requirements"]["review_gate"] == "climate_nat_review"
    assert packet["claim_count"] == 1
    assert packet["support_count"] == 2
    assert packet["contradiction_count"] == 1
    assert packet["claims"][0]["claim_id"] == "claim-1"
    assert packet["claims"][0]["normal_form"] == "climate_nat:temperature_anomaly(gt,threshold)"
    assert packet["claims"][0]["rendered_claim"] == "Observed temperature anomaly exceeds the NAT threshold."
    assert packet["claims"][0]["candidate_status"] == "candidate"
    assert packet["claims"][0]["support_count"] == 2
    assert packet["claims"][0]["contradiction_count"] == 1
    assert packet["claims"][0]["citations"] == ["climate:claim:1"]
    assert packet["claims"][0]["provenance_refs"] == ["climate:prov:1"]
    assert packet["claims"][0]["authority_label"] == "candidate-only"
    assert packet["claims"][0]["gate_requirements"]["review_gate"] == "climate_nat_review"
    assert packet["citations"] == ["climate:claim:1", "climate:packet:source"]
    assert packet["provenance_refs"] == ["climate:prov:1", "climate:packet:prov"]
    assert packet["authority_boundary"]["candidate_only"] is True
    assert packet["authority_boundary"]["non_authoritative"] is True
    assert packet["authority_boundary"]["promotion_authority"] is False
    assert packet["summary"].startswith("Candidate-only Climate NAT claim review packet")
    _assert_no_bulky_fields(packet)


def test_climate_claim_review_rejects_non_candidate_authority_label() -> None:
    payload = _climate_claim_review_payload()
    payload["authority_label"] = "authoritative"

    with pytest.raises(ToolInputError, match="authority_label must be candidate-only"):
        climate_claim_review(payload)


def test_wikidata_migration_candidate_compiles_normalized_packet_without_raw_text() -> None:
    packet = wikidata_migration_candidate(_wikidata_migration_candidate_payload())

    assert packet["version"] == "itir.wikidata.migration_candidate.v1"
    assert packet["domain"] == "wikidata"
    assert packet["packet_kind"] == "candidate_migration_packet"
    assert packet["candidate_only"] is True
    assert packet["non_authoritative"] is True
    assert packet["promoted_claims"] is False
    assert packet["truth_claims"] is False
    assert packet["authority_label"] == "candidate-only"
    assert packet["statement_refs"] == ["stmt-1", "stmt-2"]
    assert packet["property_hints"] == ["wikidata:P31", "wikidata:P106"]
    assert packet["class_hints"] == ["wikidata:Q5"]
    assert packet["expected_fields"] == ["property", "class"]
    assert packet["characteristic_fields"] == ["label", "description"]
    assert packet["constraint_refs"] == ["constraint:1"]
    assert packet["repair_refs"] == ["repair:1"]
    assert packet["report_refs"] == ["report:1"]
    assert packet["citations"] == ["citation:1"]
    assert packet["provenance_refs"] == ["prov:1"]
    assert packet["authority_boundary"]["read_only"] is True
    assert packet["authority_boundary"]["promotion_authority"] is False
    assert "raw_text" not in packet
    assert "full_receipts" not in packet
    assert "span_refs" not in packet
    assert "spans" not in packet
    assert packet["summary"].startswith("Candidate-only Wikidata migration packet")


def test_gwb_follow_graph_compiles_candidate_only_sanitized_summary() -> None:
    graph = gwb_follow_graph(_gwb_follow_graph_payload())

    assert graph["version"] == "itir.gwb.follow_graph.v1"
    assert graph["domain"] == "gwb"
    assert graph["graph_kind"] == "candidate_follow_graph"
    assert graph["candidate_only"] is True
    assert graph["non_authoritative"] is True
    assert graph["promoted_claims"] is False
    assert graph["truth_claims"] is False
    assert graph["authority_label"] == "external authority follow graph"
    assert graph["authority_boundary"]["read_only"] is True
    assert graph["authority_boundary"]["non_authoritative"] is True
    assert graph["authority_boundary"]["promotion_authority"] is False
    assert graph["source_refs"] == ["source:gwb-1", "source:gwb-2"]
    assert graph["authority_refs"] == ["authority:uk-parliament", "authority:eu-council"]
    assert [edge["edge_ref"] for edge in graph["follow_edges"]] == ["edge-1", "edge-2"]
    assert graph["follow_edges"][1]["relation"] == "depends_on"
    assert graph["unresolved_obligations"][0]["obligation_ref"] == "obligation-1"
    assert graph["unresolved_obligations"][0]["status"] == "open"
    assert graph["citations"] == ["cite-0", "cite-1", "cite-2"]
    assert graph["provenance_refs"] == ["prov-0", "prov-1", "prov-2"]
    assert "raw_text" not in graph
    assert "full_receipts" not in graph
    assert "spans" not in graph
    assert "full_receipt" not in graph["follow_edges"][0]
    assert "spans" not in graph["follow_edges"][0]
    assert "text" not in graph["follow_edges"][0]
    assert "text" not in graph["unresolved_obligations"][0]
    assert graph["summary"].startswith("Candidate-only GWB follow graph")
    _assert_no_bulky_fields(graph)


def test_gwb_follow_graph_rejects_promoted_or_self_authorizing_input() -> None:
    with pytest.raises(ToolInputError, match="promoted_claims must be false"):
        gwb_follow_graph({**_gwb_follow_graph_payload(), "promoted_claims": True})

    with pytest.raises(ToolInputError, match="authority_label must not claim promotion"):
        gwb_follow_graph({**_gwb_follow_graph_payload(), "authority_label": "self_authorizing"})


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

    with pytest.raises(ToolInputError, match="Expected array field: statement_refs"):
        wikidata_migration_candidate(
            {
                "statement_refs": {},
                "authority_label": "candidate-only",
            }
        )

    with pytest.raises(ToolInputError, match="must include structural refs or hints"):
        wikidata_migration_candidate({"authority_label": "candidate-only"})

    with pytest.raises(ToolInputError, match="Expected array field: claims"):
        climate_claim_review({"claims": {}, "authority_label": "candidate-only"})


def test_domain_tools_register_through_default_registry() -> None:
    registry = build_default_registry()
    names = {tool.name for tool in registry.list_tools()}
    assert "itir.climate.claim_review" in names
    assert "itir.gwb.follow_graph" in names
    assert "itir.wikidata.migration_candidate" in names
    assert "itir.wikidata.review_packet" in names
    assert "itir.zelph.partial_closure" in names

    climate = registry.invoke("itir.climate.claim_review", _climate_claim_review_payload())
    assert climate["ok"] is True
    assert climate["result"]["non_authoritative"] is True
    assert climate["result"]["truth_claims"] is False

    gwb = registry.invoke("itir.gwb.follow_graph", _gwb_follow_graph_payload())
    assert gwb["ok"] is True
    assert gwb["result"]["non_authoritative"] is True
    assert gwb["result"]["truth_claims"] is False

    migration = registry.invoke("itir.wikidata.migration_candidate", _wikidata_migration_candidate_payload())
    assert migration["ok"] is True
    assert migration["result"]["non_authoritative"] is True
    assert migration["result"]["truth_claims"] is False

    wikidata = registry.invoke("itir.wikidata.review_packet", _wikidata_review_payload())
    assert wikidata["ok"] is True
    assert wikidata["result"]["non_authoritative"] is True
    assert wikidata["result"]["truth_claims"] is False

    zelph = registry.invoke("itir.zelph.partial_closure", {"partial_graph_view": _partial_graph_view()})
    assert zelph["ok"] is True
    assert zelph["result"]["non_authoritative"] is True
    assert zelph["result"]["incomplete_closure"] is True
