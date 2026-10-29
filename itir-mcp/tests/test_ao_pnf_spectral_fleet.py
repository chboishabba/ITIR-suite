from __future__ import annotations

import pytest

from itir_mcp.pnf_spectral_packet import classify_pnf_head, validate_pnf_hierarchy_metadata
from itir_mcp.fleet_round_runner import build_fleet_round_plan


@pytest.mark.parametrize("head", [
    "0xffff1000()", "than(rather) · change", "ago · ago(day)",
    "package · satisfy", "support · fp16", "document.querySelector('#app')",
])
def test_low_alpha_noise_is_rejected(head: str) -> None:
    result = classify_pnf_head(head)
    assert result["accepted"] is False
    assert result["authority"] == "none"


@pytest.mark.parametrize("head", [
    "YangMillsMassGap", "NavierStokesTriadKN", "GoemansWilliamsonMaxCut",
    "DeonticObligationCalculus", "DioxusReactiveTree", "E8LatticeMoonshine",
    "BalabanRenormalization",
])
def test_domain_heads_remain_candidate_only(head: str) -> None:
    result = classify_pnf_head(head)
    assert result["accepted"] is True
    assert result["status"] == "candidate_unverified"
    assert result["authority"] == "none"


def test_ontology_and_ast_labels_are_explicit_evidence() -> None:
    assert classify_pnf_head("qxyzontology", ontology_labels=["qxyzontology"])["accepted"]
    assert classify_pnf_head("lemma_foo", ast_symbols=["lemma_foo"])["accepted"]


@pytest.mark.parametrize("k", [50, 100])
def test_hierarchy_has_distinct_levels_without_claiming_spectral_computation(k: int) -> None:
    payload = {"k": k, "eigenspace": [{}], "primary_topics": [], "subtopics": [],
               "fibres": [], "goals": []}
    result = validate_pnf_hierarchy_metadata(payload)
    assert result["k"] == k
    assert result["level_counts"]["eigenspace"] == 1
    assert result["spectral_computation"] == "not_performed"
    assert result["authority"] == "none"


def test_hierarchy_rejects_unsupported_rank() -> None:
    payload = {"k": 8, "eigenspace": [], "primary_topics": [], "subtopics": [],
               "fibres": [], "goals": []}
    with pytest.raises(ValueError, match="50 or 100"):
        validate_pnf_hierarchy_metadata(payload)


def _goal(goal_id: str, alpha: float, symbol: str) -> dict:
    return {"id": goal_id, "alpha": alpha, "blocked": False,
            "typed_support": {"files": ["A.agda"], "symbols": [symbol], "lemmas": []}}


def test_round_means_tranche_and_proof_required_for_pairwise_lanes() -> None:
    goals = [_goal("g1", 0.9, "lemmaA"), _goal("g2", 0.8, "lemmaB")]
    result = build_fleet_round_plan([goals], no_typed_meet_receipts={})
    assert result["round_count"] == 1
    assert result["rounds"][0]["selected_count"] == 1
    assert result["rounds"][0]["held"][0]["reason"] == "typed_support_overlap"


def test_twenty_rounds_allow_up_to_four_hundred_calls() -> None:
    rounds = [[{"id": f"g{r}-{i}", "alpha": 1.0 - i / 100,
                "blocked": False,
                "typed_support": {"files": [f"f{r}-{i}.agda"],
                                  "symbols": [f"s{r}-{i}"], "lemmas": [f"l{r}-{i}"]}}
               for i in range(20)] for r in range(20)]
    receipts = {}
    for goals in rounds:
        for i, left in enumerate(goals):
            for right in goals[i + 1:]:
                receipts["|".join(sorted((left["id"], right["id"])))] = True
    result = build_fleet_round_plan(rounds, no_typed_meet_receipts=receipts)
    assert result["round_count"] == 20
    assert result["total_planned_worker_calls"] == 400
    assert result["maximum_possible_calls"] == 400
    assert all(r["selected_count"] == 20 for r in result["rounds"])
    assert result["dispatch_performed"] is False


def test_blocked_goals_are_not_scheduled_and_round_capacity_is_capped() -> None:
    goals = [{"id": f"g{i}", "alpha": 1, "blocked": i == 0,
              "typed_support": {"files": [f"{i}.agda"], "symbols": [str(i)], "lemmas": []}}
             for i in range(25)]
    result = build_fleet_round_plan([goals], no_typed_meet_receipts={},
                                    worker_limit=20)
    assert result["rounds"][0]["selected_count"] == 20
    assert all(lane["goal_id"] != "g0" for lane in result["rounds"][0]["lanes"])
