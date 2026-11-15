#!/usr/bin/env python3
"""Resumable physical byte audit for every chunk in one Zelph name section.

This verifies complete published packed-shard bytes versus exact original .bin
HTTP206 intervals via the existing HF connector. A full section byte cover
does NOT imply native name-row enumeration or collision fibre completeness.
Default is dry-run, bounded execute is explicit; no full original download.
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
from verify_zelph_index_manifest_original import verify_index_manifest_files
from verify_zelph_hf_direct_original_chunk import verify_direct_original_chunk

_SHA = re.compile(r"[0-9a-f]{64}\Z")
_REV = re.compile(r"[0-9a-f]{40}\Z")
_NAMES = ("nameOfNode", "nodeOfName")
_VERSION = "itir.zelph.direct_original_selected_chunk_equality.v1"


def _read_receipt(path: Path) -> dict:
    if path.is_symlink() or not path.is_file() or not 0 < path.stat().st_size <= 32768:
        raise ValueError("invalid retained original name-chunk receipt")
    def no_duplicate(pairs):
        out = {}
        for k, v in pairs:
            if k in out:
                raise ValueError("duplicate receipt JSON field")
            out[k] = v
        return out
    result = json.loads(path.read_bytes(), object_pairs_hook=no_duplicate)
    if not isinstance(result, dict):
        raise ValueError("name-chunk receipt must be a JSON object")
    return result


def _check_receipt(proof: dict, *, row: dict, number: int, section: str,
                   rev: str, manifest_sha: str, index_sha: str, bin_size: int):
    mandatory = {
        "version": _VERSION, "dataset_revision": rev,
        "original_manifest_raw_sha256": manifest_sha,
        "original_index_raw_sha256": index_sha,
        "source_bin_size_bytes": bin_size,
        "section": section, "chunk_index": number,
        "original_source_offset": row["offset"],
        "source_range_end_inclusive": row["offset"] + row["length"] - 1,
        "bytes_compared": row["length"],
        "published_object_uri": row["object_uri"],
        "original_binary_uri": f"hf://datasets/acrion/zelph/{_ARTIFACT}.bin",
        "original_source_http_status": 206,
        "exact_original_packed_bytes_equal_published_shard": True,
        "full_index_manifest_offset_cover_checked": True,
        "original_qid_route_verified": False,
        "whole_name_domain_enumerated": False,
        "all_query_frontiers_closed": False,
        "native_p854_source_support_paid": False,
        "s29_persistence_paid": False, "edit_authority": False,
    }
    for key, expected in mandatory.items():
        if type(proof.get(key)) is not type(expected) or proof[key] != expected:
            raise ValueError(f"name chunk receipt disagrees with pinned original: {key}")
    a = proof.get("published_shard_raw_sha256")
    b = proof.get("original_packed_range_raw_sha256")
    if (type(a) is not str or not _SHA.fullmatch(a)
            or a != b or proof.get("published_shard_http_status") not in (200, 206)):
        raise ValueError("name chunk receipt has mismatched source/raw digest")


def audit_name_section(*, manifest_path: Path, original_index_path: Path,
                       dataset_revision: str, manifest_sha256: str,
                       section: str, receipts_dir: Path,
                       original_index_sha256: str | None = None,
                       max_chunk_mib: int = 128, max_transfer_mib: int = 512,
                       max_new_chunks: int = 4, execute: bool = False,
                       opener: Callable[..., Any] | None = None,
                       save_published_root: Path | None = None) -> dict:
    if (type(dataset_revision) is not str or not _REV.fullmatch(dataset_revision)
            or type(manifest_sha256) is not str
            or not _SHA.fullmatch(manifest_sha256)):
        raise ValueError("immutable original revision and manifest SHA required")
    if original_index_sha256 is not None and (
        type(original_index_sha256) is not str
        or not _SHA.fullmatch(original_index_sha256)
    ):
        raise ValueError("invalid original index SHA256")
    if section not in _NAMES:
        raise ValueError("only complete named sections may be audited")
    if (type(max_chunk_mib) is not int or not 1 <= max_chunk_mib <= 16384
            or type(max_transfer_mib) is not int or not 1 <= max_transfer_mib <= 262144
            or type(max_new_chunks) is not int or not 0 <= max_new_chunks <= 10000):
        raise ValueError("explicit bounded chunk/network budgets required")
    if receipts_dir.is_symlink():
        raise ValueError("name receipt directory symlink refused")
    if save_published_root is not None:
        if not isinstance(save_published_root, Path) or save_published_root.is_symlink():
            raise ValueError("native packed shard root symlink/invalid path refused")
        if save_published_root.exists() and not save_published_root.is_dir():
            raise ValueError("native packed shard root must be a directory")
        if (save_published_root.resolve() == receipts_dir.resolve()
                or save_published_root.resolve().is_relative_to(receipts_dir.resolve())
                or receipts_dir.resolve().is_relative_to(save_published_root.resolve())):
            raise ValueError("native source shard copies and physical receipts require separate roots")
    crosswalk = verify_index_manifest_files(
        manifest_path=manifest_path, index_path=original_index_path,
        manifest_sha256=manifest_sha256, index_sha256=original_index_sha256,
    )
    original_index_sha = crosswalk["original_index_raw_sha256_rechecked"]
    bin_size = crosswalk["original_bin_size_bytes"]
    chunks = _manifest_index(
        _read_json(manifest_path, 16 * 1024 * 1024), _ARTIFACT
    )
    ordered = sorted((n, row) for (s, n), row in chunks.items() if s == section)
    if (not ordered or [n for n, _ in ordered] != list(range(len(ordered)))
            or crosswalk["section_chunk_counts"][section + "ChunkCount"] != len(ordered)):
        raise ValueError("name section geometry not complete")
    retained, missing = [], []
    for n, row in ordered:
        path = receipts_dir / f"{section}-{n:06d}.json"
        if path.is_symlink():
            raise ValueError("symlinked name receipt rejected")
        if path.exists():
            proof = _read_receipt(path)
            if dest is not None and proof.get("saved_original_equal_published_copy") != str(dest):
                raise ValueError("native shard copy missing from exact source-byte receipt")
            _check_receipt(
                proof, row=row, number=n, section=section, rev=dataset_revision,
                manifest_sha=manifest_sha256, index_sha=original_index_sha,
                bin_size=bin_size,
            )
            retained.append((n, row, path, sha256(path.read_bytes()).hexdigest()))
        else:
            missing.append((n, row, path))
    transfer_bytes = 0
    scheduled, deferred = [], []
    for n, row, path in missing:
        two_source_bytes = row["length"] * 2
        if (len(scheduled) >= max_new_chunks
                or row["length"] > max_chunk_mib * 1024**2
                or transfer_bytes + two_source_bytes > max_transfer_mib * 1024**2):
            deferred.append(n)
        else:
            scheduled.append((n, row, path))
            transfer_bytes += two_source_bytes
    if execute and scheduled:
        if receipts_dir.exists() and not receipts_dir.is_dir():
            raise ValueError("receipt destination must be directory")
        receipts_dir.mkdir(parents=True, exist_ok=True)
        if save_published_root is not None:
            save_published_root.mkdir(parents=True, exist_ok=True)
        # Refuse preexisting targets before any fetch in this batch.
        for n, row, path in scheduled:
            if save_published_root is not None:
                dest = save_published_root / row["relative"]
                if (dest.exists() or dest.is_symlink()
                        or not dest.resolve().is_relative_to(save_published_root.resolve())):
                    raise ValueError("refuse overwrite or escape of locally retained original-equal shard")
        for n, row, path in scheduled:
            dest = None
            if save_published_root is not None:
                dest = save_published_root / row["relative"]
                dest.parent.mkdir(parents=True, exist_ok=True)
                if dest.parent.is_symlink():
                    raise ValueError("symlinked native shard parent refused")
            proof = verify_direct_original_chunk(
                manifest_path=manifest_path, original_index_path=original_index_path,
                dataset_revision=dataset_revision, manifest_sha256=manifest_sha256,
                original_index_sha256=original_index_sha, section=section,
                chunk_index=n, max_chunk_mib=max_chunk_mib, opener=opener,
                **({"save_published_copy": dest} if dest is not None else {}),
            )
            _check_receipt(
                proof, row=row, number=n, section=section, rev=dataset_revision,
                manifest_sha=manifest_sha256, index_sha=original_index_sha,
                bin_size=bin_size,
            )
            with path.open("x", encoding="utf-8") as output:
                json.dump(proof, output, indent=2, sort_keys=True)
                output.write("\n")
            retained.append((n, row, path, sha256(path.read_bytes()).hexdigest()))
    covered = sorted(n for n, _, _, _ in retained)
    complete = len(covered) == len(ordered)
    return {
        "version": "itir.zelph.name_section_original_byte_audit.v1",
        "dataset_revision": dataset_revision, "section": section,
        "manifest_raw_sha256": manifest_sha256,
        "original_index_raw_sha256": original_index_sha,
        "original_bin_size_bytes": bin_size,
        "source_section_chunk_count": len(ordered),
        "source_section_chunk_bytes": sum(row["length"] for _, row in ordered),
        "verified_chunk_indices": covered, "verified_chunk_count": len(covered),
        "receipt_hashes": [{
            "chunk_index": n, "receipt_path": str(path),
            "receipt_raw_sha256": digest,
        } for n, row, path, digest in sorted(retained)],
        "new_chunk_indices": [n for n, _, _ in scheduled] if execute else [],
        "planned_chunk_indices": [n for n, _, _ in scheduled],
        "deferred_chunk_indices": deferred,
        "planned_transfer_bytes": transfer_bytes,
        "network_executed": execute and bool(scheduled),
        "saved_native_shard_root": (
            str(save_published_root) if save_published_root is not None else None
        ),
        "new_original_equal_shard_copy_indices": (
            [n for n, _, _ in scheduled] if execute and save_published_root is not None else []
        ),
        "all_name_section_packed_payload_bytes_verified": complete,
        "all_native_name_rows_decoded": False,
        "collision_preserving_name_fibres_verified": False,
        "full_A1_name_domain_theorem_instantiated": False,
        "original_qid_route_verified": False,
        "native_p854_source_support_paid": False,
        "edit_authority": False,
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--original-index", type=Path, required=True)
    p.add_argument("--dataset-revision", required=True)
    p.add_argument("--manifest-sha256", required=True)
    p.add_argument("--original-index-sha256")
    p.add_argument("--section", choices=_NAMES, required=True)
    p.add_argument("--receipts-dir", type=Path, required=True)
    p.add_argument("--max-chunk-mib", type=int, default=128)
    p.add_argument("--max-transfer-mib", type=int, default=512)
    p.add_argument("--max-new-chunks", type=int, default=4)
    p.add_argument("--save-published-root", type=Path,
                   help="reuse exact byte comparison transfer to retain immutable packed shards for native row decoding")
    p.add_argument("--execute", action="store_true")
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    try:
        result = audit_name_section(
            manifest_path=args.manifest, original_index_path=args.original_index,
            dataset_revision=args.dataset_revision, manifest_sha256=args.manifest_sha256,
            original_index_sha256=args.original_index_sha256,
            section=args.section, receipts_dir=args.receipts_dir,
            max_chunk_mib=args.max_chunk_mib, max_transfer_mib=args.max_transfer_mib,
            max_new_chunks=args.max_new_chunks, execute=args.execute,
            save_published_root=args.save_published_root,
        )
        rendered = json.dumps(result, sort_keys=True, indent=2) + "\n"
        if args.output:
            if args.output.exists() or args.output.is_symlink():
                raise ValueError("refuse overwrite existing original name audit summary")
            with args.output.open("x", encoding="utf-8") as stream:
                stream.write(rendered)
        else:
            print(rendered, end="")
        return 0
    except (ValueError, OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "blocked", "reason": str(exc),
                          "edit_authority": False}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
