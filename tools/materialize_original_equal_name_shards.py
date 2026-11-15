#!/usr/bin/env python3
"""Restore actual packed native name shards from previously verified HTTP206 receipts.

A retained original-.bin HTTP206/shard equality receipt may predate optional
same-pass local shard saving. Re-fetch ONLY the pinned published complete
object, stream-hash it against the prior original-range SHA256, atomically
preserve the packed bytes, and retain the distinction:
  * new network check = published object equals previously receipted digest
  * prior physical receipt = published object == original .bin range
This does not recheck the original range or infer any missing QID absence.
Uses ITIR's existing shard_transport; no new network transport owner.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import sys
import tempfile
from typing import Any, Callable

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "itir-mcp" / "src"))
from itir_mcp.shard_transport import open_pinned_zelph_complete_object
from audit_zelph_hf_name_section_bytes import _read_receipt, _check_receipt
from verify_zelph_bin_shard_exact import _ARTIFACT, _manifest_index, _read_json
from verify_zelph_index_manifest_original import verify_index_manifest_files

_SHA = re.compile(r"[0-9a-f]{64}\Z")
_REV = re.compile(r"[0-9a-f]{40}\Z")
_MIB = 1024 * 1024
_NAMES = ("nodeOfName", "nameOfNode")


def _hash(path: Path, limit: int | None = None) -> str:
    if not path.is_file() or path.is_symlink():
        raise ValueError("missing actual original packed bytes or symlink")
    if limit is not None and not 0 < path.stat().st_size <= limit:
        raise ValueError("physical source evidence exceeds bound")
    h = sha256()
    with path.open("rb") as inp:
        for block in iter(lambda: inp.read(_MIB), b""):
            h.update(block)
    return h.hexdigest()


def materialization_plan(*, manifest: Path, original_index: Path,
                         revision: str, manifest_sha256: str,
                         original_index_sha256: str,
                         physical_receipts_dirs: list[Path], shard_root: Path,
                         max_new_chunks: int = 8, max_transfer_mib: int = 512,
                         max_chunk_mib: int = 256) -> dict:
    if (type(revision) is not str or not _REV.fullmatch(revision)
            or type(manifest_sha256) is not str or not _SHA.fullmatch(manifest_sha256)
            or type(original_index_sha256) is not str or not _SHA.fullmatch(original_index_sha256)
            or type(max_new_chunks) is not int or not 0 <= max_new_chunks <= 4096
            or type(max_transfer_mib) is not int or not 0 < max_transfer_mib <= 65536
            or type(max_chunk_mib) is not int or not 0 < max_chunk_mib <= 16384):
        raise ValueError("exact immutable revision and bounded transfer budgets required")
    if not physical_receipts_dirs or any(not d.is_dir() or d.is_symlink()
                                          for d in physical_receipts_dirs):
        raise ValueError("physical original HTTP206 evidence directories required")
    if shard_root.is_symlink():
        raise ValueError("saved native root may not be a symlink")
    if shard_root.exists() and not shard_root.is_dir():
        raise ValueError("saved native root is not directory")
    if (not shard_root.exists() and
            (not shard_root.parent.is_dir() or shard_root.parent.is_symlink())):
        raise ValueError("saved native root parent absent")
    base = shard_root.resolve(strict=False)
    cover = verify_index_manifest_files(
        manifest_path=manifest, index_path=original_index,
        manifest_sha256=manifest_sha256, index_sha256=original_index_sha256)
    objects = _manifest_index(_read_json(manifest, 16*_MIB), _ARTIFACT)
    known, retained, missing = [], [], []
    for (section, chunk), item in sorted(objects.items()):
        if section not in _NAMES:
            continue
        evidence = []
        for root in physical_receipts_dirs:
            p = root / f"{section}-{chunk:06d}.json"
            if p.is_symlink():
                raise ValueError("symlink physical original chunk receipt")
            if p.exists():
                proof = _read_receipt(p)
                _check_receipt(proof, row=item, number=chunk, section=section,
                               rev=revision, manifest_sha=manifest_sha256,
                               index_sha=original_index_sha256,
                               bin_size=cover["original_bin_size_bytes"])
                evidence.append((p, proof))
        if not evidence:
            continue
        first = evidence[0][1]
        if any(p["published_shard_raw_sha256"] != first["published_shard_raw_sha256"]
               for _, p in evidence[1:]):
            raise ValueError("conflicting physical original source-equality receipts")
        rel = item["relative"]
        destination = (shard_root / rel).resolve(strict=False)
        if not destination.is_relative_to(base) or destination.is_symlink():
            raise ValueError("unsafe original packed native saved path")
        row = {
            "section": section, "chunk_index": chunk,
            "published_object_uri": item["object_uri"],
            "physical_receipt_sha256": _hash(evidence[0][0], _MIB),
            "original_equal_sha256": first["published_shard_raw_sha256"],
            "length": item["length"], "destination": str(destination),
        }
        known.append(row)
        if destination.exists():
            if (not destination.is_file() or destination.stat().st_size != item["length"]
                    or _hash(destination) != row["original_equal_sha256"]):
                raise ValueError("existing saved native shard differs from exact original source")
            retained.append(row)
        else:
            missing.append(row)
    transfer = 0
    selected = []
    for row in missing:
        if len(selected) >= max_new_chunks or (
            row["length"] > max_chunk_mib * _MIB
            or transfer + row["length"] > max_transfer_mib * _MIB):
            continue
        selected.append(row)
        transfer += row["length"]
    return {
        "version": "itir.zelph.original_equal_name_shard_rematerialization_plan.v1",
        "dataset_revision": revision, "manifest_sha256": manifest_sha256,
        "original_index_sha256": original_index_sha256,
        "eligible_prior_original_byte_witnesses": len(known),
        "already_locally_verified_shards": len(retained),
        "missing_locally_saved_shards": len(missing),
        "selected_restore_chunks": selected,
        "selected_object_count": len(selected),
        "planned_one_sided_hf_bytes": transfer,
        "original_http206_reverified_in_this_step": False,
        "full_name_domain_enumerated": False,
        "source_support_paid": False, "edit_authority": False,
    }


def restore(*, plan: dict, opener: Callable[..., Any] | None = None) -> dict:
    if plan.get("version") != "itir.zelph.original_equal_name_shard_rematerialization_plan.v1":
        raise ValueError("invalid pinned restore plan")
    saved = []
    for row in plan["selected_restore_chunks"]:
        destination = Path(row["destination"])
        if destination.exists() or destination.is_symlink():
            raise ValueError("original equal shard destination already exists")
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.parent.is_symlink():
            raise ValueError("saved original packed shard parent symlink")
        temp = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="wb", dir=destination.parent,
                prefix=".original-native-hf-", delete=False,
            ) as out:
                temp = Path(out.name)
                remote_args = dict(
                    hf_uri=row["published_object_uri"],
                    revision=plan["dataset_revision"],
                    expected_size=row["length"], max_bytes=row["length"])
                if opener is not None:
                    remote_args["opener"] = opener
                with open_pinned_zelph_complete_object(**remote_args) as response:
                    count = 0
                    h = sha256()
                    while count < row["length"]:
                        block = response.read(min(_MIB, row["length"] - count))
                        if not block:
                            raise ValueError("published original name shard truncated")
                        out.write(block)
                        h.update(block)
                        count += len(block)
                    if response.read(1) or h.hexdigest() != row["original_equal_sha256"]:
                        raise ValueError("refetched native packed shard differs from original HTTP206 receipt")
                out.flush()
                os.fsync(out.fileno())
            os.link(temp, destination, follow_symlinks=False)
            saved.append({"section": row["section"], "chunk_index": row["chunk_index"],
                          "sha256": row["original_equal_sha256"],
                          "physical_receipt_sha256": row["physical_receipt_sha256"],
                          "saved_path": str(destination)})
        finally:
            if temp is not None:
                temp.unlink(missing_ok=True)
    return {**plan, "saved_new_chunks": saved,
            "all_selected_saved_shards_match_prior_original_http206_receipts": True,
            "revalidated_original_bin_remote_byte_ranges_in_this_step": False,
            "edit_authority": False}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--original-index", type=Path, required=True)
    p.add_argument("--dataset-revision", required=True)
    p.add_argument("--manifest-sha256", required=True)
    p.add_argument("--original-index-sha256", required=True)
    p.add_argument("--physical-receipts-dir", type=Path, action="append", required=True)
    p.add_argument("--save-published-root", type=Path, required=True)
    p.add_argument("--max-new-chunks", type=int, default=8)
    p.add_argument("--max-transfer-mib", type=int, default=512)
    p.add_argument("--max-chunk-mib", type=int, default=256)
    p.add_argument("--execute", action="store_true")
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    try:
        plan = materialization_plan(
            manifest=args.manifest, original_index=args.original_index,
            revision=args.dataset_revision, manifest_sha256=args.manifest_sha256,
            original_index_sha256=args.original_index_sha256,
            physical_receipts_dirs=args.physical_receipts_dir,
            shard_root=args.save_published_root,
            max_new_chunks=args.max_new_chunks,
            max_transfer_mib=args.max_transfer_mib,
            max_chunk_mib=args.max_chunk_mib)
        result = restore(plan=plan) if args.execute else plan
        rendered = json.dumps(result, sort_keys=True, indent=2) + "\n"
        if args.output:
            with args.output.open("x", encoding="utf-8") as out:
                out.write(rendered)
        else:
            print(rendered, end="")
        return 0
    except (OSError, ValueError, KeyError, TypeError, OverflowError,
            json.JSONDecodeError) as exc:
        print(json.dumps({"status": "blocked", "reason": str(exc),
                          "edit_authority": False}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
