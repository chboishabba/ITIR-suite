from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sqlite3
import subprocess
import sys

SENSIBLAW_ROOT = Path("SensibLaw").resolve()
SENSIBLAW_SRC = SENSIBLAW_ROOT / "src"
for path in (SENSIBLAW_ROOT, SENSIBLAW_SRC):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from fact_intake import persist_contested_affidavit_review


def _load_script_module():
    script_path = Path("scripts/render_sl_zkperf_spectrogram.py").resolve()
    spec = importlib.util.spec_from_file_location("render_sl_zkperf_spectrogram", script_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _sample_contested_review_payload() -> dict:
    return {
        "version": "affidavit.coverage.review.v1",
        "fixture_kind": "contested_review",
        "source_input": {
            "path": "https://example.test/response",
            "source_kind": "google_doc",
            "source_label": "response_doc",
        },
        "affidavit_input": {
            "path": "https://example.test/affidavit",
            "character_count": 123,
        },
        "summary": {
            "source_row_count": 1,
            "affidavit_proposition_count": 1,
            "covered_count": 1,
            "partial_count": 0,
            "contested_affidavit_count": 0,
            "unsupported_affidavit_count": 0,
            "missing_review_count": 0,
            "contested_source_count": 0,
            "abstained_source_count": 0,
            "semantic_basis_counts": {"structural": 1},
            "promotion_status_counts": {"promoted_true": 1},
            "support_direction_counts": {"for": 1},
            "conflict_state_counts": {"clean": 1},
            "evidentiary_state_counts": {"supported": 1},
            "operational_status_counts": {"claim_with_support": 1},
        },
        "affidavit_rows": [
            {
                "proposition_id": "aff-prop:p1-s1",
                "paragraph_id": "p1",
                "paragraph_order": 1,
                "sentence_order": 1,
                "text": "Test proposition",
                "coverage_status": "covered",
                "best_source_row_id": "source-row-1",
                "best_match_score": 0.9,
                "best_adjusted_match_score": 0.95,
                "best_match_basis": "structural",
                "best_match_excerpt": "Test excerpt",
                "duplicate_match_excerpt": "",
                "best_response_role": "admission",
                "support_status": "supported",
                "semantic_basis": "structural",
                "promotion_status": "promoted_true",
                "promotion_basis": "structural",
                "promotion_reason": "matched",
                "support_direction": "for",
                "conflict_state": "clean",
                "evidentiary_state": "supported",
                "operational_status": "claim_with_support",
                "relation_root": "agrees",
                "relation_leaf": "predicate_text",
                "primary_target_component": "predicate_text",
                "explanation": {"reason": "demo"},
                "missing_dimensions": [],
                "semantic_candidate": {"schema_version": "contested.semantic_candidate.v1"},
                "claim": {"text": "Test proposition"},
                "response": {"text": "Test excerpt"},
                "justifications": [],
                "matched_source_rows": [],
            }
        ],
        "source_review_rows": [
            {
                "source_row_id": "source-row-1",
                "source_kind": "google_doc",
                "text": "Test excerpt",
                "candidate_status": "candidate",
                "review_status": "accepted",
                "best_affidavit_proposition_id": "aff-prop:p1-s1",
                "best_match_score": 0.9,
                "best_adjusted_match_score": 0.95,
                "best_match_basis": "structural",
                "best_match_excerpt": "Test excerpt",
                "best_response_role": "admission",
                "matched_affidavit_proposition_ids": ["aff-prop:p1-s1"],
                "related_affidavit_proposition_ids": [],
                "reason_codes": [],
                "workload_classes": [],
                "candidate_anchors": [],
            }
        ],
        "zelph_claim_state_facts": [
            {
                "fact_id": "zelph:1",
                "proposition_id": "aff-prop:p1-s1",
                "best_source_row_id": "source-row-1",
                "fact_kind": "contested_claim_state",
                "semantic_basis": "structural",
                "promotion_status": "promoted_true",
                "promotion_basis": "structural",
                "support_direction": "for",
                "conflict_state": "clean",
                "evidentiary_state": "supported",
                "operational_status": "claim_with_support",
            }
        ],
    }


def _sample_fixture(path: Path) -> Path:
    fixture = {
        "contractVersion": "zkperf-stream/v1",
        "streamId": "zkperf-stream-demo",
        "streamRevision": "rev-demo",
        "streamKind": "zkperf-observation-stream",
        "windowingMode": "grouped-by-run",
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
                            ],
                        }
                    ]
                },
            }
        ],
    }
    path.write_text(json.dumps(fixture), encoding="utf-8")
    return path


def test_render_sl_zkperf_spectrogram_from_db(tmp_path: Path) -> None:
    db_path = tmp_path / "itir.sqlite"
    with sqlite3.connect(str(db_path)) as conn:
        persist_summary = persist_contested_affidavit_review(conn, _sample_contested_review_payload())

    out_dir = tmp_path / "out"
    summary_path = tmp_path / "summary.json"
    command = [
        sys.executable,
        "scripts/render_sl_zkperf_spectrogram.py",
        "--db-path",
        str(db_path),
        "--review-run-id",
        persist_summary["review_run_id"],
        "--output-dir",
        str(out_dir),
        "--write-observation",
        "--write-fixture",
        "--summary-output",
        str(summary_path),
    ]
    subprocess.run(command, cwd=Path.cwd(), check=True)

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["inputMode"] == "db"
    assert Path(summary["featureSpectrogram"]["outputPath"]).exists()
    assert Path(summary["pcaSpectrogram"]["outputPath"]).exists()
    assert Path(summary["observationPath"]).exists()
    assert Path(summary["fixturePath"]).exists()


def test_render_sl_zkperf_spectrogram_from_fixture(tmp_path: Path) -> None:
    fixture_path = _sample_fixture(tmp_path / "fixture.json")
    out_dir = tmp_path / "out"
    summary_path = tmp_path / "summary.json"
    command = [
        sys.executable,
        "scripts/render_sl_zkperf_spectrogram.py",
        "--fixture",
        str(fixture_path),
        "--output-dir",
        str(out_dir),
        "--cluster-k",
        "1",
        "--summary-output",
        str(summary_path),
    ]
    subprocess.run(command, cwd=Path.cwd(), check=True)

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["inputMode"] == "fixture"
    assert Path(summary["featureSpectrogram"]["outputPath"]).exists()
    assert Path(summary["pcaSpectrogram"]["outputPath"]).exists()
    assert "clusterLabels" not in summary["featureSpectrogram"]


def test_render_sl_zkperf_spectrogram_cluster_report(tmp_path: Path) -> None:
    fixture_path = _sample_fixture(tmp_path / "fixture.json")
    out_dir = tmp_path / "out"
    summary_path = tmp_path / "summary.json"
    command = [
        sys.executable,
        "scripts/render_sl_zkperf_spectrogram.py",
        "--fixture",
        str(fixture_path),
        "--output-dir",
        str(out_dir),
        "--cluster-k",
        "2",
        "--cluster-report",
        "--cluster-top-metrics",
        "2",
        "--summary-output",
        str(summary_path),
    ]
    subprocess.run(command, cwd=Path.cwd(), check=True)

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert "clusterReportPath" in summary
    cluster_report = json.loads(Path(summary["clusterReportPath"]).read_text(encoding="utf-8"))
    assert cluster_report["clusterCount"] >= 1
    assert "topMetrics" in cluster_report["clusters"][0]


def test_render_sl_zkperf_spectrogram_cluster_report_with_query_selection(tmp_path: Path) -> None:
    fixture_path = _sample_fixture(tmp_path / "fixture.json")
    out_dir = tmp_path / "out"
    summary_path = tmp_path / "summary.json"
    command = [
        sys.executable,
        "scripts/render_sl_zkperf_spectrogram.py",
        "--fixture",
        str(fixture_path),
        "--output-dir",
        str(out_dir),
        "--cluster-k",
        "2",
        "--cluster-report",
        "--query-preset",
        "semantic-gap",
        "--summary-output",
        str(summary_path),
    ]
    subprocess.run(command, cwd=Path.cwd(), check=True)

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    cluster_report = summary["clusterReport"]
    assert cluster_report["selection"]["mode"] == "query_alignment"
    assert cluster_report["selection"]["recommendedClusterLabels"]
    assert cluster_report["selection"]["recommendedRows"]
    assert "selectionFixturePath" in summary
    selection_fixture = json.loads(Path(summary["selectionFixturePath"]).read_text(encoding="utf-8"))
    assert selection_fixture["selectionMode"] == "query_alignment"


def test_render_sl_zkperf_spectrogram_with_query_metrics(tmp_path: Path) -> None:
    fixture_path = _sample_fixture(tmp_path / "fixture.json")
    out_dir = tmp_path / "out"
    summary_path = tmp_path / "summary.json"
    command = [
        sys.executable,
        "scripts/render_sl_zkperf_spectrogram.py",
        "--fixture",
        str(fixture_path),
        "--output-dir",
        str(out_dir),
        "--query-metric",
        "summary.covered_count=1",
        "--query-metric",
        "summary.missing_review_count=-1",
        "--summary-output",
        str(summary_path),
    ]
    subprocess.run(command, cwd=Path.cwd(), check=True)

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert "querySpectrogram" in summary
    assert Path(summary["querySpectrogram"]["outputPath"]).exists()
    assert summary["querySpectrogram"]["queryFeatureNames"] == [
        "summary.covered_count",
        "summary.missing_review_count",
    ]


def test_render_sl_zkperf_spectrogram_with_query_preset(tmp_path: Path) -> None:
    fixture_path = _sample_fixture(tmp_path / "fixture.json")
    out_dir = tmp_path / "out"
    summary_path = tmp_path / "summary.json"
    command = [
        sys.executable,
        "scripts/render_sl_zkperf_spectrogram.py",
        "--fixture",
        str(fixture_path),
        "--output-dir",
        str(out_dir),
        "--query-preset",
        "semantic-gap",
        "--summary-output",
        str(summary_path),
    ]
    subprocess.run(command, cwd=Path.cwd(), check=True)

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert "querySpectrogram" in summary
    assert summary["querySpectrogram"]["queryPresetNames"] == ["semantic-gap"]
    assert summary["querySpectrogram"]["queryPresetMetrics"] == {
        "summary.contested_affidavit_count": 2.0,
        "summary.covered_count": 1.0,
        "summary.missing_review_count": 3.0,
        "summary.unresolved_conflict_count": 2.5,
    }
    assert Path(summary["querySpectrogram"]["outputPath"]).exists()
    assert summary["querySpectrogram"]["queryFeatureNames"] == [
        "summary.covered_count",
        "summary.missing_review_count",
    ]


def test_render_sl_zkperf_spectrogram_with_query_intent(tmp_path: Path) -> None:
    fixture_path = _sample_fixture(tmp_path / "fixture.json")
    out_dir = tmp_path / "out"
    summary_path = tmp_path / "summary.json"
    command = [
        sys.executable,
        "scripts/render_sl_zkperf_spectrogram.py",
        "--fixture",
        str(fixture_path),
        "--output-dir",
        str(out_dir),
        "--query-intent",
        "coverage-recovery",
        "--summary-output",
        str(summary_path),
    ]
    subprocess.run(command, cwd=Path.cwd(), check=True)

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["querySpectrogram"]["queryIntentNames"] == ["coverage-recovery"]
    assert "semantic-gap" in summary["querySpectrogram"]["queryPresetNames"]
    assert "coverage-focus" in summary["querySpectrogram"]["queryPresetNames"]


def test_render_sl_zkperf_spectrogram_lists_query_catalog(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/render_sl_zkperf_spectrogram.py",
            "--list-query-presets",
        ],
        cwd=Path.cwd(),
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert "semantic-gap" in payload["queryPresets"]
    assert payload["queryIntents"]["coverage-recovery"] == ["coverage-focus", "semantic-gap"]


def test_render_sl_zkperf_spectrogram_from_hf_index_with_mocked_resolution(tmp_path: Path, monkeypatch) -> None:
    module = _load_script_module()
    fixture_path = _sample_fixture(tmp_path / "fixture-seed.json")
    out_dir = tmp_path / "out"
    summary_path = tmp_path / "summary.json"

    def fake_resolve_zkperf_stream_from_index_hf(**kwargs):
        assert kwargs["fixture_path"] == fixture_path
        assert kwargs["index_hf_uri"] == "hf://datasets/example/zkperf/demo.index.json"
        return {
            "streamId": "zkperf-stream-remote",
            "streamRevision": "rev-remote",
            "windows": [
                {
                    "window": {"windowId": "window-0009", "sequence": 9},
                    "payload": {
                        "json": {
                            "observations": [
                                {
                                    "zkperf_observation_id": "obs-remote",
                                    "metrics": [
                                        {"metric": "summary.covered_count", "value": 3, "unit": "count"},
                                        {"metric": "summary.missing_review_count", "value": 1, "unit": "count"},
                                    ],
                                }
                            ]
                        }
                    },
                }
            ],
        }

    monkeypatch.setattr(module, "resolve_zkperf_stream_from_index_hf", fake_resolve_zkperf_stream_from_index_hf)
    rc = module.main(
        [
            "--index-hf-uri",
            "hf://datasets/example/zkperf/demo.index.json",
            "--fixture-seed",
            str(fixture_path),
            "--output-dir",
            str(out_dir),
            "--write-fixture",
            "--summary-output",
            str(summary_path),
        ]
    )
    assert rc == 0

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["inputMode"] == "hf_index"
    assert Path(summary["resolvedFixturePath"]).exists()
    assert Path(summary["featureSpectrogram"]["outputPath"]).exists()
    assert Path(summary["pcaSpectrogram"]["outputPath"]).exists()
