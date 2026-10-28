from __future__ import annotations

from itir_mcp import fleet_round_runner
from itir_mcp.pnf_spectral_packet import extract_relational_frames, spectral_no_typed_meet


def _frame(predicate: str, actor: str, theme: str) -> dict:
    return {
        "predicate": predicate,
        "arguments": {
            "actor": [actor],
            "theme": [theme],
        },
        "boundary_metadata": [],
    }


def _real_world_graph() -> dict:
    nodes = [
        {"id": "source:ym", "kind": "source_manifestation"},
        {"id": "pnf:ym", "kind": "pnf_candidate"},
        {"id": "atom:ym", "kind": "world_atom"},
        {"id": "source:metrology", "kind": "source_manifestation"},
        {"id": "pnf:metrology", "kind": "pnf_candidate"},
        {"id": "atom:metrology", "kind": "world_atom"},
        {"id": "ontology:gauge", "kind": "external_graph_entity"},
        {"id": "ontology:metric", "kind": "external_graph_entity"},
        {"id": "ontology:curvature", "kind": "external_graph_entity"},
        {"id": "ontology:fisher", "kind": "external_graph_entity"},
        {"id": "ontology:information-geometry", "kind": "external_graph_entity"},
        {"id": "ontology:nv-center", "kind": "external_graph_entity"},
        {"id": "ontology:rg-flow", "kind": "external_graph_entity"},
        {"id": "ontology:two-point", "kind": "external_graph_entity"},
        {"id": "ontology:riemannian", "kind": "external_graph_entity"},
    ]
    edges = [
        {"edge_ref": "e01", "relation_kind": "source_to_pnf", "from_node_ref": "source:ym", "to_node_ref": "pnf:ym", "provenance_ref": "slr-world-v2"},
        {"edge_ref": "e02", "relation_kind": "pnf_to_atom", "from_node_ref": "pnf:ym", "to_node_ref": "atom:ym", "provenance_ref": "slr-world-v2"},
        {"edge_ref": "e03", "relation_kind": "external_bridge", "from_node_ref": "atom:ym", "to_node_ref": "ontology:gauge", "provenance_ref": "reviewed-world-bridge"},
        {"edge_ref": "e04", "relation_kind": "external_bridge", "from_node_ref": "atom:ym", "to_node_ref": "ontology:curvature", "provenance_ref": "reviewed-world-bridge"},
        {"edge_ref": "e05", "relation_kind": "external_bridge", "from_node_ref": "atom:ym", "to_node_ref": "ontology:rg-flow", "provenance_ref": "reviewed-world-bridge"},
        {"edge_ref": "e06", "relation_kind": "external_bridge", "from_node_ref": "atom:ym", "to_node_ref": "ontology:two-point", "provenance_ref": "reviewed-world-bridge"},
        {"edge_ref": "e07", "relation_kind": "source_to_pnf", "from_node_ref": "source:metrology", "to_node_ref": "pnf:metrology", "provenance_ref": "slr-world-v2"},
        {"edge_ref": "e08", "relation_kind": "pnf_to_atom", "from_node_ref": "pnf:metrology", "to_node_ref": "atom:metrology", "provenance_ref": "slr-world-v2"},
        {"edge_ref": "e09", "relation_kind": "external_bridge", "from_node_ref": "atom:metrology", "to_node_ref": "ontology:fisher", "provenance_ref": "reviewed-world-bridge"},
        {"edge_ref": "e10", "relation_kind": "external_bridge", "from_node_ref": "atom:metrology", "to_node_ref": "ontology:information-geometry", "provenance_ref": "reviewed-world-bridge"},
        {"edge_ref": "e11", "relation_kind": "external_bridge", "from_node_ref": "atom:metrology", "to_node_ref": "ontology:nv-center", "provenance_ref": "reviewed-world-bridge"},
        {"edge_ref": "e12", "relation_kind": "ontology_relation", "from_node_ref": "ontology:fisher", "to_node_ref": "ontology:metric", "provenance_ref": "revision-pinned-external-graph"},
        {"edge_ref": "e13", "relation_kind": "ontology_relation", "from_node_ref": "ontology:information-geometry", "to_node_ref": "ontology:metric", "provenance_ref": "revision-pinned-external-graph"},
        {"edge_ref": "e14", "relation_kind": "ontology_relation", "from_node_ref": "ontology:metric", "to_node_ref": "ontology:riemannian", "provenance_ref": "revision-pinned-external-graph"},
        {"edge_ref": "e15", "relation_kind": "ontology_relation", "from_node_ref": "ontology:gauge", "to_node_ref": "ontology:riemannian", "provenance_ref": "revision-pinned-external-graph"},
        {"edge_ref": "e16", "relation_kind": "ontology_relation", "from_node_ref": "ontology:curvature", "to_node_ref": "ontology:gauge", "provenance_ref": "revision-pinned-external-graph"},
        {"edge_ref": "e17", "relation_kind": "reviewed_cross_bridge", "from_node_ref": "ontology:two-point", "to_node_ref": "ontology:fisher", "provenance_ref": "reviewed-world-bridge"},
    ]
    return {
        "projection_ref": "pnf-follow:test:ym-metrology:revision-1",
        "nodes": nodes,
        "edges": edges,
    }


def _disconnected_world_graph() -> dict:
    return {
        "projection_ref": "pnf-follow:test:fractran-fluid:revision-1",
        "nodes": [
            {"id": "source:fractran", "kind": "source_manifestation"},
            {"id": "pnf:fractran", "kind": "pnf_candidate"},
            {"id": "atom:fractran", "kind": "world_atom"},
            {"id": "source:fluid", "kind": "source_manifestation"},
            {"id": "pnf:fluid", "kind": "pnf_candidate"},
            {"id": "atom:fluid", "kind": "world_atom"},
        ],
        "edges": [
            {"edge_ref": "f1", "from_node_ref": "source:fractran", "to_node_ref": "pnf:fractran", "relation_kind": "source_to_pnf"},
            {"edge_ref": "f2", "from_node_ref": "pnf:fractran", "to_node_ref": "atom:fractran", "relation_kind": "pnf_to_atom"},
            {"edge_ref": "g1", "from_node_ref": "source:fluid", "to_node_ref": "pnf:fluid", "relation_kind": "source_to_pnf"},
            {"edge_ref": "g2", "from_node_ref": "pnf:fluid", "to_node_ref": "atom:fluid", "relation_kind": "pnf_to_atom"},
        ],
    }


def _lane(
    name: str,
    frame: dict,
    *,
    support: str,
    anchor: str,
    world_graph: dict,
    scale: int = 0,
    status: str = "dev",
    schema_altering: bool = False,
    typed_signatures: list[str] | None = None,
) -> dict:
    return {
        "orchestrator_id": name,
        "typed_support": {"files": [support], "symbols": [], "lemmas": []},
        "relational_frames": [frame],
        "typed_signatures": typed_signatures or [],
        "world_graph": world_graph,
        "graph_anchor_ids": [anchor],
        "carrier": {"scale": scale, "status": status},
        "mutation": {"schema_altering": schema_altering},
    }

def test_shared_real_world_graph_detects_macroscopic_meet_without_name_rules() -> None:
    graph = _real_world_graph()
    carrier = _lane(
        "carrier-root",
        _frame("persist", "world_store", "relational_schema"),
        support="crates/world_store.rs",
        anchor="atom:ym",
        world_graph=graph,
        scale=0,
        status="prod",
    )
    projection = _lane(
        "projection-fiber",
        _frame("estimate", "sensor", "metric"),
        support="src/projection.py",
        anchor="atom:metrology",
        world_graph=graph,
        scale=1,
    )

    receipt = spectral_no_typed_meet(carrier, projection)

    assert 0.0 < receipt["cosine_similarity"] < 1.0
    assert receipt["shared_quotient_orbit"] is True
    assert receipt["meet_macro_disjoint"] is False
    assert receipt["spectral_grounding"]["source"] == "real_pnf_world_graph"
    assert receipt["spectral_grounding"]["real_world_graph"] is True
    assert receipt["spectral_grounding"]["connecting_path"]
    assert receipt["formal_boundary"]["quotient_projection_equality_proved"] is False


def test_balaban_and_quantum_metrology_coupling_comes_from_real_graph_paths() -> None:
    graph = _real_world_graph()
    ym = _lane(
        "balaban-ym",
        _frame("renormalize", "polymer", "gauge_block"),
        support="DASHI/Physics/YM.agda",
        anchor="atom:ym",
        world_graph=graph,
        typed_signatures=["renormalize|actor,theme"],
    )
    metrology = _lane(
        "quantum-metrology",
        _frame("estimate", "sensor", "fisher_metric"),
        support="DASHI/Physics/QuantumMetrology.agda",
        anchor="atom:metrology",
        world_graph=graph,
        typed_signatures=["estimate|actor,theme"],
    )

    receipt = spectral_no_typed_meet(ym, metrology)

    assert abs(receipt["cosine_similarity"] - 0.45414567507874104) < 1e-9
    assert abs(receipt["cosine_similarity"] - 0.5) > 1e-3
    assert receipt["orbit_relation"] == "shared_quotient_orbit"
    assert receipt["sub_eigen_meet"] == "noTypedMeet"
    assert receipt["sub_eigen_applicable"] is True
    grounding = receipt["spectral_grounding"]
    assert grounding["node_count"] == 15
    assert grounding["hyperedge_count"] == 17
    assert grounding["decomposition"] == "deterministic_one_sided_jacobi_svd"
    assert all(0.0 <= value <= 1.0 + 1e-12 for value in grounding["singular_values"])
    assert all(-1e-12 <= value <= 1.0 + 1e-12 for value in grounding["laplacian_eigenvalues"])
    assert grounding["connecting_path"][0] == "atom:ym"
    assert grounding["connecting_path"][-1] == "atom:metrology"
    assert len(grounding["singular_values"]) >= 4
    assert receipt["admissible"] is False


def test_fractran_and_fluid_enstrophy_remain_macro_orthogonal() -> None:
    graph = _disconnected_world_graph()
    fractran = _lane(
        "fractran",
        _frame("multiply", "register", "prime"),
        support="DASHI/Computation/FRACTRAN.agda",
        anchor="atom:fractran",
        world_graph=graph,
        typed_signatures=["multiply|register"],
    )
    fluid = _lane(
        "fluid-enstrophy",
        _frame("transport", "vorticity", "enstrophy"),
        support="DASHI/Physics/Fluid.agda",
        anchor="atom:fluid",
        world_graph=graph,
        typed_signatures=["transport|vorticity"],
    )

    receipt = spectral_no_typed_meet(fractran, fluid)

    assert receipt["cosine_similarity"] < 1e-12
    assert receipt["orbit_relation"] == "orthogonal_domains"
    assert receipt["meet_macro_disjoint"] is True
    assert receipt["sub_eigen_applicable"] is False
    assert receipt["residual_status"] == "not_applicable"
    assert receipt["spectral_grounding"]["connecting_path"] == []
    assert receipt["admissible"] is True


def test_prod_carrier_schema_mutation_is_illegal_defect() -> None:
    graph = _real_world_graph()
    shared = _frame("persist", "world_store", "relational_schema")
    root = _lane(
        "root",
        shared,
        support="crates/world_store.rs",
        anchor="atom:ym",
        world_graph=graph,
        scale=0,
        status="prod",
    )
    downstream = _lane(
        "fiber",
        shared,
        support="src/projection.py",
        anchor="atom:metrology",
        world_graph=graph,
        scale=2,
        schema_altering=True,
    )

    receipt = spectral_no_typed_meet(root, downstream)

    assert receipt["carrier_scale_delta"] == 2.0
    assert receipt["prod_invariant_violation"] is True
    assert receipt["defect_status"] == "illegalDefect"
    assert receipt["residual_status"] == "contradiction"
    assert receipt["pressure_status"] == "critical"
    assert receipt["zoom_out_accommodates"] is False
    assert receipt["admissible"] is False
    assert receipt["formal_boundary"]["illegal_defect_maps_to_contradiction_and_critical_pressure_in_agda"] is True


def test_relational_frames_keep_domain_arguments_and_move_wrappers_to_boundary_metadata() -> None:
    slots = [
        {
            "slot_id": "s0",
            "sentence_id": "sentence-1",
            "head_ordinal": 3,
            "head_lemma": "prove",
            "lemma": "you",
            "is_boundary": True,
            "boundary_kind": "dialogue_deictic",
        },
        {
            "slot_id": "s1",
            "sentence_id": "sentence-1",
            "head_ordinal": 3,
            "head_lemma": "prove",
            "lemma": "i",
            "is_boundary": True,
            "boundary_kind": "dialogue_deictic",
        },
        {
            "slot_id": "s2",
            "sentence_id": "sentence-1",
            "head_ordinal": 3,
            "head_lemma": "prove",
            "lemma": "to",
            "is_boundary": True,
            "boundary_kind": "auxiliary",
        },
        {
            "slot_id": "s3",
            "sentence_id": "sentence-1",
            "head_ordinal": 3,
            "head_lemma": "prove",
            "lemma": "system",
            "argument_role": "actor",
        },
        {
            "slot_id": "s4",
            "sentence_id": "sentence-1",
            "head_ordinal": 3,
            "head_lemma": "prove",
            "lemma": "consistency",
            "argument_role": "theme",
        },
    ]

    frames = extract_relational_frames(slots)

    assert len(frames) == 1
    frame = frames[0]
    assert frame["predicate"] == "prove"
    assert frame["arguments"] == {"actor": ["system"], "theme": ["consistency"]}
    assert [item["lemma"] for item in frame["boundary_metadata"]] == ["you", "i", "to"]
    assert [item["boundary_kind"] for item in frame["boundary_metadata"]] == [
        "dialogue_deictic",
        "dialogue_deictic",
        "auxiliary",
    ]


def test_fleet_verifier_rejects_shared_quotient_orbit_with_disjoint_flat_keys() -> None:
    graph = _real_world_graph()
    shared = _frame("persist", "world_store", "relational_schema")
    left = _lane("left", shared, support="src/left.py", anchor="atom:ym", world_graph=graph)
    right = _lane("right", shared, support="src/right.py", anchor="atom:metrology", world_graph=graph)

    try:
        fleet_round_runner._verify_pairwise_no_typed_meet([left, right])
    except ValueError as exc:
        assert "spectral noTypedMeet violation" in str(exc)
    else:
        raise AssertionError("shared quotient orbit must block parallel dispatch")


def test_no_typed_meet_is_sub_eigen_not_macro_orthogonality() -> None:
    graph = _real_world_graph()
    left = _lane(
        "left",
        _frame("prove", "system", "consistency"),
        support="src/left.py",
        anchor="atom:ym",
        world_graph=graph,
        typed_signatures=["prove|actor"],
    )
    right = _lane(
        "right",
        _frame("measure", "sensor", "metric"),
        support="src/right.py",
        anchor="atom:metrology",
        world_graph=graph,
        typed_signatures=["measure|theme"],
    )

    receipt = spectral_no_typed_meet(left, right)

    assert receipt["orbit_relation"] == "shared_quotient_orbit"
    assert receipt["sub_eigen_meet"] == "noTypedMeet"
    assert receipt["meet_macro_disjoint"] is False
    assert receipt["residual_status"] == "noTypedMeet"


def test_default_spectral_engine_rejects_synthetic_feature_only_input() -> None:
    left = {
        "orchestrator_id": "left",
        "typed_support": {"files": ["a"], "symbols": [], "lemmas": []},
        "world_features": ["fake:a", "fake:b"],
    }
    right = {
        "orchestrator_id": "right",
        "typed_support": {"files": ["b"], "symbols": [], "lemmas": []},
        "world_features": ["fake:b", "fake:c"],
    }

    try:
        spectral_no_typed_meet(left, right)
    except ValueError as exc:
        assert "real world_graph is required" in str(exc)
    else:
        raise AssertionError("synthetic feature lists must not create spectral geometry")
