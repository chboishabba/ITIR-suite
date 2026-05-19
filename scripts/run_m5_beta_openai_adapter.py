#!/usr/bin/env python3
"""Run the guarded M5-beta answer-generation lane through OpenAI.

This adapter intentionally does not call an API-based judge. It generates the
baseline/treatment answers, writes auditable packets, and leaves the preliminary
PNF judgment to Codex/human review in the same local artifacts.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts import run_m5_beta_preflight as beta
from scripts import run_m5_eval_protocol as protocol


DEFAULT_ENV_FILE = Path(os.environ.get("M5_BETA_OPENAI_ENV_FILE", ".env"))
DEFAULT_OUTPUT_DIR = protocol.REPO_ROOT / "runs" / "m5_beta_openai"
DEFAULT_MODEL = "gpt-4.1-mini"
DEFAULT_MAX_OUTPUT_TOKENS = 700
ANSWER_ARTIFACT_DIR = "answers"
CONTEXT_ARTIFACT_DIR = "contexts"
JUDGE_PACKET_DIR = "codex_judge_packets"


@dataclass(frozen=True)
class AnswerResult:
    query_id: str
    arm: str
    run_index: int
    model: str
    answer_text: str
    answer_latency_ms: int
    input_tokens: int | None
    output_tokens: int | None
    total_tokens: int | None
    cost_estimate_usd: float | None
    response_id: str | None


def load_env_file(path: Path) -> list[str]:
    """Load KEY=VALUE lines without printing or returning secret values."""
    loaded: list[str] = []
    if not path.exists():
        raise FileNotFoundError(f"env file not found: {path}")
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if not key:
            continue
        os.environ.setdefault(key, value)
        loaded.append(key)
    return loaded


def render_prompt(template: str, query: str, retrieval_context: dict[str, Any]) -> str:
    context_json = json.dumps(retrieval_context, indent=2, sort_keys=True)
    return template.replace("{{query}}", query).replace(
        "{{retrieval_context_json}}", context_json
    )


def build_baseline_context(query: dict[str, Any], suite: dict[str, Any]) -> dict[str, Any]:
    return {
        "context_mode": "baseline_local_protocol_excerpt",
        "retrieval_is_live_m4": False,
        "retrieval_latency_ms": 0,
        "source_boundary": "local frozen M5 protocol/query suite context only",
        "query_id": query["query_id"],
        "query_category": query["category"],
        "available_protocol_facts": {
            "suite_id": suite["suite_id"],
            "frozen_at": suite["frozen_at"],
            "phase_boundary": suite["phase_boundary"],
            "settings": suite["settings"],
        },
        "candidate_axes": query["candidate_axes"],
        "core_facets": query["core_facets"],
        "governance_invariants": {
            field: False for field in protocol.GOVERNANCE_INVARIANTS
        },
        "authority": {
            "promotion_authority": False,
            "routing": False,
            "semantic_fact_emission": False,
        },
        "residual_profile": {
            "surface": "unresolved",
            "receipt": "local_protocol_only",
            "authority": "unresolved",
            "projection_grade": "candidate",
        },
    }


def build_treatment_context(query: dict[str, Any], suite: dict[str, Any]) -> dict[str, Any]:
    support_packets = [
        {
            "support_id": f"{query['query_id']}-suite-core-facets",
            "source": "docs/planning/m5_query_suite_v1.json",
            "span": f"queries[{query['query_id']}].core_facets",
            "receipt": "m5_query_suite_v1:frozen_at=2026-05-19",
            "surface": "frozen query suite",
            "candidate_axis": query["candidate_axes"],
            "support_grade": query["expected_support_profile"],
            "facets": query["core_facets"],
        },
        {
            "support_id": f"{query['query_id']}-phase-boundary",
            "source": "docs/planning/m5_answer_quality_evaluation_protocol_20260519.md",
            "span": "Phase Boundary / M5-beta Machine-Assisted Preliminary Lane",
            "receipt": "m5_protocol_doc:2026-05-19",
            "surface": "protocol narrative",
            "candidate_axis": ["phase_boundary", "evaluation_protocol"],
            "support_grade": "candidate_receipt_backed",
            "facets": [
                "M4 structural retrieval recorded pass",
                "M5-alpha completed",
                "M5 protocol frozen/ready",
                "full M5 proof pending",
                "M6 promotion authority not started",
            ],
        },
        {
            "support_id": f"{query['query_id']}-governance",
            "source": "scripts/run_m5_eval_protocol.py",
            "span": "GOVERNANCE_INVARIANTS",
            "receipt": "runner_constant:GOVERNANCE_INVARIANTS",
            "surface": "protocol runner constant",
            "candidate_axis": ["governance_invariants"],
            "support_grade": "exact_protocol_constant",
            "facets": protocol.GOVERNANCE_INVARIANTS,
        },
    ]
    return {
        "context_mode": "treatment_structured_candidate_axis_context",
        "retrieval_is_live_m4": False,
        "retrieval_latency_ms": 0,
        "source_boundary": "local frozen M5 artifacts with structured support packets",
        "query_id": query["query_id"],
        "query_category": query["category"],
        "facet_carrier": {
            "query": query["query"],
            "core_facets": query["core_facets"],
        },
        "axis_candidate_set": [
            {
                "axis_id": axis,
                "compatible_facet_fibres": query["core_facets"],
                "predicate_posture": "candidate",
                "role_posture": "candidate",
                "temporal_posture": "frozen_protocol_date",
                "domain_posture": query["category"],
                "surface_participation": True,
                "residual_ambiguity": "authority_unresolved_no_promotion",
            }
            for axis in query["candidate_axes"]
        ],
        "support_packets": support_packets,
        "typed_residual_profile": {
            "lexical": "compatible",
            "predicate": "compatible",
            "role": "compatible",
            "temporal": "compatible",
            "domain": "compatible",
            "surface": "compatible",
            "authority": "unresolved",
            "projection_grade": "candidate",
        },
        "governance_invariants": {
            field: False for field in protocol.GOVERNANCE_INVARIANTS
        },
        "hard_limits": [
            "candidate_axis_support_does_not_imply_truth",
            "answer_quality_does_not_imply_promotion",
            "surface_ref_does_not_imply_truth",
            "M6_alone_can_prove_promotion_authority",
        ],
    }


def token_cost(
    input_tokens: int | None,
    output_tokens: int | None,
    input_cost_per_1m: float | None,
    output_cost_per_1m: float | None,
) -> float | None:
    if (
        input_tokens is None
        or output_tokens is None
        or input_cost_per_1m is None
        or output_cost_per_1m is None
    ):
        return None
    return (input_tokens / 1_000_000 * input_cost_per_1m) + (
        output_tokens / 1_000_000 * output_cost_per_1m
    )


def usage_value(usage: Any, name: str) -> int | None:
    if usage is None:
        return None
    if isinstance(usage, dict):
        value = usage.get(name)
    else:
        value = getattr(usage, name, None)
    return int(value) if value is not None else None


def response_text(response: Any) -> str:
    text = getattr(response, "output_text", None)
    if text:
        return str(text)
    pieces: list[str] = []
    for item in getattr(response, "output", []) or []:
        for content in getattr(item, "content", []) or []:
            content_text = getattr(content, "text", None)
            if content_text:
                pieces.append(str(content_text))
    return "\n".join(pieces).strip()


def call_openai_answer(
    prompt: str,
    model: str,
    max_output_tokens: int,
    input_cost_per_1m: float | None,
    output_cost_per_1m: float | None,
) -> tuple[str, dict[str, Any]]:
    from openai import OpenAI

    client = OpenAI()
    start = time.perf_counter()
    response = client.responses.create(
        model=model,
        input=[
            {
                "role": "system",
                "content": (
                    "You are generating an M5-beta evaluation answer. Follow the "
                    "provided frozen prompt exactly. Do not claim truth, routing, "
                    "promotion authority, or full M5 proof."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0,
        max_output_tokens=max_output_tokens,
    )
    elapsed_ms = int((time.perf_counter() - start) * 1000)
    usage = getattr(response, "usage", None)
    input_tokens = usage_value(usage, "input_tokens")
    output_tokens = usage_value(usage, "output_tokens")
    total_tokens = usage_value(usage, "total_tokens")
    return response_text(response), {
        "answer_latency_ms": elapsed_ms,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
        "cost_estimate_usd": token_cost(
            input_tokens, output_tokens, input_cost_per_1m, output_cost_per_1m
        ),
        "response_id": getattr(response, "id", None),
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_judge_packet(
    path: Path,
    pair: beta.BetaPair,
    baseline_answer: dict[str, Any],
    treatment_answer: dict[str, Any],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            [
                f"# M5-beta Codex Judge Packet: {pair.query_id}",
                "",
                "Status: pending Codex/human preliminary review.",
                "",
                "Governance: this packet is not full M5, not RFP pass/fail, not truth, not promotion, and not routing authority.",
                "",
                "## Query",
                "",
                pair.query,
                "",
                "## Baseline Answer",
                "",
                baseline_answer["answer_text"],
                "",
                "## Treatment Answer",
                "",
                treatment_answer["answer_text"],
                "",
                "## Preliminary Grading Slots",
                "",
                "- relevance:",
                "- grounding:",
                "- completeness:",
                "- hallucination risk:",
                "- citation/traceability:",
                "- residual honesty:",
                "- governance violations:",
                "- direction:",
                "",
            ]
        ),
        encoding="utf-8",
    )


def write_live_score_sheet(path: Path, rows: list[dict[str, Any]]) -> None:
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
        "codex_judge_packet_ref",
        "codex_prelim_judgment_ref",
        "baseline_answer_latency_ms",
        "treatment_answer_latency_ms",
        "baseline_input_tokens",
        "baseline_output_tokens",
        "treatment_input_tokens",
        "treatment_output_tokens",
        "baseline_cost_estimate_usd",
        "treatment_cost_estimate_usd",
        *beta.BETA_SCORE_FIELDS,
        *protocol.GOVERNANCE_INVARIANTS,
        "notes",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            safe_row = {field: row.get(field, "") for field in fieldnames}
            writer.writerow(safe_row)


def run_adapter(args: argparse.Namespace) -> dict[str, Any]:
    loaded_env_keys = load_env_file(args.env_file)
    if not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is not configured after loading env file")

    suite = protocol.load_suite(args.suite)
    errors = protocol.validate_suite(suite)
    if errors:
        raise ValueError("; ".join(errors))
    pairs = beta.build_beta_pairs(suite, args.query_count)
    template = (
        protocol.REPO_ROOT / "docs" / "planning" / "m5_answer_prompt_template_v1.md"
    ).read_text(encoding="utf-8")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    score_rows: list[dict[str, Any]] = []
    answer_refs: list[str] = []
    context_refs: list[str] = []
    packet_refs: list[str] = []

    query_by_id = {item["query_id"]: item for item in suite["queries"]}
    for pair in pairs:
        query = query_by_id[pair.query_id]
        baseline_context = build_baseline_context(query, suite)
        treatment_context = build_treatment_context(query, suite)

        baseline_context_ref = (
            args.output_dir
            / CONTEXT_ARTIFACT_DIR
            / f"{pair.query_id}.baseline.context.json"
        )
        treatment_context_ref = (
            args.output_dir
            / CONTEXT_ARTIFACT_DIR
            / f"{pair.query_id}.treatment.context.json"
        )
        write_json(baseline_context_ref, baseline_context)
        write_json(treatment_context_ref, treatment_context)
        context_refs.extend([str(baseline_context_ref), str(treatment_context_ref)])

        answer_payloads: dict[str, dict[str, Any]] = {}
        for arm, context in (
            ("baseline", baseline_context),
            ("treatment", treatment_context),
        ):
            prompt = render_prompt(template, pair.query, context)
            answer_text, meta = call_openai_answer(
                prompt=prompt,
                model=args.model,
                max_output_tokens=args.max_output_tokens,
                input_cost_per_1m=args.input_cost_per_1m,
                output_cost_per_1m=args.output_cost_per_1m,
            )
            answer_payload = {
                "protocol": "m5_beta_openai_answer/v1",
                "query_id": pair.query_id,
                "category": pair.category,
                "query": pair.query,
                "arm": arm,
                "run_index": 1,
                "model": args.model,
                "fixed_temperature": 0,
                "answer_text": answer_text,
                "context_artifact_ref": str(
                    baseline_context_ref if arm == "baseline" else treatment_context_ref
                ),
                "prompt_template_ref": "docs/planning/m5_answer_prompt_template_v1.md",
                "api_judge_used": False,
                "governance_invariants": {
                    field: False for field in protocol.GOVERNANCE_INVARIANTS
                },
                "not_claimed": [
                    "full_m5_proven",
                    "m5_answer_quality_lift_proven",
                    "m5_beta_rfp_pass",
                    "promotion_authority",
                    "routing_or_decision_use",
                ],
                **meta,
            }
            answer_ref = (
                args.output_dir
                / ANSWER_ARTIFACT_DIR
                / f"{pair.query_id}.{arm}.answer.json"
            )
            write_json(answer_ref, answer_payload)
            answer_refs.append(str(answer_ref))
            answer_payloads[arm] = answer_payload

        packet_ref = (
            args.output_dir / JUDGE_PACKET_DIR / f"{pair.query_id}.codex_judge_packet.md"
        )
        write_judge_packet(
            packet_ref,
            pair,
            answer_payloads["baseline"],
            answer_payloads["treatment"],
        )
        packet_refs.append(str(packet_ref))

        score_row = {
            "query_id": pair.query_id,
            "category": pair.category,
            "query": pair.query,
            "human_reviewer": "",
            "human_review_status": "pending_codex_prelim_judge",
            "baseline_answer_artifact_ref": str(
                args.output_dir
                / ANSWER_ARTIFACT_DIR
                / f"{pair.query_id}.baseline.answer.json"
            ),
            "baseline_retrieval_artifact_ref": str(baseline_context_ref),
            "treatment_answer_artifact_ref": str(
                args.output_dir
                / ANSWER_ARTIFACT_DIR
                / f"{pair.query_id}.treatment.answer.json"
            ),
            "treatment_retrieval_artifact_ref": str(treatment_context_ref),
            "codex_judge_packet_ref": str(packet_ref),
            "codex_prelim_judgment_ref": "",
            "baseline_answer_latency_ms": answer_payloads["baseline"][
                "answer_latency_ms"
            ],
            "treatment_answer_latency_ms": answer_payloads["treatment"][
                "answer_latency_ms"
            ],
            "baseline_input_tokens": answer_payloads["baseline"].get("input_tokens"),
            "baseline_output_tokens": answer_payloads["baseline"].get("output_tokens"),
            "treatment_input_tokens": answer_payloads["treatment"].get("input_tokens"),
            "treatment_output_tokens": answer_payloads["treatment"].get("output_tokens"),
            "baseline_cost_estimate_usd": answer_payloads["baseline"].get(
                "cost_estimate_usd"
            ),
            "treatment_cost_estimate_usd": answer_payloads["treatment"].get(
                "cost_estimate_usd"
            ),
            "notes": "Preliminary answer artifacts generated; Codex/human judge pending.",
        }
        score_row.update({field: "" for field in beta.BETA_SCORE_FIELDS})
        score_row.update({field: "false" for field in protocol.GOVERNANCE_INVARIANTS})
        score_rows.append(score_row)

    score_sheet_ref = args.output_dir / "m5_beta_live_score_sheet.csv"
    write_live_score_sheet(score_sheet_ref, score_rows)

    report = {
        "ok": True,
        "protocol": "m5_beta_openai_adapter/v1",
        "execution_status": "answers_generated_codex_judge_pending",
        "suite_id": suite["suite_id"],
        "model": args.model,
        "matrix": {
            "query_count": len(pairs),
            "baseline_answer_runs": len(pairs),
            "treatment_answer_runs": len(pairs),
            "total_answer_runs": len(pairs) * 2,
            "api_judge_runs": 0,
            "codex_judge_pairs_pending": len(pairs),
        },
        "env_file": str(args.env_file),
        "loaded_env_keys": sorted(loaded_env_keys),
        "secret_values_printed": False,
        "artifacts": {
            "score_sheet": str(score_sheet_ref),
            "answer_refs": answer_refs,
            "context_refs": context_refs,
            "codex_judge_packet_refs": packet_refs,
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
            "Codex/human preliminary judge must review the generated packets and "
            "write m5_beta_codex_prelim_judgment artifacts."
        ),
    }
    write_json(args.output_dir / "m5_beta_openai_adapter_report.json", report)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--suite", type=Path, default=protocol.DEFAULT_SUITE)
    parser.add_argument("--env-file", type=Path, default=DEFAULT_ENV_FILE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--query-count", type=int, default=beta.DEFAULT_QUERY_COUNT)
    parser.add_argument("--model", default=os.environ.get("M5_BETA_OPENAI_MODEL", DEFAULT_MODEL))
    parser.add_argument("--max-output-tokens", type=int, default=DEFAULT_MAX_OUTPUT_TOKENS)
    parser.add_argument("--input-cost-per-1m", type=float)
    parser.add_argument("--output-cost-per-1m", type=float)
    args = parser.parse_args(argv)

    try:
        report = run_adapter(args)
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, indent=2, sort_keys=True))
        return 2
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
