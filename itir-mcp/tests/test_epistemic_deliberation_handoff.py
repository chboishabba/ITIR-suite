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
    project_source_replay_handoff,
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


def _captured_text_fixture():
    import hashlib

    base = _payload()
    expected = {
        base["deliberation"]["source_revision_ref"],
        base["deliberation"]["policy_revision_ref"],
        *(event["source_revision_ref"] for event in base["deliberation"]["events"]),
    }
    references = {}
    input_rows = []
    for i, old in enumerate(sorted(expected), start=1):
        source_ref = f"wikidata:page:{1000+i}"
        original_text = f"original Wikidata revision {old} source bytes"
        digest = "sha256:" + hashlib.sha256(original_text.encode("utf-8")).hexdigest()
        acquisition = "wiki-acquisition:sha256:" + hashlib.sha256(
            ("\n".join([source_ref, f"https://www.wikidata.org/w/api.php?revid={i}", digest])).encode()
        ).hexdigest()
        fields = ("generic-source-revision:v1", source_ref, "wikidata:mediawiki-api",
                  acquisition, digest, "text/x-wiki")
        encoded=b"".join(len(v.encode()).to_bytes(8,"big")+v.encode() for v in fields)
        revision="source-revision:sha256:"+hashlib.sha256(encoded).hexdigest()
        references[old]=(revision,original_text,digest,acquisition)
        input_rows.append({
            "envelope":{
                "source_ref":source_ref,"source_revision_ref":revision,
                "provider_ref":"wikidata:mediawiki-api","family":"wiki",
                "role_class":"content_source","content_digest_ref":digest,
                "acquisition_receipt_ref":acquisition,"media_type_ref":"text/x-wiki",
                "candidate_only":True,"creates_semantic_authority":False,
                "applicability_promoted":False,"claim_truth_promoted":False,
            },
            "canonical_text":original_text,
        })
    discussion=base["deliberation"]
    discussion["source_revision_ref"]=references[discussion["source_revision_ref"]][0]
    discussion["policy_revision_ref"]=references[discussion["policy_revision_ref"]][0]
    for event in discussion["events"]:
        old=event["source_revision_ref"]
        event["source_revision_ref"]=references[old][0]
    source_seals=[]
    for old in sorted(references):
        revision,original_text,digest,acquisition=references[old]
        source_seals.append({
            "source_revision_ref":revision,"content_digest_ref":digest,
            "acquisition_receipt_ref":acquisition,
        })
    for anchor in base["event_anchors"]:
        old=anchor["source_revision_ref"]
        revision,original_text,digest,acquisition=references[old]
        anchor["source_revision_ref"]=revision
        anchor["end_byte"]=len(original_text.encode())
        anchor["excerpt_digest_ref"]=digest
    base["source_seals"]=source_seals
    return base,input_rows


def test_captured_sensiblaw_historical_wiki_wrapper_is_exactly_slr_handoff_and_non_authoritative():
    native,source_inputs=_captured_text_fixture()
    policy_source=next(row for row in source_inputs if
        row["envelope"]["source_revision_ref"]==native["deliberation"]["policy_revision_ref"])
    policy_oldid=int(policy_source["envelope"]["source_ref"].rsplit(":",1)[1])
    policy_window={
        "opening_policy_page_oldid":policy_oldid,
        "closing_policy_page_oldid":policy_oldid,
        "opening_policy_revision_time":"2021-12-30T00:00:00Z",
        "closing_policy_revision_time":"2021-12-30T00:00:00Z",
        "policy_content_digest_ref":policy_source["envelope"]["content_digest_ref"],
        "closing_policy_content_digest_ref":policy_source["envelope"]["content_digest_ref"],
        "closing_acquisition_url":"https://www.wikidata.org/w/api.php?revid=policy",
        "comparison_status":"unchanged_across_proposal_window",
        "candidate_only":True,
        "policy_normatively_verified":False,
    }
    wrapper={
        "schema_version":"sl.wikidata_deliberation_slr_handoff_draft.v0_1",
        "itir_slr_input":native,
        "slr_source_inputs":source_inputs,
        "historical_policy_drift_status":"unchanged_across_proposal_window",
        "historical_policy_window_source_witness":policy_window,
        "source_revision_refs":[v["source_revision_ref"] for v in native["source_seals"]],
        "candidate_only":True,
        "producer_canonical_byte_digests_observed":True,
        "independent_source_provider_receipts_verified":False,
        "historical_policy_applicability_verified":False,
        "historical_policy_interpretation_verified":False,
        "creator_role_verified":False,
        "community_consensus_verified":False,
        "source_ingested_and_reopened_in_slr":False,
        "wikidata_edit_authorised":False,
        "ao_dispatch_allowed":False,
    }
    result=project_source_replay_handoff(wrapper)
    ordinary=project_slr_handoff(native)
    assert result["slr_input"]==ordinary["slr_packet"]
    assert result["slr_source_seals"]==ordinary["slr_source_seals"]
    assert result["slr_event_anchors"]==ordinary["slr_event_anchors"]
    assert result["slr_source_inputs"]==sorted(source_inputs,key=lambda x:x["envelope"]["source_revision_ref"])
    assert result["normative_policy_hold"] is False
    assert result["historical_policy_window_source_witness"]==policy_window
    assert result["authority"]["candidate_only"]
    assert not result["authority"]["slr_pg_reopened"]
    assert result["independent_source_verification"]=="not_completed"
    assert not result["authority"]["wikidata_edit_authorised"]
    assert not result["authority"]["ao_dispatch_allowed"]
    assert build_default_registry().get_tool_spec(
        "itir.governance.wikidata_source_replay_handoff").read_only
    bad=deepcopy(wrapper)
    bad["historical_policy_interpretation_verified"]=True
    with pytest.raises(ToolInputError):
        project_source_replay_handoff(bad)
    bad=deepcopy(wrapper)
    bad["historical_policy_drift_status"]="closure_policy_not_examined"
    bad["historical_policy_window_source_witness"]=None
    pending=project_source_replay_handoff(bad)
    assert pending["normative_policy_hold"] is True
    bad["historical_policy_drift_status"]="changed_during_proposal_requires_independent_rule_adjudication"
    bad["historical_policy_window_source_witness"]=deepcopy(policy_window)
    bad["historical_policy_window_source_witness"]["comparison_status"]=bad["historical_policy_drift_status"]
    bad["historical_policy_window_source_witness"]["closing_policy_page_oldid"]+=1
    assert project_source_replay_handoff(bad)["normative_policy_hold"] is True
    bad=deepcopy(wrapper)
    bad["historical_policy_window_source_witness"]["policy_content_digest_ref"]="sha256:"+"0"*64
    with pytest.raises(ToolInputError):
        project_source_replay_handoff(bad)
    bad=deepcopy(wrapper)
    bad["source_revision_refs"].pop()
    with pytest.raises(ToolInputError):
        project_source_replay_handoff(bad)
    bad=deepcopy(wrapper)
    bad["source_revision_refs"].append(bad["source_revision_refs"][0])
    with pytest.raises(ToolInputError):
        project_source_replay_handoff(bad)
    bad=deepcopy(wrapper)
    bad["itir_slr_input"]["event_anchors"][0]["end_byte"]=0
    with pytest.raises(ToolInputError):
        project_source_replay_handoff(bad)
    bad=deepcopy(wrapper)
    bad["slr_source_inputs"][0]["canonical_text"]+=" tampered"
    with pytest.raises(ToolInputError):
        project_source_replay_handoff(bad)
    bad=deepcopy(wrapper)
    bad["slr_source_inputs"][0]["envelope"]["source_revision_ref"]="source-revision:sha256:"+"0"*64
    with pytest.raises(ToolInputError):
        project_source_replay_handoff(bad)
