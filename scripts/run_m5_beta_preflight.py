#!/usr/bin/env python3
"""Preflight the M5-beta machine-assisted preliminary A/B lane.

M5-beta is a small AI-judge smoke lane between M5-alpha and the full M5
human-scored A/B proof. It deliberately does not claim RFP pass/fail status.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts import run_m5_eval_protocol as protocol


DEFAULT_OUTPUT_DIR = protocol.REPO_ROOT / "runs" / "m5_beta_preflight"
DEFAULT_QUERY_COUNT = 3
MIN_QUERY_COUNT = 3
MAX_QUERY_COUNT = 5
BETA_HOOKS = {
    "baseline_retrieval_command": {
        "env": "M5_BETA_BASELINE_RETRIEVAL_COMMAND",
        "required": True,
        "purpose": "produce baseline context and retrieval latency for the beta subset",
    },
    "baseline_answer_command": {
        "env": "M5_BETA_BASELINE_ANSWER_COMMAND",
        "required": True,
        "purpose": "produce baseline answer artifact and token/latency accounting",
    },
    "treatment_retrieval_command": {
        "env": "M5_BETA_TREATMENT_RETRIEVAL_COMMAND",
        "required": True,
        "purpose": "produce ITIR treatment context and retrieval latency for the beta subset",
    },
    "treatment_answer_command": {
        "env": "M5_BETA_TREATMENT_ANSWER_COMMAND",
        "required": True,
        "purpose": "produce treatment answer artifact and token/latency accounting",
    },
    "machine_judge_command": {
        "env": "M5_BETA_MACHINE_JUDGE_COMMAND",
        "required": True,
        "purpose": "produce structured PNF claim/support judgment for human review",
    },
}
BETA_SCORE_FIELDS = [
    "baseline_relevance_0_1",
    "treatment_relevance_0_1",
    "baseline_grounding_0_1",
    "treatment_grounding_0_1",
    "baseline_completeness_0_1",
    "treatment_completeness_0_1",
    "baseline_hallucination_rate",
    "treatment_hallucination_rate",
    "baseline_citation_support_rate",
    "treatment_citation_support_rate",
    "baseline_residual_laundering_rate",
    "treatment_residual_laundering_rate",
    "baseline_governance_violations_count",
    "treatment_governance_violations_count",
    "directional_grounding_delta",
    "directional_completeness_delta",
    "directional_hallucination_delta",
    "ai_judge_directionally_useful",
    "human_agrees_with_judge_direction",
]


@dataclass(frozen=True)
class BetaPair:
    query_id: str
    query: str
    category: str
    baseline_run_index: int = 1
    treatment_run_index: int = 1


def _hook_cli_value(args: argparse.Namespace, name: str) -> str:
    value = getattr(args, name)
    return str(value or "").strip()


def resolve_hooks(args: argparse.Namespace) -> dict[str, dict[str, Any]]:
    resolved: dict[str, dict[str, Any]] = {}
    for name, spec in BETA_HOOKS.items():
        cli_value = _hook_cli_value(args, name)
        env_name = str(spec["env"])
        env_value = str(os.environ.get(env_name) or "").strip()
        configured = bool(cli_value or env_value)
        source = "cli" if cli_value else "env" if env_value else "missing"
        resolved[name] = {
            "configured": configured,
            "source": source,
            "env": env_name,
            "required": spec["required"],
            "purpose": spec["purpose"],
        }
    return resolved


def build_beta_pairs(suite: dict[str, Any], query_count: int) -> list[BetaPair]:
    if not MIN_QUERY_COUNT <= query_count <= MAX_QUERY_COUNT:
        raise ValueError(
            f"M5-beta query_count must be between {MIN_QUERY_COUNT} and {MAX_QUERY_COUNT}"
        )
    queries = suite["queries"][:query_count]
    return [
        BetaPair(
            query_id=query["query_id"],
            query=query["query"],
            category=query["category"],
        )
        for query in queries
    ]


def manifest_for_beta(
    suite: dict[str, Any], pairs: list[BetaPair], output_dir: Path
) -> dict[str, Any]:
    return {
        "protocol": "m5_beta_machine_assisted_preliminary_ab/v1",
        "suite_id": suite["suite_id"],
        "frozen_at": suite["frozen_at"],
        "phase_boundary": {
            **suite["phase_boundary"],
            "m5_beta_machine_assisted_preliminary": "preflight_only",
            "m5_beta_is_full_m5": False,
            "m5_beta_is_rfp_pass": False,
        },
        "matrix": {
            "query_count": len(pairs),
            "baseline_runs_per_query": 1,
            "treatment_runs_per_query": 1,
            "answer_runs": len(pairs) * 2,
            "judge_pairs": len(pairs),
        },
        "methodology": {
            "purpose": "rubric, prompt, claim extraction, and judge debugging before the full 72-run M5",
            "ai_judge_score_is_final_truth": False,
            "ai_judge_score_is_rfp_pass": False,
            "ai_judge_score_implies_promotion": False,
            "human_review_required": True,
            "manual_m5_remains_primary": True,
        },
        "success_to_proceed": {
            "treatment_directionally_better_on_grounding_or_completeness": True,
            "ai_judge_catches_unsupported_claims": True,
            "human_agrees_judge_is_directionally_useful": True,
            "governance_violations": 0,
        },
        "artifacts": {
            "manifest": str(output_dir / "m5_beta_manifest.json"),
            "score_sheet": str(output_dir / "m5_beta_score_sheet.csv"),
            "preflight_report": str(output_dir / "m5_beta_preflight.json"),
            "query_suite": str(protocol.DEFAULT_SUITE),
            "prompt_template": str(
                protocol.REPO_ROOT
                / "docs"
                / "planning"
                / "m5_answer_prompt_template_v1.md"
            ),
            "pnf_machine_judge_schema": str(
                protocol.REPO_ROOT
                / "docs"
                / "planning"
                / "m5_pnf_machine_judge_output_schema_v1.json"
            ),
        },
        "pairs": [pair.__dict__ for pair in pairs],
    }


def write_beta_score_sheet(path: Path, pairs: list[BetaPair]) -> None:
    fieldnames = [
        "query_id",
        "category",
        "query",
        "human_reviewer",
        "human_review_status",
        "baseline_answer_artifact_ref",
        "baseline_retrieval_artifact_ref",
        "treatment_answer_artifact_ref",
        "treatment_retrieval_artifact_ref",
        "machine_judge_artifact_ref",
        "claim_list_artifact_ref",
        *BETA_SCORE_FIELDS,
        *protocol.GOVERNANCE_INVARIANTS,
        "notes",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for pair in pairs:
            row = {
                "query_id": pair.query_id,
                "category": pair.category,
                "query": pair.query,
                "human_reviewer": "",
                "human_review_status": "pending",
                "baseline_answer_artifact_ref": "",
                "baseline_retrieval_artifact_ref": "",
                "treatment_answer_artifact_ref": "",
                "treatment_retrieval_artifact_ref": "",
                "machine_judge_artifact_ref": "",
                "claim_list_artifact_ref": "",
                "notes": "",
            }
            row.update({field: "" for field in BETA_SCORE_FIELDS})
            row.update({field: "false" for field in protocol.GOVERNANCE_INVARIANTS})
            writer.writerow(row)


def build_preflight_report(
    suite: dict[str, Any],
    manifest: dict[str, Any],
    hooks: dict[str, dict[str, Any]],
    output_dir: Path,
) -> dict[str, Any]:
    missing_hooks = [
        name
        for name, hook in hooks.items()
        if hook["required"] and not hook["configured"]
    ]
    blocked = bool(missing_hooks)
    return {
        "ok": not blocked,
        "protocol": "m5_beta_preflight/v1",
        "execution_status": (
            "blocked_missing_live_hooks" if blocked else "ready_for_m5_beta_execution"
        ),
        "suite_id": suite["suite_id"],
        "matrix": manifest["matrix"],
        "hooks": hooks,
        "missing_required_hooks": missing_hooks,
        "artifacts": manifest["artifacts"],
        "human_review_status": {
            "score_sheet_materialized": True,
            "human_review_completed": False,
            "human_gate_required": True,
        },
        "not_claimed": [
            "full_m5_proven",
            "m5_answer_quality_lift_proven",
            "m5_beta_rfp_pass",
            "promotion_authority",
            "routing_or_decision_use",
        ],
        "governance_invariants": {
            field: False for field in protocol.GOVERNANCE_INVARIANTS
        },
        "next_required_action": (
            "Configure beta retrieval, answer, and machine-judge hooks; run the "
            "three-query preliminary A/B; then have a human review the judge output."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--suite", type=Path, default=protocol.DEFAULT_SUITE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--query-count", type=int, default=DEFAULT_QUERY_COUNT)
    parser.add_argument("--baseline-retrieval-command")
    parser.add_argument("--baseline-answer-command")
    parser.add_argument("--treatment-retrieval-command")
    parser.add_argument("--treatment-answer-command")
    parser.add_argument("--machine-judge-command")
    parser.add_argument(
        "--expect-blocked",
        action="store_true",
        help="Return zero when the preflight correctly blocks on missing live hooks.",
    )
    args = parser.parse_args(argv)

    suite = protocol.load_suite(args.suite)
    errors = protocol.validate_suite(suite)
    if errors:
        print(json.dumps({"ok": False, "errors": errors}, indent=2, sort_keys=True))
        return 2

    try:
        pairs = build_beta_pairs(suite, args.query_count)
    except ValueError as exc:
        print(json.dumps({"ok": False, "errors": [str(exc)]}, indent=2, sort_keys=True))
        return 2

    args.output_dir.mkdir(parents=True, exist_ok=True)
    manifest = manifest_for_beta(suite, pairs, args.output_dir)
    hooks = resolve_hooks(args)

    manifest_path = args.output_dir / "m5_beta_manifest.json"
    score_sheet_path = args.output_dir / "m5_beta_score_sheet.csv"
    preflight_path = args.output_dir / "m5_beta_preflight.json"

    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    write_beta_score_sheet(score_sheet_path, pairs)

    report = build_preflight_report(suite, manifest, hooks, args.output_dir)
    preflight_path.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2, sort_keys=True))

    if report["ok"]:
        return 0
    return 0 if args.expect_blocked else 3


if __name__ == "__main__":
    raise SystemExit(main())
