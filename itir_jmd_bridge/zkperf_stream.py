from __future__ import annotations

import io
import json
import tarfile
import time
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from typing import Any, Iterable

from .providers.hf import fetch_hf_object, upload_hf_file_with_ack, download_hf_object_bytes
from .providers.ipfs import fetch_ipfs_object, download_ipfs_object_bytes


def load_zkperf_stream_fixture(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_zkperf_observations(path: str | Path) -> list[dict[str, Any]]:
    raw = Path(path).read_text(encoding="utf-8")
    stripped = raw.strip()
    if not stripped:
        return []
    if stripped.startswith("["):
        payload = json.loads(stripped)
        if not isinstance(payload, list):
            raise ValueError("expected a JSON array of observations")
        return [dict(item) for item in payload]
    if stripped.startswith("{"):
        payload = json.loads(stripped)
        observations = payload.get("observations") if isinstance(payload, dict) else None
        if isinstance(observations, list):
            return [dict(item) for item in observations]
        if isinstance(payload, dict) and "zkperf_observation_id" in payload:
            return [dict(payload)]
        raise ValueError("expected a single observation object or an object with an observations list")
    observations = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        observations.append(dict(json.loads(line)))
    return observations


def build_zkperf_stream_fixture_from_observations(
    observations: list[dict[str, Any]],
    *,
    stream_id: str | None = None,
    stream_revision: str | None = None,
    created_at_utc: str | None = None,
    max_observations_per_window: int | None = None,
) -> dict[str, Any]:
    if not observations:
        raise ValueError("at least one observation is required")
    for observation in observations:
        _validate_zkperf_observation(observation)
    created_at = created_at_utc or _derive_created_at_utc(observations)
    revision = stream_revision or _default_stream_revision(created_at)
    resolved_stream_id = stream_id or _derive_stream_id(observations)
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for observation in observations:
        group_key = (
            str(observation.get("run_id") or "unknown-run"),
            str(observation.get("trace_id") or observation["zkperf_observation_id"]),
        )
        grouped.setdefault(group_key, []).append(observation)
    ordered_groups = sorted(
        grouped.items(),
        key=lambda entry: (
            min(_parse_utc(item["asserted_at"]) for item in entry[1]),
            entry[0][0],
            entry[0][1],
        ),
    )
    chunk_size = max_observations_per_window or 0
    sequence = 1
    windows: list[dict[str, Any]] = []
    for (run_id, trace_id), group in ordered_groups:
        ordered = sorted(group, key=lambda item: (_parse_utc(item["asserted_at"]), item["zkperf_observation_id"]))
        chunks = [ordered]
        if chunk_size > 0:
            chunks = [ordered[index:index + chunk_size] for index in range(0, len(ordered), chunk_size)]
        for chunk in chunks:
            windows.append(
                {
                    "windowId": f"window-{sequence:04d}",
                    "sequence": sequence,
                    "runId": run_id,
                    "traceId": trace_id,
                    "observationIds": [item["zkperf_observation_id"] for item in chunk],
                    "startedAtUtc": min(item["asserted_at"] for item in chunk),
                    "endedAtUtc": max(item["asserted_at"] for item in chunk),
                    "payload": {"observations": chunk},
                }
            )
            sequence += 1
    return {
        "contractVersion": "zkperf-stream/v1",
        "streamId": resolved_stream_id,
        "streamRevision": revision,
        "streamKind": "zkperf-observation-stream",
        "windowingMode": "trace-id-grouped",
        "createdAtUtc": created_at,
        "windows": windows,
        "containerObjectRef": None,
    }


def build_zkperf_stream_bundle(stream_manifest: dict[str, Any]) -> dict[str, Any]:
    stream_id = stream_manifest["streamId"]
    stream_revision = stream_manifest["streamRevision"]
    stream_window_count = len(stream_manifest.get("windows", []))
    stream_observation_count = 0
    observation_index: list[dict[str, Any]] = []
    windows = []
    tar_bytes_io = io.BytesIO()
    with tarfile.open(fileobj=tar_bytes_io, mode="w") as handle:
        for window in stream_manifest.get("windows", []):
            observations = list(window.get("payload", {}).get("observations", []))
            window_observation_count = len(observations)
            stream_observation_count += window_observation_count
            for observation in observations:
                observation_index.append(
                    {
                        "observationId": observation.get("zkperf_observation_id"),
                        "runId": observation.get("run_id"),
                        "traceId": observation.get("trace_id"),
                        "assertedAtUtc": observation.get("asserted_at"),
                        "hash": observation.get("hash"),
                        "sourceRef": observation.get("source_ref"),
                        "status": observation.get("status"),
                    }
                )
                _append_zkperf_metrics(
                    observation,
                    [
                        {
                            "metric": "stream_window_count",
                            "unit": "count",
                            "value": stream_window_count,
                        },
                        {
                            "metric": "stream_observation_count",
                            "unit": "count",
                            "value": stream_observation_count,
                        },
                        {
                            "metric": "window_observation_count",
                            "unit": "count",
                            "value": window_observation_count,
                        },
                        {
                            "metric": "window_sequence",
                            "unit": "count",
                            "value": window["sequence"],
                        },
                    ],
                )
            payload_bytes = _canonical_json_bytes(window["payload"])
            member_path = f"windows/{window['windowId']}.json"
            info = tarfile.TarInfo(name=member_path)
            info.size = len(payload_bytes)
            handle.addfile(info, io.BytesIO(payload_bytes))
            windows.append(
                {
                    "windowId": window["windowId"],
                    "sequence": window["sequence"],
                    "runId": window["runId"],
                    "traceId": window["traceId"],
                    "observationIds": list(window.get("observationIds") or []),
                    "memberPath": member_path,
                    "contentDigest": f"sha256:{sha256(payload_bytes).hexdigest()}",
                    "sizeBytes": len(payload_bytes),
                    "startedAtUtc": window["startedAtUtc"],
                    "endedAtUtc": window["endedAtUtc"],
                }
            )
    tar_bytes = tar_bytes_io.getvalue()
    manifest = {
        "contractVersion": stream_manifest["contractVersion"],
        "streamId": stream_id,
        "streamRevision": stream_revision,
            "streamKind": stream_manifest["streamKind"],
            "windowingMode": stream_manifest["windowingMode"],
            "createdAtUtc": stream_manifest["createdAtUtc"],
            "windowCount": len(windows),
            "observationCount": stream_observation_count,
            "observationIndex": observation_index,
            "latestWindowId": windows[-1]["windowId"] if windows else None,
            "sequenceRange": {
                "start": windows[0]["sequence"] if windows else None,
                "end": windows[-1]["sequence"] if windows else None,
            },
        "windows": windows,
        "containerObjectRef": {
            "sink": "hf",
            "uri": f"hf://datasets/local/{stream_id}/{stream_revision}/zkperf-stream.tar",
            "sizeBytes": len(tar_bytes),
            "contentDigest": f"sha256:{sha256(tar_bytes).hexdigest()}",
        },
    }
    return {
        "streamManifest": manifest,
        "tarBytes": tar_bytes,
        "tarDigest": sha256(tar_bytes).hexdigest(),
    }


def publish_zkperf_stream_to_hf(
    *,
    fixture_path: str | Path,
    hf_uri: str,
    commit_message: str | None = None,
    artifact_output_root: str | Path | None = None,
    index_hf_uri: str | None = None,
    retention_policy: dict[str, Any] | None = None,
) -> dict[str, Any]:
    total_started = time.perf_counter()
    fixture = load_zkperf_stream_fixture(fixture_path)
    stream_build_started = time.perf_counter()
    bundle = build_zkperf_stream_bundle(fixture)
    stream_build_ms = _elapsed_ms(stream_build_started)
    tar_write_started = time.perf_counter()
    temp_tar = Path("/tmp") / f"{fixture['streamId']}-{fixture['streamRevision']}.tar"
    temp_tar.write_bytes(bundle["tarBytes"])
    tar_write_ms = _elapsed_ms(tar_write_started)
    hf_publish_started = time.perf_counter()
    receipt = upload_hf_file_with_ack(
        local_path=str(temp_tar),
        hf_uri=hf_uri,
        commit_message=commit_message or f"Publish zkperf stream {fixture['streamRevision']}",
    )
    hf_publish_ms = _elapsed_ms(hf_publish_started)
    bundle["streamManifest"]["containerObjectRef"] = {
        "sink": "hf",
        "uri": hf_uri,
        "sizeBytes": receipt["localSizeBytes"],
        "contentDigest": f"sha256:{receipt['localSha256']}",
    }
    payload = {
        "streamManifest": bundle["streamManifest"],
        "streamLatest": build_zkperf_stream_latest(bundle["streamManifest"], receipt),
        "hfReceipt": receipt,
    }
    if index_hf_uri is not None:
        index_load_started = time.perf_counter()
        existing_index = load_remote_zkperf_stream_index(index_hf_uri)
        index_load_ms = _elapsed_ms(index_load_started)
        index_update_started = time.perf_counter()
        payload["streamIndex"] = update_zkperf_stream_index(
            existing_index=existing_index,
            stream_manifest=bundle["streamManifest"],
            hf_receipt=receipt,
            index_hf_uri=index_hf_uri,
            retention_policy=retention_policy,
        )
        index_update_ms = _elapsed_ms(index_update_started)
        index_publish_started = time.perf_counter()
        payload["streamIndexReceipt"] = publish_zkperf_stream_index_to_hf(
            stream_index=payload["streamIndex"],
            index_hf_uri=index_hf_uri,
            commit_message=f"Update zkperf stream index {fixture['streamRevision']}",
        )
        index_publish_ms = _elapsed_ms(index_publish_started)
    else:
        index_load_ms = None
        index_update_ms = None
        index_publish_ms = None
    if artifact_output_root is not None:
        artifact_write_started = time.perf_counter()
        payload["artifactPaths"] = write_zkperf_stream_publish_artifacts(
            output_root=artifact_output_root,
            publish_payload=payload,
        )
        artifact_write_ms = _elapsed_ms(artifact_write_started)
    else:
        artifact_write_ms = None
    payload["timings"] = {
        "streamBuildMs": stream_build_ms,
        "tarWriteMs": tar_write_ms,
        "hfPublishMs": hf_publish_ms,
        "indexLoadMs": index_load_ms,
        "indexUpdateMs": index_update_ms,
        "indexPublishMs": index_publish_ms,
        "artifactWriteMs": artifact_write_ms,
        "totalMs": _elapsed_ms(total_started),
    }
    return payload


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
        "indexObjectRef": {
            "sink": "hf",
            "uri": index_hf_uri,
        } if index_hf_uri else None,
    }


def load_remote_zkperf_stream_index(
    index_hf_uri: str,
    *,
    revision: str | None = None,
) -> dict[str, Any] | None:
    try:
        fetched = fetch_hf_object(hf_uri=index_hf_uri, revision=revision)
    except Exception:
        return None
    text = fetched.get("text")
    if not text:
        return None
    return json.loads(text)


def load_remote_zkperf_stream_index_ipfs(
    index_ipfs_uri: str,
    *,
    gateway_base_url: str | None = None,
) -> dict[str, Any] | None:
    try:
        fetched = fetch_ipfs_object(ipfs_uri=index_ipfs_uri, base_url=gateway_base_url)
    except Exception:
        return None
    text = fetched.get("text")
    if not text:
        return None
    return json.loads(text)


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
    latest = revisions[-1] if revisions else None
    index["latestRevision"] = latest["streamRevision"] if latest else None
    index["latestWindowId"] = latest["latestWindowId"] if latest else None
    index["observationCount"] = latest.get("observationCount") if latest else None
    index["observationIndex"] = list(latest.get("observationIndex") or []) if latest else []
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


def publish_zkperf_stream_index_to_hf(
    *,
    stream_index: dict[str, Any],
    index_hf_uri: str,
    commit_message: str | None = None,
) -> dict[str, Any]:
    temp_index = Path("/tmp") / f"{stream_index['streamId']}-stream-index.json"
    temp_index.write_text(json.dumps(stream_index, indent=2, sort_keys=True), encoding="utf-8")
    return upload_hf_file_with_ack(
        local_path=str(temp_index),
        hf_uri=index_hf_uri,
        commit_message=commit_message or f"Update zkperf stream index {stream_index['latestRevision']}",
    )


def resolve_zkperf_stream_from_index_hf(
    *,
    fixture_path: str | Path,
    index_hf_uri: str,
    index_revision: str | None = None,
    latest: bool = False,
    stream_revision: str | None = None,
    window_id: str | None = None,
    sequence_start: int | None = None,
    sequence_end: int | None = None,
    window_ids: Iterable[str] | None = None,
) -> dict[str, Any]:
    total_started = time.perf_counter()
    index_load_started = time.perf_counter()
    stream_index = load_remote_zkperf_stream_index(index_hf_uri, revision=index_revision)
    index_load_ms = _elapsed_ms(index_load_started)
    if stream_index is None:
        raise RuntimeError(f"unable to load stream index from {index_hf_uri}")
    record_started = time.perf_counter()
    record = get_zkperf_stream_index_record(
        stream_index,
        stream_revision=stream_revision,
        latest=latest,
    )
    record_ms = _elapsed_ms(record_started)
    manifest_started = time.perf_counter()
    fixture = load_zkperf_stream_fixture(fixture_path)
    stream_manifest = {
        "contractVersion": fixture["contractVersion"],
        "streamId": fixture["streamId"],
        "streamRevision": record["streamRevision"],
        "streamKind": fixture["streamKind"],
        "windowingMode": fixture["windowingMode"],
        "createdAtUtc": record.get("createdAtUtc") or fixture.get("createdAtUtc"),
        "windowCount": record["windowCount"],
        "latestWindowId": record["latestWindowId"],
        "sequenceRange": dict(record["sequenceRange"]),
        "windows": [dict(window) for window in record.get("windows", [])],
        "containerObjectRef": dict(record["containerObjectRef"]),
    }
    manifest_ms = _elapsed_ms(manifest_started)
    hf_revision = record["acknowledgedRevision"]
    fetch_started = time.perf_counter()
    if window_id is not None:
        payload = resolve_remote_zkperf_stream_window(
            stream_manifest=stream_manifest,
            hf_revision=hf_revision,
            window_id=window_id,
        )
    else:
        payload = resolve_remote_zkperf_stream_windows(
            stream_manifest=stream_manifest,
            hf_revision=hf_revision,
            latest=latest and stream_revision is None and sequence_start is None and sequence_end is None and not window_ids,
            sequence_start=sequence_start,
            sequence_end=sequence_end,
            window_ids=window_ids,
        )
    fetch_ms = _elapsed_ms(fetch_started)
    payload["streamIndex"] = {
        "indexUri": index_hf_uri,
        "indexRevision": index_revision,
        "resolvedStreamRevision": record["streamRevision"],
        "acknowledgedRevision": hf_revision,
    }
    payload["timings"] = {
        "indexLoadMs": index_load_ms,
        "indexRecordMs": record_ms,
        "manifestMaterializeMs": manifest_ms,
        "fetchAndExtractMs": fetch_ms,
        "totalMs": _elapsed_ms(total_started),
    }
    return payload


def resolve_zkperf_stream_from_index_ipfs(
    *,
    fixture_path: str | Path,
    index_ipfs_uri: str,
    gateway_base_url: str | None = None,
    latest: bool = False,
    stream_revision: str | None = None,
    window_id: str | None = None,
    sequence_start: int | None = None,
    sequence_end: int | None = None,
    window_ids: Iterable[str] | None = None,
) -> dict[str, Any]:
    total_started = time.perf_counter()
    index_load_started = time.perf_counter()
    stream_index = load_remote_zkperf_stream_index_ipfs(
        index_ipfs_uri,
        gateway_base_url=gateway_base_url,
    )
    index_load_ms = _elapsed_ms(index_load_started)
    if stream_index is None:
        raise RuntimeError(f"unable to load stream index from {index_ipfs_uri}")
    record_started = time.perf_counter()
    record = get_zkperf_stream_index_record(
        stream_index,
        stream_revision=stream_revision,
        latest=latest,
    )
    record_ms = _elapsed_ms(record_started)
    manifest_started = time.perf_counter()
    fixture = load_zkperf_stream_fixture(fixture_path)
    stream_manifest = {
        "contractVersion": fixture["contractVersion"],
        "streamId": fixture["streamId"],
        "streamRevision": record["streamRevision"],
        "streamKind": fixture["streamKind"],
        "windowingMode": fixture["windowingMode"],
        "createdAtUtc": record.get("createdAtUtc") or fixture.get("createdAtUtc"),
        "windowCount": record["windowCount"],
        "latestWindowId": record["latestWindowId"],
        "sequenceRange": dict(record["sequenceRange"]),
        "windows": [dict(window) for window in record.get("windows", [])],
        "containerObjectRef": dict(record["containerObjectRef"]),
    }
    manifest_ms = _elapsed_ms(manifest_started)
    fetch_started = time.perf_counter()
    if window_id is not None:
        payload = resolve_remote_zkperf_stream_window_ipfs(
            stream_manifest=stream_manifest,
            window_id=window_id,
            gateway_base_url=gateway_base_url,
        )
    else:
        payload = resolve_remote_zkperf_stream_windows_ipfs(
            stream_manifest=stream_manifest,
            latest=latest and stream_revision is None and sequence_start is None and sequence_end is None and not window_ids,
            sequence_start=sequence_start,
            sequence_end=sequence_end,
            window_ids=window_ids,
            gateway_base_url=gateway_base_url,
        )
    fetch_ms = _elapsed_ms(fetch_started)
    payload["streamIndex"] = {
        "indexUri": index_ipfs_uri,
        "gatewayBaseUrl": gateway_base_url,
        "resolvedStreamRevision": record["streamRevision"],
    }
    payload["timings"] = {
        "indexLoadMs": index_load_ms,
        "indexRecordMs": record_ms,
        "manifestMaterializeMs": manifest_ms,
        "fetchAndExtractMs": fetch_ms,
        "totalMs": _elapsed_ms(total_started),
    }
    return payload


def resolve_remote_zkperf_stream_window(
    *,
    stream_manifest: dict[str, Any],
    hf_revision: str,
    window_id: str,
) -> dict[str, Any]:
    window = next((w for w in stream_manifest.get("windows", []) if w["windowId"] == window_id), None)
    if window is None:
        raise KeyError(f"unknown windowId: {window_id}")
    object_ref = stream_manifest["containerObjectRef"]
    fetched = download_hf_object_bytes(hf_uri=object_ref["uri"], revision=hf_revision)
    payload = _extract_member_from_tar_bytes(fetched["bytes"], window["memberPath"])
    return {
        "streamId": stream_manifest["streamId"],
        "streamRevision": stream_manifest["streamRevision"],
        "window": window,
        "fetch": {
            "sink": "hf",
            "uri": object_ref["uri"],
            "revision": hf_revision,
            "metadata": fetched["metadata"],
        },
        "payload": {
            "sizeBytes": len(payload),
            "sha256": sha256(payload).hexdigest(),
            "json": json.loads(payload.decode("utf-8")),
        },
    }


def resolve_remote_zkperf_stream_window_ipfs(
    *,
    stream_manifest: dict[str, Any],
    window_id: str,
    gateway_base_url: str | None = None,
) -> dict[str, Any]:
    window = next((w for w in stream_manifest.get("windows", []) if w["windowId"] == window_id), None)
    if window is None:
        raise KeyError(f"unknown windowId: {window_id}")
    object_ref = stream_manifest["containerObjectRef"]
    fetched = download_ipfs_object_bytes(
        ipfs_uri=object_ref["uri"],
        base_url=gateway_base_url,
    )
    payload = _extract_member_from_tar_bytes(fetched["bytes"], window["memberPath"])
    return {
        "streamId": stream_manifest["streamId"],
        "streamRevision": stream_manifest["streamRevision"],
        "window": window,
        "fetch": {
            "sink": "ipfs",
            "uri": object_ref["uri"],
            "metadata": fetched["metadata"],
        },
        "payload": {
            "sizeBytes": len(payload),
            "sha256": sha256(payload).hexdigest(),
            "json": json.loads(payload.decode("utf-8")),
        },
    }


def resolve_remote_zkperf_stream_windows(
    *,
    stream_manifest: dict[str, Any],
    hf_revision: str,
    latest: bool = False,
    sequence_start: int | None = None,
    sequence_end: int | None = None,
    window_ids: Iterable[str] | None = None,
) -> dict[str, Any]:
    selected = select_zkperf_stream_windows(
        stream_manifest,
        latest=latest,
        sequence_start=sequence_start,
        sequence_end=sequence_end,
        window_ids=window_ids,
    )
    object_ref = stream_manifest["containerObjectRef"]
    fetched = download_hf_object_bytes(hf_uri=object_ref["uri"], revision=hf_revision)
    windows = []
    for window in selected:
        payload = _extract_member_from_tar_bytes(fetched["bytes"], window["memberPath"])
        windows.append(
            {
                "window": window,
                "payload": {
                    "sizeBytes": len(payload),
                    "sha256": sha256(payload).hexdigest(),
                    "json": json.loads(payload.decode("utf-8")),
                },
            }
        )
    return {
        "streamId": stream_manifest["streamId"],
        "streamRevision": stream_manifest["streamRevision"],
        "selection": {
            "latest": latest,
            "sequenceStart": sequence_start,
            "sequenceEnd": sequence_end,
            "windowIds": list(window_ids or []),
            "selectedWindowIds": [window["windowId"] for window in selected],
        },
        "fetch": {
            "sink": "hf",
            "uri": object_ref["uri"],
            "revision": hf_revision,
            "metadata": fetched["metadata"],
        },
        "windows": windows,
    }


def resolve_remote_zkperf_stream_windows_ipfs(
    *,
    stream_manifest: dict[str, Any],
    latest: bool = False,
    sequence_start: int | None = None,
    sequence_end: int | None = None,
    window_ids: Iterable[str] | None = None,
    gateway_base_url: str | None = None,
) -> dict[str, Any]:
    selected = select_zkperf_stream_windows(
        stream_manifest,
        latest=latest,
        sequence_start=sequence_start,
        sequence_end=sequence_end,
        window_ids=window_ids,
    )
    object_ref = stream_manifest["containerObjectRef"]
    fetched = download_ipfs_object_bytes(
        ipfs_uri=object_ref["uri"],
        base_url=gateway_base_url,
    )
    windows = []
    for window in selected:
        payload = _extract_member_from_tar_bytes(fetched["bytes"], window["memberPath"])
        windows.append(
            {
                "window": window,
                "payload": {
                    "sizeBytes": len(payload),
                    "sha256": sha256(payload).hexdigest(),
                    "json": json.loads(payload.decode("utf-8")),
                },
            }
        )
    return {
        "streamId": stream_manifest["streamId"],
        "streamRevision": stream_manifest["streamRevision"],
        "selection": {
            "latest": latest,
            "sequenceStart": sequence_start,
            "sequenceEnd": sequence_end,
            "windowIds": list(window_ids or []),
            "selectedWindowIds": [window["windowId"] for window in selected],
        },
        "fetch": {
            "sink": "ipfs",
            "uri": object_ref["uri"],
            "metadata": fetched["metadata"],
        },
        "windows": windows,
    }


def select_zkperf_stream_windows(
    stream_manifest: dict[str, Any],
    *,
    latest: bool = False,
    sequence_start: int | None = None,
    sequence_end: int | None = None,
    window_ids: Iterable[str] | None = None,
) -> list[dict[str, Any]]:
    windows = list(stream_manifest.get("windows", []))
    if latest:
        if not windows:
            return []
        return [max(windows, key=lambda item: item["sequence"])]
    if window_ids:
        wanted = set(window_ids)
        selected = [window for window in windows if window["windowId"] in wanted]
        missing = wanted.difference(window["windowId"] for window in selected)
        if missing:
            raise KeyError(f"unknown windowIds: {sorted(missing)}")
        return selected
    if sequence_start is not None or sequence_end is not None:
        low = sequence_start if sequence_start is not None else min(window["sequence"] for window in windows)
        high = sequence_end if sequence_end is not None else max(window["sequence"] for window in windows)
        return [window for window in windows if low <= window["sequence"] <= high]
    raise ValueError("must select latest, a sequence range, or explicit window ids")


def _canonical_json_bytes(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _elapsed_ms(started_at: float) -> int:
    return int(round((time.perf_counter() - started_at) * 1000))


def _extract_member_from_tar_bytes(data: bytes, member_path: str) -> bytes:
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:*") as handle:
        member = handle.getmember(member_path)
        extracted = handle.extractfile(member)
        if extracted is None:
            raise KeyError(f"unable to extract member: {member_path}")
        return extracted.read()


def _validate_zkperf_observation(observation: dict[str, Any]) -> None:
    required = [
        "zkperf_observation_id",
        "trace_id",
        "run_id",
        "asserted_at",
        "source_ref",
        "status",
        "metrics",
        "trace_refs",
        "proof_refs",
        "hash",
    ]
    missing = [field for field in required if field not in observation or observation[field] in (None, "")]
    if missing:
        raise ValueError(f"observation {observation.get('zkperf_observation_id', '<unknown>')} missing required fields: {missing}")
    if not isinstance(observation.get("metrics"), list):
        raise ValueError("metrics must be a list")
    if not isinstance(observation.get("trace_refs"), list):
        raise ValueError("trace_refs must be a list")
    if not isinstance(observation.get("proof_refs"), list):
        raise ValueError("proof_refs must be a list")
    if not observation.get("trace_refs") and not observation.get("proof_refs"):
        raise ValueError("at least one of trace_refs or proof_refs must be present")
    _parse_utc(str(observation["asserted_at"]))


def _append_zkperf_metrics(observation: dict[str, Any], metrics: Iterable[dict[str, Any]]) -> None:
    existing = observation.get("metrics")
    if existing is None:
        existing = []
        observation["metrics"] = existing
    if not isinstance(existing, list):
        raise ValueError("metrics must be a list")
    has_metric = any(isinstance(item, dict) and "metric" in item for item in existing)
    has_name = any(isinstance(item, dict) and "name" in item for item in existing)
    known = set()
    if has_metric or not has_name:
        known = {item.get("metric") for item in existing if isinstance(item, dict)}
    elif has_name:
        known = {item.get("name") for item in existing if isinstance(item, dict)}
    for metric in metrics:
        name = metric.get("metric") if isinstance(metric, dict) else None
        if name and name in known:
            continue
        if has_name and not has_metric:
            value = metric.get("value") if isinstance(metric, dict) else None
            kind = "integer" if isinstance(value, int) else "number"
            existing.append({"name": name, "kind": kind, "value": value})
            continue
        existing.append(metric)


def _parse_utc(value: str) -> datetime:
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    return datetime.fromisoformat(value).astimezone(UTC)


def _derive_created_at_utc(observations: list[dict[str, Any]]) -> str:
    latest = max(_parse_utc(item["asserted_at"]) for item in observations)
    return latest.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _default_stream_revision(created_at_utc: str) -> str:
    stamp = _parse_utc(created_at_utc).strftime("%Y%m%dT%H%M%SZ")
    return f"rev-{stamp}"


def _derive_stream_id(observations: list[dict[str, Any]]) -> str:
    run_ids = sorted({str(item.get("run_id") or "unknown-run") for item in observations})
    if len(run_ids) == 1:
        suffix = _slugify(run_ids[0])
    else:
        suffix = "multi-run"
    return f"zkperf-stream-{suffix}"


def _slugify(value: str) -> str:
    chars = []
    for char in value.lower():
        chars.append(char if char.isalnum() else "-")
    slug = "".join(chars).strip("-")
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug or "stream"
