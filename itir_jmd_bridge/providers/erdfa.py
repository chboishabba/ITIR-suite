from __future__ import annotations

import json
import struct
import tarfile
from hashlib import sha256
from pathlib import Path
from typing import Any


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


DA51_TAG = 0xDA51


class CborDecodeError(ValueError):
    pass


def _read_uint(data: bytes, offset: int, additional: int) -> tuple[int, int]:
    if additional < 24:
        return additional, offset
    if additional == 24:
        return data[offset], offset + 1
    if additional == 25:
        return int.from_bytes(data[offset : offset + 2], "big"), offset + 2
    if additional == 26:
        return int.from_bytes(data[offset : offset + 4], "big"), offset + 4
    if additional == 27:
        return int.from_bytes(data[offset : offset + 8], "big"), offset + 8
    raise CborDecodeError(f"unsupported CBOR additional info: {additional}")


def _decode_item(data: bytes, offset: int = 0) -> tuple[Any, int]:
    if offset >= len(data):
        raise CborDecodeError("unexpected end of CBOR payload")
    head = data[offset]
    offset += 1
    major = head >> 5
    additional = head & 0x1F

    if additional == 31:
        raise CborDecodeError("indefinite-length CBOR items are not supported")

    if major == 0:
        return _read_uint(data, offset, additional)

    if major == 1:
        value, offset = _read_uint(data, offset, additional)
        return -1 - value, offset

    if major == 2:
        length, offset = _read_uint(data, offset, additional)
        return data[offset : offset + length], offset + length

    if major == 3:
        length, offset = _read_uint(data, offset, additional)
        return data[offset : offset + length].decode("utf-8"), offset + length

    if major == 4:
        length, offset = _read_uint(data, offset, additional)
        items = []
        for _ in range(length):
            value, offset = _decode_item(data, offset)
            items.append(value)
        return items, offset

    if major == 5:
        length, offset = _read_uint(data, offset, additional)
        items: dict[Any, Any] = {}
        for _ in range(length):
            key, offset = _decode_item(data, offset)
            value, offset = _decode_item(data, offset)
            items[key] = value
        return items, offset

    if major == 6:
        tag, offset = _read_uint(data, offset, additional)
        value, offset = _decode_item(data, offset)
        return {"__cbor_tag__": tag, "value": value}, offset

    if major != 7:
        raise CborDecodeError(f"unsupported CBOR major type: {major}")

    if additional == 20:
        return False, offset
    if additional == 21:
        return True, offset
    if additional == 22:
        return None, offset
    if additional == 23:
        return None, offset
    if additional == 24:
        return data[offset], offset + 1
    if additional == 25:
        return struct.unpack(">e", data[offset : offset + 2])[0], offset + 2
    if additional == 26:
        return struct.unpack(">f", data[offset : offset + 4])[0], offset + 4
    if additional == 27:
        return struct.unpack(">d", data[offset : offset + 8])[0], offset + 8
    raise CborDecodeError(f"unsupported CBOR simple value: {additional}")


def decode_cbor(data: bytes) -> Any:
    value, offset = _decode_item(data, 0)
    if offset != len(data):
        raise CborDecodeError("trailing bytes after CBOR payload")
    return value


def _unwrap_da51_tag(value: Any) -> Any:
    if isinstance(value, dict) and value.get("__cbor_tag__") == DA51_TAG:
        return value.get("value")
    return value


def _pairs_to_map(pairs: Any) -> dict[str, str]:
    result: dict[str, str] = {}
    if not isinstance(pairs, list):
        return result
    for pair in pairs:
        if isinstance(pair, list | tuple) and len(pair) == 2:
            key, value = pair
            result[str(key)] = str(value)
    return result


def decode_erdfa_cbor_bytes(data: bytes) -> dict[str, Any]:
    payload = _unwrap_da51_tag(decode_cbor(data))
    if not isinstance(payload, dict):
        raise CborDecodeError("expected DA51 payload to decode to a CBOR map")
    return payload


def summarize_erdfa_object(payload: dict[str, Any]) -> dict[str, Any]:
    summary: dict[str, Any] = {"kind": "unknown"}
    if "shards" in payload and "name" in payload:
        summary["kind"] = "manifest"
        summary["name"] = str(payload["name"])
        shards = payload.get("shards")
        summary["shards"] = list(shards) if isinstance(shards, list) else []
        summary["shard_count"] = len(summary["shards"])
        return summary

    if "component" in payload and "id" in payload:
        component = payload.get("component")
        component_type = component.get("type") if isinstance(component, dict) else None
        pairs = _pairs_to_map(component.get("pairs")) if isinstance(component, dict) else {}
        tags = [str(tag) for tag in payload.get("tags") or []]
        summary.update(
            {
                "kind": "shard",
                "id": str(payload.get("id")),
                "cid": str(payload.get("cid")) if payload.get("cid") is not None else None,
                "tags": tags,
                "component_type": component_type,
                "component_pairs": pairs,
            }
        )
        if pairs.get("content"):
            summary["content_preview"] = pairs["content"][:160]
        return summary

    if {"prefix", "dasl_type", "cid"}.issubset(payload):
        summary.update(
            {
                "kind": "dasl_object",
                "prefix": payload.get("prefix"),
                "dasl_type": payload.get("dasl_type"),
                "cid": str(payload.get("cid")) if payload.get("cid") is not None else None,
                "orbifold": list(payload.get("orbifold") or []),
                "bott": payload.get("bott"),
            }
        )
        return summary

    summary["payload_keys"] = sorted(str(key) for key in payload.keys())
    return summary


def _shard_node_id(shard_id: str) -> str:
    return f"jmd:erdfa:shard:{shard_id}"


def _manifest_node_id(name: str) -> str:
    return f"jmd:erdfa:manifest:{name}"


def _primary_shard_summary(decoded_objects: list[dict[str, Any]]) -> dict[str, Any] | None:
    shard_summaries = [item for item in decoded_objects if item.get("kind") == "shard"]
    non_arrow = [item for item in shard_summaries if "arrow" not in set(item.get("tags") or [])]
    if non_arrow:
        return non_arrow[0]
    if shard_summaries:
        return shard_summaries[0]
    return None


def _component_kind_from_type(component_type: Any) -> str | None:
    if component_type is None:
        return None
    component_type = str(component_type)
    if component_type in {"Paragraph", "Heading", "Code", "Table", "List", "Link", "Image", "Group", "Tree"}:
        return "text"
    if component_type == "KeyValue":
        return "metadata"
    if component_type == "MapEntity":
        return "map"
    return component_type.lower()


def _derive_archive_graph(decoded_objects: list[dict[str, Any]]) -> dict[str, Any]:
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    seen_nodes: set[str] = set()
    seen_edges: set[str] = set()
    manifest = next((item for item in decoded_objects if item.get("kind") == "manifest"), None)
    manifest_id = None
    if manifest and manifest.get("name"):
        manifest_id = _manifest_node_id(str(manifest["name"]))
        seen_nodes.add(manifest_id)
        nodes.append(
            {
                "node_id": manifest_id,
                "kind": "manifest",
                "cid": None,
                "label": str(manifest["name"]),
                "ref": manifest_id,
            }
        )

    def add_shard_node(shard: dict[str, Any]) -> None:
        shard_id = str(shard["id"])
        node_id = _shard_node_id(shard_id)
        if node_id in seen_nodes:
            return
        seen_nodes.add(node_id)
        tags = list(shard.get("tags") or [])
        component_type = shard.get("component_type")
        kind = "arrow_shard" if "arrow" in set(tags) else str(component_type or "shard").lower()
        nodes.append(
            {
                "node_id": node_id,
                "kind": kind,
                "cid": shard.get("cid"),
                "label": shard_id,
                "ref": node_id,
                "component_type": component_type,
                "tags": tags,
            }
        )

    def add_edge(edge: dict[str, Any]) -> None:
        edge_id = edge["edge_id"]
        if edge_id not in seen_edges:
            seen_edges.add(edge_id)
            edges.append(edge)

    shard_summaries = [item for item in decoded_objects if item.get("kind") == "shard"]
    for shard in shard_summaries:
        add_shard_node(shard)
        shard_node_id = _shard_node_id(str(shard["id"]))
        if manifest_id is not None:
            add_edge(
                {
                    "edge_id": f"{manifest_id}->{shard_node_id}:contains",
                    "from_node_id": manifest_id,
                    "to_node_id": shard_node_id,
                    "kind": "contains",
                }
            )
        pairs = shard.get("component_pairs") or {}
        if pairs.get("parent"):
            parent_node_id = _shard_node_id(str(pairs["parent"]))
            if parent_node_id not in seen_nodes:
                seen_nodes.add(parent_node_id)
                nodes.append(
                    {
                        "node_id": parent_node_id,
                        "kind": "shard",
                        "cid": None,
                        "label": str(pairs["parent"]),
                        "ref": parent_node_id,
                    }
                )
            add_edge(
                {
                    "edge_id": f"{parent_node_id}->{shard_node_id}:parent",
                    "from_node_id": parent_node_id,
                    "to_node_id": shard_node_id,
                    "kind": "parent",
                }
            )
        if "arrow" in set(shard.get("tags") or []) and pairs.get("from") and pairs.get("to"):
            from_node_id = _shard_node_id(str(pairs["from"]))
            to_node_id = _shard_node_id(str(pairs["to"]))
            for node_id, label in ((from_node_id, str(pairs["from"])), (to_node_id, str(pairs["to"]))):
                if node_id not in seen_nodes:
                    seen_nodes.add(node_id)
                    nodes.append(
                        {
                            "node_id": node_id,
                            "kind": "shard",
                            "cid": None,
                            "label": label,
                            "ref": node_id,
                        }
                    )
            add_edge(
                {
                    "edge_id": f"{from_node_id}->{to_node_id}:cft_arrow",
                    "from_node_id": from_node_id,
                    "to_node_id": to_node_id,
                    "kind": "cft_arrow",
                    "morphism": pairs.get("morphism"),
                    "scale_from": pairs.get("scale_from"),
                    "scale_to": pairs.get("scale_to"),
                    "arrow_shard_id": str(shard["id"]),
                }
            )
    return {"nodes": nodes, "edges": edges}


def describe_erdfa_tar(path: str | Path) -> dict[str, Any]:
    tar_path = Path(path)
    members: list[dict[str, Any]] = []
    decoded_objects: list[dict[str, Any]] = []
    manifest_summary: dict[str, Any] | None = None
    with tarfile.open(tar_path, "r:*") as archive:
        for member in archive.getmembers():
            if member.isdir():
                continue
            shard_id = Path(member.name).stem if member.name.endswith(".cbor") else None
            entry: dict[str, Any] = {
                "name": member.name,
                "size": member.size,
                "kind": "cbor_shard" if member.name.endswith(".cbor") else "artifact",
                "shard_id": shard_id,
            }
            if member.name.endswith(".cbor"):
                extracted = archive.extractfile(member)
                payload = extracted.read() if extracted is not None else b""
                try:
                    decoded = summarize_erdfa_object(decode_erdfa_cbor_bytes(payload))
                    entry["decode_status"] = "ok"
                    entry["decoded_kind"] = decoded.get("kind")
                    if decoded.get("kind") == "shard":
                        entry["decoded_id"] = decoded.get("id")
                        entry["component_type"] = decoded.get("component_type")
                        entry["tags"] = decoded.get("tags")
                        decoded_objects.append(decoded)
                    elif decoded.get("kind") == "manifest":
                        manifest_summary = decoded
                        decoded_objects.append(decoded)
                    else:
                        entry["summary"] = decoded
                except Exception as exc:
                    entry["decode_status"] = "error"
                    entry["decode_error"] = str(exc)
            members.append(entry)
    archive_sha256 = sha256(tar_path.read_bytes()).hexdigest()
    shard_members = [member["shard_id"] for member in members if member["shard_id"] and member["shard_id"] != "manifest"]
    archive_graph = _derive_archive_graph(decoded_objects)
    primary_shard = _primary_shard_summary(decoded_objects)
    return {
        "provider": "erdfa-publish-rs",
        "archive_path": str(tar_path),
        "archive_sha256": archive_sha256,
        "member_count": len(members),
        "members": members,
        "shard_members": shard_members,
        "manifest_present": any(member["name"] == "manifest.cbor" for member in members),
        "manifest": manifest_summary,
        "decoded_shards": decoded_objects,
        "primary_shard_id": primary_shard.get("id") if primary_shard else None,
        "primary_shard": primary_shard,
        "graph": archive_graph,
    }


def normalize_erdfa_descriptor(
    descriptor: dict[str, Any] | str | Path | None = None,
    *,
    tar_path: str | Path | None = None,
) -> dict[str, Any]:
    normalized: dict[str, Any] = {
        "provider": "erdfa-publish-rs",
        "component_kind": "text",
        "parent_refs": [],
        "link_refs": [],
        "tags": [],
    }
    if descriptor is not None:
        if isinstance(descriptor, (str, Path)):
            loaded = _read_json(Path(descriptor))
        else:
            loaded = dict(descriptor)
        normalized.update(loaded)
    if tar_path is not None:
        normalized["archive"] = describe_erdfa_tar(tar_path)
        primary_shard = normalized["archive"].get("primary_shard") or {}
        if primary_shard:
            normalized.setdefault("component_type", primary_shard.get("component_type"))
            component_kind = _component_kind_from_type(primary_shard.get("component_type"))
            if component_kind and normalized.get("component_kind") == "text":
                normalized["component_kind"] = component_kind
            normalized.setdefault("cid", primary_shard.get("cid"))
            normalized["tags"] = list(dict.fromkeys([*normalized.get("tags", []), *(primary_shard.get("tags") or [])]))
            pairs = primary_shard.get("component_pairs") or {}
            if pairs.get("parent"):
                normalized["parent_refs"] = list(dict.fromkeys([*normalized.get("parent_refs", []), str(pairs["parent"])]))
        if not normalized.get("shard_id"):
            shard_id = normalized["archive"].get("primary_shard_id")
            if shard_id:
                normalized["shard_id"] = shard_id
            else:
                shard_members = normalized["archive"].get("shard_members") or []
                if shard_members:
                    normalized["shard_id"] = shard_members[0]
    return normalized
