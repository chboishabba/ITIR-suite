from __future__ import annotations

import csv
import json
from pathlib import Path

from scripts import run_m5_ab_preflight as preflight


def test_m5_ab_preflight_blocks_without_live_hooks(tmp_path: Path) -> None:
    rc = preflight.main(["--output-dir", str(tmp_path), "--expect-blocked"])
    assert rc == 0

    report = json.loads(
        (tmp_path / "m5_execution_preflight.json").read_text(encoding="utf-8")
    )
    assert report["ok"] is False
    assert report["execution_status"] == "blocked_missing_live_hooks"
    assert report["run_matrix"]["total_answer_runs"] == 72
    assert report["manual_scoring_status"]["score_sheet_materialized"] is True
    assert report["manual_scoring_status"]["manual_scores_completed"] is False
    assert report["not_claimed"] == [
        "full_m5_proven",
        "answer_quality_lift_proven",
        "promotion_authority",
        "routing_or_decision_use",
    ]
    assert set(report["missing_required_hooks"]) == {
        "baseline_retrieval_command",
        "baseline_answer_command",
        "treatment_retrieval_command",
        "treatment_answer_command",
    }

    rows = list(csv.DictReader((tmp_path / "m5_score_sheet.csv").open(encoding="utf-8")))
    assert len(rows) == 72
    assert {row["arm"] for row in rows} == {"baseline", "treatment"}
    assert all(row["promotion_authority"] == "false" for row in rows)


def test_m5_ab_preflight_can_mark_live_hooks_ready(tmp_path: Path) -> None:
    rc = preflight.main(
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
        ]
    )
    assert rc == 0

    report = json.loads(
        (tmp_path / "m5_execution_preflight.json").read_text(encoding="utf-8")
    )
    assert report["ok"] is True
    assert report["execution_status"] == "ready_for_live_ab_execution"
    assert report["missing_required_hooks"] == []
    assert report["hooks"]["machine_judge_command"]["required"] is False
