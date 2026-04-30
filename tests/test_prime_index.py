from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

import pytest

from tools import prime_index as pi


@pytest.fixture()
def fixture_facts() -> List[Dict]:
    return [
        {
            "fact_id": "f1",
            "predicate": "applies",
            "arguments": {"subject": "contract", "object": "pet_policy"},
            "qualifiers": {"jurisdiction": "nsw"},
            "provenance": [{"doc_id": "doc1", "start": 120, "end": 174}],
            "promotion_receipt": "r1",
            "reconstructible": True,
        },
        {
            "fact_id": "f2",
            "predicate": "requires",
            "arguments": {"subject": "lease", "object": "bond_payment"},
            "qualifiers": {"jurisdiction": "nsw"},
            "provenance": [{"doc_id": "doc1", "start": 220, "end": 260}],
            "promotion_receipt": "r2",
            "reconstructible": True,
        },
    ]


@pytest.fixture()
def fixture_shards(tmp_path: Path, fixture_facts: List[Dict]) -> List[pi.PrimeIndexShard]:
    paths = {}
    for fact in fixture_facts:
        p = tmp_path / f"{fact['fact_id']}.json"
        p.write_text(json.dumps(fact), encoding="utf-8")
        paths[fact["fact_id"]] = p

    shards: List[pi.PrimeIndexShard] = []
    for fact in fixture_facts:
        phi = pi.phi_from_sl_fact(fact)
        emb = pi.make_embedding(phi)
        hecke = pi.infer_hecke_signature(phi)
        selector_terms = sorted(
            {
                *(str(v).lower() for v in fact.get("arguments", {}).values()),
                *pi._norm_text(fact["predicate"]).split(),
            }
        )
        shards.append(
            pi.PrimeIndexShard(
                shard_id=f"shard::{fact['fact_id']}",
                artifact_revision="rev-1",
                selector_terms=selector_terms,
                fact_ids=[fact["fact_id"]],
                phi=phi,
                embedding=emb,
                hecke_sig=hecke,
                provenance_ids=[f"{fact['fact_id']}::span0"],
                promotion_receipts=[fact["promotion_receipt"]],
                sink_refs=[pi.SinkRef("file", str(paths[fact["fact_id"]]))],
            )
        )
    return shards


def test_retrieve_selects_grounded_match(fixture_shards: List[pi.PrimeIndexShard]) -> None:
    selector = pi.LogicalShardSelector(fixture_shards)
    cfg = pi.RetrievalConfig(min_grounded_overlap=1.0, min_domain_overlap=0, min_required_gain=0.0, cone_eps=1e6)
    signature_matrix = pi.default_signature_matrix()

    results = pi.retrieve("pet policy contract", selector, signature_matrix, cfg)
    assert results, "expected at least one admissible shard"
    shard, metrics = results[0]
    assert metrics["grounded"] >= 1.0
    assert shard.shard_id.startswith("shard::")


def test_admissible_respects_mdl_upper_bound(fixture_shards: List[pi.PrimeIndexShard]) -> None:
    selector = pi.LogicalShardSelector(fixture_shards)
    cfg = pi.RetrievalConfig(min_grounded_overlap=1.0, min_domain_overlap=0, min_required_gain=1e9, cone_eps=0.0)
    signature_matrix = pi.default_signature_matrix()

    results = pi.retrieve("pet policy contract", selector, signature_matrix, cfg)
    assert results == [], "high required gain should prune all candidates"


def test_build_zelph_input_matches_schema(fixture_shards: List[pi.PrimeIndexShard], fixture_facts: List[Dict]) -> None:
    bundle = pi.build_zelph_input(fixture_facts, fixture_shards)
    # Minimal structural checks aligned with schemas/zelph_input.schema.json
    assert bundle["provenance_mode"] == "strict"
    assert isinstance(bundle["facts"], list)
    assert isinstance(bundle["semantic_overlays"], list)

    for fact in bundle["facts"]:
        for key in ("fact_id", "predicate", "arguments", "provenance"):
            assert key in fact
        assert isinstance(fact["provenance"], list)
        assert fact["parse_tree"]["text"]
        assert isinstance(fact["parse_tree"]["sents"], list)

    for overlay in bundle["semantic_overlays"]:
        for key in ("zos_id", "kind", "members", "features", "candidate_score", "promoted"):
            assert key in overlay
        assert isinstance(overlay["members"], list)


def test_signature_matrix_learned_from_deltas(fixture_shards: List[pi.PrimeIndexShard]) -> None:
    deltas = pi._collect_fixture_deltas(fixture_shards)
    M = pi.signature_matrix_from_delta_stats(deltas, time_prime=7, space_primes=(2, 3, 5))
    assert len(M) == len(pi.PRIMES)
    assert M[pi.PRIMES.index(7)][pi.PRIMES.index(7)] < 0.0
