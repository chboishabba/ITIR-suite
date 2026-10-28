from __future__ import annotations

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
