from zos_pipeline.monster_lattice import resonance_score
from zos_pipeline.retrieval import AdmissibilityPolicy, manifold_aware_rank, manifold_aware_select
from zos_pipeline.types import FactRecord, Query, ShardSummary, TraceEvent, TraceWindow


def test_resonance_pipeline_smoke():
    score = resonance_score(b"tenant mould high severity")
    assert 0 <= score.o71 < 71
    assert 0 <= score.o59 < 59
    assert 0 <= score.o47 < 47


def test_ranking_prefers_housing():
    shard_a = ShardSummary(
        shard_id="tenant_a",
        facts=[
            FactRecord("f1", "housing_issue", {"tenant": "p1", "issue": "mould"}, {"severity": "high"}),
            FactRecord("f2", "complaint", {"tenant": "p2", "issue": "dampness"}, {"severity": "high"}),
        ],
        trace_windows=[TraceWindow("w1", "tenant_a", [TraceEvent(1, "extract", "promote_fact", {"r1": 1}, ["cone_ok"], "loopA")])],
    )
    shard_b = ShardSummary(
        shard_id="runtime_b",
        facts=[FactRecord("f3", "service_event", {"service": "node", "status": "up"})],
        trace_windows=[TraceWindow("w2", "runtime_b", [TraceEvent(1, "runtime", "sync_peer", {"r1": 8}, ["loop_ok"], "loopB")])],
    )
    q = Query("q1", "tenant mould complaint", predicate_hints=["housing_issue"], role_hints={"tenant": "any"})
    out = manifold_aware_rank(q, [shard_a, shard_b], top_k=2)
    assert out[0].shard_id == "tenant_a"
    assert out[0].spectral_score > out[1].spectral_score


def test_ranking_uses_real_domain_match():
    shard_a = ShardSummary(
        shard_id="tenant_a",
        facts=[FactRecord("f1", "housing_issue", {"tenant": "p1", "issue": "mould"}, {"severity": "high"})],
        trace_windows=[TraceWindow("w1", "tenant_a", [TraceEvent(1, "extract", "promote_fact", {"r1": 1}, ["cone_ok"], "loopA")], domain_hint="housing")],
    )
    shard_b = ShardSummary(
        shard_id="runtime_b",
        facts=[FactRecord("f2", "service_event", {"service": "node", "status": "up"})],
        trace_windows=[TraceWindow("w2", "runtime_b", [TraceEvent(1, "runtime", "sync_peer", {"r1": 8}, ["loop_ok"], "loopB")], domain_hint="runtime")],
    )

    q = Query("q1", "tenant mould complaint", predicate_hints=["housing_issue"], role_hints={"tenant": "any"})
    out = manifold_aware_rank(q, [shard_a, shard_b], top_k=2)

    by_id = {result.shard_id: result for result in out}
    assert by_id["tenant_a"].domain_match == 1.0
    assert by_id["runtime_b"].domain_match == 0.0


def test_admissibility_filter_accepts_structured_match_and_rejects_resonance_only():
    shard_a = ShardSummary(
        shard_id="tenant_a",
        facts=[FactRecord("f1", "housing_issue", {"tenant": "p1", "issue": "mould"}, {"severity": "high"})],
        trace_windows=[TraceWindow("w1", "tenant_a", [TraceEvent(1, "extract", "promote_fact", {"r1": 1}, ["cone_ok"], "loopA")], domain_hint="housing")],
    )
    shard_b = ShardSummary(
        shard_id="runtime_b",
        facts=[FactRecord("f2", "service_event", {"service": "node", "status": "up"})],
        trace_windows=[TraceWindow("w2", "runtime_b", [TraceEvent(1, "runtime", "sync_peer", {"r1": 8}, ["loop_ok"], "loopB")], domain_hint="runtime")],
    )

    q = Query("q1", "tenant mould complaint", predicate_hints=["housing_issue"], role_hints={"tenant": "any"})
    decisions = manifold_aware_select(q, [shard_a, shard_b], top_k=2, policy=AdmissibilityPolicy())

    by_id = {decision.shard_id: decision for decision in decisions}
    assert by_id["tenant_a"].accepted is True
    assert "structured_alignment" in by_id["tenant_a"].accepted_by
    assert by_id["runtime_b"].accepted is False
    assert "resonance_only_signal" in by_id["runtime_b"].blocked_by
