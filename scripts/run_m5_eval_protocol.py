#!/usr/bin/env python3
"""Validate and materialize the frozen M5 manual evaluation protocol."""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SUITE = REPO_ROOT / "docs" / "planning" / "m5_query_suite_v1.json"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "runs" / "m5_eval_protocol"
FORMALISM_DOC = "docs/planning/m4_m5_retrieval_support_scoring_formalism_20260519.md"
PNF_MACHINE_JUDGE_SCHEMA = "docs/planning/m5_pnf_machine_judge_output_schema_v1.json"
REQUIRED_CATEGORIES = {
    "exact_support",
    "partial_support",
    "contradiction",
    "missing_support",
    "temporal_update_heavy",
    "policy_regulatory",
    "market_liquidity",
    "entity_specific",
    "broad_generic",
    "negative_control",
}
GOVERNANCE_INVARIANTS = [
    "promotion_authority",
    "routing",
    "semantic_fact_emission",
    "surface_ref_implies_truth",
    "candidate_axis_support_implies_truth",
    "answer_quality_implies_promotion",
]
RFP_GATE_FIELDS = [
    "relevance_score_0_1",
    "factual_grounding_score_0_1",
    "completeness_score_0_1",
    "hallucination_rate",
    "hallucination_inverse_0_1",
    "rfp_composite_quality_score_0_1",
    "relevance_1_5",
    "grounding_1_5",
    "completeness_1_5",
    "hallucination_safety_1_5",
    "rfp_composite_quality_score_1_5",
    "successful_processing",
]
PNF_JUDGE_FIELDS = [
    "claim_count",
    "supported_claim_count",
    "partial_claim_count",
    "unsupported_claim_count",
    "contradicted_claim_count",
    "authority_overclaim_count",
    "unsupported_entity_claim_count",
    "unsupported_temporal_claim_count",
    "unsupported_causal_claim_count",
    "unsupported_numeric_claim_count",
    "unsupported_authority_claim_count",
    "residual_laundering_rate",
    "citation_support_rate",
    "governance_violations_count",
    "claim_pnf_judgment_artifact_ref",
]
ITIR_DIAGNOSTIC_FIELDS = [
    "candidate_axis_receipt_backed_support",
    "candidate_axis_core_coverage",
    "candidate_axis_surface_backed_support",
    "span_receipt_surface_coverage",
    "typed_residual_profile_distribution",
    "supported_claim_rate",
    "unsupported_claim_count",
    "citation_present_rate",
    "citation_correctness",
    "source_span_receipt_traceability",
    "query_facets_covered_in_answer",
    "missing_core_facets",
    "candidate_axis_coverage_in_answer",
    "residuals_disclosed",
    "contradictions_disclosed",
    "authority_limits_disclosed",
    "overclaim_count",
    "candidate_only_language_preserved",
    "citation_precision",
    "citation_supports_sentence",
    "citation_relevance",
    "citation_overload_rate",
    "unsupported_entities",
    "unsupported_temporal_claims",
    "unsupported_causal_claims",
    "unsupported_numeric_claims",
    "unsupported_authority_claims",
    "relevance",
    "specificity",
    "clarity",
    "compactness",
    "actionability",
    "non_redundancy",
    "retrieval_latency_ms",
    "answer_latency_ms",
    "total_latency_ms",
    "input_tokens",
    "output_tokens",
    "cost_estimate",
    "retrieval_overlap",
    "answer_score_variance",
    "citation_variance",
    "same_query_repeat_variance",
]
SCORE_FIELDS = [
    *RFP_GATE_FIELDS,
    *PNF_JUDGE_FIELDS,
    *ITIR_DIAGNOSTIC_FIELDS,
]


@dataclass(frozen=True)
class RunCell:
    query_id: str
    query: str
    category: str
    arm: str
    run_index: int


def load_suite(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("suite root must be an object")
    return data


def validate_suite(suite: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    queries = suite.get("queries")
    settings = suite.get("settings") or {}
    if not isinstance(queries, list):
        return ["queries must be a list"]
    if not 10 <= len(queries) <= 20:
        errors.append("query suite must contain 10-20 frozen queries")
    categories = {str(item.get("category")) for item in queries if isinstance(item, dict)}
    missing = sorted(REQUIRED_CATEGORIES - categories)
    if missing:
        errors.append(f"missing required categories: {', '.join(missing)}")
    seen_ids: set[str] = set()
    for index, query in enumerate(queries, start=1):
        if not isinstance(query, dict):
            errors.append(f"query {index} must be an object")
            continue
        query_id = str(query.get("query_id") or "")
        if not query_id:
            errors.append(f"query {index} missing query_id")
        elif query_id in seen_ids:
            errors.append(f"duplicate query_id: {query_id}")
        seen_ids.add(query_id)
        if not str(query.get("query") or "").strip():
            errors.append(f"{query_id or index} missing query text")
        for field in ("core_facets", "candidate_axes"):
            value = query.get(field)
            if not isinstance(value, list) or not value:
                errors.append(f"{query_id or index} missing non-empty {field}")
    if settings.get("baseline_runs_per_query") != 3:
        errors.append("baseline_runs_per_query must be 3")
    if settings.get("treatment_runs_per_query") != 3:
        errors.append("treatment_runs_per_query must be 3")
    if settings.get("fixed_temperature") != 0:
        errors.append("fixed_temperature must be 0")
    boundary = suite.get("phase_boundary") or {}
    if boundary.get("full_m5_proven") is not False:
        errors.append("phase_boundary.full_m5_proven must be false")
    return errors


def build_run_cells(suite: dict[str, Any]) -> list[RunCell]:
    settings = suite["settings"]
    cells: list[RunCell] = []
    for query in suite["queries"]:
        for arm, count_key in (
            ("baseline", "baseline_runs_per_query"),
            ("treatment", "treatment_runs_per_query"),
        ):
            for run_index in range(1, int(settings[count_key]) + 1):
                cells.append(
                    RunCell(
                        query_id=query["query_id"],
                        query=query["query"],
                        category=query["category"],
                        arm=arm,
                        run_index=run_index,
                    )
                )
    return cells


def manifest_for_suite(suite: dict[str, Any], cells: list[RunCell]) -> dict[str, Any]:
    settings = suite["settings"]
    return {
        "protocol": "m5_answer_quality_eval/v1",
        "suite_id": suite["suite_id"],
        "frozen_at": suite["frozen_at"],
        "phase_boundary": suite["phase_boundary"],
        "settings": settings,
        "run_matrix": {
            "query_count": len(suite["queries"]),
            "baseline_runs_per_query": settings["baseline_runs_per_query"],
            "treatment_runs_per_query": settings["treatment_runs_per_query"],
            "total_answer_runs": len(cells),
        },
        "methodology": {
            "fixed_prompt_suite": True,
            "identical_prompts_and_retrieval_limits": True,
            "blind_scoring_where_possible": True,
            "manual_rubric_scale": "1-5 RFP gate plus 0-3 diagnostic fields",
            "minimum_runs_per_query_per_arm": 3,
            "variance_confidence_reporting_required": True,
        },
        "first_pass_gate": {
            "rfp_composite_quality_delta_required": 0.15,
            "hallucination_rate_delta_required": -0.20,
            "end_to_end_latency_p95_max_regression": 0.10,
            "successful_processing_rate_required": 0.99,
            "unsupported_claim_rate_delta_required": -0.20,
            "citation_traceability_delta_required": 0.20,
            "core_facet_coverage_delta_required": 0.15,
            "grounded_claim_rate": "improve",
            "governance_hard_fail_fields": GOVERNANCE_INVARIANTS,
        },
        "score_layers": {
            "rfp_gate": {
                "fields": RFP_GATE_FIELDS,
                "composite_quality_formula": "mean(relevance, factual_grounding, completeness, hallucination_inverse)",
                "purpose": "primary RFP pass/fail gate",
            },
            "pnf_machine_judge": {
                "fields": PNF_JUDGE_FIELDS,
                "schema": PNF_MACHINE_JUDGE_SCHEMA,
                "purpose": "claim-level support comparison substrate",
            },
            "itir_diagnostics": {
                "fields": ITIR_DIAGNOSTIC_FIELDS,
                "purpose": "retrieval/support/residual explanation; not mixed into RFP composite quality",
            },
        },
        "formalism": {
            "document": FORMALISM_DOC,
            "governance_laws": [
                "retrieval_score_does_not_entail_support",
                "support_score_does_not_entail_promotion",
                "answer_quality_does_not_entail_promotion",
                "surface_ref_does_not_imply_truth",
                "candidate_axis_support_does_not_imply_truth",
            ],
        },
        "artifacts": {
            "query_suite": "docs/planning/m5_query_suite_v1.json",
            "prompt_template": "docs/planning/m5_answer_prompt_template_v1.md",
            "formalism": FORMALISM_DOC,
            "pnf_machine_judge_schema": PNF_MACHINE_JUDGE_SCHEMA,
            "score_sheet": "m5_score_sheet.csv",
        },
        "runs": [cell.__dict__ for cell in cells],
    }


def write_score_sheet(path: Path, cells: list[RunCell]) -> None:
    fieldnames = [
        "query_id",
        "category",
        "arm",
        "run_index",
        "reviewer",
        "answer_artifact_ref",
        "retrieval_artifact_ref",
        *SCORE_FIELDS,
        *GOVERNANCE_INVARIANTS,
        "notes",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for cell in cells:
            row = {
                "query_id": cell.query_id,
                "category": cell.category,
                "arm": cell.arm,
                "run_index": cell.run_index,
                "reviewer": "",
                "answer_artifact_ref": "",
                "retrieval_artifact_ref": "",
                "notes": "",
            }
            row.update({field: "" for field in SCORE_FIELDS})
            row.update({field: "false" for field in GOVERNANCE_INVARIANTS})
            writer.writerow(row)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--suite", type=Path, default=DEFAULT_SUITE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--check", action="store_true", help="Validate only; do not write outputs.")
    args = parser.parse_args(argv)

    suite = load_suite(args.suite)
    errors = validate_suite(suite)
    if errors:
        print(json.dumps({"ok": False, "errors": errors}, indent=2, sort_keys=True))
        return 2

    cells = build_run_cells(suite)
    manifest = manifest_for_suite(suite, cells)
    if args.check:
        print(json.dumps({"ok": True, "manifest": manifest}, indent=2, sort_keys=True))
        return 0

    args.output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = args.output_dir / "m5_eval_manifest.json"
    score_sheet_path = args.output_dir / "m5_score_sheet.csv"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_score_sheet(score_sheet_path, cells)
    print(
        json.dumps(
            {
                "ok": True,
                "manifest_path": str(manifest_path),
                "score_sheet_path": str(score_sheet_path),
                "total_answer_runs": len(cells),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
