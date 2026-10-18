#!/usr/bin/env python3
"""Autonomous Carousel Fleet Orchestrator for ITIR-suite.

Maintains a pool of N concurrently active research threads across the 200-thread fleet,
cycling round-robin so all threads advance toward physics and repository unification.

Orchestrator Lifecycle Decisions:
1. ADVANCE: Thread produced new premises or reduced Delta_Gap -> cycle to back of queue.
2. INTEGRATE (DONE): Delta_Gap == 0 or formal verification succeeded -> retire as proven.
3. REVIVE (FATIGUE): Turn count > 400 or context degraded -> distill mathematical core and spawn clean child.
4. PARK / BRANCH (DEAD END): 3 consecutive turns without factor reduction -> park in quarantine or branch.
"""

from __future__ import annotations

# Retired entrypoint: block before imports, sessions, or side effects.
if __name__ == "__main__":
    raise SystemExit("Legacy carousel retired: no account dispatch. Use python -m scripts.evidence_fleet_controller --db PATH --plan")


import argparse
import concurrent.futures
import json
import logging
import os
import signal
import sqlite3
import sys
import time
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Ensure ITIR-suite, itir-mcp, and reverse-engineered-chatgpt are on path
REPO_ROOT = Path(__file__).resolve().parents[1]
ITIR_MCP_ROOT = REPO_ROOT / "itir-mcp" / "src"
STATIBAKER_ROOT = REPO_ROOT / "StatiBaker"
RE_GPT_ROOT = REPO_ROOT / "reverse-engineered-chatgpt"
for p in (REPO_ROOT, ITIR_MCP_ROOT, STATIBAKER_ROOT, RE_GPT_ROOT):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from itir_mcp.autonomous_orchestrator_tools import (
    ao_claim_lane,
    ao_heartbeat,
    ao_report_result,
    ao_status,
)
from sb.ao_kanboard_control import build_ao_control_runsheet
from re_gpt.mutation_service import MutationService
import threading

RUNNING = True
BROWSER_LOCK = threading.Lock()


def _sig_handler(signum: int, frame: Any) -> None:
    global RUNNING
    logging.info(f"Received signal {signum}, initiating graceful shutdown...")
    RUNNING = False


signal.signal(signal.SIGINT, _sig_handler)
signal.signal(signal.SIGTERM, _sig_handler)


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def resolve_database_url() -> str | None:
    env_file = Path("/home/c/Documents/code/slr/.env")
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("DATABASE_URL="):
                return line.split("=", 1)[1].strip()
    return os.getenv("DATABASE_URL")


class ThreadLifecycleManager:
    """Decides when threads should advance, integrate, revive, or park."""

    def __init__(self, db_path: Path, max_turns_before_revive: int = 400, max_stagnant_turns: int = 3):
        self.db_path = db_path
        self.max_turns_before_revive = max_turns_before_revive
        self.max_stagnant_turns = max_stagnant_turns
        self.history: dict[str, dict[str, Any]] = {}

    def get_thread_info(self, cid: str) -> dict[str, Any]:
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute(
            "SELECT c.title, count(m.message_index) as turns, max(m.create_time) as last_ts "
            "FROM conversations c "
            "LEFT JOIN messages m ON c.conversation_id = m.conversation_id "
            "WHERE c.conversation_id LIKE ? "
            "GROUP BY c.conversation_id",
            (f"{cid[:8]}%",)
        )
        row = cur.fetchone()
        conn.close()
        if not row:
            return {"title": "Unknown", "turns": 0, "last_ts": 0}
        return {"title": row[0] or "Untitled", "turns": row[1] or 0, "last_ts": row[2] or 0}

    def evaluate_lifecycle(self, cid: str, gap_report: Any | None = None) -> tuple[str, str]:
        info = self.get_thread_info(cid)
        turns = info["turns"]
        state_hist = self.history.setdefault(cid, {"prior_gaps": [], "stagnant_count": 0, "status": "active"})

        # 1. Integration check
        if gap_report and gap_report.exact_multiset_match:
            state_hist["status"] = "integrated"
            return "INTEGRATE", f"Delta_Gap is zero; fully proved and integrated ({turns} turns)."

        # 2. Stagnation check
        if gap_report:
            current_unmatched = gap_report.unmatched_formal_factors
            prior_gaps = state_hist["prior_gaps"]
            if prior_gaps and prior_gaps[-1] <= current_unmatched:
                state_hist["stagnant_count"] += 1
            else:
                state_hist["stagnant_count"] = 0
            prior_gaps.append(current_unmatched)

            if state_hist["stagnant_count"] >= self.max_stagnant_turns:
                state_hist["status"] = "parked_stagnant"
                return "PARK", f"Stagnant for {state_hist['stagnant_count']} turns without Delta_Gap reduction."

        # 3. Fatigue check
        if turns >= self.max_turns_before_revive:
            state_hist["status"] = "fatigued"
            return "REVIVE", f"Thread has reached {turns} turns; needs context distillation & revival."

        # 4. Standard advance
        state_hist["status"] = "active"
        return "ADVANCE", f"Actively advancing (turn {turns})."


class CarouselFleetOrchestrator:
    def __init__(
        self,
        repo_root: Path,
        *,
        concurrency: int = 20,
        interval: float = 10.0,
        db_path: Path | None = None,
    ) -> None:
        self.repo_root = repo_root
        self.concurrency = concurrency
        self.interval = interval
        self.db_path = db_path or (Path.home() / ".chatgpt_history.sqlite3")
        self.cp_dir = repo_root / ".autonomous-orchestrator"
        self.lifecycle = ThreadLifecycleManager(self.db_path)
        self.mutation_service = MutationService()

        # Thread queue (round-robin carousel)
        self.roster: list[dict[str, Any]] = []
        self.active_in_flight: set[str] = set()
        self.load_fleet_roster()

    def load_fleet_roster(self) -> None:
        """Load prioritized research threads from the database."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute(
            """
            SELECT c.conversation_id, c.title, count(m.message_index) as turns
            FROM conversations c
            LEFT JOIN messages m ON c.conversation_id = m.conversation_id
            GROUP BY c.conversation_id
            HAVING turns >= 4
            ORDER BY turns DESC
            LIMIT 150
            """
        )
        rows = cur.fetchall()
        conn.close()

        self.roster = []
        for cid, title, turns in rows:
            self.roster.append({
                "conversation_id": cid,
                "title": title or "Untitled",
                "turns": turns,
                "lane": f"fleet.{cid[:8]}",
                "status": "queued",
                "last_run_at": 0.0,
            })
        logging.info(f"Loaded {len(self.roster)} candidate threads into carousel roster.")

    def synthesize_prompt(self, cid: str, title: str) -> str:
        """Synthesize a targeted falsifiable continuation prompt."""
        t_lower = title.lower()
        if "millennium" in t_lower or "navier" in t_lower:
            return (
                "Regarding our ongoing Navier-Stokes and Millennium closure: "
                "in NSCanonicalClayResidualExact.agda, invariants property:a2highenvelope and "
                "property:cdkernelbuild remain open. Formulate the exact quantitative bound on the "
                "A2 high-envelope that discharges the Clay C/D commutators without energy blow-up."
            )
        elif "moonshine" in t_lower or "e8" in t_lower:
            return (
                "Regarding our Monstrous Moonshine PR #1098 and MonsterWeightTwoLinearActionBridgeExact: "
                "we have the Suzuki 3B character family split (65610 = 90 x 729 = (12 + 78) x 729). "
                "Provide the proof-bearing linear inhabitant for the 196883 Griess constituent to close "
                "the weight-two linear Monster bridge."
            )
        elif "goldbach" in t_lower or "fractran" in t_lower:
            return (
                "Regarding PR #1214 and the Goldbach 30 -> 29 FRACTRAN register machine: "
                "verify the transition invariant and bound the register state to ensure deterministic convergence."
            )
        elif "casimir" in t_lower or "wec" in t_lower:
            return (
                "Regarding the Casimir stress-energy tensor and WEC/MEC quantum inequality bounds: "
                "derive the exact Ford-Roman spacetime sampling bound bounding the negative energy density integral."
            )
        elif "torque" in t_lower:
            return (
                "Regarding relativistic torque and angular momentum transport in continuous media: "
                "formulate the conservation divergence equation linking the anti-symmetric stress tensor to boundary torque."
            )
        else:
            return (
                "Proceed with the next rigorous formalization step: state the key open lemma, "
                "bound all unproven invariants, and provide the exact typed AST definition."
            )

    def advance_single_thread(self, thread_item: dict[str, Any]) -> None:
        cid = thread_item["conversation_id"]
        title = thread_item["title"]
        cid_short = cid[:8]

        try:
            logging.info(f"[{cid_short}] Dispatching active turn for '{title[:30]}'...")
            prompt = self.synthesize_prompt(cid, title)

            # Claim lane & heartbeat
            ao_claim_lane({
                "repo_root": str(self.repo_root),
                "orchestrator_id": f"runner_{cid_short}",
                "lane": thread_item["lane"],
                "lane_claim": title,
            })
            ao_heartbeat({
                "repo_root": str(self.repo_root),
                "orchestrator_id": f"runner_{cid_short}",
                "state": "busy",
                "phase": "mutation_turn",
                "current_step": "Awaiting assistant streaming response",
            })

            # Execute turn via MutationService (async-first with backoff, strictly locked DOM fallback)
            res = None
            for attempt in range(2):
                try:
                    res = self.mutation_service.continue_thread(
                        cid,
                        prompt,
                        write_transport="async",
                        dom_fallback=False,
                        follow=True,
                        follow_timeout=120.0,
                    )
                    break
                except Exception as async_err:
                    logging.warning(f"[{cid_short}] Async attempt {attempt+1} failed ({async_err}), backing off...")
                    time.sleep(2.0 + attempt * 2.0)

            if res is None:
                logging.info(f"[{cid_short}] Acquiring BROWSER_LOCK for rapid DOM submission...")
                with BROWSER_LOCK:
                    res = self.mutation_service.continue_thread(
                        cid,
                        prompt,
                        write_transport="dom",
                        dom_fallback=True,
                        reconcile_attempts=0,
                        follow=False,
                    )
                logging.info(f"[{cid_short}] DOM submission completed; BROWSER_LOCK released.")

            # If response is pending, reconcile outside BROWSER_LOCK
            op_id = res.get("operation_id") if isinstance(res, dict) else None
            assistant_text = res.get("assistant_text", "") if isinstance(res, dict) else ""
            if not assistant_text and op_id:
                logging.info(f"[{cid_short}] Polling for assistant completion (op={op_id[:8]})...")
                deadline = time.monotonic() + 90.0
                while time.monotonic() < deadline:
                    time.sleep(3.0)
                    try:
                        status = self.mutation_service.operation_status(op_id)
                        if status and status.get("state") == "complete":
                            res = status
                            assistant_text = status.get("assistant_text", "")
                            break
                        rec = self.mutation_service.reconcile(
                            op_id,
                            prompt=prompt,
                            not_before=time.time() - 120.0,
                            browser_fallback=False,
                        )
                        if rec and rec.get("state") == "complete":
                            res = rec
                            assistant_text = rec.get("assistant_text", "")
                            break
                    except Exception:
                        pass

                if not assistant_text and op_id:
                    with BROWSER_LOCK:
                        try:
                            rec = self.mutation_service.reconcile(
                                op_id,
                                prompt=prompt,
                                not_before=time.time() - 150.0,
                                browser_fallback=True,
                            )
                            if rec and rec.get("state") == "complete":
                                res = rec
                                assistant_text = rec.get("assistant_text", "")
                        except Exception:
                            pass

            assistant_text = (res or {}).get("assistant_text", "")
            logging.info(f"[{cid_short}] Turn completed ({len(assistant_text)} chars returned).")

            # Evaluate lifecycle decision
            action, reason = self.lifecycle.evaluate_lifecycle(cid)
            logging.info(f"[{cid_short}] Orchestrator Lifecycle Decision: {action} ({reason})")

            # Handle automatic revival if fatigued
            if action == "REVIVE":
                try:
                    from re_gpt.revive import revive_thread
                    logging.info(f"[{cid_short}] Triggering automatic context revival into clean child thread...")
                    rev_prompt = self.synthesize_prompt(cid, title)
                    rev_res = revive_thread(
                        cid,
                        rev_prompt,
                        write_transport="async",
                        dom_fallback=True,
                    )
                    new_cid = str(rev_res.get("conversation_id") or rev_res.get("resolved_thread_id") or "")
                    if new_cid:
                        logging.info(f"[{cid_short}] Successfully revived into fresh child: {new_cid[:8]}")
                        thread_item["conversation_id"] = new_cid
                        thread_item["turns"] = 1
                        thread_item["status"] = "revived_active"
                        cid = new_cid
                        cid_short = new_cid[:8]
                except Exception as rev_err:
                    logging.warning(f"[{cid_short}] Revival skipped or failed: {rev_err}")

            # Report result
            ao_report_result({
                "repo_root": str(self.repo_root),
                "orchestrator_id": f"runner_{cid_short}",
                "parent_orchestrator_id": "root_toe_orchestrator",
                "lane": thread_item["lane"],
                "status": "completed" if action == "INTEGRATE" else "in_progress",
                "summary": f"Turn completed: {action} - {reason}",
                "zkp_frame": {
                    "objective": title,
                    "reality": f"Response length: {len(assistant_text)} chars",
                    "plan": action,
                    "receipt": res.get("assistant_node_id"),
                },
            })

            thread_item["last_run_at"] = time.time()
            if thread_item.get("status") != "revived_active":
                thread_item["status"] = action

        except Exception as exc:
            logging.error(f"[{cid_short}] Error executing turn: {exc}")
            thread_item["status"] = "error"
        finally:
            self.active_in_flight.discard(cid)

    def run_carousel_tick(self, executor: concurrent.futures.ThreadPoolExecutor) -> None:
        """Check active pool and fill open slots up to concurrency limit."""
        open_slots = self.concurrency - len(self.active_in_flight)
        if open_slots <= 0:
            return

        # Find eligible threads not currently in-flight, sorted by least-recently-run
        now = time.time()
        candidates = [
            t for t in self.roster
            if t["conversation_id"] not in self.active_in_flight
            and t["status"] not in ("INTEGRATE", "PARK")
            and (now - t["last_run_at"]) > 60.0  # pace individual threads by 60s
        ]
        candidates.sort(key=lambda x: x["last_run_at"])

        to_launch = candidates[:open_slots]
        for t in to_launch:
            cid = t["conversation_id"]
            self.active_in_flight.add(cid)
            executor.submit(self.advance_single_thread, t)
            time.sleep(1.5)  # Stagger dispatches to prevent burst collision

        # Pulse daemon status & runsheet
        try:
            build_ao_control_runsheet(self.cp_dir)
            daemon_heartbeat = {
                "orchestrator_id": "carousel_orchestrator",
                "state": "running",
                "last_heartbeat": utc_now(),
                "active_in_flight": list(self.active_in_flight),
                "active_count": len(self.active_in_flight),
                "concurrency_limit": self.concurrency,
                "roster_total": len(self.roster),
            }
            (self.cp_dir / "heartbeat.carousel.json").write_text(json.dumps(daemon_heartbeat, indent=2) + "\n", encoding="utf-8")
        except Exception as exc:
            logging.warning(f"Error compiling runsheet: {exc}")

    def run_loop(self) -> None:
        logging.info(f"Starting Carousel Fleet Orchestrator (Concurrency={self.concurrency}, Interval={self.interval}s)...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.concurrency) as executor:
            while RUNNING:
                try:
                    self.run_carousel_tick(executor)
                except Exception as exc:
                    logging.error(f"Error in carousel tick: {exc}", exc_info=True)
                time.sleep(self.interval)
        logging.info("Carousel Fleet Orchestrator stopped.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Carousel Fleet Orchestrator")
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--concurrency", "-c", type=int, default=20, help="Number of concurrent active threads (default: 20)")
    parser.add_argument("--interval", "-i", type=float, default=10.0, help="Tick loop interval in seconds (default: 10)")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    orchestrator = CarouselFleetOrchestrator(
        args.repo_root.resolve(),
        concurrency=args.concurrency,
        interval=args.interval,
    )
    orchestrator.run_loop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
