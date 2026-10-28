from __future__ import annotations

import math
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
