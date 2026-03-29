from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path
import tarfile
from typing import Any


def load_erdfa_manifest_fixture(path: str | Path) -> dict[str, Any]:
    fixture_path = Path(path)
    return json.loads(fixture_path.read_text(encoding="utf-8"))


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
