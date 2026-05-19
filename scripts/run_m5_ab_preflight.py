#!/usr/bin/env python3
"""Preflight the full M5 A/B execution boundary.

This script deliberately does not synthesize answers. It materializes the
frozen M5 run matrix, then verifies that explicit live baseline/treatment
commands have been configured before full A/B execution can be claimed.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts import run_m5_eval_protocol as protocol


DEFAULT_OUTPUT_DIR = protocol.REPO_ROOT / "runs" / "m5_ab_preflight"
EXECUTION_HOOKS = {
    "baseline_retrieval_command": {
        "env": "M5_BASELINE_RETRIEVAL_COMMAND",
        "required": True,
        "purpose": "produce baseline retrieval/context artifact and retrieval latency",
    },
    "baseline_answer_command": {
        "env": "M5_BASELINE_ANSWER_COMMAND",
        "required": True,
        "purpose": "produce baseline answer artifact, answer latency, and token usage",
    },
    "treatment_retrieval_command": {
        "env": "M5_TREATMENT_RETRIEVAL_COMMAND",
        "required": True,
        "purpose": "produce ITIR treatment retrieval artifact and retrieval latency",
    },
    "treatment_answer_command": {
        "env": "M5_TREATMENT_ANSWER_COMMAND",
        "required": True,
        "purpose": "produce treatment answer artifact, answer latency, and token usage",
    },
    "machine_judge_command": {
        "env": "M5_MACHINE_JUDGE_COMMAND",
        "required": False,
        "purpose": "optional PNF machine-judge pass; manual rubric remains primary",
    },
}


def _hook_cli_value(args: argparse.Namespace, name: str) -> str:
    value = getattr(args, name)
    return str(value or "").strip()


def resolve_hooks(args: argparse.Namespace) -> dict[str, dict[str, Any]]:
    resolved: dict[str, dict[str, Any]] = {}
    for name, spec in EXECUTION_HOOKS.items():
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
        "protocol": "m5_ab_execution_preflight/v1",
        "execution_status": (
            "blocked_missing_live_hooks" if blocked else "ready_for_live_ab_execution"
        ),
        "suite_id": suite["suite_id"],
        "phase_boundary": suite["phase_boundary"],
        "run_matrix": manifest["run_matrix"],
        "hooks": hooks,
        "missing_required_hooks": missing_hooks,
        "artifacts": {
            "manifest": str(output_dir / "m5_eval_manifest.json"),
            "score_sheet": str(output_dir / "m5_score_sheet.csv"),
            "preflight_report": str(output_dir / "m5_execution_preflight.json"),
            "query_suite": str(protocol.DEFAULT_SUITE),
            "prompt_template": str(
                protocol.REPO_ROOT / "docs" / "planning" / "m5_answer_prompt_template_v1.md"
            ),
        },
        "manual_scoring_status": {
            "score_sheet_materialized": True,
            "manual_scores_completed": False,
            "manual_rubric_first": True,
        },
        "not_claimed": [
            "full_m5_proven",
            "answer_quality_lift_proven",
            "promotion_authority",
            "routing_or_decision_use",
        ],
        "governance_invariants": {
            field: False for field in protocol.GOVERNANCE_INVARIANTS
        },
        "next_required_action": (
            "Configure required live commands via CLI flags or M5_*_COMMAND "
            "environment variables, then run the A/B matrix and fill the manual score sheet."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--suite", type=Path, default=protocol.DEFAULT_SUITE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
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

    cells = protocol.build_run_cells(suite)
    manifest = protocol.manifest_for_suite(suite, cells)
    hooks = resolve_hooks(args)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = args.output_dir / "m5_eval_manifest.json"
    score_sheet_path = args.output_dir / "m5_score_sheet.csv"
    preflight_path = args.output_dir / "m5_execution_preflight.json"

    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    protocol.write_score_sheet(score_sheet_path, cells)

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
