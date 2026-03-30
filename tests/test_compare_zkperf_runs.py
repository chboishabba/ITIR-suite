from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


def _observation(
    path: Path,
    *,
    run_id: str,
    elapsed_ms: int,
    max_rss_kb: int,
    semantic_gap: float,
    mdl_monotone: int = 1,
    mdl_violations: int = 0,
) -> None:
    payload = {
        "run_id": run_id,
        "trace_id": f"sl-trace:{run_id}",
        "metrics": [
            {"metric": "elapsed_ms", "value": elapsed_ms, "unit": "milliseconds"},
            {"metric": "max_rss_kb", "value": max_rss_kb, "unit": "kilobytes"},
            {"metric": "semantic_gap_score", "value": semantic_gap, "unit": "semantic_cost"},
            {"metric": "theory.mdl.descent_monotone", "value": mdl_monotone, "unit": "flag"},
            {"metric": "theory.mdl.violation_count", "value": mdl_violations, "unit": "count"},
        ],
    }
    path.write_text(json.dumps(payload), encoding="utf-8")


def _trace(path: Path, count: int) -> None:
    payload = [{"trace_refs": [], "metrics": []} for _ in range(count)]
    path.write_text(json.dumps(payload), encoding="utf-8")


def _timings(path: Path, wrapper_total_ms: int) -> None:
    payload = {"wrapperTotalMs": wrapper_total_ms}
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_compare_zkperf_runs_from_observations_json(tmp_path: Path) -> None:
    left_obs = tmp_path / "left-observation.json"
    right_obs = tmp_path / "right-observation.json"
    _observation(left_obs, run_id="run:left", elapsed_ms=1000, max_rss_kb=200000, semantic_gap=8.0, mdl_monotone=0, mdl_violations=2)
    _observation(right_obs, run_id="run:right", elapsed_ms=900, max_rss_kb=180000, semantic_gap=5.0, mdl_monotone=1, mdl_violations=0)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/compare_zkperf_runs.py",
            "--left-observation",
            str(left_obs),
            "--right-observation",
            str(right_obs),
            "--json",
        ],
        cwd=Path.cwd(),
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    deltas = {row["metric"]: row["delta"] for row in payload["metricDeltas"]}
    judgements = {row["metric"]: row["judgement"] for row in payload["metricDeltas"]}
    assert payload["left"]["runId"] == "run:left"
    assert payload["right"]["runId"] == "run:right"
    assert deltas["elapsed_ms"] == -100.0
    assert deltas["max_rss_kb"] == -20000.0
    assert deltas["semantic_gap_score"] == -3.0
    assert judgements["theory.mdl.violation_count"] == "improved"
    assert judgements["semantic_gap_score"] == "improved"
    assert payload["regressionSummary"]["overall"] == "improved"


def test_compare_zkperf_runs_from_output_roots(tmp_path: Path) -> None:
    left_root = tmp_path / "left"
    right_root = tmp_path / "right"
    left_root.mkdir()
    right_root.mkdir()
    _observation(left_root / "generated-zkperf-observation.json", run_id="run:left", elapsed_ms=700, max_rss_kb=150000, semantic_gap=6.0)
    _observation(right_root / "generated-zkperf-observation.json", run_id="run:right", elapsed_ms=800, max_rss_kb=170000, semantic_gap=7.0)
    _trace(left_root / "generated-zkperf-trace-observations.json", 4)
    _trace(right_root / "generated-zkperf-trace-observations.json", 7)
    _timings(left_root / "timings.json", 5000)
    _timings(right_root / "timings.json", 6500)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/compare_zkperf_runs.py",
            "--left-output-root",
            str(left_root),
            "--right-output-root",
            str(right_root),
        ],
        cwd=Path.cwd(),
        check=True,
        capture_output=True,
        text=True,
    )
    assert "left_run: run:left" in result.stdout
    assert "right_run: run:right" in result.stdout
    assert "trace_steps: 4 -> 7 (delta=3)" in result.stdout
    assert "wrapper_total_ms: 5000 -> 6500 (delta=1500)" in result.stdout
    assert "regression_summary:" in result.stdout
    assert "overall: regressed" in result.stdout
