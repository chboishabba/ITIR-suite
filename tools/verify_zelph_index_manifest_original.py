#!/usr/bin/env python3
"""Compare the ORIGINAL Zelph byte-offset index with its HF-v2 manifest.

Only immutable metadata/offset geometry is checked here. Original source
header and actual shard bytes require independent remote-byte verification.
Never promote index-file local paths, names or self-reported hashes to trust.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
from typing import Any, Mapping

from verify_zelph_bin_shard_exact import _ARTIFACT, _manifest_index, _read_json, _SHA64
from audit_zelph_original_packed_partition import verify_original_packed_partition

_SECTIONS = ("left", "right", "nameOfNode", "nodeOfName")
_COUNTS = {
    "left": "leftChunkCount",
    "right": "rightChunkCount",
    "nameOfNode": "nameOfNodeChunkCount",
    "nodeOfName": "nodeOfNameChunkCount",
}


def crosscheck_original_index(*, manifest: Mapping[str, Any],
                              original_index: Mapping[str, Any]) -> dict[str, Any]:
    """Exhaustively compare all original header and section-global chunk offsets."""
    original_header = original_index.get("header")
    source = manifest.get("source")
    if not isinstance(original_header, Mapping) or not isinstance(source, Mapping):
        raise ValueError("published offset index header and manifest source required")
    if type(original_header.get("offset")) is not int or original_header["offset"] != 0:
        raise ValueError("original offset index header must begin at byte zero")
    if type(original_header.get("length")) is not int:
        raise ValueError("original offset index header length must be integer")
    header_length = original_header["length"]
    if header_length <= 0 or source.get("headerLengthBytes") != header_length:
        raise ValueError("published manifest/index original header lengths differ")
    manifest_index = _manifest_index(manifest, _ARTIFACT)
    section_counts: dict[str, int] = {}
    for section in _SECTIONS:
        records = original_index.get(section)
        if type(records) is not list:
            raise ValueError("original offset index lacks one required section")
        section_counts[_COUNTS[section]] = len(records)
        expected = [
            manifest_index[(section, number)]
            for number in range(len(records))
            if (section, number) in manifest_index
        ]
        if len(expected) != len(records):
            raise ValueError("original offset index and manifest chunk counts differ")
        for position, (row, physical) in enumerate(zip(records, expected)):
            if type(row) is not dict:
                raise ValueError("original source index chunk must be object")
            if (type(row.get("chunkIndex")) is not int or row["chunkIndex"] != position
                    or type(row.get("offset")) is not int or row["offset"] != physical["offset"]
                    or type(row.get("length")) is not int or row["length"] != physical["length"]):
                raise ValueError(f"original index/manifest byte offset identity mismatch: {section}/{position}")
            if section in ("left", "right"):
                if row.get("which") != section:
                    raise ValueError("original offset index adjacency direction differs")
            elif row.get("lang") != physical["language"]:
                raise ValueError("original offset index name language differs")
    route_header = {
        "routeVersion": "zelph-filtered-route/v1",
        "source": {
            "headerLengthBytes": header_length,
            "binSizeBytes": source.get("binSizeBytes"),
            **section_counts,
        },
    }
    partition = verify_original_packed_partition(
        manifest=manifest, route=route_header,
    )
    return {
        "version": "itir.zelph.index_manifest_full_original_crosswalk.v1",
        "artifact_id": _ARTIFACT,
        "original_header_length_bytes": header_length,
        "original_bin_size_bytes": partition["original_bin_size_bytes"],
        "section_chunk_counts": section_counts,
        "all_manifest_chunk_offsets_equal_original_index": True,
        "entire_index_partition_gap_free": partition["manifest_offset_cover_gap_free"],
        "entire_index_partition_nonoverlapping": partition["manifest_offset_cover_nonoverlapping"],
        "section_global_indices_and_language_equal": True,
        "original_bin_header_raw_bytes_fetched": False,
        "original_source_upstream_authenticity_proved": False,
        "all_chunk_payload_bytes_checked": False,
        "entire_name_domain_byte_checked": False,
        "native_wikidata_source_support_paid": False,
        "edit_authority": False,
    }


def verify_index_manifest_files(*, manifest_path: Path, index_path: Path,
                                manifest_sha256: str, index_sha256: str | None = None) -> dict[str, Any]:
    if not _SHA64.fullmatch(manifest_sha256):
        raise ValueError("pinned raw full manifest SHA256 required")
    if index_sha256 is not None and not _SHA64.fullmatch(index_sha256):
        raise ValueError("expected original offset index SHA256 must be lowercase hex")
    for path in (manifest_path, index_path):
        if not path.is_file() or not 0 < path.stat().st_size <= 16 * 1024 * 1024:
            raise ValueError("missing or oversized original manifest/index JSON file")
    raw_manifest, raw_index = manifest_path.read_bytes(), index_path.read_bytes()
    if sha256(raw_manifest).hexdigest() != manifest_sha256:
        raise ValueError("raw pinned manifest digest mismatch")
    index_digest = sha256(raw_index).hexdigest()
    if index_sha256 is not None and index_digest != index_sha256:
        raise ValueError("original raw offset index digest mismatch")
    result = crosscheck_original_index(
        manifest=_read_json(manifest_path, 16 * 1024 * 1024),
        original_index=_read_json(index_path, 16 * 1024 * 1024),
    )
    result.update({
        "manifest_raw_sha256_rechecked": manifest_sha256,
        "original_index_raw_sha256_rechecked": index_digest,
        "original_index_expected_digest_independently_supplied": index_sha256 is not None,
        "original_index_published_revision_authenticated_here": False,
    })
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--original-index", type=Path, required=True)
    parser.add_argument("--manifest-sha256", required=True)
    parser.add_argument("--original-index-sha256")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        result = verify_index_manifest_files(
            manifest_path=args.manifest, index_path=args.original_index,
            manifest_sha256=args.manifest_sha256,
            index_sha256=args.original_index_sha256,
        )
        raw = json.dumps(result, indent=2, sort_keys=True) + "\n"
        if args.output:
            if args.output.exists():
                raise ValueError("refuse overwrite existing index crosswalk evidence")
            args.output.write_text(raw, encoding="utf-8")
        else:
            print(raw, end="")
        return 0
    except (ValueError, OSError, TypeError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "blocked", "reason": str(exc), "edit_authority": False}),
              file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
