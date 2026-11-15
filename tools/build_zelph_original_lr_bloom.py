#!/usr/bin/env python3
"""A2-B: source-equal original adjacency chunk -> verified native membership Bloom.

The real original Cap'n Proto C++ decoder sees *every* AdjPair node key and,
after exact packed EOF, emits a compact deterministic binary filter. The
filter is tied to an immutable original HTTP206-vs-published equality receipt,
the exact saved packed shard SHA, and the compiled decoder SHA.

Bloom negatives are rigorous for *this completed, verified chunk* under the
same hash algorithm. Positives are candidate routing hints, NEVER proof that
the node exists; exact native selected-node replay is still required.
Incomplete original section coverage can NEVER be used as global absence.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import resource
import sqlite3
import struct
import subprocess
import sys
import tempfile
from typing import Any, Callable

from audit_zelph_native_original_lr_roots import native_original_lr_plan
from audit_zelph_native_name_fibres import _file_sha, _strict

MASK = (1 << 64) - 1
BIT_POW = 24
BITS = 1 << BIT_POW
BYTES = BITS // 8
HASHES = 7
MAGIC = b"ZLBLOOM1"
END = b"ZLBEND01"
WIRE_BYTES = 16 + BYTES + 16
_VERSION = "itir.zelph.original_source_equal_native_lr_bloom.v1"


def splitmix64(x: int) -> int:
    x = (x + 0x9e3779b97f4a7c15) & MASK
    x = ((x ^ (x >> 30)) * 0xbf58476d1ce4e5b9) & MASK
    x = ((x ^ (x >> 27)) * 0x94d049bb133111eb) & MASK
    return x ^ (x >> 31)


def bit_positions(node: int) -> tuple[int, ...]:
    if type(node) is not int or not 0 <= node <= MASK:
        raise ValueError("original numeric key must be uint64")
    h1 = splitmix64(node ^ 0x243f6a8885a308d3)
    h2 = splitmix64(node ^ 0x13198a2e03707344) | 1
    return tuple((h1 + i * h2) & (BITS - 1) for i in range(HASHES))


def bloom_possible(bitmap: bytes | memoryview, node: int) -> bool:
    if len(bitmap) != BYTES:
        raise ValueError("original Bloom size mismatch")
    return all((bitmap[bit >> 3] >> (bit & 7)) & 1 for bit in bit_positions(node))


def validate_wire(raw: bytes, *, section: str, chunk_index: int,
                  max_key_rows: int = 2000000) -> tuple[memoryview, int]:
    if (type(raw) is not bytes or len(raw) != WIRE_BYTES or
            raw[:8] != MAGIC or raw[16+BYTES:24+BYTES] != END):
        raise ValueError("native source original bloom missing exact ABI/footer")
    if section not in ("left", "right") or type(chunk_index) is not int:
        raise ValueError("original bloom direction/chunk invalid")
    packed_chunk = struct.unpack_from("<I", raw, 8)[0]
    if (packed_chunk != chunk_index or raw[12] != (0 if section == "left" else 1)
            or raw[13] != HASHES or raw[14] != BIT_POW or raw[15] != 0):
        raise ValueError("native original bloom chunk/direction/hash ABI mismatch")
    count = struct.unpack_from("<Q", raw, 24+BYTES)[0]
    if not 0 < count <= max_key_rows:
        raise ValueError("native original bloom row-count bound or zero-row ambiguity")
    return memoryview(raw)[16:16+BYTES], count


def create_test_wire(*, section: str, chunk_index: int,
                     nodes: list[int]) -> bytes:
    """Deterministic *test fixture* only; not a source/physical evidence oracle."""
    bitmap = bytearray(BYTES)
    for node in nodes:
        for bit in bit_positions(node):
            bitmap[bit >> 3] |= 1 << (bit & 7)
    head = MAGIC + struct.pack("<I", chunk_index) + bytes(
        [0 if section == "left" else 1, HASHES, BIT_POW, 0])
    return head + bytes(bitmap) + END + struct.pack("<Q", len(nodes))


def _native_binary(*, decoder: Path, entry: dict, max_key_rows: int,
                   timeout_seconds: int,
                   runner: Callable[..., Any] | None) -> bytes:
    cmd = [str(decoder), "--file", entry["saved_original_equal_packed_file"],
           "--section", entry["section"], "--chunk-index", str(entry["chunk_index"]),
           "--adjacency-bloom", "--max-key-rows", str(max_key_rows)]
    if runner is not None:
        proc = runner(cmd, capture_output=True, timeout=timeout_seconds, check=False)
        if proc.returncode != 0 or type(proc.stdout) is not bytes:
            raise ValueError("original-schema native bloom decoder failed")
        data = proc.stdout
    else:
        # OS-enforced output cap, NOT a post-hoc capture_output limit.
        def limit_file_size():
            resource.setrlimit(resource.RLIMIT_FSIZE, (WIRE_BYTES, WIRE_BYTES))
        with tempfile.TemporaryFile(mode="w+b") as stdout:
            proc = subprocess.run(cmd, stdout=stdout, stderr=subprocess.PIPE,
                                  timeout=timeout_seconds, check=False,
                                  preexec_fn=limit_file_size)
            if proc.returncode != 0:
                raise ValueError("original-schema native bloom decoder failed/overflowed")
            stdout.seek(0)
            data = stdout.read(WIRE_BYTES + 1)
    if len(data) != WIRE_BYTES:
        raise ValueError("native original bloom output truncated/oversized")
    return data


def _atomic_write(path: Path, data: bytes) -> None:
    if path.exists() or path.is_symlink() or path.parent.is_symlink():
        raise ValueError("native original bloom evidence cannot overwrite or escape")
    scratch = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, mode="wb",
                                         prefix=".original-adj-bloom-", delete=False) as out:
            scratch = Path(out.name)
            out.write(data)
            out.flush()
            os.fsync(out.fileno())
        os.link(scratch, path, follow_symlinks=False)
    finally:
        if scratch is not None:
            scratch.unlink(missing_ok=True)


def _paths(out_root: Path, section: str, chunk: int) -> tuple[Path, Path]:
    stem = f"{section}-{chunk:06d}"
    return out_root / (stem + ".zlbloom"), out_root / (stem + ".json")


def _receipt_identity(*, plan: dict, entry: dict, decoder_sha: str,
                      raw_sha: str, rows: int) -> dict:
    return {
        "version": _VERSION,
        "dataset_revision": plan["dataset_revision"],
        "manifest_sha256": plan["manifest_sha256"],
        "original_index_sha256": plan["original_index_sha256"],
        "positive_roots_receipt_sha256": plan["positive_roots_receipt_sha256"],
        "native_decoder_sha256": decoder_sha,
        "section": entry["section"], "chunk_index": entry["chunk_index"],
        "original_packed_source_offset": entry["original_source_offset"],
        "original_packed_size_bytes": entry["packed_size_bytes"],
        "physical_http206_receipt_sha256": entry["receipt_sha256"],
        "original_equal_packed_shard_sha256": entry["packed_sha256"],
        "native_bloom_wire_sha256": raw_sha,
        "native_adjacency_key_rows_seen": rows,
        "hash_bits_power": BIT_POW, "hash_count": HASHES,
        "native_original_packed_eof_checked_before_bloom_emission": True,
        "all_original_chunks_indexed": False,
        "a_bloom_positive_requires_original_native_row_replay": True,
        "source_support_paid": False, "edit_authority": False,
    }


def build_verified_lr_blooms(*, plan: dict, decoder: Path,
                             out_root: Path, max_new_chunks: int = 8,
                             max_key_rows: int = 2000000,
                             timeout_seconds: int = 900,
                             runner: Callable[..., Any] | None = None,
                             execute: bool = False) -> dict:
    if (plan.get("version") != "itir.zelph.original_lr_native_plan.v1"
            or type(max_new_chunks) is not int or not 0 <= max_new_chunks <= 4096
            or type(max_key_rows) is not int or not 0 < max_key_rows <= 100000000
            or type(timeout_seconds) is not int or not 0 < timeout_seconds <= 7200
            or not decoder.is_file() or decoder.is_symlink()):
        raise ValueError("pinned native original section/decoder and bounds required")
    if (out_root.is_symlink() or (out_root.exists() and not out_root.is_dir())
            or not out_root.parent.is_dir() or out_root.parent.is_symlink()):
        raise ValueError("original native bloom evidence directory must be real")
    decoder_sha = _file_sha(decoder)
    existing, scheduled, created = [], [], []
    for entry in plan["available_native_source_equal_chunks"]:
        section, n = entry["section"], entry["chunk_index"]
        bitmap_file, receipt_file = _paths(out_root, section, n)
        if bitmap_file.is_symlink() or receipt_file.is_symlink():
            raise ValueError("symlinked native original membership receipt")
        if bitmap_file.exists() or receipt_file.exists():
            if not bitmap_file.is_file() or not receipt_file.is_file():
                raise ValueError("partial source Bloom publication cannot be treated as complete")
            original = _strict(receipt_file.read_bytes())
            raw = bitmap_file.read_bytes()
            _, count = validate_wire(raw, section=section, chunk_index=n,
                                     max_key_rows=max_key_rows)
            expected = _receipt_identity(
                plan=plan, entry=entry, decoder_sha=decoder_sha,
                raw_sha=sha256(raw).hexdigest(), rows=count)
            if original != expected:
                raise ValueError("retained original native Bloom changed source/decoder/bitmap")
            existing.append((section, n))
        elif len(scheduled) < max_new_chunks:
            scheduled.append(entry)
    if execute and scheduled:
        out_root.mkdir(parents=True, exist_ok=True)
        for entry in scheduled:
            packed = Path(entry["saved_original_equal_packed_file"])
            receipt = Path(entry["receipt_file"])
            if (_file_sha(packed) != entry["packed_sha256"]
                    or _file_sha(receipt, 1024*1024) != entry["receipt_sha256"]):
                raise ValueError("original physical evidence drift before native Bloom build")
            raw = _native_binary(
                decoder=decoder, entry=entry,max_key_rows=max_key_rows,
                timeout_seconds=timeout_seconds, runner=runner)
            bitmap, count = validate_wire(
                raw, section=entry["section"], chunk_index=entry["chunk_index"],
                max_key_rows=max_key_rows)
            if count == 0:
                raise ValueError("unexpected empty original native adjacency shard")
            wire_sha = sha256(raw).hexdigest()
            bitmap_file, receipt_file = _paths(
                out_root, entry["section"], entry["chunk_index"])
            _atomic_write(bitmap_file, raw)
            proof = _receipt_identity(plan=plan, entry=entry,
                                      decoder_sha=decoder_sha, raw_sha=wire_sha,
                                      rows=count)
            _atomic_write(receipt_file, (json.dumps(proof, sort_keys=True,
                                                     indent=2)+"\n").encode())
            created.append((entry["section"], entry["chunk_index"]))
    return {
        "version": "itir.zelph.original_lr_bloom_build_batch.v1",
        "dataset_revision": plan["dataset_revision"],
        "manifest_sha256": plan["manifest_sha256"],
        "original_index_sha256": plan["original_index_sha256"],
        "native_decoder_sha256": decoder_sha,
        "source_original_section_chunk_counts": plan["original_full_section_chunk_counts"],
        "available_source_equal_shards": plan["available_native_chunk_count"],
        "previously_bloom_indexed_chunks": [
            {"section":sec, "chunk_index":n} for sec,n in existing],
        "planned_new_chunks": [
            {"section":x["section"],"chunk_index":x["chunk_index"]} for x in scheduled],
        "newly_bloom_indexed_chunks": [
            {"section":sec,"chunk_index":n} for sec,n in created],
        "each_bloom_wire_bytes": WIRE_BYTES,
        "all_original_source_chunk_blooms_complete": (
            len(existing)+len(created) == sum(
                plan["original_full_section_chunk_counts"].values())),
        "bloom_negative_is_exact_only_with_verified_original_chunk": True,
        "bloom_positive_is_not_an_adjacency_edge_or_route": True,
        "unobserved_original_chunks_are_unknown": True,
        "native_p854_source_support_paid": False,
        "s29_persistence_paid": False, "edit_authority": False,
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    for name in ("manifest","original-index","positive-roots-receipt",
                 "shard-root","decoder","bloom-root"):
        p.add_argument("--"+name,type=Path,required=True)
    p.add_argument("--dataset-revision",required=True)
    p.add_argument("--manifest-sha256",required=True)
    p.add_argument("--original-index-sha256",required=True)
    p.add_argument("--physical-receipts-dir",type=Path,action="append",required=True)
    p.add_argument("--max-new-chunks",type=int,default=8)
    p.add_argument("--max-key-rows",type=int,default=2000000)
    p.add_argument("--max-chunk-mib",type=int,default=256)
    p.add_argument("--timeout-seconds",type=int,default=900)
    p.add_argument("--execute",action="store_true")
    p.add_argument("--output",type=Path)
    args=p.parse_args()
    try:
        plan=native_original_lr_plan(
            manifest=args.manifest,original_index=args.original_index,
            revision=args.dataset_revision,
            manifest_sha256=args.manifest_sha256,
            original_index_sha256=args.original_index_sha256,
            physical_receipts_dirs=args.physical_receipts_dir,
            shard_root=args.shard_root,
            positive_roots_receipt=args.positive_roots_receipt,
            max_chunk_mib=args.max_chunk_mib)
        result=build_verified_lr_blooms(
            plan=plan,decoder=args.decoder,out_root=args.bloom_root,
            max_new_chunks=args.max_new_chunks,
            max_key_rows=args.max_key_rows,
            timeout_seconds=args.timeout_seconds,execute=args.execute)
        wire=json.dumps(result,sort_keys=True,indent=2)+"\n"
        if args.output:
            with args.output.open("x",encoding="utf-8") as out:
                out.write(wire)
        else:
            print(wire,end="")
        return 0
    except (OSError,ValueError,TypeError,KeyError,json.JSONDecodeError,
            subprocess.TimeoutExpired,sqlite3.DatabaseError) as exc:
        print(json.dumps({"status":"blocked","reason":str(exc),
                          "edit_authority":False}),file=sys.stderr)
        return 2


if __name__=="__main__":
    raise SystemExit(main())
