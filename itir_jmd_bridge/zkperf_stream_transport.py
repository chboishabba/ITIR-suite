from __future__ import annotations

import json
import time
from hashlib import sha256
from pathlib import Path
from typing import Any, Callable, Iterable

from .providers.hf import download_hf_object_bytes, fetch_hf_object, upload_hf_file_with_ack
from .providers.ipfs import download_ipfs_object_bytes, fetch_ipfs_object
from .zkperf_stream_core import (
    build_zkperf_stream_bundle,
    load_zkperf_stream_fixture,
    select_zkperf_stream_windows,
)
from .zkperf_stream_index import (
    build_zkperf_stream_latest,
    get_zkperf_stream_index_record,
    update_zkperf_stream_index,
    write_zkperf_stream_publish_artifacts,
)
from .zkperf_stream_core import _elapsed_ms, _extract_member_from_tar_bytes


def publish_zkperf_stream_to_hf_impl(
    *,
    fixture_path: str | Path,
    hf_uri: str,
    commit_message: str | None,
    artifact_output_root: str | Path | None,
    index_hf_uri: str | None,
    retention_policy: dict[str, Any] | None,
    fixture_loader: Callable[[str | Path], dict[str, Any]],
    bundle_builder: Callable[[dict[str, Any]], dict[str, Any]],
    uploader: Callable[..., dict[str, Any]],
    latest_builder: Callable[[dict[str, Any], dict[str, Any]], dict[str, Any]],
    index_loader: Callable[[str], dict[str, Any] | None],
    index_updater: Callable[..., dict[str, Any]],
    index_publisher: Callable[..., dict[str, Any]],
    artifact_writer: Callable[..., dict[str, str]],
) -> dict[str, Any]:
    total_started = time.perf_counter()
    fixture = fixture_loader(fixture_path)
    stream_build_started = time.perf_counter()
    bundle = bundle_builder(fixture)
    stream_build_ms = _elapsed_ms(stream_build_started)
    tar_write_started = time.perf_counter()
    temp_tar = Path("/tmp") / f"{fixture['streamId']}-{fixture['streamRevision']}.tar"
    temp_tar.write_bytes(bundle["tarBytes"])
    tar_write_ms = _elapsed_ms(tar_write_started)
    hf_publish_started = time.perf_counter()
    receipt = uploader(
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
        "streamLatest": latest_builder(bundle["streamManifest"], receipt),
        "hfReceipt": receipt,
    }
    if index_hf_uri is not None:
        index_load_started = time.perf_counter()
        existing_index = index_loader(index_hf_uri)
        index_load_ms = _elapsed_ms(index_load_started)
        index_update_started = time.perf_counter()
        payload["streamIndex"] = index_updater(
            existing_index=existing_index,
            stream_manifest=bundle["streamManifest"],
            hf_receipt=receipt,
            index_hf_uri=index_hf_uri,
            retention_policy=retention_policy,
        )
        index_update_ms = _elapsed_ms(index_update_started)
        index_publish_started = time.perf_counter()
        payload["streamIndexReceipt"] = index_publisher(
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
        payload["artifactPaths"] = artifact_writer(
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


def load_remote_zkperf_stream_index_impl(
    *,
    index_hf_uri: str,
    revision: str | None,
    fetcher: Callable[..., dict[str, Any]],
) -> dict[str, Any] | None:
    try:
        fetched = fetcher(hf_uri=index_hf_uri, revision=revision)
    except Exception:
        return None
    text = fetched.get("text")
    if not text:
        return None
    return json.loads(text)


def load_remote_zkperf_stream_index_ipfs_impl(
    *,
    index_ipfs_uri: str,
    gateway_base_url: str | None,
    fetcher: Callable[..., dict[str, Any]],
) -> dict[str, Any] | None:
    try:
        fetched = fetcher(ipfs_uri=index_ipfs_uri, base_url=gateway_base_url)
    except Exception:
        return None
    text = fetched.get("text")
    if not text:
        return None
    return json.loads(text)


def publish_zkperf_stream_index_to_hf_impl(
    *,
    stream_index: dict[str, Any],
    index_hf_uri: str,
    commit_message: str | None,
    uploader: Callable[..., dict[str, Any]],
) -> dict[str, Any]:
    temp_index = Path("/tmp") / f"{stream_index['streamId']}-stream-index.json"
    temp_index.write_text(json.dumps(stream_index, indent=2, sort_keys=True), encoding="utf-8")
    return uploader(
        local_path=str(temp_index),
        hf_uri=index_hf_uri,
        commit_message=commit_message or f"Update zkperf stream index {stream_index['latestRevision']}",
    )


def resolve_zkperf_stream_from_index_hf_impl(
    *,
    fixture_path: str | Path,
    index_hf_uri: str,
    index_revision: str | None,
    latest: bool,
    stream_revision: str | None,
    window_id: str | None,
    sequence_start: int | None,
    sequence_end: int | None,
    window_ids: Iterable[str] | None,
    index_loader: Callable[..., dict[str, Any] | None],
    record_getter: Callable[..., dict[str, Any]],
    fixture_loader: Callable[[str | Path], dict[str, Any]],
    window_resolver: Callable[..., dict[str, Any]],
    windows_resolver: Callable[..., dict[str, Any]],
) -> dict[str, Any]:
    total_started = time.perf_counter()
    index_load_started = time.perf_counter()
    stream_index = index_loader(index_hf_uri, revision=index_revision)
    index_load_ms = _elapsed_ms(index_load_started)
    if stream_index is None:
        raise RuntimeError(f"unable to load stream index from {index_hf_uri}")
    record_started = time.perf_counter()
    record = record_getter(
        stream_index,
        stream_revision=stream_revision,
        latest=latest,
    )
    record_ms = _elapsed_ms(record_started)
    manifest_started = time.perf_counter()
    fixture = fixture_loader(fixture_path)
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
        payload = window_resolver(
            stream_manifest=stream_manifest,
            hf_revision=hf_revision,
            window_id=window_id,
        )
    else:
        payload = windows_resolver(
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


def resolve_zkperf_stream_from_index_ipfs_impl(
    *,
    fixture_path: str | Path,
    index_ipfs_uri: str,
    gateway_base_url: str | None,
    latest: bool,
    stream_revision: str | None,
    window_id: str | None,
    sequence_start: int | None,
    sequence_end: int | None,
    window_ids: Iterable[str] | None,
    index_loader: Callable[..., dict[str, Any] | None],
    record_getter: Callable[..., dict[str, Any]],
    fixture_loader: Callable[[str | Path], dict[str, Any]],
    window_resolver: Callable[..., dict[str, Any]],
    windows_resolver: Callable[..., dict[str, Any]],
) -> dict[str, Any]:
    total_started = time.perf_counter()
    index_load_started = time.perf_counter()
    stream_index = index_loader(index_ipfs_uri, gateway_base_url=gateway_base_url)
    index_load_ms = _elapsed_ms(index_load_started)
    if stream_index is None:
        raise RuntimeError(f"unable to load stream index from {index_ipfs_uri}")
    record_started = time.perf_counter()
    record = record_getter(
        stream_index,
        stream_revision=stream_revision,
        latest=latest,
    )
    record_ms = _elapsed_ms(record_started)
    manifest_started = time.perf_counter()
    fixture = fixture_loader(fixture_path)
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
        payload = window_resolver(
            stream_manifest=stream_manifest,
            window_id=window_id,
            gateway_base_url=gateway_base_url,
        )
    else:
        payload = windows_resolver(
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


def resolve_remote_zkperf_stream_window_impl(
    *,
    stream_manifest: dict[str, Any],
    hf_revision: str,
    window_id: str,
    fetcher: Callable[..., dict[str, Any]],
) -> dict[str, Any]:
    window = next((w for w in stream_manifest.get("windows", []) if w["windowId"] == window_id), None)
    if window is None:
        raise KeyError(f"unknown windowId: {window_id}")
    object_ref = stream_manifest["containerObjectRef"]
    fetched = fetcher(hf_uri=object_ref["uri"], revision=hf_revision)
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


def resolve_remote_zkperf_stream_window_ipfs_impl(
    *,
    stream_manifest: dict[str, Any],
    window_id: str,
    gateway_base_url: str | None,
    fetcher: Callable[..., dict[str, Any]],
) -> dict[str, Any]:
    window = next((w for w in stream_manifest.get("windows", []) if w["windowId"] == window_id), None)
    if window is None:
        raise KeyError(f"unknown windowId: {window_id}")
    object_ref = stream_manifest["containerObjectRef"]
    fetched = fetcher(ipfs_uri=object_ref["uri"], base_url=gateway_base_url)
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


def resolve_remote_zkperf_stream_windows_impl(
    *,
    stream_manifest: dict[str, Any],
    hf_revision: str,
    latest: bool,
    sequence_start: int | None,
    sequence_end: int | None,
    window_ids: Iterable[str] | None,
    selector: Callable[..., list[dict[str, Any]]],
    fetcher: Callable[..., dict[str, Any]],
) -> dict[str, Any]:
    selected = selector(
        stream_manifest,
        latest=latest,
        sequence_start=sequence_start,
        sequence_end=sequence_end,
        window_ids=window_ids,
    )
    object_ref = stream_manifest["containerObjectRef"]
    fetched = fetcher(hf_uri=object_ref["uri"], revision=hf_revision)
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


def resolve_remote_zkperf_stream_windows_ipfs_impl(
    *,
    stream_manifest: dict[str, Any],
    latest: bool,
    sequence_start: int | None,
    sequence_end: int | None,
    window_ids: Iterable[str] | None,
    gateway_base_url: str | None,
    selector: Callable[..., list[dict[str, Any]]],
    fetcher: Callable[..., dict[str, Any]],
) -> dict[str, Any]:
    selected = selector(
        stream_manifest,
        latest=latest,
        sequence_start=sequence_start,
        sequence_end=sequence_end,
        window_ids=window_ids,
    )
    object_ref = stream_manifest["containerObjectRef"]
    fetched = fetcher(ipfs_uri=object_ref["uri"], base_url=gateway_base_url)
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


def publish_zkperf_stream_to_hf(
    *,
    fixture_path: str | Path,
    hf_uri: str,
    commit_message: str | None = None,
    artifact_output_root: str | Path | None = None,
    index_hf_uri: str | None = None,
    retention_policy: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return publish_zkperf_stream_to_hf_impl(
        fixture_path=fixture_path,
        hf_uri=hf_uri,
        commit_message=commit_message,
        artifact_output_root=artifact_output_root,
        index_hf_uri=index_hf_uri,
        retention_policy=retention_policy,
        fixture_loader=load_zkperf_stream_fixture,
        bundle_builder=build_zkperf_stream_bundle,
        uploader=upload_hf_file_with_ack,
        latest_builder=build_zkperf_stream_latest,
        index_loader=load_remote_zkperf_stream_index,
        index_updater=update_zkperf_stream_index,
        index_publisher=publish_zkperf_stream_index_to_hf,
        artifact_writer=write_zkperf_stream_publish_artifacts,
    )


def load_remote_zkperf_stream_index(
    index_hf_uri: str,
    *,
    revision: str | None = None,
) -> dict[str, Any] | None:
    return load_remote_zkperf_stream_index_impl(
        index_hf_uri=index_hf_uri,
        revision=revision,
        fetcher=fetch_hf_object,
    )


def load_remote_zkperf_stream_index_ipfs(
    index_ipfs_uri: str,
    *,
    gateway_base_url: str | None = None,
) -> dict[str, Any] | None:
    return load_remote_zkperf_stream_index_ipfs_impl(
        index_ipfs_uri=index_ipfs_uri,
        gateway_base_url=gateway_base_url,
        fetcher=fetch_ipfs_object,
    )


def publish_zkperf_stream_index_to_hf(
    *,
    stream_index: dict[str, Any],
    index_hf_uri: str,
    commit_message: str | None = None,
) -> dict[str, Any]:
    return publish_zkperf_stream_index_to_hf_impl(
        stream_index=stream_index,
        index_hf_uri=index_hf_uri,
        commit_message=commit_message,
        uploader=upload_hf_file_with_ack,
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
    return resolve_zkperf_stream_from_index_hf_impl(
        fixture_path=fixture_path,
        index_hf_uri=index_hf_uri,
        index_revision=index_revision,
        latest=latest,
        stream_revision=stream_revision,
        window_id=window_id,
        sequence_start=sequence_start,
        sequence_end=sequence_end,
        window_ids=window_ids,
        index_loader=load_remote_zkperf_stream_index,
        record_getter=get_zkperf_stream_index_record,
        fixture_loader=load_zkperf_stream_fixture,
        window_resolver=resolve_remote_zkperf_stream_window,
        windows_resolver=resolve_remote_zkperf_stream_windows,
    )


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
    return resolve_zkperf_stream_from_index_ipfs_impl(
        fixture_path=fixture_path,
        index_ipfs_uri=index_ipfs_uri,
        gateway_base_url=gateway_base_url,
        latest=latest,
        stream_revision=stream_revision,
        window_id=window_id,
        sequence_start=sequence_start,
        sequence_end=sequence_end,
        window_ids=window_ids,
        index_loader=load_remote_zkperf_stream_index_ipfs,
        record_getter=get_zkperf_stream_index_record,
        fixture_loader=load_zkperf_stream_fixture,
        window_resolver=resolve_remote_zkperf_stream_window_ipfs,
        windows_resolver=resolve_remote_zkperf_stream_windows_ipfs,
    )


def resolve_remote_zkperf_stream_window(
    *,
    stream_manifest: dict[str, Any],
    hf_revision: str,
    window_id: str,
) -> dict[str, Any]:
    return resolve_remote_zkperf_stream_window_impl(
        stream_manifest=stream_manifest,
        hf_revision=hf_revision,
        window_id=window_id,
        fetcher=download_hf_object_bytes,
    )


def resolve_remote_zkperf_stream_window_ipfs(
    *,
    stream_manifest: dict[str, Any],
    window_id: str,
    gateway_base_url: str | None = None,
) -> dict[str, Any]:
    return resolve_remote_zkperf_stream_window_ipfs_impl(
        stream_manifest=stream_manifest,
        window_id=window_id,
        gateway_base_url=gateway_base_url,
        fetcher=download_ipfs_object_bytes,
    )


def resolve_remote_zkperf_stream_windows(
    *,
    stream_manifest: dict[str, Any],
    hf_revision: str,
    latest: bool = False,
    sequence_start: int | None = None,
    sequence_end: int | None = None,
    window_ids: Iterable[str] | None = None,
) -> dict[str, Any]:
    return resolve_remote_zkperf_stream_windows_impl(
        stream_manifest=stream_manifest,
        hf_revision=hf_revision,
        latest=latest,
        sequence_start=sequence_start,
        sequence_end=sequence_end,
        window_ids=window_ids,
        selector=select_zkperf_stream_windows,
        fetcher=download_hf_object_bytes,
    )


def resolve_remote_zkperf_stream_windows_ipfs(
    *,
    stream_manifest: dict[str, Any],
    latest: bool = False,
    sequence_start: int | None = None,
    sequence_end: int | None = None,
    window_ids: Iterable[str] | None = None,
    gateway_base_url: str | None = None,
) -> dict[str, Any]:
    return resolve_remote_zkperf_stream_windows_ipfs_impl(
        stream_manifest=stream_manifest,
        latest=latest,
        sequence_start=sequence_start,
        sequence_end=sequence_end,
        window_ids=window_ids,
        gateway_base_url=gateway_base_url,
        selector=select_zkperf_stream_windows,
        fetcher=download_ipfs_object_bytes,
    )


__all__ = [
    "load_remote_zkperf_stream_index",
    "load_remote_zkperf_stream_index_ipfs",
    "publish_zkperf_stream_index_to_hf",
    "publish_zkperf_stream_to_hf",
    "resolve_remote_zkperf_stream_window",
    "resolve_remote_zkperf_stream_window_ipfs",
    "resolve_remote_zkperf_stream_windows",
    "resolve_remote_zkperf_stream_windows_ipfs",
    "resolve_zkperf_stream_from_index_hf",
    "resolve_zkperf_stream_from_index_ipfs",
]
