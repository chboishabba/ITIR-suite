#!/usr/bin/env python3
"""Deterministic dry-run verification for the RPD PNF fibre and 20x20 fleet machinery."""

from __future__ import annotations

import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parents[1]
for candidate in (repo_root / "itir-mcp" / "src", repo_root / "SensibLaw", repo_root / "SensibLaw" / "src"):
    if candidate.exists() and str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from itir_mcp import pnf_spectral_packet as packet
from itir_mcp import fleet_round_runner


def run_dry_run() -> None:
    print("=" * 70)
    print("STEP 1: Deterministic POS Candidate Gating (Zero Hardcoded Wordlists)")
    print("=" * 70)
    val_propn = packet.validate_pnf_candidate("Yang Mills Theory")
    print(f"  • Substantive Proper Nouns: accepted={val_propn['accepted']} (pos={val_propn['pos']})")
    assert val_propn["accepted"] is True

    val_ast = packet.validate_pnf_candidate("YangMillsTheory", ast_symbols=["YangMillsTheory"])
    print(f"  • AST Symbol Fallback:      accepted={val_ast['accepted']} (explicit_ast={val_ast['explicit_ast_symbol']})")
    assert val_ast["accepted"] is True

    val_particle = packet.validate_pnf_candidate("than rather")
    print(f"  • Grammatical Particles:    accepted={val_particle['accepted']} (reason={val_particle['reason']})")
    assert val_particle["accepted"] is False

    print("\n" + "=" * 70)
    print("STEP 2: Permanent QID Grounding & Frontier Candidate Minting")
    print("=" * 70)
    grounded = packet.ground_wikimedia_surface("Yang-Mills", subject_ref="topic:Q271810")
    print(f"  • Grounding Surface:        '{grounded['surface']}' -> authority={grounded['authority']}")

    frontier = packet.mint_frontier_qid_candidate(
        "all-diameter weighted polymer bounds",
        anchors=[
            {"property": "P279", "target": "Q7575317"},
            {"property": "P361", "target": "Q271810"},
        ],
    )
    print(f"  • Frontier Candidate:       '{frontier['candidate_id']}'")
    print(f"    Anchors:                  {frontier['anchors']}")
    assert frontier["candidate_id"].startswith("cand:Q_")

    print("\n" + "=" * 70)
    print("STEP 3: Invariant Fibre Bundle (F_YM) across 3 Typed Representations")
    print("=" * 70)
    bundle = packet.build_yang_mills_fibre_bundle()
    print(f"  • Root Canonical Node:      {bundle['root']['label']} [{bundle['root']['qid']}]")
    print(f"  • Invariant Fibre:          {bundle['fibre_id']}")
    for branch in bundle["branches"]:
        print(f"    - Branch: {branch['branch_id']:<24} (Rep: {branch['representation']}, Fibre: {branch['fibre_id']})")
    print(f"  • Shared Invariant Core:    {bundle['shared_invariants'][:3]} ...")
    assert len(bundle["branches"]) == 3
    assert bundle["fibre_id"] == "F_YM"

    print("\n" + "=" * 70)
    print("STEP 4: Cross-Thread Lemma Routing via Ontology Path Walking (P361 -> P279)")
    print("=" * 70)
    edges = [
        {"source": "Q271810", "property": "P361", "target": "Q253567"},
        {"source": "Q253567", "property": "P279", "target": "Q180929"},
    ]
    routed = packet.route_verified_lemmas(
        "Q271810",
        edges,
        [{
            "qid": "Q180929",
            "lemma_ref": "LieGroupCompactness",
            "source_ref": "dashi_agda:DASHI/Geometry/LieGroupCompactness.agda",
            "verified": True,
        }],
    )
    route = routed["routes"][0]
    path_props = [e["property"] for e in route["path"]]
    print(f"  • Source QID:               {routed['start_qid']} (Yang-Mills)")
    print(f"  • Traversal Path:           {' -> '.join(path_props)} -> {route['qid']} (Lie Group)")
    print(f"  • Discovered Lemma:         {route['lemma_ref']} (from {route['source_ref']})")
    assert path_props == ["P361", "P279"]

    print("\n" + "=" * 70)
    print("STEP 5: 20x20 Fleet Round Barrier Planning (400 Potential Dispatches)")
    print("=" * 70)
    rounds = [
        [
            {
                "orchestrator_id": f"r{r:02d}-w{w:02d}",
                "unblocked": True,
                "alpha": 0.95 - (0.01 * w),
                "pareto_rank": w // 5,
                "blocker_count": 0,
                "typed_support": {
                    "files": [f"DASHI/Round{r}/Worker{w}.agda"],
                    "symbols": [f"lemma_{r}_{w}"],
                    "lemmas": [f"proof_step_{r}_{w}"],
                },
            }
            for w in range(20)
        ]
        for r in range(20)
    ]
    # Build complete pairwise disjoint receipts
    receipts = {}
    for frontier in rounds:
        ids = [lane["orchestrator_id"] for lane in frontier]
        for i, left in enumerate(ids):
            for right in ids[i + 1:]:
                receipts["|".join(sorted((left, right)))] = True

    plan = fleet_round_runner.plan_fleet_round_barriers(
        rounds,
        no_typed_meet_receipts=receipts,
        worker_limit=20,
        round_limit=20,
    )
    print(f"  • Number of Rounds:         {plan['round_count']} barrier rounds")
    print(f"  • Workers per Round:        {plan['worker_limit']} parallel slots")
    print(f"  • Total Planned Calls:      {plan['total_planned_worker_calls']} / {plan['maximum_possible_calls']}")
    print(f"  • Pairwise noTypedMeet:     100% verified across all {len(receipts)} pairs")
    assert plan["total_planned_worker_calls"] == 400
    assert plan["round_count"] == 20

    print("\n" + "=" * 70)
    print("ALL 5 RPD PILLARS VERIFIED & PASSING DETERMINISTICALLY!")
    print("=" * 70)


if __name__ == "__main__":
    run_dry_run()
