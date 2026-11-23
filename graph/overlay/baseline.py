from __future__ import annotations

import json
from hashlib import sha256
from typing import Any

_CONTRACT_VERSION = "graph.overlay.baseline.v1"
_REPLAY_ALGORITHM = "graph.overlay.baseline.v1"


def _canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _sha256_hex(value: Any) -> str:
    return sha256(_canonical_json_bytes(value)).hexdigest()


def _source_snapshot(runtime_object: dict[str, Any]) -> dict[str, Any]:
    obj = runtime_object.get("object")
    if not isinstance(obj, dict):
        raise ValueError("runtime object payload is missing object")

    object_id = obj.get("object_id")
    provenance = obj.get("provenance")
    if not isinstance(object_id, str) or not object_id:
        raise ValueError("runtime object is missing object_id")
    if not isinstance(provenance, dict):
        raise ValueError("runtime object is missing provenance")

    content_sha256 = provenance.get("body_text_sha256")
    if not isinstance(content_sha256, str) or len(content_sha256) != 64:
        raise ValueError("runtime object provenance is missing body_text_sha256")

    return {
        "object_id": object_id,
        "content_sha256": content_sha256,
        "source": provenance.get("source"),
        "source_url": provenance.get("source_url"),
    }


def _graph_snapshot(runtime_graph: dict[str, Any]) -> dict[str, Any]:
    source_object_id = runtime_graph.get("source_object_id")
    graph_id = runtime_graph.get("graph_id")
    nodes = runtime_graph.get("nodes")
    edges = runtime_graph.get("edges")

    if not isinstance(source_object_id, str) or not source_object_id:
        raise ValueError("runtime graph is missing source_object_id")
    if not isinstance(graph_id, str) or not graph_id:
        raise ValueError("runtime graph is missing graph_id")
    if not isinstance(nodes, list) or not all(isinstance(node, dict) for node in nodes):
        raise ValueError("runtime graph nodes must be a list of objects")
    if not isinstance(edges, list) or not all(isinstance(edge, dict) for edge in edges):
        raise ValueError("runtime graph edges must be a list of objects")

    node_ids = [node.get("node_id") for node in nodes]
    edge_ids = [edge.get("edge_id") for edge in edges]
    if not all(isinstance(node_id, str) and node_id for node_id in node_ids):
        raise ValueError("runtime graph node is missing node_id")
    if not all(isinstance(edge_id, str) and edge_id for edge_id in edge_ids):
        raise ValueError("runtime graph edge is missing edge_id")
    if len(set(node_ids)) != len(node_ids):
        raise ValueError("runtime graph contains duplicate node_id")
    if len(set(edge_ids)) != len(edge_ids):
        raise ValueError("runtime graph contains duplicate edge_id")

    return {
        "contract_version": runtime_graph.get("contract_version"),
        "graph_id": graph_id,
        "source_object_id": source_object_id,
        "nodes": sorted((dict(node) for node in nodes), key=lambda node: node["node_id"]),
        "edges": sorted((dict(edge) for edge in edges), key=lambda edge: edge["edge_id"]),
    }


def _node_source_refs(node: dict[str, Any], source_object_id: str) -> list[str]:
    refs = {source_object_id}
    ref = node.get("ref")
    if isinstance(ref, str) and ref:
        refs.add(ref)
    return sorted(refs)


def _edge_source_refs(
    edge: dict[str, Any],
    *,
    source_object_id: str,
    refs_by_node_id: dict[str, list[str]],
) -> list[str]:
    refs = {source_object_id}
    for endpoint in ("from_node_id", "to_node_id"):
        node_id = edge.get(endpoint)
        if isinstance(node_id, str):
            refs.update(refs_by_node_id.get(node_id, []))
    return sorted(refs)


def _emit_from_snapshots(
    source_snapshot: dict[str, Any],
    graph_snapshot: dict[str, Any],
    *,
    expected_input_sha256: str | None = None,
) -> dict[str, Any]:
    inputs = {
        "source_snapshot": source_snapshot,
        "graph_snapshot": graph_snapshot,
    }
    input_sha256 = _sha256_hex(inputs)
    if expected_input_sha256 is not None and input_sha256 != expected_input_sha256:
        raise ValueError("replay input digest mismatch")

    source_object_id = source_snapshot["object_id"]
    if graph_snapshot["source_object_id"] != source_object_id:
        raise ValueError("runtime object and graph source_object_id differ")

    nodes: list[dict[str, Any]] = []
    refs_by_node_id: dict[str, list[str]] = {}
    for graph_node in graph_snapshot["nodes"]:
        source_refs = _node_source_refs(graph_node, source_object_id)
        refs_by_node_id[graph_node["node_id"]] = source_refs
        nodes.append(
            {
                "node_id": graph_node["node_id"],
                "kind": graph_node.get("kind"),
                "label": graph_node.get("label"),
                "source_refs": source_refs,
            }
        )

    edges: list[dict[str, Any]] = []
    for graph_edge in graph_snapshot["edges"]:
        edges.append(
            {
                "edge_id": graph_edge["edge_id"],
                "from_node_id": graph_edge.get("from_node_id"),
                "to_node_id": graph_edge.get("to_node_id"),
                "kind": graph_edge.get("kind"),
                "source_refs": _edge_source_refs(
                    graph_edge,
                    source_object_id=source_object_id,
                    refs_by_node_id=refs_by_node_id,
                ),
            }
        )

    graph_sha256 = _sha256_hex(graph_snapshot)
    return {
        "contract_version": _CONTRACT_VERSION,
        "overlay_id": f"graph-overlay:{input_sha256[:16]}",
        "source_object_id": source_object_id,
        "nodes": nodes,
        "edges": edges,
        "provenance": {
            "source_object_id": source_object_id,
            "source_content_sha256": source_snapshot["content_sha256"],
            "source": source_snapshot.get("source"),
            "source_url": source_snapshot.get("source_url"),
            "runtime_graph_id": graph_snapshot["graph_id"],
            "runtime_graph_sha256": graph_sha256,
        },
        "replay": {
            "algorithm": _REPLAY_ALGORITHM,
            "input_sha256": input_sha256,
            "source_snapshot": source_snapshot,
            "graph_snapshot": graph_snapshot,
        },
    }


def emit_baseline_overlay(
    runtime_object: dict[str, Any],
    runtime_graph: dict[str, Any],
) -> dict[str, Any]:
    """Emit the conservative provenance-labelled baseline graph overlay."""

    return _emit_from_snapshots(
        _source_snapshot(runtime_object),
        _graph_snapshot(runtime_graph),
    )


def replay_baseline_overlay(replay_manifest: dict[str, Any]) -> dict[str, Any]:
    """Replay one baseline overlay from its embedded canonical input snapshots."""

    if replay_manifest.get("algorithm") != _REPLAY_ALGORITHM:
        raise ValueError("unsupported replay algorithm")

    source_snapshot = replay_manifest.get("source_snapshot")
    graph_snapshot = replay_manifest.get("graph_snapshot")
    input_sha256 = replay_manifest.get("input_sha256")
    if not isinstance(source_snapshot, dict) or not isinstance(graph_snapshot, dict):
        raise ValueError("replay manifest is missing canonical input snapshots")
    if not isinstance(input_sha256, str) or len(input_sha256) != 64:
        raise ValueError("replay manifest is missing input_sha256")

    return _emit_from_snapshots(
        source_snapshot,
        graph_snapshot,
        expected_input_sha256=input_sha256,
    )


def canonical_overlay_bytes(overlay: dict[str, Any]) -> bytes:
    """Return the deterministic byte representation used for replay checks."""

    return _canonical_json_bytes(overlay)
