#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


def _metric_map(observation: dict) -> dict[str, float]:
    return {
        str(row["metric"]): row["value"]
        for row in observation.get("metrics", [])
        if isinstance(row, dict) and "metric" in row and "value" in row
    }


def _trace_ref_value(observation: dict, kind: str) -> str | None:
    for row in observation.get("trace_refs", []):
        if isinstance(row, dict) and row.get("kind") == kind and row.get("ref") is not None:
            return str(row["ref"])
    return None


def _observation_metric_map(observation: dict | None) -> dict[str, float]:
    if not isinstance(observation, dict):
        return {}
    return _metric_map(observation)


def build_summary(trace_observations: list[dict], *, observation: dict | None = None) -> dict[str, object]:
    stage_counts: Counter[str] = Counter()
    stage_family_counts: Counter[str] = Counter()
    section_counts: Counter[str] = Counter()
    status_counts: Counter[str] = Counter()
    domain_role_counts: Counter[str] = Counter()
    domain_signal_counts: Counter[str] = Counter()
    transition_counts: Counter[str] = Counter()
    progress_ratios: list[float] = []
    elapsed_seconds: list[float] = []
    progress_regressions = 0
    progress_plateaus = 0
    progress_advances = 0

    ordered_stages: list[str] = []
    previous_ratio: float | None = None
    for trace_observation in trace_observations:
        stage = _trace_ref_value(trace_observation, "progress_stage")
        section = _trace_ref_value(trace_observation, "progress_section")
        status = _trace_ref_value(trace_observation, "progress_status")
        if stage:
            stage_counts[stage] += 1
            ordered_stages.append(stage)
        if section:
            section_counts[section] += 1
        if status:
            status_counts[status] += 1

        metrics = _metric_map(trace_observation)
        for name, value in metrics.items():
            if not isinstance(value, (int, float)):
                continue
            if name.startswith("trace.stage_family.") and value:
                stage_family_counts[name.removeprefix("trace.stage_family.")] += 1
            elif name.startswith("trace.domain_role.") and value:
                domain_role_counts[name.removeprefix("trace.domain_role.")] += 1
            elif name.startswith("trace.domain_signal.") and value:
                domain_signal_counts[name.removeprefix("trace.domain_signal.")] += 1
            elif name.startswith("trace.transition.") and value:
                transition_counts[name.removeprefix("trace.transition.")] += 1
        ratio = metrics.get("trace.progress_ratio")
        if isinstance(ratio, (int, float)):
            ratio_value = float(ratio)
            progress_ratios.append(ratio_value)
            if previous_ratio is not None:
                if ratio_value > previous_ratio:
                    progress_advances += 1
                elif ratio_value < previous_ratio:
                    progress_regressions += 1
                else:
                    progress_plateaus += 1
            previous_ratio = ratio_value
        elapsed = metrics.get("trace.detail.elapsed_seconds")
        if isinstance(elapsed, (int, float)):
            elapsed_seconds.append(float(elapsed))

    summary: dict[str, object] = {
        "stepCount": len(trace_observations),
        "stageCounts": dict(stage_counts),
        "stageFamilyCounts": dict(stage_family_counts),
        "sectionCounts": dict(section_counts),
        "statusCounts": dict(status_counts),
        "domainRoleCounts": dict(domain_role_counts),
        "domainSignalCounts": dict(domain_signal_counts),
        "transitionCounts": dict(transition_counts),
    }
    if ordered_stages:
        summary["firstStage"] = ordered_stages[0]
        summary["lastStage"] = ordered_stages[-1]
    if progress_ratios:
        summary["maxProgressRatio"] = max(progress_ratios)
        summary["minProgressRatio"] = min(progress_ratios)
    summary["progressAdvanceCount"] = progress_advances
    summary["progressRegressionCount"] = progress_regressions
    summary["progressPlateauCount"] = progress_plateaus
    if elapsed_seconds:
        summary["maxElapsedSeconds"] = max(elapsed_seconds)
        summary["lastElapsedSeconds"] = elapsed_seconds[-1]
    observation_metrics = _observation_metric_map(observation)
    summary["theoryStatus"] = _theory_status(observation_metrics)
    summary["healthReadout"] = _build_health_readout(summary, observation_metrics)
    return summary


def _theory_status(observation_metrics: dict[str, float]) -> dict[str, str]:
    mdl_status = "implemented" if observation_metrics.get("theory.mdl.available", 0) else "unavailable"
    dynamics_status = (
        "implemented"
        if any(
            observation_metrics.get(name, 0)
            for name in (
                "theory.dynamics.cone_ok",
                "theory.dynamics.fejer_ok",
                "theory.dynamics.closest_ok",
                "theory.dynamics.fejer.available",
                "theory.dynamics.closestpoint.available",
            )
        )
        else "scaffolded"
    )
    return {
        "STRUCTURE": "implemented",
        "SEMANTICS": "implemented",
        "DYNAMICS": dynamics_status,
        "MDL": mdl_status,
        "GEOMETRY": "scaffolded",
        "ALIGNMENT": "scaffolded",
    }


def _build_health_readout(summary: dict[str, object], observation_metrics: dict[str, float]) -> dict[str, object]:
    regressions = int(summary.get("progressRegressionCount", 0) or 0)
    advances = int(summary.get("progressAdvanceCount", 0) or 0)
    domain_signals = summary.get("domainSignalCounts") if isinstance(summary.get("domainSignalCounts"), dict) else {}
    if regressions > 0:
        dynamic_signal = "regressive"
    elif advances == 0:
        dynamic_signal = "flat"
    else:
        dynamic_signal = "active"
    semantic_signal = "observed" if domain_signals else "thin"
    mdl_signal = "unavailable"
    if observation_metrics.get("theory.mdl.available", 0):
        mdl_signal = "monotone" if observation_metrics.get("theory.mdl.descent_monotone", 0) else "violating"
    return {
        "availability": _theory_status(observation_metrics),
        "dynamicSignal": dynamic_signal,
        "semanticSignal": semantic_signal,
        "mdlSignal": mdl_signal,
        "progressMonotonicity": "violated" if regressions > 0 else "bounded",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Summarize stepwise zkperf trace observations.")
    parser.add_argument("--input", type=Path, required=True, help="Path to generated-zkperf-trace-observations.json")
    parser.add_argument("--observation", type=Path, help="Optional final summary observation JSON to enrich theory/health status")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Emit JSON instead of human-readable text")
    args = parser.parse_args(argv)

    payload = json.loads(args.input.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise SystemExit("trace observations input must be a JSON array")

    observation = None
    if args.observation is not None:
        observation = json.loads(args.observation.read_text(encoding="utf-8"))
        if not isinstance(observation, dict):
            raise SystemExit("observation input must be a JSON object")

    summary = build_summary(payload, observation=observation)
    if args.json_output:
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0

    print(f"steps: {summary['stepCount']}")
    if "firstStage" in summary:
        print(f"first_stage: {summary['firstStage']}")
    if "lastStage" in summary:
        print(f"last_stage: {summary['lastStage']}")
    if "maxProgressRatio" in summary:
        print(f"progress_ratio: {summary['minProgressRatio']} -> {summary['maxProgressRatio']}")
    if "lastElapsedSeconds" in summary:
        print(f"elapsed_seconds_last: {summary['lastElapsedSeconds']}")
    print(
        "progress_shape: "
        f"advance={summary['progressAdvanceCount']} "
        f"plateau={summary['progressPlateauCount']} "
        f"regression={summary['progressRegressionCount']}"
    )
    print("stage_counts:")
    for key, value in sorted(summary["stageCounts"].items()):
        print(f"  {key}: {value}")
    if summary["sectionCounts"]:
        print("section_counts:")
        for key, value in sorted(summary["sectionCounts"].items()):
            print(f"  {key}: {value}")
    if summary["statusCounts"]:
        print("status_counts:")
        for key, value in sorted(summary["statusCounts"].items()):
            print(f"  {key}: {value}")
    if summary["domainRoleCounts"]:
        print("domain_role_counts:")
        for key, value in sorted(summary["domainRoleCounts"].items()):
            print(f"  {key}: {value}")
    if summary["domainSignalCounts"]:
        print("domain_signal_counts:")
        for key, value in sorted(summary["domainSignalCounts"].items()):
            print(f"  {key}: {value}")
    health = summary["healthReadout"]
    if isinstance(health, dict):
        print("health_readout:")
        print(f"  dynamics: {health.get('dynamicSignal')}")
        print(f"  semantics: {health.get('semanticSignal')}")
        print(f"  mdl: {health.get('mdlSignal')}")
        print(f"  progress_monotonicity: {health.get('progressMonotonicity')}")
        availability = health.get("availability")
        if isinstance(availability, dict):
            for key, value in availability.items():
                print(f"  {key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
