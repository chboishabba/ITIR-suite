from __future__ import annotations

from pathlib import Path

from itir_mcp.pnf_spectral_packet import (
    add_discrete_waves,
    apply_stalk_restriction,
    build_typed_hyperfabric_operator,
)
from itir_mcp.registry import build_default_registry
from itir_mcp.spectral_plot_tools import (
    generate_corpus_spectral_visualizations,
    render_spectral_heatmap,
    render_spectral_scatter,
)


def test_sheaf_stalk_restriction_and_block_coboundary() -> None:
    graph = {
        "projection_ref": "pnf-follow:test:typed-fibre:revision-1",
        "nodes": [
            {
                "id": "node:a",
                "kind": "pnf_factor",
                "stalk": {
                    "dimension": 2,
                    "type_ref": "stalk:actor-state",
                    "discrete_wave": {"re": [1, 2], "im": [0, 1]},
                },
            },
            {
                "id": "node:b",
                "kind": "pnf_factor",
                "stalk": {
                    "dimension": 2,
                    "type_ref": "stalk:theme-state",
                    "discrete_wave": {"re": [3, 4], "im": [1, 0]},
                },
            },
        ],
        "hyperedges": [
            {
                "id": "edge:predicate",
                "kind": "predicate_frame",
                "members": ["node:a", "node:b"],
                "edge_stalk": {"dimension": 2, "type_ref": "stalk:predicate"},
                "restrictions": {
                    "node:a": [[1, 0], [0, 1]],
                    "node:b": [[1, 1], [0, 1]],
                },
                "provenance_ref": "pnf-frame:test",
            }
        ],
    }

    assert apply_stalk_restriction([[1, 1], [1, -1]], [2, 3]) == [5.0, -1.0]

    operator = build_typed_hyperfabric_operator(graph)

    assert operator["stalk_coordinate_count"] == 4
    assert operator["restriction_row_count"] == 2
    assert operator["restriction_maps_explicit"] == 2
    assert operator["scalar_identity_lifts"] == 0
    assert len(operator["coboundary"]) == 2
    assert all(len(row) == 4 for row in operator["coboundary"])

    wave = operator["wave_synthesis"]
    assert wave["edge_count"] == 1
    assert wave["additive_superposition"] is True
    assert wave["every_pnf_synthesis_rule_identified_with_wave_addition"] is False
    edge = wave["edges"][0]
    assert edge["formal_discrete_wave_commutator_applicable"] is True
    assert edge["superposition"] == {"re": [8, 6], "im": [1, 1]}
    assert edge["synthesis_defect"] == {"re": 0, "im": 0}


def test_additive_discrete_wave_superposition() -> None:
    result = add_discrete_waves(
        [
            {"re": 2, "im": -1},
            {"re": 5, "im": 3},
            {"re": -4, "im": 2},
        ]
    )

    assert result == {"re": 3, "im": 4}


def _coordinates_payload() -> dict:
    return {
        "mp_threshold": 2.75,
        "eigenvalues": [74.5526, 18.8350, 5.5865, 1.2],
        "points": [
            {"entity_ref": "fibre:a", "coordinates": [0.72, 0.18, 0.11], "cluster": "macro-0"},
            {"entity_ref": "fibre:b", "coordinates": [0.68, 0.25, 0.08], "cluster": "macro-0"},
            {"entity_ref": "fibre:c", "coordinates": [-0.14, 0.81, 0.24], "cluster": "macro-1"},
            {"entity_ref": "fibre:d", "coordinates": [-0.21, 0.77, 0.31], "cluster": "macro-1"},
        ],
    }


def test_scatter_and_heatmap_generation(tmp_path: Path) -> None:
    payload = _coordinates_payload()

    scatter_png = tmp_path / "scatter.png"
    scatter_svg = tmp_path / "scatter.svg"
    heatmap_png = tmp_path / "heatmap.png"
    matrix = [
        [1.0, 0.95, 0.10, 0.02],
        [0.95, 1.0, 0.16, 0.08],
        [0.10, 0.16, 1.0, 0.96],
        [0.02, 0.08, 0.96, 1.0],
    ]
    labels = ["fibre:a", "fibre:b", "fibre:c", "fibre:d"]

    scatter_receipt = render_spectral_scatter(payload, scatter_png)
    render_spectral_scatter(payload, scatter_svg)
    heatmap_receipt = render_spectral_heatmap(matrix, labels, heatmap_png)

    assert scatter_receipt["point_count"] == 4
    assert scatter_receipt["cluster_count"] == 2
    assert heatmap_receipt["matrix_size"] == 4
    assert scatter_png.is_file() and scatter_png.stat().st_size > 0
    assert scatter_svg.is_file() and scatter_svg.stat().st_size > 0
    assert heatmap_png.is_file() and heatmap_png.stat().st_size > 0


def test_generate_corpus_visualizations_emits_png_and_svg_pairs(tmp_path: Path) -> None:
    result = generate_corpus_spectral_visualizations(_coordinates_payload(), tmp_path)

    assert result["point_count"] == 4
    assert result["matrix_size"] == 4
    assert result["candidate_only"] is True
    assert result["canonical_truth_mutated"] is False
    paths = {Path(item["output_path"]).name for item in result["artifacts"]}
    assert paths == {
        "spectral_scatter.png",
        "spectral_scatter.svg",
        "spectral_heatmap.png",
        "spectral_heatmap.svg",
    }
    for item in result["artifacts"]:
        path = Path(item["output_path"])
        assert path.is_file()
        assert path.stat().st_size > 0


def test_spectral_plot_tools_are_registered_with_receipt_authority() -> None:
    registry = build_default_registry()

    for name in (
        "itir.spectral.render_scatter",
        "itir.spectral.render_heatmap",
        "itir.spectral.visualize_corpus",
    ):
        spec = registry.get_tool_spec(name)
        profile = registry.get_tool_authority_profile(name)
        assert spec is not None
        assert profile is not None
        assert profile["max_authority"] == "receipt"
        assert profile["mutates"] is True
        assert profile["authority_notes"]["non_authoritative"] is True
