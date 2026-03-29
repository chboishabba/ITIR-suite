from __future__ import annotations

import argparse
import json
from .retrieval import AdmissibilityPolicy, manifold_aware_rank, manifold_aware_select
from .types import FactRecord, Query, ShardSummary, TraceEvent, TraceWindow


def demo() -> None:
    parser = argparse.ArgumentParser(description="ZOS/SL bridge demo")
    parser.add_argument("--query", required=True)
    parser.add_argument("--admit", action="store_true", help="apply post-ranking admissibility filter")
    parser.add_argument("--min-score", type=float, default=0.1)
    parser.add_argument("--min-spectral", type=float, default=0.01)
    args = parser.parse_args()

    shard_a = ShardSummary(
        shard_id="tenant_a",
        facts=[
            FactRecord("f1", "housing_issue", {"tenant": "p1", "issue": "mould"}, {"severity": "high"}),
            FactRecord("f2", "complaint", {"tenant": "p2", "issue": "dampness"}, {"severity": "high"}),
        ],
        trace_windows=[
            TraceWindow("w1", "tenant_a", [TraceEvent(1, "extract", "promote_fact", {"r1": 1}, ["cone_ok"], "loopA")]),
        ],
    )
    shard_b = ShardSummary(
        shard_id="runtime_b",
        facts=[FactRecord("f3", "service_event", {"service": "node", "status": "up"})],
        trace_windows=[
            TraceWindow("w2", "runtime_b", [TraceEvent(1, "runtime", "sync_peer", {"r1": 8}, ["loop_ok"], "loopB")]),
        ],
    )

    q = Query("q1", args.query, predicate_hints=["housing_issue"], role_hints={"tenant": "any"})
    if args.admit:
        policy = AdmissibilityPolicy(
            min_score=args.min_score,
            min_spectral_for_non_domain=args.min_spectral,
        )
        decisions = manifold_aware_select(q, [shard_a, shard_b], top_k=2, policy=policy)
        rendered = []
        for decision in decisions:
            rendered.append(
                {
                    "shard_id": decision.shard_id,
                    "accepted": decision.accepted,
                    "accepted_by": decision.accepted_by,
                    "blocked_by": decision.blocked_by,
                    "result": decision.result.__dict__ if decision.result else None,
                }
            )
        print(json.dumps(rendered, indent=2))
        return

    out = manifold_aware_rank(q, [shard_a, shard_b], top_k=2)
    print(json.dumps([r.__dict__ for r in out], indent=2))


if __name__ == "__main__":
    demo()
