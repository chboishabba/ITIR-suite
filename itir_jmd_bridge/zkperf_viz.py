from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

_REGISTER_NAMES = ["AX", "BX", "CX", "DX", "SI", "DI", "R8", "R9", "R10", "R11", "R12", "R13", "R14", "R15"]
_FINGERPRINT_CODES = {"C": 0.0, "L": 1.0, "M": 2.0, "H": 3.0}
_HEX_RE = re.compile(r"^0x[0-9a-fA-F]+$")
_FLOW_RE = re.compile(
    r"^(?P<name>[A-Za-z0-9_?]+):(?:(?P<old>0x[0-9a-fA-F]+)→(?P<new>0x[0-9a-fA-F]+)|=(?P<assign>0x[0-9a-fA-F]+))$"
)


def load_zkperf_stream_fixture(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("zkperf stream fixture must be a JSON object")
    return payload


def project_zkperf_observation_metrics(observation: dict[str, Any]) -> dict[str, float]:
    values: dict[str, float] = {}
    _merge_explicit_metrics(observation, values)
    _merge_register_values(observation, values)
    _merge_register_fingerprints(observation, values)
    _merge_register_changes(observation, values)
    _merge_flow_tags(observation, values)
    _merge_flow_regions(observation, values)
    _merge_flow_transitions(observation, values)
    return values


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
    return project_zkperf_observation_metrics(observation)


def _merge_explicit_metrics(observation: dict[str, Any], values: dict[str, float]) -> None:
    metrics = observation.get("metrics")
    if not isinstance(metrics, list):
        return
    for row in metrics:
        if not isinstance(row, dict):
            continue
        name = row.get("metric") or row.get("name")
        value = row.get("value")
        if isinstance(name, str) and isinstance(value, (int, float)):
            values[name] = float(value)


def _merge_register_values(observation: dict[str, Any], values: dict[str, float]) -> None:
    for key in ("registers", "regs", "registerValues", "register_values"):
        payload = observation.get(key)
        if isinstance(payload, dict):
            for name, raw in payload.items():
                register = _normalize_register_name(name)
                number = _coerce_number(raw)
                if register and number is not None:
                    values[f"reg.{register}.value"] = number
        elif isinstance(payload, list):
            for row in payload:
                if not isinstance(row, dict):
                    continue
                register = _normalize_register_name(
                    row.get("register") or row.get("reg") or row.get("name") or row.get("registerName")
                )
                number = _coerce_number(row.get("value"))
                if register and number is not None:
                    values[f"reg.{register}.value"] = number


def _merge_register_fingerprints(observation: dict[str, Any], values: dict[str, float]) -> None:
    for key in ("registerFingerprints", "register_fingerprints", "fingerprints", "registerPatterns"):
        payload = observation.get(key)
        if isinstance(payload, dict):
            for name, raw in payload.items():
                register = _normalize_register_name(name)
                code = _coerce_fingerprint_code(raw)
                if register and code is not None:
                    values[f"reg.{register}.fingerprint_code"] = code
        elif isinstance(payload, list):
            for row in payload:
                if not isinstance(row, dict):
                    continue
                register = _normalize_register_name(
                    row.get("register") or row.get("reg") or row.get("name") or row.get("registerName")
                )
                code = _coerce_fingerprint_code(
                    row.get("fingerprint") or row.get("variance") or row.get("class") or row.get("tag")
                )
                if register and code is not None:
                    values[f"reg.{register}.fingerprint_code"] = code
    overall = observation.get("fingerprint")
    if isinstance(overall, str):
        register_order = observation.get("registerOrder")
        if isinstance(register_order, list) and register_order:
            names = [_normalize_register_name(item) or "" for item in register_order]
        else:
            names = _REGISTER_NAMES
        for register, raw in zip(names, overall):
            code = _coerce_fingerprint_code(raw)
            if register and code is not None:
                values[f"reg.{register}.fingerprint_code"] = code


def _merge_register_changes(observation: dict[str, Any], values: dict[str, float]) -> None:
    for key in (
        "registerChanges",
        "register_changes",
        "changedRegisters",
        "changed_registers",
        "registerFlows",
        "register_flows",
        "flows",
    ):
        payload = observation.get(key)
        if not isinstance(payload, list):
            continue
        for row in payload:
            _merge_one_register_change(row, values)


def _merge_one_register_change(row: Any, values: dict[str, float]) -> None:
    if isinstance(row, str):
        parsed = _FLOW_RE.match(row.strip())
        if parsed is None:
            return
        name = parsed.group("name")
        register = _normalize_register_name(name)
        if register == "IP":
            values["flow.transition.ip"] = values.get("flow.transition.ip", 0.0) + 1.0
            delta = _coerce_delta(parsed.group("old"), parsed.group("new"), parsed.group("assign"))
            if delta is not None:
                values["flow.ip.delta"] = delta
            return
        if register is None:
            return
        values[f"reg.{register}.changed"] = 1.0
        delta = _coerce_delta(parsed.group("old"), parsed.group("new"), parsed.group("assign"))
        if delta is not None:
            values[f"reg.{register}.delta"] = delta
        return
    if not isinstance(row, dict):
        return
    register = _normalize_register_name(
        row.get("register") or row.get("reg") or row.get("name") or row.get("registerName")
    )
    old_value = _coerce_number(row.get("old") or row.get("from"))
    new_value = _coerce_number(row.get("new") or row.get("to") or row.get("value"))
    if register == "IP":
        values["flow.transition.ip"] = values.get("flow.transition.ip", 0.0) + 1.0
        if old_value is not None and new_value is not None:
            values["flow.ip.delta"] = new_value - old_value
        return
    if register is None:
        return
    values[f"reg.{register}.changed"] = 1.0
    if old_value is not None and new_value is not None:
        values[f"reg.{register}.delta"] = new_value - old_value
    elif new_value is not None:
        values.setdefault(f"reg.{register}.value", new_value)


def _merge_flow_tags(observation: dict[str, Any], values: dict[str, float]) -> None:
    for key in ("flowTags", "flow_tags", "tags"):
        payload = observation.get(key)
        if isinstance(payload, str):
            items = [item.strip() for item in payload.split(",") if item.strip()]
        elif isinstance(payload, list):
            items = []
            for item in payload:
                if isinstance(item, str):
                    items.append(item.strip())
        else:
            continue
        for tag in items:
            token = _sanitize_feature_token(tag)
            if token:
                values[f"flow.tag.{token}"] = values.get(f"flow.tag.{token}", 0.0) + 1.0


def _merge_flow_regions(observation: dict[str, Any], values: dict[str, float]) -> None:
    for key in ("region", "regionId", "region_id", "subRegion", "sub_region", "blockRegion", "ipRegion"):
        token = _sanitize_feature_token(observation.get(key))
        if token:
            values[f"flow.region.{token}"] = 1.0


def _merge_flow_transitions(observation: dict[str, Any], values: dict[str, float]) -> None:
    for key in ("transition", "ipTransition", "ip_transition"):
        payload = observation.get(key)
        if isinstance(payload, str):
            token = _sanitize_feature_token(payload)
            if token:
                values[f"flow.transition.{token}"] = 1.0
    pairs = [
        ("fromRegion", "toRegion"),
        ("from_region", "to_region"),
        ("sourceRegion", "targetRegion"),
    ]
    for left_key, right_key in pairs:
        left = _sanitize_feature_token(observation.get(left_key))
        right = _sanitize_feature_token(observation.get(right_key))
        if left and right:
            values[f"flow.transition.{left}__{right}"] = 1.0


def _normalize_register_name(value: Any) -> str | None:
    if isinstance(value, int):
        if 0 <= value < len(_REGISTER_NAMES):
            return _REGISTER_NAMES[value]
        return None
    if not isinstance(value, str):
        return None
    token = value.strip().upper()
    if token.startswith("R") and token[1:].isdigit():
        return token
    if token in {"AX", "BX", "CX", "DX", "SI", "DI", "IP"}:
        return token
    return token if token in _REGISTER_NAMES else None


def _coerce_number(value: Any) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        stripped = value.strip()
        if _HEX_RE.match(stripped):
            return float(int(stripped, 16))
        try:
            return float(stripped)
        except ValueError:
            return None
    return None


def _coerce_delta(old_raw: str | None, new_raw: str | None, assign_raw: str | None) -> float | None:
    if assign_raw is not None:
        assigned = _coerce_number(assign_raw)
        return assigned if assigned is not None else None
    old_value = _coerce_number(old_raw)
    new_value = _coerce_number(new_raw)
    if old_value is None or new_value is None:
        return None
    return new_value - old_value


def _coerce_fingerprint_code(value: Any) -> float | None:
    if isinstance(value, str):
        token = value.strip().upper()
        if token in _FINGERPRINT_CODES:
            return _FINGERPRINT_CODES[token]
    if isinstance(value, (int, float)):
        return float(value)
    return None


def _sanitize_feature_token(value: Any) -> str | None:
    if value is None:
        return None
    token = str(value).strip()
    if not token:
        return None
    token = re.sub(r"[^A-Za-z0-9_]+", "_", token).strip("_")
    return token or None


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
