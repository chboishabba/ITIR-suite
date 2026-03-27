#!/usr/bin/env python3
"""Build a deterministic ipfs:// ref map for a shared shard contract.

This does not publish anything. It computes raw CIDv1 identifiers from local
shard bytes so the same logical shard ids can carry IPFS refs in the shared
artifact contract.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build an IPFS ref map from a shared shard contract and local shard tree.")
    parser.add_argument("--shared-contract", required=True, help="Path to the shared contract JSON.")
    parser.add_argument("--shard-root", required=True, help="Root directory containing local shard files.")
    parser.add_argument(
        "--routing-index-local-path",
        default=None,
        help="Optional local path for the routing index sidecar to map into ipfs:// as well.",
    )
    parser.add_argument("--output", required=True, help="Path to write the IPFS ref map JSON.")
    return parser.parse_args()


def encode_varint(value: int) -> bytes:
    out = bytearray()
    remaining = int(value)
    while True:
        to_write = remaining & 0x7F
        remaining >>= 7
        if remaining:
            out.append(to_write | 0x80)
        else:
            out.append(to_write)
            return bytes(out)


def raw_cidv1_sha256(data: bytes) -> str:
    digest = hashlib.sha256(data).digest()
    cid_bytes = (
        encode_varint(1)  # cidv1
        + encode_varint(0x55)  # raw codec
        + encode_varint(0x12)  # sha2-256 multihash code
        + encode_varint(len(digest))
        + digest
    )
    encoded = base64.b32encode(cid_bytes).decode("ascii").lower().rstrip("=")
    return "b" + encoded


def resolve_local_path(uri: str, shard_root: Path) -> Path:
    if "/shards/" in uri:
        tail = uri.split("/shards/", 1)[1]
        return shard_root / tail
    path = Path(uri)
    if path.is_absolute():
        return path
    return shard_root / path.name


def add_ipfs_entry(mapping: dict[str, Any], key: str, local_path: Path) -> None:
    data = local_path.read_bytes()
    cid = raw_cidv1_sha256(data)
    mapping[key] = {
        "uri": f"ipfs://{cid}",
        "sizeBytes": len(data),
        "contentDigest": "sha256:" + hashlib.sha256(data).hexdigest(),
        "localPath": str(local_path),
    }


def build_ipfs_map(
    contract: dict[str, Any],
    shard_root: Path,
    routing_index_local_path: Path | None,
) -> dict[str, Any]:
    mapping: dict[str, Any] = {}
    for shard in contract.get("shards", []):
        refs = shard.get("objectRefs", [])
        preferred = next((ref for ref in refs if ref.get("sink") in {"hf", "file"}), None)
        if preferred is None:
            continue
        local_path = resolve_local_path(str(preferred["uri"]), shard_root)
        add_ipfs_entry(mapping, shard["shardId"], local_path)

    routing_index = contract.get("routingIndex") or {}
    routing_refs = routing_index.get("objectRefs", [])
    preferred_route = next((ref for ref in routing_refs if ref.get("sink") in {"hf", "file"}), None)
    if preferred_route is not None and routing_index_local_path is not None:
        add_ipfs_entry(mapping, "routingIndex", routing_index_local_path)
        mapping[str(preferred_route["uri"])] = dict(mapping["routingIndex"])
    return mapping


def main() -> int:
    args = parse_args()
    contract_path = Path(args.shared_contract).resolve()
    shard_root = Path(args.shard_root).resolve()
    routing_index_local_path = (
        Path(args.routing_index_local_path).resolve()
        if args.routing_index_local_path
        else None
    )
    output_path = Path(args.output).resolve()

    with contract_path.open("r", encoding="utf-8") as handle:
        contract = json.load(handle)

    mapping = build_ipfs_map(contract, shard_root, routing_index_local_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(mapping, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
