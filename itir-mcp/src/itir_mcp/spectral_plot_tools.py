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


def render_hierarchical_spectral_manifold(
    hierarchy: Mapping[str, Any],
    output_path: str | Path,
) -> dict[str, Any]:
    rows = hierarchy.get("conversation_rows")
    if not isinstance(rows, Sequence) or isinstance(rows, (str, bytes, bytearray)) or not rows:
        raise ValueError("hierarchy requires conversation_rows")
    path = _output_path(output_path)
    plt = _pyplot()

    parsed: list[dict[str, Any]] = []
    for index, row in enumerate(rows):
        if not isinstance(row, Mapping):
            raise ValueError("conversation_rows entries must be objects")
        xy = row.get("xy")
        if not isinstance(xy, Sequence) or isinstance(xy, (str, bytes, bytearray)) or len(xy) < 2:
            raise ValueError(f"conversation row {index} requires xy coordinates")
        parsed.append(
            {
                "conversation_id": str(row.get("conversation_id") or f"row:{index}"),
                "x": float(xy[0]),
                "y": float(xy[1]),
                "primary_id": str(row.get("primary_id") or "primary-unknown"),
                "subtopic_id": str(row.get("subtopic_id") or "subtopic-unknown"),
                "alpha": max(0.0, float(row.get("alpha", 0.0))),
            }
        )

    primary_ids = sorted({row["primary_id"] for row in parsed})
    primary_index = {topic_id: index for index, topic_id in enumerate(primary_ids)}
    x = [row["x"] for row in parsed]
    y = [row["y"] for row in parsed]
    colors = [primary_index[row["primary_id"]] for row in parsed]
    alpha_values = [row["alpha"] for row in parsed]
    max_alpha = max(alpha_values, default=1.0) or 1.0
    sizes = [18.0 + 110.0 * (value / max_alpha) ** 0.5 for value in alpha_values]

    figure, axis = plt.subplots(figsize=(11, 8))
    scatter = axis.scatter(x, y, c=colors, s=sizes, alpha=0.78)
    axis.set_xlabel("Spectral Eigen 0")
    axis.set_ylabel("Spectral Eigen 1")
    axis.set_title(f"PNF conversation manifold ({len(parsed)} conversations)")
    axis.grid(True, alpha=0.2)

    subtopic_rows: dict[str, list[tuple[float, float]]] = {}
    for row in parsed:
        subtopic_rows.setdefault(row["subtopic_id"], []).append((row["x"], row["y"]))
    hull_count = 0
    for subtopic_id in sorted(subtopic_rows):
        points = subtopic_rows[subtopic_id]
        if len(points) < 3:
            continue
        hull = _convex_hull(points)
        if len(hull) < 3:
            continue
        closed = hull + [hull[0]]
        axis.plot(
            [point[0] for point in closed],
            [point[1] for point in closed],
            linewidth=0.7,
            alpha=0.35,
        )
        hull_count += 1

    if len(primary_ids) <= 20 and len(primary_ids) > 1:
        handles, _ = scatter.legend_elements(num=len(primary_ids))
        axis.legend(handles, primary_ids, title="Primary topic", loc="best", fontsize=7)

    mp = hierarchy.get("marchenko_pastur")
    if isinstance(mp, Mapping):
        lambda_plus = mp.get("lambda_plus")
        macro_count = mp.get("macro_mode_count")
        if isinstance(lambda_plus, (int, float)) and not isinstance(lambda_plus, bool):
            note = f"MP λ+={float(lambda_plus):.6g}"
            if isinstance(macro_count, int):
                note += f" · macro modes={macro_count}"
            axis.text(0.01, 0.99, note, transform=axis.transAxes, va="top", ha="left", fontsize=9)

    figure.tight_layout()
    figure.savefig(path)
    plt.close(figure)
    return {
        "version": VERSION,
        "artifact_kind": "hierarchical_spectral_manifold",
        "output_path": str(path),
        "format": path.suffix.lower().lstrip("."),
        "conversation_count": len(parsed),
        "primary_cluster_count": len(primary_ids),
        "subtopic_hull_count": hull_count,
        "candidate_only": True,
        "non_authoritative": True,
    }


def _convex_hull(points: Sequence[tuple[float, float]]) -> list[tuple[float, float]]:
    unique = sorted(set((float(x), float(y)) for x, y in points))
    if len(unique) <= 2:
        return unique

    def cross(
        origin: tuple[float, float],
        left: tuple[float, float],
        right: tuple[float, float],
    ) -> float:
        return (
            (left[0] - origin[0]) * (right[1] - origin[1])
            - (left[1] - origin[1]) * (right[0] - origin[0])
        )

    lower: list[tuple[float, float]] = []
    for point in unique:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], point) <= 0.0:
            lower.pop()
        lower.append(point)

    upper: list[tuple[float, float]] = []
    for point in reversed(unique):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], point) <= 0.0:
            upper.pop()
        upper.append(point)
    return lower[:-1] + upper[:-1]


def _topic_centroid_rows(hierarchy: Mapping[str, Any]) -> tuple[list[str], list[list[float]]]:
    topics = hierarchy.get("primary_topics")
    if not isinstance(topics, Sequence) or isinstance(topics, (str, bytes, bytearray)) or not topics:
        raise ValueError("hierarchy requires primary_topics")
    labels: list[str] = []
    centroids: list[list[float]] = []
    for topic in topics:
        if not isinstance(topic, Mapping):
            raise ValueError("primary topic entries must be objects")
        centroid = topic.get("semantic_centroid")
        if not isinstance(centroid, Mapping):
            raise ValueError("primary topic requires semantic_centroid")
        values = centroid.get("spectral_coordinates")
        if not isinstance(values, Sequence) or isinstance(values, (str, bytes, bytearray)):
            raise ValueError("primary topic centroid requires spectral_coordinates")
        vector = [float(value) for value in values]
        if not vector or any(not math.isfinite(value) for value in vector):
            raise ValueError("primary topic centroid coordinates must be finite")
        labels.append(str(topic.get("name") or topic.get("topic_id") or f"topic:{len(labels)}"))
        centroids.append(vector)
    return labels, centroids


def _pairwise_cosine_matrix(vectors: Sequence[Sequence[float]]) -> list[list[float]]:
    return [[_cosine(left, right) for right in vectors] for left in vectors]


def render_hierarchical_topic_heatmap(
    hierarchy: Mapping[str, Any],
    output_path: str | Path,
) -> dict[str, Any]:
    labels, centroids = _topic_centroid_rows(hierarchy)
    return render_spectral_heatmap(_pairwise_cosine_matrix(centroids), labels, output_path)


def render_hierarchical_topic_dendrogram(
    hierarchy: Mapping[str, Any],
    output_path: str | Path,
) -> dict[str, Any]:
    primary = hierarchy.get("primary_topics")
    subtopics = hierarchy.get("subtopics")
    fibres = hierarchy.get("fibre_cliques")
    if not all(
        isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray))
        for value in (primary, subtopics, fibres)
    ):
        raise ValueError("hierarchy requires primary_topics, subtopics, and fibre_cliques")
    path = _output_path(output_path)
    plt = _pyplot()

    primary_rows = [topic for topic in primary if isinstance(topic, Mapping)]
    sub_rows = [topic for topic in subtopics if isinstance(topic, Mapping)]
    fibre_rows = [topic for topic in fibres if isinstance(topic, Mapping)]

    leaf_order = sorted(
        fibre_rows,
        key=lambda topic: (
            str(topic.get("parent_id") or ""),
            str(topic.get("topic_id") or ""),
        ),
    )
    leaf_x = {
        str(topic.get("topic_id")): float(index)
        for index, topic in enumerate(leaf_order)
    }
    sub_children: dict[str, list[str]] = {}
    for fibre in fibre_rows:
        sub_children.setdefault(str(fibre.get("parent_id") or ""), []).append(str(fibre.get("topic_id") or ""))
    primary_children: dict[str, list[str]] = {}
    for subtopic in sub_rows:
        primary_children.setdefault(str(subtopic.get("parent_id") or ""), []).append(str(subtopic.get("topic_id") or ""))

    sub_x: dict[str, float] = {}
    for subtopic in sub_rows:
        sub_id = str(subtopic.get("topic_id") or "")
        children = [leaf_x[child] for child in sub_children.get(sub_id, []) if child in leaf_x]
        if children:
            sub_x[sub_id] = sum(children) / len(children)

    primary_x: dict[str, float] = {}
    for topic in primary_rows:
        topic_id = str(topic.get("topic_id") or "")
        children = [sub_x[child] for child in primary_children.get(topic_id, []) if child in sub_x]
        if children:
            primary_x[topic_id] = sum(children) / len(children)

    thresholds = hierarchy.get("thresholds")
    threshold_map = thresholds if isinstance(thresholds, Mapping) else {}
    fibre_y = float(threshold_map.get("fibre_tau", 0.0))
    sub_y = float(threshold_map.get("subtopic_tau", fibre_y + 1.0))
    primary_y = float(threshold_map.get("primary_tau", sub_y + 1.0))

    figure, axis = plt.subplots(figsize=(max(10.0, len(leaf_order) / 6.0), 7))
    for sub_id, children in sorted(sub_children.items()):
        xs = [leaf_x[child] for child in children if child in leaf_x]
        if not xs or sub_id not in sub_x:
            continue
        for x_value in xs:
            axis.plot([x_value, x_value, sub_x[sub_id]], [0.0, fibre_y, sub_y], linewidth=0.7)
    for primary_id, children in sorted(primary_children.items()):
        xs = [sub_x[child] for child in children if child in sub_x]
        if not xs or primary_id not in primary_x:
            continue
        for x_value in xs:
            axis.plot([x_value, x_value, primary_x[primary_id]], [sub_y, sub_y, primary_y], linewidth=0.9)

    axis.set_ylabel("Spectral quotient threshold τ")
    axis.set_xlabel("Dynamically discovered fibre leaves")
    axis.set_title("PNF hierarchical quotient dendrogram")
    if len(leaf_order) <= 80:
        axis.set_xticks(
            [leaf_x[str(topic.get("topic_id"))] for topic in leaf_order],
            labels=[str(topic.get("name") or topic.get("topic_id")) for topic in leaf_order],
            rotation=90,
            fontsize=5,
        )
    else:
        axis.set_xticks([])
    figure.tight_layout()
    figure.savefig(path)
    plt.close(figure)
    return {
        "version": VERSION,
        "artifact_kind": "hierarchical_topic_dendrogram",
        "output_path": str(path),
        "format": path.suffix.lower().lstrip("."),
        "primary_topic_count": len(primary_rows),
        "subtopic_count": len(sub_rows),
        "fibre_count": len(fibre_rows),
        "candidate_only": True,
        "non_authoritative": True,
    }


def generate_hierarchical_corpus_visualizations(
    hierarchy: Mapping[str, Any],
    output_dir: str | Path,
) -> dict[str, Any]:
    target = Path(output_dir).expanduser().resolve()
    target.mkdir(parents=True, exist_ok=True)
    artifacts = [
        render_hierarchical_spectral_manifold(hierarchy, target / "fleet_manifold.png"),
        render_hierarchical_spectral_manifold(hierarchy, target / "fleet_manifold.svg"),
        render_hierarchical_topic_heatmap(hierarchy, target / "fleet_topic_heatmap.png"),
        render_hierarchical_topic_heatmap(hierarchy, target / "fleet_topic_heatmap.svg"),
        render_hierarchical_topic_dendrogram(hierarchy, target / "fleet_topic_dendrogram.png"),
        render_hierarchical_topic_dendrogram(hierarchy, target / "fleet_topic_dendrogram.svg"),
    ]
    return {
        "version": VERSION,
        "conversation_count": len(hierarchy.get("conversation_rows") or ()),
        "artifacts": artifacts,
        "candidate_only": True,
        "non_authoritative": True,
        "canonical_truth_mutated": False,
    }
