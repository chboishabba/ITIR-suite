from __future__ import annotations

import io
import json
from hashlib import sha256
from pathlib import Path
import tarfile
from typing import Any
from urllib.parse import parse_qs, unquote, urlparse

from .providers.hf import download_hf_object_bytes
from .providers.ipfs import download_ipfs_object_bytes


def load_erdfa_manifest_fixture(path: str | Path) -> dict[str, Any]:
    fixture_path = Path(path)
    payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    return _normalize_manifest_shape(payload)


def load_hf_container_fixture(path: str | Path) -> dict[str, Any]:
    fixture_path = Path(path)
    return json.loads(fixture_path.read_text(encoding="utf-8"))


def resolve_selector_to_shard(
    manifest: dict[str, Any],
    *,
    selectors: list[str],
) -> dict[str, Any]:
    selector_set = set(selectors)
    if not selector_set:
        raise ValueError("at least one selector is required")

    for shard in manifest.get("shards", []):
        shard_id = shard.get("id")
        if f"direct-shard={shard_id}" in selector_set:
            return {
                "artifactId": manifest["artifactId"],
                "artifactRevision": manifest["artifactRevision"],
                "matchedBy": "direct-shard",
                "selectors": selectors,
                "shard": shard,
            }
        routing_keys = set(shard.get("routingKeys", []))
        if selector_set.issubset(routing_keys):
            return {
                "artifactId": manifest["artifactId"],
                "artifactRevision": manifest["artifactRevision"],
                "matchedBy": "routingKeys",
                "selectors": selectors,
                "shard": shard,
            }
    raise KeyError(f"no shard matched selectors: {selectors}")


def build_container_index_from_tar(
    manifest: dict[str, Any],
    *,
    tar_path: str | Path,
    container_object_ref: dict[str, Any],
    container_id: str | None = None,
    container_revision: str | None = None,
    container_encoding: str = "tar",
) -> dict[str, Any]:
    archive_path = Path(tar_path)
    with tarfile.open(archive_path, "r:*") as handle:
        names = set(handle.getnames())

    members: list[dict[str, Any]] = []
    for shard in manifest.get("shards", []):
        shard_id = str(shard["id"])
        member_path = _infer_member_path_from_names(
            names,
            shard_id=shard_id,
            fallback=f"{shard_id}.cbor",
        )
        payload = extract_tar_member_bytes(archive_path, member_path=member_path)
        members.append(
            {
                "shardId": shard_id,
                "memberPath": member_path,
                "sizeBytes": len(payload),
                "contentDigest": f"sha256:{sha256(payload).hexdigest()}",
            }
        )

    return {
        "artifactId": manifest.get("artifactId"),
        "artifactRevision": manifest.get("artifactRevision"),
        "containerId": container_id or f"container:{archive_path.name}",
        "containerRevision": container_revision or manifest.get("artifactRevision"),
        "containerEncoding": container_encoding,
        "containerObjectRef": container_object_ref,
        "members": members,
    }


def attach_object_refs_from_container(
    manifest: dict[str, Any],
    container_index: dict[str, Any],
    *,
    object_refs: list[dict[str, Any]],
) -> dict[str, Any]:
    out = {
        **manifest,
        "shards": [],
    }
    by_shard = {entry["shardId"]: entry for entry in container_index.get("members", [])}
    for shard in manifest.get("shards", []):
        member = by_shard.get(shard["id"])
        if member is None:
            out["shards"].append(dict(shard))
            continue
        enriched_refs: list[dict[str, Any]] = []
        for ref in object_refs:
            enriched_refs.append(
                {
                    **ref,
                    "memberPath": member["memberPath"],
                    "sizeBytes": member["sizeBytes"],
                    "contentDigest": member["contentDigest"],
                }
            )
        out["shards"].append(
            {
                **shard,
                "objectRefs": enriched_refs,
            }
        )
    return out


def resolve_selector_to_object_ref(
    manifest: dict[str, Any],
    *,
    selectors: list[str],
    preferred_sinks: list[str] | None = None,
) -> dict[str, Any]:
    shard_resolution = resolve_selector_to_shard(manifest, selectors=selectors)
    shard = shard_resolution["shard"]
    object_refs = list(shard.get("objectRefs") or [])
    if not object_refs:
        raise KeyError(f"shard {shard['id']} has no objectRefs")

    sink_order = preferred_sinks or ["file", "hf", "ipfs"]
    selected = None
    for sink in sink_order:
        selected = next((ref for ref in object_refs if ref.get("sink") == sink), None)
        if selected is not None:
            break
    if selected is None:
        selected = object_refs[0]

    return {
        **shard_resolution,
        "selectedObjectRef": selected,
        "objectRefs": object_refs,
    }


def fetch_payload_from_object_ref(
    object_ref: dict[str, Any],
    *,
    hf_uri_map: dict[str, str] | None = None,
    ipfs_uri_map: dict[str, str] | None = None,
    ipfs_cid_map: dict[str, str] | None = None,
) -> dict[str, Any]:
    sink = object_ref.get("sink")
    uri = str(object_ref.get("uri"))
    member_path = object_ref.get("memberPath")

    local_object_path = _resolve_sink_object_path(
        sink=sink,
        uri=uri,
        hf_uri_map=hf_uri_map,
        ipfs_uri_map=ipfs_uri_map,
        ipfs_cid_map=ipfs_cid_map,
    )
    data = Path(local_object_path).read_bytes()
    resolved_member = _resolve_member_path(uri=uri, explicit_member=member_path)
    if resolved_member:
        payload = _extract_member_from_tar_bytes(data, resolved_member)
    else:
        payload = data
    return {
        "sink": sink,
        "uri": uri,
        "objectPath": str(local_object_path),
        "memberPath": resolved_member,
        "payload": {
            "sizeBytes": len(payload),
            "sha256": sha256(payload).hexdigest(),
        },
    }


def resolve_selector_to_object_ref_payload(
    manifest: dict[str, Any],
    *,
    selectors: list[str],
    preferred_sinks: list[str] | None = None,
    hf_uri_map: dict[str, str] | None = None,
    ipfs_uri_map: dict[str, str] | None = None,
    ipfs_cid_map: dict[str, str] | None = None,
) -> dict[str, Any]:
    plan = resolve_selector_to_object_ref(
        manifest,
        selectors=selectors,
        preferred_sinks=preferred_sinks,
    )
    fetched = fetch_payload_from_object_ref(
        plan["selectedObjectRef"],
        hf_uri_map=hf_uri_map,
        ipfs_uri_map=ipfs_uri_map,
        ipfs_cid_map=ipfs_cid_map,
    )
    return {
        "artifactId": plan["artifactId"],
        "artifactRevision": plan["artifactRevision"],
        "matchedBy": plan["matchedBy"],
        "selectors": selectors,
        "shard": plan["shard"],
        "selectedObjectRef": plan["selectedObjectRef"],
        "payload": fetched["payload"],
        "fetch": {
            "sink": fetched["sink"],
            "uri": fetched["uri"],
            "objectPath": fetched["objectPath"],
            "memberPath": fetched["memberPath"],
        },
    }


def resolve_selector_to_remote_hf_payload(
    manifest: dict[str, Any],
    *,
    selectors: list[str],
    hf_revision: str,
    preferred_sinks: list[str] | None = None,
) -> dict[str, Any]:
    plan = resolve_selector_to_object_ref(
        manifest,
        selectors=selectors,
        preferred_sinks=preferred_sinks or ["hf"],
    )
    selected = plan["selectedObjectRef"]
    if selected.get("sink") != "hf":
        raise ValueError(f"selected object ref is not hf: {selected}")
    fetched = download_hf_object_bytes(
        hf_uri=str(selected["uri"]),
        revision=hf_revision,
    )
    member_path = selected.get("memberPath")
    payload_bytes = fetched["bytes"]
    if member_path:
        payload_bytes = _extract_member_from_tar_bytes(payload_bytes, member_path)
    return {
        "artifactId": plan["artifactId"],
        "artifactRevision": plan["artifactRevision"],
        "matchedBy": plan["matchedBy"],
        "selectors": selectors,
        "shard": plan["shard"],
        "selectedObjectRef": selected,
        "payload": {
            "sizeBytes": len(payload_bytes),
            "sha256": sha256(payload_bytes).hexdigest(),
        },
        "fetch": {
            "sink": "hf",
            "uri": selected["uri"],
            "revision": hf_revision,
            "memberPath": member_path,
            "metadata": fetched["metadata"],
        },
    }


def resolve_selector_to_remote_ipfs_payload(
    manifest: dict[str, Any],
    *,
    selectors: list[str],
    gateway_base_url: str | None = None,
    preferred_sinks: list[str] | None = None,
) -> dict[str, Any]:
    plan = resolve_selector_to_object_ref(
        manifest,
        selectors=selectors,
        preferred_sinks=preferred_sinks or ["ipfs"],
    )
    selected = plan["selectedObjectRef"]
    if selected.get("sink") != "ipfs":
        raise ValueError(f"selected object ref is not ipfs: {selected}")
    fetched = download_ipfs_object_bytes(
        ipfs_uri=str(selected["uri"]),
        base_url=gateway_base_url,
    )
    member_path = selected.get("memberPath")
    payload_bytes = fetched["bytes"]
    if member_path:
        payload_bytes = _extract_member_from_tar_bytes(payload_bytes, member_path)
    return {
        "artifactId": plan["artifactId"],
        "artifactRevision": plan["artifactRevision"],
        "matchedBy": plan["matchedBy"],
        "selectors": selectors,
        "shard": plan["shard"],
        "selectedObjectRef": selected,
        "payload": {
            "sizeBytes": len(payload_bytes),
            "sha256": sha256(payload_bytes).hexdigest(),
        },
        "fetch": {
            "sink": "ipfs",
            "uri": selected["uri"],
            "memberPath": member_path,
            "metadata": fetched["metadata"],
        },
    }


def resolve_container_member(
    fixture: dict[str, Any] | None,
    *,
    shard_id: str,
) -> dict[str, Any]:
    if fixture is None:
        return {
            "artifactId": None,
            "artifactRevision": None,
            "containerId": None,
            "containerRevision": None,
            "containerEncoding": None,
            "containerObjectRef": None,
            "member": {
                "shardId": shard_id,
                "memberPath": f"{shard_id}.cbor",
            },
        }

    for member in fixture.get("members", []):
        if member.get("shardId") == shard_id:
            return {
                "artifactId": fixture["artifactId"],
                "artifactRevision": fixture["artifactRevision"],
                "containerId": fixture["containerId"],
                "containerRevision": fixture["containerRevision"],
                "containerEncoding": fixture["containerEncoding"],
                "containerObjectRef": fixture["containerObjectRef"],
                "member": member,
            }
    raise KeyError(f"unknown shardId: {shard_id}")


def resolve_selector_to_container_member(
    manifest: dict[str, Any],
    container_fixture: dict[str, Any] | None,
    *,
    selectors: list[str],
) -> dict[str, Any]:
    shard_resolution = resolve_selector_to_shard(manifest, selectors=selectors)
    container_resolution = resolve_container_member(
        container_fixture,
        shard_id=shard_resolution["shard"]["id"],
    )
    return {
        "artifactId": shard_resolution["artifactId"],
        "artifactRevision": shard_resolution["artifactRevision"],
        "matchedBy": shard_resolution["matchedBy"],
        "selectors": selectors,
        "shard": shard_resolution["shard"],
        "container": {
            "containerId": container_resolution["containerId"],
            "containerRevision": container_resolution["containerRevision"],
            "containerEncoding": container_resolution["containerEncoding"],
            "containerObjectRef": container_resolution["containerObjectRef"],
        },
        "member": container_resolution["member"],
    }


def extract_tar_member_bytes(
    tar_path: str | Path,
    *,
    member_path: str,
) -> bytes:
    archive_path = Path(tar_path)
    with tarfile.open(archive_path, "r:*") as handle:
        member = handle.getmember(member_path)
        extracted = handle.extractfile(member)
        if extracted is None:
            raise KeyError(f"unable to extract member: {member_path}")
        return extracted.read()


def resolve_selector_to_local_member_payload(
    manifest: dict[str, Any],
    container_fixture: dict[str, Any] | None,
    *,
    selectors: list[str],
    tar_path: str | Path,
) -> dict[str, Any]:
    resolved = resolve_selector_to_container_member(
        manifest,
        container_fixture,
        selectors=selectors,
    )
    member_path = resolved["member"]["memberPath"]
    if container_fixture is None:
        member_path = _infer_member_path_from_tar(tar_path, shard_id=resolved["shard"]["id"], fallback=member_path)
    payload = extract_tar_member_bytes(
        tar_path,
        member_path=member_path,
    )
    return {
        **resolved,
        "payload": {
            "sizeBytes": len(payload),
            "sha256": sha256(payload).hexdigest(),
        },
        "member": {**resolved["member"], "memberPath": member_path},
    }


def _infer_member_path_from_tar(tar_path: str | Path, *, shard_id: str, fallback: str) -> str:
    candidates = [fallback, f"payload/{shard_id}.cbor", f"{shard_id}.cbor"]
    archive_path = Path(tar_path)
    with tarfile.open(archive_path, "r:*") as handle:
        names = set(handle.getnames())
    for candidate in candidates:
        if candidate in names:
            return candidate
    raise KeyError(f"no matching member for shardId={shard_id} in tar; tried {candidates}")


def _normalize_manifest_shape(payload: dict[str, Any]) -> dict[str, Any]:
    if "artifactId" in payload:
        manifest = dict(payload)
        manifest["shards"] = [_normalize_shard_entry(entry) for entry in manifest.get("shards", [])]
        return manifest

    manifest = {
        "contractVersion": payload.get("contractVersion") or payload.get("contract_version"),
        "artifactId": payload.get("artifactId") or payload.get("artifact_id"),
        "artifactRevision": payload.get("artifactRevision") or payload.get("artifact_revision"),
        "artifactClass": payload.get("artifactClass") or payload.get("artifact_class"),
        "createdAtUtc": payload.get("createdAtUtc") or payload.get("created_at_utc"),
        "buildProvenance": payload.get("buildProvenance") or payload.get("build_provenance"),
        "name": payload.get("name"),
        "shards": [],
    }
    manifest["shards"] = [_normalize_shard_entry(entry) for entry in payload.get("shards", [])]
    return manifest


def _normalize_shard_entry(entry: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": entry.get("id"),
        "cid": entry.get("cid"),
        "tags": list(entry.get("tags") or []),
        "logicalKind": entry.get("logicalKind") or entry.get("logical_kind"),
        "encoding": entry.get("encoding"),
        "sizeBytes": entry.get("sizeBytes") or entry.get("size_bytes"),
        "objectRefs": [
            {
                "sink": ref.get("sink"),
                "uri": ref.get("uri"),
                "sizeBytes": ref.get("sizeBytes") or ref.get("size_bytes"),
                "contentDigest": ref.get("contentDigest") or ref.get("content_digest"),
                **({"memberPath": ref["memberPath"]} if ref.get("memberPath") is not None else {}),
            }
            for ref in (entry.get("objectRefs") or entry.get("object_refs") or [])
        ],
        "routingKeys": list(entry.get("routingKeys") or entry.get("routing_keys") or []),
    }


def _resolve_sink_object_path(
    *,
    sink: str | None,
    uri: str,
    hf_uri_map: dict[str, str] | None = None,
    ipfs_uri_map: dict[str, str] | None = None,
    ipfs_cid_map: dict[str, str] | None = None,
) -> Path:
    if sink == "file":
        parsed = urlparse(uri)
        if parsed.scheme == "file":
            return Path(unquote(parsed.path))
        return Path(uri)
    if sink == "hf":
        if hf_uri_map and uri in hf_uri_map:
            return Path(hf_uri_map[uri])
        raise KeyError(f"no local hf mapping for uri: {uri}")
    if sink == "ipfs":
        if ipfs_uri_map and uri in ipfs_uri_map:
            return Path(ipfs_uri_map[uri])
        parsed = urlparse(uri)
        cid = parsed.netloc or parsed.path.lstrip("/")
        if ipfs_cid_map and cid in ipfs_cid_map:
            return Path(ipfs_cid_map[cid])
        raise KeyError(f"no local ipfs mapping for uri/cid: {uri}")
    raise ValueError(f"unsupported sink: {sink}")


def _resolve_member_path(*, uri: str, explicit_member: str | None) -> str | None:
    if explicit_member:
        return explicit_member
    parsed = urlparse(uri)
    if parsed.fragment:
        query = parse_qs(parsed.fragment)
        member = query.get("member")
        if member:
            return member[0]
        if parsed.fragment.startswith("member="):
            return parsed.fragment.split("=", 1)[1]
    return None


def _extract_member_from_tar_bytes(data: bytes, member_path: str) -> bytes:
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:*") as handle:
        member = handle.getmember(member_path)
        extracted = handle.extractfile(member)
        if extracted is None:
            raise KeyError(f"unable to extract member: {member_path}")
        return extracted.read()


def _infer_member_path_from_names(names: set[str], *, shard_id: str, fallback: str) -> str:
    candidates = [fallback, f"payload/{shard_id}.cbor", f"{shard_id}.cbor"]
    for candidate in candidates:
        if candidate in names:
            return candidate
    raise KeyError(f"no matching member for shardId={shard_id}; tried {candidates}")
