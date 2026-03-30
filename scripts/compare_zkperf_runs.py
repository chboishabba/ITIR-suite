#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any


DEFAULT_METRICS = (
    "semantic_gap_score",
    "elapsed_ms",
    "max_rss_kb",
    "payload_bytes",
    "theory.mdl.descent_monotone",
    "theory.mdl.violation_count",
    "theory.mdl.worst_increase",
)

LOWER_IS_BETTER = {
    "semantic_gap_score",
    "elapsed_ms",
    "max_rss_kb",
    "wrapperTotalMs",
    "theory.mdl.violation_count",
    "theory.mdl.worst_increase",
}


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _metric_map(observation: dict[str, Any]) -> dict[str, float]:
    values: dict[str, float] = {}
    for row in observation.get("metrics", []):
        if not isinstance(row, dict):
            continue
        metric = row.get("metric")
        value = row.get("value")
        if isinstance(metric, str) and isinstance(value, (int, float)):
            values[metric] = float(value)
    return values


def _resolve_paths(
    *,
    output_root: Path | None,
    observation_path: Path | None,
    trace_path: Path | None,
    timings_path: Path | None,
) -> tuple[Path, Path | None, Path | None]:
    if output_root is not None:
        root = output_root.resolve()
        observation = observation_path or (root / "generated-zkperf-observation.json")
        trace = trace_path or (root / "generated-zkperf-trace-observations.json")
        timings = timings_path or (root / "timings.json")
    else:
        if observation_path is None:
            raise SystemExit("missing observation path")
        observation = observation_path.resolve()
        trace = trace_path.resolve() if trace_path else None
        timings = timings_path.resolve() if timings_path else None
    if not observation.exists():
        raise SystemExit(f"missing observation file: {observation}")
    if trace is not None and not trace.exists():
        trace = None
    if timings is not None and not timings.exists():
        timings = None
    return observation, trace, timings


def _load_run_payload(
    *,
    label: str,
    output_root: Path | None,
    observation_path: Path | None,
    trace_path: Path | None,
    timings_path: Path | None,
) -> dict[str, Any]:
    resolved_observation, resolved_trace, resolved_timings = _resolve_paths(
        output_root=output_root,
        observation_path=observation_path,
        trace_path=trace_path,
        timings_path=timings_path,
    )
    observation = _load_json(resolved_observation)
    if not isinstance(observation, dict):
        raise SystemExit(f"observation must be a JSON object: {resolved_observation}")
    trace_steps = None
    if resolved_trace is not None:
        trace_payload = _load_json(resolved_trace)
        if isinstance(trace_payload, list):
            trace_steps = len(trace_payload)
    timings = _load_json(resolved_timings) if resolved_timings is not None else {}
    if not isinstance(timings, dict):
        timings = {}
    return {
        "label": label,
        "observationPath": str(resolved_observation),
        "tracePath": str(resolved_trace) if resolved_trace is not None else None,
        "timingsPath": str(resolved_timings) if resolved_timings is not None else None,
        "runId": observation.get("run_id"),
        "traceId": observation.get("trace_id"),
        "metrics": _metric_map(observation),
        "traceStepCount": trace_steps,
        "wrapperTotalMs": timings.get("wrapperTotalMs"),
    }


def _diff_values(left: float | None, right: float | None) -> float | None:
    if left is None or right is None:
        return None
    return right - left


def compare_runs(left: dict[str, Any], right: dict[str, Any], metric_names: list[str]) -> dict[str, Any]:
    metric_deltas: list[dict[str, Any]] = []
    for name in metric_names:
        left_value = left["metrics"].get(name)
        right_value = right["metrics"].get(name)
        if left_value is None and right_value is None:
            continue
        delta = _diff_values(left_value, right_value)
        metric_deltas.append(
            {
                "metric": name,
                "left": left_value,
                "right": right_value,
                "delta": delta,
                "judgement": _judge_metric_delta(name, delta),
            }
        )

    semantic_trend = _judge_metric_delta(
        "semantic_gap_score",
        _diff_values(left["metrics"].get("semantic_gap_score"), right["metrics"].get("semantic_gap_score")),
    )
    runtime_trend = _judge_metric_delta(
        "elapsed_ms",
        _diff_values(left["metrics"].get("elapsed_ms"), right["metrics"].get("elapsed_ms")),
    )
    memory_trend = _judge_metric_delta(
        "max_rss_kb",
        _diff_values(left["metrics"].get("max_rss_kb"), right["metrics"].get("max_rss_kb")),
    )
    return {
        "left": {
            "label": left["label"],
            "runId": left["runId"],
            "traceId": left["traceId"],
            "observationPath": left["observationPath"],
            "tracePath": left["tracePath"],
            "timingsPath": left["timingsPath"],
            "traceStepCount": left["traceStepCount"],
            "wrapperTotalMs": left["wrapperTotalMs"],
        },
        "right": {
            "label": right["label"],
            "runId": right["runId"],
            "traceId": right["traceId"],
            "observationPath": right["observationPath"],
            "tracePath": right["tracePath"],
            "timingsPath": right["timingsPath"],
            "traceStepCount": right["traceStepCount"],
            "wrapperTotalMs": right["wrapperTotalMs"],
        },
        "metricDeltas": metric_deltas,
        "traceStepDelta": _diff_values(left["traceStepCount"], right["traceStepCount"]),
        "wrapperTotalMsDelta": _diff_values(left["wrapperTotalMs"], right["wrapperTotalMs"]),
        "regressionSummary": {
            "semanticTrend": semantic_trend,
            "runtimeTrend": runtime_trend,
            "memoryTrend": memory_trend,
            "overall": _combine_trends(semantic_trend, runtime_trend, memory_trend),
        },
    }


def _judge_metric_delta(metric: str, delta: float | None) -> str:
    if delta is None:
        return "unavailable"
    if abs(delta) < 1e-9:
        return "flat"
    if metric in LOWER_IS_BETTER:
        return "improved" if delta < 0 else "regressed"
    return "increased" if delta > 0 else "decreased"


def _combine_trends(*trends: str) -> str:
    meaningful = [trend for trend in trends if trend not in {"flat", "unavailable"}]
    if not meaningful:
        return "stable"
    if all(trend == "improved" for trend in meaningful):
        return "improved"
    if any(trend == "regressed" for trend in meaningful):
        return "regressed"
    return "mixed"


def _print_human(result: dict[str, Any]) -> None:
    left = result["left"]
    right = result["right"]
    print(f"left_run: {left.get('runId')}")
    print(f"right_run: {right.get('runId')}")
    if result.get("traceStepDelta") is not None:
        print(
            f"trace_steps: {left.get('traceStepCount')} -> {right.get('traceStepCount')} "
            f"(delta={result['traceStepDelta']})"
        )
    if result.get("wrapperTotalMsDelta") is not None:
        print(
            f"wrapper_total_ms: {left.get('wrapperTotalMs')} -> {right.get('wrapperTotalMs')} "
            f"(delta={result['wrapperTotalMsDelta']})"
        )
    print("metric_deltas:")
    for row in result["metricDeltas"]:
        print(
            f"  {row['metric']}: {row.get('left')} -> {row.get('right')} "
            f"(delta={row.get('delta')}, judgement={row.get('judgement')})"
        )
    summary = result.get("regressionSummary")
    if isinstance(summary, dict):
        print("regression_summary:")
        print(f"  semantic: {summary.get('semanticTrend')}")
        print(f"  runtime: {summary.get('runtimeTrend')}")
        print(f"  memory: {summary.get('memoryTrend')}")
        print(f"  overall: {summary.get('overall')}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Compare two zkperf runs from observation files or wrapper output roots."
    )
    parser.add_argument("--left-output-root", type=Path)
    parser.add_argument("--right-output-root", type=Path)
    parser.add_argument("--left-observation", type=Path)
    parser.add_argument("--right-observation", type=Path)
    parser.add_argument("--left-trace", type=Path)
    parser.add_argument("--right-trace", type=Path)
    parser.add_argument("--left-timings", type=Path)
    parser.add_argument("--right-timings", type=Path)
    parser.add_argument(
        "--metric",
        action="append",
        dest="metrics",
        help="Metric name to compare. Repeatable. Defaults to a bounded set.",
    )
    parser.add_argument("--json", action="store_true", dest="json_output")
    args = parser.parse_args(argv)

    left = _load_run_payload(
        label="left",
        output_root=args.left_output_root,
        observation_path=args.left_observation,
        trace_path=args.left_trace,
        timings_path=args.left_timings,
    )
    right = _load_run_payload(
        label="right",
        output_root=args.right_output_root,
        observation_path=args.right_observation,
        trace_path=args.right_trace,
        timings_path=args.right_timings,
    )
    metric_names = args.metrics if args.metrics else list(DEFAULT_METRICS)
    result = compare_runs(left, right, metric_names)

    if args.json_output:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        _print_human(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
