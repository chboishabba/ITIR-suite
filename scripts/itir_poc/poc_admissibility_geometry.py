#!/usr/bin/env python3
"""Candidate-surface admissibility geometry for the ITIR PoC."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Callable, Sequence

try:
    from poc_hashing import canonical_json, stable_hash
except ModuleNotFoundError:
    from scripts.itir_poc.poc_hashing import canonical_json, stable_hash

try:
    from poc_pnf_carrier import PREDICATE_ATOM_RECEIPT_FIELDS, PROJECTION_NAMESPACE
except ModuleNotFoundError:
    from scripts.itir_poc.poc_pnf_carrier import PREDICATE_ATOM_RECEIPT_FIELDS, PROJECTION_NAMESPACE

try:
    from poc_sqlite_surfaces import (
        RESIDUAL_LEVELS,
        compare_fact_residual,
        fact_atom_id,
        join_residual_levels,
        parse_event_datetime,
        prepare_fact_runtime_indexes,
        surface_adjacency_edge,
    )
except ModuleNotFoundError:
    from scripts.itir_poc.poc_sqlite_surfaces import (
        RESIDUAL_LEVELS,
        compare_fact_residual,
        fact_atom_id,
        join_residual_levels,
        parse_event_datetime,
        prepare_fact_runtime_indexes,
        surface_adjacency_edge,
    )


PromotionCertificateFn = Callable[..., dict[str, Any]]
SurfaceJoinSummaryFn = Callable[[Sequence[dict[str, Any]]], dict[str, Any]]

ADMISSIBILITY_GEOMETRY_OWNER_SYMBOLS = (
    "candidate_surfaces",
    "bounded_candidate_surfaces_v0_2",
    "bounded_surface_edges",
    "recursive_surface_join",
    "recursive_surface_join_closure",
    "promotion_certificate",
)
SQLITE_SURFACE_OWNER_SYMBOLS = (
    "sqlite_connect",
    "init_surface_artifact_db",
    "refresh_sqlite_delta_tables_for_run",
    "compare_sqlite_surface_runs",
    "compare_surface_summary_artifacts",
)


def admissibility_sqlite_boundary() -> dict[str, Any]:
    return {
        "admissibility_geometry": {
            "module": "poc_admissibility_geometry.py",
            "compatibility_module": "news_enrichment_poc.py",
            "owns": ADMISSIBILITY_GEOMETRY_OWNER_SYMBOLS,
            "sqlite_dependency_allowed": False,
        },
        "sqlite_surfaces": {
            "module": "poc_sqlite_surfaces.py",
            "owns": SQLITE_SURFACE_OWNER_SYMBOLS,
            "constructs_candidates": False,
            "closes_recursive_geometry": False,
            "schema_write_behavior_changes_allowed": False,
        },
        "compatibility_wrappers": {
            "module": "news_enrichment_poc.py",
            "must_remain": (
                "persist_surface_artifact_sqlite",
                "compare_sqlite_surface_runs",
                "compare_sqlite_surface_runs_main",
            ),
        },
    }


def receipt_complete(fact: dict[str, Any]) -> bool:
    receipts = fact.get("receipts") if isinstance(fact.get("receipts"), dict) else {}
    required = set(PREDICATE_ATOM_RECEIPT_FIELDS)
    receipt_ids = fact.get("receipt_ids") if isinstance(fact.get("receipt_ids"), list) else []
    return required.issubset(receipts.keys()) and all(receipts.get(key) for key in required) and len(receipt_ids) >= len(required)


def member_atom_projection(fact: dict[str, Any]) -> dict[str, Any]:
    return {
        "atom_id": fact_atom_id(fact),
        "fibre_id": fact.get("fibre_id"),
        "structural_signature": fact.get("structural_signature"),
        "source_feed_id": fact.get("source_feed_id"),
        "span_ref": fact.get("span_ref", {}),
        "receipt_ids": fact.get("receipt_ids", []),
        "wrapper_state": fact.get("wrapper_state", "asserted"),
    }


def candidate_surfaces(
    facts: Sequence[dict[str, Any]],
    *,
    promotion_certificate_fn: PromotionCertificateFn,
    surface_join_summary_fn: SurfaceJoinSummaryFn,
    max_surfaces: int | None = None,
    include_join_edges: bool = True,
    max_member_atoms: int | None = None,
    max_residual_comparisons_per_fibre: int = 256,
) -> list[dict[str, Any]]:
    by_signature: dict[str, list[dict[str, Any]]] = {}
    by_fibre: dict[str, list[dict[str, Any]]] = {}
    indexed_facts = [fact for fact in facts if fact.get("structural_signature") and fact.get("fibre_id")]
    prepare_fact_runtime_indexes(indexed_facts)
    for fact in facts:
        signature = fact.get("_signature_key") or ""
        fibre_id = fact.get("_fibre_key") or ""
        if not signature or not fibre_id:
            continue
        by_signature.setdefault(signature, []).append(fact)
        by_fibre.setdefault(fibre_id, []).append(fact)

    surfaces: list[dict[str, Any]] = []
    fibre_items = sorted(by_fibre.items(), key=lambda item: (-len(item[1]), str(item[0])))
    if max_surfaces is not None:
        fibre_items = fibre_items[:max(0, max_surfaces)]
    for fibre_id, fibre_facts in fibre_items:
        first = fibre_facts[0]
        signature = str(first.get("structural_signature") or "")
        compatible = by_signature.get(signature, [])
        residual_levels: list[str] = []
        comparison_count = 0
        for fact in fibre_facts:
            for other in compatible:
                residual_levels.append(compare_fact_residual(fact, other))
                comparison_count += 1
                if comparison_count >= max_residual_comparisons_per_fibre:
                    break
            if comparison_count >= max_residual_comparisons_per_fibre:
                break
        residual_summary = {level: residual_levels.count(level) for level in RESIDUAL_LEVELS}
        source_ids = sorted({str(fact.get("source_feed_id")) for fact in fibre_facts if fact.get("source_feed_id")})
        role_vectors = {
            fact.get("_role_vector_key") or canonical_json((fact.get("pnf") or {}).get("role_index") or [])
            for fact in fibre_facts
        }
        complete_receipts = sum(1 for fact in fibre_facts if receipt_complete(fact))
        support_count = len(fibre_facts)
        source_count = len(source_ids)
        receipt_completeness = complete_receipts / max(1, support_count)
        role_stability = 1.0 / max(1, len(role_vectors))
        blockers = []
        if receipt_completeness < 1.0:
            blockers.append("incomplete_receipts")
        if residual_summary["CONTRADICTION"]:
            blockers.append("contradiction_residual")
        if residual_summary["NO_TYPED_MEET"]:
            blockers.append("no_typed_meet_residual")
        if source_count < 2:
            blockers.append("single_source_support")
        blockers.append("external_promotion_authority_missing")
        surface_id = stable_hash(["candidate-surface", fibre_id, signature])[:24]
        pnf = first.get("pnf") if isinstance(first.get("pnf"), dict) else {}
        role_index = pnf.get("role_index") if isinstance(pnf.get("role_index"), list) else []
        member_atom_facts = fibre_facts if max_member_atoms is None else fibre_facts[:max(0, max_member_atoms)]
        join_edges: list[dict[str, Any]] = []
        seen_edges: set[str] = set()
        if include_join_edges:
            for fact in fibre_facts:
                for other in indexed_facts:
                    if other.get("_fibre_key") == fibre_id:
                        continue
                    edge = surface_adjacency_edge(fact, other)
                    if edge is None or edge["edge_id"] in seen_edges:
                        continue
                    seen_edges.add(edge["edge_id"])
                    join_edges.append(edge)
                    if len(join_edges) >= 32:
                        break
                if len(join_edges) >= 32:
                    break
        certificate = promotion_certificate_fn(
            receipt_completeness=receipt_completeness,
            residual_summary=residual_summary,
            source_count=source_count,
            blockers=blockers,
        )
        surfaces.append(
            {
                "candidate_id": stable_hash(["candidate", fibre_id])[:24],
                "surface_id": surface_id,
                "surface_kind": "fibre_candidate_surface",
                "fibre_id": fibre_id,
                "fibres": [fibre_id],
                "predicate": first.get("predicate"),
                "structural_signature": signature,
                "structural_signatures": [signature],
                "structural_signature_payload": first.get("structural_signature_payload"),
                "role_hashes": role_index,
                "projection_method": first.get("projection_method", PROJECTION_NAMESPACE),
                "projection_tags": [],
                "support_count": support_count,
                "source_count": source_count,
                "source_feed_ids": source_ids,
                "role_stability": role_stability,
                "residual_summary": residual_summary,
                "residual_join": join_residual_levels(residual_levels),
                "receipt_completeness": receipt_completeness,
                "receipt_ids": sorted({receipt_id for fact in fibre_facts for receipt_id in fact.get("receipt_ids", [])}),
                "blockers": blockers,
                "promotable": False,
                "promotion_certificate": certificate,
                "surface_certificate": certificate,
                "member_atoms": [member_atom_projection(fact) for fact in member_atom_facts],
                "join_edges": join_edges,
                "surface_join_summary": surface_join_summary_fn(join_edges),
                "pressure_score": support_count + max(0, source_count - 1),
                "span_refs": [fact.get("span_ref") for fact in fibre_facts if fact.get("span_ref")][:8],
            }
        )
    surfaces.sort(key=lambda item: (-item["pressure_score"], -item["support_count"], item["fibre_id"]))
    return surfaces


def edge_sources_cross(edge: dict[str, Any]) -> bool:
    left_source = edge.get("left_source_feed_id")
    right_source = edge.get("right_source_feed_id")
    return bool(left_source and right_source and left_source != right_source)


def edge_has_local_adjacency(edge: dict[str, Any]) -> bool:
    signals = set(edge.get("signals", []) or [])
    return bool(signals & {"same_source", "same_span", "overlapping_span", "temporal_proximity"})


def edge_has_convergence_witness(edge: dict[str, Any]) -> bool:
    signals = set(edge.get("signals", []) or [])
    if not edge_sources_cross(edge):
        return False
    if edge.get("residual_join") in {"CONTRADICTION", "NO_TYPED_MEET"}:
        return False
    return bool(signals & {"shared_role_hash", "fibre_compatible"})


def adjacency_support_measurements(surfaces: Sequence[dict[str, Any]], *, previous_surface_ids: set[str] | None = None) -> dict[str, Any]:
    join_edges = [edge for surface in surfaces for edge in surface.get("join_edges", []) or []]
    edge_count = len(join_edges)
    surface_count = len(surfaces)
    same_source_edges = [edge for edge in join_edges if "same_source" in set(edge.get("signals", []) or [])]
    same_source_only_edges = [edge for edge in same_source_edges if not edge_sources_cross(edge) and not edge_has_convergence_witness(edge)]
    cross_source_edges = [edge for edge in join_edges if edge_sources_cross(edge)]
    cross_source_support_edges = [edge for edge in cross_source_edges if edge_has_convergence_witness(edge)]
    local_adjacency_edges = [edge for edge in join_edges if edge_has_local_adjacency(edge)]
    convergence_witness_edges = [edge for edge in join_edges if edge_has_convergence_witness(edge)]
    previous_surface_ids = previous_surface_ids or set()
    persistent_surfaces = [surface for surface in surfaces if surface.get("surface_id") and str(surface.get("surface_id")) in previous_surface_ids]
    cross_source_surfaces = [surface for surface in surfaces if int(surface.get("source_count") or 0) >= 2]
    persistent_cross_source_surfaces = [surface for surface in persistent_surfaces if int(surface.get("source_count") or 0) >= 2]
    return {
        "edge_denominator_n": edge_count,
        "surface_denominator_n": surface_count,
        "same_source_edge_count": len(same_source_edges),
        "same_source_edge_ratio": len(same_source_edges) / max(1, edge_count),
        "same_source_edge_ratio(n)": len(same_source_edges) / max(1, edge_count),
        "same_source_only_edge_count": len(same_source_only_edges),
        "same_source_only_edge_ratio": len(same_source_only_edges) / max(1, edge_count),
        "same_source_only_edge_ratio(n)": len(same_source_only_edges) / max(1, edge_count),
        "local_adjacency_edge_count": len(local_adjacency_edges),
        "local_adjacency_edge_ratio": len(local_adjacency_edges) / max(1, edge_count),
        "local_adjacency_edge_ratio(n)": len(local_adjacency_edges) / max(1, edge_count),
        "cross_source_edge_count": len(cross_source_edges),
        "cross_source_edge_ratio": len(cross_source_edges) / max(1, edge_count),
        "cross_source_edge_ratio(n)": len(cross_source_edges) / max(1, edge_count),
        "cross_source_support_edge_count": len(cross_source_support_edges),
        "cross_source_support_ratio": len(cross_source_support_edges) / max(1, edge_count),
        "cross_source_support_ratio(n)": len(cross_source_support_edges) / max(1, edge_count),
        "convergence_witness_edge_count": len(convergence_witness_edges),
        "convergence_witness_ratio": len(convergence_witness_edges) / max(1, edge_count),
        "convergence_witness_ratio(n)": len(convergence_witness_edges) / max(1, edge_count),
        "single_source_surface_count": surface_count - len(cross_source_surfaces),
        "cross_source_supported_surface_count": len(cross_source_surfaces),
        "cross_source_supported_surface_ratio": len(cross_source_surfaces) / max(1, surface_count),
        "cross_source_supported_surface_ratio(n)": len(cross_source_surfaces) / max(1, surface_count),
        "persistent_surface_count": len(persistent_surfaces),
        "persistent_surface_ratio": len(persistent_surfaces) / max(1, surface_count),
        "persistent_surface_ratio(n)": len(persistent_surfaces) / max(1, surface_count),
        "persistent_cross_source_surface_count": len(persistent_cross_source_surfaces),
        "persistent_cross_source_surface_ratio": len(persistent_cross_source_surfaces) / max(1, surface_count),
        "persistent_cross_source_surface_ratio(n)": len(persistent_cross_source_surfaces) / max(1, surface_count),
        "local_adjacency_metadata_signals": ["same_source", "same_span", "overlapping_span", "temporal_proximity"],
        "convergence_witness_requirements": {
            "cross_source": True,
            "compatible_support_signal": ["shared_role_hash", "fibre_compatible"],
            "excluded_residuals": ["CONTRADICTION", "NO_TYPED_MEET"],
        },
        "same_source_is_convergence_witness": False,
        "promotion_from_same_source_only": False,
    }


def connected_component_sizes(surfaces: Sequence[dict[str, Any]]) -> list[int]:
    surface_by_fibre = {str(surface["fibre_id"]): str(surface.get("surface_id")) for surface in surfaces if surface.get("fibre_id")}
    graph: dict[str, set[str]] = {str(surface.get("surface_id")): set() for surface in surfaces}
    for surface in surfaces:
        left_surface_id = str(surface.get("surface_id"))
        for edge in surface.get("join_edges", []) or []:
            right_surface_id = surface_by_fibre.get(str(edge.get("right_fibre_id")))
            if right_surface_id and right_surface_id in graph and right_surface_id != left_surface_id:
                graph[left_surface_id].add(right_surface_id)
                graph[right_surface_id].add(left_surface_id)
    seen: set[str] = set()
    sizes: list[int] = []
    for node in graph:
        if node in seen:
            continue
        stack = [node]
        seen.add(node)
        size = 0
        while stack:
            current = stack.pop()
            size += 1
            for next_node in graph[current]:
                if next_node not in seen:
                    seen.add(next_node)
                    stack.append(next_node)
        sizes.append(size)
    return sizes


def recursive_surface_join_closure(
    surfaces: Sequence[dict[str, Any]],
    *,
    max_recursive_joins: int = 4096,
    max_no_typed_meet: int = 0,
    recursive_surface_join: Callable[..., dict[str, Any]] | None = None,
    surface_blocker_reasons: Callable[[dict[str, Any]], list[str]] | None = None,
    residual_levels: Sequence[str] | None = None,
) -> dict[str, Any]:
    if recursive_surface_join is None or surface_blocker_reasons is None or residual_levels is None:
        try:
            from news_enrichment_poc import recursive_surface_join as _join, surface_blocker_reasons as _reasons
        except ModuleNotFoundError:
            from scripts.itir_poc.news_enrichment_poc import recursive_surface_join as _join, surface_blocker_reasons as _reasons
        recursive_surface_join = recursive_surface_join or _join
        surface_blocker_reasons = surface_blocker_reasons or _reasons
        residual_levels = residual_levels or RESIDUAL_LEVELS
    surface_by_fibre = {str(surface.get("fibre_id")): surface for surface in surfaces if surface.get("fibre_id") and surface.get("surface_id")}
    attempted_pairs: set[tuple[str, str]] = set()
    blocked_reasons: dict[str, int] = {}
    residual_reasons: dict[str, int] = {level: 0 for level in residual_levels}
    allowed_recursive_surface_ids: set[str] = set()
    blocked = 0
    truncated = False
    for left in surfaces:
        left_id = str(left.get("surface_id") or "")
        if not left_id:
            continue
        for edge in left.get("join_edges", []) or []:
            right = surface_by_fibre.get(str(edge.get("right_fibre_id")))
            right_id = str(right.get("surface_id") if right else "")
            if right is None or not right_id or right_id == left_id:
                continue
            pair = tuple(sorted((left_id, right_id)))
            if pair in attempted_pairs:
                continue
            if len(attempted_pairs) >= max_recursive_joins:
                truncated = True
                break
            attempted_pairs.add(pair)
            joined = recursive_surface_join(left, right, max_no_typed_meet=max_no_typed_meet)
            for level, count in (joined.get("residual_summary") or {}).items():
                residual_reasons[str(level)] = residual_reasons.get(str(level), 0) + int(count)
            if joined.get("join_status") == "joined":
                allowed_recursive_surface_ids.add(str(joined.get("surface_id")))
                continue
            blocked += 1
            for reason in surface_blocker_reasons(joined):
                blocked_reasons[reason] = blocked_reasons.get(reason, 0) + 1
        if truncated:
            break
    attempts = len(attempted_pairs)
    allowed = len(allowed_recursive_surface_ids)
    return {
        "budget": max_recursive_joins,
        "max_no_typed_meet": max_no_typed_meet,
        "attempts": attempts,
        "allowed": allowed,
        "blocked": blocked,
        "growth": allowed,
        "truncated": truncated,
        "blocked_ratio": blocked / max(1, attempts),
        "allowed_ratio": allowed / max(1, attempts),
        "residual_reasons": dict(sorted(residual_reasons.items())),
        "blocker_reasons": dict(sorted(blocked_reasons.items())),
    }


def _record_time_value(record: dict[str, Any], field: str) -> Any:
    if field == "event_time":
        return record.get("event_time")
    metadata = record.get("source_metadata") if isinstance(record.get("source_metadata"), dict) else {}
    return record.get(field) or metadata.get(field)


def temporal_width_seconds(records: Sequence[dict[str, Any]], field: str) -> float | None:
    parsed: list[datetime] = []
    for record in records:
        timestamp = parse_event_datetime(_record_time_value(record, field))
        if timestamp is None:
            continue
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)
        parsed.append(timestamp)
    if len(parsed) < 2:
        return 0.0 if parsed else None
    return (max(parsed) - min(parsed)).total_seconds()


def surface_metrics(
    records: Sequence[dict[str, Any]],
    facts: Sequence[dict[str, Any]],
    surfaces: Sequence[dict[str, Any]],
    *,
    window_field: str,
    previous_surface_ids: set[str] | None = None,
    recursive_closure: dict[str, Any] | None = None,
    surface_classifications: dict[str, int] | None = None,
) -> dict[str, Any]:
    join_edges = [edge for surface in surfaces for edge in surface.get("join_edges", []) or []]
    residual_distribution = {level: 0 for level in RESIDUAL_LEVELS}
    blocked_certificate_classes: dict[str, int] = {}
    role_stability_values: list[float] = []
    source_ids: set[str] = set()
    for surface in surfaces:
        for level, count in (surface.get("residual_summary") or {}).items():
            residual_distribution[str(level)] = residual_distribution.get(str(level), 0) + int(count)
        for blocker in surface.get("blockers", []) or []:
            blocked_certificate_classes[str(blocker)] = blocked_certificate_classes.get(str(blocker), 0) + 1
        if surface.get("role_stability") is not None:
            role_stability_values.append(float(surface["role_stability"]))
        source_ids.update(str(value) for value in surface.get("source_feed_ids", []) or [] if value)
    surface_by_fibre = {str(surface.get("fibre_id")): str(surface.get("surface_id")) for surface in surfaces if surface.get("fibre_id") and surface.get("surface_id")}
    surface_pairs = {
        (str(surface.get("surface_id")), surface_by_fibre[str(edge.get("right_fibre_id"))])
        for surface in surfaces
        for edge in surface.get("join_edges", []) or []
        if edge.get("right_fibre_id") and str(edge.get("right_fibre_id")) in surface_by_fibre
    }
    surface_count = len(surfaces)
    possible_edges = surface_count * max(0, surface_count - 1)
    previous_surface_ids = previous_surface_ids or set()
    current_surface_ids = {str(surface.get("surface_id")) for surface in surfaces if surface.get("surface_id")}
    recursive_closure = recursive_closure or {}
    support = adjacency_support_measurements(surfaces, previous_surface_ids=previous_surface_ids)
    component_sizes = connected_component_sizes(surfaces)
    return {
        "documents": len(records),
        "facts": len(facts),
        "fibres": len({str(fact.get("fibre_id")) for fact in facts if fact.get("fibre_id")}),
        "surfaces": surface_count,
        "adjacency_edges": len(join_edges),
        "adjacency_density": len(surface_pairs) / possible_edges if possible_edges else 0.0,
        "edges_per_surface": len(join_edges) / max(1, surface_count),
        "residual_distribution": dict(sorted(residual_distribution.items())),
        "contradiction_mass": residual_distribution.get("CONTRADICTION", 0) / max(1, sum(residual_distribution.values())),
        "role_stability": sum(role_stability_values) / max(1, len(role_stability_values)) if role_stability_values else None,
        "source_diversity": len(source_ids) / max(1, len(records)),
        "temporal_window_width": temporal_width_seconds(records, window_field),
        "surface_persistence": len(current_surface_ids & previous_surface_ids) / max(1, len(previous_surface_ids)) if previous_surface_ids else None,
        "surface_classifications": surface_classifications or {},
        "blocked_certificate_classes": dict(sorted(blocked_certificate_classes.items())),
        "support_measurements": support,
        "same_source_edge_ratio": support["same_source_edge_ratio"],
        "same_source_edge_ratio(n)": support["same_source_edge_ratio(n)"],
        "cross_source_support_ratio": support["cross_source_support_ratio"],
        "cross_source_support_ratio(n)": support["cross_source_support_ratio(n)"],
        "persistent_surface_ratio": support["persistent_surface_ratio"],
        "persistent_surface_ratio(n)": support["persistent_surface_ratio(n)"],
        "local_adjacency_edge_ratio": support["local_adjacency_edge_ratio"],
        "local_adjacency_edge_ratio(n)": support["local_adjacency_edge_ratio(n)"],
        "convergence_witness_ratio": support["convergence_witness_ratio"],
        "convergence_witness_ratio(n)": support["convergence_witness_ratio(n)"],
        "recursive_join_attempts": int(recursive_closure.get("attempts") or 0),
        "recursive_join_allowed": int(recursive_closure.get("allowed") or 0),
        "recursive_join_blocked": int(recursive_closure.get("blocked") or 0),
        "recursive_join_growth": int(recursive_closure.get("growth") or 0),
        "giant_component_ratio": (max(component_sizes) / max(1, surface_count)) if component_sizes else 0.0,
    }


def classify_window(metrics: dict[str, Any], warnings: Sequence[dict[str, Any]], recursive_closure: dict[str, Any]) -> str:
    residual_distribution = metrics.get("residual_distribution") if isinstance(metrics.get("residual_distribution"), dict) else {}
    if int(residual_distribution.get("CONTRADICTION", 0) or 0) > 0:
        return "contradictory"
    if warnings or recursive_closure.get("truncated"):
        return "exploding"
    if metrics.get("surface_persistence") is not None and float(metrics.get("surface_persistence") or 0.0) > 0.0:
        blocked_classes = set((metrics.get("blocked_certificate_classes") or {}).keys())
        if blocked_classes - {"external_promotion_authority_missing"}:
            return "persistent_blocked"
        if float(metrics.get("source_diversity") or 0.0) > 0.0:
            return "persistent_supported"
    return "ephemeral"


def convergence_certificate(*, classification: str, metrics: dict[str, Any], warnings: Sequence[dict[str, Any]], recursive_closure: dict[str, Any]) -> dict[str, Any]:
    return {
        "certificate_type": "candidate_surface_convergence_window",
        "classification": classification,
        "evidence": {
            "warnings": list(warnings),
            "surface_persistence": metrics.get("surface_persistence"),
            "source_diversity": metrics.get("source_diversity"),
            "contradiction_mass": metrics.get("contradiction_mass"),
            "recursive_join_growth": recursive_closure.get("growth"),
            "recursive_join_truncated": recursive_closure.get("truncated"),
        },
        "promotion_authority": False,
        "proof_status": "diagnostic_only",
    }


def counterexample_certificate_from_convergence(certificate: dict[str, Any]) -> dict[str, Any]:
    classification = certificate.get("classification")
    if classification in {"contradictory", "exploding"}:
        status = "counterexample_observed"
    elif classification == "persistent_blocked":
        status = "blocked_persistence_observed"
    else:
        status = "not_observed"
    return {
        "certificate_type": "candidate_surface_counterexample_window",
        "status": status,
        "classification": classification,
        "promotion_authority": False,
        "proof_status": "diagnostic_only",
    }


def explosion_warnings(metrics: dict[str, Any], policy: str, previous_metrics: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    warnings: list[dict[str, Any]] = []
    if policy == "strict_bounded" and float(metrics.get("edges_per_surface") or 0.0) > 16:
        warnings.append({"class": "strict_edges_per_surface", "policy": policy, "threshold": 16, "value": metrics.get("edges_per_surface")})
    if float(metrics.get("giant_component_ratio") or 0.0) > 0.5:
        warnings.append({"class": "giant_component", "policy": policy, "threshold": 0.5, "value": metrics.get("giant_component_ratio")})
    if previous_metrics:
        recursive_growth = float(metrics.get("recursive_join_growth") or 0.0) - float(previous_metrics.get("recursive_join_growth") or 0.0)
        surface_growth = float(metrics.get("surfaces") or 0.0) - float(previous_metrics.get("surfaces") or 0.0)
        if recursive_growth > max(0.0, surface_growth):
            warnings.append({"class": "recursive_growth_exceeds_surface_growth", "policy": policy, "threshold": "surface_count_growth", "value": recursive_growth, "surface_growth": surface_growth})
    return warnings
