from __future__ import annotations

import json
from pathlib import Path

from itir_jmd_bridge.zkperf_viz import (
    build_zkperf_feature_spectrogram_payload,
    render_zkperf_feature_spectrogram,
    render_zkperf_pca_spectrogram,
    render_zkperf_query_spectrogram,
)


def _fixture(tmp_path: Path) -> Path:
    fixture = {
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
                            ],
                        }
                    ]
                },
            },
            {
                "windowId": "window-0002",
                "sequence": 2,
                "payload": {
                    "observations": [
                        {
                            "zkperf_observation_id": "obs-2",
                            "metrics": [
                                {"metric": "summary.covered_count", "value": 2, "unit": "count"},
                                {"metric": "summary.missing_review_count", "value": 3, "unit": "count"},
                                {"metric": "semantic_gap_score", "value": 4, "unit": "semantic_cost"},
                            ],
                        }
                    ]
                },
            },
        ],
    }
    path = tmp_path / "fixture.json"
    path.write_text(json.dumps(fixture), encoding="utf-8")
    return path


def test_build_feature_spectrogram_payload(tmp_path: Path) -> None:
    fixture = json.loads(_fixture(tmp_path).read_text(encoding="utf-8"))
    payload = build_zkperf_feature_spectrogram_payload(
        fixture,
        top_k_features=3,
        feature_prefixes=["summary", "semantic_gap_score"],
    )
    assert payload["streamId"] == "zkperf-stream-demo"
    assert len(payload["rowLabels"]) == 2
    assert "semantic_gap_score" in payload["featureNames"]
    assert len(payload["matrix"]) == 2


def test_render_feature_and_pca_spectrogram(tmp_path: Path) -> None:
    fixture = json.loads(_fixture(tmp_path).read_text(encoding="utf-8"))
    feature_png = tmp_path / "feature.png"
    feature_meta = tmp_path / "feature.json"
    pca_png = tmp_path / "pca.png"
    pca_meta = tmp_path / "pca.json"
    query_png = tmp_path / "query.png"
    query_meta = tmp_path / "query.json"

    feature_payload = render_zkperf_feature_spectrogram(
        fixture,
        output_path=feature_png,
        metadata_path=feature_meta,
        top_k_features=3,
        cluster_k=2,
    )
    pca_payload = render_zkperf_pca_spectrogram(
        fixture,
        output_path=pca_png,
        metadata_path=pca_meta,
        top_k_features=3,
        components=2,
        cluster_k=2,
    )
    query_payload = render_zkperf_query_spectrogram(
        fixture,
        output_path=query_png,
        metadata_path=query_meta,
        query_metrics={"summary.covered_count": 1.0, "summary.missing_review_count": -1.0},
    )

    assert feature_png.exists()
    assert feature_png.stat().st_size > 0
    assert feature_meta.exists()
    assert feature_payload["featureCount"] >= 1
    assert len(feature_payload.get("clusterLabels", [])) == len(feature_payload["rowLabels"])
    assert feature_payload.get("clusterCounts")

    assert pca_png.exists()
    assert pca_png.stat().st_size > 0
    assert pca_meta.exists()
    assert pca_payload["componentLabels"] == ["PC1", "PC2"]
    assert len(pca_payload.get("clusterLabels", [])) == len(pca_payload["rowLabels"])
    assert pca_payload.get("clusterCounts")
    assert query_png.exists()
    assert query_png.stat().st_size > 0
    assert query_meta.exists()
    assert query_payload["queryFeatureNames"]
    assert len(query_payload["scores"]) == len(query_payload["rowLabels"])
