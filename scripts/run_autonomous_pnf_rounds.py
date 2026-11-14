#!/usr/bin/env python3
"""Autonomous PNF Spectral & Dynamic Fleet Wave Conductor.

Implements the user-directed mode:
  AO PNF Leaf -> Pruned PNF Graph + GH Refs -> Headless Fast MCP Worker -> Return -> World Ingestion -> Mathematical Steer
Completes 5 rounds of up to 10 workers across unblocked leaves of the top eigens.
"""

from __future__ import annotations

import collections
import json
from pathlib import Path
import struct
import sys
import time
from typing import Any

# Repo imports
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "itir-mcp" / "src"))
sys.path.insert(0, str(REPO_ROOT / "reverse-engineered-chatgpt"))
sys.path.insert(0, str(REPO_ROOT / "SensibLaw"))
sys.path.insert(0, str(REPO_ROOT / "SensibLaw" / "src"))
sys.path.insert(0, str(REPO_ROOT / "StatiBaker"))

from re_gpt.gap_comparator import (
    DEFAULT_WORLD_DIR,
    FRAGMENT_NAMES,
    SHAPE_NAMES,
    ExactGapComparator,
)
from re_gpt.fleet import FleetOrchestrator
from itir_mcp.pnf_spectral_packet import (
    analyze_pareto_distribution,
    compute_hierarchical_eigen_coordinates,
)
from itir_mcp.fleet_round_runner import spawn_parallel_lanes


LEDGER_PATH = REPO_ROOT / "docs" / "fleet" / "autonomous_rounds_ledger.json"
SPECTRAL_OUTPUT_PATH = REPO_ROOT / "docs" / "fleet" / "full_corpus_spectral_coordinates.json"


def step1_pnf_spectral_and_doc_pass() -> dict[str, Any]:
    """Ingest hydrated threads and repo docs to extract the full macroscopic spectrum."""
    print("=" * 70)
    print("STEP 1: Full Corpus PNF Spectral & Doc Ingestion Pass")
    print("=" * 70)

    t0 = time.perf_counter()
    slrw_path = DEFAULT_WORLD_DIR / "fleet_top500_iter1.slrw"
    multisets: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)

    if slrw_path.exists():
        print(f"Streaming PNF factor atoms from {slrw_path} ({slrw_path.stat().st_size / 1e6:.1f} MB)...")
        with open(slrw_path, "rb") as f:
            while True:
                magic = f.read(4)
                if not magic or magic != b"SLRW":
                    break
                _ver = struct.unpack("<H", f.read(2))[0]
                header = f.read(2)
                kind_u8 = header[0]
                id_len, aux_len, payload_len = struct.unpack("<III", f.read(12))
                _iteration = struct.unpack("<q", f.read(8))[0]
                rec_id = f.read(id_len).decode("utf-8", errors="replace")
                aux = f.read(aux_len).decode("utf-8", errors="replace") if aux_len else ""
                payload = f.read(payload_len)
                if kind_u8 == 2 and payload.startswith(b"PNF1"):
                    frag_u8 = payload[4]
                    shape_u8 = payload[5]
                    role = FRAGMENT_NAMES.get(frag_u8, "other")
                    dep = SHAPE_NAMES.get(shape_u8, "unresolved")
                    pos = 32
                    try:
                        olen = struct.unpack("<I", payload[pos : pos + 4])[0]
                        pos += 4 + olen
                        llen = struct.unpack("<I", payload[pos : pos + 4])[0]
                        pos += 4
                        lemma = payload[pos : pos + llen].decode("utf-8", errors="replace")
                        sig = f"{role}:{lemma.lower()}:{dep}"
                        cid = aux[:36]
                        if cid:
                            multisets[cid][sig] += 1
                    except Exception:
                        continue
        print(f"Extracted {len(multisets)} threads from .slrw store.")

    # Ingest repo docs
    comp = ExactGapComparator()
    doc_paths = [
        REPO_ROOT / "ROADMAP.md",
        REPO_ROOT.parent / "COMPACTIFIED_CONTEXT.md",
        REPO_ROOT / "docs" / "adr" / "ADR_014_crisis_advocacy_module_cam_20260208.md",
        REPO_ROOT / "docs" / "adr" / "ADR_contextual_fields_non_authoritative.md",
        REPO_ROOT / "SensibLaw" / "docs" / "ADR_LAYER3_SPAN_CONTRACT.md",
        REPO_ROOT / "SensibLaw" / "docs" / "regex_semantic_policy.md",
        REPO_ROOT / "docs" / "fleet" / "topical_pnf_world_model_convergence_20261027.md",
    ]
    for dp in doc_paths:
        if dp.exists():
            ms = comp.extract_formal_multiset(dp)
            if ms:
                multisets[f"doc:{dp.name}"] = ms

    print(f"Ingested {len(multisets)} total entities (threads + docs) in {time.perf_counter() - t0:.2f}s")

    corpus_factor_counts: collections.Counter = collections.Counter()
    for ms in multisets.values():
        for factor, cnt in ms.items():
            corpus_factor_counts[factor] += cnt

    top_factors = [factor for factor, _ in corpus_factor_counts.most_common(250)]
    thread_rows = []
    for entity_id, ms in multisets.items():
        factors_dict = {f: ms[f] for f in top_factors if ms[f] > 0}
        if factors_dict:
            thread_rows.append({"thread_id": entity_id, "factors": factors_dict})

    print(f"Computing hierarchical eigen coordinates across {len(thread_rows)} entities with top {len(top_factors)} factors...")
    coords = compute_hierarchical_eigen_coordinates(thread_rows, k_eigens=8)

    # Pareto analysis over factor frequencies
    factor_freqs = [cnt for _, cnt in corpus_factor_counts.most_common(100)]
    pareto_res = analyze_pareto_distribution({"factor_frequencies": factor_freqs})

    spectral_payload = {
        "version": "itir.pnf.full_corpus_spectral.v1",
        "timestamp": time.time(),
        "entity_count": len(thread_rows),
        "distinct_factors": len(corpus_factor_counts),
        "singular_values": coords["singular_values"],
        "marchenko_pastur": coords["marchenko_pastur"],
        "eigen_motifs": coords["eigen_motifs"],
        "concept_coordinates": coords["concept_coordinates"][:50],
        "pareto_analysis": pareto_res,
    }

    SPECTRAL_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    SPECTRAL_OUTPUT_PATH.write_text(json.dumps(spectral_payload, indent=2), encoding="utf-8")
    print(f"Saved spectral coordinates to {SPECTRAL_OUTPUT_PATH}")

    mp = coords["marchenko_pastur"]
    print(f"Marchenko-Pastur lambda_plus: {mp['lambda_plus']:.2f}")
    print(f"Macroscopic Components: {mp['macroscopic_component_count']}")
    for comp_info in coords["components"][:8]:
        tag = "[MACRO]" if comp_info["macroscopic"] else "[bulk]"
        print(f"  {tag} Eigen {comp_info['index']}: lambda={comp_info['singular_value']:.2f} | Motif: {comp_info['motif_name']}")

    return spectral_payload


def build_autonomous_pnf_prompt(leaf_claim: dict[str, Any], eigen_info: dict[str, Any] | None = None) -> str:
    """Build the autonomous mode prompt containing GH refs, pruned PNF graph, and mathematical invariants."""
    lane = leaf_claim.get("lane", "")
    orchestrator_id = leaf_claim.get("orchestrator_id", "")
    claim_text = leaf_claim.get("lane_claim", "")
    support = leaf_claim.get("typed_support", {})
    files = support.get("files", [])
    symbols = support.get("symbols", [])
    lemmas = support.get("lemmas", [])

    motif_hint = ""
    if eigen_info:
        motif_hint = f"Macroscopic Eigen-Motif: {eigen_info.get('motif_name', 'Algebraic Unification')}\n"

    prompt = (
        f"@ao_autonomous_pnf @pnf_steer @zero_trust_escapes @actor_critic\n\n"
        f"Lane: {lane}\n"
        f"Orchestrator ID: {orchestrator_id}\n"
        f"Obligation: {claim_text}\n"
        f"{motif_hint}"
        f"Pruned PNF Typed Support:\n"
        f"  Target Files: {', '.join(files) if files else 'None'}\n"
        f"  Target Symbols: {', '.join(symbols) if symbols else 'None'}\n"
        f"  Target Lemmas: {', '.join(lemmas) if lemmas else 'None'}\n\n"
        f"Execution Instructions:\n"
        f"1. Implement exactly this unblocked leaf obligation on a dedicated git branch via your GitHub connector.\n"
        f"2. Maintain strict pairwise noTypedMeet independence: do not edit surfaces outside your declared typed support.\n"
        f"3. Anti-Proliferation & Zero Trust Escapes:\n"
        f"   - Strictly 0 postulates, 0 allow-unsolved-metas, 0 TERMINATING, 0 NO_POSITIVITY_CHECK.\n"
        f"   - Strictly 0 edits to protected ESD surfaces (dashi_digital_esd, *digital_esd*, *ESD*).\n"
        f"   - Complete implementation and deterministic verification. Do not leave skeletons or stubs.\n"
    )
    return prompt


def step2_execute_5_rounds_of_10_workers(spectral_data: dict[str, Any]) -> None:
    """Execute 5 concurrent rounds of up to 10 workers each."""
    print("\n" + "=" * 70)
    print("STEP 2: Dynamic Parallel Wave Execution (5 Rounds x up to 10 Workers)")
    print("=" * 70)

    claims_dir = REPO_ROOT / ".autonomous-orchestrator" / "lane_claims"
    claim_files = sorted(claims_dir.glob("ao-fleet-conductor-leaf-*.json"))
    if not claim_files:
        raise RuntimeError("No leaf claim files found in .autonomous-orchestrator/lane_claims/")

    all_claims = []
    for p in claim_files:
        try:
            all_claims.append(json.loads(p.read_text("utf-8")))
        except Exception:
            pass

    print(f"Loaded {len(all_claims)} candidate independent leaf claims from disk.")

    # Get mature fleet workers
    orc = FleetOrchestrator()
    fleet_pool = orc.iterate_tranche(prefix=None, min_turns=10, limit=200)
    worker_cids = [m.conversation_id for m in fleet_pool]
    if len(worker_cids) < 50:
        # Fallback to any distinct conversation_ids in SQLite
        import sqlite3
        with sqlite3.connect(orc.db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT conversation_id FROM conversations ORDER BY remote_update_time DESC LIMIT 100")
            worker_cids = [r[0] for r in cur.fetchall()]

    print(f"Available distinct worker pool: {len(worker_cids)} conversation IDs.")

    rounds_records = []
    total_dispatched = 0
    workers_used = set()

    eigen_motifs = spectral_data.get("eigen_motifs", [])

    for round_num in range(1, 6):
        print(f"\n>>> Starting Round {round_num} of 5 <<<")
        start_idx = (round_num - 1) * 10
        end_idx = min(start_idx + 10, len(all_claims))
        round_claims = all_claims[start_idx:end_idx]

        if not round_claims:
            print("No more unblocked claims available. Completing loop early.")
            break

        # Select 10 unused workers
        batch_workers = []
        for cid in worker_cids:
            if cid not in workers_used:
                batch_workers.append(cid)
                workers_used.add(cid)
                if len(batch_workers) == len(round_claims):
                    break

        # Prepare batch lanes
        batch_lanes = []
        for i, claim in enumerate(round_claims):
            eigen_info = eigen_motifs[i % len(eigen_motifs)] if eigen_motifs else None
            prompt_text = build_autonomous_pnf_prompt(claim, eigen_info)
            batch_lanes.append({
                "orchestrator_id": claim.get("orchestrator_id"),
                "lane": claim.get("lane"),
                "prompt": prompt_text,
                "lane_claim": claim.get("lane_claim"),
                "typed_support": claim.get("typed_support"),
                "noTypedMeet": claim.get("noTypedMeet"),
            })

        print(f"Dispatching Round {round_num}: {len(batch_lanes)} parallel workers via itir.ao.spawn_parallel_lanes...")
        for lane_item, cid in zip(batch_lanes, batch_workers):
            print(f"  - [{lane_item['lane']}] -> Worker {cid[:8]} | Task: {lane_item['lane_claim'][:50]}")

        t_round_start = time.perf_counter()
        spawn_result = spawn_parallel_lanes(batch_lanes, batch_workers)
        round_duration = time.perf_counter() - t_round_start

        results = spawn_result.get("results", [])
        success_count = sum(1 for r in results if r.get("state") != "error")
        error_count = len(results) - success_count

        round_record = {
            "round": round_num,
            "timestamp": time.time(),
            "duration_seconds": round_duration,
            "lane_count": len(batch_lanes),
            "success_count": success_count,
            "error_count": error_count,
            "lanes": [
                {
                    "lane": l["lane"],
                    "orchestrator_id": l["orchestrator_id"],
                    "conversation_id": w,
                    "lane_claim": l["lane_claim"],
                    "operation_status": r.get("state", "submitted") if r else "unknown",
                    "operation_id": r.get("operation", {}).get("operation_id") if r else None,
                }
                for l, w, r in zip(batch_lanes, batch_workers, results)
            ],
            "policy": spawn_result.get("policy", {}),
        }
        rounds_records.append(round_record)
        total_dispatched += len(batch_lanes)

        print(f"Round {round_num} Complete: {success_count} submitted, {error_count} errors in {round_duration:.2f}s.")
        time.sleep(2)  # Cooldown between waves to ensure clean transport pacing

    # Record full ledger
    ledger_data = {
        "version": "itir.ao.dynamic_autonomous_rounds.v1",
        "completed_at": time.time(),
        "total_rounds": len(rounds_records),
        "total_workers_dispatched": total_dispatched,
        "mode": "autonomous_pnf_steer",
        "rounds": rounds_records,
    }
    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    LEDGER_PATH.write_text(json.dumps(ledger_data, indent=2), encoding="utf-8")
    print(f"\nAll 5 rounds complete. Ledger saved to {LEDGER_PATH}")


def main() -> None:
    spectral_data = step1_pnf_spectral_and_doc_pass()
    step2_execute_5_rounds_of_10_workers(spectral_data)


if __name__ == "__main__":
    main()
