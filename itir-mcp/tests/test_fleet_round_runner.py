from __future__ import annotations

from pathlib import Path

import pytest

from itir_mcp import fleet_round_runner


def _lane(name: str, support: str) -> dict:
    return {
        "orchestrator_id": name,
        "lane": f"ao.fleet.dynamic.{name}",
        "lane_claim": f"Implement {name}",
        "prompt": f"Implement {name} and verify it.",
        "typed_support": {"files": [support], "symbols": [], "lemmas": []},
        "noTypedMeet": {
            "pairwise_independent": True,
            "support_keys": [f"files:{support}"],
        },
    }


def test_spawn_parallel_lanes_forces_fast_direct_transport(monkeypatch, tmp_path: Path) -> None:
    calls = []

    class FakeFleetOrchestrator:
        def __init__(self, *, db_path=None):
            self.db_path = Path(db_path) if db_path is not None else tmp_path / "archive.sqlite"

    def fake_continue(**kwargs):
        calls.append(kwargs)
        return {"operation_id": f"op-{kwargs['conversation_id']}", "state": "submission_observed"}

    monkeypatch.setattr(fleet_round_runner, "FleetOrchestrator", FakeFleetOrchestrator)
    monkeypatch.setattr(fleet_round_runner, "chatgpt_continue", fake_continue)

    result = fleet_round_runner.spawn_parallel_lanes(
        [_lane("lane-a", "src/a.py"), _lane("lane-b", "src/b.py")],
        ["conversation-a", {"conversation_id": "conversation-b"}],
        db_path=tmp_path / "archive.sqlite",
    )

    assert result["lane_count"] == 2
    assert [row["conversation_id"] for row in result["results"]] == [
        "conversation-a",
        "conversation-b",
    ]
    assert len(calls) == 2
    for call in calls:
        assert call["follow"] is False
        assert call["write_transport"] == "async"
        assert call["dom_fallback"] is False
        assert call["reconcile_attempts"] == 0
    assert result["policy"]["automatic_resend"] is False
    assert result["policy"]["pairwise_noTypedMeet"] is True


def test_spawn_parallel_lanes_rejects_typed_meet_before_dispatch(monkeypatch) -> None:
    def fail_continue(**kwargs):
        raise AssertionError("dispatch must not run")

    monkeypatch.setattr(fleet_round_runner, "chatgpt_continue", fail_continue)

    with pytest.raises(ValueError, match="noTypedMeet violation"):
        fleet_round_runner.spawn_parallel_lanes(
            [_lane("lane-a", "src/shared.py"), _lane("lane-b", "src/shared.py")],
            ["conversation-a", "conversation-b"],
        )


def test_spawn_parallel_lanes_rejects_duplicate_worker_conversation(monkeypatch) -> None:
    def fail_continue(**kwargs):
        raise AssertionError("dispatch must not run")

    monkeypatch.setattr(fleet_round_runner, "chatgpt_continue", fail_continue)

    with pytest.raises(ValueError, match="distinct worker conversation_id"):
        fleet_round_runner.spawn_parallel_lanes(
            [_lane("lane-a", "src/a.py"), _lane("lane-b", "src/b.py")],
            ["conversation-a", "conversation-a"],
        )


def test_compute_dynamic_lane_descent_delegates_to_statibaker(monkeypatch, tmp_path: Path) -> None:
    expected = {"lane_count": 1, "lanes": [{"orchestrator_id": "lane-a"}]}
    monkeypatch.setattr(
        fleet_round_runner,
        "_load_lane_planner",
        lambda repo_root: lambda root: expected,
    )

    assert fleet_round_runner.compute_dynamic_lane_descent(tmp_path) == expected
