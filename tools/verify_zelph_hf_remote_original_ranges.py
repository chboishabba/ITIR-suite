#!/usr/bin/env python3
"""Compare selected HF-v2 packed shards against exact immutable source .bin HTTP ranges.

Strict remote proof boundary: pinned revision URL, TLS, exact 206 + Content-Range
and byte equality. No 82 GiB full .bin download or query/semantic promotion.
Uses streaming bounded memory and a user-declared total transfer cap.

The operator must already have the *selected* shard files and pinned manifest
locally; this cannot infer that the manifest covers every original graph fact.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import sys
from urllib.request import Request, urlopen
from typing import Any, Callable

from verify_zelph_bin_shard_exact import (
    _ARTIFACT, _BLOCK, _SHA40, _SHA64,
    _manifest_index, _read_json, _selected_route_keys,
)


def compare_remote_source_range(
    *, url: str, shard: Path, start: int, size: int, total_size: int,
    opener: Callable[..., Any] = urlopen, timeout: int = 60
) -> dict[str, Any]:
    """Reject silent 200/full-body fallbacks and incorrect Content-Range.

    `opener` is injectable only for deterministic offline tests; callers
    must construct `url` from the pinned immutable HF revision.
    """
    if not url.startswith("https://huggingface.co/datasets/acrion/zelph/resolve/"):
        raise ValueError("only official immutable Zelph dataset URLs supported")
    if type(start) is not int or type(size) is not int or type(total_size) is not int:
        raise ValueError("byte-range fields must be integers")
    if start < 0 or size <= 0 or start + size > total_size:
        raise ValueError("requested range outside the remote original source")
    if not shard.is_file() or shard.stat().st_size != size:
        raise ValueError("missing or wrong-sized local selected shard")
    end = start + size - 1
    req = Request(
        url, headers={
            "Range": f"bytes={start}-{end}",
            "Accept-Encoding": "identity",
            "User-Agent": "itir-zelph-physical-range-audit/1",
        },
        method="GET",
    )
    with opener(req, timeout=timeout) as response:
        status = getattr(response, "status", None)
        if status != 206:
            raise ValueError(f"range server refused exact HTTP 206 (got {status})")
        content_range = response.headers.get("Content-Range", "")
        required_range = f"bytes {start}-{end}/{total_size}"
        if content_range != required_range:
            raise ValueError(
                f"remote original source Content-Range mismatch: {content_range!r}"
            )
        encoding = response.headers.get("Content-Encoding", "identity").lower()
        if encoding not in ("", "identity"):
            raise ValueError("remote packed bytes unexpectedly content-encoded")
        length = response.headers.get("Content-Length")
        if length is not None and (not length.isdecimal() or int(length) != size):
            raise ValueError("remote original source range length mismatch")
        digest = sha256()
        left = size
        with shard.open("rb") as stream:
            while left:
                amount = min(_BLOCK, left)
                remote_bytes = response.read(amount)
                local_bytes = stream.read(amount)
                if len(remote_bytes) != amount or remote_bytes != local_bytes:
                    raise ValueError("remote original bin range differs from published shard bytes")
                digest.update(remote_bytes)
                left -= amount
            if response.read(1) or stream.read(1):
                raise ValueError("unadvertised trailing bytes in remote range/shard")
    return {
        "source_offset": start,
        "source_end_inclusive": end,
        "bytes_compared": size,
        "equal_raw_sha256": digest.hexdigest(),
        "range_http_status": 206,
        "exact_content_range_verified": True,
    }


def verify_pinned_remote_ranges(
    *, manifest_path: Path, route_path: Path, shard_root: Path,
    dataset_revision: str, manifest_sha256: str,
    max_selected_gib: int = 8,
    opener: Callable[..., Any] = urlopen,
) -> dict[str, Any]:
    if not _SHA40.fullmatch(dataset_revision) or not _SHA64.fullmatch(manifest_sha256):
        raise ValueError("immutable dataset revision and manifest SHA256 required")
    raw_manifest = manifest_path.read_bytes()
    if not raw_manifest or len(raw_manifest) > 16 * 1024 * 1024:
        raise ValueError("missing/oversized original HF manifest")
    if sha256(raw_manifest).hexdigest() != manifest_sha256:
        raise ValueError("pinned original manifest SHA256 mismatch")
    manifest = _read_json(manifest_path, 16 * 1024 * 1024)
    route = _read_json(route_path, 64 * 1024 * 1024)
    index = _manifest_index(manifest, _ARTIFACT)
    selected = _selected_route_keys(route)
    if selected - set(index):
        raise ValueError("original route references chunks outside the pinned manifest")
    route_source = route.get("source")
    if not isinstance(route_source, dict):
        raise ValueError("source-bin route metadata missing")
    total_size = route_source.get("binSizeBytes")
    if type(total_size) is not int or total_size <= 0:
        raise ValueError("source-bin total byte count missing")
    manifest_source = manifest["source"]
    advertised_size = manifest_source.get("binSizeBytes")
    if advertised_size is not None and advertised_size != total_size:
        raise ValueError("manifest and source-bin total sizes differ")
    sections = ("left", "right", "nameOfNode", "nodeOfName")
    counts = ("leftChunkCount", "rightChunkCount", "nameOfNodeChunkCount", "nodeOfNameChunkCount")
    for section, count_label in zip(sections, counts):
        if route_source.get(count_label) != sum(x == section for x, _ in index):
            raise ValueError(f"manifest/source-bin {section} section count mismatch")
    total = sum(index[key]["length"] for key in selected)
    if (type(max_selected_gib) is not int or max_selected_gib <= 0
            or total > max_selected_gib * 1024**3):
        raise ValueError("selected network transfer exceeds explicit budget")
    if not shard_root.is_dir():
        raise ValueError("shard-root directory missing")
    root = shard_root.resolve(strict=True)
    source_url = (
        "https://huggingface.co/datasets/acrion/zelph/resolve/"
        + dataset_revision + "/" + _ARTIFACT + ".bin"
    )
    receipts = []
    for key in sorted(selected):
        item = index[key]
        offset, size = item["offset"], item["length"]
        if offset + size > total_size:
            raise ValueError("manifest source range outside immutable original bin")
        # Path is constructed exclusively by validated manifest section/index.
        local = (root / item["relative"]).resolve(strict=True)
        if not local.is_relative_to(root):
            raise ValueError("shard path escapes verified root")
        proof = compare_remote_source_range(
            url=source_url, shard=local, start=offset, size=size,
            total_size=total_size, opener=opener
        )
        receipts.append({
            "section": key[0], "chunk_index": key[1],
            "shard_object_uri": item["object_uri"],
            **proof,
        })
    return {
        "version": "itir.zelph.pinned_hf_remote_bin_ranges.v1",
        "dataset_revision": dataset_revision,
        "manifest_raw_sha256": manifest_sha256,
        "route_raw_sha256": sha256(route_path.read_bytes()).hexdigest(),
        "source_bin_url": source_url,
        "selected_object_count": len(receipts),
        "selected_byte_count": total,
        "selected_raw_remote_bin_ranges_equal_local_shard_bytes": True,
        "receipts": receipts,
        "all_source_bin_bytes_checked": False,
        "remote_shard_origin_separately_authenticated": False,
        "source_graph_query_closed": False,
        "native_statement_or_P854_proved": False,
        "edit_authority": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--route", type=Path, required=True)
    parser.add_argument("--shard-root", type=Path, required=True)
    parser.add_argument("--dataset-revision", required=True)
    parser.add_argument("--manifest-sha256", required=True)
    parser.add_argument("--max-selected-gib", type=int, default=8)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        receipt = verify_pinned_remote_ranges(
            manifest_path=args.manifest, route_path=args.route,
            shard_root=args.shard_root,
            dataset_revision=args.dataset_revision,
            manifest_sha256=args.manifest_sha256,
            max_selected_gib=args.max_selected_gib,
        )
        data = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
        if args.output:
            args.output.write_text(data, encoding="utf-8")
        else:
            sys.stdout.write(data)
        return 0
    except (ValueError, OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        print(json.dumps({
            "status": "blocked", "reason": str(exc), "edit_authority": False
        }, sort_keys=True), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
