#!/usr/bin/env python3
"""P0/P2: compare selected published Zelph shard bytes with original .bin ranges.

This is a bounded-memory *same-file source* witness. It never scans or loads the
82 GiB graph, and does not authenticate that the caller's .bin is the published
Wikidata source: that independent source provenance remains necessary.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import sys
from typing import Any, BinaryIO, Mapping

_ARTIFACT = "wikidata-20260309-all"
_REPO = "acrion/zelph"
_SHA40 = re.compile(r"[0-9a-f]{40}\Z")
_SHA64 = re.compile(r"[0-9a-f]{64}\Z")
_SECTIONS = ("left", "right", "nameOfNode", "nodeOfName")
_BLOCK = 1024 * 1024


def _unique_json(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _read_json(path: Path, max_size: int) -> dict[str, Any]:
    if not 0 < path.stat().st_size <= max_size:
        raise ValueError(f"invalid input JSON size: {path}")
    data = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_unique_json)
    if not isinstance(data, dict):
        raise ValueError("JSON root must be object")
    return data


def _checked_int(value: Any, where: str) -> int:
    if type(value) is not int or value < 0:
        raise ValueError(f"nonnegative integer required at {where}")
    return value


def _manifest_index(manifest: Mapping[str, Any], artifact: str) -> dict[tuple[str, int], dict]:
    """One strict original-v2 chunk ABI, accepting two documented wire dialects.

    Historical ITIR synthetic index: manifestVersion=2, storageMode=
    split-by-direction-and-section, chunks.offset, source.artifactName.
    Upstream Zelph emit_zelph_hf_v2.py: manifestVersion=zelph-hf-layout/v2,
    storageMode=multi-object-shards, chunks.sourceOffset, source.binPath.
    Preserve all exact original byte offsets, identity and path checks.
    """
    version, mode = manifest.get("manifestVersion"), manifest.get("storageMode")
    legacy = version == 2 and mode == "split-by-direction-and-section"
    upstream = (version == "zelph-hf-layout/v2"
                and mode == "multi-object-shards")
    if not legacy and not upstream:
        raise ValueError("unsupported published manifest v2 layout")
    source = manifest.get("source")
    if not isinstance(source, dict):
        raise ValueError("manifest names a different original graph")
    if legacy and source.get("artifactName") != artifact:
        raise ValueError("manifest names a different original graph")
    if upstream:
        expected_bin_uri = f"hf://datasets/{_REPO}/{artifact}.bin"
        if source.get("binPath") != expected_bin_uri:
            raise ValueError("upstream manifest source.binPath is not pinned original HF artifact")
        if ("artifactName" in source and source["artifactName"] != artifact):
            raise ValueError("upstream manifest artifactName differs from original graph")
        if manifest.get("transport", {}).get("primary") != "hf-object-fetch":
            raise ValueError("upstream original manifest must use HF-object-fetch")
    sections = manifest.get("sections")
    if not isinstance(sections, dict) or set(sections) != set(_SECTIONS):
        raise ValueError("manifest is missing one of four original graph sections")
    index: dict[tuple[str, int], dict] = {}
    all_bytes = 0
    for section in _SECTIONS:
        parts = sections[section]
        if not isinstance(parts, dict) or not isinstance(parts.get("chunks"), list):
            raise ValueError(f"manifest section invalid: {section}")
        section_bytes = 0
        for part in parts["chunks"]:
            if not isinstance(part, dict):
                raise ValueError("manifest chunk is not an object")
            number = _checked_int(part.get("chunkIndex"), "chunkIndex")
            if upstream:
                offset = _checked_int(part.get("sourceOffset"), "sourceOffset")
                if "offset" in part and part["offset"] != offset:
                    raise ValueError("upstream sourceOffset and offset disagree")
            else:
                offset = _checked_int(part.get("offset"), "offset")
                if "sourceOffset" in part and part["sourceOffset"] != offset:
                    raise ValueError("legacy offset and sourceOffset disagree")
            size = _checked_int(part.get("length"), "length")
            if size == 0:
                raise ValueError("zero-length Cap'n Proto packed chunk")
            if section in {"left", "right"}:
                if part.get("which") != section:
                    raise ValueError("manifest adjacency section direction mismatch")
                suffix = f"chunk-{number:06d}.capnp-packed"
            else:
                lang = part.get("lang")
                if (not isinstance(lang, str)
                        or not re.fullmatch(r"[a-zA-Z][a-zA-Z0-9_.-]{0,31}", lang)):
                    raise ValueError("unsafe or missing name language")
                suffix = f"chunk-{number:06d}-{lang}.capnp-packed"
            relative = f"{artifact}/shards/{section}/{suffix}"
            expected = f"hf://datasets/{_REPO}/{relative}"
            if part.get("objectPath") != expected:
                raise ValueError(
                    f"manifest object is not exact immutable artifact path: {section}/{number}"
                )
            if upstream:
                obj = part.get("object")
                if (not isinstance(obj, dict) or obj.get("path") != expected
                        or type(obj.get("sizeBytes")) is not int
                        or obj["sizeBytes"] != size):
                    raise ValueError("upstream manifest nested object path/length mismatch")
                if part.get("sourceRange") != f"bytes={offset}-{offset + size - 1}":
                    raise ValueError("upstream manifest sourceRange mismatches sourceOffset/length")
            key = (section, number)
            if key in index:
                raise ValueError(f"duplicate manifest chunk {key}")
            index[key] = {
                "offset": offset, "length": size,
                "language": part.get("lang"), "relative": relative,
                "object_uri": expected,
            }
            section_bytes += size
            all_bytes += size
        if upstream and (
            type(parts.get("chunkCount")) is not int
            or parts["chunkCount"] != len(parts["chunks"])
            or type(parts.get("totalBytes")) is not int
            or parts["totalBytes"] != section_bytes
        ):
            raise ValueError(f"upstream manifest {section} section size/count mismatch")
    for section in _SECTIONS:
        numbers = sorted(number for sect, number in index if sect == section)
        if numbers != list(range(len(numbers))):
            raise ValueError(f"manifest {section} chunks not dense section-global 0..N-1")
    if upstream and (
        type(source.get("totalChunkCount")) is not int
        or source["totalChunkCount"] != len(index)
        or type(source.get("totalChunkBytes")) is not int
        or source["totalChunkBytes"] != all_bytes
    ):
        raise ValueError("upstream source total chunk count/byte count mismatch")
    return index


def _selected_route_keys(route: Mapping[str, Any]) -> set[tuple[str, int]]:
    if route.get("routeVersion") != "zelph-filtered-route/v1":
        raise ValueError("original .bin filtered route expected")
    qids = route.get("requestedQids")
    nodes = route.get("qidToZelphNodeIds")
    name_chunks = route.get("qidToNodeOfNameChunks")
    node_routes = route.get("nodeRoutes")
    if not (isinstance(qids, list) and qids and isinstance(nodes, dict)
            and isinstance(name_chunks, dict) and isinstance(node_routes, dict)):
        raise ValueError("incomplete route physical selection")
    if (len(qids) != len(set(qids)) or set(nodes) != set(qids)
            or set(name_chunks) != set(qids)
            or any(not isinstance(qid, str) or not re.fullmatch(r"Q[1-9][0-9]*", qid) for qid in qids)):
        raise ValueError("QID route domain not exact")
    if any(type(nodes[qid]) is not int or nodes[qid] < 0
           or type(name_chunks[qid]) is not int or name_chunks[qid] < 0
           for qid in qids):
        raise ValueError("unresolved QID cannot certify source-bin chunk equality")
    wanted: set[tuple[str, int]] = {
        ("nodeOfName", name_chunks[qid]) for qid in qids
    }
    extra_numeric = route.get("additionalNumericNodes", [])
    if (
        not isinstance(extra_numeric, list)
        or len(extra_numeric) > 100000
        or any(type(node) is not int or not 0 <= node <= (2**64 - 1)
               for node in extra_numeric)
        or extra_numeric != sorted(set(extra_numeric))
    ):
        raise ValueError("extra numeric frontier nodes must be sorted distinct uint64 values")
    expected_root_nodes = {str(nodes[qid]) for qid in qids} | {
        str(node) for node in extra_numeric
    }
    if set(node_routes) != expected_root_nodes:
        raise ValueError("node route domain differs from named and numeric source roots")
    for node, parts in node_routes.items():
        if not isinstance(parts, dict):
            raise ValueError(f"invalid route for {node}")
        for section in ("left", "right", "nameOfNode"):
            nums = parts.get(section)
            if not isinstance(nums, list) or any(type(n) is not int or n < 0 for n in nums):
                raise ValueError(f"invalid {section} chunk selection")
            if len(nums) != len(set(nums)):
                raise ValueError("duplicate physical chunk route")
            wanted.update((section, n) for n in nums)
    return wanted


def _compare(source: BinaryIO, shard_path: Path, offset: int, size: int) -> str:
    if not shard_path.is_file() or shard_path.stat().st_size != size:
        raise ValueError(f"physical shard missing or wrong length: {shard_path}")
    source.seek(offset)
    digest = sha256()
    remaining = size
    with shard_path.open("rb") as shard:
        while remaining:
            width = min(_BLOCK, remaining)
            a, b = source.read(width), shard.read(width)
            if len(a) != width or len(b) != width or a != b:
                raise ValueError(f"source .bin and shard bytes differ: {shard_path} at offset {offset + size - remaining}")
            digest.update(b)
            remaining -= width
        if shard.read(1):
            raise ValueError("shard contains trailing bytes")
    return digest.hexdigest()


def verify_selected_source_ranges(
    *, manifest_path: Path, route_path: Path, source_bin: Path,
    shard_root: Path, dataset_revision: str, manifest_sha256: str,
    artifact: str = _ARTIFACT, max_selected_gib: int = 16,
) -> dict[str, Any]:
    if not _SHA40.fullmatch(dataset_revision):
        raise ValueError("immutable HF dataset SHA required")
    if not _SHA64.fullmatch(manifest_sha256):
        raise ValueError("exact 64-hex pinned manifest digest required")
    raw_manifest = manifest_path.read_bytes()
    if not raw_manifest or len(raw_manifest) > 16 * 1024 * 1024:
        raise ValueError("raw manifest is empty or over 16 MiB cap")
    if sha256(raw_manifest).hexdigest() != manifest_sha256:
        raise ValueError("physical manifest SHA256 mismatch")
    manifest = _read_json(manifest_path, 16 * 1024 * 1024)
    route = _read_json(route_path, 64 * 1024 * 1024)
    index = _manifest_index(manifest, artifact)
    selected = _selected_route_keys(route)
    if not selected:
        raise ValueError("empty selected physical object domain")
    if selected - set(index):
        raise ValueError(f"route references absent physical chunks: {sorted(selected - set(index))}")
    original_size = source_bin.stat().st_size
    source = manifest.get("source")
    if not isinstance(source, dict):
        raise ValueError("manifest original source missing")
    manifest_size = source.get("binSizeBytes")
    if manifest_size is not None and original_size != _checked_int(manifest_size, "source.binSizeBytes"):
        raise ValueError("local original .bin size differs from manifest")
    route_source = route.get("source")
    if (not isinstance(route_source, dict)
            or original_size != _checked_int(route_source.get("binSizeBytes"), "route.source.binSizeBytes")):
        raise ValueError("local original .bin size differs from route")
    for section, label in (("left", "leftChunkCount"), ("right", "rightChunkCount"),
                           ("nameOfNode", "nameOfNodeChunkCount"),
                           ("nodeOfName", "nodeOfNameChunkCount")):
        if route_source.get(label) != sum(sec == section for sec, _ in index):
            raise ValueError(f"original route/manifest {section} count mismatch")
    for key in selected:
        entry = index[key]
        if entry["offset"] + entry["length"] > original_size:
            raise ValueError(f"selected chunk exceeds .bin length: {key}")
    total = sum(index[key]["length"] for key in selected)
    if type(max_selected_gib) is not int or max_selected_gib <= 0 or total > max_selected_gib * 1024**3:
        raise ValueError(f"selected byte count {total} exceeds explicit max-selected-GiB budget")
    if not shard_root.is_dir():
        raise ValueError("local shard root does not exist")
    # The shard-root points at the containing tree. Do not use manifest
    # supplied arbitrary local paths or allow symlink escape.
    root = shard_root.resolve(strict=True)
    receipts = []
    with source_bin.open("rb") as source_stream:
        for key in sorted(selected):
            entry = index[key]
            # Local artifact path rooted under user-specified, trusted shard-root.
            path = (root / entry["relative"]).resolve(strict=True)
            if not path.is_relative_to(root) or not path.is_file():
                raise ValueError("shard-root symlink/path escape refused")
            shard_sha = _compare(source_stream, path, entry["offset"], entry["length"])
            receipts.append({
                "section": key[0], "chunk_index": key[1],
                "source_offset": entry["offset"],
                "bytes_compared": entry["length"],
                "sha256": shard_sha,
                "object_uri": entry["object_uri"],
            })
    return {
        "version": "itir.zelph.exact_original_bin_selected_hf_ranges.v1",
        "graph_revision_claim": dataset_revision,
        "manifest_sha256_verified": manifest_sha256,
        "route_sha256_verified": sha256(route_path.read_bytes()).hexdigest(),
        "original_bin_local_path": str(source_bin),
        "original_bin_size_bytes": original_size,
        "selected_object_count": len(receipts),
        "selected_bytes_compared": total,
        "physical_receipts": receipts,
        "all_selected_shards_equal_local_original_bin_packed_ranges": True,
        "entire_bin_sha256_verified": False,
        "original_bin_upstream_authenticity_proved": False,
        "manifest_covers_entire_original_graph_proved": False,
        "capnp_decoder_correctness_proved": False,
        "full_query_family_closure_proved": False,
        "native_wikidata_source_proved": False,
        "candidate_only": True,
        "promotion_authority": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--route", type=Path, required=True)
    parser.add_argument("--source-bin", type=Path, required=True)
    parser.add_argument("--shard-root", type=Path, required=True)
    parser.add_argument("--dataset-revision", required=True)
    parser.add_argument("--manifest-sha256", required=True)
    parser.add_argument("--max-selected-gib", type=int, default=16)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        result = verify_selected_source_ranges(
            manifest_path=args.manifest,
            route_path=args.route,
            source_bin=args.source_bin,
            shard_root=args.shard_root,
            dataset_revision=args.dataset_revision,
            manifest_sha256=args.manifest_sha256,
            max_selected_gib=args.max_selected_gib,
        )
        output = json.dumps(result, indent=2, sort_keys=True) + "\n"
        if args.output:
            args.output.write_text(output, encoding="utf-8")
        else:
            sys.stdout.write(output)
        return 0
    except (ValueError, OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        print(json.dumps({"status": "blocked", "reason": str(exc),
                          "promotion_authority": False}, sort_keys=True), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
