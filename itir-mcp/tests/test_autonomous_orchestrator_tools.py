from __future__ import annotations

import json
from pathlib import Path

import pytest
from itir_mcp import build_default_registry


def test_ao_status_and_claim_and_heartbeat(tmp_path: Path) -> None:
    registry = build_default_registry()

    # 1. Claim a lane
    claim_res = registry.invoke(
        "itir.ao.claim_lane",
        {
            "repo_root": str(tmp_path),
            "orchestrator_id": "test_runner_1",
            "lane": "physics_unification",
            "lane_claim": "Navier Stokes C/D bounds",
            "parent_orchestrator_id": "root_manager",
        },
    )
    assert claim_res["ok"] is True
    assert claim_res["result"]["claim"]["orchestrator_id"] == "test_runner_1"

    # 2. Emit heartbeat
    hb_res = registry.invoke(
        "itir.ao.heartbeat",
        {
            "repo_root": str(tmp_path),
            "orchestrator_id": "test_runner_1",
            "state": "busy",
            "phase": "running",
            "current_step": "testing Mosco projection",
        },
    )
    assert hb_res["ok"] is True
    assert hb_res["result"]["heartbeat"]["state"] == "busy"

    # 3. Report result with ZKP framing
    rep_res = registry.invoke(
        "itir.ao.report_result",
        {
            "repo_root": str(tmp_path),
            "orchestrator_id": "test_runner_1",
            "parent_orchestrator_id": "root_manager",
            "lane": "physics_unification",
            "status": "completed",
            "summary": "Discharged A2 envelope bound",
            "zkp_frame": {
                "objective": "Discharge A2 envelope",
                "reality": "Bound verified in Agda",
                "plan": "Step 1 complete",
            },
            "changed_files": ["DASHI/Physics/Closure/NSCanonicalClayResidualExact.agda"],
        },
    )
    assert rep_res["ok"] is True
    assert rep_res["result"]["report_count"] == 1

    # 4. Status inspect
    status_res = registry.invoke(
        "itir.ao.status",
        {
            "repo_root": str(tmp_path),
        },
    )
    assert status_res["ok"] is True
    res = status_res["result"]
    assert "test_runner_1" in res["lane_claims"]
    assert "heartbeat.test_runner_1.json" in res["heartbeats"]
    assert "root_manager" in res["parent_reports"]
