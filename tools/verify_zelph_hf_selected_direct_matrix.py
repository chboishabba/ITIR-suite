#!/usr/bin/env python3
"""P0-S: compare an EXPLICIT selected set of original Zelph HTTP206 chunks.

Reuses the existing immutable manifest/index crosswalk and genuine streaming
complete-object-vs-original-range comparator. PRE-FLIGHTS total two-sided
network bytes before executing any request. No local full 82 GiB .bin required.

Chunk selection is never evidence of QID routing, name-domain coverage,
all-word query completeness, P854 support, S29 review or source authority.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import sys
from typing import Any, Callable

from verify_zelph_bin_shard_exact import _ARTIFACT, _manifest_index, _read_json
from verify_zelph_hf_direct_original_chunk import verify_direct_original_chunk
from verify_zelph_index_manifest_original import verify_index_manifest_files

_SECTIONS = ("left", "right", "nameOfNode", "nodeOfName")
_CHUNK = re.compile(r"(left|right|nameOfNode|nodeOfName):([0-9]+)\Z")
_SHA40 = re.compile(r"[0-9a-f]{40}\Z")
_SHA64 = re.compile(r"[0-9a-f]{64}\Z")
_MIB = 1024 * 1024


def parse_keys(tokens: list[str]) -> list[tuple[str, int]]:
    if not isinstance(tokens, list) or not 0 < len(tokens) <= 4096:
        raise ValueError("1..4096 explicit original chunk keys required")
    result = []
    for token in tokens:
        m = _CHUNK.fullmatch(token) if isinstance(token, str) else None
        if not m or int(m[2]) > 2**32 - 1:
            raise ValueError("invalid original section:chunk-index key")
        result.append((m[1], int(m[2])))
    if len(set(result)) != len(result):
        raise ValueError("duplicate original selected chunk key")
    return sorted(result, key=lambda p: (_SECTIONS.index(p[0]), p[1]))


def plan_matrix(*, manifest_path: Path, original_index_path: Path,
                dataset_revision: str, manifest_sha256: str,
                original_index_sha256: str, keys: list[tuple[str, int]],
                max_total_mib: int = 1024, max_chunk_mib: int = 128) -> dict[str, Any]:
    if (not isinstance(dataset_revision, str) or not _SHA40.fullmatch(dataset_revision)
            or not isinstance(manifest_sha256, str) or not _SHA64.fullmatch(manifest_sha256)
            or not isinstance(original_index_sha256, str)
            or not _SHA64.fullmatch(original_index_sha256)):
        raise ValueError("immutable revision, independent manifest and index SHA required")
    if (type(max_total_mib) is not int or not 0 < max_total_mib <= 65536
            or type(max_chunk_mib) is not int or not 0 < max_chunk_mib <= 16384):
        raise ValueError("bounded positive total/single chunk budget required")
    if (not isinstance(keys, list) or not 0 < len(keys) <= 4096
            or len(set(keys)) != len(keys)
            or any(type(key) is not tuple or len(key) != 2
                   or key[0] not in _SECTIONS
                   or type(key[1]) is not int or not 0 <= key[1] <= 2**32 - 1
                   for key in keys)):
        raise ValueError("invalid explicit physical chunk selection")
    metadata = verify_index_manifest_files(
        manifest_path=manifest_path, index_path=original_index_path,
        manifest_sha256=manifest_sha256, index_sha256=original_index_sha256)
    if (metadata.get("all_manifest_chunk_offsets_equal_original_index") is not True
            or metadata.get("entire_index_partition_gap_free") is not True
            or metadata.get("entire_index_partition_nonoverlapping") is not True):
        raise ValueError("original complete index/manifest geometry not proven")
    index = _manifest_index(_read_json(manifest_path, 16 * _MIB), _ARTIFACT)
    entries = []
    for section, number in sorted(keys, key=lambda p: (_SECTIONS.index(p[0]), p[1])):
        if (section, number) not in index:
            raise ValueError("selected section/index missing from original manifest")
        item = index[(section, number)]
        size, offset = item["length"], item["offset"]
        if size > max_chunk_mib * _MIB:
            raise ValueError("individual selected chunk exceeds byte budget")
        if offset + size > metadata["original_bin_size_bytes"]:
            raise ValueError("selected source interval exceeds full original binary")
        entries.append({"section": section, "chunk_index": number,
                        "source_offset": offset, "source_end_inclusive": offset + size - 1,
                        "bytes": size, "published_object_uri": item["object_uri"]})
    bytes_one_side = sum(r["bytes"] for r in entries)
    if 2 * bytes_one_side > max_total_mib * _MIB:
        raise ValueError("selected two-sided HTTP payload exceeds aggregate budget")
    return {
        "version": "itir.zelph.direct_selected_matrix_plan.v1",
        "revision": dataset_revision,
        "manifest_sha256": manifest_sha256,
        "index_sha256": original_index_sha256,
        "original_bin_size_bytes": metadata["original_bin_size_bytes"],
        "original_chunk_total_count": sum(metadata["section_chunk_counts"].values()),
        "entries": entries,
        "selected_chunk_count": len(entries),
        "selected_bytes_each_source": bytes_one_side,
        "total_two_sided_payload_bytes": 2 * bytes_one_side,
        "max_total_mib": max_total_mib,
        "max_chunk_mib": max_chunk_mib,
        "complete_original_index_geometry_checked": True,
        "network_executed": False, "original_full_bin_downloaded": False,
        "original_full_bin_sha256_verified": False,
        "qid_routes_verified": False,
        "all_query_frontiers_closed": False,
        "edit_authority": False,
    }


def _save(path: Path, value: dict) -> str:
    raw = (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n").encode()
    with path.open("xb") as output:
        output.write(raw)
    return sha256(raw).hexdigest()


def execute_matrix(*, plan: dict, manifest_path: Path,
                   original_index_path: Path, evidence_dir: Path,
                   verify_one: Callable[..., dict] = verify_direct_original_chunk,
                   opener: Callable[..., Any] | None = None) -> dict[str, Any]:
    if evidence_dir.exists() or evidence_dir.is_symlink():
        raise ValueError("immutable physical evidence directory already exists")
    if not evidence_dir.parent.is_dir() or evidence_dir.parent.is_symlink():
        raise ValueError("physical evidence parent must be an existing real directory")
    if plan.get("version") != "itir.zelph.direct_selected_matrix_plan.v1":
        raise ValueError("invalid selected original matrix plan")
    # A stale/mutated plan cannot silently change selected bytes.
    fresh = plan_matrix(
        manifest_path=manifest_path, original_index_path=original_index_path,
        dataset_revision=plan["revision"], manifest_sha256=plan["manifest_sha256"],
        original_index_sha256=plan["index_sha256"],
        keys=[(r["section"], r["chunk_index"]) for r in plan["entries"]],
        max_total_mib=plan["max_total_mib"], max_chunk_mib=plan["max_chunk_mib"])
    if plan != fresh:
        raise ValueError("source manifest/index or selected matrix plan drifted")
    evidence_dir.mkdir(mode=0o700)
    receipts = []
    for row in plan["entries"]:
        kwargs = dict(manifest_path=manifest_path, original_index_path=original_index_path,
            dataset_revision=plan["revision"], manifest_sha256=plan["manifest_sha256"],
            original_index_sha256=plan["index_sha256"],
            section=row["section"], chunk_index=row["chunk_index"],
            max_chunk_mib=plan["max_chunk_mib"])
        if opener is not None:
            kwargs["opener"] = opener
        witness = verify_one(**kwargs)
        digest = witness.get("published_shard_raw_sha256")
        if (witness.get("version") != "itir.zelph.direct_original_selected_chunk_equality.v1"
                or witness.get("dataset_revision") != plan["revision"]
                or witness.get("original_manifest_raw_sha256") != plan["manifest_sha256"]
                or witness.get("original_index_raw_sha256") != plan["index_sha256"]
                or witness.get("section") != row["section"]
                or witness.get("chunk_index") != row["chunk_index"]
                or witness.get("original_source_offset") != row["source_offset"]
                or witness.get("source_range_end_inclusive") != row["source_end_inclusive"]
                or witness.get("bytes_compared") != row["bytes"]
                or witness.get("published_object_uri") != row["published_object_uri"]
                or witness.get("original_source_http_status") != 206
                or witness.get("exact_original_packed_bytes_equal_published_shard") is not True
                or witness.get("full_index_manifest_offset_cover_checked") is not True
                or type(digest) is not str or not _SHA64.fullmatch(digest)
                or witness.get("original_packed_range_raw_sha256") != digest
                or any(witness.get(field) is not False for field in (
                    "original_bin_full_digest_verified", "original_qid_route_verified",
                    "all_query_frontiers_closed", "native_p854_source_support_paid",
                    "s29_persistence_paid", "edit_authority"))):
            raise ValueError("physical chunk witness identity, equality, or authority mismatch")
        name = f"{row['section']}-{row['chunk_index']:06d}.json"
        receipt_sha = _save(evidence_dir / name, witness)
        receipts.append({"section": row["section"], "chunk_index": row["chunk_index"],
            "bytes_equal": row["bytes"], "sha256": digest,
            "receipt_file": name, "receipt_sha256": receipt_sha})
    final = {
        "version": "itir.zelph.direct_selected_matrix_receipt.v1",
        "dataset_revision": plan["revision"],
        "manifest_sha256": plan["manifest_sha256"],
        "original_index_sha256": plan["index_sha256"],
        "original_bin_size_bytes": plan["original_bin_size_bytes"],
        "original_chunk_total_count": plan["original_chunk_total_count"],
        "selected_chunk_count": len(receipts),
        "selected_byte_count": sum(x["bytes_equal"] for x in receipts),
        "selected_receipts": receipts,
        "all_explicitly_selected_chunks_byte_equal": True,
        "all_original_chunks_byte_checked": False,
        "full_original_binary_downloaded": False,
        "full_original_bin_sha256_verified": False,
        "qid_routes_verified": False,
        "all_query_frontiers_closed": False,
        "whole_name_domain_enumerated": False,
        "native_p854_source_support_paid": False,
        "s29_persistence_paid": False,
        "edit_authority": False,
    }
    # Written only when EVERY exact selected source HTTP206 witness succeeds.
    _save(evidence_dir / "selected-matrix-complete.json", final)
    return final


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--original-index", type=Path, required=True)
    p.add_argument("--dataset-revision", required=True)
    p.add_argument("--manifest-sha256", required=True)
    p.add_argument("--original-index-sha256", required=True)
    p.add_argument("--chunk", action="append", required=True)
    p.add_argument("--evidence-dir", type=Path, required=True)
    p.add_argument("--max-total-mib", type=int, default=1024)
    p.add_argument("--max-chunk-mib", type=int, default=128)
    p.add_argument("--execute", action="store_true")
    args = p.parse_args()
    try:
        plan = plan_matrix(
            manifest_path=args.manifest, original_index_path=args.original_index,
            dataset_revision=args.dataset_revision,
            manifest_sha256=args.manifest_sha256,
            original_index_sha256=args.original_index_sha256,
            keys=parse_keys(args.chunk), max_total_mib=args.max_total_mib,
            max_chunk_mib=args.max_chunk_mib)
        if not args.execute:
            print(json.dumps(plan, sort_keys=True, indent=2))
            return 0
        out = execute_matrix(plan=plan, manifest_path=args.manifest,
            original_index_path=args.original_index, evidence_dir=args.evidence_dir)
        print(json.dumps(out, sort_keys=True, indent=2))
        return 0
    except (OSError, ValueError, TypeError, KeyError, OverflowError,
            json.JSONDecodeError) as exc:
        print(json.dumps({"status": "blocked", "reason": str(exc),
                          "edit_authority": False}, sort_keys=True), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
