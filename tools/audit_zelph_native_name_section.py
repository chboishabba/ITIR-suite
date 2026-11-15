#!/usr/bin/env python3
"""A1 conditional section-domain evidence join over original packed name shards.

Consume EVERY section chunk from the independently pinned original index:
1. original .bin HTTP206-vs-published raw-byte physical receipt,
2. locally compiled pinned upstream Capnp native complete-name-row receipt,
3. saved full NDJSON row stream with exact sequence + terminal EOF marker.

All 204 original name chunks may be audited incrementally. This local join
uses streaming reads, preserves duplicate name/node fibre values for chosen
QIDs, and marks complete only when the entire source section has both kinds
of evidence. It does not assert source authorship, graph routing, uniqueness,
general Wikibase semantics, Agda theorem instantiation or edit authority.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import sys
from typing import Any

from audit_zelph_hf_name_section_bytes import _check_receipt, _read_receipt
from audit_zelph_native_name_rows import _hash_file, _json_object, _ROW, _END, _VERSION
from verify_zelph_bin_shard_exact import _ARTIFACT, _manifest_index, _read_json
from verify_zelph_index_manifest_original import verify_index_manifest_files

_SHA = re.compile(r"[0-9a-f]{64}\Z")
_REV = re.compile(r"[0-9a-f]{40}\Z")
_QID = re.compile(r"Q[1-9][0-9]*\Z")


def _native_receipt(path: Path) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file() or not 0 < path.stat().st_size <= 65536:
        raise ValueError("native original name receipt invalid or oversized")
    data = _json_object(path.read_bytes())
    return data


def _scan_rows(*, rows_file: Path, source_section: str, chunk_index: int,
               expected_rows: int, target_names: dict[str, list[int]],
               max_line_bytes: int, max_target_hits: int) -> int:
    count = 0
    end_seen = False
    with rows_file.open("rb") as data:
        while True:
            line = data.readline(max_line_bytes + 1)
            if not line:
                break
            if len(line) > max_line_bytes or not line.endswith(b"\n"):
                raise ValueError("native original complete name rows truncated/oversized")
            frame = _json_object(line)
            if frame.get("version") == _END:
                if end_seen or data.read(1):
                    raise ValueError("native name-row terminal footer not final")
                if frame != {
                    "version": _END, "section": source_section,
                    "chunk_index": chunk_index, "language": "wikidata",
                    "rows_emitted": count, "candidate_only": True,
                    "authority": False,
                }:
                    raise ValueError("native original row terminal count/identity mismatch")
                end_seen = True
                break
            if (set(frame) != {"version", "section", "chunk_index", "language",
                               "row_index", "name", "node_id"}
                    or frame.get("version") != _ROW
                    or frame.get("section") != source_section
                    or frame.get("chunk_index") != chunk_index
                    or frame.get("language") != "wikidata"
                    or type(frame.get("row_index")) is not int
                    or frame["row_index"] != count
                    or type(frame.get("name")) is not str
                    or type(frame.get("node_id")) is not int
                    or not 0 <= frame["node_id"] <= 2**64 - 1):
                raise ValueError("native original row stream schema/order mismatch")
            if frame["name"] in target_names:
                if sum(map(len, target_names.values())) >= max_target_hits:
                    raise ValueError("bounded complete target name fibre cap exceeded")
                target_names[frame["name"]].append(frame["node_id"])
            count += 1
            if count > expected_rows:
                raise ValueError("native original row count exceeds exact receipt")
    if not end_seen or count != expected_rows:
        raise ValueError("native original name row file lacks complete expected footer")
    return count


def audit_original_name_section_domain(
    *, manifest_path: Path, original_index_path: Path,
    dataset_revision: str, manifest_sha256: str, original_index_sha256: str,
    decoder_sha256: str, section: str,
    physical_receipts_dir: Path, native_receipts_dir: Path,
    target_qids: tuple[str, ...] = (),
    max_line_bytes: int = 65536, max_target_hits: int = 100000,
    require_complete: bool = False,
) -> dict[str, Any]:
    if (type(dataset_revision) is not str or not _REV.fullmatch(dataset_revision)
            or any(type(x) is not str or not _SHA.fullmatch(x)
                   for x in (manifest_sha256, original_index_sha256, decoder_sha256))):
        raise ValueError("original revision, manifest/index and native decoder pins required")
    if section not in ("nodeOfName", "nameOfNode"):
        raise ValueError("name section only")
    if (type(max_line_bytes) is not int or not 1 <= max_line_bytes <= 1048576
            or type(max_target_hits) is not int or not 0 <= max_target_hits <= 10000000
            or type(require_complete) is not bool):
        raise ValueError("invalid bounded native fibre audit controls")
    if (type(target_qids) is not tuple or len(set(target_qids)) != len(target_qids)
            or len(target_qids) > 10000
            or any(type(q) is not str or not _QID.fullmatch(q)
                   for q in target_qids)):
        raise ValueError("unique exact QID target names required")
    for root in (physical_receipts_dir, native_receipts_dir):
        if root.is_symlink() or not root.is_dir():
            raise ValueError("real existing original name receipt directories required")
    cross = verify_index_manifest_files(
        manifest_path=manifest_path, index_path=original_index_path,
        manifest_sha256=manifest_sha256, index_sha256=original_index_sha256,
    )
    idx = _manifest_index(_read_json(manifest_path, 16 * 1024 * 1024), _ARTIFACT)
    chunks = sorted((n, row) for (s, n), row in idx.items() if s == section)
    if (not chunks or [n for n, _ in chunks] != list(range(len(chunks)))
            or cross["section_chunk_counts"][section + "ChunkCount"] != len(chunks)
            or any(row["language"] != "wikidata" for _, row in chunks)):
        raise ValueError("entire original native name-section geometry/language invalid")
    target_fibres = {q: [] for q in target_qids}
    physical_verified = []
    native_verified = []
    missing_physical = []
    missing_native = []
    native_row_count = 0
    detailed = []
    for n, row in chunks:
        physical_path = physical_receipts_dir / f"{section}-{n:06d}.json"
        native_path = native_receipts_dir / f"{section}-{n:06d}.native.json"
        rows_path = native_receipts_dir / f"{section}-{n:06d}.native.ndjson"
        if (physical_path.is_symlink() or native_path.is_symlink()
                or rows_path.is_symlink()):
            raise ValueError("symlinked source/native name receipt refused")
        if not physical_path.is_file():
            missing_physical.append(n)
            if native_path.exists() or rows_path.exists():
                raise ValueError("orphan native row evidence has no original source-byte receipt")
            continue
        proof = _read_receipt(physical_path)
        _check_receipt(
            proof, row=row, number=n, section=section,
            rev=dataset_revision, manifest_sha=manifest_sha256,
            index_sha=original_index_sha256,
            bin_size=cross["original_bin_size_bytes"],
        )
        physical_verified.append(n)
        if not native_path.exists() and not rows_path.exists():
            missing_native.append(n)
            continue
        if not native_path.is_file() or not rows_path.is_file():
            raise ValueError("native original name row receipt/stream pair incomplete")
        native = _native_receipt(native_path)
        required = {
            "version": _VERSION,
            "dataset_revision": dataset_revision,
            "section": section, "chunk_index": n, "language": "wikidata",
            "manifest_raw_sha256": manifest_sha256,
            "original_index_raw_sha256": original_index_sha256,
            "physical_original_name_chunk_receipt_sha256": _hash_file(physical_path),
            "original_packed_chunk_raw_sha256": proof["original_packed_range_raw_sha256"],
            "native_decoder_executable_sha256": decoder_sha256,
            "complete_native_row_stream_for_this_chunk": True,
            "name_duplicates_discarded": False,
            "all_original_name_chunks_verified": False,
            "full_name_domain_A1_instantiated": False,
            "global_name_absence_proved": False,
            "edit_authority": False,
            "native_name_rows_file": str(rows_path),
        }
        for label, expected in required.items():
            if type(native.get(label)) is not type(expected) or native[label] != expected:
                raise ValueError(f"native original name receipt mismatched identity: {label}")
        count = native.get("native_packed_chunk_rows_enumerated")
        bytes_out = native.get("native_stdout_bytes")
        row_sha = native.get("native_name_rows_stdout_sha256")
        if (type(count) is not int or count < 0
                or type(bytes_out) is not int or bytes_out <= 0
                or type(row_sha) is not str or not _SHA.fullmatch(row_sha)
                or rows_path.stat().st_size != bytes_out
                or _hash_file(rows_path) != row_sha):
            raise ValueError("native original name rows file changed from complete receipt")
        actual = _scan_rows(
            rows_file=rows_path, source_section=section, chunk_index=n,
            expected_rows=count, target_names=target_fibres,
            max_line_bytes=max_line_bytes, max_target_hits=max_target_hits,
        )
        native_row_count += actual
        native_verified.append(n)
        detailed.append({
            "chunk_index": n,
            "packed_chunk_sha256": proof["published_shard_raw_sha256"],
            "physical_receipt_sha256": _hash_file(physical_path),
            "native_row_receipt_sha256": _hash_file(native_path),
            "native_rows_file_sha256": row_sha,
            "native_row_count": actual,
        })
    complete = (len(physical_verified) == len(chunks)
                and len(native_verified) == len(chunks))
    if require_complete and not complete:
        raise ValueError("original native name section incomplete: missing physical/native chunks")
    return {
        "version": "itir.zelph.native_original_name_section_domain.v1",
        "section": section, "dataset_revision": dataset_revision,
        "manifest_sha256": manifest_sha256,
        "original_index_sha256": original_index_sha256,
        "native_decoder_sha256": decoder_sha256,
        "source_original_name_chunk_count": len(chunks),
        "source_original_name_packed_bytes": sum(row["length"] for _, row in chunks),
        "verified_physical_chunks": physical_verified,
        "verified_native_name_row_chunks": native_verified,
        "missing_physical_chunk_indices": missing_physical,
        "missing_native_row_chunk_indices": missing_native,
        "native_rows_verified": native_row_count,
        "source_original_native_row_receipts": detailed,
        "target_name_fibres_preserving_repeated_values": target_fibres,
        "target_name_scope_is_full_original_name_section": complete,
        "original_packed_byte_and_native_row_section_cover": complete,
        "decoder_adequacy_formal_theorem_instantiated": False,
        "global_name_fibre_A1_proved": False,
        "all_wikibase_entities_or_statements_verified": False,
        "original_qid_adjacency_routes_proved": False,
        "edit_authority": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--original-index", type=Path, required=True)
    parser.add_argument("--dataset-revision", required=True)
    parser.add_argument("--manifest-sha256", required=True)
    parser.add_argument("--original-index-sha256", required=True)
    parser.add_argument("--decoder-sha256", required=True)
    parser.add_argument("--section", choices=("nodeOfName", "nameOfNode"), required=True)
    parser.add_argument("--physical-receipts-dir", type=Path, required=True)
    parser.add_argument("--native-receipts-dir", type=Path, required=True)
    parser.add_argument("--qid", action="append", default=[])
    parser.add_argument("--require-complete", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        if args.output is not None and (args.output.exists() or args.output.is_symlink()):
            raise ValueError("refuse overwrite original native section join receipt")
        proof = audit_original_name_section_domain(
            manifest_path=args.manifest, original_index_path=args.original_index,
            dataset_revision=args.dataset_revision,
            manifest_sha256=args.manifest_sha256,
            original_index_sha256=args.original_index_sha256,
            decoder_sha256=args.decoder_sha256, section=args.section,
            physical_receipts_dir=args.physical_receipts_dir,
            native_receipts_dir=args.native_receipts_dir,
            target_qids=tuple(args.qid), require_complete=args.require_complete,
        )
        rendered = json.dumps(proof, sort_keys=True, indent=2) + "\n"
        if args.output is None:
            print(rendered, end="")
        else:
            with args.output.open("x", encoding="utf-8") as stream:
                stream.write(rendered)
        return 0
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "blocked", "reason": str(exc),
                          "edit_authority": False}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
