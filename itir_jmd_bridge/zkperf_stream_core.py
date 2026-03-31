from __future__ import annotations

import io
import json
import tarfile
import time
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from typing import Any, Iterable


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
                        {"metric": "stream_window_count", "unit": "count", "value": stream_window_count},
                        {"metric": "stream_observation_count", "unit": "count", "value": stream_observation_count},
                        {"metric": "window_observation_count", "unit": "count", "value": window_observation_count},
                        {"metric": "window_sequence", "unit": "count", "value": window["sequence"]},
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


__all__ = [
    "build_zkperf_stream_bundle",
    "build_zkperf_stream_fixture_from_observations",
    "load_zkperf_observations",
    "load_zkperf_stream_fixture",
    "select_zkperf_stream_windows",
]
