from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


def _trace_fixture(path: Path) -> Path:
    payload = [
        {
            "trace_refs": [
                {"kind": "progress_stage", "ref": "load_started"},
                {"kind": "progress_section", "ref": "google_docs"},
                {"kind": "progress_status", "ref": "running"},
            ],
            "metrics": [
                {"metric": "trace.progress_ratio", "value": 0.0, "unit": "ratio"},
                {"metric": "trace.detail.elapsed_seconds", "value": 0.1, "unit": "seconds"},
                {"metric": "trace.stage_family.start", "value": 1, "unit": "count"},
                {"metric": "trace.domain_role.source", "value": 1, "unit": "count"},
                {"metric": "trace.domain_signal.source_ingest", "value": 1, "unit": "count"},
            ],
        },
        {
            "trace_refs": [
                {"kind": "progress_stage", "ref": "load_finished"},
                {"kind": "progress_section", "ref": "google_docs"},
                {"kind": "progress_status", "ref": "complete"},
            ],
            "metrics": [
                {"metric": "trace.progress_ratio", "value": 1.0, "unit": "ratio"},
                {"metric": "trace.detail.elapsed_seconds", "value": 0.3, "unit": "seconds"},
                {"metric": "trace.stage_family.finish", "value": 1, "unit": "count"},
                {"metric": "trace.transition.load-started__to__load-finished", "value": 1, "unit": "count"},
            ],
        },
    ]
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_summarize_zkperf_trace_json(tmp_path: Path) -> None:
    fixture = _trace_fixture(tmp_path / "trace.json")
    observation = tmp_path / "observation.json"
    observation.write_text(
        json.dumps(
            {
                "metrics": [
                    {"metric": "theory.mdl.available", "value": 1, "unit": "flag"},
                    {"metric": "theory.mdl.descent_monotone", "value": 0, "unit": "flag"},
                    {"metric": "theory.dynamics.closest_ok", "value": 1, "unit": "flag"},
                ]
            }
        ),
        encoding="utf-8",
    )
    result = subprocess.run(
        [sys.executable, "scripts/summarize_zkperf_trace.py", "--input", str(fixture), "--observation", str(observation), "--json"],
        cwd=Path.cwd(),
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert payload["stepCount"] == 2
    assert payload["firstStage"] == "load_started"
    assert payload["lastStage"] == "load_finished"
    assert payload["stageCounts"]["load_started"] == 1
    assert payload["sectionCounts"]["google_docs"] == 2
    assert payload["statusCounts"]["running"] == 1
    assert payload["domainRoleCounts"]["source"] == 1
    assert payload["domainSignalCounts"]["source_ingest"] == 1
    assert payload["healthReadout"]["dynamicSignal"] == "active"
    assert payload["healthReadout"]["availability"]["MDL"] == "implemented"
    assert payload["healthReadout"]["mdlSignal"] == "violating"


def test_summarize_zkperf_trace_human(tmp_path: Path) -> None:
    fixture = _trace_fixture(tmp_path / "trace.json")
    result = subprocess.run(
        [sys.executable, "scripts/summarize_zkperf_trace.py", "--input", str(fixture)],
        cwd=Path.cwd(),
        check=True,
        capture_output=True,
        text=True,
    )
    assert "steps: 2" in result.stdout
    assert "first_stage: load_started" in result.stdout
    assert "stage_counts:" in result.stdout
    assert "health_readout:" in result.stdout
    assert "mdl: unavailable" in result.stdout
