from __future__ import annotations

import hashlib
import json
from collections import Counter
from dataclasses import asdict, dataclass
from typing import Any


def stable_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def fake_cid(obj: Any) -> str:
    digest = hashlib.sha256(stable_json(obj).encode("utf-8")).hexdigest()
    return f"cid:{digest}"


@dataclass
class Node:
    id: str
    type: str
    text: str = ""
    tags: list[str] | None = None


@dataclass
class Edge:
    id: str
    source: str
    target: str
    morphism: str


@dataclass
class Graph:
    doc_id: str
    nodes: list[Node]
    edges: list[Edge]


@dataclass
class CandidateTransform:
    kind: str
    pattern: tuple[str, ...]
    reuse_count: int
    dict_cost: int
    savings: int
    net_gain: int


@dataclass
class MDLProof:
    type: str
    version: str
    input_cid: str
    input_graph_cid: str
    normalized_graph_cid: str
    dictionary_cid: str
    transform_plan_cid: str
    base_cost: int
    normalized_cost: int
    net_gain: int
    reconstructible: bool
    type_preserved: bool
    canonical_export_preserved: bool
    search_family: str
    interpreter_version: str
    proof_mode: str
    proof_payload_cid: str


def ingest_graph(raw: dict[str, Any]) -> Graph:
    nodes = [Node(**item) for item in raw["nodes"]]
    edges = [Edge(**item) for item in raw.get("edges", [])]
    return Graph(doc_id=raw["doc_id"], nodes=nodes, edges=edges)


def _append_unique(parts: list[str], value: str | None) -> None:
    candidate = (value or "").strip()
    if candidate and candidate not in parts:
        parts.append(candidate)


def _runtime_object_context_lines(runtime_object: dict[str, Any]) -> list[str]:
    erdfa = runtime_object.get("erdfa") or {}
    archive = erdfa.get("archive") or {}
    archive_manifest = archive.get("manifest") or {}
    dasl = erdfa.get("dasl") or {}

    parts: list[str] = []
    _append_unique(parts, runtime_object.get("title"))
    _append_unique(parts, runtime_object.get("content_type"))

    component_kind = erdfa.get("component_kind")
    component_type = erdfa.get("component_type")
    if component_kind or component_type:
        _append_unique(parts, "component " + " ".join(str(item) for item in (component_kind, component_type) if item))

    tags = [str(tag).strip() for tag in erdfa.get("tags") or [] if str(tag).strip()]
    if tags:
        _append_unique(parts, "tags " + " ".join(tags))

    if erdfa.get("reply_to"):
        _append_unique(parts, f"reply_to {erdfa['reply_to']}")
    if dasl.get("type_code") is not None:
        _append_unique(parts, f"dasl_type {dasl['type_code']}")
    if erdfa.get("local_cid"):
        _append_unique(parts, f"local_cid {erdfa['local_cid']}")
    if erdfa.get("cid"):
        _append_unique(parts, f"cid {erdfa['cid']}")
    if archive_manifest.get("name"):
        _append_unique(parts, f"archive_manifest {archive_manifest['name']}")
    elif archive.get("primary_shard_id"):
        _append_unique(parts, f"archive_primary {archive['primary_shard_id']}")

    provenance = runtime_object.get("provenance") or {}
    if provenance.get("source_url"):
        _append_unique(parts, f"source_url {provenance['source_url']}")
    return parts


def _graph_edge_context(runtime_graph: dict[str, Any]) -> dict[str, list[str]]:
    context: dict[str, list[str]] = {}

    def remember(node_id: str, text: str) -> None:
        bucket = context.setdefault(node_id, [])
        if text not in bucket:
            bucket.append(text)

    for edge in runtime_graph.get("edges", []):
        from_node_id = edge["from_node_id"]
        to_node_id = edge["to_node_id"]
        kind = edge["kind"]
        remember(from_node_id, f"outgoing {kind} {to_node_id}")
        remember(to_node_id, f"incoming {kind} {from_node_id}")
    return context


def project_runtime_bundle_to_graph_input(bundle: dict[str, Any]) -> dict[str, Any]:
    runtime_object = bundle["runtime_object"]["object"]
    runtime_graph = bundle["runtime_graph"]
    source_object_id = runtime_graph["source_object_id"]
    source_text = (runtime_object.get("text") or "").strip()
    source_context = _runtime_object_context_lines(runtime_object)
    edge_context = _graph_edge_context(runtime_graph)

    nodes: list[dict[str, Any]] = []
    for node in runtime_graph["nodes"]:
        node_id = node["node_id"]
        label = (node.get("label") or "").strip()
        kind = (node.get("kind") or "").strip()
        ref = (node.get("ref") or "").strip()
        cid = (node.get("cid") or "").strip()

        text_parts: list[str] = []
        if node_id == source_object_id and source_text:
            text_parts.append(source_text)
        if node_id == source_object_id:
            for item in source_context:
                _append_unique(text_parts, item)
        if label and label not in {node_id, source_text}:
            _append_unique(text_parts, label)
        if kind:
            _append_unique(text_parts, kind)
        if ref and ref not in {node_id, label}:
            _append_unique(text_parts, ref)
        if cid:
            _append_unique(text_parts, cid)
        for item in edge_context.get(node_id, []):
            _append_unique(text_parts, item)

        node_text = " ".join(part for part in text_parts if part).strip() or node_id
        nodes.append(
            {
                "id": node_id,
                "type": kind or "RuntimeNode",
                "text": node_text,
                "tags": [kind] if kind else [],
            }
        )

    edges = [
        {
            "id": edge["edge_id"],
            "source": edge["from_node_id"],
            "target": edge["to_node_id"],
            "morphism": edge["kind"],
        }
        for edge in runtime_graph.get("edges", [])
    ]

    return {
        "doc_id": runtime_graph["graph_id"],
        "nodes": nodes,
        "edges": edges,
    }


def graph_tokens(graph: Graph) -> list[str]:
    tokens: list[str] = []
    for node in graph.nodes:
        tokens.extend(node.text.split())
    return tokens


def graph_cost(graph: Graph) -> int:
    token_cost = sum(len(token) for token in graph_tokens(graph))
    structure_cost = 8 * len(graph.nodes) + 4 * len(graph.edges)
    return token_cost + structure_cost


def discover_motifs(graph: Graph, min_len: int = 2, max_len: int = 4) -> list[CandidateTransform]:
    counts: Counter[tuple[str, ...]] = Counter()
    for node in graph.nodes:
        tokens = node.text.split()
        for ngram_len in range(min_len, min(max_len, len(tokens)) + 1):
            for start in range(len(tokens) - ngram_len + 1):
                counts[tuple(tokens[start : start + ngram_len])] += 1

    candidates: list[CandidateTransform] = []
    for pattern, reuse_count in counts.items():
        if reuse_count < 2:
            continue
        dict_cost = sum(len(part) for part in pattern) + 4
        raw_mass = reuse_count * sum(len(part) for part in pattern)
        savings = raw_mass - reuse_count
        net_gain = savings - dict_cost
        if net_gain > 0:
            candidates.append(
                CandidateTransform(
                    kind="macro_subgraph",
                    pattern=pattern,
                    reuse_count=reuse_count,
                    dict_cost=dict_cost,
                    savings=savings,
                    net_gain=net_gain,
                )
            )
    # Prefer motifs with better gain, then higher reuse, then shorter patterns to
    # bias toward reusable local macros rather than brittle long matches.
    candidates.sort(key=lambda item: (item.net_gain, item.reuse_count, -len(item.pattern)), reverse=True)
    return candidates


def apply_best_plan(graph: Graph, candidates: list[CandidateTransform]) -> tuple[Graph, dict[str, str], list[dict[str, Any]]]:
    if not candidates:
        return graph, {}, []

    best = candidates[0]
    macro_id = "M0"
    needle = " ".join(best.pattern)
    dictionary = {macro_id: needle}
    plan = [
        {
            "kind": best.kind,
            "macro_id": macro_id,
            "pattern": list(best.pattern),
            "reuse_count": best.reuse_count,
            "net_gain": best.net_gain,
        }
    ]

    new_nodes: list[Node] = []
    for node in graph.nodes:
        new_nodes.append(
            Node(
                id=node.id,
                type=node.type,
                text=node.text.replace(needle, macro_id),
                tags=list(node.tags or []),
            )
        )
    return Graph(doc_id=graph.doc_id, nodes=new_nodes, edges=graph.edges), dictionary, plan


def dictionary_cost(dictionary: dict[str, str]) -> int:
    return sum(len(key) + len(value) for key, value in dictionary.items())


def total_normalized_cost(graph: Graph, dictionary: dict[str, str]) -> int:
    return graph_cost(graph) + dictionary_cost(dictionary)


def build_mdl_proof(
    input_graph: Graph,
    normalized_graph: Graph,
    dictionary: dict[str, str],
    plan: list[dict[str, Any]],
) -> MDLProof:
    input_graph_obj = {
        "doc_id": input_graph.doc_id,
        "nodes": [asdict(node) for node in input_graph.nodes],
        "edges": [asdict(edge) for edge in input_graph.edges],
    }
    normalized_graph_obj = {
        "doc_id": normalized_graph.doc_id,
        "nodes": [asdict(node) for node in normalized_graph.nodes],
        "edges": [asdict(edge) for edge in normalized_graph.edges],
    }
    base_cost = graph_cost(input_graph)
    normalized_cost = total_normalized_cost(normalized_graph, dictionary)
    proof_payload = {
        "base_cost": base_cost,
        "normalized_cost": normalized_cost,
        "dictionary": dictionary,
        "plan": plan,
    }
    return MDLProof(
        type="sl::MDLProof",
        version="sl-mdl-proof@0.1.0",
        input_cid=fake_cid({"doc_id": input_graph.doc_id}),
        input_graph_cid=fake_cid(input_graph_obj),
        normalized_graph_cid=fake_cid(normalized_graph_obj),
        dictionary_cid=fake_cid({"dictionary": dictionary}),
        transform_plan_cid=fake_cid({"plan": plan}),
        base_cost=base_cost,
        normalized_cost=normalized_cost,
        net_gain=base_cost - normalized_cost,
        reconstructible=True,
        type_preserved=True,
        canonical_export_preserved=True,
        search_family="macro_subgraph_v1",
        interpreter_version="casey-mdl@0.1.0",
        proof_mode="hash-stub",
        proof_payload_cid=fake_cid(proof_payload),
    )


def run_pipeline(raw: dict[str, Any]) -> dict[str, Any]:
    input_graph = ingest_graph(raw)
    candidates = discover_motifs(input_graph)
    normalized_graph, dictionary, plan = apply_best_plan(input_graph, candidates)
    proof = build_mdl_proof(input_graph, normalized_graph, dictionary, plan)
    return {
        "input_graph": {
            "doc_id": input_graph.doc_id,
            "nodes": [asdict(node) for node in input_graph.nodes],
            "edges": [asdict(edge) for edge in input_graph.edges],
        },
        "candidate_transforms": [asdict(item) for item in candidates],
        "normalized_graph": {
            "doc_id": normalized_graph.doc_id,
            "nodes": [asdict(node) for node in normalized_graph.nodes],
            "edges": [asdict(edge) for edge in normalized_graph.edges],
        },
        "dictionary": dictionary,
        "transform_plan": plan,
        "proof": asdict(proof),
    }


def run_runtime_bundle_pipeline(bundle: dict[str, Any]) -> dict[str, Any]:
    return run_pipeline(project_runtime_bundle_to_graph_input(bundle))
