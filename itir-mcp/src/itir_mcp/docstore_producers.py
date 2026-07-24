from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


JsonDict = dict[str, Any]

OPEN_QUESTION_SCHEMA_VERSION = "itir.open_question.item.v1"
NORMALIZED_ARTIFACT_SCHEMA_VERSION = "itir.normalized.artifact.v1"

PROMOTION_TYPED_SOURCE = "typed_source"
PROMOTION_STRUCTURED_HINT = "structured_hint"
PROMOTION_CANDIDATE_HINT = "candidate_hint"

__all__ = [
    "NORMALIZED_ARTIFACT_SCHEMA_VERSION",
    "OPEN_QUESTION_SCHEMA_VERSION",
    "PROMOTION_CANDIDATE_HINT",
    "PROMOTION_STRUCTURED_HINT",
    "PROMOTION_TYPED_SOURCE",
    "collect_producer_pressure_from_paths",
    "discover_missing_normalized_artifact_pressure",
    "extract_sensiblaw_fact_review_pressure",
    "extract_sensiblaw_operator_view_pressure",
    "extract_statibaker_codex_trace_pressure",
    "extract_statibaker_dashboard_pressure",
    "read_json_payload",
]


def extract_sensiblaw_fact_review_pressure(
    payload: Mapping[str, Any],
    *,
    source_path: str | Path | None = None,
) -> list[JsonDict]:
    """Extract typed pressure from SensibLaw review/fact-review packets.

    The adapter only reads structured fields. It does not infer whether the
    underlying legal or Wikidata claim is true.
    """
    if not isinstance(payload, Mapping):
        return []

    artifact_id = _artifact_id(payload, source_path, keys=("packet_id", "artifact_id", "review_id"))
    source_ref = _source_ref("sensiblaw_fact_review", source_path, artifact_id)
    out: list[JsonDict] = []

    page_signals = _mapping(payload.get("page_signals"))
    for index, item in enumerate(_list(page_signals.get("unresolved_questions"))):
        text = _item_text(item, ("question", "question_text", "text", "reason"))
        if not text:
            continue
        out.append(
            _pressure_record(
                source_system="SensibLaw",
                lane="fact_review_packet",
                artifact_id=artifact_id,
                item_id=_hash_parts(artifact_id, "page_signals.unresolved_questions", str(index), text),
                status=_item_status(item) or "open",
                pressure_kind="open_question",
                text=text,
                next_action=_item_next_action(item) or "review packet unresolved question",
                authority_class="review",
                promotion_level=PROMOTION_TYPED_SOURCE,
                provenance_refs=[{**source_ref, "field_path": f"page_signals.unresolved_questions[{index}]"}],
            )
        )

    for receipt_index, receipt in enumerate(_list(payload.get("follow_receipts"))):
        if not isinstance(receipt, Mapping):
            continue
        receipt_id = str(receipt.get("receipt_id") or receipt_index)
        for uncertainty_index, uncertainty in enumerate(_list(receipt.get("unresolved_uncertainty"))):
            text = _item_text(uncertainty, ("question", "question_text", "text", "reason"))
            if not text:
                continue
            out.append(
                _pressure_record(
                    source_system="SensibLaw",
                    lane="fact_review_packet",
                    artifact_id=artifact_id,
                    item_id=_hash_parts(artifact_id, "follow_receipts", receipt_id, str(uncertainty_index), text),
                    status=_item_status(uncertainty) or "open",
                    pressure_kind="unresolved_uncertainty",
                    text=text,
                    next_action=_item_next_action(uncertainty) or "review unresolved follow receipt uncertainty",
                    authority_class="review",
                    promotion_level=PROMOTION_TYPED_SOURCE,
                    provenance_refs=[
                        {
                            **source_ref,
                            "field_path": f"follow_receipts[{receipt_index}].unresolved_uncertainty[{uncertainty_index}]",
                            "receipt_id": receipt_id,
                        }
                    ],
                )
            )

    reviewer_view = _mapping(payload.get("reviewer_view"))
    next_action = _first_text(
        reviewer_view,
        ("recommended_next_step", "smallest_next_check", "next_action"),
        default="review uncertainty flag",
    )
    for index, flag in enumerate(_list(reviewer_view.get("uncertainty_flags"))):
        text = _item_text(flag, ("flag", "text", "reason"))
        if not text:
            continue
        out.append(
            _pressure_record(
                source_system="SensibLaw",
                lane="fact_review_packet",
                artifact_id=artifact_id,
                item_id=_hash_parts(artifact_id, "reviewer_view.uncertainty_flags", str(index), text),
                status=_item_status(flag) or "open",
                pressure_kind="uncertainty_flag",
                text=text,
                next_action=next_action,
                authority_class="review",
                promotion_level=PROMOTION_TYPED_SOURCE,
                provenance_refs=[{**source_ref, "field_path": f"reviewer_view.uncertainty_flags[{index}]"}],
            )
        )

    split_context = _mapping(payload.get("split_review_context"))
    if split_context.get("review_required") is True:
        text = _first_text(
            split_context,
            ("suggested_action", "status", "split_plan_id"),
            default="split review requires operator review",
        )
        out.append(
            _pressure_record(
                source_system="SensibLaw",
                lane="fact_review_packet",
                artifact_id=artifact_id,
                item_id=_hash_parts(artifact_id, "split_review_context.review_required", text),
                status="review_required",
                pressure_kind="review_required",
                text=text,
                next_action=_first_text(split_context, ("suggested_action",), default="review structured split"),
                authority_class="review",
                promotion_level=PROMOTION_TYPED_SOURCE,
                provenance_refs=[{**source_ref, "field_path": "split_review_context.review_required"}],
            )
        )

    return out


def extract_sensiblaw_operator_view_pressure(
    payload: Mapping[str, Any],
    *,
    source_path: str | Path | None = None,
) -> list[JsonDict]:
    """Extract review pressure from SensibLaw operator surfaces and packets."""
    if not isinstance(payload, Mapping):
        return []

    artifact_id = _artifact_id(payload, source_path, keys=("packet_id", "cohort_id", "lane_id", "artifact_id"))
    source_ref = _source_ref("sensiblaw_operator_view", source_path, artifact_id)
    out: list[JsonDict] = []

    governance = _mapping(payload.get("governance"))
    if governance.get("requires_human_review") is True or str(payload.get("decision") or "").lower() == "review":
        text = _first_text(payload, ("source_bucket_decision", "decision"), default="operator packet requires review")
        out.append(
            _pressure_record(
                source_system="SensibLaw",
                lane="operator_view",
                artifact_id=artifact_id,
                item_id=_hash_parts(artifact_id, "governance.review", text),
                status="review_required",
                pressure_kind="operator_review_required",
                text=text,
                next_action="perform bounded operator review",
                authority_class="review",
                promotion_level=PROMOTION_TYPED_SOURCE,
                provenance_refs=[{**source_ref, "field_path": "governance.requires_human_review"}],
            )
        )

    if governance.get("fail_closed") is True or str(governance.get("promotion_guard") or "").lower() == "hold":
        text = _first_text(governance, ("promotion_guard",), default="fail_closed governance guard is active")
        out.append(
            _pressure_record(
                source_system="SensibLaw",
                lane="operator_view",
                artifact_id=artifact_id,
                item_id=_hash_parts(artifact_id, "governance.fail_closed", text),
                status="held",
                pressure_kind="governance_hold",
                text=text,
                next_action="keep candidate held until explicit review receipt",
                authority_class="review",
                promotion_level=PROMOTION_STRUCTURED_HINT,
                provenance_refs=[{**source_ref, "field_path": "governance"}],
            )
        )

    for index, prompt in enumerate(_list(payload.get("triage_prompts"))):
        text = _item_text(prompt, ("prompt", "text", "reason"))
        if not text:
            continue
        out.append(
            _pressure_record(
                source_system="SensibLaw",
                lane="operator_view",
                artifact_id=artifact_id,
                item_id=_hash_parts(artifact_id, "triage_prompts", str(index), text),
                status="open",
                pressure_kind="triage_prompt",
                text=text,
                next_action="review operator triage prompt",
                authority_class="review",
                promotion_level=PROMOTION_STRUCTURED_HINT,
                provenance_refs=[{**source_ref, "field_path": f"triage_prompts[{index}]"}],
            )
        )

    for row_index, row in enumerate(_list(payload.get("selected_rows"))):
        if not isinstance(row, Mapping):
            continue
        row_id = str(row.get("row_id") or row.get("entity_qid") or row_index)
        for question_index, question in enumerate(_list(row.get("reviewer_questions"))):
            text = _item_text(question, ("question", "question_text", "text", "reason"))
            if not text:
                continue
            out.append(
                _pressure_record(
                    source_system="SensibLaw",
                    lane="operator_view",
                    artifact_id=artifact_id,
                    item_id=_hash_parts(artifact_id, "selected_rows", row_id, "reviewer_questions", str(question_index), text),
                    status="open",
                    pressure_kind="open_question",
                    text=text,
                    next_action="answer selected row reviewer question",
                    authority_class="review",
                    promotion_level=PROMOTION_TYPED_SOURCE,
                    provenance_refs=[
                        {**source_ref, "field_path": f"selected_rows[{row_index}].reviewer_questions[{question_index}]", "row_id": row_id}
                    ],
                )
            )
        for flag_index, flag in enumerate(_list(row.get("variance_flags"))):
            text = _item_text(flag, ("flag", "text", "reason"))
            if not text:
                continue
            out.append(
                _pressure_record(
                    source_system="SensibLaw",
                    lane="operator_view",
                    artifact_id=artifact_id,
                    item_id=_hash_parts(artifact_id, "selected_rows", row_id, "variance_flags", str(flag_index), text),
                    status="review_needed",
                    pressure_kind="variance_flag",
                    text=text,
                    next_action="inspect selected row variance flag",
                    authority_class="review",
                    promotion_level=PROMOTION_TYPED_SOURCE,
                    provenance_refs=[
                        {**source_ref, "field_path": f"selected_rows[{row_index}].variance_flags[{flag_index}]", "row_id": row_id}
                    ],
                )
            )

    for index, item in enumerate(_list(payload.get("operator_queue"))):
        if not isinstance(item, Mapping):
            continue
        queue_id = str(item.get("packet_id") or item.get("review_entity_qid") or index)
        queue_next_action = _first_text(
            item,
            ("smallest_next_check", "recommended_next_step"),
            default="review queued operator packet",
        )
        if item.get("execution_allowed") is False or _list(item.get("uncertainty_flags")):
            text = queue_next_action
            out.append(
                _pressure_record(
                    source_system="SensibLaw",
                    lane="operator_view",
                    artifact_id=artifact_id,
                    item_id=_hash_parts(artifact_id, "operator_queue", queue_id, text),
                    status="review_needed",
                    pressure_kind="operator_queue_item",
                    text=text,
                    next_action=queue_next_action,
                    authority_class="review",
                    promotion_level=PROMOTION_TYPED_SOURCE,
                    provenance_refs=[{**source_ref, "field_path": f"operator_queue[{index}]", "queue_id": queue_id}],
                )
            )
        for flag_index, flag in enumerate(_list(item.get("uncertainty_flags"))):
            text = _item_text(flag, ("flag", "text", "reason"))
            if not text:
                continue
            out.append(
                _pressure_record(
                    source_system="SensibLaw",
                    lane="operator_view",
                    artifact_id=artifact_id,
                    item_id=_hash_parts(artifact_id, "operator_queue", queue_id, "uncertainty_flags", str(flag_index), text),
                    status="open",
                    pressure_kind="uncertainty_flag",
                    text=text,
                    next_action=queue_next_action,
                    authority_class="review",
                    promotion_level=PROMOTION_TYPED_SOURCE,
                    provenance_refs=[
                        {**source_ref, "field_path": f"operator_queue[{index}].uncertainty_flags[{flag_index}]", "queue_id": queue_id}
                    ],
                )
            )

    for index, violation in enumerate(_list(payload.get("contract_violations"))):
        text = _item_text(violation, ("violation", "text", "reason", "code"))
        if not text:
            continue
        out.append(
            _pressure_record(
                source_system="SensibLaw",
                lane="operator_view",
                artifact_id=artifact_id,
                item_id=_hash_parts(artifact_id, "contract_violations", str(index), text),
                status=_item_status(violation) or "open",
                pressure_kind="contract_violation",
                text=text,
                next_action=_item_next_action(violation) or "resolve operator contract violation",
                authority_class="review",
                promotion_level=PROMOTION_TYPED_SOURCE,
                provenance_refs=[{**source_ref, "field_path": f"contract_violations[{index}]"}],
            )
        )

    return out


def extract_statibaker_dashboard_pressure(
    payload: Mapping[str, Any],
    *,
    source_path: str | Path | None = None,
) -> list[JsonDict]:
    """Extract pressure from structured StatiBaker dashboard JSON."""
    if not isinstance(payload, Mapping):
        return []

    date_text = str(payload.get("date") or payload.get("generated_at") or "unknown").strip() or "unknown"
    artifact_id = f"statiBaker.dashboard:{date_text}"
    source_ref = _source_ref("statibaker_dashboard", source_path, artifact_id)
    out: list[JsonDict] = []

    for index, warning in enumerate(_list(payload.get("warnings"))):
        text = _item_text(warning, ("warning", "text", "reason"))
        if not text:
            continue
        out.append(
            _pressure_record(
                source_system="StatiBaker",
                lane="dashboard",
                artifact_id=artifact_id,
                item_id=_hash_parts(artifact_id, "warnings", str(index), text),
                status="open",
                pressure_kind="dashboard_warning",
                text=text,
                next_action="review dashboard warning",
                authority_class="state",
                promotion_level=PROMOTION_TYPED_SOURCE,
                provenance_refs=[{**source_ref, "field_path": f"warnings[{index}]"}],
            )
        )

    context_usage = _mapping(payload.get("chat_context_usage"))
    overflow_threads = _safe_int(context_usage.get("overflow_threads"))
    overflow_tokens = _safe_int(context_usage.get("overflow_tokens"))
    if overflow_threads > 0 or overflow_tokens > 0:
        text = f"context overflow: {overflow_threads} thread(s), {overflow_tokens} token(s)"
        out.append(
            _pressure_record(
                source_system="StatiBaker",
                lane="dashboard",
                artifact_id=artifact_id,
                item_id=_hash_parts(artifact_id, "chat_context_usage.overflow", text),
                status="follow_needed",
                pressure_kind="context_overflow",
                text=text,
                next_action="review context overflow before promotion",
                authority_class="state",
                promotion_level=PROMOTION_TYPED_SOURCE,
                provenance_refs=[{**source_ref, "field_path": "chat_context_usage"}],
            )
        )

    agent_edit = _mapping(payload.get("agent_edit_summary"))
    for index, warning in enumerate(_list(agent_edit.get("warnings"))):
        text = _item_text(warning, ("warning", "text", "reason"))
        if not text:
            continue
        out.append(
            _pressure_record(
                source_system="StatiBaker",
                lane="dashboard",
                artifact_id=artifact_id,
                item_id=_hash_parts(artifact_id, "agent_edit_summary.warnings", str(index), text),
                status="open",
                pressure_kind="agent_edit_warning",
                text=text,
                next_action="review agent edit summary warning",
                authority_class="state",
                promotion_level=PROMOTION_TYPED_SOURCE,
                provenance_refs=[{**source_ref, "field_path": f"agent_edit_summary.warnings[{index}]"}],
            )
        )

    out.extend(
        _completion_candidate_records(
            payload.get("task_completion_candidates"),
            source_system="StatiBaker",
            lane="dashboard",
            artifact_id=artifact_id,
            source_ref=source_ref,
            field_path="task_completion_candidates",
        )
    )
    out.extend(
        _open_commitment_records(
            payload.get("external_commitments"),
            source_system="StatiBaker",
            lane="dashboard",
            artifact_id=artifact_id,
            source_ref=source_ref,
            field_path="external_commitments",
        )
    )
    return out


def extract_statibaker_codex_trace_pressure(
    payload: Mapping[str, Any],
    *,
    source_path: str | Path | None = None,
) -> list[JsonDict]:
    """Extract pressure from StatiBaker codex_trace_facts_v1 payloads."""
    if not isinstance(payload, Mapping) or payload.get("contract_version") != "codex_trace_facts_v1":
        return []

    trace_scope = _mapping(payload.get("trace_scope"))
    artifact_id = "statiBaker.codex_trace:" + str(
        payload.get("fact_digest") or trace_scope.get("primary_thread_id") or trace_scope.get("window_start") or "unknown"
    )
    source_ref = _source_ref("statibaker_codex_trace", source_path, artifact_id)
    out: list[JsonDict] = []
    outcomes = _mapping(payload.get("outcomes"))

    for index, gap in enumerate(_list(outcomes.get("evidence_gaps"))):
        text = _item_text(gap, ("reason", "text", "warning"))
        if not text:
            continue
        out.append(
            _pressure_record(
                source_system="StatiBaker",
                lane="codex_trace",
                artifact_id=artifact_id,
                item_id=_hash_parts(artifact_id, "outcomes.evidence_gaps", str(index), text),
                status="open",
                pressure_kind="evidence_gap",
                text=text,
                next_action="review codex trace evidence gap",
                authority_class="observer",
                promotion_level=PROMOTION_TYPED_SOURCE,
                provenance_refs=[{**source_ref, "field_path": f"outcomes.evidence_gaps[{index}]"}],
            )
        )

    for index, blocker in enumerate(_list(outcomes.get("unresolved_blockers"))):
        text = _item_text(blocker, ("warning", "reason", "text"))
        if not text:
            continue
        out.append(
            _pressure_record(
                source_system="StatiBaker",
                lane="codex_trace",
                artifact_id=artifact_id,
                item_id=_hash_parts(artifact_id, "outcomes.unresolved_blockers", str(index), text),
                status="open",
                pressure_kind="unresolved_blocker",
                text=text,
                next_action="review codex trace blocker",
                authority_class="observer",
                promotion_level=PROMOTION_TYPED_SOURCE,
                provenance_refs=[{**source_ref, "field_path": f"outcomes.unresolved_blockers[{index}]"}],
            )
        )

    out.extend(
        _open_commitment_records(
            outcomes.get("open_commitments"),
            source_system="StatiBaker",
            lane="codex_trace",
            artifact_id=artifact_id,
            source_ref=source_ref,
            field_path="outcomes.open_commitments",
        )
    )
    out.extend(
        _completion_candidate_records(
            outcomes.get("completion_candidates"),
            source_system="StatiBaker",
            lane="codex_trace",
            artifact_id=artifact_id,
            source_ref=source_ref,
            field_path="outcomes.completion_candidates",
        )
    )

    message_flow = _mapping(payload.get("message_flow"))
    unanswered = _safe_int(message_flow.get("unanswered_user_messages"))
    if unanswered > 0:
        text = f"{unanswered} unanswered user message(s) in codex trace"
        out.append(
            _pressure_record(
                source_system="StatiBaker",
                lane="codex_trace",
                artifact_id=artifact_id,
                item_id=_hash_parts(artifact_id, "message_flow.unanswered_user_messages", text),
                status="follow_needed",
                pressure_kind="unanswered_user_message",
                text=text,
                next_action="review unanswered user message pressure",
                authority_class="observer",
                promotion_level=PROMOTION_STRUCTURED_HINT,
                provenance_refs=[{**source_ref, "field_path": "message_flow.unanswered_user_messages"}],
            )
        )

    tool_use = _mapping(payload.get("tool_use"))
    input_requests = _safe_int(tool_use.get("request_user_input_count"))
    if input_requests > 0:
        text = f"{input_requests} request_user_input call(s) observed"
        out.append(
            _pressure_record(
                source_system="StatiBaker",
                lane="codex_trace",
                artifact_id=artifact_id,
                item_id=_hash_parts(artifact_id, "tool_use.request_user_input_count", text),
                status="review_needed",
                pressure_kind="human_input_request",
                text=text,
                next_action="check whether user input request was resolved",
                authority_class="observer",
                promotion_level=PROMOTION_STRUCTURED_HINT,
                provenance_refs=[{**source_ref, "field_path": "tool_use.request_user_input_count"}],
            )
        )

    return out


def discover_missing_normalized_artifact_pressure(
    generated_paths: Iterable[str | Path],
    *,
    suite_root: str | Path | None = None,
) -> list[JsonDict]:
    """Find explicit generated artifacts that look normalizable but lack a persisted normalized artifact.

    This is intentionally path-driven. It does not walk the repository, and it
    emits only candidate hints.
    """
    root = Path(suite_root).resolve() if suite_root is not None else None
    out: list[JsonDict] = []
    seen: set[Path] = set()
    for raw_path in generated_paths:
        path = Path(raw_path).expanduser().resolve()
        if path in seen or not path.exists() or not path.is_file():
            continue
        seen.add(path)
        payload = read_json_payload(path)
        if not isinstance(payload, Mapping) or _is_normalized_artifact(payload):
            continue
        candidate = _normalizable_candidate(path, payload)
        if candidate is None or _has_persisted_normalized_artifact(path):
            continue
        artifact_id = candidate["artifact_id"]
        rel_path = _display_path(path, root)
        out.append(
            _pressure_record(
                source_system=candidate["source_system"],
                lane="normalized_artifact_discovery",
                artifact_id=artifact_id,
                item_id=_hash_parts(artifact_id, "missing_normalized_artifact", str(path)),
                status="candidate",
                pressure_kind="normalized_artifact_missing",
                text=candidate["reason"],
                next_action="persist or explicitly waive normalized artifact",
                authority_class="observer",
                promotion_level=PROMOTION_CANDIDATE_HINT,
                provenance_refs=[
                    {
                        "kind": "generated_artifact",
                        "path": rel_path,
                        "artifact_role": candidate["artifact_role"],
                        "candidate_identity": candidate["candidate_identity"],
                    }
                ],
            )
        )
    return out


def collect_producer_pressure_from_paths(
    *,
    sensiblaw_fact_review_paths: Iterable[str | Path] = (),
    sensiblaw_operator_view_paths: Iterable[str | Path] = (),
    statibaker_dashboard_paths: Iterable[str | Path] = (),
    statibaker_codex_trace_paths: Iterable[str | Path] = (),
    generated_artifact_paths: Iterable[str | Path] = (),
    suite_root: str | Path | None = None,
) -> list[JsonDict]:
    """Integration-ready explicit-path collector for producer adapters."""
    out: list[JsonDict] = []
    for path in sensiblaw_fact_review_paths:
        payload = read_json_payload(path)
        if isinstance(payload, Mapping):
            out.extend(extract_sensiblaw_fact_review_pressure(payload, source_path=path))
    for path in sensiblaw_operator_view_paths:
        payload = read_json_payload(path)
        if isinstance(payload, Mapping):
            out.extend(extract_sensiblaw_operator_view_pressure(payload, source_path=path))
    for path in statibaker_dashboard_paths:
        payload = read_json_payload(path)
        if isinstance(payload, Mapping):
            out.extend(extract_statibaker_dashboard_pressure(payload, source_path=path))
    for path in statibaker_codex_trace_paths:
        payload = read_json_payload(path)
        if isinstance(payload, Mapping):
            out.extend(extract_statibaker_codex_trace_pressure(payload, source_path=path))
    out.extend(discover_missing_normalized_artifact_pressure(generated_artifact_paths, suite_root=suite_root))
    return out


def read_json_payload(path: str | Path) -> Any:
    """Read JSON from an explicit path; malformed inputs fail closed as None."""
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, TypeError):
        return None


def _completion_candidate_records(
    raw_items: Any,
    *,
    source_system: str,
    lane: str,
    artifact_id: str,
    source_ref: JsonDict,
    field_path: str,
) -> list[JsonDict]:
    out: list[JsonDict] = []
    for index, item in enumerate(_list(raw_items)):
        text = _item_text(item, ("candidate_id", "external_item_id", "text", "summary", "reason"))
        if not text:
            continue
        out.append(
            _pressure_record(
                source_system=source_system,
                lane=lane,
                artifact_id=artifact_id,
                item_id=_hash_parts(artifact_id, field_path, str(index), text),
                status=_item_status(item) or "candidate",
                pressure_kind="completion_candidate",
                text=text,
                next_action=_item_next_action(item) or "review completion candidate before promotion",
                authority_class="observer",
                promotion_level=PROMOTION_CANDIDATE_HINT,
                provenance_refs=[{**source_ref, "field_path": f"{field_path}[{index}]"}],
            )
        )
    return out


def _open_commitment_records(
    raw_items: Any,
    *,
    source_system: str,
    lane: str,
    artifact_id: str,
    source_ref: JsonDict,
    field_path: str,
) -> list[JsonDict]:
    out: list[JsonDict] = []
    for index, item in enumerate(_list(raw_items)):
        if not isinstance(item, Mapping):
            continue
        status = _item_status(item) or "open"
        if status.lower() not in {"open", "needs_action", "follow_needed", "review_needed"}:
            continue
        text = _item_text(item, ("external_item_id", "candidate_id", "text", "summary", "reason"))
        if not text:
            continue
        out.append(
            _pressure_record(
                source_system=source_system,
                lane=lane,
                artifact_id=artifact_id,
                item_id=_hash_parts(artifact_id, field_path, str(index), text),
                status=status,
                pressure_kind="open_commitment",
                text=text,
                next_action=_item_next_action(item) or "resolve open commitment",
                authority_class="observer",
                promotion_level=PROMOTION_TYPED_SOURCE,
                provenance_refs=[{**source_ref, "field_path": f"{field_path}[{index}]"}],
            )
        )
    return out


def _normalizable_candidate(path: Path, payload: Mapping[str, Any]) -> JsonDict | None:
    date_text = str(payload.get("date") or "").strip()
    if path.name == "state.json" and date_text and any(isinstance(payload.get(key), list) for key in ("alerts", "open_questions", "blocked_tasks")):
        return {
            "source_system": "StatiBaker",
            "artifact_role": "compiled_state",
            "artifact_id": f"statiBaker.compiled_state:{date_text}",
            "candidate_identity": f"statiBaker_day_state:{date_text}",
            "reason": f"generated StatiBaker state for {date_text} has no persisted normalized artifact",
        }

    schema_version = str(payload.get("schema_version") or "")
    if schema_version.startswith("sl.wikidata_review_packet"):
        packet_id = str(payload.get("packet_id") or path.stem)
        return {
            "source_system": "SensibLaw",
            "artifact_role": "fact_review_packet",
            "artifact_id": f"sensiblaw.fact_review:{packet_id}",
            "candidate_identity": packet_id,
            "reason": "generated SensibLaw fact-review packet has no persisted normalized artifact",
        }

    if schema_version.startswith("sl.") and ("operator" in schema_version or payload.get("operator_queue") is not None):
        identity = str(payload.get("packet_id") or payload.get("cohort_id") or payload.get("lane_id") or path.stem)
        return {
            "source_system": "SensibLaw",
            "artifact_role": "operator_view",
            "artifact_id": f"sensiblaw.operator_view:{identity}",
            "candidate_identity": identity,
            "reason": "generated SensibLaw operator artifact has no persisted normalized artifact",
        }

    return None


def _has_persisted_normalized_artifact(path: Path) -> bool:
    candidates = (
        path.parent / "suite_normalized_artifact.json",
        path.parent / "normalized_artifact.json",
        path.with_name(f"{path.stem}_normalized_artifact.json"),
    )
    for candidate in candidates:
        payload = read_json_payload(candidate)
        if isinstance(payload, Mapping) and _is_normalized_artifact(payload):
            return True
    return False


def _is_normalized_artifact(payload: Mapping[str, Any]) -> bool:
    return payload.get("schema_version") == NORMALIZED_ARTIFACT_SCHEMA_VERSION


def _pressure_record(
    *,
    source_system: str,
    lane: str,
    artifact_id: str,
    item_id: str,
    status: str,
    pressure_kind: str,
    text: str,
    next_action: str,
    authority_class: str,
    promotion_level: str,
    provenance_refs: list[JsonDict],
) -> JsonDict:
    return {
        "schema_version": OPEN_QUESTION_SCHEMA_VERSION,
        "source_system": source_system,
        "lane": lane,
        "artifact_id": artifact_id,
        "item_id": item_id,
        "status": status,
        "pressure_kind": pressure_kind,
        "question_text_or_reason": text,
        "next_action": next_action,
        "authority_class": authority_class,
        "promotion_level": promotion_level,
        "provenance_refs": provenance_refs,
    }


def _artifact_id(payload: Mapping[str, Any], source_path: str | Path | None, *, keys: Sequence[str]) -> str:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    if source_path is not None:
        return str(Path(source_path))
    schema_version = str(payload.get("schema_version") or "unknown")
    return "producer_artifact:" + _hash_parts(schema_version, json.dumps(dict(payload), sort_keys=True, default=str))


def _source_ref(kind: str, source_path: str | Path | None, artifact_id: str) -> JsonDict:
    ref: JsonDict = {"kind": kind, "artifact_id": artifact_id}
    if source_path is not None:
        ref["path"] = str(source_path)
    return ref


def _item_text(item: Any, keys: Sequence[str]) -> str:
    if isinstance(item, Mapping):
        for key in keys:
            value = item.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                return str(value)
        return ""
    if isinstance(item, (str, int, float)) and not isinstance(item, bool):
        return str(item).strip()
    return ""


def _item_status(item: Any) -> str:
    if isinstance(item, Mapping):
        for key in ("status", "resolution_status", "review_status", "state"):
            value = item.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return ""


def _item_next_action(item: Any) -> str:
    if isinstance(item, Mapping):
        for key in ("next_action", "smallest_next_check", "recommended_next_step", "recommended_follow_target"):
            value = item.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return ""


def _first_text(payload: Mapping[str, Any], keys: Sequence[str], *, default: str) -> str:
    text = _item_text(payload, keys)
    return text or default


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    if value is None:
        return []
    return [value]


def _safe_int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _display_path(path: Path, root: Path | None) -> str:
    if root is None:
        return str(path)
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def _hash_parts(*parts: str) -> str:
    return "sha256:" + sha256("|".join(parts).encode("utf-8")).hexdigest()
