"""Autonomous tranche runner for converging the 200+ fleet conversations toward DASHI TOE.

Iterates through all 254 threads in the 6a% tranche:
- Extracts thread context, cluster, and title
- Generates domain-aware @converge_toe prompt pointing to EverythingTOESymmetryResolved369.agda / Unifier.agda
- Dispatches turns through async curl_cffi with GlobalBackendRateLimiter pacing
- Protects ESD surfaces (import only, zero edits)
- Records operations and progress in durable JSON ledger
"""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
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
{domain_specific}- Assume all needed constructions already exist in-repo across `dashi_agda`, `casey-git-clone`, `zkSEC`, and meta-introspector repos (`zkperf`, `zos-server`, `erdfa-py`, `aristotle-cli-rs`).
- Search first for existing/duplicate constructions via code search / preflight before writing any new code.
- Strict constraint: DO NOT touch ESD surfaces (`dashi_digital_esd`, `*digital_esd*`, `*ESD*`); import only.
- Preserve attribution for original authors and meta-introspector repos. Do not truncate formal proofs or reasoning traces.
"""


def run_tranche_pass(
    batch_size: int = 10,
    dry_run: bool = False,
    pause_seconds: float = 3.0,
    fast: bool = False,
    ledger_path: Path = DEFAULT_LEDGER_PATH,
) -> dict[str, Any]:
    fo = FleetOrchestrator()
    members = fo.iterate_tranche(prefix="6a", min_turns=50, sort_by="turns")
    ledger = load_tranche_ledger(ledger_path)
    dispatches = ledger.get("dispatches", {})

    # Check already dispatched in mutation_attempts
    with sqlite3.connect(DEFAULT_DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT conversation_id FROM mutation_attempts WHERE conversation_id IS NOT NULL")
        mutated_cids = set(r[0] for r in cur.fetchall())

    candidates = [
        m for m in members
        if m.conversation_id not in dispatches and m.conversation_id not in mutated_cids
    ]

    print(f"Total tranche members: {len(members)}")
    print(f"Already dispatched (ledger or db): {len(members) - len(candidates)}")
    print(f"Candidates remaining: {len(candidates)}")
    print(f"Executing batch of up to {batch_size} (fast={fast}, pause={pause_seconds}s)...")

    results = []
    for i, m in enumerate(candidates[:batch_size], 1):
        cid = m.conversation_id
        prompt = generate_convergence_prompt(m)
        print(f"\n[{i}/{batch_size}] Dispatching {cid[:8]}... | turns={m.message_count} | cluster={m.cluster} | title='{m.title[:40]}'")

        if dry_run:
            print("  [DRY RUN] Would dispatch prompt.")
            results.append({"conversation_id": cid, "status": "dry_run"})
            continue

        try:
            reconcile_attempts = 0 if fast else 3
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
                    print("  Session stale detected; auto-refreshing session...")
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
            print(f"  Dispatched: status={status}, op_id={op_id}")
            dispatches[cid] = {
                "title": m.title,
                "cluster": m.cluster,
                "turns": m.message_count,
                "dispatched_at": datetime.now(timezone.utc).isoformat(),
                "status": status,
                "operation_id": op_id,
            }
            results.append({"conversation_id": cid, "status": status, "operation_id": op_id})
            save_tranche_ledger(ledger_path, ledger)
        except Exception as exc:
            print(f"  Error dispatching {cid[:8]}: {exc}")
            results.append({"conversation_id": cid, "status": "error", "error": str(exc)})

        if i < batch_size and pause_seconds > 0:
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
    parser.add_argument("--batch-size", type=int, default=5, help="Number of conversations to dispatch in this batch")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without submitting")
    parser.add_argument("--pause", "--stagger", dest="pause", type=float, default=3.0, help="Pause/stagger between dispatches (seconds)")
    parser.add_argument("--fast", action="store_true", help="Fast submission mode: submit without pulling full multi-MB graph")
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER_PATH, help="Path to convergence ledger")
    args = parser.parse_args()

    res = run_tranche_pass(
        batch_size=args.batch_size,
        dry_run=args.dry_run,
        pause_seconds=args.pause,
        fast=args.fast,
        ledger_path=args.ledger,
    )
    print("\nBatch Summary:", json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
