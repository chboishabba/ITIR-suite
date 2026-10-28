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


def build_pareto_conductor_plan(
    hierarchy: Mapping[str, Any],
    worker_capacity: int,
    *,
    candidate_lanes: Mapping[str, Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build an AO conductor plan from the continuous hierarchy.

    W <= 10 uses primary-roll mode. W == 20 branches subtopics. Intermediate
    capacities use adaptive subtopic mode. All modes expose the continuous
    threshold selected by the same capacity-aware spectral scheduler.
    """
    if isinstance(worker_capacity, bool) or not isinstance(worker_capacity, int):
        raise ValueError("worker_capacity must be an integer")
    if worker_capacity < 1 or worker_capacity > 20:
        raise ValueError("worker_capacity must be within [1, 20]")

    allocation = allocate_hierarchical_spectral_workers(
        hierarchy,
        worker_capacity,
        parallel_admissibility=None,
    )
    thresholds = hierarchy.get("thresholds")
    threshold_map = thresholds if isinstance(thresholds, Mapping) else {}
    primary_tau = float(threshold_map.get("primary_tau", allocation["selected_tau"]))
    subtopic_tau = float(threshold_map.get("subtopic_tau", allocation["selected_tau"]))

    if worker_capacity <= 10:
        mode = "primary_roll"
        topics = _hierarchy_topics(hierarchy, "primary_topics")
        conductor_tau = max(float(allocation["selected_tau"]), primary_tau)
    elif worker_capacity == 20:
        mode = "independent_subtopics"
        topics = _hierarchy_topics(hierarchy, "subtopics")
        conductor_tau = subtopic_tau
    else:
        mode = "adaptive_subtopics"
        topics = _hierarchy_topics(hierarchy, "subtopics")
        fraction = float(worker_capacity - 10) / 10.0
        conductor_tau = primary_tau - fraction * (primary_tau - subtopic_tau)

    ordered_topics = _pareto_order_topic_rows(topics)
    selected_topics = ordered_topics[:worker_capacity]
    deferred_topics = ordered_topics[worker_capacity:]
    subtopics = _hierarchy_topics(hierarchy, "subtopics")
    subtopics_by_primary: dict[str, list[dict[str, Any]]] = {}
    for subtopic in subtopics:
        subtopics_by_primary.setdefault(str(subtopic.get("parent_id") or ""), []).append(subtopic)
    for rows in subtopics_by_primary.values():
        rows.sort(
            key=lambda topic: (
                int(topic.get("pareto_rank", 0)),
                -float(_topic_alpha(topic).get("mean", 0.0)),
                str(topic.get("topic_id") or ""),
            )
        )

    prepared_lanes: list[dict[str, Any]] = []
    missing_lane_topics: list[str] = []
    lane_map = candidate_lanes if isinstance(candidate_lanes, Mapping) else {}
    for topic in selected_topics:
        topic_id = str(topic.get("topic_id") or "")
        raw_lane = lane_map.get(topic_id)
        if not isinstance(raw_lane, Mapping):
            missing_lane_topics.append(topic_id)
            continue
        lane = dict(raw_lane)
        lane["topic_id"] = topic_id
        lane["topic_name"] = str(topic.get("name") or topic_id)
        lane["alpha"] = _topic_alpha(topic)
        lane["pareto_rank"] = int(topic.get("pareto_rank", 0))

        internal_packets: list[dict[str, Any]] = []
        if mode == "primary_roll":
            children = subtopics_by_primary.get(topic_id, [])
            for sequence, child in enumerate(_pareto_order_topic_rows(children)):
                internal_packets.append(
                    {
                        "sequence": sequence,
                        "topic_id": str(child.get("topic_id") or ""),
                        "topic_name": str(child.get("name") or child.get("topic_id") or ""),
                        "alpha": _topic_alpha(child),
                    }
                )
        lane["internal_work_packets"] = internal_packets
        lane["conductor_mode"] = mode
        lane["selected_tau"] = conductor_tau
        lane["prompt"] = _pareto_lane_prompt(lane, internal_packets)
        prepared_lanes.append(lane)

    no_typed_meet_verified = False
    verification_error: str | None = None
    if prepared_lanes:
        try:
            _verify_pairwise_no_typed_meet(prepared_lanes)
            no_typed_meet_verified = True
        except ValueError as exc:
            verification_error = str(exc)

    if mode == "independent_subtopics" and prepared_lanes and not no_typed_meet_verified:
        dispatchable_lanes: list[dict[str, Any]] = []
    else:
        dispatchable_lanes = prepared_lanes if no_typed_meet_verified else []

    return {
        "schema": "itir.ao.pnf_pareto_conductor.v1",
        "worker_capacity": worker_capacity,
        "mode": mode,
        "selected_tau": conductor_tau,
        "spectral_resolution": allocation["resolution"],
        "selected_topic_count": len(selected_topics),
        "prepared_lane_count": len(prepared_lanes),
        "dispatchable_lane_count": len(dispatchable_lanes),
        "capacity_cut_tau": float(allocation["selected_tau"]),
        "selected_topics": [
            {
                "topic_id": str(topic.get("topic_id") or ""),
                "name": str(topic.get("name") or topic.get("topic_id") or ""),
                "alpha": _topic_alpha(topic),
                "pareto_rank": int(topic.get("pareto_rank", 0)),
            }
            for topic in selected_topics
        ],
        "deferred_topics": [
            {
                "topic_id": str(topic.get("topic_id") or ""),
                "name": str(topic.get("name") or topic.get("topic_id") or ""),
                "alpha": _topic_alpha(topic),
                "pareto_rank": int(topic.get("pareto_rank", 0)),
            }
            for topic in deferred_topics
        ],
        "lanes": dispatchable_lanes,
        "missing_lane_topics": missing_lane_topics,
        "pairwise_noTypedMeet_verified": no_typed_meet_verified,
        "verification_error": verification_error,
        "allocation": allocation,
        "policy": {
            "max_workers": 20,
            "constrained_primary_roll_at_or_below": 10,
            "expanded_independent_subtopics_at": 20,
            "continuous_tau_controls_discrete_concurrency": True,
            "alpha_pareto_order_is_strict": True,
            "parallel_requires_pairwise_noTypedMeet": True,
            "dispatch_uses_existing_exactly_once_transport": True,
        },
    }


def _hierarchy_topics(hierarchy: Mapping[str, Any], key: str) -> list[dict[str, Any]]:
    raw = hierarchy.get(key)
    if not isinstance(raw, Sequence) or isinstance(raw, (str, bytes, bytearray)):
        raise ValueError(f"hierarchy requires {key}")
    return [dict(topic) for topic in raw if isinstance(topic, Mapping)]


def _topic_alpha(topic: Mapping[str, Any]) -> dict[str, float]:
    raw = topic.get("alpha")
    alpha = raw if isinstance(raw, Mapping) else {}
    return {
        "mean": float(alpha.get("mean", 0.0)),
        "max": float(alpha.get("max", 0.0)),
        "spectral_energy_mean": float(alpha.get("spectral_energy_mean", 0.0)),
        "theorem_density_mean": float(alpha.get("theorem_density_mean", 0.0)),
        "formal_gap_reduction_mean": float(alpha.get("formal_gap_reduction_mean", 0.0)),
    }


def _pareto_order_topic_rows(topics: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    rows = [dict(topic) for topic in topics]
    pseudo_components = [
        {
            "component_id": str(topic.get("topic_id") or f"topic-{index:03d}"),
            "alpha": _topic_alpha(topic),
        }
        for index, topic in enumerate(rows)
    ]
    layers = _pareto_layers(pseudo_components) if pseudo_components else []
    rank: dict[str, int] = {}
    for layer_index, layer in enumerate(layers):
        for topic_id in layer:
            rank[topic_id] = layer_index
    for topic in rows:
        topic_id = str(topic.get("topic_id") or "")
        topic["pareto_rank"] = rank.get(topic_id, len(layers))
    return sorted(
        rows,
        key=lambda topic: (
            int(topic.get("pareto_rank", 0)),
            -_topic_alpha(topic)["mean"],
            -_topic_alpha(topic)["spectral_energy_mean"],
            str(topic.get("topic_id") or ""),
        ),
    )


def _pareto_lane_prompt(
    lane: Mapping[str, Any],
    internal_packets: Sequence[Mapping[str, Any]],
) -> str:
    base = str(lane.get("prompt") or lane.get("lane_claim") or "").strip()
    if not base:
        raise ValueError("candidate lane requires prompt or lane_claim")
    if not internal_packets:
        return base
    packet_lines = [
        "",
        "AO conductor internal work packets. Execute in this order within this worker turn:",
    ]
    for packet in internal_packets:
        packet_lines.append(
            f"{int(packet['sequence']) + 1}. {packet['topic_id']} — {packet['topic_name']}"
        )
    return base + "\n" + "\n".join(packet_lines)


def execute_pareto_conductor(
    hierarchy: Mapping[str, Any],
    worker_capacity: int,
    candidate_lanes: Mapping[str, Mapping[str, Any]],
    workers: Sequence[Any],
    *,
    db_path: str | Path | None = None,
    dispatch: bool = False,
) -> dict[str, Any]:
    plan = build_pareto_conductor_plan(
        hierarchy,
        worker_capacity,
        candidate_lanes=candidate_lanes,
    )
    if not dispatch:
        return {"plan": plan, "dispatch": None}
    lanes = plan["lanes"]
    if not lanes:
        raise ValueError(
            plan.get("verification_error")
            or "no pairwise-noTypedMeet-verified lanes are dispatchable"
        )
    worker_rows = list(workers)
    if len(worker_rows) < len(lanes):
        raise ValueError("workers must provide at least one worker per dispatchable lane")
    dispatch_receipt = spawn_parallel_lanes(
        lanes,
        worker_rows[: len(lanes)],
        db_path=db_path,
    )
    return {
        "plan": plan,
        "dispatch": dispatch_receipt,
    }

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
