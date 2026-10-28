from __future__ import annotations

import math
import struct
from pathlib import Path
from collections import Counter, defaultdict
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


RELATIONAL_FRAME_SCHEMA = "itir.pnf.relational_frame.v1"
SPECTRAL_NO_TYPED_MEET_SCHEMA = "itir.ao.spectral_no_typed_meet.v1"


def extract_relational_frames(slots: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Group structural PNF slots into predicate-argument factor frames."""
    if not isinstance(slots, Sequence) or isinstance(slots, (str, bytes, bytearray)):
        raise ValueError("slots must be an array of objects")

    grouped: dict[tuple[str, int, str], list[Mapping[str, Any]]] = defaultdict(list)
    for slot in slots:
        if not isinstance(slot, Mapping):
            raise ValueError("slot entries must be objects")
        sentence_id = _text(slot.get("sentence_id"))
        head_lemma = _text(slot.get("head_lemma")).casefold()
        if not sentence_id or not head_lemma:
            raise ValueError("every slot requires sentence_id and head_lemma")
        try:
            head_ordinal = int(slot.get("head_ordinal"))
        except (TypeError, ValueError) as exc:
            raise ValueError("every slot requires an integer head_ordinal") from exc
        grouped[(sentence_id, head_ordinal, head_lemma)].append(slot)

    frames: list[dict[str, Any]] = []
    for (sentence_id, head_ordinal, head_lemma), rows in sorted(grouped.items()):
        arguments: dict[str, list[str]] = defaultdict(list)
        boundary_metadata: list[dict[str, Any]] = []
        source_slot_ids: list[str] = []
        for slot in rows:
            slot_id = _text(slot.get("slot_id"))
            if slot_id:
                source_slot_ids.append(slot_id)

            boundary = slot.get("boundary_metadata")
            boundary_kind = _text(slot.get("boundary_kind"))
            if bool(slot.get("is_boundary")) or boundary_kind or isinstance(boundary, Mapping):
                entry: dict[str, Any] = {
                    "lemma": _text(slot.get("lemma")).casefold(),
                    "boundary_kind": boundary_kind,
                }
                role = _text(slot.get("argument_role") or slot.get("slot_role"))
                if role:
                    entry["slot_role"] = role
                if isinstance(boundary, Mapping):
                    entry["metadata"] = dict(boundary)
                boundary_metadata.append(entry)
                continue

            role = _text(slot.get("argument_role"))
            lemma = _text(slot.get("lemma")).casefold()
            if role and lemma and lemma not in arguments[role]:
                arguments[role].append(lemma)

        frames.append(
            {
                "schema": RELATIONAL_FRAME_SCHEMA,
                "sentence_id": sentence_id,
                "head_ordinal": head_ordinal,
                "predicate": head_lemma,
                "arguments": {role: sorted(values) for role, values in sorted(arguments.items())},
                "boundary_metadata": boundary_metadata,
                "source_slot_ids": sorted(set(source_slot_ids)),
            }
        )
    return frames


def spectral_no_typed_meet(
    lane_a: Mapping[str, Any],
    lane_b: Mapping[str, Any],
    spectral_model: Any = None,
    threshold: float = 0.15,
) -> dict[str, Any]:
    """Classify multiscale lane overlap without promoting geometry to theorem authority."""
    if not isinstance(lane_a, Mapping) or not isinstance(lane_b, Mapping):
        raise ValueError("lane_a and lane_b must be objects")
    if isinstance(threshold, bool) or not isinstance(threshold, (int, float)):
        raise ValueError("threshold must be numeric")
    threshold_value = float(threshold)
    if not math.isfinite(threshold_value) or not 0.0 <= threshold_value <= 1.0:
        raise ValueError("threshold must be finite and within [0, 1]")

    frames_a = _lane_relational_frames(lane_a)
    frames_b = _lane_relational_frames(lane_b)
    if spectral_model is None:
        vector_a, vector_b, graph_receipt = _world_graph_spectral_pair(lane_a, lane_b)
    else:
        vector_a, vector_b = _lane_embedding_pair(
            lane_a,
            lane_b,
            frames_a,
            frames_b,
            spectral_model=spectral_model,
        )
        graph_receipt = _world_graph_receipt(
            lane_a,
            lane_b,
            spectral_model=spectral_model,
        )
    cosine = abs(_cosine_similarity(vector_a, vector_b))
    shared_quotient_orbit = cosine > threshold_value
    meet_macro_disjoint = not shared_quotient_orbit

    carrier_a = _carrier_state(lane_a)
    carrier_b = _carrier_state(lane_b)
    carrier_scale_delta = abs(carrier_a["scale"] - carrier_b["scale"])
    prod_invariant_violation = _prod_invariant_violation(
        carrier_a,
        carrier_b,
        shared_quotient_orbit=shared_quotient_orbit,
    )
    defect_status = "illegalDefect" if prod_invariant_violation else "lawful"
    signatures_a = _sub_eigen_signatures(lane_a, frames_a)
    signatures_b = _sub_eigen_signatures(lane_b, frames_b)
    sub_eigen_meet = _sub_eigen_meet(signatures_a, signatures_b)
    orbit_relation = "shared_quotient_orbit" if shared_quotient_orbit else "orthogonal_domains"
    residual_status = "contradiction" if prod_invariant_violation else (
        sub_eigen_meet if shared_quotient_orbit else "not_applicable"
    )

    return {
        "schema": SPECTRAL_NO_TYPED_MEET_SCHEMA,
        "meet_macro_disjoint": meet_macro_disjoint,
        "cosine_similarity": cosine,
        "shared_quotient_orbit": shared_quotient_orbit,
        "orbit_relation": orbit_relation,
        "sub_eigen_meet": sub_eigen_meet,
        "sub_eigen_applicable": shared_quotient_orbit,
        "spectral_grounding": graph_receipt,
        "carrier_scale_delta": carrier_scale_delta,
        "prod_invariant_violation": prod_invariant_violation,
        "defect_status": defect_status,
        "residual_status": residual_status,
        "pressure_status": "critical" if prod_invariant_violation else "noncritical",
        "zoom_out_accommodates": not prod_invariant_violation,
        "admissible": meet_macro_disjoint and not prod_invariant_violation,
        "threshold": threshold_value,
        "frame_counts": {"lane_a": len(frames_a), "lane_b": len(frames_b)},
        "formal_boundary": {
            "quotient_projection_equality_proved": False,
            "spectral_overlap_is_candidate_fibre_only": True,
            "no_typed_meet_is_sub_eigen_residual": True,
            "illegal_defect_maps_to_contradiction_and_critical_pressure_in_agda": True,
            "world_invalidation_cannot_factor_through_collapsed_quotient": True,
            "agda_owners": [
                "Ontology/Hecke/PNFResidualBridge.agda",
                "DASHI/Interop/WorldEigenResidualStratification.agda",
            ],
        },
    }


def _lane_relational_frames(lane: Mapping[str, Any]) -> list[dict[str, Any]]:
    frames = lane.get("relational_frames")
    if isinstance(frames, Sequence) and not isinstance(frames, (str, bytes, bytearray)):
        return [dict(frame) for frame in frames if isinstance(frame, Mapping)]

    slots = lane.get("pnf_slots")
    if slots is None:
        slots = lane.get("slots")
    if isinstance(slots, Sequence) and not isinstance(slots, (str, bytes, bytearray)):
        return extract_relational_frames([slot for slot in slots if isinstance(slot, Mapping)])
    return []



def _sub_eigen_signatures(
    lane: Mapping[str, Any],
    frames: Sequence[Mapping[str, Any]],
) -> set[str]:
    explicit = lane.get("typed_signatures")
    if isinstance(explicit, Sequence) and not isinstance(explicit, (str, bytes, bytearray)):
        values = {_text(value) for value in explicit if _text(value)}
        if values:
            return values

    signatures: set[str] = set()
    for frame in frames:
        predicate = _text(frame.get("predicate")).casefold()
        arguments = frame.get("arguments")
        if not predicate or not isinstance(arguments, Mapping):
            continue
        roles = sorted(_text(role) for role in arguments if _text(role))
        signatures.add(predicate + "|" + ",".join(roles))
    return signatures


def _sub_eigen_meet(left: set[str], right: set[str]) -> str:
    if left and left == right:
        return "exact"
    if left & right:
        return "partial"
    return "noTypedMeet"


def _default_lane_embedding(
    lane: Mapping[str, Any],
    frames: Sequence[Mapping[str, Any]],
) -> Counter[str]:
    features: Counter[str] = Counter()
    for frame in frames:
        predicate = _text(frame.get("predicate")).casefold()
        if predicate:
            features[f"predicate:{predicate}"] += 1
        arguments = frame.get("arguments")
        if isinstance(arguments, Mapping):
            for role, values in arguments.items():
                role_text = _text(role)
                if not role_text or not isinstance(values, Sequence) or isinstance(values, (str, bytes, bytearray)):
                    continue
                for value in values:
                    lemma = _text(value).casefold()
                    if not lemma:
                        continue
                    features[f"argument:{role_text}:{lemma}"] += 1
                    if predicate:
                        features[f"edge:{predicate}:{role_text}:{lemma}"] += 1

    typed_support = lane.get("typed_support")
    if isinstance(typed_support, Mapping):
        for support_kind, values in typed_support.items():
            kind_text = _text(support_kind)
            if not kind_text or not isinstance(values, Sequence) or isinstance(values, (str, bytes, bytearray)):
                continue
            for value in values:
                norm = _text(value)
                if norm:
                    features[f"support:{kind_text}:{norm}"] += 1
    return features


def _lane_embedding_pair(
    lane_a: Mapping[str, Any],
    lane_b: Mapping[str, Any],
    frames_a: Sequence[Mapping[str, Any]],
    frames_b: Sequence[Mapping[str, Any]],
    *,
    spectral_model: Any,
) -> tuple[Mapping[str, float] | Sequence[float], Mapping[str, float] | Sequence[float]]:
    if spectral_model is None:
        left, right, _ = _world_graph_spectral_pair(lane_a, lane_b)
        return left, right
    if callable(spectral_model):
        return spectral_model(lane_a, frames_a), spectral_model(lane_b, frames_b)
    embed_lane = getattr(spectral_model, "embed_lane", None)
    if callable(embed_lane):
        return embed_lane(lane_a, frames_a), embed_lane(lane_b, frames_b)
    raise ValueError("spectral_model must be callable or provide embed_lane")


def _world_graph_receipt(
    lane_a: Mapping[str, Any],
    lane_b: Mapping[str, Any],
    *,
    spectral_model: Any,
) -> dict[str, Any]:
    if spectral_model is not None:
        return {
            "source": "external_spectral_model",
            "real_world_graph": False,
            "singular_values": [],
            "connecting_path": [],
        }
    _, _, receipt = _world_graph_spectral_pair(lane_a, lane_b)
    return receipt


def _world_graph_spectral_pair(
    lane_a: Mapping[str, Any],
    lane_b: Mapping[str, Any],
) -> tuple[list[float], list[float], dict[str, Any]]:
    graph = _merge_world_graphs(lane_a.get("world_graph"), lane_b.get("world_graph"))
    node_ids, hyperedges = _normalise_world_graph(graph)
    anchors_a = _graph_anchor_ids(lane_a, node_ids)
    anchors_b = _graph_anchor_ids(lane_b, node_ids)

    operator = build_typed_hyperfabric_operator(graph, node_ids=node_ids, hyperedges=hyperedges)
    coboundary = operator["coboundary"]
    transposed = _transpose_matrix(coboundary)
    singular_values, stalk_vectors = _jacobi_svd_left(transposed)

    usable = [
        index
        for index, value in enumerate(singular_values)
        if value > 1e-12
    ]
    dimensions = usable[-8:] if len(usable) > 8 else usable
    coordinate_offsets = operator["node_coordinate_offsets"]
    coordinates: dict[str, list[float]] = {}
    for node_id in node_ids:
        start, stop = coordinate_offsets[node_id]
        width = max(1, stop - start)
        coordinates[node_id] = [
            sum(stalk_vectors[row][dimension] for row in range(start, stop)) / width
            for dimension in dimensions
        ]

    left = _mean_anchor_coordinate(anchors_a, coordinates)
    right = _mean_anchor_coordinate(anchors_b, coordinates)
    path = _shortest_hypergraph_path(node_ids, hyperedges, anchors_a, anchors_b)
    selected_singular = [singular_values[index] for index in dimensions]
    return left, right, {
        "source": "real_pnf_typed_hyperfabric",
        "real_world_graph": True,
        "typed_hyperfabric": True,
        "node_count": len(node_ids),
        "hyperedge_count": len(hyperedges),
        "stalk_coordinate_count": operator["stalk_coordinate_count"],
        "restriction_row_count": operator["restriction_row_count"],
        "graph_refs": list(graph.get("graph_refs") or ()),
        "spectral_dimensions": len(dimensions),
        "singular_values": selected_singular,
        "sheaf_laplacian_eigenvalues": [value * value for value in selected_singular],
        "left_anchors": anchors_a,
        "right_anchors": anchors_b,
        "connecting_path": path,
        "operator": "normalized_typed_hyperfabric_coboundary_delta_then_deltaT_delta",
        "decomposition": "deterministic_one_sided_jacobi_svd",
        "restriction_maps_explicit": operator["restriction_maps_explicit"],
        "scalar_identity_lifts": operator["scalar_identity_lifts"],
        "stalk_type_refs": operator["stalk_type_refs"],
        "section_compatibility": operator["section_compatibility"],
        "wave_synthesis": operator["wave_synthesis"],
        "formal_boundary": {
            "typed_hyperfabric_owner": "DASHI/Reasoning/TypedHyperfabricCore.agda",
            "local_fibre_owner": "DASHI/Reasoning/LocalFibreHyperfabricExact.agda",
            "wave_owner": "DASHI/Reasoning/PNFWaveSynthesisCommutatorExact.agda",
            "spectral_owner": "DASHI/Interop/PNFSpectralFieldGraph.agda",
            "every_pnf_synthesis_rule_is_wave_addition": False,
            "semantic_truth_promotion": False,
        },
    }


def _merge_world_graphs(left: Any, right: Any) -> dict[str, Any]:
    if not isinstance(left, Mapping) and not isinstance(right, Mapping):
        raise ValueError(
            "real world_graph is required for default spectral geometry; "
            "synthetic feature vectors are not accepted"
        )
    graphs = [graph for graph in (left, right) if isinstance(graph, Mapping)]
    nodes: dict[str, dict[str, Any]] = {}
    edges: dict[str, dict[str, Any]] = {}
    for graph in graphs:
        for raw_node in graph.get("nodes") or ():
            if not isinstance(raw_node, Mapping):
                raise ValueError("world_graph nodes must be objects")
            node_id = _text(raw_node.get("id") or raw_node.get("node_ref"))
            if not node_id:
                raise ValueError("world_graph node requires id or node_ref")
            candidate = dict(raw_node)
            candidate["id"] = node_id
            prior = nodes.get(node_id)
            if prior is not None and prior != candidate:
                raise ValueError(f"world_graph node {node_id} disagrees across lane inputs")
            nodes[node_id] = candidate

        raw_edges = graph.get("hyperedges")
        if raw_edges is None:
            raw_edges = graph.get("edges")
        for ordinal, raw_edge in enumerate(raw_edges or ()):
            if not isinstance(raw_edge, Mapping):
                raise ValueError("world_graph hyperedges must be objects")
            edge_id = _text(raw_edge.get("id") or raw_edge.get("edge_ref"))
            if not edge_id:
                raise ValueError("world_graph edge requires id or edge_ref")
            candidate = dict(raw_edge)
            candidate["id"] = edge_id
            prior = edges.get(edge_id)
            if prior is not None and prior != candidate:
                raise ValueError(f"world_graph edge {edge_id} disagrees across lane inputs")
            edges[edge_id] = candidate

    if not nodes or not edges:
        raise ValueError("world_graph must contain nodes and hyperedges/edges")
    graph_refs = {
        _text(graph.get("projection_ref") or graph.get("graph_ref") or graph.get("revision_ref"))
        for graph in graphs
    }
    graph_refs.discard("")
    if not graph_refs:
        raise ValueError(
            "world_graph requires projection_ref, graph_ref, or revision_ref "
            "from a revision-bound graph projection"
        )
    return {
        "nodes": [nodes[key] for key in sorted(nodes)],
        "hyperedges": [edges[key] for key in sorted(edges)],
        "graph_refs": sorted(graph_refs),
    }


def _normalise_world_graph(
    graph: Mapping[str, Any],
) -> tuple[list[str], list[dict[str, Any]]]:
    node_ids = sorted(
        _text(node.get("id"))
        for node in graph.get("nodes") or ()
        if isinstance(node, Mapping) and _text(node.get("id"))
    )
    node_set = set(node_ids)
    if len(node_set) != len(node_ids):
        raise ValueError("world_graph node ids must be unique")

    hyperedges: list[dict[str, Any]] = []
    for raw_edge in graph.get("hyperedges") or ():
        state = _text(raw_edge.get("admissibility_state")).casefold()
        if state in {"blocked", "rejected"}:
            continue
        members = raw_edge.get("members")
        if members is None:
            members = [
                raw_edge.get("from_node_ref") or raw_edge.get("source_ref"),
                raw_edge.get("to_node_ref") or raw_edge.get("target_ref"),
            ]
        if not isinstance(members, Sequence) or isinstance(members, (str, bytes, bytearray)):
            raise ValueError("world_graph edge members must be an array")
        normalised_members = sorted(
            {
                _text(member)
                for member in members
                if _text(member)
            }
        )
        if len(normalised_members) < 2:
            continue
        unknown = [member for member in normalised_members if member not in node_set]
        if unknown:
            raise ValueError(f"world_graph edge references unknown nodes: {unknown}")
        raw_weight = raw_edge.get("weight", 1.0)
        if isinstance(raw_weight, bool) or not isinstance(raw_weight, (int, float)):
            raise ValueError("world_graph edge weight must be numeric")
        weight = float(raw_weight)
        if not math.isfinite(weight) or weight <= 0.0:
            raise ValueError("world_graph edge weight must be finite and positive")
        edge_stalk = raw_edge.get("edge_stalk")
        restrictions = raw_edge.get("restrictions")
        hyperedges.append(
            {
                "id": _text(raw_edge.get("id")),
                "kind": _text(raw_edge.get("kind") or raw_edge.get("relation_kind")),
                "members": normalised_members,
                "weight": weight,
                "provenance_ref": _text(raw_edge.get("provenance_ref")),
                "edge_stalk": dict(edge_stalk) if isinstance(edge_stalk, Mapping) else {},
                "restrictions": dict(restrictions) if isinstance(restrictions, Mapping) else {},
            }
        )
    if not hyperedges:
        raise ValueError("world_graph has no usable hyperedges")
    return node_ids, hyperedges


def _graph_anchor_ids(lane: Mapping[str, Any], node_ids: Sequence[str]) -> list[str]:
    raw = lane.get("graph_anchor_ids")
    if raw is None:
        raw = lane.get("world_graph_anchor_ids")
    if not isinstance(raw, Sequence) or isinstance(raw, (str, bytes, bytearray)):
        raise ValueError("lane requires graph_anchor_ids for real graph spectral projection")
    anchors = sorted({_text(value) for value in raw if _text(value)})
    unknown = [value for value in anchors if value not in set(node_ids)]
    if unknown:
        raise ValueError(f"graph anchors are not present in world_graph: {unknown}")
    if not anchors:
        raise ValueError("graph_anchor_ids must not be empty")
    return anchors


def apply_stalk_restriction(
    restriction: Sequence[Sequence[float]],
    value: Sequence[float],
) -> list[float]:
    if not isinstance(restriction, Sequence) or isinstance(restriction, (str, bytes, bytearray)):
        raise ValueError("restriction must be a matrix")
    vector = [float(item) for item in value]
    rows: list[list[float]] = []
    for row in restriction:
        if not isinstance(row, Sequence) or isinstance(row, (str, bytes, bytearray)):
            raise ValueError("restriction rows must be arrays")
        numeric = [float(item) for item in row]
        if len(numeric) != len(vector):
            raise ValueError("restriction row width must match stalk dimension")
        if any(not math.isfinite(item) for item in numeric):
            raise ValueError("restriction coefficients must be finite")
        rows.append(numeric)
    return [sum(coefficient * coordinate for coefficient, coordinate in zip(row, vector, strict=True)) for row in rows]


def add_discrete_waves(waves: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    if not isinstance(waves, Sequence) or isinstance(waves, (str, bytes, bytearray)):
        raise ValueError("waves must be an array")
    real: list[int] | None = None
    imag: list[int] | None = None
    for wave in waves:
        if not isinstance(wave, Mapping):
            raise ValueError("wave entries must be objects")
        re_values = _integer_wave_vector(wave.get("re"), "re")
        im_values = _integer_wave_vector(wave.get("im"), "im")
        if len(re_values) != len(im_values):
            raise ValueError("wave real and imaginary dimensions must match")
        if real is None:
            real = [0] * len(re_values)
            imag = [0] * len(im_values)
        if len(re_values) != len(real):
            raise ValueError("all waves must have the same dimension")
        for index, value in enumerate(re_values):
            real[index] += value
        for index, value in enumerate(im_values):
            imag[index] += value
    result_re = real or []
    result_im = imag or []
    if len(result_re) == 1:
        return {"re": result_re[0], "im": result_im[0]}
    return {"re": result_re, "im": result_im}


def _integer_wave_vector(value: Any, label: str) -> list[int]:
    if isinstance(value, bool):
        raise ValueError(f"wave {label} must be integer-valued")
    if isinstance(value, int):
        return [value]
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        result: list[int] = []
        for item in value:
            if isinstance(item, bool) or not isinstance(item, int):
                raise ValueError(f"wave {label} must be integer-valued")
            result.append(item)
        if result:
            return result
    raise ValueError(f"wave {label} must be an integer or integer array")


def build_typed_hyperfabric_operator(
    graph: Mapping[str, Any],
    *,
    node_ids: Sequence[str] | None = None,
    hyperedges: Sequence[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    if node_ids is None or hyperedges is None:
        node_ids, hyperedges = _normalise_world_graph(graph)
    nodes = {
        _text(node.get("id")): node
        for node in graph.get("nodes") or ()
        if isinstance(node, Mapping) and _text(node.get("id"))
    }
    if set(node_ids) != set(nodes):
        raise ValueError("typed hyperfabric node registry disagrees with normalized world graph")

    dimensions: dict[str, int] = {}
    offsets: dict[str, tuple[int, int]] = {}
    cursor = 0
    for node_id in node_ids:
        stalk = nodes[node_id].get("stalk")
        stalk_map = stalk if isinstance(stalk, Mapping) else {}
        raw_dimension = stalk_map.get("dimension", 1)
        if isinstance(raw_dimension, bool) or not isinstance(raw_dimension, int) or raw_dimension < 1:
            raise ValueError(f"node stalk dimension must be a positive integer: {node_id}")
        dimensions[node_id] = raw_dimension
        offsets[node_id] = (cursor, cursor + raw_dimension)
        cursor += raw_dimension

    degree = {node_id: 0.0 for node_id in node_ids}
    for edge in hyperedges:
        for member in edge["members"]:
            degree[member] += float(edge["weight"])

    coboundary: list[list[float]] = []
    explicit_restrictions = 0
    identity_lifts = 0
    wave_edges: list[dict[str, Any]] = []
    section_edges: list[dict[str, Any]] = []
    stalk_type_refs: set[str] = set()
    for node_id in node_ids:
        stalk = nodes[node_id].get("stalk")
        stalk_map = stalk if isinstance(stalk, Mapping) else {}
        type_ref = _text(stalk_map.get("type_ref"))
        if type_ref:
            stalk_type_refs.add(type_ref)

    for edge in hyperedges:
        members = list(edge["members"])
        edge_stalk = edge.get("edge_stalk")
        edge_stalk_map = edge_stalk if isinstance(edge_stalk, Mapping) else {}
        raw_edge_dimension = edge_stalk_map.get("dimension", 1)
        if isinstance(raw_edge_dimension, bool) or not isinstance(raw_edge_dimension, int) or raw_edge_dimension < 1:
            raise ValueError(f"edge stalk dimension must be a positive integer: {edge['id']}")
        edge_dimension = raw_edge_dimension
        restrictions = edge.get("restrictions")
        restriction_map = restrictions if isinstance(restrictions, Mapping) else {}

        resolved: dict[str, list[list[float]]] = {}
        for member in members:
            raw_matrix = restriction_map.get(member)
            if raw_matrix is None:
                if dimensions[member] != 1 or edge_dimension != 1:
                    raise ValueError(
                        f"explicit restriction required for non-scalar incidence {member}->{edge['id']}"
                    )
                matrix = [[1.0]]
                identity_lifts += 1
            else:
                matrix = _restriction_matrix(
                    raw_matrix,
                    edge_dimension=edge_dimension,
                    node_dimension=dimensions[member],
                    edge_id=str(edge["id"]),
                    node_id=member,
                )
                explicit_restrictions += 1
            resolved[member] = matrix

        pivot = members[0]
        scale = math.sqrt(float(edge["weight"]))
        for member in members[1:]:
            for edge_coordinate in range(edge_dimension):
                row = [0.0] * cursor
                pivot_start, _ = offsets[pivot]
                member_start, _ = offsets[member]
                pivot_norm = math.sqrt(degree[pivot]) if degree[pivot] > 0.0 else 1.0
                member_norm = math.sqrt(degree[member]) if degree[member] > 0.0 else 1.0
                for local, coefficient in enumerate(resolved[pivot][edge_coordinate]):
                    row[pivot_start + local] -= scale * coefficient / pivot_norm
                for local, coefficient in enumerate(resolved[member][edge_coordinate]):
                    row[member_start + local] += scale * coefficient / member_norm
                coboundary.append(row)

        wave_receipt = _edge_wave_superposition(
            edge=edge,
            members=members,
            nodes=nodes,
            restrictions=resolved,
            dimensions=dimensions,
        )
        if wave_receipt is not None:
            wave_edges.append(wave_receipt)

        section_receipt = _edge_section_compatibility(
            edge=edge,
            members=members,
            nodes=nodes,
            restrictions=resolved,
            dimensions=dimensions,
            edge_dimension=edge_dimension,
        )
        section_edges.append(section_receipt)

    if not coboundary:
        raise ValueError("typed hyperfabric requires at least one restriction compatibility row")
    return {
        "coboundary": coboundary,
        "node_coordinate_offsets": offsets,
        "stalk_coordinate_count": cursor,
        "restriction_row_count": len(coboundary),
        "restriction_maps_explicit": explicit_restrictions,
        "scalar_identity_lifts": identity_lifts,
        "stalk_type_refs": sorted(stalk_type_refs),
        "section_compatibility": {
            "evaluated_edge_count": sum(edge["evaluated"] for edge in section_edges),
            "obstruction_count": sum(1 for edge in section_edges if edge["obstructed"]),
            "global_section_compatible": (
                all(not edge["obstructed"] for edge in section_edges)
                if section_edges and all(edge["evaluated"] for edge in section_edges)
                else None
            ),
            "edges": section_edges,
            "formal_owner": "DASHI/Reasoning/TypedHyperfabricCore.agda",
        },
        "wave_synthesis": {
            "edge_count": len(wave_edges),
            "edges": wave_edges,
            "additive_superposition": True,
            "formal_owner": "DASHI/Reasoning/PNFWaveSynthesisCommutatorExact.agda",
            "every_pnf_synthesis_rule_identified_with_wave_addition": False,
        },
    }


def _restriction_matrix(
    value: Any,
    *,
    edge_dimension: int,
    node_dimension: int,
    edge_id: str,
    node_id: str,
) -> list[list[float]]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        raise ValueError(f"restriction {node_id}->{edge_id} must be a matrix")
    rows: list[list[float]] = []
    for raw_row in value:
        if not isinstance(raw_row, Sequence) or isinstance(raw_row, (str, bytes, bytearray)):
            raise ValueError(f"restriction {node_id}->{edge_id} rows must be arrays")
        row = [float(item) for item in raw_row]
        if len(row) != node_dimension:
            raise ValueError(f"restriction {node_id}->{edge_id} width must match node stalk")
        if any(not math.isfinite(item) for item in row):
            raise ValueError(f"restriction {node_id}->{edge_id} must be finite")
        rows.append(row)
    if len(rows) != edge_dimension:
        raise ValueError(f"restriction {node_id}->{edge_id} height must match edge stalk")
    return rows


def _edge_section_compatibility(
    *,
    edge: Mapping[str, Any],
    members: Sequence[str],
    nodes: Mapping[str, Mapping[str, Any]],
    restrictions: Mapping[str, Sequence[Sequence[float]]],
    dimensions: Mapping[str, int],
    edge_dimension: int,
    tolerance: float = 1e-12,
) -> dict[str, Any]:
    projected: dict[str, list[float]] = {}
    for member in members:
        stalk = nodes[member].get("stalk")
        stalk_map = stalk if isinstance(stalk, Mapping) else {}
        state = stalk_map.get("state")
        if state is None:
            continue
        if not isinstance(state, Sequence) or isinstance(state, (str, bytes, bytearray)):
            raise ValueError(f"stalk state for {member} must be a numeric array")
        numeric = [float(value) for value in state]
        if len(numeric) != dimensions[member] or any(not math.isfinite(value) for value in numeric):
            raise ValueError(f"stalk state dimension/values invalid for {member}")
        projected[member] = apply_stalk_restriction(restrictions[member], numeric)

    if len(projected) != len(members):
        return {
            "edge_id": _text(edge.get("id")),
            "evaluated": False,
            "obstructed": False,
            "reason": "not all incident node stalk states are supplied",
        }

    edge_stalk = edge.get("edge_stalk")
    edge_stalk_map = edge_stalk if isinstance(edge_stalk, Mapping) else {}
    edge_state = edge_stalk_map.get("state")
    targets: dict[str, list[float]] = {}
    if edge_state is not None:
        if not isinstance(edge_state, Sequence) or isinstance(edge_state, (str, bytes, bytearray)):
            raise ValueError(f"edge stalk state for {edge['id']} must be a numeric array")
        target = [float(value) for value in edge_state]
        if len(target) != edge_dimension or any(not math.isfinite(value) for value in target):
            raise ValueError(f"edge stalk state dimension/values invalid for {edge['id']}")
        targets = {member: target for member in members}
    else:
        pivot = members[0]
        target = projected[pivot]
        targets = {member: target for member in members}

    residuals: dict[str, float] = {}
    for member in members:
        delta = [
            value - target
            for value, target in zip(projected[member], targets[member], strict=True)
        ]
        residuals[member] = math.sqrt(sum(value * value for value in delta))
    max_residual = max(residuals.values(), default=0.0)
    return {
        "edge_id": _text(edge.get("id")),
        "evaluated": True,
        "obstructed": max_residual > tolerance,
        "max_residual_l2": max_residual,
        "incident_residual_l2": residuals,
    }


def _edge_wave_superposition(
    *,
    edge: Mapping[str, Any],
    members: Sequence[str],
    nodes: Mapping[str, Mapping[str, Any]],
    restrictions: Mapping[str, Sequence[Sequence[float]]],
    dimensions: Mapping[str, int],
) -> dict[str, Any] | None:
    restricted_waves: list[dict[str, Any]] = []
    integral_transport = True
    for member in members:
        stalk = nodes[member].get("stalk")
        stalk_map = stalk if isinstance(stalk, Mapping) else {}
        wave = stalk_map.get("discrete_wave")
        if wave is None:
            wave = nodes[member].get("discrete_wave")
        if wave is None:
            continue
        if not isinstance(wave, Mapping):
            raise ValueError(f"discrete_wave for {member} must be an object")
        re_values = _integer_wave_vector(wave.get("re"), "re")
        im_values = _integer_wave_vector(wave.get("im"), "im")
        if len(re_values) != dimensions[member] or len(im_values) != dimensions[member]:
            raise ValueError(f"discrete_wave dimension must match node stalk: {member}")
        matrix = restrictions[member]
        if any(float(value) != int(float(value)) for row in matrix for value in row):
            integral_transport = False
        restricted_re = apply_stalk_restriction(matrix, re_values)
        restricted_im = apply_stalk_restriction(matrix, im_values)
        if any(value != int(value) for value in restricted_re + restricted_im):
            integral_transport = False
        restricted_waves.append(
            {
                "re": [int(value) if value == int(value) else value for value in restricted_re],
                "im": [int(value) if value == int(value) else value for value in restricted_im],
            }
        )
    if not restricted_waves:
        return None
    if not integral_transport:
        return {
            "edge_id": _text(edge.get("id")),
            "formal_discrete_wave_commutator_applicable": False,
            "reason": "restriction transport leaves the integer DiscreteWave carrier",
        }
    total = add_discrete_waves(restricted_waves)
    return {
        "edge_id": _text(edge.get("id")),
        "restricted_incidence_count": len(restricted_waves),
        "superposition": total,
        "formal_discrete_wave_commutator_applicable": True,
        "synthesis_defect": {"re": 0, "im": 0},
    }


def _transpose_matrix(matrix: Sequence[Sequence[float]]) -> list[list[float]]:
    if not matrix:
        return []
    width = len(matrix[0])
    if any(len(row) != width for row in matrix):
        raise ValueError("matrix rows must have equal length")
    return [[float(matrix[row][column]) for row in range(len(matrix))] for column in range(width)]


def _jacobi_svd_left(
    matrix: Sequence[Sequence[float]],
    *,
    tolerance: float = 1e-12,
    max_sweeps: int = 64,
) -> tuple[list[float], list[list[float]]]:
    if not matrix:
        return [], []
    row_count = len(matrix)
    column_count = len(matrix[0])
    if column_count == 0:
        return [], [[] for _ in range(row_count)]
    if any(len(row) != column_count for row in matrix):
        raise ValueError("incidence matrix rows must have equal length")

    rotated = [[float(value) for value in row] for row in matrix]
    for _ in range(max_sweeps):
        changed = False
        for left_col in range(column_count - 1):
            for right_col in range(left_col + 1, column_count):
                alpha = sum(row[left_col] * row[left_col] for row in rotated)
                beta = sum(row[right_col] * row[right_col] for row in rotated)
                gamma = sum(row[left_col] * row[right_col] for row in rotated)
                if alpha == 0.0 or beta == 0.0:
                    continue
                if abs(gamma) <= tolerance * math.sqrt(alpha * beta):
                    continue
                zeta = (beta - alpha) / (2.0 * gamma)
                sign = 1.0 if zeta >= 0.0 else -1.0
                tangent = sign / (abs(zeta) + math.sqrt(1.0 + zeta * zeta))
                cosine = 1.0 / math.sqrt(1.0 + tangent * tangent)
                sine = cosine * tangent
                for row in rotated:
                    left_value = row[left_col]
                    right_value = row[right_col]
                    row[left_col] = cosine * left_value - sine * right_value
                    row[right_col] = sine * left_value + cosine * right_value
                changed = True
        if not changed:
            break

    singular_values_unsorted = [
        math.sqrt(sum(row[column] * row[column] for row in rotated))
        for column in range(column_count)
    ]
    order = sorted(
        range(column_count),
        key=lambda column: (-singular_values_unsorted[column], column),
    )
    singular_values = [singular_values_unsorted[column] for column in order]
    left_vectors = [
        [
            (
                rotated[row_index][column] / singular_values_unsorted[column]
                if singular_values_unsorted[column] > tolerance
                else 0.0
            )
            for column in order
        ]
        for row_index in range(row_count)
    ]
    return singular_values, left_vectors


def _mean_anchor_coordinate(
    anchors: Sequence[str],
    coordinates: Mapping[str, Sequence[float]],
) -> list[float]:
    width = len(next(iter(coordinates.values()), ()))
    return [
        sum(float(coordinates[anchor][dimension]) for anchor in anchors) / len(anchors)
        for dimension in range(width)
    ]


def _shortest_hypergraph_path(
    node_ids: Sequence[str],
    hyperedges: Sequence[Mapping[str, Any]],
    left_anchors: Sequence[str],
    right_anchors: Sequence[str],
) -> list[str]:
    adjacency: dict[str, set[str]] = {node_id: set() for node_id in node_ids}
    for edge in hyperedges:
        members = list(edge["members"])
        for left in members:
            adjacency[left].update(member for member in members if member != left)

    targets = set(right_anchors)
    queue: list[str] = list(left_anchors)
    parent: dict[str, str | None] = {anchor: None for anchor in left_anchors}
    cursor = 0
    found: str | None = None
    while cursor < len(queue):
        current = queue[cursor]
        cursor += 1
        if current in targets:
            found = current
            break
        for neighbour in sorted(adjacency[current]):
            if neighbour not in parent:
                parent[neighbour] = current
                queue.append(neighbour)
    if found is None:
        return []
    path: list[str] = []
    current: str | None = found
    while current is not None:
        path.append(current)
        current = parent[current]
    path.reverse()
    return path


def _cosine_similarity(
    vector_a: Mapping[str, float] | Sequence[float],
    vector_b: Mapping[str, float] | Sequence[float],
) -> float:
    if isinstance(vector_a, Mapping) and isinstance(vector_b, Mapping):
        keys = set(vector_a) | set(vector_b)
        dot = sum(float(vector_a.get(key, 0.0)) * float(vector_b.get(key, 0.0)) for key in keys)
        norm_a = math.sqrt(sum(float(value) ** 2 for value in vector_a.values()))
        norm_b = math.sqrt(sum(float(value) ** 2 for value in vector_b.values()))
    elif (
        isinstance(vector_a, Sequence)
        and isinstance(vector_b, Sequence)
        and not isinstance(vector_a, (str, bytes, bytearray))
        and not isinstance(vector_b, (str, bytes, bytearray))
    ):
        if len(vector_a) != len(vector_b):
            raise ValueError("spectral model vectors must have equal length")
        values_a = [float(value) for value in vector_a]
        values_b = [float(value) for value in vector_b]
        dot = sum(left * right for left, right in zip(values_a, values_b, strict=True))
        norm_a = math.sqrt(sum(value * value for value in values_a))
        norm_b = math.sqrt(sum(value * value for value in values_b))
    else:
        raise ValueError("spectral model must return two mappings or two numeric sequences")

    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


def _carrier_state(lane: Mapping[str, Any]) -> dict[str, Any]:
    carrier = lane.get("carrier")
    carrier_map = carrier if isinstance(carrier, Mapping) else {}
    raw_scale = carrier_map.get("scale", lane.get("carrier_scale", 0))
    if isinstance(raw_scale, bool) or not isinstance(raw_scale, (int, float)):
        raise ValueError("carrier scale must be numeric")
    scale = float(raw_scale)
    if not math.isfinite(scale):
        raise ValueError("carrier scale must be finite")

    mutation = lane.get("mutation")
    mutation_map = mutation if isinstance(mutation, Mapping) else {}
    return {
        "status": _text(carrier_map.get("status", lane.get("carrier_status"))).casefold(),
        "scale": scale,
        "schema_altering": bool(
            mutation_map.get("schema_altering", lane.get("schema_altering", False))
        ),
    }


def _prod_invariant_violation(
    carrier_a: Mapping[str, Any],
    carrier_b: Mapping[str, Any],
    *,
    shared_quotient_orbit: bool,
) -> bool:
    if not shared_quotient_orbit:
        return False
    for root, downstream in ((carrier_a, carrier_b), (carrier_b, carrier_a)):
        if (
            _text(root.get("status")).casefold() == "prod"
            and float(downstream.get("scale", 0.0)) > float(root.get("scale", 0.0))
            and bool(downstream.get("schema_altering"))
        ):
            return True
    return False


HIERARCHICAL_SPECTRAL_SCHEMA = "itir.pnf.hierarchical_spectral_pareto.v1"

GENERIC_CONVERSATIONAL_PREDICATES = frozenset({
    "want",
    "need",
    "return",
    "keep",
    "get",
    "think",
    "go",
    "see",
    "make",
    "do",
    "have",
    "be",
})



def load_slrw_conversation_factors(
    slrw_path: str | Path,
    *,
    conversation_limit: int | None = None,
) -> dict[str, Any]:
    """Load all PNF candidate factors from one revision-bound SLRW stream.

    The parser follows sl-world-compiler's WireRecord and PNF1 layouts. It
    scans once and groups candidates by the exact document_ref carried in aux1.
    """
    path = Path(slrw_path).expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError(f"SLRW corpus not found: {path}")
    if conversation_limit is not None and conversation_limit < 1:
        raise ValueError("conversation_limit must be positive")

    try:
        from re_gpt.pnf_compiler import FRAGMENT_NAMES, SHAPE_NAMES
    except Exception:
        FRAGMENT_NAMES = {}
        SHAPE_NAMES = {}

    conversations: dict[str, dict[str, Any]] = {}
    frame_members: dict[str, dict[tuple[int, int, str], list[tuple[str, str, str]]]] = defaultdict(dict)
    record_count = 0
    pnf_count = 0

    with path.open("rb") as handle:
        while True:
            magic = handle.read(4)
            if not magic:
                break
            if magic != b"SLRW":
                raise ValueError(f"invalid SLRW magic at record {record_count}: {magic!r}")
            version_raw = handle.read(2)
            header = handle.read(2)
            lengths = handle.read(12)
            iteration_raw = handle.read(8)
            if len(version_raw) != 2 or len(header) != 2 or len(lengths) != 12 or len(iteration_raw) != 8:
                raise ValueError("truncated SLRW record header")
            version = struct.unpack("<H", version_raw)[0]
            if version != 1:
                raise ValueError(f"unsupported SLRW version: {version}")
            kind_u8 = header[0]
            id_len, aux_len, payload_len = struct.unpack("<III", lengths)
            rec_id_raw = handle.read(id_len)
            aux_raw = handle.read(aux_len)
            payload = handle.read(payload_len)
            if len(rec_id_raw) != id_len or len(aux_raw) != aux_len or len(payload) != payload_len:
                raise ValueError("truncated SLRW record body")
            record_count += 1
            if kind_u8 != 2 or not payload.startswith(b"PNF1"):
                continue

            document_ref = aux_raw.decode("utf-8", errors="replace")
            if not document_ref:
                continue
            conversation_id = document_ref[5:] if document_ref.startswith("chat:") else document_ref
            if conversation_id not in conversations:
                if conversation_limit is not None and len(conversations) >= conversation_limit:
                    continue
                conversations[conversation_id] = {
                    "conversation_id": conversation_id,
                    "document_ref": document_ref,
                    "factor_counts": Counter(),
                    "frame_counts": Counter(),
                    "pnf_candidate_count": 0,
                }
                frame_members[conversation_id] = {}
            elif conversation_limit is not None and conversation_id not in conversations:
                continue

            decoded = _decode_slrw_pnf1(payload)
            fragment = str(FRAGMENT_NAMES.get(decoded["fragment"], f"fragment-{decoded['fragment']}"))
            shape = str(SHAPE_NAMES.get(decoded["shape"], f"shape-{decoded['shape']}"))
            lemma = decoded["lemma"].casefold()
            head_lemma = decoded["head_lemma"].casefold() or lemma
            factor_key = f"{head_lemma}|{fragment}|{lemma}|{shape}"
            row = conversations[conversation_id]
            row["factor_counts"][factor_key] += 1
            row["pnf_candidate_count"] += 1
            pnf_count += 1

            frame_key = (
                decoded["sentence_id"],
                decoded["head_ordinal"],
                head_lemma,
            )
            members = frame_members[conversation_id].setdefault(frame_key, [])
            members.append((fragment, lemma, shape))

    for conversation_id, groups in frame_members.items():
        target = conversations[conversation_id]["frame_counts"]
        for (_, _, predicate), members in groups.items():
            ordered = sorted(set(members))
            args = ",".join(f"{role}:{lemma}" for role, lemma, _shape in ordered)
            target[f"{predicate}({args})"] += 1

    normalized = {
        conversation_id: {
            **{key: value for key, value in row.items() if key not in {"factor_counts", "frame_counts"}},
            "factor_counts": dict(sorted(row["factor_counts"].items())),
            "frame_counts": dict(sorted(row["frame_counts"].items())),
        }
        for conversation_id, row in sorted(conversations.items())
    }
    return {
        "schema": "itir.pnf.slrw_corpus_factors.v1",
        "source_path": str(path),
        "record_count": record_count,
        "pnf_candidate_count": pnf_count,
        "conversation_count": len(normalized),
        "conversations": normalized,
        "source_contract": {
            "wire_owner": "slr/crates/sl-world-store",
            "pnf_owner": "slr/crates/sl-world-compiler",
            "record_kind": "PnfCandidate",
            "payload_magic": "PNF1",
        },
    }


def _decode_slrw_pnf1(payload: bytes) -> dict[str, Any]:
    if len(payload) < 32 or payload[:4] != b"PNF1":
        raise ValueError("invalid PNF1 payload")
    fragment = payload[4]
    shape = payload[5]
    sentence_id = struct.unpack("<Q", payload[8:16])[0]
    local_ordinal = struct.unpack("<I", payload[16:20])[0]
    head_ordinal = struct.unpack("<I", payload[20:24])[0]
    start_char = struct.unpack("<I", payload[24:28])[0]
    end_char = struct.unpack("<I", payload[28:32])[0]
    position = 32
    texts: list[str] = []
    for _ in range(4):
        if position + 4 > len(payload):
            raise ValueError("truncated PNF1 text length")
        length = struct.unpack("<I", payload[position : position + 4])[0]
        position += 4
        if position + length > len(payload):
            raise ValueError("truncated PNF1 text payload")
        texts.append(payload[position : position + length].decode("utf-8", errors="replace"))
        position += length
    orth, lemma, head_orth, head_lemma = texts
    return {
        "fragment": fragment,
        "shape": shape,
        "sentence_id": sentence_id,
        "local_ordinal": local_ordinal,
        "head_ordinal": head_ordinal,
        "start_char": start_char,
        "end_char": end_char,
        "orth": orth,
        "lemma": lemma,
        "head_orth": head_orth,
        "head_lemma": head_lemma,
    }


def build_hierarchical_pnf_topics(
    corpus: Mapping[str, Any] | str | Path,
    *,
    ontology_edges: Sequence[Mapping[str, Any]] | None = None,
    alpha_signals: Mapping[str, Mapping[str, Any]] | None = None,
    max_features: int = 256,
    max_spectral_dimensions: int = 16,
) -> dict[str, Any]:
    """Discover a nested topic hierarchy directly from corpus PNF incidence.

    No topic names or cluster count are predefined. Primary, sub-topic, and
    fibre partitions are induced by deterministic thresholds over continuous
    spectral coordinates.
    """
    if isinstance(corpus, (str, Path)):
        loaded = load_slrw_conversation_factors(corpus)
    elif isinstance(corpus, Mapping):
        loaded = dict(corpus)
    else:
        raise ValueError("corpus must be an SLRW path or corpus mapping")

    raw_conversations = loaded.get("conversations")
    if not isinstance(raw_conversations, Mapping):
        raise ValueError("corpus requires conversations mapping")
    conversation_ids = sorted(str(key) for key in raw_conversations)
    if len(conversation_ids) < 2:
        raise ValueError("hierarchical spectral analysis requires at least two conversations")
    if max_features < 2 or max_spectral_dimensions < 2:
        raise ValueError("spectral feature/dimension caps must be at least two")

    factor_counts: dict[str, Counter[str]] = {}
    frame_counts: dict[str, Counter[str]] = {}
    for conversation_id in conversation_ids:
        row = raw_conversations[conversation_id]
        if not isinstance(row, Mapping):
            raise ValueError(f"conversation row must be an object: {conversation_id}")
        factors = row.get("factor_counts")
        frames = row.get("frame_counts")
        factor_counts[conversation_id] = Counter(
            {
                str(key): float(value)
                for key, value in (factors.items() if isinstance(factors, Mapping) else [])
                if isinstance(value, (int, float)) and not isinstance(value, bool) and float(value) > 0.0
            }
        )
        frame_counts[conversation_id] = Counter(
            {
                str(key): float(value)
                for key, value in (frames.items() if isinstance(frames, Mapping) else [])
                if isinstance(value, (int, float)) and not isinstance(value, bool) and float(value) > 0.0
            }
        )

    ontology_feature_counts = _ontology_feature_counts(conversation_ids, ontology_edges or ())
    for conversation_id in conversation_ids:
        factor_counts[conversation_id].update(ontology_feature_counts[conversation_id])

    matrix_receipt = _corpus_factor_matrix(
        conversation_ids,
        factor_counts,
        max_features=max_features,
    )
    spectral = _mp_spectral_coordinates(
        matrix_receipt["matrix"],
        max_spectral_dimensions=max_spectral_dimensions,
    )
    coordinates = spectral["coordinates"]
    distance_matrix = _cosine_distance_matrix(coordinates)
    mst_edges = _minimum_spanning_tree(conversation_ids, distance_matrix)
    residual_thresholds = _dynamic_hierarchy_thresholds([edge["distance"] for edge in mst_edges])

    macro_coordinates = spectral["macro_coordinates"]
    if spectral["macro_mode_count"] > 0:
        macro_distance_matrix = _cosine_distance_matrix(macro_coordinates)
        macro_mst_edges = _minimum_spanning_tree(conversation_ids, macro_distance_matrix)
        macro_thresholds = _dynamic_hierarchy_thresholds(
            [edge["distance"] for edge in macro_mst_edges]
        )
        primary_tau = max(
            float(macro_thresholds["primary_tau"]),
            float(residual_thresholds["subtopic_tau"]),
        )
        primary_components = _threshold_components(
            conversation_ids,
            macro_distance_matrix,
            primary_tau,
        )
    else:
        macro_mst_edges = []
        primary_tau = max(2.0, float(residual_thresholds["subtopic_tau"]))
        primary_components = [conversation_ids]

    thresholds = {
        "fibre_tau": float(residual_thresholds["fibre_tau"]),
        "subtopic_tau": float(residual_thresholds["subtopic_tau"]),
        "primary_tau": primary_tau,
        "primary_metric": "mp_retained_macro_coordinates",
        "subtopic_metric": "full_spectral_coordinates",
        "fibre_metric": "full_spectral_coordinates_complete_link",
    }
    sub_components: list[list[str]] = []
    fibre_components: list[list[str]] = []
    primary_of: dict[str, str] = {}
    sub_of: dict[str, str] = {}
    fibre_of: dict[str, str] = {}

    primary_topics: list[dict[str, Any]] = []
    sub_topics: list[dict[str, Any]] = []
    fibre_topics: list[dict[str, Any]] = []

    alpha_rows, alpha_coverage = _conversation_alpha_rows(
        conversation_ids,
        coordinates,
        alpha_signals or {},
    )

    id_to_index = {conversation_id: index for index, conversation_id in enumerate(conversation_ids)}
    for primary_index, members in enumerate(primary_components):
        primary_id = f"primary-{primary_index:03d}"
        for member in members:
            primary_of[member] = primary_id
        primary_topics.append(
            _topic_summary(
                primary_id,
                "primary",
                members,
                factor_counts,
                frame_counts,
                ontology_feature_counts,
                coordinates,
                alpha_rows,
                id_to_index,
            )
        )
        local_subs = _threshold_components(
            members,
            distance_matrix,
            thresholds["subtopic_tau"],
            global_index=id_to_index,
        )
        for sub_index, sub_members in enumerate(local_subs):
            sub_id = f"{primary_id}.sub-{sub_index:03d}"
            sub_components.append(sub_members)
            for member in sub_members:
                sub_of[member] = sub_id
            summary = _topic_summary(
                sub_id,
                "subtopic",
                sub_members,
                factor_counts,
                frame_counts,
                ontology_feature_counts,
                coordinates,
                alpha_rows,
                id_to_index,
            )
            summary["parent_id"] = primary_id
            sub_topics.append(summary)

            cliques = _complete_link_threshold_groups(
                sub_members,
                distance_matrix,
                thresholds["fibre_tau"],
                id_to_index,
            )
            for fibre_index, fibre_members in enumerate(cliques):
                fibre_id = f"{sub_id}.fibre-{fibre_index:03d}"
                fibre_components.append(fibre_members)
                for member in fibre_members:
                    fibre_of[member] = fibre_id
                fibre_summary = _topic_summary(
                    fibre_id,
                    "fibre",
                    fibre_members,
                    factor_counts,
                    frame_counts,
                    ontology_feature_counts,
                    coordinates,
                    alpha_rows,
                    id_to_index,
                )
                fibre_summary["parent_id"] = sub_id
                fibre_topics.append(fibre_summary)

    primary_topics = _apply_discriminative_topic_motifs(
        primary_topics,
        frame_counts=frame_counts,
        ontology_counts=ontology_feature_counts,
    )
    sub_topics = _apply_discriminative_topic_motifs(
        sub_topics,
        frame_counts=frame_counts,
        ontology_counts=ontology_feature_counts,
    )
    fibre_topics = _apply_discriminative_topic_motifs(
        fibre_topics,
        frame_counts=frame_counts,
        ontology_counts=ontology_feature_counts,
    )

    conversation_rows = []
    for index, conversation_id in enumerate(conversation_ids):
        coordinate = [float(value) for value in coordinates[index]]
        xy = coordinate[:2] if len(coordinate) >= 2 else coordinate + [0.0]
        conversation_rows.append(
            {
                "conversation_id": conversation_id,
                "primary_id": primary_of[conversation_id],
                "subtopic_id": sub_of[conversation_id],
                "fibre_id": fibre_of[conversation_id],
                "coordinates": coordinate,
                "xy": xy,
                **alpha_rows[conversation_id],
            }
        )

    return {
        "schema": HIERARCHICAL_SPECTRAL_SCHEMA,
        "source": {
            "source_path": loaded.get("source_path"),
            "conversation_count": len(conversation_ids),
            "pnf_candidate_count": loaded.get("pnf_candidate_count"),
            "source_contract": loaded.get("source_contract"),
        },
        "feature_space": {
            "selected_feature_count": len(matrix_receipt["features"]),
            "features": matrix_receipt["features"],
            "selection": "corpus_energy_x_inverse_document_frequency",
            "hardcoded_topic_count": False,
        },
        "marchenko_pastur": {
            "gamma": spectral["gamma"],
            "sigma2": spectral["sigma2"],
            "lambda_plus": spectral["lambda_plus"],
            "eigenvalues": spectral["eigenvalues"],
            "macro_mode_count": spectral["macro_mode_count"],
            "retained_macro_indices": spectral["retained_macro_indices"],
        },
        "thresholds": thresholds,
        "mst_edges": mst_edges,
        "macro_mst_edges": macro_mst_edges,
        "primary_topics": primary_topics,
        "subtopics": sub_topics,
        "fibre_cliques": fibre_topics,
        "conversation_rows": conversation_rows,
        "alpha_signal_coverage": alpha_coverage,
        "formal_boundary": {
            "topics_are_data_derived": True,
            "topic_names_are_motif_receipts_not_semantic_truth": True,
            "ontology_terms_require_explicit_incidence_edges": True,
            "spectral_coordinates_are_operator_relative": True,
        },
    }


def _ontology_feature_counts(
    conversation_ids: Sequence[str],
    ontology_edges: Sequence[Mapping[str, Any]],
) -> dict[str, Counter[str]]:
    known = set(conversation_ids)
    result = {conversation_id: Counter() for conversation_id in conversation_ids}
    for edge in ontology_edges:
        if not isinstance(edge, Mapping):
            raise ValueError("ontology_edges entries must be objects")
        members = edge.get("conversation_ids")
        if members is None:
            members = edge.get("members")
        if not isinstance(members, Sequence) or isinstance(members, (str, bytes, bytearray)):
            raise ValueError("ontology edge requires conversation_ids/members array")
        label = _text(
            edge.get("label")
            or edge.get("target_label")
            or edge.get("predicate")
            or edge.get("edge_ref")
        ).casefold()
        if not label:
            raise ValueError("ontology edge requires a stable label/predicate/ref")
        raw_weight = edge.get("weight", 1.0)
        if isinstance(raw_weight, bool) or not isinstance(raw_weight, (int, float)):
            raise ValueError("ontology edge weight must be numeric")
        weight = float(raw_weight)
        if not math.isfinite(weight) or weight <= 0.0:
            raise ValueError("ontology edge weight must be finite and positive")
        feature = f"ontology:{label}"
        for member in members:
            conversation_id = _text(member)
            if conversation_id in known:
                result[conversation_id][feature] += weight
    return result


def _corpus_factor_matrix(
    conversation_ids: Sequence[str],
    factor_counts: Mapping[str, Counter[str]],
    *,
    max_features: int,
) -> dict[str, Any]:
    import numpy as np

    document_frequency: Counter[str] = Counter()
    energy: Counter[str] = Counter()
    for conversation_id in conversation_ids:
        counts = factor_counts[conversation_id]
        for feature, count in counts.items():
            if count <= 0:
                continue
            document_frequency[feature] += 1
            energy[feature] += math.log1p(float(count)) ** 2

    n = len(conversation_ids)
    ranked = sorted(
        energy,
        key=lambda feature: (
            -energy[feature] * math.log1p(n / max(1, document_frequency[feature])),
            feature,
        ),
    )
    cap = min(max_features, max(2, n - 1), len(ranked))
    features = ranked[:cap]
    if len(features) < 2:
        raise ValueError("corpus does not contain enough varying PNF factors")

    matrix = np.zeros((n, len(features)), dtype=float)
    for row_index, conversation_id in enumerate(conversation_ids):
        counts = factor_counts[conversation_id]
        for column_index, feature in enumerate(features):
            count = float(counts.get(feature, 0.0))
            if count <= 0.0:
                continue
            idf = math.log((1.0 + n) / (1.0 + document_frequency[feature])) + 1.0
            matrix[row_index, column_index] = math.log1p(count) * idf

    means = matrix.mean(axis=0)
    std = matrix.std(axis=0, ddof=1)
    keep = std > 1e-12
    matrix = matrix[:, keep]
    features = [feature for feature, retained in zip(features, keep.tolist(), strict=True) if retained]
    if matrix.shape[1] < 2:
        raise ValueError("corpus PNF factors collapse to fewer than two varying dimensions")
    matrix = (matrix - matrix.mean(axis=0)) / matrix.std(axis=0, ddof=1)
    return {"matrix": matrix, "features": features}


def _mp_spectral_coordinates(
    matrix: Any,
    *,
    max_spectral_dimensions: int,
) -> dict[str, Any]:
    import numpy as np

    n, d = matrix.shape
    covariance = (matrix.T @ matrix) / max(1, n - 1)
    eigenvalues, eigenvectors = np.linalg.eigh(covariance)
    order = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[order]
    eigenvectors = eigenvectors[:, order]

    positive = eigenvalues[eigenvalues > 1e-12]
    if positive.size == 0:
        raise ValueError("spectral covariance has no positive modes")
    tail_start = max(1, int(math.floor(0.20 * len(positive))))
    bulk = positive[tail_start:] if tail_start < len(positive) else positive
    sigma2 = float(np.median(bulk))
    gamma = float(d / n)
    lambda_plus = sigma2 * (1.0 + math.sqrt(gamma)) ** 2
    retained = [int(index) for index, value in enumerate(eigenvalues) if float(value) > lambda_plus]

    dimension_count = min(max_spectral_dimensions, d)
    coordinates = matrix @ eigenvectors[:, :dimension_count]
    retained_limited = [index for index in retained if index < dimension_count]
    macro_coordinates = (
        matrix @ eigenvectors[:, retained_limited]
        if retained_limited
        else np.zeros((n, 1), dtype=float)
    )
    return {
        "coordinates": coordinates,
        "macro_coordinates": macro_coordinates,
        "eigenvalues": [float(value) for value in eigenvalues[:dimension_count]],
        "gamma": gamma,
        "sigma2": sigma2,
        "lambda_plus": lambda_plus,
        "macro_mode_count": len(retained_limited),
        "retained_macro_indices": retained_limited,
    }


def _cosine_distance_matrix(coordinates: Any) -> Any:
    import numpy as np

    matrix = np.asarray(coordinates, dtype=float)
    norms = np.linalg.norm(matrix, axis=1)
    normalized = np.zeros_like(matrix)
    nonzero = norms > 1e-12
    normalized[nonzero] = matrix[nonzero] / norms[nonzero, None]
    similarity = normalized @ normalized.T
    similarity = np.clip(similarity, -1.0, 1.0)
    distance = 1.0 - similarity
    np.fill_diagonal(distance, 0.0)
    return distance


def _minimum_spanning_tree(
    conversation_ids: Sequence[str],
    distance_matrix: Any,
) -> list[dict[str, Any]]:
    n = len(conversation_ids)
    selected = [False] * n
    best = [math.inf] * n
    parent = [-1] * n
    best[0] = 0.0
    edges: list[dict[str, Any]] = []
    for _ in range(n):
        node = min((index for index in range(n) if not selected[index]), key=lambda index: (best[index], conversation_ids[index]))
        selected[node] = True
        if parent[node] >= 0:
            edges.append(
                {
                    "left": conversation_ids[parent[node]],
                    "right": conversation_ids[node],
                    "distance": float(distance_matrix[parent[node]][node]),
                }
            )
        for candidate in range(n):
            if selected[candidate] or candidate == node:
                continue
            value = float(distance_matrix[node][candidate])
            if value < best[candidate] - 1e-15 or (
                abs(value - best[candidate]) <= 1e-15
                and (parent[candidate] < 0 or conversation_ids[node] < conversation_ids[parent[candidate]])
            ):
                best[candidate] = value
                parent[candidate] = node
    return sorted(edges, key=lambda edge: (edge["distance"], edge["left"], edge["right"]))


def _dynamic_hierarchy_thresholds(mst_weights: Sequence[float]) -> dict[str, float]:
    import numpy as np

    values = sorted(float(value) for value in mst_weights if math.isfinite(float(value)) and float(value) >= 0.0)
    if not values:
        return {"fibre_tau": 0.0, "subtopic_tau": 0.0, "primary_tau": 0.0}
    if len(values) == 1:
        base = values[0]
        return {
            "fibre_tau": base * 0.50,
            "subtopic_tau": base * 0.75,
            "primary_tau": base,
        }

    gaps = [
        (values[index + 1] - values[index], index)
        for index in range(len(values) - 1)
    ]
    gap, gap_index = max(gaps, key=lambda item: (item[0], item[1]))
    gap_cut = (values[gap_index] + values[gap_index + 1]) / 2.0 if gap > 1e-15 else float(np.quantile(values, 0.75))
    fine = float(np.quantile(values, 0.25))
    sub = float(np.quantile(values, 0.50))
    primary = max(gap_cut, float(np.quantile(values, 0.75)))
    if sub < fine:
        sub = fine
    if primary < sub:
        primary = sub
    return {
        "fibre_tau": fine,
        "subtopic_tau": sub,
        "primary_tau": primary,
    }


def _threshold_components(
    members: Sequence[str],
    distance_matrix: Any,
    tau: float,
    *,
    global_index: Mapping[str, int] | None = None,
) -> list[list[str]]:
    ordered = sorted(members)
    index = global_index or {member: position for position, member in enumerate(ordered)}
    adjacency = {member: [] for member in ordered}
    for left_position, left in enumerate(ordered):
        for right in ordered[left_position + 1 :]:
            if float(distance_matrix[index[left]][index[right]]) <= tau + 1e-15:
                adjacency[left].append(right)
                adjacency[right].append(left)
    seen: set[str] = set()
    components: list[list[str]] = []
    for seed in ordered:
        if seed in seen:
            continue
        queue = [seed]
        seen.add(seed)
        component: list[str] = []
        while queue:
            current = queue.pop()
            component.append(current)
            for neighbour in adjacency[current]:
                if neighbour not in seen:
                    seen.add(neighbour)
                    queue.append(neighbour)
        components.append(sorted(component))
    return sorted(components, key=lambda component: (component[0], len(component)))


def _complete_link_threshold_groups(
    members: Sequence[str],
    distance_matrix: Any,
    tau: float,
    index: Mapping[str, int],
) -> list[list[str]]:
    groups: list[list[str]] = []
    for member in sorted(members):
        placed = False
        for group in groups:
            if all(float(distance_matrix[index[member]][index[other]]) <= tau + 1e-15 for other in group):
                group.append(member)
                placed = True
                break
        if not placed:
            groups.append([member])
    return [sorted(group) for group in groups]


def _conversation_alpha_rows(
    conversation_ids: Sequence[str],
    coordinates: Any,
    alpha_signals: Mapping[str, Mapping[str, Any]],
) -> tuple[dict[str, dict[str, float]], dict[str, Any]]:
    import numpy as np

    energies = np.sum(np.asarray(coordinates, dtype=float) ** 2, axis=1)
    energy_max = max(float(np.max(energies)), 1e-12)
    theorem_raw: dict[str, float] = {}
    gap_raw: dict[str, float] = {}
    theorem_supplied = 0
    gap_supplied = 0
    for conversation_id in conversation_ids:
        signals = alpha_signals.get(conversation_id)
        signal_map = signals if isinstance(signals, Mapping) else {}
        theorem_value = signal_map.get("theorem_density", 0.0)
        gap_value = signal_map.get("formal_gap_reduction", 0.0)
        theorem = float(theorem_value) if isinstance(theorem_value, (int, float)) and not isinstance(theorem_value, bool) else 0.0
        gap = float(gap_value) if isinstance(gap_value, (int, float)) and not isinstance(gap_value, bool) else 0.0
        theorem_raw[conversation_id] = max(0.0, theorem)
        gap_raw[conversation_id] = max(0.0, gap)
        theorem_supplied += int("theorem_density" in signal_map)
        gap_supplied += int("formal_gap_reduction" in signal_map)

    theorem_max = max(theorem_raw.values(), default=0.0)
    gap_max = max(gap_raw.values(), default=0.0)
    rows: dict[str, dict[str, float]] = {}
    for index, conversation_id in enumerate(conversation_ids):
        spectral_energy = float(energies[index]) / energy_max
        theorem_density = theorem_raw[conversation_id] / theorem_max if theorem_max > 0.0 else 0.0
        formal_gap_reduction = gap_raw[conversation_id] / gap_max if gap_max > 0.0 else 0.0
        alpha = 0.50 * spectral_energy + 0.30 * theorem_density + 0.20 * formal_gap_reduction
        rows[conversation_id] = {
            "spectral_energy": spectral_energy,
            "theorem_density": theorem_density,
            "formal_gap_reduction": formal_gap_reduction,
            "alpha": alpha,
        }
    return rows, {
        "conversation_count": len(conversation_ids),
        "theorem_density_supplied": theorem_supplied,
        "formal_gap_reduction_supplied": gap_supplied,
        "spectral_energy_supplied": len(conversation_ids),
        "weights": {
            "spectral_energy": 0.50,
            "theorem_density": 0.30,
            "formal_gap_reduction": 0.20,
        },
    }


def _topic_summary(
    topic_id: str,
    level: str,
    members: Sequence[str],
    factor_counts: Mapping[str, Counter[str]],
    frame_counts: Mapping[str, Counter[str]],
    ontology_counts: Mapping[str, Counter[str]],
    coordinates: Any,
    alpha_rows: Mapping[str, Mapping[str, float]],
    index: Mapping[str, int],
) -> dict[str, Any]:
    aggregate_factors: Counter[str] = Counter()
    aggregate_frames: Counter[str] = Counter()
    aggregate_ontology: Counter[str] = Counter()
    for member in members:
        aggregate_factors.update(factor_counts[member])
        aggregate_frames.update(frame_counts[member])
        aggregate_ontology.update(ontology_counts[member])

    top_frames = [
        {
            "motif": motif,
            "count": float(weight),
            "typed": True,
            "predicate": _frame_predicate(motif),
        }
        for motif, weight in aggregate_frames.most_common(8)
        if not _is_generic_frame_motif(motif)
    ]
    top_ontology = [
        {
            "feature": feature.removeprefix("ontology:"),
            "count": float(weight),
            "typed": True,
            "stalk_label": f"external:{feature.removeprefix('ontology:')}",
        }
        for feature, weight in aggregate_ontology.most_common(8)
    ]
    name = topic_id

    width = len(coordinates[0])
    centroid = [
        sum(float(coordinates[index[member]][dimension]) for member in members) / len(members)
        for dimension in range(width)
    ]
    alpha_values = [float(alpha_rows[member]["alpha"]) for member in members]
    energy_values = [float(alpha_rows[member]["spectral_energy"]) for member in members]
    theorem_values = [float(alpha_rows[member]["theorem_density"]) for member in members]
    gap_values = [float(alpha_rows[member]["formal_gap_reduction"]) for member in members]
    return {
        "topic_id": topic_id,
        "level": level,
        "name": name,
        "member_count": len(members),
        "members": sorted(members),
        "semantic_centroid": {
            "spectral_coordinates": centroid,
            "top_relational_frames": top_frames,
            "top_ontology_incidence": top_ontology,
            "discriminative_motifs": [],
        },
        "alpha": {
            "mean": sum(alpha_values) / len(alpha_values),
            "max": max(alpha_values),
            "spectral_energy_mean": sum(energy_values) / len(energy_values),
            "theorem_density_mean": sum(theorem_values) / len(theorem_values),
            "formal_gap_reduction_mean": sum(gap_values) / len(gap_values),
        },
    }



def _frame_predicate(motif: str) -> str:
    return motif.split("(", 1)[0].strip().casefold()


def _is_generic_frame_motif(motif: str) -> bool:
    return _frame_predicate(motif) in GENERIC_CONVERSATIONAL_PREDICATES


def rank_discriminative_topic_motifs(
    topics: Sequence[Mapping[str, Any]],
    *,
    frame_counts: Mapping[str, Counter[str]],
    ontology_counts: Mapping[str, Counter[str]],
    limit: int = 8,
) -> list[dict[str, Any]]:
    return _apply_discriminative_topic_motifs(
        topics,
        frame_counts=frame_counts,
        ontology_counts=ontology_counts,
        limit=limit,
    )


def _apply_discriminative_topic_motifs(
    topics: Sequence[Mapping[str, Any]],
    *,
    frame_counts: Mapping[str, Counter[str]],
    ontology_counts: Mapping[str, Counter[str]],
    limit: int = 8,
) -> list[dict[str, Any]]:
    rows = [dict(topic) for topic in topics]
    if not rows:
        return rows

    cluster_frames: list[Counter[str]] = []
    cluster_ontology: list[Counter[str]] = []
    frame_df: Counter[str] = Counter()
    ontology_df: Counter[str] = Counter()

    for topic in rows:
        members = [
            str(member)
            for member in topic.get("members") or ()
            if str(member)
        ]
        frames: Counter[str] = Counter()
        ontology: Counter[str] = Counter()
        for member in members:
            frames.update(frame_counts.get(member, Counter()))
            ontology.update(ontology_counts.get(member, Counter()))
        frames = Counter({
            motif: count
            for motif, count in frames.items()
            if count > 0 and not _is_generic_frame_motif(motif)
        })
        ontology = Counter({
            feature: count
            for feature, count in ontology.items()
            if count > 0
        })
        cluster_frames.append(frames)
        cluster_ontology.append(ontology)
        frame_df.update(frames.keys())
        ontology_df.update(ontology.keys())

    total_clusters = len(rows)
    for index, topic in enumerate(rows):
        frames = cluster_frames[index]
        ontology = cluster_ontology[index]
        total_frames = sum(frames.values())
        total_ontology = sum(ontology.values())

        scored: list[dict[str, Any]] = []
        if total_frames > 0:
            for motif, count in frames.items():
                score = (
                    (float(count) / float(total_frames))
                    * math.log(float(total_clusters) / float(1 + frame_df[motif]))
                )
                scored.append({
                    "kind": "typed_frame",
                    "label": motif,
                    "predicate": _frame_predicate(motif),
                    "count": float(count),
                    "cluster_tf": float(count) / float(total_frames),
                    "cluster_df": int(frame_df[motif]),
                    "contrastive_score": score,
                    "stalk_label": f"predicate:{_frame_predicate(motif)}",
                })

        if total_ontology > 0:
            for feature, count in ontology.items():
                label = feature.removeprefix("ontology:")
                score = (
                    (float(count) / float(total_ontology))
                    * math.log(float(total_clusters) / float(1 + ontology_df[feature]))
                )
                scored.append({
                    "kind": "ontology_bridge",
                    "label": label,
                    "count": float(count),
                    "cluster_tf": float(count) / float(total_ontology),
                    "cluster_df": int(ontology_df[feature]),
                    "contrastive_score": score,
                    "stalk_label": f"external:{label}",
                })

        scored.sort(
            key=lambda item: (
                -float(item["contrastive_score"]),
                0 if item["kind"] == "typed_frame" else 1,
                -float(item["count"]),
                str(item["label"]),
            )
        )
        positive = [item for item in scored if float(item["contrastive_score"]) > 0.0]
        selected = (positive or scored)[:limit]

        centroid = topic.get("semantic_centroid")
        centroid_map = dict(centroid) if isinstance(centroid, Mapping) else {}
        centroid_map["discriminative_motifs"] = selected
        centroid_map["motif_scoring"] = {
            "formula": "(count_in_cluster/total_cluster_frames)*log(total_clusters/(1+cluster_document_frequency))",
            "total_clusters": total_clusters,
            "generic_predicate_filter": sorted(GENERIC_CONVERSATIONAL_PREDICATES),
            "typed_frames_prioritized": True,
            "ontology_labels_require_explicit_incidence": True,
        }
        centroid_map["top_relational_frames"] = [
            item for item in selected if item["kind"] == "typed_frame"
        ]
        centroid_map["top_ontology_incidence"] = [
            item for item in selected if item["kind"] == "ontology_bridge"
        ]
        topic["semantic_centroid"] = centroid_map

        typed = [item for item in selected if item["kind"] == "typed_frame"]
        external = [item for item in selected if item["kind"] == "ontology_bridge"]
        name_parts = [str(item["label"]) for item in typed[:2]]
        if len(name_parts) < 2:
            name_parts.extend(str(item["label"]) for item in external[: 2 - len(name_parts)])
        topic["name"] = " + ".join(name_parts) if name_parts else str(topic.get("topic_id"))
        topic["motif_name_source"] = "contrastive_typed_pnf_frames_and_explicit_ontology"
    return rows


def _factor_display_name(feature: str) -> str:
    if feature.startswith("ontology:"):
        return feature.removeprefix("ontology:")
    parts = feature.split("|")
    if len(parts) >= 3:
        return f"{parts[0]}:{parts[1]}:{parts[2]}"
    return feature
