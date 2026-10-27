from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import Any

from .pnf_spectral_numeric_abi import spectral_parity_hash, validate_spectral_numeric_abi


VERSION = "itir.pnf.spectral_candidate_packet.v0_1"

_FORBIDDEN_AUTHORITY_KEYS = {
    "truth",
    "support",
    "admissibility",
    "runtime",
    "promoted",
    "routing",
    "vector",
    "truth_authority",
    "support_authority",
    "admissibility_authority",
    "promotion_authority",
    "promotion",
    "promotion_enabled",
}


def build_candidate_spectral_packet(
    partial_view: Mapping[str, Any],
    spectral_payload_summary_or_payload: Mapping[str, Any],
) -> dict[str, Any]:
    partial = _mapping(partial_view, "partial_view")
    _reject_authority_creep(partial, "partial_view")

    graph_refs = _graph_refs(partial)
    spectral_input = _mapping(spectral_payload_summary_or_payload, "spectral_payload_summary_or_payload")
    _reject_authority_creep(spectral_input, "spectral_payload_summary_or_payload")

    if _looks_like_full_spectral_payload(spectral_input):
        validated_summary = validate_spectral_numeric_abi(dict(spectral_input))
        candidate_refs = _candidate_refs_from_full_payload(spectral_input)
        validation = {"status": "validated", "summary": validated_summary}
        parity_hash = validated_summary.get("parity_hash")
        summary_for_projection: Mapping[str, Any] = validated_summary
    else:
        summary_for_projection = _summary_payload(spectral_input)
        candidate_refs = _candidate_refs_from_summary(spectral_input)
        parity_hash = _parity_hash_from_summary(spectral_input)
        validation = {"status": "not_performed", "summary": _summary_projection(summary_for_projection)}

    phi_psi_ref_summary = _phi_psi_ref_summary(candidate_refs, summary_for_projection, graph_refs)
    packet: dict[str, Any] = {
        "version": VERSION,
        "candidate_only": True,
        "non_authoritative": True,
        "graph_refs": graph_refs,
        "candidate_refs": candidate_refs,
        "phi_psi_ref_summary": phi_psi_ref_summary,
        "validation": validation,
        "authority_boundary": {
            "read_only": True,
            "non_authoritative": True,
            "candidate_only": True,
            "canonical_truth_mutated": False,
            "truth": False,
            "support": False,
            "admissibility": False,
            "runtime": False,
            "promoted": False,
            "routing": False,
            "vector": False,
        },
    }
    if parity_hash is not None:
        packet["parity_hash"] = parity_hash
    return packet



def compute_hierarchical_eigen_coordinates(
    thread_multisets: Sequence[Mapping[str, Any]],
    k_eigens: int = 5,
) -> dict[str, Any]:
    """Compute deterministic covariance-SVD coordinates and MP motif selection.

    A covariance matrix is symmetric positive semidefinite, so its Jacobi
    eigendecomposition is its singular-value decomposition. The implementation
    stays dependency-free and fixes eigenvector signs from the largest loading
    so repeated runs have stable coordinates and motif names.
    """

    if isinstance(k_eigens, bool) or not isinstance(k_eigens, int) or k_eigens < 1:
        raise ValueError("k_eigens must be a positive integer")
    rows, thread_ids, factor_names = _normalise_thread_multisets(thread_multisets)
    if not rows or not factor_names:
        raise ValueError("thread_multisets must contain at least one numeric factor")

    n_threads = len(rows)
    n_factors = len(factor_names)
    means = [sum(row[j] for row in rows) / n_threads for j in range(n_factors)]
    centered = [[row[j] - means[j] for j in range(n_factors)] for row in rows]
    denom = max(n_threads - 1, 1)
    covariance = [
        [
            sum(centered[i][j] * centered[i][k] for i in range(n_threads)) / denom
            for k in range(n_factors)
        ]
        for j in range(n_factors)
    ]

    eigenvalues, eigenvectors = _symmetric_svd(covariance)
    k = min(k_eigens, n_factors)
    singular_values = [max(0.0, value) for value in eigenvalues[:k]]
    vectors = eigenvectors[:k]

    diagonal_variances = [max(0.0, covariance[i][i]) for i in range(n_factors)]
    sigma2 = _median(diagonal_variances)
    gamma = n_factors / n_threads
    lambda_plus = sigma2 * (1.0 + math.sqrt(gamma)) ** 2

    components: list[dict[str, Any]] = []
    for index, (value, vector) in enumerate(zip(singular_values, vectors, strict=True)):
        ordered = sorted(
            ((abs(vector[j]), factor_names[j], vector[j]) for j in range(n_factors)),
            key=lambda item: (-item[0], item[1]),
        )
        top = ordered[: min(3, len(ordered))]
        motif_name = " · ".join(name for _, name, _ in top)
        components.append(
            {
                "index": index,
                "singular_value": value,
                "macroscopic": value > lambda_plus,
                "motif_name": motif_name,
                "top_loadings": [
                    {"factor": name, "loading": loading, "abs_loading": magnitude}
                    for magnitude, name, loading in top
                ],
            }
        )

    thread_coordinates: list[dict[str, Any]] = []
    for thread_id, row in zip(thread_ids, centered, strict=True):
        coordinates = [sum(row[j] * vector[j] for j in range(n_factors)) for vector in vectors]
        thread_coordinates.append(
            {
                "thread_id": thread_id,
                "eigen": coordinates,
                "hierarchical": _hierarchical_coordinate(coordinates),
            }
        )

    concept_coordinates: list[dict[str, Any]] = []
    for factor_index, factor_name in enumerate(factor_names):
        coordinates = [
            vector[factor_index] * math.sqrt(max(0.0, value))
            for value, vector in zip(singular_values, vectors, strict=True)
        ]
        concept_coordinates.append(
            {
                "concept": factor_name,
                "eigen": coordinates,
                "hierarchical": _hierarchical_coordinate(coordinates),
            }
        )

    return {
        "schema": "itir.pnf.eigen_coordinates.v1",
        "method": "symmetric_covariance_svd_jacobi",
        "thread_count": n_threads,
        "factor_count": n_factors,
        "factor_names": factor_names,
        "k_eigens": k,
        "singular_values": singular_values,
        "marchenko_pastur": {
            "sigma_squared": sigma2,
            "gamma": gamma,
            "lambda_plus": lambda_plus,
            "macroscopic_component_count": sum(value > lambda_plus for value in singular_values),
        },
        "components": components,
        "eigen_motifs": [component for component in components if component["macroscopic"]],
        "thread_coordinates": thread_coordinates,
        "concept_coordinates": concept_coordinates,
        "authority_boundary": {
            "candidate_only": True,
            "diagnostic_only": True,
            "eigenvalue_magnitude_creates_proof_authority": False,
            "motif_name_creates_semantic_identity": False,
        },
    }


def analyze_pareto_distribution(factors: Mapping[str, Any] | Sequence[float | int]) -> dict[str, Any]:
    """Fit continuous Pareto and truncated discrete Zipf rank models.

    Continuous fits use the Pareto MLE above xmin=min(positive values).
    Discrete fits interpret descending positive factor magnitudes as rank
    frequencies and solve the finite Zipf MLE by deterministic bisection.
    """

    normalised = _normalise_pareto_factors(factors)
    results: dict[str, Any] = {}
    for name, values in normalised.items():
        positive = sorted(float(value) for value in values if float(value) > 0.0)
        results[name] = {
            "continuous_pareto": _fit_continuous_pareto(positive),
            "discrete_zipf": _fit_discrete_zipf(positive),
        }

    receipt = {
        "receipt_type": "itir.pnf.discrete_zipf_non_promotion.v1",
        "candidate_only": True,
        "diagnostic_only": True,
        "discrete_zipf_rank_creates_mathematical_theorem_truth": False,
        "rank_frequency_fit_creates_proof_authority": False,
        "mathematical_theorem_truth_requires_independent_formal_verification": True,
        "assertion": (
            "Discrete Zipf rank is a descriptive distribution fit only and cannot pay "
            "for mathematical theorem truth or proof authority."
        ),
    }
    return {
        "schema": "itir.pnf.pareto_distribution.v1",
        "factors": results,
        "non_promotion_receipt": receipt,
    }


def _normalise_thread_multisets(
    thread_multisets: Sequence[Mapping[str, Any]],
) -> tuple[list[list[float]], list[str], list[str]]:
    if not isinstance(thread_multisets, Sequence) or isinstance(thread_multisets, (str, bytes, bytearray)):
        raise ValueError("thread_multisets must be an array of objects")
    if not thread_multisets:
        raise ValueError("thread_multisets must not be empty")

    extracted: list[tuple[str, dict[str, float]]] = []
    all_factors: set[str] = set()
    for index, item in enumerate(thread_multisets):
        if not isinstance(item, Mapping):
            raise ValueError("thread_multisets entries must be objects")
        thread_id = _text(item.get("thread_id")) or f"thread:{index}"
        raw_factors = item.get("factors")
        factor_mapping = raw_factors if isinstance(raw_factors, Mapping) else item
        factors: dict[str, float] = {}
        for key, value in factor_mapping.items():
            if key == "thread_id":
                continue
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                if isinstance(raw_factors, Mapping):
                    raise ValueError(f"factor {key!r} must be numeric")
                continue
            number = float(value)
            if not math.isfinite(number) or number < 0.0:
                raise ValueError(f"factor {key!r} must be finite and non-negative")
            name = str(key).strip()
            if not name:
                raise ValueError("factor names must be non-empty")
            factors[name] = number
            all_factors.add(name)
        extracted.append((thread_id, factors))

    factor_names = sorted(all_factors)
    rows = [[factors.get(name, 0.0) for name in factor_names] for _, factors in extracted]
    return rows, [thread_id for thread_id, _ in extracted], factor_names


def _symmetric_svd(matrix: Sequence[Sequence[float]]) -> tuple[list[float], list[list[float]]]:
    size = len(matrix)
    if size == 0:
        return [], []
    a = [list(map(float, row)) for row in matrix]
    if any(len(row) != size for row in a):
        raise ValueError("covariance matrix must be square")
    vectors = [[1.0 if i == j else 0.0 for j in range(size)] for i in range(size)]
    tolerance = 1e-12
    max_steps = max(32, 50 * size * size)

    for _ in range(max_steps):
        p, q = 0, 0
        largest = 0.0
        for i in range(size):
            for j in range(i + 1, size):
                candidate = abs(a[i][j])
                if candidate > largest:
                    largest = candidate
                    p, q = i, j
        if largest <= tolerance:
            break

        app = a[p][p]
        aqq = a[q][q]
        apq = a[p][q]
        angle = 0.5 * math.atan2(2.0 * apq, aqq - app)
        cosine = math.cos(angle)
        sine = math.sin(angle)

        for i in range(size):
            if i in (p, q):
                continue
            aip = a[i][p]
            aiq = a[i][q]
            a[i][p] = a[p][i] = cosine * aip - sine * aiq
            a[i][q] = a[q][i] = sine * aip + cosine * aiq

        a[p][p] = cosine * cosine * app - 2.0 * sine * cosine * apq + sine * sine * aqq
        a[q][q] = sine * sine * app + 2.0 * sine * cosine * apq + cosine * cosine * aqq
        a[p][q] = a[q][p] = 0.0

        for i in range(size):
            vip = vectors[i][p]
            viq = vectors[i][q]
            vectors[i][p] = cosine * vip - sine * viq
            vectors[i][q] = sine * vip + cosine * viq

    pairs: list[tuple[float, list[float]]] = []
    for column in range(size):
        vector = [vectors[row][column] for row in range(size)]
        pairs.append((max(0.0, a[column][column]), _orient_vector(vector)))
    pairs.sort(key=lambda pair: pair[0], reverse=True)
    return [value for value, _ in pairs], [vector for _, vector in pairs]


def _orient_vector(vector: list[float]) -> list[float]:
    if not vector:
        return vector
    pivot = max(range(len(vector)), key=lambda index: (abs(vector[index]), -index))
    if vector[pivot] < 0.0:
        return [-value for value in vector]
    return vector


def _hierarchical_coordinate(values: Sequence[float]) -> dict[str, float]:
    padded = list(values[:3]) + [0.0] * max(0, 3 - len(values))
    return {
        "x_main_eigen": padded[0],
        "y_sub_eigen": padded[1],
        "z_leaf": padded[2],
    }


def _median(values: Sequence[float]) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[middle]
    return 0.5 * (ordered[middle - 1] + ordered[middle])


def _normalise_pareto_factors(
    factors: Mapping[str, Any] | Sequence[float | int],
) -> dict[str, list[float]]:
    if isinstance(factors, Mapping):
        result: dict[str, list[float]] = {}
        for raw_name, raw_values in factors.items():
            name = str(raw_name).strip()
            if not name:
                raise ValueError("factor names must be non-empty")
            values = raw_values.get("values") if isinstance(raw_values, Mapping) else raw_values
            if isinstance(values, Sequence) and not isinstance(values, (str, bytes, bytearray)):
                result[name] = [_finite_number(value, name) for value in values]
            else:
                result[name] = [_finite_number(values, name)]
        return result
    if isinstance(factors, Sequence) and not isinstance(factors, (str, bytes, bytearray)):
        return {"factor": [_finite_number(value, "factor") for value in factors]}
    raise ValueError("factors must be an object or numeric array")


def _finite_number(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label} values must be numeric")
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"{label} values must be finite")
    return number


def _fit_continuous_pareto(values: Sequence[float]) -> dict[str, Any]:
    if len(values) < 2:
        return {"status": "insufficient_data", "sample_count": len(values)}
    xmin = min(values)
    log_sum = sum(math.log(value / xmin) for value in values)
    if log_sum <= 0.0:
        return {
            "status": "insufficient_variation",
            "sample_count": len(values),
            "xmin": xmin,
        }
    alpha = len(values) / log_sum
    empirical = sorted(values)
    ks = 0.0
    count = len(empirical)
    for index, value in enumerate(empirical, start=1):
        empirical_cdf = index / count
        model_cdf = 1.0 - (xmin / value) ** alpha
        ks = max(ks, abs(empirical_cdf - model_cdf))
    return {
        "status": "fit",
        "sample_count": len(values),
        "xmin": xmin,
        "alpha": alpha,
        "density_exponent_alpha_plus_one": alpha + 1.0,
        "ks_distance": ks,
        "model": "continuous_pareto",
    }


def _fit_discrete_zipf(values: Sequence[float]) -> dict[str, Any]:
    weights = sorted((value for value in values if value > 0.0), reverse=True)
    if len(weights) < 2:
        return {"status": "insufficient_data", "rank_count": len(weights)}
    total = sum(weights)
    observed_log_rank = sum(weight * math.log(rank) for rank, weight in enumerate(weights, start=1)) / total

    def expected_log_rank(nu: float) -> float:
        probs = [rank ** (-nu) for rank in range(1, len(weights) + 1)]
        norm = sum(probs)
        return sum(prob * math.log(rank) for rank, prob in enumerate(probs, start=1)) / norm

    low, high = 0.0, 20.0
    if observed_log_rank >= expected_log_rank(low):
        nu = low
    elif observed_log_rank <= expected_log_rank(high):
        nu = high
    else:
        for _ in range(80):
            mid = 0.5 * (low + high)
            if expected_log_rank(mid) > observed_log_rank:
                low = mid
            else:
                high = mid
        nu = 0.5 * (low + high)

    model_weights = [rank ** (-nu) for rank in range(1, len(weights) + 1)]
    model_norm = sum(model_weights)
    empirical_cumulative = 0.0
    model_cumulative = 0.0
    ks = 0.0
    for weight, model_weight in zip(weights, model_weights, strict=True):
        empirical_cumulative += weight / total
        model_cumulative += model_weight / model_norm
        ks = max(ks, abs(empirical_cumulative - model_cumulative))

    return {
        "status": "fit",
        "rank_count": len(weights),
        "total_weight": total,
        "nu": nu,
        "ks_distance": ks,
        "model": "truncated_discrete_zipf",
        "rank_interpretation": "descending_positive_factor_magnitude",
    }



def _looks_like_full_spectral_payload(payload: Mapping[str, Any]) -> bool:
    required_keys = {
        "schema",
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
    }
    return required_keys.issubset(payload.keys())


def _graph_refs(partial_view: Mapping[str, Any]) -> dict[str, Any]:
    graph_refs: dict[str, Any] = {
        "artifact_identity": _artifact_identity(partial_view),
        "selectors": _string_list(partial_view.get("selectors")),
        "selected_shard_ids": _string_list(partial_view.get("selected_shard_ids")),
        "selected_sections": _string_list(partial_view.get("selected_sections")),
        "selected_shard_count": len(_string_list(partial_view.get("selected_shard_ids"))),
    }
    for key in ("completeness", "subset_of_artifact"):
        if key in partial_view:
            graph_refs[key] = partial_view[key]
    return graph_refs


def _artifact_identity(partial_view: Mapping[str, Any]) -> dict[str, Any]:
    identity = partial_view.get("artifact_identity")
    if not isinstance(identity, Mapping):
        return {}
    allowed = ("contractVersion", "artifactId", "artifactRevision", "artifactClass", "createdAtUtc")
    return {key: identity[key] for key in allowed if key in identity}


def _summary_payload(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    if "summary" in payload and isinstance(payload.get("summary"), Mapping):
        return payload["summary"]  # type: ignore[return-value]
    return payload


def _summary_projection(summary_payload: Mapping[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key in ("schema", "graph_version", "operator_profile", "objects", "rows", "spectral_dimensions", "probe_rows", "edge_kinds", "gemv_rows", "parity_hash", "candidate_only", "diagnostic_only"):
        if key in summary_payload:
            result[key] = summary_payload[key]
    if "validation" in summary_payload:
        result["validation"] = summary_payload["validation"]
    return result


def _candidate_refs_from_full_payload(payload: Mapping[str, Any]) -> list[dict[str, Any]]:
    spectral_coordinates = _mapping(payload.get("spectral_coordinates"), "spectral_coordinates")
    psi = _mapping(spectral_coordinates.get("psi"), "spectral_coordinates.psi")
    probes = psi.get("probes")
    if not isinstance(probes, list):
        return []
    refs: list[dict[str, Any]] = []
    for probe_index, probe_item in enumerate(probes):
        probe = _mapping(probe_item, f"spectral_coordinates.psi.probes[{probe_index}]")
        probe_id = _text(probe.get("probe_id"))
        for index, ref_item in enumerate(probe.get("candidate_refs") or []):
            ref = _mapping(ref_item, f"spectral_coordinates.psi.probes[{probe_index}].candidate_refs[{index}]")
            refs.append(
                {
                    "probe_id": probe_id,
                    "candidate_ref": _text(ref.get("candidate_ref")),
                    "row": _int(ref.get("row"), "row"),
                    "object_id": _text(ref.get("object_id")),
                    "rank": _int(ref.get("rank", index), "rank"),
                }
            )
    return refs


def _candidate_refs_from_summary(payload: Mapping[str, Any]) -> list[dict[str, Any]]:
    if isinstance(payload.get("candidate_refs"), list):
        return [_compact_candidate_ref(ref, index) for index, ref in enumerate(payload["candidate_refs"]) if isinstance(ref, Mapping)]

    spectral_coordinates = payload.get("spectral_coordinates")
    if isinstance(spectral_coordinates, Mapping):
        psi = spectral_coordinates.get("psi")
        if isinstance(psi, Mapping):
            probes = psi.get("probes")
            if isinstance(probes, list):
                refs: list[dict[str, Any]] = []
                for probe_index, probe_item in enumerate(probes):
                    if not isinstance(probe_item, Mapping):
                        continue
                    probe_id = _text(probe_item.get("probe_id"))
                    candidate_refs = probe_item.get("candidate_refs")
                    if not isinstance(candidate_refs, list):
                        continue
                    for index, ref_item in enumerate(candidate_refs):
                        if not isinstance(ref_item, Mapping):
                            continue
                        refs.append(
                            {
                                "probe_id": probe_id,
                                "candidate_ref": _text(ref_item.get("candidate_ref")),
                                "row": _int(ref_item.get("row"), "row"),
                                "object_id": _text(ref_item.get("object_id")),
                                "rank": _int(ref_item.get("rank", index), "rank"),
                            }
                        )
                return refs

    return []


def _compact_candidate_ref(ref: Mapping[str, Any], index: int) -> dict[str, Any]:
    result = {
        "candidate_ref": _text(ref.get("candidate_ref")),
        "row": _int(ref.get("row"), "row"),
        "object_id": _text(ref.get("object_id")),
        "rank": _int(ref.get("rank", index), "rank"),
    }
    probe_id = _text(ref.get("probe_id"))
    if probe_id:
        result["probe_id"] = probe_id
    return result


def _phi_psi_ref_summary(
    candidate_refs: Sequence[Mapping[str, Any]],
    summary_payload: Mapping[str, Any],
    graph_refs: Mapping[str, Any],
) -> dict[str, Any]:
    candidate_probe_ids = []
    candidate_rows = []
    for ref in candidate_refs:
        probe_id = _text(ref.get("probe_id"))
        if probe_id and probe_id not in candidate_probe_ids:
            candidate_probe_ids.append(probe_id)
        row = ref.get("row")
        if isinstance(row, int) and row not in candidate_rows:
            candidate_rows.append(row)

    rows = _int(summary_payload.get("rows", len(candidate_rows)), "rows")
    probe_rows = _int(summary_payload.get("probe_rows", len(candidate_probe_ids)), "probe_rows")
    return {
        "phi": {
            "rows": rows,
            "objects": _int(summary_payload.get("objects", 0), "objects") if "objects" in summary_payload else None,
            "spectral_dimensions": _int(summary_payload.get("spectral_dimensions", 0), "spectral_dimensions")
            if "spectral_dimensions" in summary_payload
            else None,
        },
        "psi": {
            "probe_rows": probe_rows,
            "probe_ids": candidate_probe_ids,
            "candidate_ref_count": len(candidate_refs),
        },
        "refs": {
            "graph_ref_count": len(_string_list(graph_refs.get("selected_shard_ids"))),
            "candidate_ref_count": len(candidate_refs),
            "candidate_rows": candidate_rows,
            "parity_hash_present": "parity_hash" in summary_payload and bool(summary_payload.get("parity_hash")),
        },
    }


def _parity_hash_from_summary(payload: Mapping[str, Any]) -> str | None:
    parity_hash = payload.get("parity_hash")
    if isinstance(parity_hash, str) and parity_hash.strip():
        return parity_hash.strip()
    summary = payload.get("summary")
    if isinstance(summary, Mapping):
        parity_hash = summary.get("parity_hash")
        if isinstance(parity_hash, str) and parity_hash.strip():
            return parity_hash.strip()
    return None


def _reject_authority_creep(payload: Mapping[str, Any], label: str) -> None:
    _scan_forbidden_authority_creep(payload, label)


def _scan_forbidden_authority_creep(value: Any, path: str) -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            next_path = f"{path}.{key}"
            if key in _FORBIDDEN_AUTHORITY_KEYS and item is True:
                raise ValueError(f"{next_path} must not be true")
            _scan_forbidden_authority_creep(item, next_path)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _scan_forbidden_authority_creep(item, f"{path}[{index}]")


def _mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{label} must be an object")
    return dict(value)


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _text(value: Any) -> str:
    if not isinstance(value, str):
        return "" if value is None else str(value).strip()
    return value.strip()


def _int(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        try:
            return int(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{label} must be an integer") from exc
    return value
