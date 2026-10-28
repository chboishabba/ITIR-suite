from __future__ import annotations

import math

from collections import Counter

from itir_mcp.fleet_round_runner import build_pareto_conductor_plan
from itir_mcp.pnf_spectral_packet import rank_discriminative_topic_motifs
from itir_mcp.registry import build_default_registry


def test_contrastive_tfidf_prefers_typed_frames_and_filters_generic_predicates() -> None:
    topics = [
        {"topic_id": "primary-000", "members": ["a"], "semantic_centroid": {}},
        {"topic_id": "primary-001", "members": ["b"], "semantic_centroid": {}},
        {"topic_id": "primary-002", "members": ["c"], "semantic_centroid": {}},
    ]
    frame_counts = {
        "a": Counter({
            "prove(actor:system,patient:consistency)": 6,
            "want(actor:user,patient:proof)": 40,
        }),
        "b": Counter({
            "measure(actor:sensor,patient:metric)": 6,
            "want(actor:user,patient:proof)": 40,
        }),
        "c": Counter({
            "partition(actor:graph,patient:cut)": 6,
            "want(actor:user,patient:proof)": 40,
        }),
    }
    ontology_counts = {
        "a": Counter({"ontology:quantum Fisher information": 2}),
        "b": Counter({"ontology:Riemannian metric tensor": 2}),
        "c": Counter({"ontology:max cut partition": 2}),
    }

    ranked = rank_discriminative_topic_motifs(
        topics,
        frame_counts=frame_counts,
        ontology_counts=ontology_counts,
    )

    expected = math.log(3.0 / 2.0)
    first = ranked[0]
    motifs = first["semantic_centroid"]["discriminative_motifs"]
    typed = [item for item in motifs if item["kind"] == "typed_frame"]
    external = [item for item in motifs if item["kind"] == "ontology_bridge"]

    assert first["name"].startswith("prove(actor:system,patient:consistency)")
    assert all(item["predicate"] != "want" for item in typed)
    assert abs(typed[0]["contrastive_score"] - expected) < 1e-12
    assert typed[0]["stalk_label"] == "predicate:prove"
    assert external[0]["stalk_label"] == "external:quantum Fisher information"
    assert first["motif_name_source"] == "contrastive_typed_pnf_frames_and_explicit_ontology"
    assert first["semantic_centroid"]["motif_scoring"]["typed_frames_prioritized"] is True


def test_ubiquitous_frame_is_downweighted_against_cluster_specific_frame() -> None:
    topics = [
        {"topic_id": "p0", "members": ["a"], "semantic_centroid": {}},
        {"topic_id": "p1", "members": ["b"], "semantic_centroid": {}},
        {"topic_id": "p2", "members": ["c"], "semantic_centroid": {}},
    ]
    common = "relate(actor:model,patient:state)"
    frame_counts = {
        "a": Counter({common: 9, "prove(actor:kernel,patient:theorem)": 3}),
        "b": Counter({common: 9, "measure(actor:sensor,patient:metric)": 3}),
        "c": Counter({common: 9, "partition(actor:graph,patient:cut)": 3}),
    }

    ranked = rank_discriminative_topic_motifs(
        topics,
        frame_counts=frame_counts,
        ontology_counts={"a": Counter(), "b": Counter(), "c": Counter()},
    )

    motifs = ranked[0]["semantic_centroid"]["discriminative_motifs"]
    scores = {item["label"]: item["contrastive_score"] for item in motifs}
    assert scores["prove(actor:kernel,patient:theorem)"] > 0.0
    if common in scores:
        assert scores[common] < scores["prove(actor:kernel,patient:theorem)"]


def _world_graph(topic_ids: list[str]) -> dict:
    nodes = []
    edges = []
    for index, topic_id in enumerate(topic_ids):
        left = f"{topic_id}:left"
        right = f"{topic_id}:right"
        nodes.extend([
            {"id": left, "kind": "pnf_factor"},
            {"id": right, "kind": "pnf_factor"},
        ])
        edges.append({
            "edge_ref": f"edge:{index}",
            "from_node_ref": left,
            "to_node_ref": right,
            "relation_kind": "predicate_frame",
        })
    return {
        "projection_ref": "pnf-follow:test:pareto-conductor:revision-1",
        "nodes": nodes,
        "edges": edges,
    }


def _hierarchy() -> dict:
    conversations = [f"c{index}" for index in range(6)]
    rows = [
        {
            "conversation_id": cid,
            "alpha": 1.0 - index * 0.08,
            "spectral_energy": 1.0 - index * 0.05,
            "theorem_density": 1.0 - index * 0.07,
            "formal_gap_reduction": 1.0 - index * 0.06,
        }
        for index, cid in enumerate(conversations)
    ]
    mst_edges = [
        {"left": "c0", "right": "c1", "distance": 0.05},
        {"left": "c1", "right": "c2", "distance": 0.10},
        {"left": "c3", "right": "c4", "distance": 0.06},
        {"left": "c4", "right": "c5", "distance": 0.11},
        {"left": "c2", "right": "c3", "distance": 0.80},
    ]
    primary_topics = [
        {
            "topic_id": "primary-000",
            "name": "prove(actor:system,patient:consistency)",
            "members": ["c0", "c1", "c2"],
            "alpha": {
                "mean": 0.90,
                "max": 1.0,
                "spectral_energy_mean": 0.92,
                "theorem_density_mean": 0.88,
                "formal_gap_reduction_mean": 0.86,
            },
        },
        {
            "topic_id": "primary-001",
            "name": "measure(actor:sensor,patient:metric)",
            "members": ["c3", "c4", "c5"],
            "alpha": {
                "mean": 0.62,
                "max": 0.76,
                "spectral_energy_mean": 0.70,
                "theorem_density_mean": 0.55,
                "formal_gap_reduction_mean": 0.58,
            },
        },
    ]
    subtopics = [
        {
            "topic_id": "primary-000.sub-000",
            "parent_id": "primary-000",
            "name": "prove(actor:kernel,patient:theorem)",
            "members": ["c0", "c1"],
            "alpha": {
                "mean": 0.95,
                "max": 1.0,
                "spectral_energy_mean": 0.96,
                "theorem_density_mean": 0.94,
                "formal_gap_reduction_mean": 0.92,
            },
        },
        {
            "topic_id": "primary-000.sub-001",
            "parent_id": "primary-000",
            "name": "verify(actor:checker,patient:proof)",
            "members": ["c2"],
            "alpha": {
                "mean": 0.76,
                "max": 0.76,
                "spectral_energy_mean": 0.80,
                "theorem_density_mean": 0.72,
                "formal_gap_reduction_mean": 0.70,
            },
        },
        {
            "topic_id": "primary-001.sub-000",
            "parent_id": "primary-001",
            "name": "measure(actor:sensor,patient:metric)",
            "members": ["c3", "c4", "c5"],
            "alpha": {
                "mean": 0.62,
                "max": 0.70,
                "spectral_energy_mean": 0.70,
                "theorem_density_mean": 0.55,
                "formal_gap_reduction_mean": 0.58,
            },
        },
    ]
    return {
        "conversation_rows": rows,
        "mst_edges": mst_edges,
        "thresholds": {
            "fibre_tau": 0.06,
            "subtopic_tau": 0.12,
            "primary_tau": 0.80,
        },
        "primary_topics": primary_topics,
        "subtopics": subtopics,
    }


def _candidate_lanes() -> dict:
    topic_ids = [
        "primary-000",
        "primary-001",
        "primary-000.sub-000",
        "primary-000.sub-001",
        "primary-001.sub-000",
    ]
    graph = _world_graph(topic_ids)
    lanes = {}
    for index, topic_id in enumerate(topic_ids):
        lanes[topic_id] = {
            "orchestrator_id": f"worker-{index}",
            "lane": f"lane.{index}",
            "lane_claim": f"Complete topic {topic_id}.",
            "typed_support": {
                "files": [f"src/topic_{index}.py"],
                "symbols": [f"topic_{index}"],
                "lemmas": [f"lemma_{index}"],
            },
            "world_graph": graph,
            "graph_anchor_ids": [f"{topic_id}:left"],
            "typed_signatures": [f"topic-{index}|actor,theme"],
        }
    return lanes


def test_conductor_primary_roll_for_constrained_workers() -> None:
    plan = build_pareto_conductor_plan(
        _hierarchy(),
        2,
        candidate_lanes=_candidate_lanes(),
    )

    assert plan["mode"] == "primary_roll"
    assert plan["worker_capacity"] == 2
    assert plan["prepared_lane_count"] == 2
    assert plan["pairwise_noTypedMeet_verified"] is True
    assert plan["selected_topics"][0]["topic_id"] == "primary-000"
    first_lane = plan["lanes"][0]
    assert [packet["topic_id"] for packet in first_lane["internal_work_packets"]] == [
        "primary-000.sub-000",
        "primary-000.sub-001",
    ]
    assert "Execute in this order" in first_lane["prompt"]


def test_conductor_w20_branches_independent_subtopics_in_alpha_pareto_order() -> None:
    plan = build_pareto_conductor_plan(
        _hierarchy(),
        20,
        candidate_lanes=_candidate_lanes(),
    )

    assert plan["mode"] == "independent_subtopics"
    assert plan["worker_capacity"] == 20
    assert plan["pairwise_noTypedMeet_verified"] is True
    assert plan["dispatchable_lane_count"] == 3
    assert [topic["topic_id"] for topic in plan["selected_topics"]] == [
        "primary-000.sub-000",
        "primary-000.sub-001",
        "primary-001.sub-000",
    ]
    assert all(not lane["internal_work_packets"] for lane in plan["lanes"])


def test_conductor_caps_workers_at_twenty() -> None:
    try:
        build_pareto_conductor_plan(_hierarchy(), 21, candidate_lanes=_candidate_lanes())
    except ValueError as exc:
        assert "within [1, 20]" in str(exc)
    else:
        raise AssertionError("worker capacity above 20 must fail")


def test_pareto_conductor_is_registered() -> None:
    registry = build_default_registry()
    spec = registry.get_tool_spec("itir.ao.pareto_conductor")

    assert spec is not None
    assert spec.read_only is False
    assert spec.input_schema["properties"]["worker_capacity"]["maximum"] == 20
