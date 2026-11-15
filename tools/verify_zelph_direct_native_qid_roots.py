#!/usr/bin/env python3
"""P1 positive QID -> native internal node witnesses, sourced from P0-S equality.

Requires a COMPLETE direct selected-chunk matrix receipt and its individual
original-range/published-object equality files, local exact shard bytes,
and actual upstream-schema C++ Cap'n Proto selected decoder. QID/chunk
assignments are operator-declared candidates: only exact native positive
decoded rows are accepted. No original global name absence or adjacency
chunk route is inferred from an unobserved QID/chunk.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any, Callable

from verify_zelph_bin_shard_exact import _ARTIFACT, _manifest_index, _read_json

_QID = re.compile(r"(Q[1-9][0-9]*):([0-9]+)\Z")
_REV = re.compile(r"[0-9a-f]{40}\Z")
_SHA = re.compile(r"[0-9a-f]{64}\Z")
_SOURCE = "itir.zelph.direct_selected_matrix_receipt.v1"
_NATIVE = "itir.zelph.selected_native_capnp_decode.v1"


def parse_qid_selections(tokens: list[str]) -> dict[str, int]:
    if not isinstance(tokens, list) or not 0 < len(tokens) <= 10000:
        raise ValueError("1..10000 explicit QID:nodeOfNameChunk selections required")
    rows = {}
    for token in tokens:
        matched = _QID.fullmatch(token) if isinstance(token, str) else None
        if matched is None or int(matched[2]) > 2**32 - 1:
            raise ValueError("invalid exact QID:section-global-chunk hint")
        if matched[1] in rows:
            raise ValueError("duplicate QID original name selection")
        rows[matched[1]] = int(matched[2])
    return rows


def _hash_path(path: Path, max_bytes: int | None = None) -> str:
    if not path.is_file() or path.is_symlink():
        raise ValueError("expected actual original source evidence file")
    if max_bytes is not None and not 0 < path.stat().st_size <= max_bytes:
        raise ValueError("original physical receipt exceeds size limit")
    digest = sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _strict_load(raw: bytes) -> dict:
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate decoded/native receipt key")
            result[key] = value
        return result
    result = json.loads(raw.decode("utf-8"), object_pairs_hook=unique,
                        parse_constant=lambda v: (_ for _ in ()).throw(
                            ValueError("invalid non-JSON native number")))
    if type(result) is not dict:
        raise ValueError("native selected proof must be JSON object")
    return result


def verify_native_qid_roots(
    *, manifest_path: Path, manifest_sha256: str, matrix_dir: Path,
    shard_root: Path, decoder: Path, qid_chunks: dict[str, int],
    decoder_timeout_seconds: int = 120,
    runner: Callable[..., Any] = subprocess.run,
) -> dict[str, Any]:
    if (type(manifest_sha256) is not str or not _SHA.fullmatch(manifest_sha256)
            or _hash_path(manifest_path, 16 * 1024 * 1024) != manifest_sha256):
        raise ValueError("external pinned original manifest digest required")
    if not matrix_dir.is_dir() or matrix_dir.is_symlink():
        raise ValueError("existing physical matrix evidence directory required")
    if not decoder.is_file() or decoder.is_symlink():
        raise ValueError("actual original-schema Capnp decoder binary required")
    if (type(decoder_timeout_seconds) is not int or
            not 0 < decoder_timeout_seconds <= 900):
        raise ValueError("positive bounded native decode timeout required")
    if not qid_chunks or any(
        type(qid) is not str or not re.fullmatch(r"Q[1-9][0-9]*", qid)
        or type(chunk) is not int or not 0 <= chunk <= 2**32 - 1
        for qid, chunk in qid_chunks.items()
    ):
        raise ValueError("explicit positive QID/native name-shard hints required")
    summary_path = matrix_dir / "selected-matrix-complete.json"
    summary = _strict_load(summary_path.read_bytes())
    if (summary.get("version") != _SOURCE
            or summary.get("manifest_sha256") != manifest_sha256
            or summary.get("all_explicitly_selected_chunks_byte_equal") is not True
            or summary.get("qid_routes_verified") is not False
            or summary.get("edit_authority") is not False):
        raise ValueError("exact original selected matrix full receipt required")
    rev = summary.get("dataset_revision")
    if type(rev) is not str or not _REV.fullmatch(rev):
        raise ValueError("matrix missing immutable original graph revision")
    raw_receipts = summary.get("selected_receipts")
    if (type(raw_receipts) is not list or not raw_receipts
            or len(raw_receipts) != summary.get("selected_chunk_count")):
        raise ValueError("incomplete selected original physical matrix receipts")
    matrix_names = {}
    for row in raw_receipts:
        if type(row) is not dict:
            raise ValueError("invalid original physical witness row")
        key = (row.get("section"), row.get("chunk_index"))
        if key in matrix_names:
            raise ValueError("duplicate physical selected source chunk")
        if (type(row.get("receipt_file")) is not str
                or row["receipt_file"] !=
                   f"{row['section']}-{row['chunk_index']:06d}.json"
                or type(row.get("receipt_sha256")) is not str
                or not _SHA.fullmatch(row["receipt_sha256"])):
            raise ValueError("invalid canonical original chunk receipt path")
        receipt_path = matrix_dir / row["receipt_file"]
        if _hash_path(receipt_path, 1024 * 1024) != row["receipt_sha256"]:
            raise ValueError("physical selected original chunk receipt SHA drift")
        receipt = _strict_load(receipt_path.read_bytes())
        if (receipt.get("version") != "itir.zelph.direct_original_selected_chunk_equality.v1"
                or receipt.get("dataset_revision") != rev
                or receipt.get("original_manifest_raw_sha256") != manifest_sha256
                or receipt.get("original_index_raw_sha256") != summary.get("original_index_sha256")
                or receipt.get("section") != row.get("section")
                or receipt.get("chunk_index") != row.get("chunk_index")
                or receipt.get("exact_original_packed_bytes_equal_published_shard") is not True
                or receipt.get("published_shard_raw_sha256") != row.get("sha256")
                or receipt.get("original_packed_range_raw_sha256") != row.get("sha256")
                or receipt.get("original_source_http_status") != 206
                or receipt.get("edit_authority") is not False):
            raise ValueError("physical original source chunk proof changed")
        matrix_names[key] = receipt
    manifest = _read_json(manifest_path, 16 * 1024 * 1024)
    manifest_index = _manifest_index(manifest, _ARTIFACT)
    root = shard_root.resolve(strict=True)
    if not root.is_dir() or shard_root.is_symlink():
        raise ValueError("bounded selected native shard root required")
    decoder_sha = _hash_path(decoder)
    rows = []
    for qid, chunk in sorted(qid_chunks.items()):
        key = ("nodeOfName", chunk)
        if key not in matrix_names or key not in manifest_index:
            raise ValueError("QID source-name chunk lacks exact direct HTTP206 equality witness")
        item, receipt = manifest_index[key], matrix_names[key]
        if item["language"] != "wikidata":
            raise ValueError("QID name root requires original wikidata language chunk")
        if (receipt["bytes_compared"] != item["length"]
                or receipt["original_source_offset"] != item["offset"]
                or receipt["published_object_uri"] != item["object_uri"]):
            raise ValueError("native source chunk offset/length/path mismatches physical proof")
        shard = (root / item["relative"]).resolve(strict=True)
        if not shard.is_relative_to(root) or _hash_path(shard) != receipt["published_shard_raw_sha256"]:
            raise ValueError("actual native packed shard differs from original physical HTTP206 witness")
        cmd = [str(decoder), "--file", str(shard),
               "--section", "nodeOfName", "--chunk-index", str(chunk),
               "--lang", "wikidata", "--qid", qid]
        process = runner(cmd, capture_output=True, timeout=decoder_timeout_seconds, check=False)
        if (process.returncode != 0 or type(process.stdout) is not bytes
                or len(process.stdout) > 2 * 1024 * 1024):
            raise ValueError("original-schema native QID lookup failed/overflowed")
        decoded = _strict_load(process.stdout)
        candidates = decoded.get("rows")
        if (decoded.get("version") != _NATIVE or decoded.get("section") != "nodeOfName"
                or decoded.get("chunk_index") != chunk
                or decoded.get("candidate_only") is not True
                or decoded.get("authority") is not False
                or type(candidates) is not list or len(candidates) != 1
                or type(candidates[0]) is not dict
                or candidates[0].get("name") != qid
                or type(candidates[0].get("node_id")) is not int
                or not 0 <= candidates[0]["node_id"] <= 2**64 - 1):
            raise ValueError("QID name row missing/ambiguous or not exact original native source")
        rows.append({
            "qid": qid, "node_id": candidates[0]["node_id"],
            "node_of_name_section_global_chunk": chunk,
            "packed_bytes_sha256_equal_original_range": receipt["published_shard_raw_sha256"],
            "native_decoder_output_sha256": sha256(process.stdout).hexdigest(),
            "source_offset": receipt["original_source_offset"],
            "physical_receipt_sha256": raw_receipts[
                next(i for i, row in enumerate(raw_receipts)
                     if row.get("section") == "nodeOfName"
                     and row.get("chunk_index") == chunk)
            ]["receipt_sha256"],
        })
    return {
        "version": "itir.zelph.original_direct_native_positive_qid_roots.v1",
        "dataset_revision": rev,
        "manifest_sha256": manifest_sha256,
        "original_index_sha256": summary["original_index_sha256"],
        "physical_complete_matrix_receipt_sha256": _hash_path(summary_path, 16 * 1024 * 1024),
        "native_decoder_binary_sha256": decoder_sha,
        "qid_count": len(rows),
        "native_exact_positive_name_to_node_rows": rows,
        "all_declared_qid_name_witnesses_positive": True,
        "original_name_chunk_bytes_equal_source_bin_ranges": True,
        "all_original_names_enumerated": False,
        "original_whole_bin_digest_verified": False,
        "selected_root_adjacency_verified": False,
        "left_right_finite_query_family_closed": False,
        "native_wikibase_p14143_p854_verified": False,
        "s29_review_persistence_paid": False,
        "source_support_paid": False, "edit_authority": False,
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--manifest-sha256", required=True)
    p.add_argument("--matrix-dir", type=Path, required=True)
    p.add_argument("--shard-root", type=Path, required=True)
    p.add_argument("--decoder", type=Path, required=True)
    p.add_argument("--qid-chunk", action="append", required=True,
                   help="Q123:section-global-nodeOfName-index, explicitly observed")
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    try:
        if args.output.exists() or args.output.is_symlink():
            raise ValueError("refuse overwrite of native positive QID witness")
        result = verify_native_qid_roots(
            manifest_path=args.manifest, manifest_sha256=args.manifest_sha256,
            matrix_dir=args.matrix_dir, shard_root=args.shard_root,
            decoder=args.decoder, qid_chunks=parse_qid_selections(args.qid_chunk))
        with args.output.open("x", encoding="utf-8") as output:
            json.dump(result, output, sort_keys=True, indent=2)
            output.write("\n")
        print(json.dumps(result, sort_keys=True, indent=2))
        return 0
    except (OSError, ValueError, TypeError, KeyError, OverflowError, json.JSONDecodeError,
            subprocess.TimeoutExpired) as exc:
        print(json.dumps({"status": "blocked", "reason": str(exc),
                          "edit_authority": False}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
