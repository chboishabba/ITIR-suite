"""Deterministic fleet-round planning; this module does not dispatch workers."""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

VERSION = "itir.ao.fleet_round_plan.v1"
MAX_WORKERS = 20
MAX_ROUNDS = 20
SUPPORT_KINDS = ("files", "symbols", "lemmas")


def _support(goal: Mapping[str, Any]) -> dict[str, set[str]]:
    value = goal.get("typed_support")
    if not isinstance(value, Mapping):
        return {kind: set() for kind in SUPPORT_KINDS}
    return {kind: {str(x) for x in value.get(kind, [])}
            if isinstance(value.get(kind, []), list) else set()
            for kind in SUPPORT_KINDS}


def _pair_key(left: str, right: str) -> str:
    return "|".join(sorted((left, right)))


def build_fleet_round_plan(
    rounds: Sequence[Sequence[Mapping[str, Any]]],
    *,
    no_typed_meet_receipts: Mapping[str, Any],
    worker_limit: int = MAX_WORKERS,
    round_limit: int = MAX_ROUNDS,
) -> dict[str, Any]:
    """Plan up to R simultaneous tranches; each pair needs an explicit proof receipt.

    Receipt keys are canonical sorted IDs joined by '|'; values must be exactly
    True. Any overlapping typed support blocks the pair even with a receipt.
    """
    if type(worker_limit) is not int or not 1 <= worker_limit <= MAX_WORKERS:
        raise ValueError("worker_limit must be in 1..20")
    if type(round_limit) is not int or not 1 <= round_limit <= MAX_ROUNDS:
        raise ValueError("round_limit must be in 1..20")
    if not isinstance(no_typed_meet_receipts, Mapping):
        raise ValueError("no_typed_meet_receipts must be a mapping")
    if not isinstance(rounds, Sequence):
        raise ValueError("rounds must be a sequence")
    plan = []
    total_lanes = 0
    for round_index, goals in enumerate(rounds[:round_limit], start=1):
        if not isinstance(goals, Sequence):
            raise ValueError("each round frontier must be a sequence")
        eligible = []
        seen = set()
        for goal in goals:
            if not isinstance(goal, Mapping):
                raise ValueError("goal must be a mapping")
            goal_id = goal.get("id")
            if not isinstance(goal_id, str) or not goal_id.strip() or goal_id in seen:
                raise ValueError("each goal needs a unique nonempty id per round")
            seen.add(goal_id)
            if goal.get("blocked") is True or goal.get("unblocked") is False:
                continue
            eligible.append(goal)
        # Stable Pareto proxy: alpha descending, blocker count ascending, id ascending.
        eligible.sort(key=lambda g: (-float(g.get("alpha", 0.0)),
                                     int(g.get("blocker_count", 0)), str(g["id"])))
        selected = []
        held = []
        for goal in eligible:
            if len(selected) >= worker_limit:
                held.append({"id": goal["id"], "reason": "worker_capacity"})
                continue
            support = _support(goal)
            conflict = None
            for other in selected:
                other_support = _support(other)
                overlap = [kind for kind in SUPPORT_KINDS
                           if support[kind] & other_support[kind]]
                key = _pair_key(str(goal["id"]), str(other["id"]))
                if overlap:
                    conflict = {"with": other["id"], "reason": "typed_support_overlap",
                                "support_kinds": overlap}
                    break
                if no_typed_meet_receipts.get(key) is not True:
                    conflict = {"with": other["id"], "reason": "missing_noTypedMeet_proof"}
                    break
            if conflict:
                held.append({"id": goal["id"], **conflict})
            else:
                selected.append(goal)
        lanes = [{"slot": i, "goal_id": str(goal["id"])} for i, goal in enumerate(selected, 1)]
        total_lanes += len(lanes)
        plan.append({"round": round_index, "lanes": lanes,
                     "selected_count": len(lanes), "held": held,
                     "frontier_count": len(eligible)})
    return {
        "version": VERSION,
        "round_count": len(plan),
        "worker_limit": worker_limit,
        "total_planned_worker_calls": total_lanes,
        "maximum_possible_calls": len(plan) * worker_limit,
        "rounds": plan,
        "dispatch_performed": False,
        "authority": "plan_only",
    }
