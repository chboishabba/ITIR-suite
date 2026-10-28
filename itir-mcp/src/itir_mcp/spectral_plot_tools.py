from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from .contracts import JsonDict, ToolHandler, ToolInputError, ToolSpec


VERSION = "itir.spectral.visualization.v1"


def _pyplot():
    import matplotlib

    matplotlib.use("Agg", force=True)
    import matplotlib.pyplot as plt

    return plt


def _output_path(value: str | Path) -> Path:
    path = Path(value).expanduser().resolve()
    if path.suffix.lower() not in {".png", ".svg"}:
        raise ValueError("spectral plot output must use .png or .svg")
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _point_rows(coordinates: Any) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    metadata: dict[str, Any] = {}
    rows = coordinates
    if isinstance(coordinates, Mapping):
        metadata = dict(coordinates)
        rows = coordinates.get("points")
        if rows is None:
            rows = coordinates.get("coordinates")
    if not isinstance(rows, Sequence) or isinstance(rows, (str, bytes, bytearray)):
        raise ValueError("coordinates must be an array or an object with points/coordinates")

    points: list[dict[str, Any]] = []
    for index, raw in enumerate(rows):
        if not isinstance(raw, Mapping):
            raise ValueError("coordinate rows must be objects")
        values = raw.get("coordinates")
        if values is None:
            values = raw.get("values")
        if values is None and "x" in raw and "y" in raw:
            values = [raw["x"], raw["y"]]
        if not isinstance(values, Sequence) or isinstance(values, (str, bytes, bytearray)):
            raise ValueError(f"coordinate row {index} requires a numeric coordinate array")
        numeric = [float(value) for value in values]
        if len(numeric) < 2 or any(not math.isfinite(value) for value in numeric):
            raise ValueError(f"coordinate row {index} requires at least two finite coordinates")
        entity_ref = str(
            raw.get("entity_ref")
            or raw.get("object_id")
            or raw.get("id")
            or raw.get("label")
            or f"row:{index}"
        )
        cluster = str(raw.get("cluster") or raw.get("cluster_ref") or "unclustered")
        points.append(
            {
                "entity_ref": entity_ref,
                "coordinates": numeric,
                "cluster": cluster,
            }
        )
    if not points:
        raise ValueError("coordinates must not be empty")
    return points, metadata


def render_spectral_scatter(coordinates: Any, output_path: str | Path) -> dict[str, Any]:
    points, metadata = _point_rows(coordinates)
    path = _output_path(output_path)
    plt = _pyplot()

    cluster_names = sorted({str(point["cluster"]) for point in points})
    cluster_ids = {name: index for index, name in enumerate(cluster_names)}
    x = [float(point["coordinates"][0]) for point in points]
    y = [float(point["coordinates"][1]) for point in points]
    c = [cluster_ids[str(point["cluster"])] for point in points]

    figure, axis = plt.subplots(figsize=(9, 7))
    scatter = axis.scatter(x, y, c=c, s=18, alpha=0.8)
    axis.set_xlabel(_axis_label(0, metadata))
    axis.set_ylabel(_axis_label(1, metadata))
    axis.set_title("PNF spectral coordinates: Eigen 0 vs Eigen 1")
    axis.grid(True, alpha=0.2)

    mp_threshold = metadata.get("mp_threshold")
    if isinstance(mp_threshold, (int, float)) and not isinstance(mp_threshold, bool):
        threshold = float(mp_threshold)
        if math.isfinite(threshold):
            eigenvalues = metadata.get("eigenvalues")
            retained = None
            if isinstance(eigenvalues, Sequence) and not isinstance(eigenvalues, (str, bytes, bytearray)):
                finite_values = [
                    float(value)
                    for value in eigenvalues
                    if isinstance(value, (int, float))
                    and not isinstance(value, bool)
                    and math.isfinite(float(value))
                ]
                retained = sum(value > threshold for value in finite_values)
            note = f"MP upper edge λ+ = {threshold:.6g}"
            if retained is not None:
                note += f" · retained modes = {retained}"
            axis.text(
                0.01,
                0.99,
                note,
                transform=axis.transAxes,
                va="top",
                ha="left",
                fontsize=9,
            )

    if len(cluster_names) <= 16 and len(cluster_names) > 1:
        handles, _ = scatter.legend_elements(num=len(cluster_names))
        axis.legend(handles, cluster_names, title="Cluster", loc="best", fontsize=8)

    figure.tight_layout()
    figure.savefig(path)
    plt.close(figure)
    return {
        "version": VERSION,
        "artifact_kind": "spectral_scatter",
        "output_path": str(path),
        "format": path.suffix.lower().lstrip("."),
        "point_count": len(points),
        "cluster_count": len(cluster_names),
        "candidate_only": True,
        "non_authoritative": True,
    }


def _axis_label(index: int, metadata: Mapping[str, Any]) -> str:
    eigenvalues = metadata.get("eigenvalues")
    mp_threshold = metadata.get("mp_threshold")
    label = f"Eigen {index}"
    if (
        isinstance(eigenvalues, Sequence)
        and not isinstance(eigenvalues, (str, bytes, bytearray))
        and index < len(eigenvalues)
        and isinstance(eigenvalues[index], (int, float))
        and not isinstance(eigenvalues[index], bool)
    ):
        value = float(eigenvalues[index])
        label += f" (λ={value:.6g}"
        if isinstance(mp_threshold, (int, float)) and not isinstance(mp_threshold, bool):
            label += ", macro" if value > float(mp_threshold) else ", MP bulk"
        label += ")"
    return label


def render_spectral_heatmap(
    similarity_matrix: Sequence[Sequence[float]],
    domain_labels: Sequence[str],
    output_path: str | Path,
) -> dict[str, Any]:
    matrix = _square_matrix(similarity_matrix)
    labels = [str(label) for label in domain_labels]
    if len(labels) != len(matrix):
        raise ValueError("domain_labels length must match similarity matrix size")
    path = _output_path(output_path)
    plt = _pyplot()

    side = min(18.0, max(6.0, 5.0 + len(matrix) / 80.0))
    figure, axis = plt.subplots(figsize=(side, side))
    image = axis.imshow(matrix, vmin=-1.0, vmax=1.0, aspect="auto")
    axis.set_title("PNF pairwise cosine similarity")
    figure.colorbar(image, ax=axis, fraction=0.046, pad=0.04)

    if len(labels) <= 64:
        ticks = list(range(len(labels)))
        axis.set_xticks(ticks, labels=labels, rotation=90, fontsize=6)
        axis.set_yticks(ticks, labels=labels, fontsize=6)
    else:
        axis.set_xlabel(f"{len(labels)} corpus/domain rows; labels suppressed for readability")
        axis.set_ylabel("corpus/domain rows")

    figure.tight_layout()
    figure.savefig(path)
    plt.close(figure)
    return {
        "version": VERSION,
        "artifact_kind": "spectral_heatmap",
        "output_path": str(path),
        "format": path.suffix.lower().lstrip("."),
        "matrix_size": len(matrix),
        "candidate_only": True,
        "non_authoritative": True,
    }


def _square_matrix(values: Sequence[Sequence[float]]) -> list[list[float]]:
    if not isinstance(values, Sequence) or isinstance(values, (str, bytes, bytearray)):
        raise ValueError("similarity_matrix must be an array")
    matrix = [[float(value) for value in row] for row in values]
    if not matrix or any(len(row) != len(matrix) for row in matrix):
        raise ValueError("similarity_matrix must be non-empty and square")
    if any(not math.isfinite(value) or value < -1.000000001 or value > 1.000000001 for row in matrix for value in row):
        raise ValueError("similarity_matrix values must be finite cosine values in [-1, 1]")
    return matrix


def _cosine(left: Sequence[float], right: Sequence[float]) -> float:
    if len(left) != len(right):
        raise ValueError("coordinate vectors must have equal length")
    dot = sum(a * b for a, b in zip(left, right, strict=True))
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if left_norm == 0.0 or right_norm == 0.0:
        return 0.0
    return dot / (left_norm * right_norm)


def _similarity_from_points(points: Sequence[Mapping[str, Any]]) -> list[list[float]]:
    vectors = [[float(value) for value in point["coordinates"]] for point in points]
    return [[_cosine(left, right) for right in vectors] for left in vectors]


def generate_corpus_spectral_visualizations(
    coordinates_payload: Mapping[str, Any],
    output_dir: str | Path,
) -> dict[str, Any]:
    if not isinstance(coordinates_payload, Mapping):
        raise ValueError("coordinates_payload must be an object")
    points, metadata = _point_rows(coordinates_payload)
    labels = [str(point["entity_ref"]) for point in points]

    matrix = coordinates_payload.get("similarity_matrix")
    if matrix is None:
        matrix = _similarity_from_points(points)
    similarity = _square_matrix(matrix)

    target = Path(output_dir).expanduser().resolve()
    target.mkdir(parents=True, exist_ok=True)
    scatter_payload = dict(metadata)
    scatter_payload["points"] = points

    artifacts = [
        render_spectral_scatter(scatter_payload, target / "spectral_scatter.png"),
        render_spectral_scatter(scatter_payload, target / "spectral_scatter.svg"),
        render_spectral_heatmap(similarity, labels, target / "spectral_heatmap.png"),
        render_spectral_heatmap(similarity, labels, target / "spectral_heatmap.svg"),
    ]
    return {
        "version": VERSION,
        "point_count": len(points),
        "matrix_size": len(similarity),
        "artifacts": artifacts,
        "candidate_only": True,
        "non_authoritative": True,
        "canonical_truth_mutated": False,
    }


def _require_path(payload: Mapping[str, Any], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ToolInputError(f"{key} must be a non-empty path")
    return value


def render_spectral_scatter_tool(payload: Mapping[str, Any]) -> JsonDict:
    if "coordinates" not in payload:
        raise ToolInputError("coordinates is required")
    return render_spectral_scatter(payload["coordinates"], _require_path(payload, "output_path"))


def render_spectral_heatmap_tool(payload: Mapping[str, Any]) -> JsonDict:
    matrix = payload.get("similarity_matrix")
    labels = payload.get("domain_labels")
    if not isinstance(matrix, Sequence) or isinstance(matrix, (str, bytes, bytearray)):
        raise ToolInputError("similarity_matrix must be an array")
    if not isinstance(labels, Sequence) or isinstance(labels, (str, bytes, bytearray)):
        raise ToolInputError("domain_labels must be an array")
    return render_spectral_heatmap(matrix, labels, _require_path(payload, "output_path"))


def generate_corpus_spectral_visualizations_tool(payload: Mapping[str, Any]) -> JsonDict:
    coordinates = payload.get("coordinates_payload")
    if not isinstance(coordinates, Mapping):
        raise ToolInputError("coordinates_payload must be an object")
    return generate_corpus_spectral_visualizations(coordinates, _require_path(payload, "output_dir"))


def get_spectral_plot_tools() -> list[tuple[ToolSpec, ToolHandler]]:
    return [
        (
            ToolSpec(
                name="itir.spectral.render_scatter",
                title="ITIR spectral scatter renderer",
                description="Render a non-authoritative Eigen-0/Eigen-1 corpus scatter plot from supplied spectral coordinates.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "coordinates": {},
                        "output_path": {"type": "string"},
                    },
                    "required": ["coordinates", "output_path"],
                    "additionalProperties": False,
                },
                response_version=VERSION,
                read_only=False,
            ),
            render_spectral_scatter_tool,
        ),
        (
            ToolSpec(
                name="itir.spectral.render_heatmap",
                title="ITIR spectral heatmap renderer",
                description="Render a non-authoritative pairwise cosine similarity heatmap.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "similarity_matrix": {"type": "array"},
                        "domain_labels": {"type": "array", "items": {"type": "string"}},
                        "output_path": {"type": "string"},
                    },
                    "required": ["similarity_matrix", "domain_labels", "output_path"],
                    "additionalProperties": False,
                },
                response_version=VERSION,
                read_only=False,
            ),
            render_spectral_heatmap_tool,
        ),
        (
            ToolSpec(
                name="itir.spectral.visualize_corpus",
                title="ITIR corpus spectral visualizer",
                description="Render PNG and SVG scatter/heatmap artifacts from a supplied candidate spectral coordinate payload.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "coordinates_payload": {"type": "object"},
                        "output_dir": {"type": "string"},
                    },
                    "required": ["coordinates_payload", "output_dir"],
                    "additionalProperties": False,
                },
                response_version=VERSION,
                read_only=False,
            ),
            generate_corpus_spectral_visualizations_tool,
        ),
    ]
