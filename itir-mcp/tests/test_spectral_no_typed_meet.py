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


def _lane(
    name: str,
    frame: dict,
    *,
    support: str,
    scale: int = 0,
    status: str = "dev",
    schema_altering: bool = False,
) -> dict:
    return {
        "orchestrator_id": name,
        "typed_support": {"files": [support], "symbols": [], "lemmas": []},
        "relational_frames": [frame],
        "carrier": {"scale": scale, "status": status},
        "mutation": {"schema_altering": schema_altering},
    }


def test_slr_and_sensiblaw_shared_frames_have_macroscopic_meet_without_name_rules() -> None:
    shared = _frame("persist", "world_store", "relational_schema")
    carrier = _lane("carrier-root", shared, support="crates/world_store.rs", scale=0, status="prod")
    projection = _lane("projection-fiber", shared, support="src/projection.py", scale=1)

    receipt = spectral_no_typed_meet(carrier, projection)

    assert receipt["cosine_similarity"] > 0.15
    assert receipt["shared_quotient_orbit"] is True
    assert receipt["meet_macro_disjoint"] is False
    assert receipt["admissible"] is False
    assert receipt["formal_boundary"]["quotient_projection_equality_proved"] is False


def test_orthogonal_balaban_and_quantum_metrology_frames_are_no_typed_meet() -> None:
    ym = _lane(
        "balaban-ym",
        _frame("renormalize", "polymer", "gauge_block"),
        support="DASHI/Physics/YM.agda",
    )
    metrology = _lane(
        "quantum-metrology",
        _frame("estimate", "sensor", "fisher_metric"),
        support="DASHI/Physics/QuantumMetrology.agda",
    )

    receipt = spectral_no_typed_meet(ym, metrology)

    assert receipt["cosine_similarity"] == 0.0
    assert receipt["shared_quotient_orbit"] is False
    assert receipt["meet_macro_disjoint"] is True
    assert receipt["admissible"] is True


def test_prod_carrier_schema_mutation_is_illegal_defect() -> None:
    shared = _frame("persist", "world_store", "relational_schema")
    root = _lane(
        "root",
        shared,
        support="crates/world_store.rs",
        scale=0,
        status="prod",
    )
    downstream = _lane(
        "fiber",
        shared,
        support="src/projection.py",
        scale=2,
        schema_altering=True,
    )

    receipt = spectral_no_typed_meet(root, downstream)

    assert receipt["carrier_scale_delta"] == 2.0
    assert receipt["prod_invariant_violation"] is True
    assert receipt["defect_status"] == "illegalDefect"
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
    shared = _frame("persist", "world_store", "relational_schema")
    left = _lane("left", shared, support="src/left.py")
    right = _lane("right", shared, support="src/right.py")

    try:
        fleet_round_runner._verify_pairwise_no_typed_meet([left, right])
    except ValueError as exc:
        assert "spectral noTypedMeet violation" in str(exc)
    else:
        raise AssertionError("shared quotient orbit must block parallel dispatch")


def test_balaban_and_quantum_metrology_wikidata_bridge_coupling() -> None:
    ym_bridged = {
        "orchestrator_id": "balaban-ym",
        "typed_support": {"files": ["DASHI/Physics/YM.agda"], "symbols": [], "lemmas": []},
        "relational_frames": [_frame("renormalize", "polymer", "gauge_block")],
        "wikidata_features": [
            "Q208227",  # gauge theory / connection form
            "Q171448",  # metric tensor / Riemannian metric
            "information_geometry:fisher_metric_flow",
        ],
    }

    qm_bridged = {
        "orchestrator_id": "quantum-metrology",
        "typed_support": {"files": ["DASHI/Physics/QuantumMetrology.agda"], "symbols": [], "lemmas": []},
        "relational_frames": [_frame("estimate", "sensor", "fisher_metric")],
        "wikidata_features": [
            "Q11455",   # Quantum Fisher Information
            "Q11108",   # Nitrogen-vacancy center
            "Q171448",  # metric tensor / Fubini-Study
            "information_geometry:fisher_metric_flow",
        ],
    }

    receipt = spectral_no_typed_meet(ym_bridged, qm_bridged)

    assert receipt["cosine_similarity"] > 0.15
    assert receipt["orbit_relation"] == "shared_quotient_orbit"
    assert "q171448" in receipt["shared_world_features"]
    assert "information_geometry:fisher_metric_flow" in receipt["shared_world_features"]
    assert receipt["sub_eigen_applicable"] is True
    assert receipt["sub_eigen_meet"] == "noTypedMeet"
    assert receipt["residual_status"] == "noTypedMeet"
    assert receipt["formal_boundary"]["no_typed_meet_is_sub_eigen_residual"] is True

