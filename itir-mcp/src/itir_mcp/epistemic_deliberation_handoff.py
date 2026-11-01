"""Candidate-only transport into SLR's native source/span-sealed governance ABI.

Reuse the generic ITIR assessment. Only SLR may reopen and verify persisted
canonical source bytes and execute S29 review. This pure adapter NEVER claims
that a supplied digest, event span or Wikidata property was verified.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping

from .contracts import ToolInputError
from .epistemic_deliberation import _ref, _time, assess_deliberation

VERSION = "itir.governance.deliberation_slr_handoff.v1"
MAX_SEALS = 130
_SHA = "0123456789abcdef"


def _sha(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.startswith("sha256:") or len(value) != 71 or any(c not in _SHA for c in value[7:]):
        raise ToolInputError(f"{field} must be lowercase sha256:<64 hex>")
    return value


def _unconstrained_claims(deliberation: Mapping[str, Any]) -> dict[str, Any]:
    """Deterministically translate the same fields as SLR DeliberationPacket."""
    items = []
    for event in deliberation["events"]:
        instant = _time(event["at"], "event.at")
        if instant.microsecond or instant < datetime(1970, 1, 1, tzinfo=timezone.utc):
            raise ToolInputError("SLR requires whole, nonnegative Unix seconds")
        items.append({
            "event_ref": event["event_ref"],
            "source_revision_ref": event["source_revision_ref"],
            "actor_ref": event["actor_ref"],
            "at_unix_seconds": int(instant.timestamp()),
            "kind": event["kind"],
            "supersedes_ref": event.get("supersedes_ref"),
            "judgement": event.get("judgement"),
            "consensus_assessment_ref": event.get("consensus_assessment_ref"),
            "authority_receipt_ref": event.get("authority_receipt_ref"),
        })
    return {
        "proposal_ref": deliberation["proposal_ref"],
        "source_revision_ref": deliberation["source_revision_ref"],
        "policy_revision_ref": deliberation["policy_revision_ref"],
        "minimum_age_seconds": deliberation["minimum_age_seconds"],
        "events": items,
        "created_property_ref": deliberation.get("created_property_ref"),
    }


def project_slr_handoff(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Expose exactly the source/anchor obligations needed by SLR persistence.

    This is a type/shape inspection of caller-supplied coordinates, never an
    SLR PG read. The output's source_binding_status stays unverified.
    """
    if not isinstance(payload, Mapping) or set(payload) != {"deliberation", "source_seals", "event_anchors"}:
        raise ToolInputError("expected exactly deliberation, source_seals and event_anchors")
    deliberation = payload["deliberation"]
    if not isinstance(deliberation, Mapping):
        raise ToolInputError("deliberation must be an object")
    assessed = assess_deliberation(deliberation)
    packet = _unconstrained_claims(deliberation)
    expected_sources = {packet["source_revision_ref"], packet["policy_revision_ref"]}
    expected_sources.update(e["source_revision_ref"] for e in packet["events"])
    raw_seals = payload["source_seals"]
    if not isinstance(raw_seals, list) or not 1 <= len(raw_seals) <= MAX_SEALS:
        raise ToolInputError("source seals must be bounded")
    source_map: dict[str, dict[str, Any]] = {}
    for seal in raw_seals:
        if not isinstance(seal, Mapping) or set(seal) != {
            "source_revision_ref", "content_digest_ref", "acquisition_receipt_ref"
        }:
            raise ToolInputError("invalid source seal fields")
        source = _ref(seal["source_revision_ref"], "source_revision_ref")
        digest = _sha(seal["content_digest_ref"], "content_digest_ref")
        receipt = _ref(seal["acquisition_receipt_ref"], "acquisition_receipt_ref")
        if source in source_map:
            raise ToolInputError("duplicate source seal")
        source_map[source] = {
            "source_revision_ref": source, "content_digest_ref": digest,
            "acquisition_receipt_ref": receipt,
        }
    if set(source_map) != expected_sources:
        raise ToolInputError("source seals must cover proposal, policy and every event exactly")
    raw_anchors = payload["event_anchors"]
    if not isinstance(raw_anchors, list) or len(raw_anchors) != len(packet["events"]):
        raise ToolInputError("each recorded event requires an exact native source span")
    event_map = {e["event_ref"]: e for e in packet["events"]}
    anchors: dict[str, dict[str, Any]] = {}
    for anchor in raw_anchors:
        if not isinstance(anchor, Mapping) or set(anchor) != {
            "event_ref", "source_revision_ref", "start_byte", "end_byte", "excerpt_digest_ref"
        }:
            raise ToolInputError("invalid event anchor fields")
        ref = _ref(anchor["event_ref"], "event_ref")
        source = _ref(anchor["source_revision_ref"], "source_revision_ref")
        start, end = anchor["start_byte"], anchor["end_byte"]
        if ref not in event_map or ref in anchors or source != event_map[ref]["source_revision_ref"]:
            raise ToolInputError("event anchor does not match source-pinned event")
        if type(start) is not int or type(end) is not int or start < 0 or end <= start:
            raise ToolInputError("event span must be a positive byte interval")
        anchors[ref] = {
            "event_ref": ref, "source_revision_ref": source,
            "start_byte": start, "end_byte": end,
            "excerpt_digest_ref": _sha(anchor["excerpt_digest_ref"], "excerpt_digest_ref"),
        }
    if len(anchors) != len(event_map):
        raise ToolInputError("missing event anchor")
    return {
        "version": VERSION,
        "slr_packet": packet,
        "slr_source_seals": [source_map[ref] for ref in sorted(source_map)],
        "slr_event_anchors": [anchors[ref] for ref in sorted(anchors)],
        "slr_consumer_contract": "existing S29 OntologyDiagnostic; source reopen required",
        "itil_accepted_review_states": ["needs_evidence", "qualified", "abstained"],
        "record_completeness": assessed["record_completeness"],
        "recorded_judgement": assessed["recorded_judgement"],
        "holds": assessed["holds"],
        "source_binding_status": "caller_supplied_unverified",
        "authority": {
            "candidate_only": True, "source_content_verified": False,
            "slr_pg_reopened": False, "s29_receipt_created": False,
            "community_consensus_verified": False, "wikidata_edit_authorised": False,
            "ao_dispatch_allowed": False,
        },
    }


def project_deliberation_consumer_link(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Join proposal history to an EXISTING generic review carrier by explicit
    source-local candidate coordinates. A property ID match is navigation only.
    """
    if not isinstance(payload, Mapping) or set(payload) != {
        "deliberation", "consumer_ref", "consumer_schema", "consumer_source_revision_ref",
        "subject_property_refs", "source_alignment_ref"
    }:
        raise ToolInputError("explicit consumer ref/schema/source alignment required")
    a = assess_deliberation(payload["deliberation"])
    consumer = _ref(payload["consumer_ref"], "consumer_ref")
    schema = _ref(payload["consumer_schema"], "consumer_schema")
    source = _ref(payload["consumer_source_revision_ref"], "consumer_source_revision_ref")
    alignment = _ref(payload["source_alignment_ref"], "source_alignment_ref")
    raw = payload["subject_property_refs"]
    if not isinstance(raw, list) or len(raw) > 64:
        raise ToolInputError("bounded subject property references required")
    refs = [_ref(x, "subject property ref") for x in raw]
    if len(set(refs)) != len(refs):
        raise ToolInputError("duplicate subject property references")
    created = a["created_property_ref"]
    hits = [p for p in refs if p == created]
    return {
        "version": "itir.governance.deliberation_consumer_link.v1",
        "proposal_ref": a["proposal_ref"], "consumer_ref": consumer,
        "consumer_schema": schema, "consumer_source_revision_ref": source,
        "source_alignment_ref": alignment, "property_ref_exact_hits": hits,
        "diagnostic_packet_ref": a["packet_ref"],
        "unpaid_obligations": [
            "source_alignment_ref_is_unverified",
            "slr_source_reopen_and_s29_receipt_required",
            "external_wikidata_role_and_consensus_not_verified",
            "consumer_structural_diagnostics_remain_independent",
        ],
        "authority": {
            "candidate_only": True, "identity_equivalence_proved": False,
            "source_alignment_verified": False, "statement_truth_promoted": False,
            "repair_authorised": False, "wikidata_edit_authorised": False,
            "ao_dispatch_allowed": False,
        },
    }


def project_source_replay_handoff(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Consume SensibLaw's *actual captured-revision* native transport envelope.

    SensibLaw owns source-byte projection; this adapter only validates the
    wrapper guard and delegates to the existing generic SLR ABI validator.
    Neither code path can independently authenticate a MediaWiki HTTP result.
    """
    if not isinstance(payload, Mapping) or payload.get("schema_version") != (
        "sl.wikidata_deliberation_slr_handoff_draft.v0_1"
    ):
        raise ToolInputError("expected the SensibLaw historical source handoff schema")
    for field in (
        "independent_source_provider_receipts_verified",
        "historical_policy_applicability_verified",
        "historical_policy_interpretation_verified",
        "creator_role_verified",
        "community_consensus_verified",
        "source_ingested_and_reopened_in_slr",
        "wikidata_edit_authorised",
        "ao_dispatch_allowed",
    ):
        if payload.get(field) is not False:
            raise ToolInputError(f"historical producer cannot claim {field} as verified")
    if payload.get("candidate_only") is not True or (
        payload.get("producer_canonical_byte_digests_observed") is not True
    ):
        raise ToolInputError("historical source projection must be candidate-only")
    policy_drift=payload.get("historical_policy_drift_status")
    if policy_drift not in (
        "closure_policy_not_examined",
        "unchanged_across_proposal_window",
        "changed_during_proposal_requires_independent_rule_adjudication",
    ):
        raise ToolInputError("historical policy must retain an explicit opening/closure drift status")
    p=payload.get("itir_slr_input")
    if not isinstance(p,Mapping):
        raise ToolInputError("historical wrapper is missing native SLR input")
    inspected=project_slr_handoff(p)
    revisions=payload.get("source_revision_refs")
    if not isinstance(revisions,list) or any(not isinstance(ref,str) for ref in revisions):
        raise ToolInputError("historical source revision refs must be an explicit list")
    if len(revisions)!=len(set(revisions)) or set(revisions) != {
        seal["source_revision_ref"] for seal in inspected["slr_source_seals"]
    }:
        raise ToolInputError("historical wrapper source revision set differs from source seals")
    # Source bytes and source identities must correspond to the original
    # INGEST-1 owner, not merely claim identical source revision *strings*.
    # The exact cross-language framed identity is independently checked here.
    import hashlib
    raw_inputs=payload.get("slr_source_inputs")
    if not isinstance(raw_inputs,list) or len(raw_inputs)!=len(inspected["slr_source_seals"]):
        raise ToolInputError("historical replay requires every original source input and text")
    by_source={row["source_revision_ref"]:row for row in inspected["slr_source_seals"]}
    observed=set()
    source_inputs=[]
    for input_row in raw_inputs:
        if not isinstance(input_row,Mapping) or set(input_row)!={"envelope","canonical_text"}:
            raise ToolInputError("invalid canonical source input fields")
        envelope=input_row["envelope"]
        canonical_text=input_row["canonical_text"]
        expected_keys={
            "source_ref","source_revision_ref","provider_ref","family","role_class",
            "content_digest_ref","acquisition_receipt_ref","media_type_ref",
            "candidate_only","creates_semantic_authority","applicability_promoted",
            "claim_truth_promoted",
        }
        if not isinstance(envelope,Mapping) or set(envelope)!=expected_keys:
            raise ToolInputError("incorrect INGEST-1 source envelope grammar")
        if not isinstance(canonical_text,str) or not canonical_text or len(canonical_text.encode("utf-8"))>4_000_000:
            raise ToolInputError("missing or unbounded canonical source text")
        for field in ("source_ref","source_revision_ref","provider_ref",
                      "content_digest_ref","acquisition_receipt_ref","media_type_ref"):
            _ref(envelope[field],field)
        if envelope["family"]!="wiki" or envelope["role_class"]!="content_source":
            raise ToolInputError("historical source must be Wiki/ContentSource")
        if envelope["provider_ref"]!="wikidata:mediawiki-api" or envelope["media_type_ref"]!="text/x-wiki":
            raise ToolInputError("source provenance or type mismatch")
        if envelope["candidate_only"] is not True or any(
            envelope[field] is not False for field in (
                "creates_semantic_authority","applicability_promoted","claim_truth_promoted")
        ):
            raise ToolInputError("source envelope attempts authority promotion")
        content_sha="sha256:"+hashlib.sha256(canonical_text.encode("utf-8")).hexdigest()
        if content_sha!=envelope["content_digest_ref"]:
            raise ToolInputError("source content digest does not match original canonical bytes")
        # Mirrors only the *identity framing* of SLR's
        # canonical_generic_source_revision_ref, not its source persistence.
        hasher=hashlib.sha256()
        for field in (
            "generic-source-revision:v1",envelope["source_ref"],
            envelope["provider_ref"],envelope["acquisition_receipt_ref"],
            content_sha,envelope["media_type_ref"]
        ):
            raw=field.encode("utf-8")
            hasher.update(len(raw).to_bytes(8,"big"))
            hasher.update(raw)
        revision="source-revision:sha256:"+hasher.hexdigest()
        if revision!=envelope["source_revision_ref"]:
            raise ToolInputError("INGEST-1 canonical source-revision identity mismatch")
        if revision in observed or revision not in by_source:
            raise ToolInputError("duplicate or missing source in replay")
        observed.add(revision)
        receipt=by_source[revision]
        if (receipt["content_digest_ref"]!=content_sha or
                receipt["acquisition_receipt_ref"]!=envelope["acquisition_receipt_ref"]):
            raise ToolInputError("source seal differs from canonical envelope")
        source_inputs.append({
            "envelope":dict(envelope),"canonical_text":canonical_text
        })
    if observed!=set(by_source):
        raise ToolInputError("historical source content set is incomplete")
    content_by_ref={s["envelope"]["source_revision_ref"]:s["canonical_text"].encode("utf-8")
                    for s in source_inputs}
    for anchor in inspected["slr_event_anchors"]:
        source=content_by_ref[anchor["source_revision_ref"]]
        start,end=anchor["start_byte"],anchor["end_byte"]
        if end>len(source) or "sha256:"+hashlib.sha256(source[start:end]).hexdigest()!=anchor["excerpt_digest_ref"]:
            raise ToolInputError("source event byte-span/hash mismatch")
    source_inputs.sort(key=lambda x:x["envelope"]["source_revision_ref"])
    window = payload.get("historical_policy_window_source_witness")
    if policy_drift == "closure_policy_not_examined":
        if window is not None:
            raise ToolInputError("unexamined policy cannot have a closure-window witness")
    else:
        required_window = {
            "opening_policy_page_oldid", "closing_policy_page_oldid",
            "opening_policy_revision_time", "closing_policy_revision_time",
            "policy_content_digest_ref", "closing_policy_content_digest_ref",
            "closing_acquisition_url", "comparison_status", "candidate_only",
            "policy_normatively_verified",
        }
        if not isinstance(window, Mapping) or set(window)!=required_window:
            raise ToolInputError("closure policy needs the full source-window witness")
        if window["comparison_status"]!=policy_drift or window["candidate_only"] is not True or (
            window["policy_normatively_verified"] is not False
        ):
            raise ToolInputError("policy window cannot promote authority")
        opening,closing=window["opening_policy_page_oldid"],window["closing_policy_page_oldid"]
        if type(opening) is not int or type(closing) is not int or min(opening,closing)<1:
            raise ToolInputError("policy window must retain exact positive oldids")
        if not isinstance(window["closing_acquisition_url"],str) or not (
            window["closing_acquisition_url"].startswith("https://www.wikidata.org/w/api.php?")
        ):
            raise ToolInputError("policy window closing source origin missing")
        policy_input = next((
            input_row for input_row in source_inputs
            if input_row["envelope"]["source_revision_ref"]==inspected["slr_packet"]["policy_revision_ref"]
        ),None)
        if policy_input is None or policy_input["envelope"]["source_ref"] != f"wikidata:page:{opening}":
            raise ToolInputError("historical policy opening oldid disagrees with canonical source")
        if window["policy_content_digest_ref"] != policy_input["envelope"]["content_digest_ref"]:
            raise ToolInputError("policy opening SHA differs from canonical source")
        _sha(window["closing_policy_content_digest_ref"],"closing_policy_content_digest_ref")
        if policy_drift == "unchanged_across_proposal_window" and (
            opening != closing
            or window["closing_policy_content_digest_ref"]!=window["policy_content_digest_ref"]
        ):
            raise ToolInputError("unchanged historical policy must have identical revision and bytes")
        if policy_drift.startswith("changed_during") and (
            opening == closing and
            window["closing_policy_content_digest_ref"]==window["policy_content_digest_ref"]
        ):
            raise ToolInputError("changed historical policy must contain an observed difference")
        start=_time(window["opening_policy_revision_time"],"opening_policy_revision_time")
        stop=_time(window["closing_policy_revision_time"],"closing_policy_revision_time")
        if start>stop or stop>_time(p["deliberation"]["events"][-1]["at"], "proposal closure"):
            raise ToolInputError("policy revision times must precede closure")
    return {
        "version":"itir.governance.wikidata_source_replay_handoff.v1",
        "origin":"sl.wikidata_deliberation_slr_handoff_draft.v0_1",
        "slr_input":inspected["slr_packet"],
        "slr_source_seals":inspected["slr_source_seals"],
        "slr_event_anchors":inspected["slr_event_anchors"],
        "slr_source_inputs":source_inputs,
        "historical_policy_drift_status":policy_drift,
        "historical_policy_window_source_witness":dict(window) if window is not None else None,
        "normative_policy_hold":policy_drift!="unchanged_across_proposal_window",
        "holds":inspected["holds"],
        "record_completeness":inspected["record_completeness"],
        "scope":"not_assigned_until_s29",
        "independent_source_verification":"not_completed",
        "community_creator_role_verification":"not_completed",
        "community_consensus_verification":"not_completed",
        "authority":{
            "candidate_only":True,"slr_pg_reopened":False,
            "community_consensus_verified":False,
            "wikidata_edit_authorised":False,"ao_dispatch_allowed":False,
        },
    }
