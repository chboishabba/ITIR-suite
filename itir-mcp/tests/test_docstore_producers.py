from __future__ import annotations

import json
from pathlib import Path

from itir_mcp.docstore_producers import (
    PROMOTION_CANDIDATE_HINT,
    PROMOTION_STRUCTURED_HINT,
    PROMOTION_TYPED_SOURCE,
    collect_producer_pressure_from_paths,
    discover_missing_normalized_artifact_pressure,
    extract_sensiblaw_fact_review_pressure,
    extract_sensiblaw_operator_view_pressure,
    extract_statibaker_codex_trace_pressure,
    extract_statibaker_dashboard_pressure,
    read_json_payload,
)


def _write_json(path: Path, payload: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return path


def test_sensiblaw_fact_review_extracts_structured_packet_pressure() -> None:
    packet = {
        "schema_version": "sl.wikidata_review_packet.v0_1",
        "packet_id": "review-packet:abc",
        "page_signals": {
            "unresolved_questions": [
                "Which revision-locked source resolves the query row?",
                {"question_text": "Does the rank need review?", "status": "open"},
            ]
        },
        "follow_receipts": [
            {
                "receipt_id": "follow:query:1",
                "unresolved_uncertainty": [
                    "query output is live search evidence",
                    {"reason": "followed link was not expanded", "next_action": "fetch bounded source"},
                ],
            }
        ],
        "reviewer_view": {
            "uncertainty_flags": ["page_open_questions"],
            "recommended_next_step": "review_structured_split",
        },
        "split_review_context": {
            "review_required": True,
            "suggested_action": "review_structured_split",
        },
    }

    records = extract_sensiblaw_fact_review_pressure(packet, source_path="/tmp/packet.json")

    texts = {item["question_text_or_reason"] for item in records}
    assert "Which revision-locked source resolves the query row?" in texts
    assert "query output is live search evidence" in texts
    assert "page_open_questions" in texts
    assert "review_structured_split" in texts
    assert {item["promotion_level"] for item in records} == {PROMOTION_TYPED_SOURCE}
    assert all(item["source_system"] == "SensibLaw" for item in records)
    assert all(item["schema_version"] == "itir.open_question.item.v1" for item in records)
    assert all(item["provenance_refs"][0]["field_path"] for item in records)


def test_sensiblaw_operator_view_extracts_review_queue_and_row_pressure() -> None:
    surface = {
        "schema_version": "sl.wikidata_nat_cohort_d_operator_review_surface.v0_1",
        "cohort_id": "cohort-d",
        "governance": {
            "fail_closed": True,
            "promotion_guard": "hold",
            "requires_human_review": True,
        },
        "triage_prompts": ["Review highest-variance rows first."],
        "selected_rows": [
            {
                "row_id": "Q1|P1|1",
                "reviewer_questions": ["Does class Q1 preserve semantics?"],
                "variance_flags": ["missing_expected_reference_properties"],
            }
        ],
        "operator_queue": [
            {
                "packet_id": "review-packet:queued",
                "smallest_next_check": "resolve_page_open_questions",
                "uncertainty_flags": ["page_open_questions"],
                "execution_allowed": False,
            }
        ],
    }

    records = extract_sensiblaw_operator_view_pressure(surface)

    kinds = {item["pressure_kind"] for item in records}
    assert "operator_review_required" in kinds
    assert "governance_hold" in kinds
    assert "triage_prompt" in kinds
    assert "open_question" in kinds
    assert "variance_flag" in kinds
    assert "operator_queue_item" in kinds
    assert {PROMOTION_TYPED_SOURCE, PROMOTION_STRUCTURED_HINT}.issubset(
        {item["promotion_level"] for item in records}
    )
    assert "Does class Q1 preserve semantics?" in {item["question_text_or_reason"] for item in records}


def test_statibaker_dashboard_and_codex_trace_extract_pressure_without_truth_promotion() -> None:
    dashboard = {
        "date": "2026-05-04",
        "warnings": ["No in-scope assistant/tool messages found."],
        "chat_context_usage": {"overflow_threads": 1, "overflow_tokens": 2048},
        "agent_edit_summary": {"warnings": ["No agent edit blocks found."]},
        "task_completion_candidates": [{"candidate_id": "cand-1"}],
        "external_commitments": [
            {"external_item_id": "task-1", "status": "needs_action"},
            {"external_item_id": "task-2", "status": "completed"},
        ],
    }
    trace = {
        "contract_version": "codex_trace_facts_v1",
        "fact_digest": "sha256:trace",
        "trace_scope": {"primary_thread_id": "thread-1"},
        "message_flow": {"unanswered_user_messages": 2},
        "tool_use": {"request_user_input_count": 1},
        "outcomes": {
            "evidence_gaps": [{"reason": "missing verification"}],
            "unresolved_blockers": [{"warning": "blocked on user approval"}],
            "open_commitments": [{"external_item_id": "task-3", "status": "open"}],
            "completion_candidates": [{"candidate_id": "cand-2"}],
        },
    }

    dashboard_records = extract_statibaker_dashboard_pressure(dashboard)
    trace_records = extract_statibaker_codex_trace_pressure(trace)

    dashboard_kinds = {item["pressure_kind"] for item in dashboard_records}
    trace_kinds = {item["pressure_kind"] for item in trace_records}
    assert {"dashboard_warning", "context_overflow", "agent_edit_warning", "completion_candidate", "open_commitment"}.issubset(
        dashboard_kinds
    )
    assert {"evidence_gap", "unresolved_blocker", "open_commitment", "completion_candidate"}.issubset(trace_kinds)
    assert "unanswered_user_message" in trace_kinds
    assert "human_input_request" in trace_kinds
    assert any(item["promotion_level"] == PROMOTION_CANDIDATE_HINT for item in dashboard_records + trace_records)
    assert all(item["authority_class"] in {"state", "observer"} for item in dashboard_records + trace_records)


def test_missing_normalized_artifact_discovery_is_explicit_path_and_fail_closed(tmp_path: Path) -> None:
    state_path = _write_json(
        tmp_path / "runs" / "2026-05-04" / "outputs" / "state.json",
        {
            "date": "2026-05-04",
            "open_questions": ["Which review packet should be promoted?"],
            "blocked_tasks": [],
            "alerts": [],
        },
    )
    persisted_state_path = _write_json(
        tmp_path / "runs" / "2026-05-05" / "outputs" / "state.json",
        {
            "date": "2026-05-05",
            "open_questions": ["Should not emit because normalized artifact exists."],
            "blocked_tasks": [],
            "alerts": [],
        },
    )
    _write_json(
        persisted_state_path.parent / "suite_normalized_artifact.json",
        {
            "schema_version": "itir.normalized.artifact.v1",
            "artifact_id": "statiBaker.compiled_state:2026-05-05",
        },
    )
    malformed = tmp_path / "bad.json"
    malformed.write_text("{not-json", encoding="utf-8")

    records = discover_missing_normalized_artifact_pressure(
        [state_path, persisted_state_path, malformed, tmp_path / "missing.json"],
        suite_root=tmp_path,
    )

    assert len(records) == 1
    assert records[0]["pressure_kind"] == "normalized_artifact_missing"
    assert records[0]["promotion_level"] == PROMOTION_CANDIDATE_HINT
    assert records[0]["provenance_refs"][0]["path"] == "runs/2026-05-04/outputs/state.json"
    assert read_json_payload(malformed) is None


def test_collect_producer_pressure_from_paths_skips_malformed_inputs(tmp_path: Path) -> None:
    packet_path = _write_json(
        tmp_path / "packet.json",
        {
            "packet_id": "review-packet:abc",
            "page_signals": {"unresolved_questions": ["What source resolves Q1?"]},
        },
    )
    dashboard_path = _write_json(
        tmp_path / "dashboard.json",
        {"date": "2026-05-04", "warnings": ["dashboard warning"]},
    )
    malformed = tmp_path / "bad.json"
    malformed.write_text("[", encoding="utf-8")

    records = collect_producer_pressure_from_paths(
        sensiblaw_fact_review_paths=[packet_path, malformed],
        statibaker_dashboard_paths=[dashboard_path, malformed],
        statibaker_codex_trace_paths=[malformed],
    )

    assert "What source resolves Q1?" in {item["question_text_or_reason"] for item in records}
    assert "dashboard warning" in {item["question_text_or_reason"] for item in records}
    assert all(item["schema_version"] == "itir.open_question.item.v1" for item in records)
