from __future__ import annotations

import pytest

from itir_mcp.contracts import ToolInputError
from itir_mcp.promotion_tools import PROPOSAL_RECEIPT_VERSION, get_promotion_tools, proposal_receipt


def _hint(**overrides):
    payload = {
        "source_system": "Docstore",
        "lane": "markdown_hint",
        "artifact_id": "doc:planning.md",
        "item_id": "sha256:item",
        "status": "open",
        "pressure_kind": "open_question",
        "question_text_or_reason": "Should this hint become a reviewed proposal?",
        "authority_class": "observer",
        "provenance_refs": [{"kind": "repo_markdown", "path": "planning.md", "line_no": 7}],
        "promotion_level": "structured_hint",
    }
    payload.update(overrides)
    return payload


def _review(**overrides):
    payload = {
        "reviewer_id": "human:lane-3",
        "reviewer_role": "promotion_workflow_reviewer",
        "review_action": "review",
        "reviewed_at": "2026-05-04T10:00:00+10:00",
        "decision_reason": "Hint is coherent enough to record as a proposal receipt.",
    }
    payload.update(overrides)
    return payload


def test_get_promotion_tools_exposes_unregistered_spec() -> None:
    tools = get_promotion_tools()

    assert len(tools) == 1
    spec, handler = tools[0]
    assert spec.name == "itir.docstore.proposal_receipt"
    assert spec.response_version == PROPOSAL_RECEIPT_VERSION
    assert spec.read_only is True
    assert handler is proposal_receipt


def test_proposal_receipt_is_stable_and_non_authoritative() -> None:
    payload = {"hint": _hint(), **_review()}

    first = proposal_receipt(payload)
    second = proposal_receipt(dict(payload))

    assert first == second
    assert first["version"] == PROPOSAL_RECEIPT_VERSION
    assert first["receipt_id"].startswith("itir.proposal_receipt:")
    assert first["receipt_hash"].startswith("sha256:")
    assert first["hint_hash"].startswith("sha256:")
    assert first["decision"]["status"] == "reviewed"
    assert first["decision"]["canonical_truth_mutated"] is False
    assert first["decision"]["non_authoritative"] is True
    assert "separate external promotion process accepts it" in first["decision"]["authority_notice"]
    assert first["source_hint"]["question_text_or_reason"] == payload["hint"]["question_text_or_reason"]
    assert first["authority_class"] == "non_authoritative_review_receipt"


def test_candidate_hint_can_only_be_marked_promotable_with_external_authority() -> None:
    receipt = proposal_receipt(
        {
            "hint": _hint(promotion_level="candidate_hint"),
            **_review(
                review_action="mark_promotable",
                downstream_promotion_authority={
                    "authority_id": "parent-orchestrator",
                    "process": "future external promotion workflow",
                },
            ),
        }
    )

    assert receipt["decision"]["status"] == "promotable"
    assert receipt["decision"]["eligible_for_external_promotion"] is True
    assert receipt["decision"]["canonical_truth_mutated"] is False
    assert receipt["decision_gates"]["candidate_hint_fact_guard"] is True
    assert receipt["decision_gates"]["can_be_promotable"] is True


def test_mark_promotable_without_downstream_authority_is_held() -> None:
    receipt = proposal_receipt(
        {
            "hint": _hint(promotion_level="candidate_hint"),
            **_review(review_action="mark_promotable"),
        }
    )

    assert receipt["decision"]["requested_action"] == "mark_promotable"
    assert receipt["decision"]["status"] == "held"
    assert receipt["decision"]["eligible_for_external_promotion"] is False
    assert receipt["decision_gates"]["downstream_authority_present"] is False
    assert receipt["decision_gates"]["can_be_promotable"] is False


def test_batch_receipts_share_review_payload() -> None:
    result = proposal_receipt(
        {
            "hints": [
                _hint(item_id="sha256:first"),
                _hint(item_id="sha256:second", promotion_level="candidate_hint"),
            ],
            **_review(review_action="hold", decision_reason="Holding until reviewer authority is clarified."),
        }
    )

    assert result["version"] == PROPOSAL_RECEIPT_VERSION
    assert result["receipt_count"] == 2
    assert [item["decision"]["status"] for item in result["receipts"]] == ["held", "held"]
    assert {item["proposal_id"] for item in result["receipts"]} != {result["receipts"][0]["proposal_id"]}


def test_rejects_non_hint_promotion_level() -> None:
    with pytest.raises(ToolInputError, match="promotion_level"):
        proposal_receipt({"hint": _hint(promotion_level="typed_source"), **_review()})


def test_requires_human_review_identity_and_action_fields() -> None:
    with pytest.raises(ToolInputError) as excinfo:
        proposal_receipt({"hint": _hint(), "review_action": "review"})

    assert excinfo.value.details["missing"] == ["reviewer_id", "reviewed_at", "decision_reason"]
