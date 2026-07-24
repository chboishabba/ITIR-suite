from __future__ import annotations

import json
from hashlib import sha256
from typing import Any, Mapping, Sequence

from .contracts import JsonDict, ToolHandler, ToolInputError, ToolSpec


PROPOSAL_RECEIPT_VERSION = "itir.docstore.proposal_receipt.v1"

_ALLOWED_HINT_LEVELS = {"structured_hint", "candidate_hint"}
_ALLOWED_ACTIONS = {"draft", "review", "reject", "hold", "mark_promotable"}
_STATUS_BY_ACTION = {
    "draft": "proposal_receipt_draft",
    "review": "reviewed",
    "reject": "rejected",
    "hold": "held",
    "mark_promotable": "promotable",
}
_REQUIRED_HINT_FIELDS = (
    "source_system",
    "lane",
    "artifact_id",
    "item_id",
    "status",
    "pressure_kind",
    "question_text_or_reason",
    "authority_class",
    "provenance_refs",
    "promotion_level",
)


def get_promotion_tools() -> list[tuple[ToolSpec, ToolHandler]]:
    return [
        (
            ToolSpec(
                name="itir.docstore.proposal_receipt",
                title="ITIR docstore proposal receipt",
                description=(
                    "Build non-authoritative review receipts for structured_hint and "
                    "candidate_hint docstore records without mutating promoted truth."
                ),
                input_schema=_proposal_receipt_input_schema(),
                response_version=PROPOSAL_RECEIPT_VERSION,
                read_only=True,
            ),
            proposal_receipt,
        )
    ]


def proposal_receipt(payload: Mapping[str, Any]) -> JsonDict:
    hints = _payload_hints(payload)
    receipts = [_build_receipt(payload, hint) for hint in hints]
    if "hints" in payload:
        return {
            "version": PROPOSAL_RECEIPT_VERSION,
            "receipt_count": len(receipts),
            "receipts": receipts,
        }
    return receipts[0]


def _proposal_receipt_input_schema() -> JsonDict:
    return {
        "type": "object",
        "properties": {
            "hint": {"type": "object"},
            "hints": {"type": "array", "items": {"type": "object"}},
            "review": {"type": "object"},
            "reviewer_id": {"type": "string"},
            "reviewer_role": {"type": "string"},
            "review_action": {"type": "string", "enum": sorted(_ALLOWED_ACTIONS)},
            "reviewed_at": {"type": "string"},
            "decision_reason": {"type": "string"},
            "downstream_promotion_authority": {"type": "object"},
        },
        "required": [],
        "additionalProperties": True,
    }


def _payload_hints(payload: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    if "hint" in payload and "hints" in payload:
        raise ToolInputError("provide either hint or hints, not both")
    hint = payload.get("hint")
    if isinstance(hint, Mapping):
        return [hint]
    hints = payload.get("hints")
    if isinstance(hints, Sequence) and not isinstance(hints, (str, bytes, bytearray)):
        out: list[Mapping[str, Any]] = []
        for item in hints:
            if not isinstance(item, Mapping):
                raise ToolInputError("Expected object entries in hints")
            out.append(item)
        if not out:
            raise ToolInputError("hints must not be empty")
        return out
    raise ToolInputError("Expected object field: hint")


def _build_receipt(payload: Mapping[str, Any], raw_hint: Mapping[str, Any]) -> JsonDict:
    hint = _validated_hint(raw_hint)
    review = _validated_review(payload)
    hint_hash = _hash_json(hint)
    proposal_id = "itir.proposal:" + _hash_json(
        {
            "artifact_id": hint["artifact_id"],
            "item_id": hint["item_id"],
            "promotion_level": hint["promotion_level"],
            "hint_hash": hint_hash,
        },
        bare=True,
    )

    gates = _decision_gates(hint, review)
    requested_action = str(review["review_action"])
    effective_status = _STATUS_BY_ACTION[requested_action]
    if requested_action == "mark_promotable" and not gates["downstream_authority_present"]:
        effective_status = "held"

    receipt_body = {
        "version": PROPOSAL_RECEIPT_VERSION,
        "schema_version": PROPOSAL_RECEIPT_VERSION,
        "proposal_id": proposal_id,
        "hint_hash": hint_hash,
        "source_hint": hint,
        "review": review,
        "decision": {
            "requested_action": requested_action,
            "status": effective_status,
            "promotion_level": "proposal_receipt",
            "eligible_for_external_promotion": effective_status == "promotable",
            "canonical_truth_mutated": False,
            "non_authoritative": True,
            "authority_notice": (
                "This receipt is non-authoritative until a separate external "
                "promotion process accepts it. Candidate hints do not become facts here."
            ),
        },
        "decision_gates": gates,
        "provenance_refs": _receipt_provenance_refs(hint, hint_hash),
        "authority_class": "non_authoritative_review_receipt",
    }
    receipt_hash = _hash_json(receipt_body)
    return {
        **receipt_body,
        "receipt_id": "itir.proposal_receipt:" + receipt_hash.removeprefix("sha256:"),
        "receipt_hash": receipt_hash,
    }


def _validated_hint(raw_hint: Mapping[str, Any]) -> JsonDict:
    missing = [field for field in _REQUIRED_HINT_FIELDS if not _present(raw_hint.get(field))]
    if missing:
        raise ToolInputError("hint is missing required fields", details={"missing": missing})
    promotion_level = str(raw_hint.get("promotion_level") or "").strip()
    if promotion_level not in _ALLOWED_HINT_LEVELS:
        raise ToolInputError(
            "hint promotion_level must be structured_hint or candidate_hint",
            details={"promotion_level": promotion_level},
        )
    provenance_refs = raw_hint.get("provenance_refs")
    if not isinstance(provenance_refs, Sequence) or isinstance(provenance_refs, (str, bytes, bytearray)):
        raise ToolInputError("hint provenance_refs must be an array")

    return {
        "source_system": str(raw_hint["source_system"]).strip(),
        "lane": str(raw_hint["lane"]).strip(),
        "artifact_id": str(raw_hint["artifact_id"]).strip(),
        "item_id": str(raw_hint["item_id"]).strip(),
        "status": str(raw_hint["status"]).strip(),
        "pressure_kind": str(raw_hint["pressure_kind"]).strip(),
        "question_text_or_reason": str(raw_hint["question_text_or_reason"]).strip(),
        "authority_class": str(raw_hint["authority_class"]).strip(),
        "provenance_refs": [dict(item) for item in provenance_refs if isinstance(item, Mapping)],
        "promotion_level": promotion_level,
    }


def _validated_review(payload: Mapping[str, Any]) -> JsonDict:
    review_payload = payload.get("review") if isinstance(payload.get("review"), Mapping) else {}
    review = {
        "reviewer_id": _review_value(payload, review_payload, "reviewer_id"),
        "reviewer_role": _review_value(payload, review_payload, "reviewer_role") or "human_reviewer",
        "review_action": _review_value(payload, review_payload, "review_action"),
        "reviewed_at": _review_value(payload, review_payload, "reviewed_at"),
        "decision_reason": _review_value(payload, review_payload, "decision_reason"),
        "downstream_promotion_authority": _review_mapping(
            payload,
            review_payload,
            "downstream_promotion_authority",
        ),
    }
    missing = [
        field
        for field in ("reviewer_id", "review_action", "reviewed_at", "decision_reason")
        if not _present(review.get(field))
    ]
    if missing:
        raise ToolInputError("review is missing required fields", details={"missing": missing})
    if review["review_action"] not in _ALLOWED_ACTIONS:
        raise ToolInputError(
            "review_action is not allowed",
            details={"allowed_actions": sorted(_ALLOWED_ACTIONS), "review_action": review["review_action"]},
        )
    return review


def _decision_gates(hint: Mapping[str, Any], review: Mapping[str, Any]) -> JsonDict:
    authority = review.get("downstream_promotion_authority")
    authority_present = isinstance(authority, Mapping) and bool(authority)
    requested_action = str(review.get("review_action") or "")
    return {
        "allowed_hint_level": hint.get("promotion_level") in _ALLOWED_HINT_LEVELS,
        "reviewer_identity_present": bool(str(review.get("reviewer_id") or "").strip()),
        "review_action_allowed": requested_action in _ALLOWED_ACTIONS,
        "decision_reason_present": bool(str(review.get("decision_reason") or "").strip()),
        "downstream_authority_present": authority_present,
        "external_authority_required_for_promotable": requested_action == "mark_promotable",
        "can_be_promotable": requested_action == "mark_promotable" and authority_present,
        "canonical_truth_mutation_allowed": False,
        "candidate_hint_fact_guard": hint.get("promotion_level") == "candidate_hint",
    }


def _receipt_provenance_refs(hint: Mapping[str, Any], hint_hash: str) -> list[JsonDict]:
    refs = [dict(item) for item in hint.get("provenance_refs") or [] if isinstance(item, Mapping)]
    refs.append(
        {
            "kind": "docstore_hint",
            "artifact_id": hint["artifact_id"],
            "item_id": hint["item_id"],
            "hint_hash": hint_hash,
        }
    )
    return refs


def _review_value(payload: Mapping[str, Any], review: Mapping[str, Any], key: str) -> str:
    value = review.get(key, payload.get(key))
    return str(value).strip() if value is not None else ""


def _review_mapping(payload: Mapping[str, Any], review: Mapping[str, Any], key: str) -> JsonDict | None:
    value = review.get(key, payload.get(key))
    if value is None:
        return None
    if not isinstance(value, Mapping):
        raise ToolInputError(f"Expected object field: {key}")
    return dict(value)


def _present(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return bool(value)
    return value is not None


def _hash_json(payload: Mapping[str, Any], *, bare: bool = False) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    digest = sha256(encoded.encode("utf-8")).hexdigest()
    return digest if bare else "sha256:" + digest
