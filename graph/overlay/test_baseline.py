from __future__ import annotations

import copy

import pytest

from graph.overlay.baseline import (
    canonical_overlay_bytes,
    emit_baseline_overlay,
    replay_baseline_overlay,
)


def _runtime_object() -> dict:
    return {
        "contract_version": "jmd.runtime.object.v1",
        "resolved_at": "2026-10-28T00:00:00Z",
        "object": {
            "object_id": "jmd:erdfa:shard:note-0001",
            "provenance": {
                "body_text_sha256": "a" * 64,
                "source": "pastebin",
                "source_url": "https://example.invalid/paste/note-0001",
            },
        },
    }


def _runtime_graph() -> dict:
    return {
        "contract_version": "jmd.runtime.graph.v1",
        "generated_at": "2026-10-28T00:00:00Z",
        "graph_id": "jmd-graph:fixture",
        "source_object_id": "jmd:erdfa:shard:note-0001",
        "nodes": [
            {
                "node_id": "node:b",
                "kind": "linked",
                "label": "B",
                "ref": "jmd:erdfa:shard:other",
                "cid": None,
            },
            {
                "node_id": "node:a",
                "kind": "shard",
                "label": "A",
                "ref": "jmd:erdfa:shard:note-0001",
                "cid": "bafkfixture",
            },
        ],
        "edges": [
            {
                "edge_id": "edge:b",
                "from_node_id": "node:b",
                "to_node_id": "node:a",
                "kind": "parent",
            },
            {
                "edge_id": "edge:a",
                "from_node_id": "node:a",
                "to_node_id": "node:b",
                "kind": "link",
            },
        ],
    }


def test_baseline_overlay_emits_provenance_and_replays_byte_identically() -> None:
    runtime_object = _runtime_object()
    runtime_graph = _runtime_graph()

    overlay = emit_baseline_overlay(runtime_object, runtime_graph)

    assert overlay["contract_version"] == "graph.overlay.baseline.v1"
    assert overlay["source_object_id"] == "jmd:erdfa:shard:note-0001"
    assert overlay["provenance"]["source_content_sha256"] == "a" * 64
    assert overlay["provenance"]["runtime_graph_id"] == "jmd-graph:fixture"
    assert len(overlay["provenance"]["runtime_graph_sha256"]) == 64
    assert [node["node_id"] for node in overlay["nodes"]] == ["node:a", "node:b"]
    assert [edge["edge_id"] for edge in overlay["edges"]] == ["edge:a", "edge:b"]
    assert all(node["source_refs"] for node in overlay["nodes"])
    assert all(edge["source_refs"] for edge in overlay["edges"])

    replayed = replay_baseline_overlay(overlay["replay"])
    assert canonical_overlay_bytes(replayed) == canonical_overlay_bytes(overlay)


def test_baseline_overlay_ignores_wall_clock_and_input_order() -> None:
    runtime_object = _runtime_object()
    first_graph = _runtime_graph()
    second_graph = copy.deepcopy(first_graph)
    second_graph["generated_at"] = "2099-12-31T23:59:59Z"
    second_graph["nodes"].reverse()
    second_graph["edges"].reverse()

    first = emit_baseline_overlay(runtime_object, first_graph)
    second = emit_baseline_overlay(runtime_object, second_graph)

    assert canonical_overlay_bytes(first) == canonical_overlay_bytes(second)
    assert first["overlay_id"] == second["overlay_id"]


def test_replay_rejects_tampered_manifest() -> None:
    overlay = emit_baseline_overlay(_runtime_object(), _runtime_graph())
    manifest = copy.deepcopy(overlay["replay"])
    manifest["graph_snapshot"]["nodes"][0]["label"] = "tampered"

    with pytest.raises(ValueError, match="replay input digest mismatch"):
        replay_baseline_overlay(manifest)
