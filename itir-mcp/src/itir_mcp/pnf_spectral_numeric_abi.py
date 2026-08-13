from __future__ import annotations

import hashlib
import json
from enum import Enum
from typing import Any, Mapping


SCHEMA = "itir.pnf.spectral_numeric_abi.v0_2"

SAME_FIBRE_EDGE = "sameFibreEdge"
EXACT_RESIDUAL_EDGE = "exactResidualEdge"
PARTIAL_RESIDUAL_EDGE = "partialResidualEdge"
NO_TYPED_MEET_EDGE = "noTypedMeetEdge"
COMPATIBLE_JOIN_EDGE = "compatibleJoinEdge"
COMPATIBLE_MEET_EDGE = "compatibleMeetEdge"
SHARED_PROVENANCE_EDGE = "sharedProvenanceEdge"
SHARED_SOURCE_EDGE = "sharedSourceEdge"
SHARED_TIME_EDGE = "sharedTimeEdge"
TEMPORAL_CONTINUATION_EDGE = "temporalContinuationEdge"
CONTRADICTION_EDGE = "contradictionEdge"


class ResidualEdgeKind(str, Enum):
    SAME_FIBRE = SAME_FIBRE_EDGE
    EXACT_RESIDUAL = EXACT_RESIDUAL_EDGE
    PARTIAL_RESIDUAL = PARTIAL_RESIDUAL_EDGE
    NO_TYPED_MEET = NO_TYPED_MEET_EDGE
    COMPATIBLE_JOIN = COMPATIBLE_JOIN_EDGE
    COMPATIBLE_MEET = COMPATIBLE_MEET_EDGE
    SHARED_PROVENANCE = SHARED_PROVENANCE_EDGE
    SHARED_SOURCE = SHARED_SOURCE_EDGE
    SHARED_TIME = SHARED_TIME_EDGE
    TEMPORAL_CONTINUATION = TEMPORAL_CONTINUATION_EDGE
    CONTRADICTION = CONTRADICTION_EDGE


RESIDUAL_EDGE_KIND_VALUES = frozenset(kind.value for kind in ResidualEdgeKind)
STRUCTURAL_CANDIDATE_EDGE_KIND_VALUES = frozenset({NO_TYPED_MEET_EDGE})

EDGE_KIND_WEIGHT_CLASS = {
    SAME_FIBRE_EDGE: "fibreWeight",
    EXACT_RESIDUAL_EDGE: "exactResidualWeight",
    PARTIAL_RESIDUAL_EDGE: "partialResidualWeight",
    NO_TYPED_MEET_EDGE: "noTypedMeetWeight",
    COMPATIBLE_JOIN_EDGE: "compatibleJoinWeight",
    COMPATIBLE_MEET_EDGE: "compatibleMeetWeight",
    SHARED_PROVENANCE_EDGE: "sharedProvenanceWeight",
    SHARED_SOURCE_EDGE: "sharedSourceWeight",
    SHARED_TIME_EDGE: "sharedTimeWeight",
    TEMPORAL_CONTINUATION_EDGE: "temporalContinuationWeight",
    CONTRADICTION_EDGE: "contradictionSignedWeight",
}

EDGE_KIND_ORIGIN_CLASS = {
    SAME_FIBRE_EDGE: "structuralFibreOrigin",
    EXACT_RESIDUAL_EDGE: "structuralFibreOrigin",
    PARTIAL_RESIDUAL_EDGE: "structuralFibreOrigin",
    NO_TYPED_MEET_EDGE: "structuralFibreOrigin",
    COMPATIBLE_JOIN_EDGE: "structuralFibreOrigin",
    COMPATIBLE_MEET_EDGE: "structuralFibreOrigin",
    SHARED_PROVENANCE_EDGE: "evidenceProvenanceTimeOrigin",
    SHARED_SOURCE_EDGE: "evidenceProvenanceTimeOrigin",
    SHARED_TIME_EDGE: "evidenceProvenanceTimeOrigin",
    TEMPORAL_CONTINUATION_EDGE: "temporalTransportOrigin",
    CONTRADICTION_EDGE: "contradictionOrigin",
}

EDGE_KIND_SOURCE_CLASS = {
    SAME_FIBRE_EDGE: "structuralFibreSource",
    EXACT_RESIDUAL_EDGE: "structuralFibreSource",
    PARTIAL_RESIDUAL_EDGE: "structuralFibreSource",
    NO_TYPED_MEET_EDGE: "structuralFibreSource",
    COMPATIBLE_JOIN_EDGE: "structuralFibreSource",
    COMPATIBLE_MEET_EDGE: "structuralFibreSource",
    SHARED_PROVENANCE_EDGE: "evidenceProvenanceTimeSource",
    SHARED_SOURCE_EDGE: "evidenceProvenanceTimeSource",
    SHARED_TIME_EDGE: "evidenceProvenanceTimeSource",
    TEMPORAL_CONTINUATION_EDGE: "temporalTransportSource",
    CONTRADICTION_EDGE: "contradictionSource",
}

RESIDUAL_EDGE_KIND_LEVEL = {
    EXACT_RESIDUAL_EDGE: "exact",
    PARTIAL_RESIDUAL_EDGE: "partial",
    NO_TYPED_MEET_EDGE: "noTypedMeet",
    CONTRADICTION_EDGE: "contradiction",
}

RESIDUAL_LEVEL_MAGNITUDE = {
    "exact": 0.0,
    "partial": 1.0,
    "noTypedMeet": 3.0,
    "contradiction": 9.0,
}

_AUTHORITY_FLAGS = (
    "truth",
    "support",
    "admissibility",
    "runtime",
    "promoted",
    "routing",
    "vector",
)


def validate_spectral_numeric_abi(payload: dict[str, Any]) -> dict[str, Any]:
    if payload.get("schema") != SCHEMA:
        raise ValueError(f"schema must be {SCHEMA}")
    for key in (
        "graph_version",
        "operator_profile",
        "object_registry",
        "row_map",
        "residual_edge_table",
        "adjacency",
        "degree",
        "laplacian",
        "spectral_coordinates",
        "gemv",
        "receipts",
        "rebuild_witness",
        "authority",
        "parity_hash",
    ):
        if key not in payload:
            raise ValueError(f"{key} is required")

    graph_version = _non_empty_str(payload.get("graph_version"), "graph_version")
    operator_profile = _non_empty_str(payload.get("operator_profile"), "operator_profile")
    object_registry = _mapping(payload.get("object_registry"), "object_registry")
    row_map = _row_map(payload.get("row_map"))
    receipts = _receipts(payload.get("receipts"))
    _validate_registry_binding(row_map, object_registry)
    _validate_receipt_coverage(row_map, receipts)

    rows = len(row_map)
    adjacency = _square_matrix(payload.get("adjacency"), "adjacency", rows)
    degree = _vector(payload.get("degree"), "degree", rows)
    laplacian = _square_matrix(payload.get("laplacian"), "laplacian", rows)
    residual_edges = _edge_table(payload.get("residual_edge_table"), rows)
    spectral = _spectral_coordinates(payload.get("spectral_coordinates"), rows)
    gemv = _gemv(payload.get("gemv"), rows)

    validate_rebuild_witness(
        {
            "row_map": row_map,
            "residual_edge_table": residual_edges,
            "adjacency": adjacency,
            "degree": degree,
            "laplacian": laplacian,
            "spectral_coordinates": spectral,
            "rebuild_witness": payload.get("rebuild_witness"),
        }
    )
    validate_authority_gate(payload.get("authority"))
    expected_hash = spectral_parity_hash(payload)
    if payload.get("parity_hash") != expected_hash:
        raise ValueError("stale parity_hash")

    return {
        "schema": SCHEMA,
        "graph_version": graph_version,
        "operator_profile": operator_profile,
        "objects": len(object_registry),
        "rows": rows,
        "spectral_dimensions": len(spectral["phi"][0]["coordinates"]) if rows else 0,
        "probe_rows": len(spectral["psi"].get("probes", [])),
        "edge_kinds": sorted({edge["kind"] for edge in residual_edges}),
        "gemv_rows": len(gemv["A"]),
        "parity_hash": expected_hash,
        "candidate_only": True,
        "diagnostic_only": True,
    }


def spectral_parity_hash(payload: Mapping[str, Any]) -> str:
    canonical = {
        "schema": payload.get("schema"),
        "graph_version": payload.get("graph_version"),
        "operator_profile": payload.get("operator_profile"),
        "object_registry": payload.get("object_registry"),
        "row_map": payload.get("row_map"),
        "residual_edge_table": payload.get("residual_edge_table"),
        "adjacency": payload.get("adjacency"),
        "degree": payload.get("degree"),
        "laplacian": payload.get("laplacian"),
        "spectral_coordinates": payload.get("spectral_coordinates"),
        "gemv": payload.get("gemv"),
        "receipts": payload.get("receipts"),
        "rebuild_witness": payload.get("rebuild_witness"),
        "authority": payload.get("authority"),
    }
    encoded = json.dumps(canonical, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def validate_rebuild_witness(payload: Mapping[str, Any]) -> dict[str, Any]:
    row_map = _row_map(payload.get("row_map"))
    rows = len(row_map)
    edges = _edge_table(payload.get("residual_edge_table"), rows)
    adjacency = _square_matrix(payload.get("adjacency"), "adjacency", rows)
    degree = _vector(payload.get("degree"), "degree", rows)
    laplacian = _square_matrix(payload.get("laplacian"), "laplacian", rows)
    spectral = _spectral_coordinates(payload.get("spectral_coordinates"), rows)
    witness = _mapping(payload.get("rebuild_witness"), "rebuild_witness")
    if witness.get("deterministic_replay") is not True:
        raise ValueError("rebuild_witness.deterministic_replay must be true")

    rebuilt = [[0.0 for _ in range(rows)] for _ in range(rows)]
    for edge in edges:
        source = edge["source_row"]
        target = edge["target_row"]
        weight = edge["weight"]
        rebuilt[source][target] += weight
        if edge["undirected"]:
            rebuilt[target][source] += weight
    _assert_matrix_close(rebuilt, adjacency, "adjacency rebuild mismatch")

    rebuilt_degree = [sum(row) for row in rebuilt]
    _assert_vector_close(rebuilt_degree, degree, "degree rebuild mismatch")

    rebuilt_laplacian = []
    for row_index in range(rows):
        row = []
        for col_index in range(rows):
            value = degree[row_index] if row_index == col_index else 0.0
            row.append(value - rebuilt[row_index][col_index])
        rebuilt_laplacian.append(row)
    _assert_matrix_close(rebuilt_laplacian, laplacian, "laplacian rebuild mismatch")

    row_ids = [row["object_id"] for row in row_map]
    phi_ids = [row["object_id"] for row in spectral["phi"]]
    if phi_ids != row_ids:
        raise ValueError("phi row alignment mismatch")
    for probe in spectral["psi"].get("probes", []):
        if probe["row"] >= rows or probe["object_id"] != row_ids[probe["row"]]:
            raise ValueError("psi row alignment mismatch")

    return {"status": "ok", "rows": rows, "edges": len(edges)}


def validate_authority_gate(authority: Any) -> dict[str, Any]:
    data = _mapping(authority, "authority")
    if data.get("candidate_only") is not True:
        raise ValueError("authority.candidate_only must be true")
    for flag in _AUTHORITY_FLAGS:
        if data.get(flag) is not False:
            raise ValueError(f"authority.{flag} must be false")
    return {"candidate_only": True, "diagnostic_only": True}


def _mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{label} must be an object")
    return dict(value)


def _non_empty_str(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty string")
    return value.strip()


def _vector(value: Any, label: str, length: int | None = None) -> list[float]:
    if not isinstance(value, list):
        raise ValueError(f"{label} must be a list")
    try:
        result = [float(item) for item in value]
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} must contain numeric values") from exc
    if length is not None and len(result) != length:
        raise ValueError(f"{label} length mismatch")
    return result


def _square_matrix(value: Any, label: str, rows: int) -> list[list[float]]:
    if not isinstance(value, list) or len(value) != rows:
        raise ValueError(f"{label} must be a square matrix matching row_map")
    matrix = [_vector(row, f"{label} row", rows) for row in value]
    return matrix


def _row_map(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise ValueError("row_map must be a non-empty list")
    rows = []
    seen: set[int] = set()
    for expected, row in enumerate(value):
        data = _mapping(row, f"row_map[{expected}]")
        index = data.get("row")
        if index != expected or index in seen:
            raise ValueError("row_map rows must be contiguous and ordered")
        seen.add(index)
        data["object_id"] = _non_empty_str(data.get("object_id"), f"row_map[{expected}].object_id")
        receipt_ids = data.get("receipt_ids")
        if not isinstance(receipt_ids, list) or not receipt_ids or not all(isinstance(item, str) and item for item in receipt_ids):
            raise ValueError(f"row_map[{expected}] requires receipt_ids")
        rows.append(data)
    return rows


def _receipts(value: Any) -> dict[str, dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise ValueError("receipts must be a non-empty list")
    receipts: dict[str, dict[str, Any]] = {}
    for index, receipt in enumerate(value):
        data = _mapping(receipt, f"receipts[{index}]")
        receipt_id = _non_empty_str(data.get("receipt_id"), f"receipts[{index}].receipt_id")
        receipts[receipt_id] = data
    return receipts


def _validate_receipt_coverage(row_map: list[dict[str, Any]], receipts: Mapping[str, Any]) -> None:
    for index, row in enumerate(row_map):
        for receipt_id in row["receipt_ids"]:
            if receipt_id not in receipts:
                raise ValueError(f"missing receipt coverage for row_map[{index}]")


def _validate_registry_binding(row_map: list[dict[str, Any]], object_registry: Mapping[str, Any]) -> None:
    for index, row in enumerate(row_map):
        if row["object_id"] not in object_registry:
            raise ValueError(f"missing object_registry binding for row_map[{index}]")


def _edge_table(value: Any, rows: int) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise ValueError("residual_edge_table must be a list")
    edges = []
    for index, edge in enumerate(value):
        data = _mapping(edge, f"residual_edge_table[{index}]")
        kind = _edge_kind(data, index)
        source = data.get("source_row")
        target = data.get("target_row")
        if not isinstance(source, int) or not isinstance(target, int) or source < 0 or target < 0 or source >= rows or target >= rows:
            raise ValueError("bad edge index")
        _validate_edge_class(data, kind, "weight_class", EDGE_KIND_WEIGHT_CLASS)
        _validate_edge_class(data, kind, "origin_class", EDGE_KIND_ORIGIN_CLASS)
        _validate_edge_class(data, kind, "source_class", EDGE_KIND_SOURCE_CLASS)
        residual_level = _edge_residual_level(data, kind, index)
        weight = _edge_weight(data, kind, residual_level, index)
        edges.append(
            {
                "kind": kind,
                "edge_kind": kind,
                "weight_class": EDGE_KIND_WEIGHT_CLASS[kind],
                "origin_class": EDGE_KIND_ORIGIN_CLASS[kind],
                "source_class": EDGE_KIND_SOURCE_CLASS[kind],
                "residual_level": residual_level,
                "source_row": source,
                "target_row": target,
                "weight": weight,
                "undirected": bool(data.get("undirected", True)),
            }
        )
    return edges


def _validate_edge_class(data: Mapping[str, Any], kind: str, field: str, expected_by_kind: Mapping[str, str]) -> None:
    expected = expected_by_kind[kind]
    actual = data.get(field, expected)
    if actual != expected:
        raise ValueError(f"{field} for {kind} must be {expected}")


def _edge_residual_level(data: Mapping[str, Any], kind: str, index: int) -> str | None:
    expected = RESIDUAL_EDGE_KIND_LEVEL.get(kind)
    raw_level = data.get("residual_level")
    if expected is None:
        if raw_level is None:
            return None
        level = _non_empty_str(raw_level, f"residual_edge_table[{index}].residual_level")
        if level not in RESIDUAL_LEVEL_MAGNITUDE:
            raise ValueError(f"residual_edge_table[{index}].residual_level is unknown")
        return level
    level = _non_empty_str(raw_level, f"residual_edge_table[{index}].residual_level")
    if level != expected:
        raise ValueError(f"residual_edge_table[{index}].residual_level must be {expected}")
    return level


def _edge_weight(data: Mapping[str, Any], kind: str, residual_level: str | None, index: int) -> float:
    signed_weight = data.get("signed_weight")
    if signed_weight is not None:
        signed = _mapping(signed_weight, f"residual_edge_table[{index}].signed_weight")
        sign = _non_empty_str(signed.get("sign"), f"residual_edge_table[{index}].signed_weight.sign")
        try:
            magnitude = float(signed.get("magnitude"))
        except (TypeError, ValueError) as exc:
            raise ValueError(f"residual_edge_table[{index}].signed_weight.magnitude must be numeric") from exc
        if magnitude < 0:
            raise ValueError(f"residual_edge_table[{index}].signed_weight.magnitude must be non-negative")
        if residual_level is not None and abs(magnitude - RESIDUAL_LEVEL_MAGNITUDE[residual_level]) > 1e-9:
            raise ValueError(f"residual_edge_table[{index}].signed_weight.magnitude does not match residual_level")
        if kind == CONTRADICTION_EDGE:
            if sign != "negativeResidualWeight":
                raise ValueError("contradictionEdge signed_weight.sign must be negativeResidualWeight")
            return -magnitude
        if sign != "positiveWeight":
            raise ValueError(f"{kind} signed_weight.sign must be positiveWeight")
        return magnitude

    default_weight = RESIDUAL_LEVEL_MAGNITUDE.get(residual_level or "", -9.0 if kind == CONTRADICTION_EDGE else 1.0)
    try:
        weight = float(data.get("weight", default_weight))
    except (TypeError, ValueError) as exc:
        raise ValueError(f"residual_edge_table[{index}].weight must be numeric") from exc
    if kind == CONTRADICTION_EDGE:
        if weight >= 0:
            raise ValueError("contradictionEdge weight must be negative")
        if abs(abs(weight) - RESIDUAL_LEVEL_MAGNITUDE["contradiction"]) > 1e-9:
            raise ValueError("contradictionEdge magnitude must match contradiction residual severity")
        return weight
    if weight < 0:
        raise ValueError(f"{kind} weight must be non-negative")
    if residual_level is not None and abs(weight - RESIDUAL_LEVEL_MAGNITUDE[residual_level]) > 1e-9:
        raise ValueError(f"residual_edge_table[{index}].weight does not match residual_level")
    return weight


def _edge_kind(edge: Mapping[str, Any], index: int) -> str:
    kind_value = edge.get("kind")
    edge_kind_value = edge.get("edge_kind") if "edge_kind" in edge else None
    if kind_value is None and edge_kind_value is None:
        return NO_TYPED_MEET_EDGE
    if kind_value is None:
        kind_value = edge_kind_value
    if edge_kind_value is not None and kind_value != edge_kind_value:
        raise ValueError(f"residual_edge_table[{index}].kind and edge_kind must match")
    kind = _non_empty_str(kind_value, f"residual_edge_table[{index}].kind")
    if kind not in RESIDUAL_EDGE_KIND_VALUES:
        raise ValueError(f"unknown edge kind: {kind}")
    return kind


def _spectral_coordinates(value: Any, rows: int) -> dict[str, Any]:
    data = _mapping(value, "spectral_coordinates")
    phi = data.get("phi")
    if not isinstance(phi, list) or len(phi) != rows:
        raise ValueError("spectral_coordinates.phi length mismatch")
    dimension: int | None = None
    normalized_phi = []
    for index, item in enumerate(phi):
        row = _mapping(item, f"spectral_coordinates.phi[{index}]")
        if row.get("row") != index:
            raise ValueError("phi row mismatch")
        coords = _vector(row.get("coordinates"), f"spectral_coordinates.phi[{index}].coordinates")
        if dimension is None:
            dimension = len(coords)
        elif len(coords) != dimension:
            raise ValueError("phi dimension mismatch")
        normalized_phi.append({"row": index, "object_id": _non_empty_str(row.get("object_id"), "phi.object_id"), "coordinates": coords})
    psi = _mapping(data.get("psi"), "spectral_coordinates.psi")
    probes = psi.get("probes")
    if not isinstance(probes, list):
        raise ValueError("spectral_coordinates.psi.probes must be a list")
    normalized_probes = []
    for index, item in enumerate(probes):
        probe = _mapping(item, f"spectral_coordinates.psi.probes[{index}]")
        row_index = probe.get("row")
        if not isinstance(row_index, int) or row_index < 0 or row_index >= rows:
            raise ValueError("psi row mismatch")
        coords = _vector(probe.get("coordinates"), f"spectral_coordinates.psi.probes[{index}].coordinates", dimension)
        normalized = {
            "probe_id": _non_empty_str(probe.get("probe_id"), "psi.probe_id"),
            "row": row_index,
            "object_id": _non_empty_str(probe.get("object_id"), "psi.object_id"),
            "coordinates": coords,
            "candidate_refs": _candidate_refs(probe.get("candidate_refs", []), rows, index),
        }
        _validate_probe_non_authority(probe, index)
        if "score" in probe:
            normalized["score"] = float(probe["score"])
        normalized_probes.append(normalized)
    return {"phi": normalized_phi, "psi": {"probes": normalized_probes}}


def _candidate_refs(value: Any, rows: int, probe_index: int) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise ValueError(f"spectral_coordinates.psi.probes[{probe_index}].candidate_refs must be a list")
    refs = []
    for index, item in enumerate(value):
        ref = _mapping(item, f"spectral_coordinates.psi.probes[{probe_index}].candidate_refs[{index}]")
        row = ref.get("row")
        if not isinstance(row, int) or row < 0 or row >= rows:
            raise ValueError("candidate_ref row mismatch")
        for flag in ("truth", "support", "admissibility", "committed_support"):
            if ref.get(flag) is True:
                raise ValueError(f"candidate_ref.{flag} must not be true")
        refs.append(
            {
                "candidate_ref": _non_empty_str(ref.get("candidate_ref"), "candidate_ref.candidate_ref"),
                "row": row,
                "object_id": _non_empty_str(ref.get("object_id"), "candidate_ref.object_id"),
                "rank": int(ref.get("rank", index)),
            }
        )
    return refs


def _validate_probe_non_authority(probe: Mapping[str, Any], index: int) -> None:
    for flag in ("truth", "support", "admissibility", "committed_support"):
        if probe.get(flag) is True:
            raise ValueError(f"spectral_coordinates.psi.probes[{index}].{flag} must not be true")


def _gemv(value: Any, rows: int) -> dict[str, Any]:
    data = _mapping(value, "gemv")
    z = _vector(data.get("z"), "gemv.z", rows)
    matrix = _square_matrix(data.get("A"), "gemv.A", rows)
    bias = data.get("b")
    if bias is not None:
        _vector(bias, "gemv.b", rows)
    row_map = data.get("row_map")
    if row_map is not None:
        _row_map(row_map)
    return {"z": z, "A": matrix, "b": bias}


def _assert_vector_close(actual: list[float], expected: list[float], message: str) -> None:
    if len(actual) != len(expected):
        raise ValueError(message)
    for left, right in zip(actual, expected):
        if abs(left - right) > 1e-9:
            raise ValueError(message)


def _assert_matrix_close(actual: list[list[float]], expected: list[list[float]], message: str) -> None:
    if len(actual) != len(expected):
        raise ValueError(message)
    for left_row, right_row in zip(actual, expected):
        _assert_vector_close(left_row, right_row, message)
