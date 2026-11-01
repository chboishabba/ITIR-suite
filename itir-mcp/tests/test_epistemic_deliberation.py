"""Contract regressions for source-pinned proposal governance and AO non-promotion."""
from __future__ import annotations

import copy

import pytest

from itir_mcp import build_default_registry
from itir_mcp.epistemic_deliberation import assess_deliberation

BASE = {
    "proposal_ref": "proposal:example",
    "source_revision_ref": "revision:archived-proposal",
    "policy_revision_ref": "policy:historical-snapshot",
    "minimum_age_seconds": 7 * 86400,
    "created_property_ref": "property:example",
    "events": [
        {"kind": "proposal", "event_ref": "event:1", "actor_ref": "editor:A",
         "source_revision_ref": "revision:1", "at": "2022-01-28T00:00:00Z"},
        {"kind": "objection", "event_ref": "event:2", "actor_ref": "editor:B",
         "source_revision_ref": "revision:2", "at": "2022-01-30T00:00:00Z"},
        {"kind": "amendment", "event_ref": "event:3", "actor_ref": "editor:A",
         "source_revision_ref": "revision:3", "at": "2022-02-01T00:00:00Z",
         "supersedes_ref": "event:1"},
        {"kind": "decision", "event_ref": "event:4", "actor_ref": "editor:C",
         "source_revision_ref": "revision:4", "at": "2022-02-05T00:00:00Z",
         "judgement": "approve",
         "consensus_assessment_ref": "discussion:judgement",
         "authority_receipt_ref": "community:role-observation"},
    ],
}


def test_reviewable_means_source_record_only_never_verified_consensus_or_ao_dispatch():
    r = assess_deliberation(BASE)
    assert r["record_completeness"] == "reviewable"
    assert r["holds"] == []
    assert r["objection_refs"] == ["event:2"]
    assert r["amendment_refs"] == ["event:3"]
    assert r["event_source_revision_refs"] == [
        "revision:1", "revision:2", "revision:3", "revision:4"]
    assert r["recorded_judgement"] == "approve"
    assert not any(r["authority"][key] for key in (
        "semantic_truth_promoted", "community_consensus_verified",
        "actor_authority_verified", "wikidata_edit_authorised",
        "ao_dispatch_allowed", "slr_s29_review_bypassed"))
    assert r["authority"]["candidate_only"] and r["authority"]["read_only"]
    assert assess_deliberation(copy.deepcopy(BASE))["packet_ref"] == r["packet_ref"]


def test_support_counts_never_replace_reasoned_consensus_or_approval_receipts():
    p = copy.deepcopy(BASE)
    p["events"][-1].pop("consensus_assessment_ref")
    p["events"][-1].pop("authority_receipt_ref")
    r = assess_deliberation(p)
    assert "consensus_judgement_source_missing" in r["holds"]
    assert "decision_authority_source_missing" in r["holds"]


def test_missing_decision_is_open_not_rejected_and_minimum_age_is_strict():
    p = copy.deepcopy(BASE)
    p["events"].pop()
    r = assess_deliberation(p)
    assert "no_terminal_decision" in r["holds"]
    assert r["recorded_judgement"] is None
    p = copy.deepcopy(BASE)
    p["events"][-1]["at"] = "2022-02-04T00:00:00Z"
    assert "minimum_proposal_age_not_met" in assess_deliberation(p)["holds"]


def test_self_approval_and_no_independent_contribution_are_held():
    p = copy.deepcopy(BASE)
    p["events"] = [p["events"][0], p["events"][-1]]
    p["events"][-1]["actor_ref"] = "editor:A"
    holds = assess_deliberation(p)["holds"]
    assert "decision_maker_equals_proposer" in holds
    assert "independent_participation_not_observed" in holds


@pytest.mark.parametrize("mutation", [
    lambda p: p["events"][1].update({"event_ref": "event:1"}),
    lambda p: p["events"][1].update({"at": "2022-01-01T00:00:00Z"}),
    lambda p: p["events"][2].update({"supersedes_ref": "event:not-yet"}),
    lambda p: p["events"][1].update({"authority_receipt_ref": "fake:authority"}),
    lambda p: p["events"][0].update({"source_revision_ref": ""}),
    lambda p: p["events"][0].update({"at": "2022-01-28T00:00:00"}),
])
def test_malformed_source_or_history_fails_closed(mutation):
    p = copy.deepcopy(BASE)
    mutation(p)
    with pytest.raises(ValueError):
        assess_deliberation(p)


def test_tool_is_exposed_by_existing_governance_registry_read_only():
    registry = build_default_registry()
    spec = registry.get_tool_spec("itir.governance.deliberation_assessment")
    assert spec is not None and spec.read_only
    output = registry.invoke("itir.governance.deliberation_assessment", BASE)
    assert output["ok"] is True
    assert output["result"]["version"] == "itir.governance.deliberation_assessment.v1"
    assert output["result"]["authority"]["wikidata_edit_authorised"] is False
