from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from itir_jmd_bridge.zkperf_viz import render_zkperf_feature_spectrogram


def _fixture() -> dict:
    return {
        "streamId": "zkperf-stream-demo",
        "streamRevision": "rev-demo",
        "windows": [
            {
                "windowId": "window-0001",
                "sequence": 1,
                "payload": {
                    "observations": [
                        {
                            "zkperf_observation_id": "obs-1",
                            "metrics": [
                                {"metric": "summary.covered_count", "value": 1, "unit": "count"},
                                {"metric": "summary.missing_review_count", "value": 5, "unit": "count"},
                                {"metric": "semantic_gap_score", "value": 7, "unit": "semantic_cost"},
                                {"metric": "trace.stage_family.progress", "value": 1, "unit": "count"},
                                {"metric": "trace.domain_signal.review_gap", "value": 1, "unit": "count"},
                            ],
                        },
                        {
                            "zkperf_observation_id": "obs-2",
                            "metrics": [
                                {"metric": "summary.covered_count", "value": 2, "unit": "count"},
                                {"metric": "summary.missing_review_count", "value": 3, "unit": "count"},
                                {"metric": "semantic_gap_score", "value": 4, "unit": "semantic_cost"},
                                {"metric": "trace.stage_family.finish", "value": 1, "unit": "count"},
                                {"metric": "trace.domain_signal.coverage_recovered", "value": 1, "unit": "count"},
                            ],
                        },
                    ]
                },
            },
            {
                "windowId": "window-0002",
                "sequence": 2,
                "payload": {
                    "observations": [
                        {
                            "zkperf_observation_id": "obs-3",
                            "metrics": [
                                {"metric": "summary.covered_count", "value": 4, "unit": "count"},
                                {"metric": "summary.missing_review_count", "value": 1, "unit": "count"},
                                {"metric": "semantic_gap_score", "value": 2, "unit": "semantic_cost"},
                                {"metric": "trace.stage_family.finish", "value": 1, "unit": "count"},
                                {"metric": "trace.domain_signal.coverage_recovered", "value": 1, "unit": "count"},
                            ],
                        }
                    ]
                },
            },
        ],
    }


def test_inspect_zkperf_clusters_json(tmp_path: Path) -> None:
    fixture = _fixture()
    metadata_path = tmp_path / "feature.json"
    render_zkperf_feature_spectrogram(
        fixture,
        output_path=tmp_path / "feature.png",
        metadata_path=metadata_path,
        top_k_features=3,
        cluster_k=2,
    )

    result = subprocess.run(
        [sys.executable, "scripts/inspect_zkperf_clusters.py", "--input", str(metadata_path), "--json"],
        cwd=Path.cwd(),
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert payload["streamId"] == "zkperf-stream-demo"
    assert payload["rowCount"] == 3
    assert payload["clusterCount"] == 2
    assert sum(payload["clusterCounts"].values()) == 3
    assert payload["clusters"][0]["firstRow"] == "0001:window-0001:1"
    assert payload["clusters"][-1]["lastRow"] == "0002:window-0002:1"


def test_inspect_zkperf_clusters_with_fixture_drilldown(tmp_path: Path) -> None:
    fixture = _fixture()
    fixture_path = tmp_path / "fixture.json"
    fixture_path.write_text(json.dumps(fixture), encoding="utf-8")
    metadata_path = tmp_path / "feature.json"
    render_zkperf_feature_spectrogram(
        fixture,
        output_path=tmp_path / "feature.png",
        metadata_path=metadata_path,
        top_k_features=3,
        cluster_k=2,
    )

    result = subprocess.run(
        [
            sys.executable,
            "scripts/inspect_zkperf_clusters.py",
            "--input",
            str(metadata_path),
            "--fixture",
            str(fixture_path),
            "--largest-only",
            "--top-metrics",
            "2",
            "--json",
        ],
        cwd=Path.cwd(),
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert payload["clusterCount"] == 1
    assert "topMetrics" in payload["clusters"][0]
    assert len(payload["clusters"][0]["topMetrics"]) <= 2
    assert payload["clusters"][0]["signals"]["matchedRowCount"] >= 1
    assert "dominantStageFamilies" in payload["clusters"][0]["signals"]
    assert "retrievalCandidates" in payload["clusters"][0]


def test_inspect_zkperf_clusters_with_query_selection(tmp_path: Path) -> None:
    fixture = _fixture()
    fixture_path = tmp_path / "fixture.json"
    fixture_path.write_text(json.dumps(fixture), encoding="utf-8")
    metadata_path = tmp_path / "feature.json"
    render_zkperf_feature_spectrogram(
        fixture,
        output_path=tmp_path / "feature.png",
        metadata_path=metadata_path,
        top_k_features=3,
        cluster_k=2,
    )
    query_metadata_path = tmp_path / "query.json"
    query_metadata_path.write_text(
        json.dumps(
            {
                "rowLabels": [
                    "0001:window-0001:1",
                    "0001:window-0001:2",
                    "0002:window-0002:1",
                ],
                "scores": [0.5, 1.5, 3.0],
            }
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            "scripts/inspect_zkperf_clusters.py",
            "--input",
            str(metadata_path),
            "--fixture",
            str(fixture_path),
            "--query-metadata",
            str(query_metadata_path),
            "--select-top-clusters",
            "1",
            "--select-top-rows",
            "2",
            "--json",
        ],
        cwd=Path.cwd(),
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert payload["selection"]["mode"] == "query_alignment"
    assert len(payload["selection"]["recommendedClusterLabels"]) == 1
    assert len(payload["selection"]["recommendedRows"]) <= 2
    assert payload["selection"]["recommendedRows"][0]["rowLabel"] == "0002:window-0002:1"


def test_inspect_zkperf_clusters_writes_selection_fixture(tmp_path: Path) -> None:
    fixture = _fixture()
    fixture_path = tmp_path / "fixture.json"
    fixture_path.write_text(json.dumps(fixture), encoding="utf-8")
    metadata_path = tmp_path / "feature.json"
    render_zkperf_feature_spectrogram(
        fixture,
        output_path=tmp_path / "feature.png",
        metadata_path=metadata_path,
        top_k_features=3,
        cluster_k=2,
    )
    query_metadata_path = tmp_path / "query.json"
    query_metadata_path.write_text(
        json.dumps(
            {
                "rowLabels": [
                    "0001:window-0001:1",
                    "0001:window-0001:2",
                    "0002:window-0002:1",
                ],
                "scores": [0.5, 1.5, 3.0],
            }
        ),
        encoding="utf-8",
    )
    selection_fixture_path = tmp_path / "selection.json"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/inspect_zkperf_clusters.py",
            "--input",
            str(metadata_path),
            "--fixture",
            str(fixture_path),
            "--query-metadata",
            str(query_metadata_path),
            "--select-top-clusters",
            "1",
            "--select-top-rows",
            "1",
            "--selection-fixture-output",
            str(selection_fixture_path),
            "--json",
        ],
        cwd=Path.cwd(),
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    selection_fixture = json.loads(selection_fixture_path.read_text(encoding="utf-8"))
    assert payload["selectionFixturePath"] == str(selection_fixture_path.resolve())
    assert selection_fixture["selectionMode"] == "query_alignment"
    assert len(selection_fixture["windows"]) == 1
    assert selection_fixture["windows"][0]["windowId"] == "window-0002"


def test_inspect_zkperf_clusters_human(tmp_path: Path) -> None:
    fixture = _fixture()
    metadata_path = tmp_path / "feature.json"
    render_zkperf_feature_spectrogram(
        fixture,
        output_path=tmp_path / "feature.png",
        metadata_path=metadata_path,
        top_k_features=3,
        cluster_k=2,
    )

    result = subprocess.run(
        [sys.executable, "scripts/inspect_zkperf_clusters.py", "--input", str(metadata_path)],
        cwd=Path.cwd(),
        check=True,
        capture_output=True,
        text=True,
    )
    assert "stream_id: zkperf-stream-demo" in result.stdout
    assert "cluster_count: 2" in result.stdout
    assert "clusters:" in result.stdout
