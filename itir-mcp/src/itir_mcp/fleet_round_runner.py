"""Fleet Round Runner for executing governed convergence rounds across active cluster leads."""

from __future__ import annotations

import logging
from typing import Any

from re_gpt.fleet import FleetOrchestrator
from re_gpt.mcp_server import chatgpt_continue, chatgpt_view

logger = logging.getLogger(__name__)

CONVERGENCE_PROMPT = """@converge_toe @max_cut @grug_ste100 @zkp_qa

Continue per max-cut and converge toward DASHI TOE (`DASHI/EverythingTOESymmetryResolved369.agda` and `DASHI/Unifier.agda`).
- Assume everything we need already exists in-repo across `dashi_agda`, `casey-git-clone`, `zkSEC`, and meta-introspector repos (`zkperf`, `zos-server`, `erdfa-py`, `aristotle-cli-rs`).
- Search first for existing/duplicate constructions via code search / preflight before writing any new code.
- Reconcile with latest PRs (#1266 / #1271 / #1241 / #1249).
- Strict constraint: DO NOT touch ESD surfaces (`dashi_digital_esd`, `*digital_esd*`, `*ESD*`); import only.
- Preserve attribution for meta-introspector repos.
"""

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
