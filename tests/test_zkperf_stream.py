from __future__ import annotations

import json
from pathlib import Path

from itir_jmd_bridge.cli import main as cli_main
from itir_jmd_bridge.zkperf_stream import (
    build_zkperf_stream_bundle,
    build_zkperf_stream_fixture_from_observations,
    load_zkperf_observations,
    load_zkperf_stream_fixture,
)

STREAM_FIXTURE = Path("docs/planning/jmd_fixtures/zkperf_stream_v1.example.json")
OBSERVATION_FIXTURE = Path("docs/planning/jmd_fixtures/zkperf_on_sl_observation_v1.example.json")


def test_build_zkperf_stream_bundle() -> None:
    fixture = load_zkperf_stream_fixture(STREAM_FIXTURE)
    bundle = build_zkperf_stream_bundle(fixture)
    assert bundle["streamManifest"]["streamId"] == "zkperf-stream-demo"
    assert bundle["streamManifest"]["latestWindowId"] == "window-0002"
    assert bundle["tarDigest"]


def test_build_zkperf_stream_fixture_from_observations_json_array(tmp_path: Path) -> None:
    base = json.loads(OBSERVATION_FIXTURE.read_text(encoding="utf-8"))
    second = json.loads(json.dumps(base))
    second["zkperf_observation_id"] = "zkperf-obsv-0002"
    second["trace_id"] = "trace-20260330-0002"
    second["asserted_at"] = "2026-03-30T10:00:03Z"
    second["proof_refs"] = ["proof:zkperf:run-20260330-a:summary-2"]
    input_path = tmp_path / "observations.json"
    input_path.write_text(json.dumps([base, second]), encoding="utf-8")
    observations = load_zkperf_observations(input_path)
    fixture = build_zkperf_stream_fixture_from_observations(observations)
    assert fixture["streamId"].startswith("zkperf-stream-")
    assert fixture["streamRevision"].startswith("rev-")
    assert [window["windowId"] for window in fixture["windows"]] == ["window-0001", "window-0002"]


def test_build_zkperf_stream_fixture_from_observations_ndjson_chunked(tmp_path: Path) -> None:
    base = json.loads(OBSERVATION_FIXTURE.read_text(encoding="utf-8"))
    items = []
    for idx in range(3):
        item = json.loads(json.dumps(base))
        item["zkperf_observation_id"] = f"zkperf-obsv-100{idx}"
        item["trace_id"] = "trace-20260330-chunk"
        item["asserted_at"] = f"2026-03-30T10:00:0{idx}Z"
        item["proof_refs"] = [f"proof:chunk:{idx}"]
        items.append(item)
    input_path = tmp_path / "observations.ndjson"
    input_path.write_text("\n".join(json.dumps(item) for item in items) + "\n", encoding="utf-8")
    fixture = build_zkperf_stream_fixture_from_observations(
        load_zkperf_observations(input_path),
        stream_id="zkperf-stream-sl-run",
        stream_revision="rev-test",
        max_observations_per_window=2,
    )
    assert fixture["streamId"] == "zkperf-stream-sl-run"
    assert fixture["streamRevision"] == "rev-test"
    assert len(fixture["windows"]) == 2
    assert fixture["windows"][0]["observationIds"] == ["zkperf-obsv-1000", "zkperf-obsv-1001"]
    assert fixture["windows"][1]["observationIds"] == ["zkperf-obsv-1002"]


def test_cli_build_zkperf_stream_from_observations(tmp_path: Path) -> None:
    base = json.loads(OBSERVATION_FIXTURE.read_text(encoding="utf-8"))
    second = json.loads(json.dumps(base))
    second["zkperf_observation_id"] = "zkperf-obsv-2002"
    second["trace_id"] = "trace-20260330-2002"
    second["asserted_at"] = "2026-03-30T10:20:03Z"
    second["proof_refs"] = ["proof:zkperf:run-20260330-a:summary-2002"]
    input_path = tmp_path / "obs.json"
    output_path = tmp_path / "stream.json"
    input_path.write_text(json.dumps({"observations": [base, second]}), encoding="utf-8")
    exit_code = cli_main([
        "build-zkperf-stream-from-observations",
        "--input",
        str(input_path),
        "--stream-id",
        "zkperf-stream-cli",
        "--stream-revision",
        "rev-cli",
        "--output",
        str(output_path),
    ])
    assert exit_code == 0
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["streamId"] == "zkperf-stream-cli"
    assert payload["streamRevision"] == "rev-cli"
    assert payload["windows"][0]["windowId"] == "window-0001"
