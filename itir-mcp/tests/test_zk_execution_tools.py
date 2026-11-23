import json
from hashlib import sha256
from unittest.mock import patch
from types import SimpleNamespace
import sys

from itir_mcp import build_default_registry
from itir_mcp.zk_execution_tools import SEC, PERF, INDEX, BUSHIDO, LAYERS


def index():
    doc = dict(schema=1, commit_claim="a"*40, layers={k: [] for k in LAYERS},
               missing_layers=list(LAYERS), state="proposal_only", grounding="OPEN",
               native_acceptance="OPEN", publication_authorized=False)
    doc["index_sha256"] = sha256(json.dumps(doc, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return doc


def test_registry_index_and_safe_boundary():
    r = build_default_registry()
    for name in (SEC, PERF, INDEX, BUSHIDO):
        assert r.get_tool_spec(name).read_only
        assert r.get_tool_authority_profile(name)["max_authority"] == "observed"
    result = r.invoke(INDEX, {"index": index()})
    assert result["ok"] and result["result"]["self_commitment_matches"]
    assert not result["result"]["files_verified"]
    assert r.safe_invoke(INDEX, {"index": index()})["result"]["decision"] == "abstained"
    bad = index()
    bad["commit_claim"] = "b"*40
    assert not r.invoke(INDEX, {"index": bad})["ok"]


def test_policy_provider_no_claimed_authority():
    r = build_default_registry()
    def assess(**kwargs):
        assert kwargs["source"] == "public" and kwargs["actor_role"] == "anonymous"
        assert kwargs["confirmed"] is False
        return SimpleNamespace(decision="deny", reason_code="proposal_from_public_source")
    with patch.dict(sys.modules, {"zksec.security": SimpleNamespace(assess_action=assess)}):
        result = r.invoke(SEC, {"action":"deploy","risk_level":"high"})
        assert result["ok"] and not result["result"]["execution_authorized"]
        assert not r.invoke(SEC, {"action":"deploy","risk_level":"high","confirmed":True})["ok"]


def test_window_provider_groups_metadata_only():
    r = build_default_registry()
    row = dict(zkperf_observation_id="o1", trace_id="t1", run_id="r1",
               asserted_at="2026-11-20T00:00:00Z", source_ref="receipt:r1",
               status="observed", metrics=[dict(name="cycles",kind="integer",value=4)],
               trace_refs=["trace:t1"], proof_refs=[], hash="sha256:"+"a"*64)
    def plan(rows, *, max_observations_per_window):
        assert rows == [row] and max_observations_per_window == 1
        return dict(contractVersion="zkperf-stream/v1", streamId="s", streamRevision="r",
                    windows=[dict(windowId="w",sequence=1,runId="r1",traceId="t1",
                                  observationIds=["o1"],startedAtUtc=row["asserted_at"],
                                  endedAtUtc=row["asserted_at"],payload={"observations":rows})])
    with patch.dict(sys.modules, {"itir_jmd_bridge.zkperf_stream_core": SimpleNamespace(build_zkperf_stream_fixture_from_observations=plan)}):
        result = r.invoke(PERF, {"observations":[row],"max_observations_per_window":1})
        assert result["ok"] and "payload" not in result["result"]["windows"][0]
        assert not result["result"]["supplied_hashes_verified"]
        assert not r.invoke(PERF, {"observations":[row,row],"max_observations_per_window":1})["ok"]
        assert not r.invoke(PERF, {"observations":[dict(row,status="promoted")],"max_observations_per_window":1})["ok"]

def bushido_reconciliation():
    names=("extension_allow_route","extension_deny_route","extension_redirect_route",
           "extension_redirect_target_route")
    return dict(version="bushido.extension_ab_reconciliation.v1",state="proposal_only",
        non_authoritative=True,candidate_only=True,native_acceptance="OPEN",
        decision="consistent_controls_observed",missing_controls=[],contradictions=[],
        baseline_origin=dict.fromkeys(names,1),
        enabled_origin=dict(zip(names,(1,0,1,0))),
        native_reported_counts=dict.fromkeys(names,1),
        fixture_run_ids=["a"*32,"b"*32],execution_authorized=False,
        publication_authorized=False,same_run_linkage_verified=False,
        request_identity_verified=False,runtime_binary_linkage_verified=False,
        physical_enforcement_verified=False,
        input_sha256={k:"c"*64 for k in ("baseline_origin","enabled_origin","baseline_preview","enabled_preview")})


def test_bushido_observation_reuses_window_provider():
    from itir_mcp.zk_execution_tools import window_plan
    from itir_jmd_bridge.zkperf_stream_core import build_zkperf_stream_fixture_from_observations
    r=build_default_registry()
    p={"reconciliation":bushido_reconciliation(),"asserted_at":"2026-11-23T03:41:00Z"}
    result=r.invoke(BUSHIDO,p)
    assert result["ok"],result
    out=result["result"]
    assert out["version"]==BUSHIDO+".v1"
    assert out["native_acceptance"]=="OPEN"
    assert out["observation"]["metrics"][0]["value"]==4
    assert out["stream_contract"]=="zkperf-stream/v1"
    assert out["windows"][0]["observationIds"]==[out["observation"]["zkperf_observation_id"]]
    assert not out["physical_enforcement_verified"]
    assert r.safe_invoke(BUSHIDO,p)["result"]["decision"]=="abstained"


def test_bushido_rejects_authority_and_false_consistency():
    r=build_default_registry()
    row=bushido_reconciliation()
    p={"reconciliation":row,"asserted_at":"2026-11-23T03:41:00Z"}
    for key,value in [
        ("native_acceptance","PASS"),("execution_authorized",True),
        ("same_run_linkage_verified",True),("decision","verified")]:
        original=row[key];row[key]=value
        assert not r.invoke(BUSHIDO,p)["ok"],(key,value)
        row[key]=original
    row["enabled_origin"]["extension_deny_route"]=1
    assert not r.invoke(BUSHIDO,p)["ok"]
    row["enabled_origin"]["extension_deny_route"]=0
    row["native_reported_counts"]["extension_redirect_target_route"]=0
    assert not r.invoke(BUSHIDO,p)["ok"]
