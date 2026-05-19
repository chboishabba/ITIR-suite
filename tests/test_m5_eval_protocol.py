from __future__ import annotations

import csv
import json
from pathlib import Path

from scripts import run_m5_eval_protocol as m5


def test_m5_query_suite_is_frozen_and_protocol_ready() -> None:
    suite = m5.load_suite(Path("docs/planning/m5_query_suite_v1.json"))

    assert m5.validate_suite(suite) == []
    assert suite["phase_boundary"] == {
        "m4_structural_retrieval": "recorded_pass",
        "m5_alpha_two_call_probe": "completed",
        "full_m5_evaluation_protocol": "frozen_ready",
        "full_m5_proven": False,
    }
    assert len(suite["queries"]) == 12
    assert {query["category"] for query in suite["queries"]} >= m5.REQUIRED_CATEGORIES


def test_m5_runner_materializes_json_and_csv_score_sheet(tmp_path: Path) -> None:
    rc = m5.main(["--output-dir", str(tmp_path)])
    assert rc == 0

    manifest = json.loads((tmp_path / "m5_eval_manifest.json").read_text(encoding="utf-8"))
    assert manifest["protocol"] == "m5_answer_quality_eval/v1"
    assert manifest["run_matrix"]["query_count"] == 12
    assert manifest["run_matrix"]["total_answer_runs"] == 72
    assert manifest["methodology"]["fixed_prompt_suite"] is True
    assert manifest["methodology"]["variance_confidence_reporting_required"] is True
    assert manifest["first_pass_gate"]["rfp_composite_quality_delta_required"] == 0.15
    assert manifest["score_layers"]["rfp_gate"]["purpose"] == "primary RFP pass/fail gate"
    assert manifest["score_layers"]["pnf_machine_judge"]["schema"].endswith(
        "m5_pnf_machine_judge_output_schema_v1.json"
    )
    assert "candidate_axis_receipt_backed_support" in manifest["score_layers"]["itir_diagnostics"]["fields"]
    assert "promotion_authority" in manifest["first_pass_gate"]["governance_hard_fail_fields"]

    rows = list(csv.DictReader((tmp_path / "m5_score_sheet.csv").open(encoding="utf-8")))
    assert len(rows) == 72
    assert {row["arm"] for row in rows} == {"baseline", "treatment"}
    assert {row["run_index"] for row in rows} == {"1", "2", "3"}
    assert all(row["promotion_authority"] == "false" for row in rows)
    assert "rfp_composite_quality_score_0_1" in rows[0]
    assert "claim_count" in rows[0]
    assert "claim_pnf_judgment_artifact_ref" in rows[0]
    assert "candidate_axis_receipt_backed_support" in rows[0]
    assert "unsupported_authority_claims" in rows[0]


def test_m5_formalism_and_machine_judge_schema_are_frozen() -> None:
    formalism = Path(
        "docs/planning/m4_m5_retrieval_support_scoring_formalism_20260519.md"
    ).read_text(encoding="utf-8")
    assert "Candidate-Axis Manifold" in formalism
    assert "Typed Residual Algebra" in formalism
    assert "Support Projection Law" in formalism
    assert "CompositeQuality" in formalism
    assert "M6 alone can prove promotion authority" in formalism

    schema = json.loads(
        Path("docs/planning/m5_pnf_machine_judge_output_schema_v1.json").read_text(
            encoding="utf-8"
        )
    )
    assert schema["title"] == "M5 PNF Machine Judge Output v1"
    assert "claim_count" in schema["required"]
    assert "residual_profile_distribution" in schema["required"]
    assert schema["properties"]["arm"]["enum"] == ["baseline", "treatment"]
    assert schema["$defs"]["residualValue"]["enum"] == [
        "exact",
        "compatible",
        "blocked",
        "unresolved",
    ]
