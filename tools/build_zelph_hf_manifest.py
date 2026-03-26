#!/usr/bin/env python3
"""Build a Hugging Face storage/query manifest for a Zelph .bin artifact.

This converts the local artifact pair:
  1) <graph>.bin
  2) <graph>.index.json

into either:
  - `zelph-hf-layout/v1`: monolithic bin + sidecar index
  - `zelph-hf-layout/v2`: multi-object shard layout
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SECTION_NAMES = ("left", "right", "nameOfNode", "nodeOfName")
SUPPORTED_LAYOUTS = ("v1", "v2")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a Zelph HF layout manifest from a .bin and sidecar index.")
    parser.add_argument("--bin", required=True, help="Path to the local Zelph .bin file.")
    parser.add_argument("--index", required=True, help="Path to the sidecar index JSON.")
    parser.add_argument("--output", required=True, help="Path to write the manifest JSON.")
    parser.add_argument(
        "--hf-root",
        default="hf://datasets/acrion/zelph",
        help="Logical HF root prefix to use in the manifest.",
    )
    parser.add_argument(
        "--artifact-name",
        default=None,
        help="Artifact name used under the HF root. Defaults to the .bin stem.",
    )
    parser.add_argument(
        "--layout",
        default="v1",
        choices=SUPPORTED_LAYOUTS,
        help="Manifest storage layout to emit. `v1` uses monolithic .bin; `v2` uses multi-object chunks.",
    )
    parser.add_argument(
        "--emit-shards",
        action="store_true",
        help="For layout v2, materialize shard objects from .bin into a local shard tree.",
    )
    parser.add_argument(
        "--shard-root",
        default=None,
        help="Root directory for materialized v2 shard files. Defaults to <artifact-name>_shards beside output.",
    )
    parser.add_argument(
        "--node-route",
        default=None,
        help="Optional exact route-sidecar artifact to advertise in the manifest.",
    )
    parser.add_argument(
        "--node-route-object-path",
        default=None,
        help="Optional HF/logical object path for the route sidecar. Defaults to <artifact-root>/artifact.route.json.",
    )
    return parser.parse_args()


def _sanitize_lang_token(lang: str) -> str:
    token = "".join(ch if (ch.isalnum() or ch in ("_", "-", ".")) else "_" for ch in lang)
    return token or "lang"


def _chunk_filename(chunk_index: int, lang: str = "") -> str:
    base = f"chunk-{int(chunk_index):06d}"
    if lang:
        return f"{base}-{_sanitize_lang_token(lang)}.capnp-packed"
    return f"{base}.capnp-packed"


def load_index(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    for name in SECTION_NAMES:
        if name not in data:
            raise ValueError(f"Index JSON is missing section '{name}'")
    return data


def range_string(offset: int, length: int) -> str:
    return f"bytes={offset}-{offset + length - 1}"


def copy_range(src: Path, dst: Path, offset: int, length: int, chunk_size: int = 1024 * 1024) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    with src.open("rb") as src_handle, dst.open("wb") as dst_handle:
        src_handle.seek(offset)
        remaining = length
        while remaining > 0:
            n = min(chunk_size, remaining)
            chunk = src_handle.read(n)
            if not chunk:
                break
            dst_handle.write(chunk)
            remaining -= len(chunk)
        if remaining > 0:
            raise ValueError(f"Could not extract full range from {src}: {remaining} bytes short")


def build_section(section_name: str, entries: list[dict[str, Any]], shard_prefix: str, layout: str) -> dict[str, Any]:
    total_bytes = 0
    chunks: list[dict[str, Any]] = []
    langs: set[str] = set()

    for entry in sorted(entries, key=lambda e: int(e["chunkIndex"])):
        chunk_index = int(entry["chunkIndex"])
        offset = int(entry["offset"])
        length = int(entry["length"])
        total_bytes += length

        chunk_path = f"{shard_prefix}/{section_name}/{_chunk_filename(chunk_index, entry.get('lang', ''))}"
        chunk = {
            "chunkIndex": chunk_index,
            "objectPath": chunk_path,
            "length": length,
            "sourceOffset": offset,
            "sourceRange": range_string(offset, length),
        }
        if "which" in entry:
            chunk["which"] = entry["which"]
        if "lang" in entry:
            chunk["lang"] = entry["lang"]
            langs.add(entry["lang"])

        if layout == "v1":
            chunk.update(offset=offset)
        else:
            chunk["object"] = {
                "path": chunk_path,
                "mediaType": "application/octet-stream",
                "sizeBytes": length,
            }
            chunk["futureObjectPath"] = chunk_path

        chunks.append(chunk)

    section: dict[str, Any] = {
        "chunkCount": len(chunks),
        "totalBytes": total_bytes,
        "chunks": chunks,
    }
    if langs:
        section["languages"] = sorted(langs)
    return section


def emit_shards(
    bin_path: Path,
    sections: dict[str, dict[str, Any]],
    shard_root: Path,
) -> list[dict[str, Any]]:
    emitted = []
    for section_name, section in sections.items():
        for chunk in section["chunks"]:
            chunk_path = shard_root / section_name / Path(chunk["objectPath"]).name
            copy_range(bin_path, chunk_path, int(chunk["sourceOffset"]), int(chunk["length"]))
            emitted.append(
                {
                    "section": section_name,
                    "chunkIndex": int(chunk["chunkIndex"]),
                    "localPath": str(chunk_path),
                    "sizeBytes": int(chunk["length"]),
                }
            )
    return emitted


def build_section_v1(section_name: str, entries: list[dict[str, Any]], future_chunk_prefix: str) -> dict[str, Any]:
    total_bytes = sum(int(entry["length"]) for entry in entries)
    chunks: list[dict[str, Any]] = []
    langs: set[str] = set()

    for entry in entries:
        chunk = {
            "chunkIndex": int(entry["chunkIndex"]),
            "offset": int(entry["offset"]),
            "length": int(entry["length"]),
            "range": range_string(int(entry["offset"]), int(entry["length"])),
            "futureObjectPath": f"{future_chunk_prefix}/{section_name}/{_chunk_filename(int(entry['chunkIndex']), entry.get('lang', ''))}",
        }
        if "which" in entry:
            chunk["which"] = entry["which"]
        if "lang" in entry:
            chunk["lang"] = entry["lang"]
            langs.add(entry["lang"])
        chunks.append(chunk)

    section: dict[str, Any] = {
        "chunkCount": len(chunks),
        "totalBytes": total_bytes,
        "chunks": chunks,
    }
    if langs:
        section["languages"] = sorted(langs)
    return section


def build_future_layout_plan(sections: dict[str, dict[str, Any]], artifact_root: str, layout: str) -> dict[str, Any]:
    by_lang: dict[str, list[str]] = defaultdict(list)
    for section_name in ("nameOfNode", "nodeOfName"):
        for chunk in sections[section_name]["chunks"]:
            lang = chunk.get("lang")
            if lang:
                by_lang[lang].append(chunk["futureObjectPath"])

    if layout == "v2":
        return {
            "layoutVersion": "multi-object/v2",
            "description": "Current published shape is explicit shard objects plus manifest.",
            "objectPrefix": f"{artifact_root}/shards",
            "nodeRoutingIndex": None,
            "nameLanguagePartitions": {lang: sorted(paths) for lang, paths in sorted(by_lang.items())},
        }

    return {
        "layoutVersion": "planned-multi-object/v0",
        "description": "Future explicit multi-object shard projection; not yet physically emitted.",
        "objectPrefix": f"{artifact_root}/chunks",
        "nodeRoutingIndex": None,
        "nameLanguagePartitions": {lang: sorted(paths) for lang, paths in sorted(by_lang.items())},
    }


def build_manifest(
    bin_path: Path,
    index_path: Path,
    output_path: Path,
    hf_root: str,
    artifact_name: str,
    layout: str,
    node_route_path: Path | None = None,
    node_route_object_path: str | None = None,
) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    index = load_index(index_path)
    artifact_root = f"{hf_root.rstrip('/')}/{artifact_name}"
    chunk_prefix = f"{artifact_root}/shards"

    if layout == "v2":
        sections = {
            name: build_section(name, list(index[name]), chunk_prefix, layout="v2")
            for name in SECTION_NAMES
        }
    else:
        future_chunk_prefix = f"{artifact_root}/chunks"
        sections = {
            name: build_section_v1(name, list(index[name]), future_chunk_prefix) for name in SECTION_NAMES
        }

    total_chunk_count = sum(section["chunkCount"] for section in sections.values())
    total_chunk_bytes = sum(section["totalBytes"] for section in sections.values())
    header_length = int(index["header"]["length"])
    bin_size = bin_path.stat().st_size

    shard_prefix = f"{artifact_root}/shards"
    storage_mode = "multi-object-shards" if layout == "v2" else "single-file-offset-sidecar"

    hf_objects: dict[str, Any] = {
        "manifest": {
            "path": f"{artifact_root}/{output_path.name}",
            "role": "layout-manifest",
            "mediaType": "application/json",
        },
        "index": {
            "path": f"{artifact_root}/artifact.index.json",
            "role": "offset-sidecar",
            "mediaType": "application/json",
            "sizeBytes": index_path.stat().st_size,
        },
    }
    if layout == "v1":
        hf_objects["bin"] = {
            "path": f"{artifact_root}/artifact.bin",
            "role": "graph-payload",
            "mediaType": "application/octet-stream",
            "sizeBytes": bin_size,
        }
    for name, section in sections.items():
        hf_objects[name] = {
            "pathPrefix": f"{shard_prefix}/{name}",
            "count": section["chunkCount"],
            "role": "section-shards",
            "mediaType": "application/octet-stream",
        }
    if node_route_path is not None:
        route_path = node_route_object_path or f"{artifact_root}/artifact.route.json"
        hf_objects["nodeRouteIndex"] = {
            "path": route_path,
            "localPath": str(node_route_path),
            "role": "node-route-sidecar",
            "mediaType": "application/json",
            "sizeBytes": node_route_path.stat().st_size,
        }

    manifest = {
        "manifestVersion": f"zelph-hf-layout/{layout}",
        "createdAtUtc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "storageMode": storage_mode,
        "transport": {
            "primary": "http-range" if layout == "v1" else "hf-object-fetch",
            "fallback": "local-file",
        },
        "source": {
            "binPath": str(bin_path),
            "indexPath": str(index_path),
            "binSizeBytes": bin_size,
            "headerLengthBytes": header_length,
            "totalChunkCount": total_chunk_count,
            "totalChunkBytes": total_chunk_bytes,
        },
        "hfObjects": hf_objects,
        "selectorModel": {
            "unit": "section-chunk",
            "supportedSections": list(SECTION_NAMES),
            "supportedOperations": [
                "header-probe",
                "selected-chunk-read",
            ],
            "unsupportedOperations": [
                "small-neighborhood-expansion",
                "reasoning-complete-query",
            ],
        },
        "sections": sections,
        "layoutPlan": {
            "isCanonical": layout == "v2",
            "supportsNodeRouteIndex": node_route_path is not None,
        },
        "capabilities": {
            "headerProbe": True,
            "selectedChunkRead": True,
            "nodeRouteIndex": node_route_path is not None,
            "smallNeighborhoodExpansion": False,
            "fullReasoningSafe": False,
        },
        "cachePolicy": {
            "mode": "immutable-range-cache",
            "recommendedKeyFields": [
                "manifestVersion",
                "hfObjects",
                "sections",
            ],
            "invalidationRule": "invalidate on manifest/object identity change",
        },
        "limitations": [
            "Chunk selectors are file-local and are not guaranteed stable across regenerated .bin files.",
        ],
        "futureLayoutPlan": build_future_layout_plan(sections, artifact_root, layout),
    }
    if node_route_path is None:
        manifest["selectorModel"]["unsupportedOperations"].insert(0, "node-route")
        manifest["limitations"].append("No node-to-chunk routing index is defined yet.")
    else:
        manifest["selectorModel"]["supportedOperations"].append("node-route")
        manifest["futureLayoutPlan"]["nodeRoutingIndex"] = {
            "path": hf_objects["nodeRouteIndex"]["path"],
            "format": "zelph-node-route/v1",
        }

    if layout == "v1":
        manifest["limitations"].insert(
            0,
            "Current v1 hosting model is still a monolithic .bin plus sidecar index.",
        )
        manifest["limitations"].append(
            "This manifest is queryable via HTTP range reads against the hosted artifact.bin."
        )

    return manifest, sections


def main() -> int:
    args = parse_args()

    bin_path = Path(args.bin).resolve()
    index_path = Path(args.index).resolve()
    output_path = Path(args.output).resolve()
    artifact_name = args.artifact_name or bin_path.stem
    node_route_path = Path(args.node_route).resolve() if args.node_route else None

    manifest, sections = build_manifest(
        bin_path,
        index_path,
        output_path,
        args.hf_root,
        artifact_name,
        args.layout,
        node_route_path=node_route_path,
        node_route_object_path=args.node_route_object_path,
    )
    if args.layout == "v2" and args.emit_shards:
        shard_root = Path(
            args.shard_root
        ).resolve() if args.shard_root else output_path.parent / f"{artifact_name}_shards"
        emit_shards(bin_path, sections, shard_root)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2, sort_keys=True)
        handle.write("\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
