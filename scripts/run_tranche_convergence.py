"""Autonomous tranche runner for converging the 200+ fleet conversations toward DASHI TOE.

Iterates through all 254 threads in the 6a% tranche:
- Extracts thread context, cluster, and title
- Generates domain-aware @converge_toe prompt pointing to EverythingTOESymmetryResolved369.agda / Unifier.agda
- Targets Stage R5 Formal AST Subtraction (584 discharged fibres, 3 macroscopic eigen-motifs, 58 unformalised gaps)
- Supports true concurrent dispatching (ThreadPoolExecutor) with clean interval staggering
- Dispatches turns through async curl_cffi with GlobalBackendRateLimiter pacing
- Protects ESD surfaces (import only, zero edits)
- Records operations and progress in durable JSON ledger
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import sqlite3
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from re_gpt.fleet import FleetOrchestrator, FleetMember
from re_gpt.global_rate_limit import GlobalBackendRateLimiter
from re_gpt.mcp_server import chatgpt_continue
from re_gpt.storage import DEFAULT_DB_PATH

DEFAULT_LEDGER_PATH = Path("docs/fleet/tranche_200_convergence_ledger.json")


def load_tranche_ledger(path: Path) -> dict[str, Any]:
    if path.exists():
        try:
            return json.loads(path.read_text())
        except Exception:
            pass
    return {
        "version": "1.0",
        "description": "200+ Fleet Tranche TOE Convergence Ledger",
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "dispatches": {},
    }


def save_tranche_ledger(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data["updated_at"] = datetime.now(timezone.utc).isoformat()
    path.write_text(json.dumps(data, indent=2))


def generate_convergence_prompt(member: FleetMember) -> str:
    domain_specific = ""
    cluster = member.cluster
    title = member.title

    if cluster == "yang_mills":
        domain_specific = (
            "- Reconcile all Balaban RG scale densities, regular-E localizations, and Casimir/stress bounds "
            "directly into the TOE aggregate `DASHI/EverythingTOESymmetryResolved369.agda` and `DASHI/Unifier.agda`.\n"
            "- Connect exact non-promotion theorems for continuum limit / RG flows directly into the TOE root.\n"
        )
    elif cluster == "max_cut":
        domain_specific = (
            "- Reconcile all Max Cut partitions, CFFI kernel bidi bindings, and ternary 27-state intertwiners "
            "with the TOE aggregate `DASHI/EverythingTOESymmetryResolved369.agda`.\n"
            "- Connect exact non-promotion theorems for non-trivial cuts directly into the TOE root.\n"
        )
    elif cluster == "sensiblaw":
        domain_specific = (
            "- Reconcile SensibLaw / Actionstep / legal compliance governance proofs and invariant handoffs "
            "with the TOE aggregate `DASHI/EverythingTOESymmetryResolved369.agda`.\n"
            "- Connect exact governance semantic non-promotion proofs directly into the TOE root.\n"
        )
    else:  # research / infrastructure
        domain_specific = (
            f"- Reconcile the core derivations and theorems from `{title}` with the TOE aggregate "
            "`DASHI/EverythingTOESymmetryResolved369.agda` and `DASHI/Unifier.agda`.\n"
            "- Connect exact non-promotion theorems directly into the TOE aggregate.\n"
        )

    return f"""@converge_toe @max_cut @grug_ste100 @zkp_qa

Continue per max-cut and converge toward DASHI TOE (`DASHI/EverythingTOESymmetryResolved369.agda` and `DASHI/Unifier.agda`).
{domain_specific}- Fleet World-Model Context: 584 fibres are already discharged across the archive.
  Marchenko-Pastur bulk collapse isolates 3 macroscopic eigen-motifs (λ₁=74.55 Balaban RG, λ₂=18.84 NS BM2, λ₃=5.59 Quantum Mereology).
  Target ONLY the 58 unformalised formal gaps and cite existing discharged proofs.
- Anti-Proliferation & Deduplication Rule: DO NOT create new versioned, numbered, or round-suffixed files (e.g. `*Round<N>*`, `*R<N>*`, `*v<N>*`). Reconcile and coalesce all findings directly into existing canonical domain files and the unified aggregates: `DASHI/EverythingTOESymmetryResolved369.agda` and `DASHI/Unifier.agda`. Treat historical round numbers as metadata/receipt provenance only, not new file names.
- Assume all needed constructions already exist in-repo across `dashi_agda`, `casey-git-clone`, `zkSEC`, and meta-introspector repos (`zkperf`, `zos-server`, `erdfa-py`, `aristotle-cli-rs`).
- Search first for existing/duplicate constructions via code search / preflight before writing any new code.
- Strict constraint: DO NOT touch ESD surfaces (`dashi_digital_esd`, `*digital_esd*`, `*ESD*`); import only.
- Zero trust escapes: 0 postulates, 0 allow-unsolved-metas, 0 TERMINATING, 0 NO_POSITIVITY_CHECK.
- Preserve attribution for original authors and meta-introspector repos. Do not truncate formal proofs or reasoning traces.
"""


def dispatch_single_member(
    member: FleetMember,
    index: int,
    total: int,
    fast: bool,
    dry_run: bool,
    ledger: dict[str, Any],
    dispatches: dict[str, Any],
    ledger_lock: threading.Lock,
    ledger_path: Path,
    stagger_delay: float = 0.0,
) -> dict[str, Any]:
    if stagger_delay > 0:
        time.sleep(stagger_delay)

    cid = member.conversation_id
    prompt = generate_convergence_prompt(member)
    print(f"\n[{index}/{total}] Launching {cid[:8]}... | turns={member.message_count} | cluster={member.cluster} | title='{member.title[:40]}'")

    if dry_run:
        print(f"  [{cid[:8]}] [DRY RUN] Would dispatch prompt.")
        return {"conversation_id": cid, "status": "dry_run"}

    reconcile_attempts = 0 if fast else 3
    try:
        try:
            res = chatgpt_continue(
                conversation_id=cid,
                prompt=prompt,
                follow=False,
                write_transport="async",
                dom_fallback=False,
                reconcile_attempts=reconcile_attempts,
            )
        except Exception as inner_exc:
            if "stale" in str(inner_exc).lower():
                print(f"  [{cid[:8]}] Session stale detected; auto-refreshing session...")
                from re_gpt.session_lifecycle import SessionLifecycle
                SessionLifecycle().refresh(browser_mode="displayless")
                res = chatgpt_continue(
                    conversation_id=cid,
                    prompt=prompt,
                    follow=False,
                    write_transport="async",
                    dom_fallback=False,
                    reconcile_attempts=reconcile_attempts,
                )
            else:
                raise

        status = res.get("status") or res.get("state") or "submitted"
        op_id = res.get("operation_id")
        print(f"  [{cid[:8]}] Dispatched: status={status}, op_id={op_id}")

        with ledger_lock:
            dispatches[cid] = {
                "title": member.title,
                "cluster": member.cluster,
                "turns": member.message_count,
                "dispatched_at": datetime.now(timezone.utc).isoformat(),
                "status": status,
                "operation_id": op_id,
            }
            save_tranche_ledger(ledger_path, ledger)

        return {"conversation_id": cid, "status": status, "operation_id": op_id}
    except Exception as exc:
        print(f"  [{cid[:8]}] Error dispatching: {exc}")
        return {"conversation_id": cid, "status": "error", "error": str(exc)}


def run_tranche_pass(
    batch_size: int = 10,
    dry_run: bool = False,
    pause_seconds: float = 5.0,
    fast: bool = False,
    concurrent_mode: bool = True,
    workers: int = 20,
    ledger_path: Path = DEFAULT_LEDGER_PATH,
) -> dict[str, Any]:
    fo = FleetOrchestrator()
    members = fo.iterate_tranche(prefix="6a", min_turns=50, sort_by="turns")
    ledger = load_tranche_ledger(ledger_path)
    dispatches = ledger.get("dispatches", {})

    # Check already dispatched in mutation_attempts
    with sqlite3.connect(DEFAULT_DB_PATH, timeout=30.0) as conn:
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT conversation_id FROM mutation_attempts WHERE conversation_id IS NOT NULL")
        mutated_cids = set(r[0] for r in cur.fetchall())

    candidates = [
        m for m in members
        if m.conversation_id not in dispatches and m.conversation_id not in mutated_cids
    ]

    batch = candidates[:batch_size]

    print(f"Total tranche members: {len(members)}")
    print(f"Already dispatched (ledger or db): {len(members) - len(candidates)}")
    print(f"Candidates remaining: {len(candidates)}")
    print(f"Executing batch of up to {len(batch)} (concurrent={concurrent_mode}, workers={workers}, fast={fast}, stagger={pause_seconds}s)...")

    results: list[dict[str, Any]] = []
    ledger_lock = threading.Lock()

    if concurrent_mode and len(batch) > 1:
        pool_size = min(workers, len(batch))
        with concurrent.futures.ThreadPoolExecutor(max_workers=pool_size) as executor:
            future_to_cid = {}
            for i, m in enumerate(batch, 1):
                delay = (i - 1) * pause_seconds
                f = executor.submit(
                    dispatch_single_member,
                    member=m,
                    index=i,
                    total=len(batch),
                    fast=fast,
                    dry_run=dry_run,
                    ledger=ledger,
                    dispatches=dispatches,
                    ledger_lock=ledger_lock,
                    ledger_path=ledger_path,
                    stagger_delay=delay,
                )
                future_to_cid[f] = m.conversation_id

            for future in concurrent.futures.as_completed(future_to_cid):
                cid = future_to_cid[future]
                try:
                    res = future.result()
                    results.append(res)
                except Exception as exc:
                    print(f"  [{cid[:8]}] Worker future crashed: {exc}")
                    results.append({"conversation_id": cid, "status": "crashed", "error": str(exc)})
    else:
        # Sequential execution
        for i, m in enumerate(batch, 1):
            res = dispatch_single_member(
                member=m,
                index=i,
                total=len(batch),
                fast=fast,
                dry_run=dry_run,
                ledger=ledger,
                dispatches=dispatches,
                ledger_lock=ledger_lock,
                ledger_path=ledger_path,
                stagger_delay=0.0,
            )
            results.append(res)
            if i < len(batch) and pause_seconds > 0:
                time.sleep(pause_seconds)

    save_tranche_ledger(ledger_path, ledger)
    return {
        "total_members": len(members),
        "dispatched_batch": len(results),
        "remaining": len(candidates) - len(results),
        "results": results,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run 200+ tranche convergence pass")
    parser.add_argument("--batch-size", type=int, default=20, help="Number of conversations to dispatch in this batch")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without submitting")
    parser.add_argument("--pause", "--stagger", dest="pause", type=float, default=5.0, help="Stagger delay between worker starts (seconds)")
    parser.add_argument("--fast", action="store_true", default=True, help="Fast submission mode: submit without pulling full multi-MB graph")
    parser.add_argument("--workers", type=int, default=20, help="Max concurrent worker threads")
    parser.add_argument("--concurrent", dest="concurrent", action="store_true", default=True, help="Run workers concurrently (default: True)")
    parser.add_argument("--no-concurrent", dest="concurrent", action="store_false", help="Run workers sequentially")
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER_PATH, help="Path to convergence ledger")
    args = parser.parse_args()

    res = run_tranche_pass(
        batch_size=args.batch_size,
        dry_run=args.dry_run,
        pause_seconds=args.pause,
        fast=args.fast,
        concurrent_mode=args.concurrent,
        workers=args.workers,
        ledger_path=args.ledger,
    )
    print("\nBatch Summary:", json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
