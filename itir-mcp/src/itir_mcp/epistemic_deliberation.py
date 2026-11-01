"""Generic, source-pinned deliberation assessment for ontology/workflow evolution.

Roszkowski (2024; Wikimedia CEE 2026) motivates proposal -> knowledge work ->
closure. This is an ITIR diagnostic projection, not consensus computation.
SLR owns persisted source/review state; AO may reference the resulting
candidate packet but cannot dispatch or promote based on this assessment.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone
from typing import Any, Mapping

from .contracts import ToolInputError

VERSION = "itir.governance.deliberation_assessment.v1"
KINDS = {"proposal", "support", "objection", "amendment", "decision"}
JUDGEMENTS = {"approve", "reject", "defer"}
MAX_EVENTS = 128
MAX_REF_LENGTH = 512


def _ref(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > MAX_REF_LENGTH or any(ord(c) < 32 for c in value):
        raise ToolInputError(f"{field} requires a bounded, nonempty source reference")
    return value


def _time(value: Any, field: str) -> datetime:
    if not isinstance(value, str):
        raise ToolInputError(f"{field} requires an ISO-8601 timestamp")
    try:
        t = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ToolInputError(f"{field} requires an ISO-8601 timestamp") from exc
    if t.tzinfo is None or t.utcoffset() is None:
        raise ToolInputError(f"{field} must retain an explicit timezone")
    return t.astimezone(timezone.utc)


def assess_deliberation(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Assess *record completeness*, never infer epistemic agreement or authority.

    Caller-supplied decision and authority refs are claims requiring independent
    verification in the SLR source/S29 and community governance boundaries.
    """
    if not isinstance(payload, Mapping) or set(payload) - {
        "proposal_ref", "source_revision_ref", "policy_revision_ref",
        "minimum_age_seconds", "events", "created_property_ref",
    }:
        raise ToolInputError("unknown deliberation assessment fields")
    proposal = _ref(payload.get("proposal_ref"), "proposal_ref")
    source = _ref(payload.get("source_revision_ref"), "source_revision_ref")
    policy = _ref(payload.get("policy_revision_ref"), "policy_revision_ref")
    minimum = payload.get("minimum_age_seconds")
    if type(minimum) is not int or not 0 <= minimum <= 366 * 86400:
        raise ToolInputError("minimum_age_seconds must be an explicit bounded policy threshold")
    events = payload.get("events")
    if not isinstance(events, list) or not 1 <= len(events) <= MAX_EVENTS:
        raise ToolInputError("events must contain 1..128 source-pinned events")
    if "created_property_ref" in payload:
        _ref(payload["created_property_ref"], "created_property_ref")

    seen: set[str] = set()
    items: list[dict[str, Any]] = []
    prior: datetime | None = None
    for i, event in enumerate(events):
        if not isinstance(event, Mapping) or set(event) - {
            "event_ref", "source_revision_ref", "actor_ref", "at",
            "kind", "judgement", "consensus_assessment_ref",
            "authority_receipt_ref", "supersedes_ref",
        }:
            raise ToolInputError("unknown deliberation event fields")
        ref = _ref(event.get("event_ref"), "event_ref")
        actor = _ref(event.get("actor_ref"), "actor_ref")
        event_source = _ref(event.get("source_revision_ref"), "event source_revision_ref")
        kind = event.get("kind")
        if not isinstance(kind, str) or kind not in KINDS or ref in seen:
            raise ToolInputError("invalid or duplicate event kind/ref")
        instant = _time(event.get("at"), "event.at")
        if prior is not None and instant < prior:
            raise ToolInputError("events must be ordered by occurrence time")
        if i == 0 and kind != "proposal" or i > 0 and kind == "proposal":
            raise ToolInputError("exactly one initial proposal event is required")
        if prior is not None and items[-1]["kind"] == "decision":
            raise ToolInputError("no events may follow the terminal decision")
        has_decision_fields = any(key in event for key in (
            "judgement", "consensus_assessment_ref", "authority_receipt_ref"))
        if kind != "decision" and has_decision_fields:
            raise ToolInputError("only decisions carry judgement and governance refs")
        if kind == "decision":
            if not isinstance(event.get("judgement"), str) or event["judgement"] not in JUDGEMENTS:
                raise ToolInputError("decision requires an explicit judgement")
            # These are source claims, not independently verified attestations.
            if "consensus_assessment_ref" in event:
                _ref(event["consensus_assessment_ref"], "consensus_assessment_ref")
            if "authority_receipt_ref" in event:
                _ref(event["authority_receipt_ref"], "authority_receipt_ref")
        if "supersedes_ref" in event:
            if kind != "amendment" or event["supersedes_ref"] == ref or event["supersedes_ref"] not in seen:
                raise ToolInputError("amendment must point to a prior recorded event")
        items.append(dict(event))
        seen.add(ref)
        prior = instant

    first = items[0]
    proposer = first["actor_ref"]
    decision = items[-1] if items[-1]["kind"] == "decision" else None
    independent = any(row["actor_ref"] != proposer and row["kind"] != "decision" for row in items[1:])
    holds: list[str] = []
    if not independent:
        holds.append("independent_participation_not_observed")
    if decision is None:
        holds.append("no_terminal_decision")
    else:
        if decision["actor_ref"] == proposer:
            holds.append("decision_maker_equals_proposer")
        age = _time(decision["at"], "decision.at") - _time(first["at"], "proposal.at")
        if age <= timedelta(seconds=minimum):
            holds.append("minimum_proposal_age_not_met")
        if not decision.get("consensus_assessment_ref"):
            holds.append("consensus_judgement_source_missing")
        if not decision.get("authority_receipt_ref"):
            holds.append("decision_authority_source_missing")
        if decision["judgement"] == "approve" and "created_property_ref" not in payload:
            holds.append("created_property_identity_not_observed")
    # Even a complete packet cannot establish that the actor, votes, or
    # consensus were valid, or that any statement about an item is true.
    stable = {
        "proposal_ref": proposal, "source_revision_ref": source,
        "policy_revision_ref": policy, "minimum_age_seconds": minimum,
        "events": items, "created_property_ref": payload.get("created_property_ref"),
    }
    digest = hashlib.sha256(json.dumps(stable, sort_keys=True, separators=(",", ":"),
                                       ensure_ascii=True).encode()).hexdigest()
    return {
        "version": VERSION, "packet_ref": "deliberation:sha256:" + digest,
        "proposal_ref": proposal, "source_revision_ref": source,
        "policy_revision_ref": policy,
        "event_refs": [item["event_ref"] for item in items],
        "event_source_revision_refs": [item["source_revision_ref"] for item in items],
        "objection_refs": [item["event_ref"] for item in items if item["kind"] == "objection"],
        "amendment_refs": [item["event_ref"] for item in items if item["kind"] == "amendment"],
        "record_completeness": "needs_evidence" if holds else "reviewable",
        "holds": holds,
        "recorded_judgement": decision["judgement"] if decision else None,
        "recorded_consensus_ref": decision.get("consensus_assessment_ref") if decision else None,
        "recorded_authority_ref": decision.get("authority_receipt_ref") if decision else None,
        "created_property_ref": payload.get("created_property_ref"),
        "authority": {
            "candidate_only": True, "read_only": True, "semantic_truth_promoted": False,
            "community_consensus_verified": False, "actor_authority_verified": False,
            "wikidata_edit_authorised": False, "ao_dispatch_allowed": False,
            "slr_s29_review_bypassed": False,
        },
    }
