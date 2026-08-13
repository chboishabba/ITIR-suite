
from manifold_retrieval import PhiBundle, QueryBundle, RetrievalConfig, ShardCandidate, top_k


def test_grounded_gate_blocks_nonmatching_resonance():
    query = QueryBundle(
        text="tenant mould complaint",
        phi=PhiBundle(
            grounded={
                "pred::complaint": 1.0,
                "role::tenant": 1.0,
                "argval::issue::mould": 1.0,
            },
            domain={"dom::housing_complaints": 1.0},
            experimental={"resonance": 0.9},
        ),
    )

    good = ShardCandidate(
        shard_id="good",
        phi=PhiBundle(
            grounded={
                "pred::complaint": 1.0,
                "role::tenant": 1.0,
                "argval::issue::mould": 1.0,
            },
            domain={"dom::housing_complaints": 1.0},
            experimental={"resonance": 0.2},
        ),
    )

    bad = ShardCandidate(
        shard_id="bad",
        phi=PhiBundle(
            grounded={"pred::invoice": 1.0},
            domain={"dom::housing_complaints": 1.0},
            experimental={"resonance": 0.9},
        ),
    )

    ranked = top_k(query, [bad, good], k=5, cfg=RetrievalConfig(shortlist_k=5))
    assert [r.shard_id for r in ranked] == ["good"]


def test_spectral_rerank_prefers_same_domain_manifold():
    query = QueryBundle(
        text="tenant mould complaint",
        phi=PhiBundle(
            grounded={"pred::complaint": 1.0, "argval::issue::mould": 1.0},
            domain={"dom::housing_complaints": 1.0, "motif::tenancy": 1.0},
        ),
    )

    a = ShardCandidate(
        shard_id="a",
        phi=PhiBundle(
            grounded={"pred::complaint": 1.0, "argval::issue::mould": 1.0},
            domain={"dom::housing_complaints": 1.0, "motif::tenancy": 1.0},
        ),
    )
    b = ShardCandidate(
        shard_id="b",
        phi=PhiBundle(
            grounded={"pred::complaint": 1.0, "argval::issue::mould": 1.0},
            domain={"dom::housing_complaints": 1.0, "motif::tenancy": 0.8},
        ),
    )
    c = ShardCandidate(
        shard_id="c",
        phi=PhiBundle(
            grounded={"pred::complaint": 1.0, "argval::issue::mould": 1.0},
            domain={"dom::tax": 1.0},
        ),
    )

    ranked = top_k(query, [c, b, a], k=5, cfg=RetrievalConfig(shortlist_k=5, graph_top_k=2))
    ids = [r.shard_id for r in ranked]
    assert ids[0] in {"a", "b"}
    assert ids[-1] == "c"
