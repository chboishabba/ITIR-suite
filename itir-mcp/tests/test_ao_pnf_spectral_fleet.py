from __future__ import annotations

import inspect
from types import SimpleNamespace

import pytest

from itir_mcp import pnf_spectral_packet as packet
from itir_mcp.fleet_round_runner import (
    conductor_topic_cost,
    execute_pareto_conductor,
    plan_fleet_round_barriers,
    spawn_parallel_lanes,
)


def _parser_for(pos: str):
    def parse(text: str):
        return {
            "text": text,
            "sents": [{
                "tokens": [{
                    "text": text,
                    "lemma": text.casefold(),
                    "pos": pos,
                }]
            }],
        }
    return parse


@pytest.mark.parametrize("pos", ["PROPN", "NOUN"])
def test_pos_gate_retains_substantive_heads(pos: str) -> None:
    result = packet.validate_pnf_candidate(
        "YangMillsMassGap",
        parser=_parser_for(pos),
        document_frequency=2,
        document_count=20,
        eigenvalue=3.0,
        lambda_plus=2.75,
    )
    assert result["accepted"] is True
    assert result["spectral_retained"] is True
    assert result["df_ratio"] == pytest.approx(0.1)


@pytest.mark.parametrize("pos", ["ADP", "CCONJ", "SCONJ", "DET", "PRON", "PUNCT"])
def test_pos_gate_rejects_particle_only_heads(pos: str) -> None:
    result = packet.validate_pnf_candidate("noise", parser=_parser_for(pos))
    assert result["accepted"] is False
    assert result["reason"] == "grammatical_particle_noise"


def test_ast_and_supplied_qid_are_explicit_substantive_evidence() -> None:
    ast = packet.validate_pnf_candidate(
        "MixedPlaquettesFaceAction",
        ast_symbols=["MixedPlaquettesFaceAction"],
        parser=None,
    )
    qid = packet.validate_pnf_candidate(
        "Q271810",
        ontology_qids=["Q271810"],
        parser=None,
    )
    assert ast["accepted"] is True
    assert ast["explicit_ast_symbol"] is True
    assert qid["accepted"] is True
    assert qid["explicit_ontology_qid"] is True


def test_df_and_mp_noise_cuts_are_data_driven() -> None:
    ubiquitous = packet.validate_pnf_candidate(
        "entity",
        parser=_parser_for("NOUN"),
        document_frequency=20,
        document_count=20,
    )
    bulk = packet.validate_pnf_candidate(
        "entity",
        parser=_parser_for("NOUN"),
        eigenvalue=2.75,
        lambda_plus=2.75,
    )
    assert ubiquitous["accepted"] is False
    assert ubiquitous["reason"] == "ubiquitous_document_frequency"
    assert bulk["accepted"] is False
    assert bulk["reason"] == "marchenko_pastur_bulk"


def test_no_ad_hoc_lexical_wordlists_remain_in_packet() -> None:
    source = inspect.getsource(packet)
    for name in (
        "GENERIC_CONVERSATIONAL_PREDICATES",
        "_HEAD_PARTICLES",
        "_HEAD_FUNCTION_WORDS",
        "_DOMAIN_HEADS",
    ):
        assert name not in source


@pytest.mark.parametrize("k", [50, 100])
def test_hierarchy_metadata_keeps_five_distinct_levels(k: int) -> None:
    result = packet.validate_pnf_hierarchy_metadata({
        "k": k,
        "eigenspace": [{"eigenvalue": 4.0}],
        "primary_topics": [{"id": "primary:ym"}],
        "subtopics": [{"id": "sub:ym:lattice"}],
        "fibres": [{"id": "F_YM"}],
        "goals": [{"id": "goal:slab"}],
    })
    assert result["k"] == k
    assert result["level_counts"] == {
        "eigenspace": 1,
        "primary_topics": 1,
        "subtopics": 1,
        "fibres": 1,
        "goals": 1,
    }


def test_yang_mills_branches_inherit_one_non_promoting_fibre() -> None:
    bundle = packet.build_invariant_fibre_bundle(
        root_qid="Q271810", root_label="Yang-Mills Theory", fibre_id="F_YM",
        branches=packet.derive_fibre_branches("Q271810", sub_eigens=[{"id": "lattice-transfer", "motif_name": "lattice_transfer_matrix"}, {"id": "continuum-curvature", "motif_name": "continuum_curvature_holonomy"}, {"id": "constructive-agda", "motif_name": "constructive_agda_types"}]),
        invariants=[{
            "invariant_id": "SpatialOnlyBlocking",
            "source_ref": "dashi_agda:DASHI/Physics/YangMills/SpatialOnlyBlocking.agda",
            "verified": True,
        }]
    )
    assert bundle["root"] == {"qid": "Q271810", "label": "Yang-Mills Theory"}
    assert {row["fibre_id"] for row in bundle["branches"]} == {"F_YM"}
    assert {row["representation"] for row in bundle["branches"]} == {
        "lattice_transfer_matrix",
        "continuum_curvature_holonomy",
        "constructive_agda_types",
    }
    routes = packet.fibre_invariant_routes(bundle, "eigen:lattice-transfer")
    assert {row["to_branch"] for row in routes} == {
        "eigen:continuum-curvature",
        "eigen:constructive-agda",
    }
    assert all(row["promotion"] == "requires_explicit_formal_bridge" for row in routes)


class _Demand:
    def __init__(self, *, demand_ref, subject_ref, surface, demand_kind, language):
        self.demand_ref = demand_ref
        self.subject_ref = subject_ref
        self.surface = surface
        self.demand_kind = demand_kind
        self.language = language
        self.lookup_key = f"{demand_kind}:{surface.casefold()}"


class _Provider:
    def __init__(self, external_id: str | None):
        self.external_id = external_id

    def lookup_batch(self, demands, *, request_budget, progress_stream):
        result = {}
        for demand in demands:
            candidates = ()
            if self.external_id is not None:
                candidates = ({
                    "external_id": self.external_id,
                    "label": demand.surface,
                    "candidate_kind": "test_candidate",
                },)
            result[demand.lookup_key] = SimpleNamespace(
                lookup_key=demand.lookup_key,
                provider_ref="test-provider",
                candidates=candidates,
                snapshot_refs=(),
                request_receipts=(),
            )
        return result


@pytest.mark.parametrize(
    ("surface", "qid"),
    [
        ("Yang-Mills", "Q271810"),
        ("Navier-Stokes", "Q215282"),
        ("Max Cut", "Q5577665"),
        ("Spectral gap", "Q7575317"),
    ],
)
def test_wikimedia_pipeline_projects_permanent_qids(monkeypatch, surface: str, qid: str) -> None:
    monkeypatch.setattr(
        packet,
        "_sensiblaw_wikimedia_dependencies",
        lambda: (_Demand, _Provider, _Provider),
    )
    result = packet.ground_wikimedia_surface(
        surface,
        subject_ref=f"topic:{qid}",
        wikidata_provider=_Provider(qid),
        wiktionary_provider=_Provider(None),
    )
    assert result["permanent_qids"] == [qid]
    assert result["authority"] == "candidate_only"
    assert result["identity_closed"] is False


def test_frontier_candidate_consumes_observational_disjointness_report(monkeypatch) -> None:
    from itir_mcp import wikidata_disjointness_tool

    monkeypatch.setattr(
        wikidata_disjointness_tool,
        "wikidata_disjointness_report",
        lambda _payload: {
            "summary": {
                "subclass_violations_count": 0,
                "instance_violations_count": 0,
            },
            "authority_boundary": {"candidate_only": True},
        },
    )
    candidate = packet.mint_frontier_qid_candidate(
        "CKN-Leray critical Besov rung",
        anchors=[{"property": "P279", "target": "Q7575317"}],
        disjointness_payload={"slice_data": {"windows": []}},
    )
    assert candidate["disjointness_clear"] is True
    assert candidate["promotion_authority"] is False


def test_frontier_candidate_is_deterministic_and_non_promoting() -> None:
    first = packet.mint_frontier_qid_candidate(
        "all-diameter weighted polymer bounds",
        anchors=[
            {"property": "P279", "target": "Q7575317"},
            {"property": "P361", "target": "Q271810"},
        ],
    )
    second = packet.mint_frontier_qid_candidate(
        "all-diameter weighted polymer bounds",
        anchors=[
            {"property": "P361", "target": "Q271810"},
            {"property": "P279", "target": "Q7575317"},
        ],
    )
    assert first["candidate_id"] == second["candidate_id"]
    assert first["candidate_id"].startswith("cand:Q_")
    assert first["wikidata_entity_created"] is False
    assert first["promotion_authority"] is False


def test_ontology_walk_routes_verified_lemma_across_p361_p279() -> None:
    edges = [
        {"source": "Q271810", "property": "P361", "target": "Q253567"},
        {"source": "Q253567", "property": "P279", "target": "Q180929"},
    ]
    routed = packet.route_verified_lemmas(
        "Q271810",
        edges,
        [{
            "qid": "Q180929",
            "lemma_ref": "LieGroupCompactness",
            "source_ref": "dashi_agda:DASHI/Geometry/LieGroupCompactness.agda",
            "verified": True,
        }],
    )
    assert routed["routes"][0]["qid"] == "Q180929"
    assert [edge["property"] for edge in routed["routes"][0]["path"]] == ["P361", "P279"]
    assert routed["routes"][0]["promotion"] == "reuse_candidate_requires_typecheck"


def _lane(round_index: int, lane_index: int) -> dict:
    lane_id = f"r{round_index:02d}-w{lane_index:02d}"
    return {
        "orchestrator_id": lane_id,
        "alpha": 1.0 - lane_index / 100.0,
        "pareto_rank": lane_index // 5,
        "unblocked": True,
        "typed_support": {
            "files": [f"DASHI/Round{round_index}/Worker{lane_index}.agda"],
            "symbols": [f"lemma_{round_index}_{lane_index}"],
            "lemmas": [f"goal_{round_index}_{lane_index}"],
        },
    }


def test_twenty_rounds_of_twenty_workers_plan_four_hundred_calls() -> None:
    frontiers = [[_lane(r, w) for w in range(20)] for r in range(20)]
    receipts = {}
    for frontier in frontiers:
        ids = [lane["orchestrator_id"] for lane in frontier]
        for i, left in enumerate(ids):
            for right in ids[i + 1:]:
                receipts["|".join(sorted((left, right)))] = True
    plan = plan_fleet_round_barriers(
        frontiers,
        no_typed_meet_receipts=receipts,
    )
    assert plan["round_count"] == 20
    assert plan["total_planned_worker_calls"] == 400
    assert plan["maximum_possible_calls"] == 400
    assert all(row["selected_count"] == 20 for row in plan["rounds"])
    assert plan["dispatch_performed"] is False


def test_round_planner_fails_closed_on_missing_pairwise_proof() -> None:
    plan = plan_fleet_round_barriers(
        [[_lane(0, 0), _lane(0, 1)]],
        no_typed_meet_receipts={},
    )
    assert plan["rounds"][0]["selected_count"] == 1
    assert plan["rounds"][0]["held"][0]["reason"] == "missing_noTypedMeet_proof"


def test_live_runner_contracts_remain_present() -> None:
    assert callable(execute_pareto_conductor)
    assert callable(spawn_parallel_lanes)
    topic = {
        "alpha": {"mean": 0.5},
        "total_goals": 2,
        "unblocked_goals": 1,
        "sub_eigen_dimension": 4,
        "token_cost_per_worker": 0.0,
    }
    receipt = conductor_topic_cost(topic, 2, worker_cap=20)
    assert receipt["formula"] == (
        "alpha*(unblocked_goals/total_goals)*min(worker_cap,sub_eigen_dimension)"
        "-token_cost(worker_count)"
    )


def test_spawn_parallel_lanes_rejects_more_than_twenty_before_dispatch() -> None:
    lanes = [
        {
            "orchestrator_id": f"lane-{index}",
            "prompt": "noop",
            "typed_support": {
                "files": [f"file-{index}.agda"],
                "symbols": [f"symbol-{index}"],
                "lemmas": [f"lemma-{index}"],
            },
        }
        for index in range(21)
    ]
    workers = [{"conversation_id": f"worker-{index}"} for index in range(21)]
    with pytest.raises(ValueError, match="at most 20"):
        spawn_parallel_lanes(lanes, workers)


def test_labelled_instance_subclass_path() -> None:
    edges = [{"source": "Q1192873", "property": "P31", "target": "Q214850"}, {"source": "Q214850", "property": "P279", "target": "Q1262328"}]
    walk = packet.walk_ontology_dag("Q1192873", edges)
    assert [edge["property_label"] for edge in walk["paths"]["Q1262328"]] == ["instance of", "subclass of"]
    assert walk["formatted_paths"]["Q1262328"] == "Q1192873 --P31 (instance of)--> Q214850 --P279 (subclass of)--> Q1262328"
