from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def build_zkperf_stream_latest(
    stream_manifest: dict[str, Any],
    hf_receipt: dict[str, Any],
) -> dict[str, Any]:
    return {
        "contractVersion": "zkperf-stream-latest/v1",
        "streamId": stream_manifest["streamId"],
        "latestRevision": stream_manifest["streamRevision"],
        "latestWindowId": stream_manifest.get("latestWindowId"),
        "windowCount": stream_manifest.get("windowCount", len(stream_manifest.get("windows", []))),
        "observationCount": stream_manifest.get("observationCount"),
        "sequenceRange": dict(stream_manifest.get("sequenceRange") or {}),
        "containerObjectRef": dict(stream_manifest["containerObjectRef"]),
        "acknowledgedRevision": hf_receipt["acknowledgedRevision"],
        "verified": hf_receipt["verified"],
    }


def write_zkperf_stream_publish_artifacts(
    *,
    output_root: str | Path,
    publish_payload: dict[str, Any],
) -> dict[str, str]:
    stream_manifest = publish_payload["streamManifest"]
    root = Path(output_root) / stream_manifest["streamId"] / stream_manifest["streamRevision"]
    root.mkdir(parents=True, exist_ok=True)
    paths = {
        "streamManifest": root / "stream-manifest.json",
        "streamLatest": root / "stream-latest.json",
        "hfReceipt": root / "hf-receipt.json",
    }
    if "streamIndex" in publish_payload:
        paths["streamIndex"] = root / "stream-index.json"
    if "streamIndexReceipt" in publish_payload:
        paths["streamIndexReceipt"] = root / "stream-index-receipt.json"
    paths["streamManifest"].write_text(json.dumps(stream_manifest, indent=2, sort_keys=True), encoding="utf-8")
    paths["streamLatest"].write_text(json.dumps(publish_payload["streamLatest"], indent=2, sort_keys=True), encoding="utf-8")
    paths["hfReceipt"].write_text(json.dumps(publish_payload["hfReceipt"], indent=2, sort_keys=True), encoding="utf-8")
    if "streamIndex" in publish_payload:
        paths["streamIndex"].write_text(json.dumps(publish_payload["streamIndex"], indent=2, sort_keys=True), encoding="utf-8")
    if "streamIndexReceipt" in publish_payload:
        paths["streamIndexReceipt"].write_text(json.dumps(publish_payload["streamIndexReceipt"], indent=2, sort_keys=True), encoding="utf-8")
    return {key: str(value) for key, value in paths.items()}


def build_zkperf_stream_index(
    *,
    stream_id: str,
    index_hf_uri: str | None = None,
    created_at: str | None = None,
    retention_policy: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "contractVersion": "zkperf-stream-index/v1",
        "streamId": stream_id,
        "createdAtUtc": created_at,
        "observationCount": None,
        "observationIndex": [],
        "retentionPolicy": retention_policy
        or {
            "policyVersion": "zkperf-retention/v1",
            "mode": "retain-latest-n",
            "maxRevisionCount": 2,
        },
        "latestRevision": None,
        "latestWindowId": None,
        "revisionCount": 0,
        "revisions": [],
        "indexObjectRef": {"sink": "hf", "uri": index_hf_uri} if index_hf_uri else None,
    }


def get_zkperf_stream_index_record(
    stream_index: dict[str, Any],
    *,
    stream_revision: str | None = None,
    latest: bool = False,
) -> dict[str, Any]:
    revisions = list(stream_index.get("revisions") or [])
    if latest:
        target = stream_index.get("latestRevision")
        if target is None:
            raise KeyError("stream index has no latestRevision")
        stream_revision = target
    if stream_revision is None:
        raise ValueError("must provide stream_revision or latest=True")
    for record in revisions:
        if record["streamRevision"] == stream_revision:
            return record
    raise KeyError(f"unknown streamRevision: {stream_revision}")


def update_zkperf_stream_index(
    *,
    existing_index: dict[str, Any] | None,
    stream_manifest: dict[str, Any],
    hf_receipt: dict[str, Any],
    index_hf_uri: str | None = None,
    retention_policy: dict[str, Any] | None = None,
) -> dict[str, Any]:
    index = existing_index or build_zkperf_stream_index(
        stream_id=stream_manifest["streamId"],
        index_hf_uri=index_hf_uri,
        created_at=stream_manifest.get("createdAtUtc"),
        retention_policy=retention_policy,
    )
    if retention_policy is not None:
        index["retentionPolicy"] = retention_policy
    revisions = list(index.get("revisions") or [])
    record = {
        "streamRevision": stream_manifest["streamRevision"],
        "createdAtUtc": stream_manifest["createdAtUtc"],
        "acknowledgedRevision": hf_receipt["acknowledgedRevision"],
        "windowCount": stream_manifest["windowCount"],
        "observationCount": stream_manifest.get("observationCount"),
        "observationIndex": list(stream_manifest.get("observationIndex") or []),
        "latestWindowId": stream_manifest["latestWindowId"],
        "sequenceRange": dict(stream_manifest["sequenceRange"]),
        "windows": [dict(window) for window in stream_manifest.get("windows", [])],
        "containerObjectRef": dict(stream_manifest["containerObjectRef"]),
        "verified": hf_receipt["verified"],
    }
    revisions = [item for item in revisions if item["streamRevision"] != record["streamRevision"]]
    revisions.append(record)
    revisions.sort(key=lambda item: item["sequenceRange"]["end"] or -1)
    revisions = apply_zkperf_stream_retention_policy(
        revisions,
        index.get("retentionPolicy"),
    )
    index["revisions"] = revisions
    index["revisionCount"] = len(revisions)
    latest_record = revisions[-1] if revisions else None
    index["latestRevision"] = latest_record["streamRevision"] if latest_record else None
    index["latestWindowId"] = latest_record["latestWindowId"] if latest_record else None
    index["observationCount"] = latest_record.get("observationCount") if latest_record else None
    index["observationIndex"] = list(latest_record.get("observationIndex") or []) if latest_record else []
    if index_hf_uri is not None:
        index["indexObjectRef"] = {"sink": "hf", "uri": index_hf_uri}
    return index


def apply_zkperf_stream_retention_policy(
    revisions: list[dict[str, Any]],
    retention_policy: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    if not retention_policy:
        return revisions
    mode = retention_policy.get("mode")
    if mode != "retain-latest-n":
        raise ValueError(f"unsupported retention mode: {mode}")
    max_revision_count = int(retention_policy.get("maxRevisionCount", len(revisions)))
    if max_revision_count <= 0:
        raise ValueError("maxRevisionCount must be positive")
    return revisions[-max_revision_count:]


__all__ = [
    "apply_zkperf_stream_retention_policy",
    "build_zkperf_stream_index",
    "build_zkperf_stream_latest",
    "get_zkperf_stream_index_record",
    "update_zkperf_stream_index",
    "write_zkperf_stream_publish_artifacts",
]
