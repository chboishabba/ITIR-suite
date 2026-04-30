"""Compatibility facade for the split zkperf stream modules.

New generic callers should prefer:
- zkperf_stream_core for fixture, observation, bundle, and window selection
- zkperf_stream_index for latest, index, retention, and artifact writes
- zkperf_stream_transport for HF/IPFS publish and resolve adapters

This module stays in place so existing ITIR scripts and tests do not need a
same-turn import migration.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

from .providers.hf import download_hf_object_bytes, fetch_hf_object, upload_hf_file_with_ack
from .providers.ipfs import download_ipfs_object_bytes, fetch_ipfs_object
from .zkperf_stream_core import (
    build_zkperf_stream_bundle,
    build_zkperf_stream_fixture_from_observations,
    load_zkperf_observations,
    load_zkperf_stream_fixture,
    select_zkperf_stream_windows,
)
from .zkperf_stream_index import (
    apply_zkperf_stream_retention_policy,
    build_zkperf_stream_index,
    build_zkperf_stream_latest,
    get_zkperf_stream_index_record,
    update_zkperf_stream_index,
    write_zkperf_stream_publish_artifacts,
)
from .zkperf_stream_transport import (
    load_remote_zkperf_stream_index_impl,
    load_remote_zkperf_stream_index_ipfs_impl,
    publish_zkperf_stream_index_to_hf_impl,
    publish_zkperf_stream_to_hf_impl,
    resolve_remote_zkperf_stream_window_impl,
    resolve_remote_zkperf_stream_window_ipfs_impl,
    resolve_remote_zkperf_stream_windows_impl,
    resolve_remote_zkperf_stream_windows_ipfs_impl,
    resolve_zkperf_stream_from_index_hf_impl,
    resolve_zkperf_stream_from_index_ipfs_impl,
)


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
    "apply_zkperf_stream_retention_policy",
    "build_zkperf_stream_bundle",
    "build_zkperf_stream_fixture_from_observations",
    "build_zkperf_stream_index",
    "build_zkperf_stream_latest",
    "get_zkperf_stream_index_record",
    "load_remote_zkperf_stream_index",
    "load_remote_zkperf_stream_index_ipfs",
    "load_zkperf_observations",
    "load_zkperf_stream_fixture",
    "publish_zkperf_stream_index_to_hf",
    "publish_zkperf_stream_to_hf",
    "resolve_remote_zkperf_stream_window",
    "resolve_remote_zkperf_stream_window_ipfs",
    "resolve_remote_zkperf_stream_windows",
    "resolve_remote_zkperf_stream_windows_ipfs",
    "resolve_zkperf_stream_from_index_hf",
    "resolve_zkperf_stream_from_index_ipfs",
    "select_zkperf_stream_windows",
    "update_zkperf_stream_index",
    "write_zkperf_stream_publish_artifacts",
]
