from __future__ import annotations

import json
from pathlib import Path


BASELINE = Path("baselines/gwb_timeline_scorecard_v0_2.json")


def test_gwb_regression_baseline_preserves_legacy_discrepancy() -> None:
    row = json.loads(BASELINE.read_text(encoding="utf-8"))

    assert row["observed_event_count"] == 223
    assert row["accepted_regression_event_count"] == 223
    assert row["superseded_legacy_expectation"]["event_count"] == 320
    assert row["superseded_legacy_expectation"]["state"] == (
        "superseded_unreconciled_expectation"
    )
    assert row["rebaseline_state"] == "accepted_for_regression"
    assert row["semantic_state_promoted"] is False
    assert row["timeline_complete"] is False
    assert row["historical_truth_closed"] is False


def test_gwb_baseline_requires_revision_evidence_for_future_change() -> None:
    row = json.loads(BASELINE.read_text(encoding="utf-8"))

    assert row["evidence_refs"]
    assert "source-revision" in row["future_change_rule"]
    assert "event-lineage" in row["future_change_rule"]
