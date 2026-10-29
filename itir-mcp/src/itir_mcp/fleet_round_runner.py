"""Fleet Round Runner for executing governed convergence rounds across active cluster leads."""

from __future__ import annotations

import logging
import math
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Mapping, Sequence

from re_gpt.fleet import FleetOrchestrator
from re_gpt.mcp_server import chatgpt_continue, chatgpt_view

from .pnf_spectral_packet import spectral_no_typed_meet

logger = logging.getLogger(__name__)

CONVERGENCE_PROMPT = """@converge_toe @max_cut @grug_ste100 @zkp_qa

Continue per max-cut and converge toward DASHI TOE (`DASHI/EverythingTOESymmetryResolved369.agda` and `DASHI/Unifier.agda`).
- Assume everything we need already exists in-repo across `dashi_agda`, `casey-git-clone`, `zkSEC`, and meta-introspector repos (`zkperf`, `zos-server`, `erdfa-py`, `aristotle-cli-rs`).
- Search first for existing/duplicate constructions via code search / preflight before writing any new code.
- Reconcile with latest PRs (#1266 / #1271 / #1241 / #1249).
- Strict constraint: DO NOT touch ESD surfaces (`dashi_digital_esd`, `*digital_esd*`, `*ESD*`); import only.
- Preserve attribution for meta-introspector repos.
"""


def _load_lane_planner(repo_root: Path):
    statibaker_root = repo_root / "StatiBaker"
    if not statibaker_root.exists():
        raise FileNotFoundError(f"StatiBaker submodule is unavailable: {statibaker_root}")
    root_text = str(statibaker_root)
    if root_text not in sys.path:
        sys.path.insert(0, root_text)
    from sb.ao_kanboard_control import compute_dynamic_lane_descent as planner

    return planner


def compute_dynamic_lane_descent(repo_root: str | Path) -> dict[str, Any]:
    """Delegate AO leaf planning to the canonical StatiBaker TODO graph surface."""
    root = Path(repo_root).expanduser().resolve()
    return _load_lane_planner(root)(root)


def _lane_support_keys(lane: Mapping[str, Any]) -> set[str]:
    receipt = lane.get("noTypedMeet")
    if isinstance(receipt, Mapping):
        keys = receipt.get("support_keys")
        if isinstance(keys, list):
            return {str(item).strip() for item in keys if str(item).strip()}

    support = lane.get("typed_support")
    if not isinstance(support, Mapping):
        return set()
    out: set[str] = set()
    for kind in ("files", "symbols", "lemmas"):
        values = support.get(kind)
        if not isinstance(values, list):
            continue
        for value in values:
            clean = str(value).strip()
            if clean:
                out.add(f"{kind}:{clean}")
    return out


def _verify_pairwise_no_typed_meet(lanes: Sequence[Mapping[str, Any]]) -> None:
    occupied: dict[str, str] = {}
    lane_rows = [dict(lane) for lane in lanes]
    for lane in lane_rows:
        lane_id = str(lane.get("orchestrator_id") or lane.get("lane") or "").strip()
        if not lane_id:
            raise ValueError("Every lane requires orchestrator_id or lane")
        keys = _lane_support_keys(lane)
        if not keys:
            raise ValueError(f"Lane {lane_id} has no concrete typed support")
        for key in sorted(keys):
            prior = occupied.get(key)
            if prior is not None:
                raise ValueError(f"noTypedMeet violation: {lane_id} collides with {prior} on {key}")
            occupied[key] = lane_id

    for index, left in enumerate(lane_rows):
        left_id = str(left.get("orchestrator_id") or left.get("lane") or "").strip()
        for right in lane_rows[index + 1 :]:
            right_id = str(right.get("orchestrator_id") or right.get("lane") or "").strip()
            receipt = spectral_no_typed_meet(left, right)
            if not receipt["admissible"]:
                raise ValueError(
                    "spectral noTypedMeet violation: "
                    f"{left_id} and {right_id} share quotient geometry "
                    f"(cosine={receipt['cosine_similarity']:.6f}, "
                    f"defect={receipt['defect_status']})"
                )


def _worker_conversation_id(worker: Any) -> str:
    if isinstance(worker, str):
        cid = worker.strip()
    elif isinstance(worker, Mapping):
        cid = str(worker.get("conversation_id") or "").strip()
    else:
        cid = ""
    if not cid:
        raise ValueError("Each worker must provide a non-empty conversation_id")
    return cid


def _dispatch_fast_lane(
    orchestrator: FleetOrchestrator,
    lane: Mapping[str, Any],
    conversation_id: str,
) -> dict[str, Any]:
    prompt = str(lane.get("prompt") or lane.get("lane_claim") or "").strip()
    if not prompt:
        raise ValueError("Each lane requires a non-empty prompt or lane_claim")
    result = chatgpt_continue(
        conversation_id=conversation_id,
        prompt=prompt,
        follow=False,
        write_transport="async",
        dom_fallback=False,
        db_path=str(orchestrator.db_path),
        reconcile_attempts=0,
    )
    return {
        "lane": str(lane.get("lane") or ""),
        "orchestrator_id": str(lane.get("orchestrator_id") or ""),
        "conversation_id": conversation_id,
        "operation": result,
        "policy": {
            "write_transport": "async",
            "dom_fallback": False,
            "follow": False,
            "reconcile_attempts": 0,
            "automatic_resend": False,
        },
    }


def spawn_parallel_lanes(
    lanes: Sequence[Mapping[str, Any]],
    workers: Sequence[Any],
    *,
    db_path: str | Path | None = None,
) -> dict[str, Any]:
    """Dispatch one independent AO lane per explicit Fleet worker in fast mode."""
    lane_rows = [dict(lane) for lane in lanes]
    worker_rows = list(workers)
    if not lane_rows:
        return {"lane_count": 0, "results": [], "policy": {"pairwise_noTypedMeet": True}}
    if len(lane_rows) != len(worker_rows):
        raise ValueError("lanes and workers must have equal length for one-lane-per-worker dispatch")

    _verify_pairwise_no_typed_meet(lane_rows)
    conversation_ids = [_worker_conversation_id(worker) for worker in worker_rows]
    if len(set(conversation_ids)) != len(conversation_ids):
        raise ValueError("Each parallel lane requires a distinct worker conversation_id")

    orchestrator = FleetOrchestrator(db_path=db_path) if db_path is not None else FleetOrchestrator()
    ordered_results: list[dict[str, Any] | None] = [None] * len(lane_rows)
    with ThreadPoolExecutor(max_workers=len(lane_rows)) as executor:
        future_to_index = {
            executor.submit(_dispatch_fast_lane, orchestrator, lane, conversation_ids[index]): index
            for index, lane in enumerate(lane_rows)
        }
        for future in as_completed(future_to_index):
            index = future_to_index[future]
            try:
                ordered_results[index] = future.result()
            except Exception as exc:
                lane = lane_rows[index]
                ordered_results[index] = {
                    "lane": str(lane.get("lane") or ""),
                    "orchestrator_id": str(lane.get("orchestrator_id") or ""),
                    "conversation_id": conversation_ids[index],
                    "state": "error",
                    "error": str(exc),
                }

    return {
        "lane_count": len(lane_rows),
        "results": [row for row in ordered_results if row is not None],
        "policy": {
            "pairwise_noTypedMeet": True,
            "one_lane_per_worker": True,
            "write_transport": "async",
            "dom_fallback": False,
            "follow": False,
            "reconcile_attempts": 0,
            "automatic_resend": False,
        },
    }



def allocate_hierarchical_spectral_workers(
    hierarchy: Mapping[str, Any],
    worker_capacity: int,
    *,
    parallel_admissibility: Mapping[str, bool] | None = None,
) -> dict[str, Any]:
    """Map a continuous spectral hierarchy onto bounded discrete worker slots.

    The selected threshold is the smallest MST cut that produces no more than
    worker_capacity components. Increasing the threshold can only merge
    components, so reduced capacity deterministically coarsens the quotient.
    """
    if isinstance(worker_capacity, bool) or not isinstance(worker_capacity, int) or worker_capacity < 1:
        raise ValueError("worker_capacity must be a positive integer")
    rows = hierarchy.get("conversation_rows")
    mst_edges = hierarchy.get("mst_edges")
    thresholds = hierarchy.get("thresholds")
    if not isinstance(rows, Sequence) or isinstance(rows, (str, bytes, bytearray)) or not rows:
        raise ValueError("hierarchy requires conversation_rows")
    if not isinstance(mst_edges, Sequence) or isinstance(mst_edges, (str, bytes, bytearray)):
        raise ValueError("hierarchy requires mst_edges")
    if not isinstance(thresholds, Mapping):
        raise ValueError("hierarchy requires thresholds")

    alpha_by_conversation: dict[str, dict[str, float]] = {}
    conversation_ids: list[str] = []
    for row in rows:
        if not isinstance(row, Mapping):
            raise ValueError("conversation_rows entries must be objects")
        conversation_id = str(row.get("conversation_id") or "").strip()
        if not conversation_id:
            raise ValueError("conversation row requires conversation_id")
        conversation_ids.append(conversation_id)
        alpha_by_conversation[conversation_id] = {
            "alpha": float(row.get("alpha", 0.0)),
            "spectral_energy": float(row.get("spectral_energy", 0.0)),
            "theorem_density": float(row.get("theorem_density", 0.0)),
            "formal_gap_reduction": float(row.get("formal_gap_reduction", 0.0)),
        }
    conversation_ids = sorted(set(conversation_ids))

    capacity_tau = _capacity_threshold_from_mst(
        conversation_count=len(conversation_ids),
        mst_edges=mst_edges,
        worker_capacity=worker_capacity,
    )
    fibre_floor = float(thresholds.get("fibre_tau", 0.0))
    tau = max(capacity_tau, fibre_floor)
    components = _mst_components_at_threshold(conversation_ids, mst_edges, tau)
    component_rows = [
        _scheduled_component_summary(index, members, alpha_by_conversation)
        for index, members in enumerate(components)
    ]
    pareto_layers = _pareto_layers(component_rows)
    pareto_rank: dict[str, int] = {}
    for rank, layer in enumerate(pareto_layers):
        for component_id in layer:
            pareto_rank[component_id] = rank
    for component in component_rows:
        component["pareto_rank"] = pareto_rank[component["component_id"]]

    ordered = sorted(
        component_rows,
        key=lambda component: (
            component["pareto_rank"],
            -component["alpha"]["mean"],
            -component["alpha"]["spectral_energy_mean"],
            component["component_id"],
        ),
    )

    selected: list[dict[str, Any]] = []
    rolled: list[dict[str, Any]] = []
    explicit_pair_checks = parallel_admissibility is not None
    for component in ordered:
        conflict_target: dict[str, Any] | None = None
        if selected and parallel_admissibility is not None:
            for prior in selected:
                key = _component_pair_key(prior["component_id"], component["component_id"])
                if parallel_admissibility.get(key) is not True:
                    conflict_target = prior
                    break
        if conflict_target is not None:
            rolled.append(
                {
                    "component_id": component["component_id"],
                    "rolled_into": conflict_target["component_id"],
                    "reason": "noTypedMeet_not_admitted",
                    "members": component["members"],
                }
            )
            conflict_target.setdefault("internal_work_packets", []).append(component["component_id"])
            continue
        selected.append(component)

    primary_tau = float(thresholds.get("primary_tau", tau))
    subtopic_tau = float(thresholds.get("subtopic_tau", tau))
    fibre_tau = float(thresholds.get("fibre_tau", tau))
    if tau >= primary_tau - 1e-15:
        resolution = "primary_or_coarser"
    elif tau >= subtopic_tau - 1e-15:
        resolution = "subtopic"
    elif tau >= fibre_tau - 1e-15:
        resolution = "fibre"
    else:
        resolution = "conversation_fine"

    worker_slots = []
    for slot, component in enumerate(selected[:worker_capacity]):
        worker_slots.append(
            {
                "worker_slot": slot,
                "component_id": component["component_id"],
                "members": component["members"],
                "alpha": component["alpha"],
                "pareto_rank": component["pareto_rank"],
                "internal_work_packets": component.get("internal_work_packets", []),
                "parallel_dispatch_authorized": explicit_pair_checks,
                "requires_noTypedMeet_check": not explicit_pair_checks,
            }
        )

    return {
        "schema": "itir.ao.hierarchical_spectral_worker_allocation.v1",
        "worker_capacity": worker_capacity,
        "selected_tau": tau,
        "resolution": resolution,
        "component_count_before_noTypedMeet": len(component_rows),
        "worker_slot_count": len(worker_slots),
        "worker_slots": worker_slots,
        "rolled_components": rolled,
        "pareto_fronts": pareto_layers,
        "policy": {
            "threshold_increases_when_capacity_decreases": True,
            "quotient_coarsening_is_monotone": True,
            "alpha_is_priority_not_authority": True,
            "parallel_requires_explicit_noTypedMeet": True,
            "parallel_admissibility_supplied": explicit_pair_checks,
        },
    }


def _capacity_threshold_from_mst(
    *,
    conversation_count: int,
    mst_edges: Sequence[Any],
    worker_capacity: int,
) -> float:
    if worker_capacity >= conversation_count:
        return 0.0
    edges = sorted(
        (
            float(edge["distance"])
            for edge in mst_edges
            if isinstance(edge, Mapping) and isinstance(edge.get("distance"), (int, float))
        )
    )
    required_merges = conversation_count - worker_capacity
    if required_merges <= 0:
        return 0.0
    if required_merges > len(edges):
        return max(edges, default=0.0)
    return edges[required_merges - 1]


def _mst_components_at_threshold(
    conversation_ids: Sequence[str],
    mst_edges: Sequence[Any],
    tau: float,
) -> list[list[str]]:
    parent = {conversation_id: conversation_id for conversation_id in conversation_ids}

    def find(value: str) -> str:
        while parent[value] != value:
            parent[value] = parent[parent[value]]
            value = parent[value]
        return value

    def union(left: str, right: str) -> None:
        left_root = find(left)
        right_root = find(right)
        if left_root == right_root:
            return
        if left_root < right_root:
            parent[right_root] = left_root
        else:
            parent[left_root] = right_root

    for edge in sorted(
        (edge for edge in mst_edges if isinstance(edge, Mapping)),
        key=lambda edge: (float(edge.get("distance", 0.0)), str(edge.get("left")), str(edge.get("right"))),
    ):
        distance = float(edge.get("distance", math.inf))
        if distance > tau + 1e-15:
            break
        left = str(edge.get("left") or "")
        right = str(edge.get("right") or "")
        if left in parent and right in parent:
            union(left, right)

    groups: dict[str, list[str]] = {}
    for conversation_id in sorted(conversation_ids):
        groups.setdefault(find(conversation_id), []).append(conversation_id)
    return sorted((sorted(group) for group in groups.values()), key=lambda group: (group[0], len(group)))


def _scheduled_component_summary(
    index: int,
    members: Sequence[str],
    alpha_rows: Mapping[str, Mapping[str, float]],
) -> dict[str, Any]:
    metrics = {
        key: [float(alpha_rows[member][key]) for member in members]
        for key in ("alpha", "spectral_energy", "theorem_density", "formal_gap_reduction")
    }
    return {
        "component_id": f"allocation-{index:03d}",
        "members": sorted(members),
        "member_count": len(members),
        "alpha": {
            "mean": sum(metrics["alpha"]) / len(members),
            "max": max(metrics["alpha"]),
            "spectral_energy_mean": sum(metrics["spectral_energy"]) / len(members),
            "theorem_density_mean": sum(metrics["theorem_density"]) / len(members),
            "formal_gap_reduction_mean": sum(metrics["formal_gap_reduction"]) / len(members),
        },
    }


def _pareto_layers(components: Sequence[Mapping[str, Any]]) -> list[list[str]]:
    remaining = [dict(component) for component in components]
    layers: list[list[str]] = []
    while remaining:
        frontier: list[dict[str, Any]] = []
        for candidate in remaining:
            dominated = any(
                _component_dominates(other, candidate)
                for other in remaining
                if other["component_id"] != candidate["component_id"]
            )
            if not dominated:
                frontier.append(candidate)
        frontier_ids = sorted(str(component["component_id"]) for component in frontier)
        if not frontier_ids:
            frontier_ids = [str(remaining[0]["component_id"])]
        layers.append(frontier_ids)
        frontier_set = set(frontier_ids)
        remaining = [
            component
            for component in remaining
            if str(component["component_id"]) not in frontier_set
        ]
    return layers


def _component_dominates(left: Mapping[str, Any], right: Mapping[str, Any]) -> bool:
    left_alpha = left["alpha"]
    right_alpha = right["alpha"]
    keys = (
        "spectral_energy_mean",
        "theorem_density_mean",
        "formal_gap_reduction_mean",
    )
    left_values = [float(left_alpha[key]) for key in keys]
    right_values = [float(right_alpha[key]) for key in keys]
    return (
        all(left_value >= right_value - 1e-15 for left_value, right_value in zip(left_values, right_values, strict=True))
        and any(left_value > right_value + 1e-15 for left_value, right_value in zip(left_values, right_values, strict=True))
    )


def _component_pair_key(left: str, right: str) -> str:
    first, second = sorted((left, right))
    return f"{first}|{second}"

def execute_fleet_lead_round(*, max_leads: int = 5) -> list[dict[str, Any]]:
    fo = FleetOrchestrator()
    summary = fo.status_summary()
    results = []

    for cluster_id, cluster_data in summary.get("clusters", {}).items():
        if len(results) >= max_leads:
            break
        lead = cluster_data.get("active_lead")
        if not lead:
            continue
        cid = lead["conversation_id"]
        title = lead.get("title", "")
        # Inspect recent turn first to avoid duplicate dispatch if turn is already in-flight
        view = chatgpt_view(cid, tail=1)
        last_msg = (view.get("messages") or [{}])[-1].get("content", "")
        
        results.append({
            "cluster": cluster_id,
            "conversation_id": cid,
            "title": title,
            "message_count": lead.get("message_count", 0),
            "status": "ready",
            "last_message_snippet": last_msg[:120].replace("\n", " "),
        })

    return results

if __name__ == "__main__":
    import json
    print(json.dumps(execute_fleet_lead_round(), indent=2))
