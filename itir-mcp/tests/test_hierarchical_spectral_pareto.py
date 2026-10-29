from __future__ import annotations

import math
import struct
from pathlib import Path

from itir_mcp.fleet_round_runner import allocate_hierarchical_spectral_workers
from itir_mcp.pnf_spectral_packet import (
    build_hierarchical_pnf_topics,
    load_slrw_conversation_factors,
)
from itir_mcp.spectral_plot_tools import (
    generate_hierarchical_corpus_visualizations,
    project_slrw_hierarchy_to_docs,
    render_hierarchical_spectral_manifold,
)


def _text(value: str) -> bytes:
    raw = value.encode("utf-8")
    return struct.pack("<I", len(raw)) + raw


def _pnf1(
    *,
    fragment: int,
    shape: int,
    sentence_id: int,
    local_ordinal: int,
    head_ordinal: int,
    orth: str,
    lemma: str,
    head_lemma: str,
) -> bytes:
    payload = bytearray(b"PNF1")
    payload.extend(bytes([fragment, shape, 1, 0]))
    payload.extend(struct.pack("<Q", sentence_id))
    payload.extend(struct.pack("<I", local_ordinal))
    payload.extend(struct.pack("<I", head_ordinal))
    payload.extend(struct.pack("<I", local_ordinal * 3))
    payload.extend(struct.pack("<I", local_ordinal * 3 + max(1, len(orth))))
    payload.extend(_text(orth))
    payload.extend(_text(lemma))
    payload.extend(_text(head_lemma))
    payload.extend(_text(head_lemma))
    return bytes(payload)


def _slrw_record(record_id: str, document_ref: str, payload: bytes, *, kind: int = 2) -> bytes:
    rec_id = record_id.encode("utf-8")
    aux = document_ref.encode("utf-8")
    header = bytearray(b"SLRW")
    header.extend(struct.pack("<H", 1))
    header.extend(bytes([kind, 0]))
    header.extend(struct.pack("<III", len(rec_id), len(aux), len(payload)))
    header.extend(struct.pack("<q", 1))
    header.extend(rec_id)
    header.extend(aux)
    header.extend(payload)
    return bytes(header)


def _write_fixture(path: Path) -> list[str]:
    conversations = [f"conversation-{index:02d}" for index in range(6)]
    group_a = [
        ("prove", "system", "consistency"),
        ("prove", "model", "invariant"),
        ("verify", "proof", "kernel"),
    ]
    group_b = [
        ("measure", "sensor", "metric"),
        ("estimate", "state", "fisher"),
        ("compare", "geometry", "curvature"),
    ]
    records = bytearray()
    candidate_index = 0
    for conversation_index, conversation_id in enumerate(conversations):
        motifs = group_a if conversation_index < 3 else group_b
        repetitions = 4 + (conversation_index % 3)
        for sentence_id in range(repetitions):
            predicate, actor, theme = motifs[sentence_id % len(motifs)]
            for local, (fragment, shape, orth, lemma) in enumerate(
                [
                    (1, 1, actor, actor),
                    (2, 2, theme, theme),
                    (3, 5, predicate, predicate),
                ]
            ):
                payload = _pnf1(
                    fragment=fragment,
                    shape=shape,
                    sentence_id=sentence_id,
                    local_ordinal=local,
                    head_ordinal=2,
                    orth=orth,
                    lemma=lemma,
                    head_lemma=predicate,
                )
                records.extend(
                    _slrw_record(
                        f"pnf-candidate:{candidate_index}",
                        f"chat:{conversation_id}",
                        payload,
                    )
                )
                candidate_index += 1
    path.write_bytes(records)
    return conversations


def _hierarchy(tmp_path: Path) -> dict:
    corpus_path = tmp_path / "fleet_top500_iter1.slrw"
    conversations = _write_fixture(corpus_path)
    corpus = load_slrw_conversation_factors(corpus_path)
    alpha_signals = {
        conversations[0]: {"theorem_density": 8.0, "formal_gap_reduction": 6.0},
        conversations[1]: {"theorem_density": 5.0, "formal_gap_reduction": 4.0},
        conversations[3]: {"theorem_density": 2.0, "formal_gap_reduction": 1.0},
    }
    ontology_edges = [
        {
            "conversation_ids": conversations[:3],
            "label": "formal proof geometry",
            "weight": 1.0,
        },
        {
            "conversation_ids": conversations[3:],
            "label": "information geometry",
            "weight": 1.0,
        },
    ]
    return build_hierarchical_pnf_topics(
        corpus,
        ontology_edges=ontology_edges,
        alpha_signals=alpha_signals,
        max_features=32,
        max_spectral_dimensions=8,
    )


def test_real_slrw_loader_and_dynamic_hierarchy(tmp_path: Path) -> None:
    corpus_path = tmp_path / "fleet_top500_iter1.slrw"
    conversations = _write_fixture(corpus_path)

    corpus = load_slrw_conversation_factors(corpus_path)
    assert corpus["conversation_count"] == 6
    assert corpus["pnf_candidate_count"] > 0
    assert set(corpus["conversations"]) == set(conversations)
    assert all(row["frame_counts"] for row in corpus["conversations"].values())

    hierarchy = build_hierarchical_pnf_topics(
        corpus,
        ontology_edges=[
            {"conversation_ids": conversations[:3], "label": "proof ontology"},
            {"conversation_ids": conversations[3:], "label": "measurement ontology"},
        ],
        max_features=32,
        max_spectral_dimensions=8,
    )

    assert hierarchy["feature_space"]["hardcoded_topic_count"] is False
    assert hierarchy["source"]["conversation_count"] == 6
    assert len(hierarchy["conversation_rows"]) == 6
    assert hierarchy["marchenko_pastur"]["lambda_plus"] > 0.0
    assert hierarchy["thresholds"]["fibre_tau"] <= hierarchy["thresholds"]["subtopic_tau"]
    assert hierarchy["thresholds"]["subtopic_tau"] <= hierarchy["thresholds"]["primary_tau"]

    primary_members = {
        topic["topic_id"]: set(topic["members"])
        for topic in hierarchy["primary_topics"]
    }
    sub_members = {
        topic["topic_id"]: set(topic["members"])
        for topic in hierarchy["subtopics"]
    }
    for topic in hierarchy["subtopics"]:
        assert set(topic["members"]) <= primary_members[topic["parent_id"]]
    for fibre in hierarchy["fibre_cliques"]:
        assert set(fibre["members"]) <= sub_members[fibre["parent_id"]]

    assert all(topic["name"] for topic in hierarchy["primary_topics"])
    # Topic heads may only use SensibLaw PROPN evidence or explicitly
    # supplied ontology incidence. The test fixture's verb-like PNF frames
    # must not be promoted merely because they are frequent.
    assert all(
        topic["name_source"] in {
            "sensiblaw_propn_relational_frames",
            "explicit_ontology_incidence",
            "opaque_topic_id",
        }
        for topic in hierarchy["primary_topics"]
    )
    assert all(
        frame.get("evidence") == "sensiblaw_propn"
        for topic in hierarchy["primary_topics"]
        for frame in topic["semantic_centroid"]["top_relational_frames"]
    )
    assert any(
        topic["semantic_centroid"]["top_ontology_incidence"]
        for topic in hierarchy["primary_topics"]
    )



def test_motif_pos_gate_abstains_without_sensiblaw(monkeypatch) -> None:
    import builtins
    from itir_mcp import pnf_spectral_packet as packet

    original_import = builtins.__import__

    def blocked_import(name, *args, **kwargs):
        if name == "sensiblaw.interfaces" or name.startswith("sensiblaw.interfaces."):
            raise ModuleNotFoundError(name)
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", blocked_import)
    assert packet._motif_has_propn_evidence("want(arg:change)") is False


def test_motif_pos_gate_requires_predicate_head_propn(monkeypatch) -> None:
    from itir_mcp import pnf_spectral_packet as packet

    import sys
    from types import ModuleType

    interface = ModuleType("sensiblaw.interfaces")
    interface.collect_canonical_relational_bundle = lambda _text: {"atoms": [
        {"text": "YangMillsMassGap", "lemma": "yangmillsmassgap", "pos": "PROPN"},
        {"text": "changes", "lemma": "change", "pos": "VERB"},
    ]}
    package = ModuleType("sensiblaw")
    package.interfaces = interface
    monkeypatch.setitem(sys.modules, "sensiblaw", package)
    monkeypatch.setitem(sys.modules, "sensiblaw.interfaces", interface)
    assert packet._motif_has_propn_evidence("YangMillsMassGap(arg:change)") is True
    assert packet._motif_has_propn_evidence("change(arg:day)") is False

def test_capacity_threshold_is_monotone_and_pareto_prioritizes_alpha(tmp_path: Path) -> None:
    hierarchy = _hierarchy(tmp_path)

    abundant = allocate_hierarchical_spectral_workers(hierarchy, 6)
    constrained = allocate_hierarchical_spectral_workers(hierarchy, 2)

    assert abundant["selected_tau"] <= constrained["selected_tau"]
    assert abundant["worker_slot_count"] >= constrained["worker_slot_count"]
    assert all(slot["requires_noTypedMeet_check"] for slot in constrained["worker_slots"])
    assert constrained["policy"]["alpha_is_priority_not_authority"] is True

    alpha_order = [slot["alpha"]["mean"] for slot in constrained["worker_slots"]]
    if len(alpha_order) > 1:
        assert alpha_order[0] >= min(alpha_order[1:])


def test_no_typed_meet_failure_rolls_component_into_internal_packet(tmp_path: Path) -> None:
    hierarchy = _hierarchy(tmp_path)
    preliminary = allocate_hierarchical_spectral_workers(hierarchy, 3)
    component_ids = [slot["component_id"] for slot in preliminary["worker_slots"]]
    if len(component_ids) < 2:
        return

    first, second = component_ids[:2]
    key = "|".join(sorted((first, second)))
    plan = allocate_hierarchical_spectral_workers(
        hierarchy,
        3,
        parallel_admissibility={key: False},
    )

    assert plan["rolled_components"]
    assert plan["rolled_components"][0]["reason"] == "noTypedMeet_not_admitted"
    assert plan["worker_slot_count"] < plan["component_count_before_noTypedMeet"]
    assert all(not slot["requires_noTypedMeet_check"] for slot in plan["worker_slots"])


def test_hierarchical_visualizations_emit_png_svg_heatmap_and_dendrogram(tmp_path: Path) -> None:
    hierarchy = _hierarchy(tmp_path)
    output_dir = tmp_path / "docs" / "fleet"

    receipt = generate_hierarchical_corpus_visualizations(hierarchy, output_dir)

    assert receipt["conversation_count"] == 6
    names = {Path(artifact["output_path"]).name for artifact in receipt["artifacts"]}
    assert names == {
        "fleet_manifold.png",
        "fleet_manifold.svg",
        "fleet_topic_heatmap.png",
        "fleet_topic_heatmap.svg",
        "fleet_topic_dendrogram.png",
        "fleet_topic_dendrogram.svg",
    }
    for artifact in receipt["artifacts"]:
        path = Path(artifact["output_path"])
        assert path.is_file()
        assert path.stat().st_size > 0


def test_manifold_renderer_accepts_full_500_conversation_surface(tmp_path: Path) -> None:
    rows = []
    for index in range(500):
        angle = (2.0 * math.pi * index) / 500.0
        rows.append(
            {
                "conversation_id": f"conversation-{index:03d}",
                "xy": [math.cos(angle), math.sin(angle)],
                "primary_id": f"primary-{index % 7:03d}",
                "subtopic_id": f"sub-{index % 21:03d}",
                "alpha": (index + 1) / 500.0,
            }
        )
    hierarchy = {
        "conversation_rows": rows,
        "marchenko_pastur": {
            "lambda_plus": 2.75,
            "macro_mode_count": 3,
        },
    }
    output = tmp_path / "docs" / "fleet" / "fleet_manifold_500.svg"

    receipt = render_hierarchical_spectral_manifold(hierarchy, output)

    assert receipt["conversation_count"] == 500
    assert receipt["primary_cluster_count"] == 7
    assert output.is_file()
    assert output.stat().st_size > 0


def test_end_to_end_slrw_to_docs_fleet_artifacts(tmp_path: Path) -> None:
    corpus_path = tmp_path / "fleet_top500_iter1.slrw"
    conversations = _write_fixture(corpus_path)
    output_dir = tmp_path / "docs" / "fleet"

    receipt = project_slrw_hierarchy_to_docs(
        corpus_path,
        output_dir,
        ontology_edges=[
            {"conversation_ids": conversations[:3], "label": "proof ontology"},
            {"conversation_ids": conversations[3:], "label": "measurement ontology"},
        ],
        max_features=32,
        max_spectral_dimensions=8,
    )

    assert receipt["conversation_count"] == 6
    hierarchy_path = Path(receipt["hierarchy_path"])
    assert hierarchy_path.is_file()
    assert hierarchy_path.stat().st_size > 0
    artifact_names = {
        Path(item["output_path"]).name
        for item in receipt["visualization"]["artifacts"]
    }
    assert artifact_names == {
        "fleet_manifold.png",
        "fleet_manifold.svg",
        "fleet_topic_heatmap.png",
        "fleet_topic_heatmap.svg",
        "fleet_topic_dendrogram.png",
        "fleet_topic_dendrogram.svg",
    }
