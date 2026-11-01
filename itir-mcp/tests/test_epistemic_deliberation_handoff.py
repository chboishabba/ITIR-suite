"""Native SLR shape parity and cross-lane non-promotion contracts."""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone

import pytest

from itir_mcp import build_default_registry
from itir_mcp.contracts import ToolInputError
from itir_mcp.epistemic_deliberation_handoff import (
    project_slr_handoff,
    project_deliberation_consumer_link,
)

# Fictional source IDs and hashes test only the contract; no historical claims.
DISCUSSION = {
    "proposal_ref": "proposal:fictional",
    "source_revision_ref": "source-revision:root",
    "policy_revision_ref": "source-revision:historical-policy",
    "minimum_age_seconds": 86400,
    "created_property_ref": "P987654",
    "events": [
        {"kind": "proposal", "event_ref": "event:proposer", "actor_ref": "actor:A",
         "source_revision_ref": "source-revision:proposal", "at": "2022-01-01T00:00:00+10:00"},
        {"kind": "objection", "event_ref": "event:critic", "actor_ref": "actor:B",
         "source_revision_ref": "source-revision:critic", "at": "2022-01-03T01:00:00+10:00"},
        {"kind": "decision", "event_ref": "event:closer", "actor_ref": "actor:C",
         "source_revision_ref": "source-revision:closure", "at": "2022-01-05T00:00:00+10:00",
         "judgement": "approve", "consensus_assessment_ref": "discussion:witness",
         "authority_receipt_ref": "role:observation"},
    ],
}
SHA = "sha256:" + "a" * 64
REQUIRED = [
    "source-revision:root", "source-revision:historical-policy",
    "source-revision:proposal", "source-revision:critic", "source-revision:closure",
]


def _payload():
    return {
        "deliberation": deepcopy(DISCUSSION),
        "source_seals": [{
            "source_revision_ref": x, "content_digest_ref": SHA,
            "acquisition_receipt_ref": "acquisition:fictional"
        } for x in REQUIRED],
        "event_anchors": [{
            "event_ref": x["event_ref"], "source_revision_ref": x["source_revision_ref"],
            "start_byte": 0, "end_byte": 2, "excerpt_digest_ref": SHA
        } for x in DISCUSSION["events"]],
    }


def test_handoff_uses_slr_native_exact_second_timestamp_and_complete_sources():
    result = project_slr_handoff(_payload())
    native = result["slr_packet"]
    assert native["events"][0]["at_unix_seconds"] == int(datetime(
        2021, 12, 31, 14, 0, tzinfo=timezone.utc).timestamp())
    assert native["events"][0]["at_unix_seconds"] < native["events"][1]["at_unix_seconds"]
    assert native["events"][-1]["judgement"] == "approve"
    assert native["events"][0]["judgement"] is None
    assert native["events"][0]["authority_receipt_ref"] is None
    assert native["created_property_ref"] == "P987654"
    assert result["record_completeness"] == "reviewable"
    assert len(result["slr_source_seals"]) == len(REQUIRED)
    assert len(result["slr_event_anchors"]) == len(native["events"])
    assert result["source_binding_status"] == "caller_supplied_unverified"
    assert not any(result["authority"][key] for key in (
        "source_content_verified", "slr_pg_reopened", "s29_receipt_created",
        "community_consensus_verified", "wikidata_edit_authorised", "ao_dispatch_allowed"
    ))


@pytest.mark.parametrize("mutation", [
    lambda p: p["source_seals"].pop(),
    lambda p: p["source_seals"].append(deepcopy(p["source_seals"][0])),
    lambda p: p["source_seals"][0].update({"content_digest_ref": "sha256:bad"}),
    lambda p: p["event_anchors"].pop(),
    lambda p: p["event_anchors"][0].update({"source_revision_ref": "source-revision:other"}),
    lambda p: p["event_anchors"][0].update({"start_byte": 2, "end_byte": 2}),
    lambda p: p["event_anchors"][0].update({"excerpt_digest_ref": "sha256:bad"}),
    lambda p: p["deliberation"]["events"][0].update({"at": "2022-01-01T00:00:00.5+10:00"}),
    lambda p: p["deliberation"]["events"][0].update({"at": "1960-01-01T00:00:00Z"}),
])
def test_fail_closed_when_seal_anchor_or_native_timestamp_cannot_match(mutation):
    p = _payload()
    mutation(p)
    with pytest.raises(ToolInputError):
        project_slr_handoff(p)


def test_all_consumer_lanes_stay_candidate_only_even_with_property_ref_hit():
    for schema in (
        "sl.wikidata_change_review_report.v0_1",
        "sl.wikidata_signal_review_bundle.v0_1",
        "itir.wikidata.disjointness_report.v1",
        "itir.wikidata.review_packet.v1",
    ):
        output = project_deliberation_consumer_link({
            "deliberation": DISCUSSION,
            "consumer_ref": "consumer:fixture", "consumer_schema": schema,
            "consumer_source_revision_ref": "source-revision:consumer",
            "subject_property_refs": ["P31", "P987654"],
            "source_alignment_ref": "alignment:candidate-not-verified",
        })
        assert output["property_ref_exact_hits"] == ["P987654"]
        assert output["authority"]["source_alignment_verified"] is False
        assert output["authority"]["identity_equivalence_proved"] is False
        assert output["authority"]["wikidata_edit_authorised"] is False
        assert output["authority"]["ao_dispatch_allowed"] is False
        assert "consumer_structural_diagnostics_remain_independent" in output["unpaid_obligations"]


def test_mismatching_property_is_not_promoted_into_a_bridge():
    p = {
        "deliberation": DISCUSSION,
        "consumer_ref": "consumer:fixture",
        "consumer_schema": "sl.wikidata_change_review_report.v0_1",
        "consumer_source_revision_ref": "source-revision:consumer",
        "subject_property_refs": ["P14143"],
        "source_alignment_ref": "alignment:candidate",
    }
    assert project_deliberation_consumer_link(p)["property_ref_exact_hits"] == []


def test_registry_exposes_both_as_read_only_and_returns_unverified_packets():
    registry = build_default_registry()
    for name in ("itir.governance.deliberation_slr_handoff", "itir.governance.deliberation_consumer_link"):
        spec = registry.get_tool_spec(name)
        assert spec is not None and spec.read_only
    actual = registry.invoke("itir.governance.deliberation_slr_handoff", _payload())
    assert actual["ok"] is True
    assert actual["result"]["authority"]["slr_pg_reopened"] is False
