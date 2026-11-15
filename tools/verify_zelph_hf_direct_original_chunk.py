#!/usr/bin/env python3
"""Direct, route-free ORIGINAL Zelph packed chunk byte comparison.

For one explicitly named (section, chunkIndex), crosscheck independently
pinned original manifest/index geometry, then stream the published full HF
shard object and original .bin HTTP206 range in bounded chunks. Compare bytes,
not hash labels alone. This deliberately DOES NOT infer node/QID routes, name
domain closure, query answers, source truth or edit authority.

The transport is exclusively itir_mcp.shard_transport. No new HF client.
"""
from __future__ import annotations

import argparse
from contextlib import ExitStack
from hashlib import sha256
import json
from pathlib import Path
import re
import sys
from typing import Any, Callable

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "itir-mcp" / "src"))

from itir_mcp.shard_transport import (
    open_pinned_zelph_complete_object,
    open_pinned_zelph_range,
)
from verify_zelph_bin_shard_exact import _ARTIFACT, _manifest_index, _read_json
from verify_zelph_index_manifest_original import verify_index_manifest_files

_SECTIONS = ("left", "right", "nameOfNode", "nodeOfName")
_REV = re.compile(r"[0-9a-f]{40}\Z")
_SHA = re.compile(r"[0-9a-f]{64}\Z")
_BLOCK = 1024 * 1024


def verify_direct_original_chunk(
    *, manifest_path: Path, original_index_path: Path,
    dataset_revision: str, manifest_sha256: str,
    section: str, chunk_index: int,
    original_index_sha256: str | None = None,
    max_chunk_mib: int = 128,
    opener: Callable[..., Any] | None = None,
) -> dict[str, Any]:
    if type(dataset_revision) is not str or not _REV.fullmatch(dataset_revision):
        raise ValueError("immutable HF 40-hex revision required")
    if type(manifest_sha256) is not str or not _SHA.fullmatch(manifest_sha256):
        raise ValueError("independently pinned original manifest digest required")
    if section not in _SECTIONS or type(chunk_index) is not int or chunk_index < 0:
        raise ValueError("explicit original section and nonnegative chunk index required")
    if type(max_chunk_mib) is not int or not 0 < max_chunk_mib <= 16384:
        raise ValueError("positive bounded chunk MiB budget required")
    # Full original upstream index-to-manifest offset cover and original
    # complete source length are checked before any remote payload byte.
    crosswalk = verify_index_manifest_files(
        manifest_path=manifest_path, index_path=original_index_path,
        manifest_sha256=manifest_sha256, index_sha256=original_index_sha256,
    )
    manifest = _read_json(manifest_path, 16 * 1024 * 1024)
    index = _manifest_index(manifest, _ARTIFACT)
    key = (section, chunk_index)
    if key not in index:
        raise ValueError("explicit selected chunk absent from original published manifest")
    item = index[key]
    size, offset = item["length"], item["offset"]
    if size > max_chunk_mib * 1024 * 1024:
        raise ValueError("original selected chunk exceeds explicit byte budget")
    source_size = crosswalk["original_bin_size_bytes"]
    if offset + size > source_size:
        raise ValueError("selected original chunk interval exceeds original .bin size")
    original_uri = f"hf://datasets/acrion/zelph/{_ARTIFACT}.bin"
    digest_shard = sha256()
    digest_original = sha256()
    count = 0
    with ExitStack() as stack:
        published = stack.enter_context(open_pinned_zelph_complete_object(
            hf_uri=item["object_uri"], revision=dataset_revision,
            expected_size=size, max_bytes=max_chunk_mib * 1024 * 1024,
            opener=opener,
        ))
        original = stack.enter_context(open_pinned_zelph_range(
            hf_uri=original_uri, revision=dataset_revision, start=offset,
            length=size, total_size=source_size,
            max_bytes=max_chunk_mib * 1024 * 1024, opener=opener,
        ))
        while count < size:
            amount = min(_BLOCK, size - count)
            a, b = published.read(amount), original.read(amount)
            if len(a) != amount or len(b) != amount or a != b:
                raise ValueError("published HF shard and original .bin HTTP206 packed bytes differ")
            digest_shard.update(a)
            digest_original.update(b)
            count += amount
        if published.read(1) or original.read(1):
            raise ValueError("selected original/shard source response has trailing bytes")
        object_status = getattr(published, "status", None)
    if digest_shard.digest() != digest_original.digest():
        raise ValueError("selected original and published shard raw hashes diverge")
    return {
        "version": "itir.zelph.direct_original_selected_chunk_equality.v1",
        "dataset_revision": dataset_revision,
        "original_manifest_raw_sha256": manifest_sha256,
        "original_index_raw_sha256": crosswalk["original_index_raw_sha256_rechecked"],
        "source_bin_size_bytes": source_size,
        "section": section, "chunk_index": chunk_index,
        "original_source_offset": offset,
        "source_range_end_inclusive": offset + size - 1,
        "bytes_compared": size,
        "published_object_uri": item["object_uri"],
        "original_binary_uri": original_uri,
        "published_shard_http_status": object_status,
        "original_source_http_status": 206,
        "original_packed_range_raw_sha256": digest_original.hexdigest(),
        "published_shard_raw_sha256": digest_shard.hexdigest(),
        "exact_original_packed_bytes_equal_published_shard": True,
        "full_index_manifest_offset_cover_checked": True,
        "original_bin_full_digest_verified": False,
        "original_qid_route_verified": False,
        "whole_name_domain_enumerated": False,
        "all_query_frontiers_closed": False,
        "native_p854_source_support_paid": False,
        "s29_persistence_paid": False,
        "edit_authority": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--original-index", type=Path, required=True)
    parser.add_argument("--dataset-revision", required=True)
    parser.add_argument("--manifest-sha256", required=True)
    parser.add_argument("--original-index-sha256")
    parser.add_argument("--section", choices=_SECTIONS, required=True)
    parser.add_argument("--chunk-index", type=int, required=True)
    parser.add_argument("--max-chunk-mib", type=int, default=128)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--execute", action="store_true",
                        help="explicit opt-in to real published shard + original .bin HTTP ranges")
    args = parser.parse_args()
    try:
        if args.output.exists() or args.output.is_symlink():
            raise ValueError("refuse overwrite of existing physical chunk evidence receipt")
        if not args.execute:
            plan = {
                "version": "itir.zelph.direct_original_chunk_plan.v1",
                "dataset_revision": args.dataset_revision,
                "section": args.section, "chunk_index": args.chunk_index,
                "max_chunk_mib": args.max_chunk_mib,
                "original_bin_download_requested": False,
                "network_executed": False, "edit_authority": False,
            }
            print(json.dumps(plan, sort_keys=True, indent=2))
            return 0
        proof = verify_direct_original_chunk(
            manifest_path=args.manifest,
            original_index_path=args.original_index,
            dataset_revision=args.dataset_revision,
            manifest_sha256=args.manifest_sha256,
            original_index_sha256=args.original_index_sha256,
            section=args.section, chunk_index=args.chunk_index,
            max_chunk_mib=args.max_chunk_mib,
        )
        with args.output.open("x", encoding="utf-8") as stream:
            json.dump(proof, stream, sort_keys=True, indent=2)
            stream.write("\n")
        print(json.dumps(proof, sort_keys=True, indent=2))
        return 0
    except (ValueError, OSError, TypeError, KeyError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "blocked", "reason": str(exc),
                          "edit_authority": False}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
