from __future__ import annotations

import json
from pathlib import Path

from itir_jmd_bridge.zkperf_stream_core import build_zkperf_stream_bundle, load_zkperf_stream_fixture
from itir_jmd_bridge.zkperf_stream_transport import (
    load_remote_zkperf_stream_index_impl,
    load_remote_zkperf_stream_index_ipfs_impl,
    resolve_remote_zkperf_stream_window_impl,
    resolve_remote_zkperf_stream_window_ipfs_impl,
    resolve_remote_zkperf_stream_windows_impl,
    resolve_remote_zkperf_stream_windows_ipfs_impl,
    resolve_zkperf_stream_from_index_hf_impl,
    resolve_zkperf_stream_from_index_ipfs_impl,
)

FIXTURE = Path("docs/planning/jmd_fixtures/zkperf_stream_v1.example.json")


def _bundle_payload() -> tuple[dict[str, object], dict[str, object]]:
    fixture = load_zkperf_stream_fixture(FIXTURE)
    bundle = build_zkperf_stream_bundle(fixture)
    return fixture, bundle


def test_remote_index_loaders_parse_text_and_handle_empty_results() -> None:
    index = {"contractVersion": "zkperf-stream-index/v1", "streamId": "demo"}

    hf = load_remote_zkperf_stream_index_impl(
        index_hf_uri="hf://datasets/example/repo/index.json",
        revision="rev-demo",
        fetcher=lambda **kwargs: {"text": json.dumps(index)},
    )
    ipfs = load_remote_zkperf_stream_index_ipfs_impl(
        index_ipfs_uri="ipfs://demo/index.json",
        gateway_base_url="https://gateway.example",
        fetcher=lambda **kwargs: {"text": json.dumps(index)},
    )
    assert hf == index
    assert ipfs == index
    assert (
        load_remote_zkperf_stream_index_impl(
            index_hf_uri="hf://datasets/example/repo/index.json",
            revision=None,
            fetcher=lambda **kwargs: {"text": ""},
        )
        is None
    )


def test_remote_window_resolvers_extract_tar_members() -> None:
    fixture, bundle = _bundle_payload()
    manifest = bundle["streamManifest"]
    fetcher = lambda **kwargs: {  # noqa: E731
        "bytes": bundle["tarBytes"],
        "metadata": {"revision": kwargs.get("revision"), "base_url": kwargs.get("base_url")},
    }

    one = resolve_remote_zkperf_stream_window_impl(
        stream_manifest=manifest,
        hf_revision="rev-demo",
        window_id="window-0002",
        fetcher=fetcher,
    )
    many = resolve_remote_zkperf_stream_windows_impl(
        stream_manifest=manifest,
        hf_revision="rev-demo",
        latest=True,
        sequence_start=None,
        sequence_end=None,
        window_ids=None,
        selector=lambda stream_manifest, **kwargs: [stream_manifest["windows"][-1]],
        fetcher=fetcher,
    )
    one_ipfs = resolve_remote_zkperf_stream_window_ipfs_impl(
        stream_manifest=manifest,
        window_id="window-0001",
        gateway_base_url="https://gateway.example",
        fetcher=fetcher,
    )
    many_ipfs = resolve_remote_zkperf_stream_windows_ipfs_impl(
        stream_manifest=manifest,
        latest=False,
        sequence_start=1,
        sequence_end=2,
        window_ids=None,
        gateway_base_url="https://gateway.example",
        selector=lambda stream_manifest, **kwargs: list(stream_manifest["windows"]),
        fetcher=fetcher,
    )

    assert one["window"]["windowId"] == "window-0002"
    assert one["payload"]["json"]["observations"]
    assert many["selection"]["selectedWindowIds"] == ["window-0002"]
    assert one_ipfs["fetch"]["sink"] == "ipfs"
    assert one_ipfs["payload"]["json"]["observations"][0]["metrics"]
    assert [item["window"]["windowId"] for item in many_ipfs["windows"]] == [
        "window-0001",
        "window-0002",
    ]


def test_resolve_from_index_impls_compose_manifest_and_timings() -> None:
    fixture, bundle = _bundle_payload()
    manifest = bundle["streamManifest"]
    record = {
        "streamRevision": manifest["streamRevision"],
        "createdAtUtc": manifest["createdAtUtc"],
        "acknowledgedRevision": "rev-demo",
        "windowCount": manifest["windowCount"],
        "latestWindowId": manifest["latestWindowId"],
        "sequenceRange": dict(manifest["sequenceRange"]),
        "windows": [dict(window) for window in manifest["windows"]],
        "containerObjectRef": dict(manifest["containerObjectRef"]),
    }

    hf = resolve_zkperf_stream_from_index_hf_impl(
        fixture_path=FIXTURE,
        index_hf_uri="hf://datasets/example/repo/index.json",
        index_revision="rev-index",
        latest=True,
        stream_revision=None,
        window_id="window-0002",
        sequence_start=None,
        sequence_end=None,
        window_ids=None,
        index_loader=lambda index_hf_uri, **kwargs: {"latestRevision": manifest["streamRevision"]},
        record_getter=lambda stream_index, **kwargs: record,
        fixture_loader=lambda path: fixture,
        window_resolver=lambda **kwargs: {"window": {"windowId": kwargs["window_id"]}},
        windows_resolver=lambda **kwargs: {"windows": [{"window": {"windowId": "window-0002"}}]},
    )
    ipfs = resolve_zkperf_stream_from_index_ipfs_impl(
        fixture_path=FIXTURE,
        index_ipfs_uri="ipfs://demo/index.json",
        gateway_base_url="https://gateway.example",
        latest=False,
        stream_revision=None,
        window_id=None,
        sequence_start=1,
        sequence_end=2,
        window_ids=None,
        index_loader=lambda index_ipfs_uri, **kwargs: {"latestRevision": manifest["streamRevision"]},
        record_getter=lambda stream_index, **kwargs: record,
        fixture_loader=lambda path: fixture,
        window_resolver=lambda **kwargs: {"window": {"windowId": kwargs["window_id"]}},
        windows_resolver=lambda **kwargs: {"windows": [{"window": {"windowId": "window-0001"}}]},
    )

    assert hf["streamIndex"]["indexUri"].startswith("hf://")
    assert hf["streamIndex"]["acknowledgedRevision"] == "rev-demo"
    assert hf["window"]["windowId"] == "window-0002"
    assert hf["timings"]["totalMs"] >= 0
    assert ipfs["streamIndex"]["gatewayBaseUrl"] == "https://gateway.example"
    assert ipfs["windows"][0]["window"]["windowId"] == "window-0001"
    assert ipfs["timings"]["totalMs"] >= 0
