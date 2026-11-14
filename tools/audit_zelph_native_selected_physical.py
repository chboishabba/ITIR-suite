#!/usr/bin/env python3
"""P0/A1/A2: stream-hash selected shards, run native Cap'n Proto decoder, join original-bin oracle.

Strictly requires a prior local or immutable-remote source .bin byte-range
equality receipt. Native decoding is source/scoped, not graph closure beyond
the selected root one-hop family, nor native Wikidata source authority.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Mapping

from verify_zelph_bin_shard_exact import (
    _ARTIFACT, _SHA40, _SHA64, _manifest_index, _read_json, _selected_route_keys,
)

_NATIVE_VERSION = "itir.zelph.selected_native_capnp_decode.v1"
_LOCAL_RANGE = "itir.zelph.exact_original_bin_selected_hf_ranges.v1"
_REMOTE_RANGE = "itir.zelph.pinned_hf_remote_bin_ranges.v1"


def _hash_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _verified_range_rows(
    proof: Mapping[str, Any], *, selected: set[tuple[str, int]],
    manifest_sha: str, route_sha: str, revision: str,
) -> dict[tuple[str, int], dict[str, Any]]:
    version = proof.get("version")
    if version == _LOCAL_RANGE:
        if (
            proof.get("all_selected_shards_equal_local_original_bin_packed_ranges") is not True
            or proof.get("manifest_sha256_verified") != manifest_sha
            or proof.get("route_sha256_verified") != route_sha
            or proof.get("graph_revision_claim") != revision
        ):
            raise ValueError("local source-bin range receipt identity invalid")
        raw_rows = proof.get("physical_receipts")
        expected_sha_key = "sha256"
        uri_key = "object_uri"
    elif version == _REMOTE_RANGE:
        if (
            proof.get("selected_raw_remote_bin_ranges_equal_local_shard_bytes") is not True
            or proof.get("manifest_raw_sha256") != manifest_sha
            or proof.get("route_raw_sha256") != route_sha
            or proof.get("dataset_revision") != revision
        ):
            raise ValueError("immutable remote original-bin range receipt identity invalid")
        raw_rows = proof.get("receipts")
        expected_sha_key = "equal_raw_sha256"
        uri_key = "shard_object_uri"
    else:
        raise ValueError("missing same-original-bin physical byte-range witness")
    if not isinstance(raw_rows, list):
        raise ValueError("range witness has no selected physical receipts")
    rows: dict[tuple[str, int], dict[str, Any]] = {}
    for row in raw_rows:
        if not isinstance(row, dict):
            raise ValueError("malformed selected original-bin range receipt")
        key = (row.get("section"), row.get("chunk_index"))
        if key in rows or key not in selected:
            raise ValueError("duplicate or undeclared source-bin range")
        sha = row.get(expected_sha_key)
        if not isinstance(sha, str) or not _SHA64.fullmatch(sha):
            raise ValueError("missing 64-hex physical byte digest")
        rows[key] = {
            "sha256": sha, "size_bytes": row.get("bytes_compared"),
            "uri": row.get(uri_key),
        }
    if set(rows) != selected:
        raise ValueError("source-bin range witness lacks selected physical chunks")
    return rows


def verify_native_selected_shard_answer(
    *, manifest_path: Path, route_path: Path, range_receipt_path: Path,
    shard_root: Path, decoder_executable: Path,
    dataset_revision: str, manifest_sha256: str,
    max_selected_gib: int = 8, decoder_timeout_seconds: int = 900,
) -> dict[str, Any]:
    if not _SHA40.fullmatch(dataset_revision) or not _SHA64.fullmatch(manifest_sha256):
        raise ValueError("immutable HF revision and exact raw manifest SHA256 required")
    if _hash_file(manifest_path) != manifest_sha256:
        raise ValueError("native audit manifest SHA256 mismatch")
    manifest = _read_json(manifest_path, 16 * 1024 * 1024)
    route = _read_json(route_path, 64 * 1024 * 1024)
    proof = _read_json(range_receipt_path, 16 * 1024 * 1024)
    index = _manifest_index(manifest, _ARTIFACT)
    selected = _selected_route_keys(route)
    route_sha = _hash_file(route_path)
    source = route.get("source")
    if not isinstance(source, dict):
        raise ValueError("missing source-bin route header")
    for section, field in (
        ("left", "leftChunkCount"), ("right", "rightChunkCount"),
        ("nameOfNode", "nameOfNodeChunkCount"), ("nodeOfName", "nodeOfNameChunkCount"),
    ):
        if source.get(field) != sum(s == section for s, _ in index):
            raise ValueError("route/manifest section count mismatch")
    if selected - set(index):
        raise ValueError("selected chunk not contained in immutable manifest")
    receipts = _verified_range_rows(
        proof, selected=selected, manifest_sha=manifest_sha,
        route_sha=route_sha, revision=dataset_revision,
    )
    total = sum(index[key]["length"] for key in selected)
    if (
        type(max_selected_gib) is not int or max_selected_gib <= 0
        or total > max_selected_gib * 1024 ** 3
    ):
        raise ValueError("native selected shard budget exceeded")
    root = shard_root.resolve(strict=True)
    if not root.is_dir() or not decoder_executable.is_file():
        raise ValueError("native shard root or Cap'n Proto decoder absent")

    qid_nodes = route["qidToZelphNodeIds"]
    qid_to_name_chunk = route["qidToNodeOfNameChunks"]
    node_routes = route["nodeRoutes"]
    oracle = route.get("nodeAdjacency")
    if not isinstance(oracle, dict) or set(oracle) != set(node_routes):
        raise ValueError("new original-bin one-hop oracle absent or wrong root domain")
    if (route.get("sourceBinToPublishedHfDatasetIdentityVerified") is not False
            or route.get("adjacencyOracleScope") != "bounded-selected-roots-in-source-bin"):
        raise ValueError("original-bin route authority/scope mismatch")
    root_ids = {str(node) for node in qid_nodes.values()}
    # Compile exact decoder invocations for all selected physical shards.
    native_rows: dict[tuple[str, int], list[dict[str, Any]]] = {}
    decoded: list[dict[str, Any]] = []
    for section, number in sorted(selected):
        item = index[(section, number)]
        path = (root / item["relative"]).resolve(strict=True)
        if not path.is_relative_to(root):
            raise ValueError("selected shard escapes trusted local root")
        prev = receipts[(section, number)]
        if (
            path.stat().st_size != item["length"]
            or prev["size_bytes"] != item["length"]
            or prev["uri"] != item["object_uri"]
            or _hash_file(path) != prev["sha256"]
        ):
            raise ValueError("physical bytes no longer match original-bin range proof")
        cmd = [
            str(decoder_executable),
            "--file", str(path), "--section", section,
            "--chunk-index", str(number),
        ]
        if section == "nodeOfName":
            targets = [
                qid for qid, chunk in qid_to_name_chunk.items() if chunk == number
            ]
            cmd.extend(x for qid in sorted(targets) for x in ("--qid", qid))
        else:
            targets = [
                node for node in sorted(root_ids, key=int)
                if number in node_routes[node][section]
            ]
            cmd.extend(x for node in targets for x in ("--node", node))
        if not targets:
            raise ValueError("selected physical chunk has no matching target")
        if section in ("nameOfNode", "nodeOfName"):
            if item["language"] != "wikidata":
                raise ValueError("Wikidata QID/name physical route requires wikidata-language chunk")
            cmd.extend(["--lang", "wikidata"])
        proc = subprocess.run(
            cmd, capture_output=True, text=True, timeout=decoder_timeout_seconds,
            check=False,
        )
        if proc.returncode != 0 or len(proc.stdout) > 32 * 1024 * 1024:
            raise ValueError(f"native decoder failed or overflowed: {section}/{number}: {proc.stderr[:300]}")
        try:
            payload = json.loads(proc.stdout)
        except json.JSONDecodeError as exc:
            raise ValueError("native decoder output is not JSON") from exc
        if (
            not isinstance(payload, dict)
            or payload.get("version") != _NATIVE_VERSION
            or payload.get("section") != section
            or payload.get("chunk_index") != number
            or payload.get("candidate_only") is not True
            or payload.get("authority") is not False
            or not isinstance(payload.get("rows"), list)
        ):
            raise ValueError("native packed decoder schema/scope mismatch")
        if section in ("nodeOfName", "nameOfNode") and payload.get("language") != "wikidata":
            raise ValueError("native decoder changed physical name language")
        native_rows[(section, number)] = payload["rows"]
        decoded.append({
            "section": section, "chunk_index": number,
            "sha256": prev["sha256"], "bytes": item["length"],
            "row_count": len(payload["rows"]),
        })
    for qid, node_id in qid_nodes.items():
        chunk = qid_to_name_chunk[qid]
        rows = native_rows[("nodeOfName", chunk)]
        matches = [
            row for row in rows if row.get("name") == qid
        ]
        if len(matches) != 1 or matches[0].get("node_id") != node_id:
            raise ValueError(f"native nodeOfName one-to-one QID route mismatch: {qid}")
        # The inverse assertion must use nameOfNode, not nodeOfName.
        names = [
            row
            for (section, _), chunk_rows in native_rows.items()
            if section == "nameOfNode"
            for row in chunk_rows
            if row.get("node_id") == node_id and row.get("name") == qid
        ]
        if len(names) != 1:
            raise ValueError(f"native nameOfNode inverse row missing/ambiguous: {qid}")

    physical_neighbours: dict[tuple[str, str], set[int]] = defaultdict(set)
    raw_value_counts: dict[tuple[str, str], int] = defaultdict(int)
    for node_id in root_ids:
        for direction in ("left", "right"):
            source_node = oracle.get(node_id)
            if not isinstance(source_node, dict):
                raise ValueError("source-bin one-hop node oracle missing")
            if source_node.get(direction + "Truncated") is not False:
                raise ValueError("original-bin adjacency was truncated")
            source_adj = source_node.get(direction)
            if not isinstance(source_adj, list) or any(
                type(x) is not int or x < 0 for x in source_adj
            ):
                raise ValueError("invalid original-bin one-hop adjacency")
            for chunk in node_routes[node_id][direction]:
                rows = [
                    row for row in native_rows[(direction, chunk)]
                    if row.get("node_id") == int(node_id)
                ]
                if len(rows) != 1:
                    raise ValueError("root node absent/duplicated in native routed physical chunk")
                row = rows[0]
                neighbors = row.get("neighbors")
                count = row.get("values_seen")
                if (
                    row.get("truncated") is not False
                    or not isinstance(neighbors, list)
                    or any(type(x) is not int or x < 0 for x in neighbors)
                    or type(count) is not int or count < 0
                ):
                    raise ValueError("native adjacency truncated or malformed")
                physical_neighbours[(node_id, direction)].update(neighbors)
                raw_value_counts[(node_id, direction)] += count
            if physical_neighbours[(node_id, direction)] != set(source_adj):
                raise ValueError("native physical adjacency differs from exact original-bin oracle")
            if raw_value_counts[(node_id, direction)] != source_node.get(direction + "ValuesSeen"):
                raise ValueError("native physical adjacency multiplicity/count differs from source")
    return {
        "version": "itir.zelph.native_physical_selected_original_query_cut.v1",
        "dataset_revision": dataset_revision,
        "manifest_sha256": manifest_sha256,
        "route_sha256": route_sha,
        "range_receipt_sha256": _hash_file(range_receipt_path),
        "selected_object_count": len(selected),
        "selected_bytes_rehashed": total,
        "native_schema_decoder_executed": True,
        "selected_name_routes_and_inverse_checked": True,
        "selected_root_one_hop_bidirectional_adjacency_equal_original_bin": True,
        "physical_chunk_receipts": decoded,
        "whole_original_graph_enumerated": False,
        "general_query_family_closed": False,
        "native_P14143_P854_support_proved": False,
        "edit_authority": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("manifest", "route", "range-receipt", "shard-root", "decoder"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--dataset-revision", required=True)
    parser.add_argument("--manifest-sha256", required=True)
    parser.add_argument("--max-selected-gib", type=int, default=8)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        result = verify_native_selected_shard_answer(
            manifest_path=args.manifest, route_path=args.route,
            range_receipt_path=args.range_receipt,
            shard_root=args.shard_root, decoder_executable=args.decoder,
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
    except (ValueError, OSError, KeyError, TypeError, subprocess.TimeoutExpired) as exc:
        print(json.dumps({"status": "blocked", "reason": str(exc),
                          "edit_authority": False}, sort_keys=True), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
