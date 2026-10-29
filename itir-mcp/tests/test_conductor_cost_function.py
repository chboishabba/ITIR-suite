from __future__ import annotations

from itir_mcp.fleet_round_runner import (
    build_pareto_conductor_plan,
    conductor_topic_cost,
)


def _alpha(value: float = 0.8) -> dict[str, float]:
    return {
        "mean": value,
        "max": value,
        "spectral_energy_mean": value,
        "theorem_density_mean": value,
        "formal_gap_reduction_mean": value,
    }


def _hierarchy(topic: dict, subtopics: list[dict] | None = None) -> dict:
    return {
        "conversation_rows": [
            {
                "conversation_id": "c0",
                "alpha": 0.8,
                "spectral_energy": 0.8,
                "theorem_density": 0.8,
                "formal_gap_reduction": 0.8,
            }
        ],
        "mst_edges": [],
        "thresholds": {
            "fibre_tau": 0.0,
            "subtopic_tau": 0.0,
            "primary_tau": 0.0,
        },
        "primary_topics": [topic],
        "subtopics": subtopics or [],
    }


def test_dynamic_cost_function_matches_declared_formula() -> None:
    topic = {
        "topic_id": "topic",
        "alpha": _alpha(0.8),
        "total_goals": 10,
        "unblocked_goals": 5,
        "sub_eigen_dimension": 3,
        "token_cost_per_worker": 0.1,
    }

    receipt = conductor_topic_cost(topic, 4, worker_cap=20)

    assert receipt["unblocked_ratio"] == 0.5
    assert receipt["spectral_width"] == 3
    assert abs(receipt["benefit"] - 1.2) < 1e-12
    assert abs(receipt["token_cost"] - 0.4) < 1e-12
    assert abs(receipt["net_cost"] - 0.8) < 1e-12


def test_frontier_blocked_topic_allocates_exactly_one_worker_per_blocker() -> None:
    topic = {
        "topic_id": "primary-blocked",
        "name": "Blocked proof frontier",
        "alpha": _alpha(),
        "total_goals": 50,
        "unblocked_goals": 46,
        "sub_eigen_dimension": 12,
        "frontier_blockers": [
            {"blocker_id": "lemma:a"},
            {"blocker_id": "lemma:b"},
            {"blocker_id": "lemma:c"},
            {"blocker_id": "lemma:d"},
        ],
    }

    plan = build_pareto_conductor_plan(_hierarchy(topic), 20)

    allocation = plan["worker_allocations"][0]
    assert plan["mode"] == "dynamic_costed"
    assert allocation["shape"] == "frontier_blocked"
    assert allocation["frontier_blocker_count"] == 4
    assert allocation["requested_workers"] == 4
    assert allocation["allocated_workers"] == 4
    assert plan["unused_worker_capacity"] == 16
    assert plan["dispatchable_lane_count"] == 0


def test_sequential_topic_allocates_one_worker_even_with_twenty_available() -> None:
    topic = {
        "topic_id": "primary-sequential",
        "name": "Sequential theorem chain",
        "alpha": _alpha(),
        "total_goals": 8,
        "unblocked_goals": 8,
        "sub_eigen_dimension": 9,
        "execution_kind": "sequential",
    }

    plan = build_pareto_conductor_plan(_hierarchy(topic), 20)

    allocation = plan["worker_allocations"][0]
    assert allocation["shape"] == "sequential"
    assert allocation["requested_workers"] == 1
    assert allocation["allocated_workers"] == 1
    assert plan["unused_worker_capacity"] == 19


def test_parallel_topic_width_tracks_sub_eigen_dimension_not_worker_cap() -> None:
    topic = {
        "topic_id": "primary-parallel",
        "name": "Parallel integration",
        "alpha": _alpha(),
        "total_goals": 12,
        "unblocked_goals": 12,
        "sub_eigen_dimension": 5,
        "execution_kind": "parallel",
    }

    plan = build_pareto_conductor_plan(_hierarchy(topic), 20)

    allocation = plan["worker_allocations"][0]
    assert allocation["shape"] == "parallel"
    assert allocation["sub_eigen_dimension"] == 5
    assert allocation["requested_workers"] == 5
    assert allocation["allocated_workers"] == 5
    assert plan["unused_worker_capacity"] == 15


def test_lower_alpha_subtopics_roll_into_parent_as_ordered_internal_packets() -> None:
    parent = {
        "topic_id": "primary-parent",
        "name": "Parent topic",
        "alpha": _alpha(0.9),
        "execution_kind": "sequential",
    }
    children = [
        {
            "topic_id": "primary-parent.sub-low",
            "parent_id": "primary-parent",
            "name": "Lower alpha",
            "alpha": _alpha(0.2),
        },
        {
            "topic_id": "primary-parent.sub-high",
            "parent_id": "primary-parent",
            "name": "Higher alpha",
            "alpha": _alpha(0.7),
        },
    ]

    plan = build_pareto_conductor_plan(_hierarchy(parent, children), 4)

    packets = plan["worker_allocations"][0]["internal_work_packets"]
    assert [packet["topic_id"] for packet in packets] == [
        "primary-parent.sub-high",
        "primary-parent.sub-low",
    ]
    assert all(packet["preserved"] is True for packet in packets)
    assert all(packet["cross_pollination_parent"] == "primary-parent" for packet in packets)
    assert all(packet["promotion_state"] == "sequenced_internal_work" for packet in packets)
