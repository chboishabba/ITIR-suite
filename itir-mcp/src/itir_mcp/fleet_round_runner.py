"""Fleet Round Runner for executing governed convergence rounds across active cluster leads."""

from __future__ import annotations

import logging
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
