#!/usr/bin/env python3
"""P0 structural full-original packed Cap'n Proto partition audit.

The published manifest must enumerate the entire source .bin after exactly
one packed header, with no gaps/overlaps/reordered sections, using section-
global dense chunk indices. This audits *offset geometry*, NOT bytes,
upstream provenance, native decoder soundness, name-key exhaustiveness
or Wikidata semantic evidence.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
from typing import Any, Mapping

from verify_zelph_bin_shard_exact import _ARTIFACT, _manifest_index, _read_json

_ORDER = ("left", "right", "nameOfNode", "nodeOfName")


def verify_original_packed_partition(*, manifest: Mapping[str, Any],
                                     route: Mapping[str, Any],
                                     actual_source_size: int | None = None) -> dict[str, Any]:
    """Use the producer's decoded original header, never guessed chunk starts."""
    index = _manifest_index(manifest, _ARTIFACT)
    header = route.get("source")
    source = manifest.get("source")
    if not isinstance(header, Mapping) or not isinstance(source, Mapping):
        raise ValueError("original-bin header and manifest source metadata required")
    length = header.get("headerLengthBytes")
    route_size = header.get("binSizeBytes")
    manifest_size = source.get("binSizeBytes")
    if (type(length) is not int or length <= 0 or
        type(route_size) is not int or route_size <= 0 or
        type(manifest_size) is not int or manifest_size <= 0):
        raise ValueError("original header length and both full-bin sizes must be positive integers")
    if route_size != manifest_size or length > route_size:
        raise ValueError("original full-bin sizes/header bounds differ")
    if actual_source_size is not None and (type(actual_source_size) is not int or
                                           actual_source_size != route_size):
        raise ValueError("local original binary size differs from published/source header")
    if route.get("routeVersion") != "zelph-filtered-route/v1":
        raise ValueError("expected source-bin filtered route")
    cursor = length
    sections: dict[str, dict[str, int]] = {}
    physical = set()
    for section in _ORDER:
        count_field = {
            "left": "leftChunkCount",
            "right": "rightChunkCount",
            "nameOfNode": "nameOfNodeChunkCount",
            "nodeOfName": "nodeOfNameChunkCount",
        }[section]
        section_keys = sorted((num for name, num in index if name == section))
        expected_count = header.get(count_field)
        if type(expected_count) is not int or expected_count != len(section_keys):
            raise ValueError(f"original header/manifest section count differs: {section}")
        section_start = cursor
        for idx in section_keys:
            row = index[(section, idx)]
            if row["offset"] != cursor:
                raise ValueError(
                    f"original packed offset discontinuity/overlap in {section}/{idx}: "
                    f"expected {cursor}, observed {row['offset']}"
                )
            cursor += row["length"]
            if cursor > route_size:
                raise ValueError(f"original packed section extends beyond full source: {section}/{idx}")
            physical.add((section, idx))
        sections[section] = {
            "start_offset": section_start,
            "end_offset_exclusive": cursor,
            "bytes": cursor - section_start,
            "chunk_count": len(section_keys),
        }
    if cursor != route_size:
        raise ValueError("original packed section cover leaves unaccounted final bytes")
    if physical != set(index):
        raise ValueError("original packed manifest sections do not exhaust chunk index")
    return {
        "version": "itir.zelph.original_bin_packed_partition.v1",
        "artifact_id": _ARTIFACT,
        "header_bytes": length,
        "original_bin_size_bytes": route_size,
        "ordered_sections": list(_ORDER),
        "sections": sections,
        "total_chunk_count": len(index),
        "total_packed_chunk_bytes": route_size - length,
        "manifest_offset_cover_gap_free": True,
        "manifest_offset_cover_nonoverlapping": True,
        "manifest_section_order_matches_original_bin_header": True,
        "actual_original_bin_size_compared": actual_source_size is not None,
        "all_original_source_bytes_rehashed": False,
        "physical_chunk_bytes_verified_here": False,
        "upstream_original_bin_authenticated": False,
        "complete_original_name_key_domain_verified": False,
        "whole_graph_query_family_closed": False,
        "source_support_paid": False,
        "edit_authority": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--route", type=Path, required=True)
    parser.add_argument("--expected-manifest-sha256", required=True)
    parser.add_argument("--source-bin", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        raw = args.manifest.read_bytes()
        if (not 0 < len(raw) <= 16 * 1024 * 1024 or
            len(args.expected_manifest_sha256) != 64 or
            sha256(raw).hexdigest() != args.expected_manifest_sha256):
            raise ValueError("original raw manifest SHA256 differs from expected digest")
        manifest = _read_json(args.manifest, 16 * 1024 * 1024)
        route = _read_json(args.route, 64 * 1024 * 1024)
        size = args.source_bin.stat().st_size if args.source_bin else None
        result = verify_original_packed_partition(
            manifest=manifest, route=route, actual_source_size=size
        )
        output = json.dumps(result, sort_keys=True, indent=2) + "\n"
        if args.output:
            if args.output.exists():
                raise ValueError("refusing overwrite of original packed partition receipt")
            args.output.write_text(output, encoding="utf-8")
        else:
            print(output, end="")
        return 0
    except (ValueError, OSError, TypeError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "blocked", "reason": str(exc),
                          "edit_authority": False}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
