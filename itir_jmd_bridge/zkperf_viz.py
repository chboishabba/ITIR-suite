from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def load_zkperf_stream_fixture(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("zkperf stream fixture must be a JSON object")
    return payload


def build_zkperf_feature_spectrogram_payload(
    fixture: dict[str, Any],
    *,
    top_k_features: int = 32,
    feature_prefixes: list[str] | None = None,
) -> dict[str, Any]:
    observations = _flatten_stream_observations(fixture)
    if not observations:
        raise ValueError("zkperf stream fixture contains no observations")
    feature_names = _select_feature_names(
        observations,
        top_k_features=top_k_features,
        feature_prefixes=feature_prefixes,
    )
    matrix = _build_feature_matrix(observations, feature_names)
    return {
        "streamId": fixture.get("streamId"),
        "streamRevision": fixture.get("streamRevision"),
        "featureNames": feature_names,
        "rowLabels": [row["rowLabel"] for row in observations],
        "matrix": matrix.tolist(),
    }


def render_zkperf_feature_spectrogram(
    fixture: dict[str, Any],
    *,
    output_path: str | Path,
    metadata_path: str | Path | None = None,
    top_k_features: int = 32,
    feature_prefixes: list[str] | None = None,
    cluster_k: int | None = None,
) -> dict[str, Any]:
    payload = build_zkperf_feature_spectrogram_payload(
        fixture,
        top_k_features=top_k_features,
        feature_prefixes=feature_prefixes,
    )
    matrix = np.asarray(payload["matrix"], dtype=float)
    cluster_labels = _cluster_rows(matrix, cluster_k) if cluster_k else None
    _render_heatmap(
        matrix,
        x_labels=payload["featureNames"],
        y_labels=payload["rowLabels"],
        title=f"ZKPerf Feature Spectrogram: {payload['streamId']}",
        output_path=output_path,
    )
    result = {
        "kind": "zkperf_feature_spectrogram",
        "streamId": payload["streamId"],
        "streamRevision": payload["streamRevision"],
        "outputPath": str(Path(output_path).resolve()),
        "featureCount": len(payload["featureNames"]),
        "rowCount": len(payload["rowLabels"]),
        "featureNames": payload["featureNames"],
        "rowLabels": payload["rowLabels"],
    }
    if cluster_labels is not None:
        result["clusterLabels"] = cluster_labels
        result["clusterCounts"] = _cluster_counts(cluster_labels)
    if metadata_path is not None:
        Path(metadata_path).write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        result["metadataPath"] = str(Path(metadata_path).resolve())
    return result


def render_zkperf_pca_spectrogram(
    fixture: dict[str, Any],
    *,
    output_path: str | Path,
    metadata_path: str | Path | None = None,
    top_k_features: int = 32,
    components: int = 8,
    feature_prefixes: list[str] | None = None,
    cluster_k: int | None = None,
) -> dict[str, Any]:
    base = build_zkperf_feature_spectrogram_payload(
        fixture,
        top_k_features=top_k_features,
        feature_prefixes=feature_prefixes,
    )
    feature_matrix = np.asarray(base["matrix"], dtype=float)
    centered = feature_matrix - feature_matrix.mean(axis=0, keepdims=True)
    rank = max(1, min(components, centered.shape[0], centered.shape[1]))
    if centered.shape[0] == 1 or np.allclose(centered, 0.0):
        projected = np.zeros((centered.shape[0], rank), dtype=float)
        explained = np.zeros(rank, dtype=float)
    else:
        _, singular_values, vh = np.linalg.svd(centered, full_matrices=False)
        projected = centered @ vh[:rank].T
        variance = singular_values**2
        explained = variance[:rank] / variance.sum() if variance.sum() > 0 else np.zeros(rank, dtype=float)

    component_labels = [f"PC{i + 1}" for i in range(projected.shape[1])]
    cluster_labels = _cluster_rows(projected, cluster_k) if cluster_k else None
    _render_heatmap(
        projected,
        x_labels=component_labels,
        y_labels=base["rowLabels"],
        title=f"ZKPerf PCA Spectrogram: {base['streamId']}",
        output_path=output_path,
    )
    result = {
        "kind": "zkperf_pca_spectrogram",
        "streamId": base["streamId"],
        "streamRevision": base["streamRevision"],
        "outputPath": str(Path(output_path).resolve()),
        "componentLabels": component_labels,
        "explainedVarianceRatio": [round(float(x), 6) for x in explained.tolist()],
        "rowLabels": base["rowLabels"],
        "sourceFeatureNames": base["featureNames"],
    }
    if cluster_labels is not None:
        result["clusterLabels"] = cluster_labels
        result["clusterCounts"] = _cluster_counts(cluster_labels)
    if metadata_path is not None:
        Path(metadata_path).write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        result["metadataPath"] = str(Path(metadata_path).resolve())
    return result


def render_zkperf_query_spectrogram(
    fixture: dict[str, Any],
    *,
    output_path: str | Path,
    metadata_path: str | Path | None = None,
    query_metrics: dict[str, float] | None = None,
    query_observation: dict[str, Any] | None = None,
    feature_prefixes: list[str] | None = None,
) -> dict[str, Any]:
    observations = _flatten_stream_observations(fixture)
    if not observations:
        raise ValueError("zkperf stream fixture contains no observations")

    query_vector = _build_query_vector(query_metrics, query_observation)
    feature_names = _select_query_features(observations, query_vector, feature_prefixes)
    matrix = _build_feature_matrix(observations, feature_names)
    query_array = np.array([query_vector[name] for name in feature_names], dtype=float)
    alignment = matrix @ query_array.reshape(-1, 1)

    _render_heatmap(
        alignment,
        x_labels=["query_alignment"],
        y_labels=[row["rowLabel"] for row in observations],
        title=f"ZKPerf Query Spectrogram: {fixture.get('streamId')}",
        output_path=output_path,
    )

    result = {
        "kind": "zkperf_query_spectrogram",
        "streamId": fixture.get("streamId"),
        "streamRevision": fixture.get("streamRevision"),
        "outputPath": str(Path(output_path).resolve()),
        "rowLabels": [row["rowLabel"] for row in observations],
        "queryFeatureNames": feature_names,
        "scores": [float(x) for x in alignment.reshape(-1).tolist()],
    }
    if metadata_path is not None:
        Path(metadata_path).write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        result["metadataPath"] = str(Path(metadata_path).resolve())
    return result


def _flatten_stream_observations(fixture: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    windows = fixture.get("windows")
    if not isinstance(windows, list):
        return rows
    for window_index, window in enumerate(windows, start=1):
        if not isinstance(window, dict):
            continue
        payload = window.get("payload")
        observations = payload.get("observations") if isinstance(payload, dict) else None
        if not isinstance(observations, list):
            continue
        window_id = str(window.get("windowId") or f"window-{window_index:04d}")
        sequence = int(window.get("sequence") or window_index)
        for observation_index, observation in enumerate(observations, start=1):
            if not isinstance(observation, dict):
                continue
            rows.append(
                {
                    "windowId": window_id,
                    "sequence": sequence,
                    "observationIndex": observation_index,
                    "rowLabel": f"{sequence:04d}:{window_id}:{observation_index}",
                    "metrics": _metric_map(observation),
                }
            )
    rows.sort(key=lambda row: (row["sequence"], row["observationIndex"]))
    return rows


def _metric_map(observation: dict[str, Any]) -> dict[str, float]:
    values: dict[str, float] = {}
    metrics = observation.get("metrics")
    if not isinstance(metrics, list):
        return values
    for row in metrics:
        if not isinstance(row, dict):
            continue
        name = row.get("metric") or row.get("name")
        value = row.get("value")
        if isinstance(name, str) and isinstance(value, (int, float)):
            values[name] = float(value)
    return values


def _select_feature_names(
    observations: list[dict[str, Any]],
    *,
    top_k_features: int,
    feature_prefixes: list[str] | None,
) -> list[str]:
    candidate_names: set[str] = set()
    for row in observations:
        candidate_names.update(row["metrics"].keys())
    names = sorted(candidate_names)
    if feature_prefixes:
        names = [
            name for name in names if any(name == prefix or name.startswith(f"{prefix}.") for prefix in feature_prefixes)
        ]
    if not names:
        raise ValueError("no metrics matched the requested feature selection")
    matrix = _build_feature_matrix(observations, names)
    variances = np.var(matrix, axis=0)
    scores = []
    for idx, name in enumerate(names):
        nonzero = float(np.count_nonzero(matrix[:, idx]))
        scores.append((float(variances[idx]), nonzero, name))
    scores.sort(key=lambda item: (item[0], item[1], item[2]), reverse=True)
    return [name for _, _, name in scores[: max(1, min(top_k_features, len(scores)))]]


def _select_query_features(
    observations: list[dict[str, Any]],
    query_vector: dict[str, float],
    feature_prefixes: list[str] | None,
) -> list[str]:
    candidate_names: set[str] = set(query_vector.keys())
    for row in observations:
        candidate_names &= set(row["metrics"].keys())
    names = sorted(candidate_names)
    if feature_prefixes:
        names = [
            name for name in names if any(name == prefix or name.startswith(f"{prefix}.") for prefix in feature_prefixes)
        ]
    if not names:
        raise ValueError("no overlapping metrics between query and observations for query spectrogram")
    return names


def _build_feature_matrix(observations: list[dict[str, Any]], feature_names: list[str]) -> np.ndarray:
    matrix = np.zeros((len(observations), len(feature_names)), dtype=float)
    for row_idx, row in enumerate(observations):
        for col_idx, name in enumerate(feature_names):
            matrix[row_idx, col_idx] = float(row["metrics"].get(name, 0.0))
    transformed = np.log1p(np.abs(matrix))
    return transformed


def _build_query_vector(
    query_metrics: dict[str, float] | None,
    query_observation: dict[str, Any] | None,
) -> dict[str, float]:
    if query_metrics is None and query_observation is None:
        raise ValueError("provide query_metrics or query_observation for query spectrogram")
    metrics: dict[str, float] = {}
    if query_metrics:
        for key, value in query_metrics.items():
            if isinstance(value, (int, float)):
                metrics[str(key)] = float(value)
    if query_observation:
        metrics.update(_metric_map(query_observation))
    if not metrics:
        raise ValueError("query vector is empty after filtering non-numeric values")
    return {key: float(np.log1p(abs(val))) for key, val in metrics.items()}


def _render_heatmap(
    matrix: np.ndarray,
    *,
    x_labels: list[str],
    y_labels: list[str],
    title: str,
    output_path: str | Path,
) -> None:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    fig_width = max(8, min(18, 0.35 * max(1, len(x_labels))))
    fig_height = max(4, min(18, 0.35 * max(1, len(y_labels))))
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    image = ax.imshow(matrix, aspect="auto", cmap="turbo", origin="upper")
    ax.set_title(title)
    ax.set_xlabel("Structured features / spectral components")
    ax.set_ylabel("Trace steps / windows")
    ax.set_xticks(range(len(x_labels)))
    ax.set_xticklabels(x_labels, rotation=90, fontsize=8)
    ax.set_yticks(range(len(y_labels)))
    ax.set_yticklabels(y_labels, fontsize=8)
    fig.colorbar(image, ax=ax, label="log1p(|activation|)")
    fig.tight_layout()
    fig.savefig(output, dpi=180)
    plt.close(fig)


def _cluster_rows(matrix: np.ndarray, k: int | None) -> list[int] | None:
    if k is None or k <= 1:
        return None
    rows = matrix.shape[0]
    k = min(k, rows)
    if rows == 0 or k == 0:
        return None
    # deterministic initialization: first k rows
    centers = matrix[:k].copy()
    labels = np.zeros(rows, dtype=int)
    for _ in range(20):
        distances = ((matrix[:, None, :] - centers[None, :, :]) ** 2).sum(axis=2)
        new_labels = distances.argmin(axis=1)
        if np.array_equal(new_labels, labels):
            break
        labels = new_labels
        for idx in range(k):
            mask = labels == idx
            if not np.any(mask):
                continue
            centers[idx] = matrix[mask].mean(axis=0)
    return labels.tolist()


def _cluster_counts(labels: list[int]) -> dict[int, int]:
    counts: dict[int, int] = {}
    for label in labels:
        counts[label] = counts.get(label, 0) + 1
    return counts
