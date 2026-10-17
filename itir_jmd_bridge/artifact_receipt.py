from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
import re
from typing import Any
from urllib.parse import urlparse


RECEIPT_SCHEMA = "artifact-resolution-receipt/v1"
LOGICAL_CONTRACT = "shared-shard-artifact/v1"
_ALLOWED_SINKS = frozenset({"file", "hf", "ipfs"})
_SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")


def _require_text(name: str, value: Any) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"{name} must be non-empty")
    return text


def _sha256_digest(name: str, value: Any) -> str:
    text = _require_text(name, value)
    body = text.split(":", 1)[1] if text.lower().startswith("sha256:") else text
    if not _SHA256_RE.fullmatch(body):
        raise ValueError(f"{name} must be a sha256 digest")
    return f"sha256:{body.lower()}"


def _ipfs_cid(uri: str) -> str:
    if not uri.startswith("ipfs://"):
        raise ValueError("IPFS object ref must use ipfs:// URI")
    parsed = urlparse(uri)
    cid = parsed.netloc or parsed.path.lstrip("/").split("/", 1)[0]
    if not cid:
        raise ValueError("IPFS object ref has no CID")
    return cid


def build_artifact_resolution_receipt(resolved: dict[str, Any]) -> dict[str, Any]:
    """Build a transport-only receipt from a resolved shared-shard payload.

    The receipt binds logical artifact identity to one selected sink and to the
    digest of the payload actually returned by the resolver.  It deliberately
    establishes neither theorem proof nor semantic/legal authority.
    """

    artifact_id = _require_text("artifactId", resolved.get("artifactId"))
    artifact_revision = _require_text(
        "artifactRevision", resolved.get("artifactRevision")
    )
    shard = resolved.get("shard") or {}
    shard_id = _require_text("shard.id", shard.get("id") or shard.get("shardId"))

    selected = deepcopy(resolved.get("selectedObjectRef") or {})
    sink = _require_text("selectedObjectRef.sink", selected.get("sink"))
    if sink not in _ALLOWED_SINKS:
        raise ValueError(f"unsupported artifact sink: {sink}")
    uri = _require_text("selectedObjectRef.uri", selected.get("uri"))

    payload = resolved.get("payload") or {}
    payload_digest = _sha256_digest("payload.sha256", payload.get("sha256"))
    payload_size = payload.get("sizeBytes")
    if not isinstance(payload_size, int) or payload_size < 0:
        raise ValueError("payload.sizeBytes must be a non-negative integer")

    object_digest_value = selected.get("contentDigest")
    shard_digest_value = shard.get("contentDigest")
    if object_digest_value is None and shard_digest_value is None:
        raise ValueError("resolved artifact has no expected content digest")
    content_digest = _sha256_digest(
        "contentDigest",
        object_digest_value if object_digest_value is not None else shard_digest_value,
    )
    if shard_digest_value is not None:
        shard_digest = _sha256_digest("shard.contentDigest", shard_digest_value)
        if shard_digest != content_digest:
            raise ValueError("shard and object-ref content digests disagree")
    if payload_digest != content_digest:
        raise ValueError("payload digest does not match logical shard content digest")

    object_size = selected.get("sizeBytes")
    if object_size is not None and int(object_size) != payload_size:
        raise ValueError("payload size does not match selected object-ref size")

    fetch = deepcopy(resolved.get("fetch") or {})
    fetch_sink = str(fetch.get("sink") or sink)
    fetch_uri = str(fetch.get("uri") or uri)
    if fetch_sink != sink or fetch_uri != uri:
        raise ValueError("fetch transport does not match selected object ref")

    transport: dict[str, Any] = {
        "sink": sink,
        "uri": uri,
    }
    metadata = deepcopy(fetch.get("metadata") or {})
    if sink == "ipfs":
        cid = _ipfs_cid(uri)
        observed_cid = metadata.get("cid")
        if observed_cid is not None and str(observed_cid) != cid:
            raise ValueError("observed IPFS CID does not match selected object ref")
        transport["cid"] = cid
    if metadata:
        transport["metadata"] = metadata
    member_path = selected.get("memberPath") or fetch.get("memberPath")
    if member_path:
        transport["memberPath"] = str(member_path)

    selected["contentDigest"] = content_digest
    selected["sizeBytes"] = payload_size

    return {
        "schemaVersion": RECEIPT_SCHEMA,
        "logicalContractVersion": LOGICAL_CONTRACT,
        "logicalArtifactRef": f"{artifact_id}@{artifact_revision}#{shard_id}",
        "artifactId": artifact_id,
        "artifactRevision": artifact_revision,
        "shardId": shard_id,
        "contentDigest": content_digest,
        "payloadDigest": payload_digest,
        "payloadSizeBytes": payload_size,
        "matchedBy": resolved.get("matchedBy"),
        "selectors": list(resolved.get("selectors") or []),
        "objectRef": selected,
        "transport": transport,
        "verified": True,
        "authority": "transport-only",
        "establishesProof": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Emit a verified transport-only receipt from an ITIR resolved-artifact JSON payload."
    )
    parser.add_argument("--resolved-json", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)

    resolved = json.loads(args.resolved_json.read_text(encoding="utf-8"))
    receipt = build_artifact_resolution_receipt(resolved)
    rendered = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    if args.output is None:
        print(rendered, end="")
    else:
        args.output.write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
