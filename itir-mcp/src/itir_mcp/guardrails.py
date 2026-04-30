from __future__ import annotations

from hashlib import sha256
from typing import Any, Iterable, Mapping

from .contracts import JsonDict, ToolPolicyError


_INJECTION_PATTERNS = (
    "ignore previous instructions",
    "ignore all previous instructions",
    "system prompt",
    "developer message",
    "override safety",
    "bypass policy",
)

_SECRET_PATTERNS = (
    "api key",
    "api keys",
    "password",
    "secret",
    "token",
    "credentials",
)

_COERCION_PATTERNS = (
    "help grandma is dying",
    "urgent",
    "immediately",
    "or i will",
)

_POLICY_REASON_META: dict[str, JsonDict] = {
    "social_engineering": {
        "control_id": "iso27001.A.5.17",
        "rule_id": "social_engineering",
        "why": "Input applies emotional coercion around a privileged or sensitive request.",
        "next_action": "block_and_report",
    },
    "sensitive_data_request": {
        "control_id": "iso27001.A.5.23",
        "rule_id": "sensitive_data_request",
        "why": "Input requests sensitive data that must not be disclosed without verified authority.",
        "next_action": "block_and_report",
    },
    "prompt_injection": {
        "control_id": "iso42001.prompt_integrity",
        "rule_id": "prompt_injection",
        "why": "Input attempts to override tool or agent instructions.",
        "next_action": "require_review",
    },
    "oversized_input": {
        "control_id": "iso27001.A.5.22",
        "rule_id": "oversized_input",
        "why": "Input exceeds the bounded review envelope and requires inspection.",
        "next_action": "require_review",
    },
    "missing_version": {
        "control_id": "iso42001.output_verification",
        "rule_id": "missing_version",
        "why": "Tool output omitted required contract version metadata.",
        "next_action": "abstain_and_audit",
    },
    "invalid_similarity": {
        "control_id": "iso42001.output_verification",
        "rule_id": "invalid_similarity",
        "why": "Tool output returned an invalid similarity score outside the declared contract range.",
        "next_action": "abstain_and_audit",
    },
    "missing_signals": {
        "control_id": "iso42001.output_verification",
        "rule_id": "missing_signals",
        "why": "Tool output omitted the declared signal breakdown required for verification.",
        "next_action": "abstain_and_audit",
    },
    "missing_text_overlap": {
        "control_id": "iso42001.output_verification",
        "rule_id": "missing_text_overlap",
        "why": "Tool output omitted the text overlap verification signal.",
        "next_action": "abstain_and_audit",
    },
    "missing_time_proximity": {
        "control_id": "iso42001.output_verification",
        "rule_id": "missing_time_proximity",
        "why": "Tool output omitted the time proximity verification signal.",
        "next_action": "abstain_and_audit",
    },
    "missing_geo_proximity": {
        "control_id": "iso42001.output_verification",
        "rule_id": "missing_geo_proximity",
        "why": "Tool output omitted the geo proximity verification signal.",
        "next_action": "abstain_and_audit",
    },
}

_REASON_PRIORITY = {
    "sensitive_data_request": 100,
    "social_engineering": 90,
    "prompt_injection": 80,
    "oversized_input": 70,
    "invalid_similarity": 60,
    "missing_signals": 50,
    "missing_text_overlap": 49,
    "missing_time_proximity": 48,
    "missing_geo_proximity": 47,
    "missing_version": 40,
}


def classify_tool_call(name: str, payload: Mapping[str, Any]) -> JsonDict:
    strings = list(_iter_strings(payload))
    lowered = [value.lower() for value in strings]
    reason_codes: list[str] = []
    details: JsonDict = {"tool": name, "string_field_count": len(strings)}

    if any(any(pattern in value for pattern in _INJECTION_PATTERNS) for value in lowered):
        reason_codes.append("prompt_injection")
    if any(any(pattern in value for pattern in _SECRET_PATTERNS) for value in lowered):
        reason_codes.append("sensitive_data_request")
    if any(any(pattern in value for pattern in _COERCION_PATTERNS) for value in lowered):
        reason_codes.append("social_engineering")

    max_string_length = max((len(value) for value in strings), default=0)
    details["max_string_length"] = max_string_length
    if max_string_length > 12000:
        reason_codes.append("oversized_input")

    decision = "allow"
    if {"sensitive_data_request", "social_engineering"} & set(reason_codes):
        decision = "reject"
    elif "prompt_injection" in reason_codes or "oversized_input" in reason_codes:
        decision = "review"

    return {
        "version": "itir.tool_guard.classification.v1",
        "tool": name,
        "decision": decision,
        "status_scope": "security",
        "status_value": "malicious_request" if decision == "reject" else ("needs_review" if decision == "review" else "allowed"),
        "status_bucket": "reject" if decision == "reject" else ("review" if decision == "review" else "allow"),
        "primary_reason_code": _primary_reason_code(reason_codes),
        "reason_codes": reason_codes,
        "details": details,
    }


def verify_tool_result(name: str, payload: Mapping[str, Any], result: Mapping[str, Any]) -> JsonDict:
    reason_codes: list[str] = []

    version = result.get("version")
    if not isinstance(version, str) or not version.strip():
        reason_codes.append("missing_version")

    if name == "itir.compare_observations":
        similarity = result.get("similarity")
        if not isinstance(similarity, (int, float)) or not 0.0 <= float(similarity) <= 1.0:
            reason_codes.append("invalid_similarity")
        signals = result.get("signals")
        if not isinstance(signals, Mapping):
            reason_codes.append("missing_signals")
        else:
            for key in ("text_overlap", "time_proximity", "geo_proximity"):
                if key not in signals:
                    reason_codes.append(f"missing_{key}")

    decision = "verified" if not reason_codes else "abstain"
    return {
        "version": "itir.tool_guard.verification.v1",
        "tool": name,
        "decision": decision,
        "primary_reason_code": _primary_reason_code(reason_codes),
        "reason_codes": reason_codes,
        "payload_hash": _stable_hash(payload),
        "result_hash": _stable_hash(result),
    }


def build_governance_receipt(
    *,
    name: str,
    payload: Mapping[str, Any],
    classification: Mapping[str, Any],
    decision: str,
    verification: Mapping[str, Any] | None = None,
) -> JsonDict:
    reason_codes = _merged_reason_codes(classification, verification)
    primary_reason_code = _primary_reason_code(reason_codes)
    policy_meta = _policy_meta(primary_reason_code)
    return {
        "version": "itir.tool_guard.receipt.v1",
        "event": _receipt_event(decision),
        "tool": name,
        "policy_id": "itir.mcp.guard.minimal.v1",
        "control_id": policy_meta.get("control_id"),
        "rule_id": policy_meta.get("rule_id"),
        "input_hash": _stable_hash(payload),
        "primary_reason_code": primary_reason_code,
        "reason_codes": reason_codes,
        "classification_reason_codes": list(classification.get("reason_codes") or []),
        "verification_reason_codes": list((verification or {}).get("reason_codes") or []),
        "decision": decision,
    }


def safe_tool_call(registry, name: str, payload: Mapping[str, Any]) -> JsonDict:
    classification = classify_tool_call(name, payload)
    if classification["decision"] == "reject":
        receipt = build_governance_receipt(
            name=name,
            payload=payload,
            classification=classification,
            decision="rejected",
        )
        return {
            "version": "itir.safe_tool_call.v1",
            "tool": name,
            "decision": "rejected",
            "classification": classification,
            "verification": None,
            "policy_outcomes": _build_policy_outcomes(classification=classification, verification=None, decision="rejected"),
            "status_explanation": _build_status_explanation(classification=classification, verification=None, decision="rejected"),
            "receipt": receipt,
            "result": None,
        }

    invoked = registry.invoke(name, payload)
    if invoked.get("ok") is False:
        raise ToolPolicyError(
            str((invoked.get("error") or {}).get("message") or "tool invocation failed"),
            details={"tool": name, "upstream_error": invoked.get("error")},
        )

    result = invoked.get("result")
    if not isinstance(result, Mapping):
        raise ToolPolicyError("tool result must be an object", details={"tool": name})

    verification = verify_tool_result(name, payload, result)
    decision = "verified" if verification["decision"] == "verified" and classification["decision"] == "allow" else "abstained"
    receipt = build_governance_receipt(
        name=name,
        payload=payload,
        classification=classification,
        verification=verification,
        decision=decision,
    )
    return {
        "version": "itir.safe_tool_call.v1",
        "tool": name,
        "decision": decision,
        "classification": classification,
        "verification": verification,
        "policy_outcomes": _build_policy_outcomes(
            classification=classification,
            verification=verification,
            decision=decision,
        ),
        "status_explanation": _build_status_explanation(
            classification=classification,
            verification=verification,
            decision=decision,
        ),
        "receipt": receipt,
        "result": dict(result),
    }


def _iter_strings(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
        return
    if isinstance(value, Mapping):
        for item in value.values():
            yield from _iter_strings(item)
        return
    if isinstance(value, (list, tuple)):
        for item in value:
            yield from _iter_strings(item)


def _stable_hash(value: Any) -> str:
    return sha256(repr(value).encode("utf-8", errors="ignore")).hexdigest()


def _receipt_event(decision: str) -> str:
    if decision == "rejected":
        return "tool_call_rejected"
    if decision == "abstained":
        return "tool_output_abstained"
    return "tool_output_verified"


def _merged_reason_codes(
    classification: Mapping[str, Any],
    verification: Mapping[str, Any] | None,
) -> list[str]:
    merged: list[str] = []
    for code in list(classification.get("reason_codes") or []) + list((verification or {}).get("reason_codes") or []):
        text = str(code or "").strip()
        if text and text not in merged:
            merged.append(text)
    return merged


def _primary_reason_code(reason_codes: Iterable[Any]) -> str | None:
    normalized = [str(code or "").strip() for code in reason_codes]
    normalized = [code for code in normalized if code]
    if not normalized:
        return None
    return max(normalized, key=lambda code: (_REASON_PRIORITY.get(code, 0), -normalized.index(code)))


def _policy_meta(reason_code: str | None) -> JsonDict:
    if reason_code and reason_code in _POLICY_REASON_META:
        return dict(_POLICY_REASON_META[reason_code])
    return {
        "control_id": "itir.guard.general",
        "rule_id": str(reason_code or "verified"),
        "why": "Tool request completed within the bounded guard policy.",
        "next_action": "record_state",
    }


def _build_policy_outcomes(
    *,
    classification: Mapping[str, Any],
    verification: Mapping[str, Any] | None,
    decision: str,
) -> list[JsonDict]:
    outcomes: list[JsonDict] = []
    for code in _merged_reason_codes(classification, verification):
        meta = _policy_meta(code)
        status = "deny" if decision == "rejected" else ("deny" if decision == "abstained" else "allow")
        outcomes.append(
            {
                "control_id": meta["control_id"],
                "rule_id": meta["rule_id"],
                "status": status,
                "reason_code": code,
            }
        )
    if outcomes:
        return outcomes
    meta = _policy_meta(None)
    return [
        {
            "control_id": meta["control_id"],
            "rule_id": meta["rule_id"],
            "status": "allow",
            "reason_code": "verified",
        }
    ]


def _build_status_explanation(
    *,
    classification: Mapping[str, Any],
    verification: Mapping[str, Any] | None,
    decision: str,
) -> JsonDict:
    reason_codes = _merged_reason_codes(classification, verification)
    primary_reason_code = _primary_reason_code(reason_codes)
    meta = _policy_meta(primary_reason_code)
    if decision == "rejected":
        status_value = "rejected"
        status_bucket = "reject"
    elif decision == "abstained":
        status_value = "abstained"
        status_bucket = "adjudicate"
    else:
        status_value = "verified"
        status_bucket = "resolved"
    return {
        "status_scope": "security",
        "status_value": status_value,
        "status_bucket": status_bucket,
        "primary_reason_code": primary_reason_code or "verified",
        "reason_codes": reason_codes or ["verified"],
        "why": meta["why"],
        "next_action": meta["next_action"],
        "details": {
            "classification_decision": classification.get("decision"),
            "verification_decision": None if verification is None else verification.get("decision"),
        },
    }
