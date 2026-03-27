#!/usr/bin/env python3
"""Build a shared shard artifact contract from an existing Zelph HF manifest.

This lifts Zelph's layout-oriented manifest into a transport-neutral logical
artifact contract and can emit both JSON and CBOR projections of the same
semantic artifact.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import cbor2


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a shared shard artifact contract from a Zelph HF manifest."
    )
    parser.add_argument("--manifest", required=True, help="Path to the Zelph manifest JSON.")
    parser.add_argument("--output-json", required=True, help="Path to write the shared contract JSON.")
    parser.add_argument("--output-cbor", default=None, help="Optional path to write the shared contract CBOR.")
    parser.add_argument("--artifact-id", default=None, help="Optional logical artifact id override.")
    parser.add_argument(
        "--artifact-revision",
        default=None,
        help="Optional immutable artifact revision override. Defaults to the manifest createdAtUtc.",
    )
    parser.add_argument(
        "--artifact-class",
        default="zelph-graph",
        help="Logical artifact class to record in the shared contract.",
    )
    parser.add_argument(
        "--ipfs-map",
        default=None,
        help="Optional JSON mapping file that attaches ipfs:// refs by shardId or HF uri.",
    )
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_ipfs_map(path: Path | None) -> dict[str, dict[str, Any]]:
    if path is None:
        return {}
    raw = load_json(path)
    if not isinstance(raw, dict):
        raise ValueError("IPFS map must be a JSON object")
    normalized: dict[str, dict[str, Any]] = {}
    for key, value in raw.items():
        if isinstance(value, str):
            normalized[key] = {"uri": value}
            continue
        if not isinstance(value, dict):
            raise ValueError("IPFS map values must be either strings or objects")
        uri = value.get("uri")
        if not uri:
            raise ValueError(f"IPFS map entry for {key!r} is missing 'uri'")
        normalized[key] = dict(value)
    return normalized


def sanitize_token(value: str) -> str:
    token = "".join(ch if (ch.isalnum() or ch in ("_", "-", ".")) else "_" for ch in value)
    return token or "token"


def logical_shard_id(chunk: dict[str, Any], selector_unit: str) -> str:
    unit = "bucket" if selector_unit == "bucket" else "chunk"
    base = f"{chunk['section']}-{unit}-{int(chunk['chunkIndex']):06d}"
    lang = chunk.get("lang")
    if lang:
        return f"{base}-{sanitize_token(lang)}"
    return base


def load_bytes_from_source(source_bin: Path, chunk: dict[str, Any]) -> bytes | None:
    offset = chunk.get("sourceOffset")
    length = chunk.get("length")
    if offset is None or length is None:
        return None
    if not source_bin.exists():
        return None
    with source_bin.open("rb") as handle:
        handle.seek(int(offset))
        data = handle.read(int(length))
    if len(data) != int(length):
        return None
    return data


def compute_digest(source_bin: Path | None, chunk: dict[str, Any]) -> str:
    if source_bin is not None:
        data = load_bytes_from_source(source_bin, chunk)
        if data is not None:
            return "sha256:" + hashlib.sha256(data).hexdigest()

    stable_bits = {
        "section": chunk["section"],
        "chunkIndex": int(chunk["chunkIndex"]),
        "length": int(chunk["length"]),
        "sourceOffset": int(chunk.get("sourceOffset", chunk.get("offset", 0))),
        "lang": chunk.get("lang"),
        "objectPath": chunk.get("objectPath") or chunk.get("futureObjectPath"),
    }
    return "identity-sha256:" + hashlib.sha256(
        json.dumps(stable_bits, sort_keys=True).encode("utf-8")
    ).hexdigest()


def infer_logical_kind(section: str, selector_unit: str) -> str:
    if section in ("left", "right"):
        return "adjacency-bucket" if selector_unit == "bucket" else "adjacency-chunk"
    if section in ("nameOfNode", "nodeOfName"):
        return "name-bucket" if selector_unit == "bucket" else "name-chunk"
    return "content-shard"


def infer_encoding(chunk: dict[str, Any]) -> str:
    object_path = chunk.get("objectPath") or chunk.get("futureObjectPath") or ""
    if object_path.endswith(".capnp-packed"):
        return "capnp-packed"
    if object_path.endswith(".cbor"):
        return "cbor"
    if object_path.endswith(".json"):
        return "json"
    return "application/octet-stream"


def attach_ipfs_refs(
    record: dict[str, Any],
    ipfs_map: dict[str, dict[str, Any]],
    *extra_candidates: str,
) -> None:
    candidates = [candidate for candidate in extra_candidates if candidate]
    record_id = record.get("shardId")
    if record_id:
        candidates.append(record_id)
    for ref in record["objectRefs"]:
        candidates.append(ref["uri"])

    for candidate in candidates:
        entry = ipfs_map.get(candidate)
        if entry is None:
            continue
        record["objectRefs"].append(
            {
                "sink": "ipfs",
                "uri": entry["uri"],
                "sizeBytes": int(entry.get("sizeBytes", record.get("sizeBytes", 0))),
                "contentDigest": entry.get(
                    "contentDigest",
                    record.get("contentDigest"),
                ),
            }
        )
        return


def flatten_sections(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    sections = manifest.get("sections", {})
    for section_name, section in sections.items():
        for chunk in section.get("chunks", []):
            row = dict(chunk)
            row["section"] = section_name
            rows.append(row)
    return rows


def build_contract(
    manifest: dict[str, Any],
    artifact_id_override: str | None,
    artifact_revision_override: str | None,
    artifact_class: str,
    ipfs_map: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    source = manifest.get("source", {})
    selector_model = manifest.get("selectorModel", {})
    selector_unit = selector_model.get("unit", "section-chunk")
    source_bin_path = source.get("binPath")
    source_bin = Path(source_bin_path).resolve() if source_bin_path else None

    artifact_id = artifact_id_override or Path(source_bin_path).stem if source_bin_path else "shared-artifact"
    artifact_revision = artifact_revision_override or manifest.get("createdAtUtc") or "unknown-revision"

    shards: list[dict[str, Any]] = []
    for chunk in flatten_sections(manifest):
        object_uri = chunk.get("objectPath") or chunk.get("futureObjectPath")
        if object_uri is None:
            object_uri = f"local-range://{chunk['section']}/{int(chunk['chunkIndex']):06d}"
        shard = {
            "shardId": logical_shard_id(chunk, selector_unit),
            "section": chunk["section"],
            "logicalKind": infer_logical_kind(chunk["section"], selector_unit),
            "encoding": infer_encoding(chunk),
            "sizeBytes": int(chunk["length"]),
            "contentDigest": compute_digest(source_bin, chunk),
            "routingKeys": [f"section:{chunk['section']}"],
            "objectRefs": [
                {
                    "sink": "hf" if str(object_uri).startswith("hf://") else "file",
                    "uri": object_uri,
                    "sizeBytes": int(chunk["length"]),
                    "contentDigest": None,
                }
            ],
        }
        if chunk.get("lang"):
            shard["routingKeys"].append(f"lang:{chunk['lang']}")
        if chunk["section"] == "left":
            shard["routingKeys"].append("route-left-node")
        elif chunk["section"] == "right":
            shard["routingKeys"].append("route-right-node")
        elif chunk["section"] == "nameOfNode":
            shard["routingKeys"].append("route-node")
        elif chunk["section"] == "nodeOfName":
            shard["routingKeys"].append("route-name")

        for ref in shard["objectRefs"]:
            ref["contentDigest"] = shard["contentDigest"]
        attach_ipfs_refs(shard, ipfs_map)
        shards.append(shard)

    routing_index = None
    node_route_obj = manifest.get("hfObjects", {}).get("nodeRouteIndex")
    if isinstance(node_route_obj, dict):
        route_uri = node_route_obj.get("path")
        if route_uri:
            routing_index = {
                "logicalKind": "routing-index",
                "format": "zelph-node-route/v1",
                "objectRefs": [
                    {
                        "sink": "hf" if str(route_uri).startswith("hf://") else "file",
                        "uri": route_uri,
                        "sizeBytes": int(node_route_obj.get("sizeBytes", 0)),
                        "contentDigest": None,
                    }
                ],
            }
            route_digest = "identity-sha256:" + hashlib.sha256(
                json.dumps(node_route_obj, sort_keys=True).encode("utf-8")
            ).hexdigest()
            routing_index["objectRefs"][0]["contentDigest"] = route_digest
            attach_ipfs_refs(routing_index, ipfs_map, "routingIndex")

    contract = {
        "contractVersion": "shared-shard-artifact/v1",
        "artifactId": artifact_id,
        "artifactRevision": artifact_revision,
        "artifactClass": artifact_class,
        "createdAtUtc": manifest.get("createdAtUtc"),
        "buildProvenance": {
            "sourceManifestVersion": manifest.get("manifestVersion"),
            "sourceManifestPath": str(manifest.get("hfObjects", {}).get("manifest", {}).get("path", "")),
            "sourceBinPath": source_bin_path,
            "builder": "tools/build_shared_shard_artifact_contract.py",
        },
        "selectorModel": {
            "unit": selector_unit,
            "supportedOperations": selector_model.get("supportedOperations", []),
            "supportedSections": selector_model.get("supportedSections", []),
        },
        "transportHints": {
            "preferredReadSink": "hf",
            "preferredPublishSink": "ipfs",
        },
        "shards": shards,
    }
    if routing_index is not None:
        contract["routingIndex"] = routing_index
    return contract


def main() -> int:
    args = parse_args()
    manifest_path = Path(args.manifest).resolve()
    output_json = Path(args.output_json).resolve()
    output_cbor = Path(args.output_cbor).resolve() if args.output_cbor else None
    ipfs_map = load_ipfs_map(Path(args.ipfs_map).resolve()) if args.ipfs_map else {}

    manifest = load_json(manifest_path)
    contract = build_contract(
        manifest,
        args.artifact_id,
        args.artifact_revision,
        args.artifact_class,
        ipfs_map,
    )

    output_json.parent.mkdir(parents=True, exist_ok=True)
    with output_json.open("w", encoding="utf-8") as handle:
        json.dump(contract, handle, indent=2, sort_keys=True)
        handle.write("\n")

    if output_cbor is not None:
        output_cbor.parent.mkdir(parents=True, exist_ok=True)
        with output_cbor.open("wb") as handle:
            cbor2.dump(contract, handle)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
