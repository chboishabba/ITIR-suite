"""Byte-audited, query-scoped Zelph name-shard index.

Distinct from the existing metadata-only exact_wikidata_name_route tool.
This consumes actual object bytes, verifies a declared content digest and
decodes each supplied chunk exactly once. The decoder is an explicit trusted
boundary: this module does NOT prove a Cap'n Proto implementation correct.
Coverage is of the caller-declared object set, not all of Wikidata.
"""
from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass
from hashlib import sha256
import re
from typing import Any

_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_QID = re.compile(r"^Q[1-9][0-9]*$")


@dataclass(frozen=True)
class DeclaredNameObject:
    shard_id: str
    chunk_index: int
    language: str
    size_bytes: int
    sha256_hex: str
    object_uri: str = ""  # optional on legacy callers; required for manifest bridge


def audit_declared_name_partition(
    *,
    artifact_id: str,
    graph_revision: str,
    declared: Sequence[DeclaredNameObject],
    raw_objects: Mapping[str, bytes],
    decode: Callable[[bytes], Iterable[tuple[str, str, int]]],
) -> dict[str, Any]:
    """Check exact byte->decoded-name membership over one *declared* cover.

    Decoder triples are (language, name, nodeId). Repeated names are retained
    as collision fibres, not discarded or arbitrarily made unique.
    The manifest's coverage of the source graph is a separate A1 premise.
    """
    if not artifact_id or not graph_revision:
        raise ValueError("artifact and immutable graph revision are required")
    if not declared:
        raise ValueError("empty manifest object cover cannot certify a partition")
    by_id: dict[str, DeclaredNameObject] = {}
    physical_keys: set[tuple[int, str]] = set()
    for entry in declared:
        if not entry.shard_id or entry.shard_id in by_id:
            raise ValueError("empty or duplicate physical shard id")
        if entry.chunk_index < 0 or not entry.language:
            raise ValueError("invalid physical section/global chunk key")
        if entry.size_bytes < 0 or not _SHA256.fullmatch(entry.sha256_hex):
            raise ValueError("physical object requires exact size and SHA256")
        physical_key = (entry.chunk_index, entry.language)
        if physical_key in physical_keys:
            raise ValueError("duplicate section/global chunk/language")
        physical_keys.add(physical_key)
        by_id[entry.shard_id] = entry

    expected = set(by_id)
    found = set(raw_objects)
    if found != expected:
        raise ValueError(
            f"declared name object coverage mismatch: missing={sorted(expected - found)}, "
            f"undeclared={sorted(found - expected)}"
        )

    hits: dict[tuple[str, str], set[tuple[str, int]]] = defaultdict(set)
    byte_count = 0
    decoded_count = 0
    receipts = []
    for shard_id in sorted(by_id):
        entry = by_id[shard_id]
        raw = raw_objects[shard_id]
        if not isinstance(raw, bytes):
            raise ValueError("raw object bytes required; no sidecar-only proof")
        if len(raw) != entry.size_bytes or sha256(raw).hexdigest() != entry.sha256_hex:
            raise ValueError(f"physical byte length/digest mismatch: {shard_id}")
        byte_count += len(raw)
        seen_pairs: set[tuple[str, int]] = set()
        for triple in decode(raw):
            if not isinstance(triple, tuple) or len(triple) != 3:
                raise ValueError("decoder must yield (language,name,nodeId)")
            lang, name, node_id = triple
            if (
                lang != entry.language
                or not isinstance(name, str)
                or not name
                or isinstance(node_id, bool)
                or not isinstance(node_id, int)
                or node_id < 0
            ):
                raise ValueError("decoder entry outside declared language/identifier domain")
            if (name, node_id) in seen_pairs:
                raise ValueError("duplicate decoded name/node pair in one object")
            seen_pairs.add((name, node_id))
            hits[(lang, name)].add((shard_id, node_id))
            decoded_count += 1
        receipts.append({
            "shard_id": shard_id,
            "chunk_index": entry.chunk_index,
            "language": entry.language,
            "object_uri": entry.object_uri,
            "sha256": entry.sha256_hex,
            "byte_count": len(raw),
            "decoded_pair_count": len(seen_pairs),
        })

    return {
        "version": "itir.zelph.byte_audited_name_partition.v1",
        "artifact_id": artifact_id,
        "graph_revision": graph_revision,
        "scope": "exactly-the-declared-nameOfNode-objects",
        "declared_object_set_exhausted": True,
        "source_graph_name_domain_exhausted": False,
        "query_family": ["nameOfNode"],
        "bytes_checked": byte_count,
        "decoded_pair_count": decoded_count,
        "physical_objects_checked": len(receipts),
        "physical_receipts": receipts,
        "collision_fibres": [
            {
                "language": lang,
                "name": name,
                "matches": [{"shard_id": sid, "node_id": node} for sid, node in sorted(matches)],
            }
            for (lang, name), matches in sorted(hits.items())
        ],
        "decoder_trust_boundary": "caller-supplied-decoder-not-formally-refined",
        "native_statement_coverage": False,
        "whole_graph_coverage": False,
        "source_support_paid": False,
        "candidate_only": True,
        "truth_authority": False,
        "promotion_authority": False,
    }


def lookup_audited_name(audit: Mapping[str, Any], qid: str) -> dict[str, Any]:
    """Lookup among checked objects, preserving ambiguous/collision results."""
    if not _QID.fullmatch(qid):
        raise ValueError("canonical Wikidata QID required")
    if audit.get("version") != "itir.zelph.byte_audited_name_partition.v1":
        raise ValueError("wrong name-partition audit contract")
    matches = [
        item["matches"]
        for item in audit["collision_fibres"]
        if item["language"] == "wikidata" and item["name"] == qid
    ]
    if len(matches) > 1:
        raise ValueError("non-canonical audit: multiple QID fibres")
    candidates = matches[0] if matches else []
    return {
        "version": "itir.zelph.audited_name_lookup.v1",
        "qid": qid,
        "graph_revision": audit["graph_revision"],
        "status": "found-in-inspected-objects" if candidates else "unresolved-in-original-graph",
        "candidate_nodes": candidates,
        "collision": len(candidates) > 1,
        "complete_for_declared_objects": audit["declared_object_set_exhausted"],
        "complete_for_source_graph": False,
        "negative_query_authority": False,
        "native_statement_coverage": False,
        "candidate_only": True,
    }


def evaluate_query_closure(
    *,
    name_audit: Mapping[str, Any],
    required: Mapping[str, Sequence[str]],
    inspected: Mapping[str, Sequence[str]],
    observation_revision: str,
) -> dict[str, Any]:
    """Conservative A2/A6 closure check; never substitutes for source attestation.

    Edges/relations must be accounted for by a caller-provided dependency map.
    All recorded observations must refer to the same immutable revision.
    Even if the dependency map is covered, source graph completeness remains
    unproved until an independent source-specific closure witness exists.
    """
    if observation_revision != name_audit.get("graph_revision"):
        raise ValueError("mixed physical graph revisions")
    missing = {
        query: sorted(set(predicates) - set(inspected.get(query, ())))
        for query, predicates in required.items()
    }
    missing = {query: predicates for query, predicates in missing.items() if predicates}
    return {
        "version": "itir.zelph.query_family_closure_audit.v1",
        "graph_revision": observation_revision,
        "family_dependencies_inspected": not missing,
        "missing_dependencies": missing,
        "original_graph_edge_closure_proved": False,
        "scoped_negative_answer_permitted": False,
        "coverage_status": "incomplete" if missing else "unverified-source-closure",
        "candidate_only": True,
    }


def verify_manifest_name_cover(
    *, manifest: Mapping[str, Any], audit: Mapping[str, Any]
) -> dict[str, Any]:
    """Compare **every** name object in the published manifest to byte-audited receipts.

    This is a structural manifest-to-physical-name-cover bridge, NOT a claim
    that the manifest itself enumerates every source-graph name or that
    the caller's Cap'n Proto decoder has been formally refined.
    """
    if (
        manifest.get("manifestVersion") != 2
        or manifest.get("storageMode") != "split-by-direction-and-section"
    ):
        raise ValueError("unsupported published numeric-v2 name manifest")
    source = manifest.get("source")
    if not isinstance(source, Mapping):
        raise ValueError("missing graph source manifest")
    artifact = source.get("artifactName")
    if not isinstance(artifact, str) or not artifact:
        raise ValueError("manifest source artifact identity missing")
    if audit.get("artifact_id") != artifact:
        raise ValueError("audited graph differs from manifest artifact")
    sections = manifest.get("sections")
    if not isinstance(sections, Mapping):
        raise ValueError("manifest sections missing")
    name_section = sections.get("nodeOfName")
    if not isinstance(name_section, Mapping):
        raise ValueError("manifest nodeOfName section missing")
    chunks = name_section.get("chunks")
    if not isinstance(chunks, list) or not chunks:
        raise ValueError("manifest nodeOfName cover empty or invalid")
    expected: dict[str, tuple[int, str, int, str]] = {}
    for chunk in chunks:
        if not isinstance(chunk, Mapping):
            raise ValueError("manifest name chunk is not an object")
        index, language, length, uri = (
            chunk.get("chunkIndex"), chunk.get("lang"),
            chunk.get("length"), chunk.get("objectPath")
        )
        if (
            type(index) is not int or index < 0
            or not isinstance(language, str) or not language
            or type(length) is not int or length < 0
            or not isinstance(uri, str)
            or not uri.startswith(f"hf://datasets/acrion/zelph/{artifact}/shards/nodeOfName/")
            or "/../" in uri or uri.endswith("/..")
        ):
            raise ValueError("untrusted name chunk identity or path in manifest")
        name_id = f"nodeOfName-chunk-{index:06d}-{language}"
        if name_id in expected:
            raise ValueError("duplicate manifest name chunk identity")
        expected[name_id] = (index, language, length, uri)
    receipts = audit.get("physical_receipts")
    if not isinstance(receipts, list):
        raise ValueError("no audited physical byte receipts")
    actual: dict[str, tuple[int, str, int, str]] = {}
    for receipt in receipts:
        if not isinstance(receipt, Mapping):
            raise ValueError("malformed byte receipt")
        name_id = receipt.get("shard_id")
        if not isinstance(name_id, str) or name_id in actual:
            raise ValueError("duplicate or invalid audited shard ID")
        actual[name_id] = (
            receipt.get("chunk_index"), receipt.get("language"),
            receipt.get("byte_count"), receipt.get("object_uri")
        )
    if actual != expected:
        raise ValueError("manifest/decoded name-object cover differs in key, length or URI")
    if audit.get("declared_object_set_exhausted") is not True:
        raise ValueError("audited physical object set not exhausted")
    return {
        "version": "itir.zelph.manifest_name_cover_bridge.v1",
        "artifact_id": artifact,
        "graph_revision": audit.get("graph_revision"),
        "manifest_declared_name_cover_exhausted": True,
        "matched_physical_object_count": len(expected),
        "actual_byte_sha_receipts_present": True,
        "decoder_refinement_proved": False,
        "source_graph_name_domain_exhausted": False,
        "graph_query_family_complete": False,
        "candidate_only": True,
        "source_support_paid": False,
    }


@dataclass(frozen=True)
class DeclaredAdjacencyObject:
    direction: str
    chunk_index: int
    size_bytes: int
    sha256_hex: str
    object_uri: str


def audit_selected_adjacency_against_bin(
    *,
    route: Mapping[str, Any],
    declared: Sequence[DeclaredAdjacencyObject],
    raw_objects: Mapping[tuple[str, int], bytes],
    decode: Callable[[bytes], tuple[str, int, Sequence[tuple[int, Sequence[int]]]]],
) -> dict[str, Any]:
    """Compare exact decoded physical chunks with the original-bin root oracle.

    This only proves equality for the declared *one-hop left/right adjacency*
    of the named root nodes between two caller-supplied carriers. The original
    .bin itself is not authenticated as the exact published HF dataset.
    It does not prove P31/P279 closure, longer relation words, native P14143,
    absence in Wikidata, qualifier/reference equivalence or edit authority.
    """
    if route.get("routeVersion") != "zelph-filtered-route/v1":
        raise ValueError("filtered route source contract required")
    qid_nodes = route.get("qidToZelphNodeIds")
    routing = route.get("nodeRoutes")
    oracle = route.get("nodeAdjacency")
    if not isinstance(qid_nodes, Mapping) or not isinstance(routing, Mapping):
        raise ValueError("source route node map missing")
    if not isinstance(oracle, Mapping):
        raise ValueError("source-bin adjacency oracle was not emitted")
    targets = {str(node) for node in qid_nodes.values() if type(node) is int}
    if not targets or set(routing) != targets or set(oracle) != targets:
        raise ValueError("source route/oracle target-node domain mismatch")

    required: set[tuple[str, int]] = set()
    for node in targets:
        branches = routing[node]
        if not isinstance(branches, Mapping):
            raise ValueError("route branch missing")
        for direction in ("left", "right"):
            indexes = branches.get(direction)
            if not isinstance(indexes, list) or any(
                type(i) is not int or i < 0 for i in indexes
            ):
                raise ValueError("invalid route adjacency chunk family")
            if len(indexes) != len(set(indexes)):
                raise ValueError("duplicate route adjacency chunk")
            required.update((direction, idx) for idx in indexes)

    expected: dict[tuple[str, int], DeclaredAdjacencyObject] = {}
    for obj in declared:
        key = (obj.direction, obj.chunk_index)
        if obj.direction not in {"left", "right"}:
            raise ValueError("unexpected physical adjacency section")
        if key in expected:
            raise ValueError("duplicate physical adjacency chunk")
        if (
            type(obj.chunk_index) is not int or obj.chunk_index < 0
            or type(obj.size_bytes) is not int or obj.size_bytes < 0
            or not _SHA256.fullmatch(obj.sha256_hex)
            or not isinstance(obj.object_uri, str)
            or "/../" in obj.object_uri
        ):
            raise ValueError("invalid physical adjacency object metadata")
        expected[key] = obj
    if set(expected) != required or set(raw_objects) != required:
        raise ValueError("selected physical adjacency cover differs from route")
    observations: dict[tuple[str, str], set[int]] = defaultdict(set)
    seen_node_chunk: set[tuple[str, str, int]] = set()
    physical_receipts = []
    for direction, idx in sorted(required):
        entry = expected[(direction, idx)]
        raw = raw_objects[(direction, idx)]
        if (
            not isinstance(raw, bytes) or len(raw) != entry.size_bytes
            or sha256(raw).hexdigest() != entry.sha256_hex
        ):
            raise ValueError("selected adjacency bytes/digest mismatch")
        actual_direction, actual_index, pairs = decode(raw)
        if actual_direction != direction or actual_index != idx:
            raise ValueError("decoded physical adjacency direction/index mismatch")
        for node, neighbors in pairs:
            if type(node) is not int or node < 0:
                raise ValueError("decoded adjacency has invalid root node")
            if not isinstance(neighbors, Sequence) or isinstance(neighbors, (str, bytes)):
                raise ValueError("decoded adjacency neighbors must be finite list")
            if any(type(adj) is not int or adj < 0 for adj in neighbors):
                raise ValueError("decoded adjacency has invalid neighbor node")
            node_key = str(node)
            if node_key not in targets:
                continue
            unique_pair = (node_key, direction, idx)
            if unique_pair in seen_node_chunk:
                raise ValueError("duplicate root row within selected physical chunk")
            seen_node_chunk.add(unique_pair)
            observations[(node_key, direction)].update(neighbors)
        physical_receipts.append({
            "direction": direction,
            "chunk_index": idx,
            "size_bytes": entry.size_bytes,
            "sha256": entry.sha256_hex,
            "object_uri": entry.object_uri,
        })
    for node in sorted(targets):
        for direction in ("left", "right"):
            expected_chunks = routing[node][direction]
            if any((node, direction, idx) not in seen_node_chunk for idx in expected_chunks):
                raise ValueError("routed root missing in advertised physical chunk")
            oracle_node = oracle[node]
            if not isinstance(oracle_node, Mapping):
                raise ValueError("missing original-bin adjacency oracle node")
            if oracle_node.get(direction + "Truncated") is not False:
                raise ValueError("original-bin adjacency oracle truncated or unverified")
            source_values = oracle_node.get(direction)
            if not isinstance(source_values, list) or any(
                type(x) is not int or x < 0 for x in source_values
            ):
                raise ValueError("invalid original-bin adjacency values")
            if set(source_values) != observations[(node, direction)]:
                raise ValueError("selected physical adjacency differs from original-bin oracle")
    return {
        "version": "itir.zelph.same_bin_selected_adjacency_audit.v1",
        "root_node_count": len(targets),
        "physical_object_count": len(required),
        "physical_byte_count": sum(item["size_bytes"] for item in physical_receipts),
        "physical_receipts": physical_receipts,
        "one_hop_root_adjacency_equal_to_source_bin": True,
        "source_bin_to_hf_dataset_identity_proved": False,
        "all_relation_words_complete": False,
        "native_statement_coverage": False,
        "global_negative_answer_authority": False,
        "candidate_only": True,
    }
