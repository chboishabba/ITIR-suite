from __future__ import annotations

import csv
import json
from pathlib import Path

from scripts import run_m5_beta_preflight as beta


def test_m5_beta_preflight_blocks_without_live_hooks(tmp_path: Path) -> None:
    rc = beta.main(["--output-dir", str(tmp_path), "--expect-blocked"])
    assert rc == 0

    report = json.loads((tmp_path / "m5_beta_preflight.json").read_text(encoding="utf-8"))
    assert report["ok"] is False
    assert report["execution_status"] == "blocked_missing_live_hooks"
    assert report["matrix"] == {
        "query_count": 3,
        "baseline_runs_per_query": 1,
        "treatment_runs_per_query": 1,
        "answer_runs": 6,
        "judge_pairs": 3,
    }
    assert set(report["missing_required_hooks"]) == {
        "baseline_retrieval_command",
        "baseline_answer_command",
        "treatment_retrieval_command",
        "treatment_answer_command",
        "machine_judge_command",
    }
    assert report["human_review_status"]["human_gate_required"] is True
    assert report["not_claimed"] == [
        "full_m5_proven",
        "m5_answer_quality_lift_proven",
        "m5_beta_rfp_pass",
        "promotion_authority",
        "routing_or_decision_use",
    ]

    rows = list(csv.DictReader((tmp_path / "m5_beta_score_sheet.csv").open(encoding="utf-8")))
    assert len(rows) == 3
    assert all(row["human_review_status"] == "pending" for row in rows)
    assert all(row["promotion_authority"] == "false" for row in rows)
    assert "baseline_grounding_0_1" in rows[0]
    assert "treatment_grounding_0_1" in rows[0]
    assert "human_agrees_with_judge_direction" in rows[0]


def test_m5_beta_preflight_can_mark_hooks_ready(tmp_path: Path) -> None:
    rc = beta.main(
        [
            "--output-dir",
            str(tmp_path),
            "--baseline-retrieval-command",
            "baseline-retrieve",
            "--baseline-answer-command",
            "baseline-answer",
            "--treatment-retrieval-command",
            "treatment-retrieve",
            "--treatment-answer-command",
            "treatment-answer",
            "--machine-judge-command",
            "pnf-judge",
        ]
    )
    assert rc == 0

    report = json.loads((tmp_path / "m5_beta_preflight.json").read_text(encoding="utf-8"))
    assert report["ok"] is True
    assert report["execution_status"] == "ready_for_m5_beta_execution"
    assert report["missing_required_hooks"] == []
    assert report["hooks"]["machine_judge_command"]["required"] is True


def test_m5_beta_query_count_is_bounded(tmp_path: Path) -> None:
    rc = beta.main(["--output-dir", str(tmp_path), "--query-count", "2"])
    assert rc == 2
