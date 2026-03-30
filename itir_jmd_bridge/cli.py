from __future__ import annotations

import argparse
import json
from pathlib import Path

from .hf_rehearsal import (
    attach_object_refs_from_container,
    build_container_index_from_tar,
    extract_tar_member_bytes,
    load_erdfa_manifest_fixture,
    load_hf_container_fixture,
    resolve_container_member,
    resolve_selector_to_object_ref_payload,
    resolve_selector_to_local_member_payload,
    resolve_selector_to_remote_ipfs_payload,
    resolve_selector_to_remote_hf_payload,
    resolve_selector_to_container_member,
)
from .providers.pastebin import discover_host_capabilities
from .providers.hf import fetch_hf_object, probe_hf_resolve_acknowledgement, upload_hf_file_with_ack
from .providers.ipfs import fetch_ipfs_object, probe_ipfs_gateway_acknowledgement, publish_ipfs_file_with_ack
from .runtime import build_runtime_bundle, build_runtime_graph, ingest_latest_pastes, inspect_latest_pastes_with_prototype
from .zkperf_stream import (
    build_zkperf_stream_bundle,
    get_zkperf_stream_index_record,
    load_zkperf_stream_fixture,
    load_remote_zkperf_stream_index,
    publish_zkperf_stream_to_hf,
    resolve_zkperf_stream_from_index_hf,
    resolve_remote_zkperf_stream_windows,
    resolve_remote_zkperf_stream_window,
)


def _write_json(payload: dict, path: Path | None) -> None:
    rendered = json.dumps(payload, indent=2, sort_keys=True)
    if path is None:
        print(rendered)
    else:
        path.write_text(rendered + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="JMD runtime bridge CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    resolve = sub.add_parser("resolve-bundle", help="Resolve a paste/ERDFA source into runtime object/graph/receipt payloads")
    resolve.add_argument("--paste-url")
    resolve.add_argument("--base-url")
    resolve.add_argument("--paste-id")
    resolve.add_argument("--erdfa-descriptor", type=Path)
    resolve.add_argument("--erdfa-tar", type=Path)
    resolve.add_argument("--object-output", type=Path)
    resolve.add_argument("--graph-output", type=Path)
    resolve.add_argument("--receipt-output", type=Path)
    resolve.add_argument("--verify-ipfs", action="store_true")

    graph = sub.add_parser("build-graph", help="Build a runtime graph from a resolved runtime object")
    graph.add_argument("--runtime-object", type=Path, required=True)
    graph.add_argument("--output", type=Path)

    latest = sub.add_parser("ingest-latest", help="Resolve the latest N browse-page pastes into runtime bundles")
    latest.add_argument("--base-url", required=True)
    latest.add_argument("--limit", type=int, default=5)
    latest.add_argument("--concurrency", type=int, default=2)
    latest.add_argument("--request-spacing-ms", type=int, default=400)
    latest.add_argument("--verify-ipfs", action="store_true")
    latest.add_argument("--ipfs-gateway-base-url")
    latest.add_argument("--allow-ipfs-cli-fallback", action="store_true")
    latest.add_argument("--output", type=Path)
    latest.add_argument("--strict", action="store_true")

    prototype_latest = sub.add_parser("inspect-latest-prototype", help="Resolve the latest N browse-page pastes and summarize prototype normalization/proof output")
    prototype_latest.add_argument("--base-url", required=True)
    prototype_latest.add_argument("--limit", type=int, default=5)
    prototype_latest.add_argument("--concurrency", type=int, default=2)
    prototype_latest.add_argument("--request-spacing-ms", type=int, default=400)
    prototype_latest.add_argument("--verify-ipfs", action="store_true")
    prototype_latest.add_argument("--ipfs-gateway-base-url")
    prototype_latest.add_argument("--allow-ipfs-cli-fallback", action="store_true")
    prototype_latest.add_argument("--output", type=Path)
    prototype_latest.add_argument("--strict", action="store_true")

    discover = sub.add_parser("discover-capabilities", help="Probe documented and observed host surfaces")
    discover.add_argument("--base-url", required=True)
    discover.add_argument("--output", type=Path)

    rehearse_hf = sub.add_parser(
        "rehearse-hf-container",
        help="Resolve one shardId through the local HF container fixture",
    )
    rehearse_hf.add_argument("--fixture", type=Path, required=True)
    rehearse_hf.add_argument("--shard-id", required=True)
    rehearse_hf.add_argument("--output", type=Path)

    rehearse_selector = sub.add_parser(
        "rehearse-selector-fetch",
        help="Resolve selectors through the promoted-manifest fixture and optional HF container fixture",
    )
    rehearse_selector.add_argument("--manifest-fixture", type=Path, required=True)
    rehearse_selector.add_argument("--container-fixture", type=Path, help="If omitted, default memberPath inference is used")
    rehearse_selector.add_argument(
        "--selector",
        action="append",
        dest="selectors",
        required=True,
        help="Selector key such as route-name=tenant or route-lang=en",
    )
    rehearse_selector.add_argument("--output", type=Path)

    rehearse_tar = sub.add_parser(
        "rehearse-local-tar-extract",
        help="Extract one member from a local tar/tar.zst by member path",
    )
    rehearse_tar.add_argument("--tar-path", type=Path, required=True)
    rehearse_tar.add_argument("--member-path", required=True)
    rehearse_tar.add_argument("--output", type=Path)

    rehearse_selector_tar = sub.add_parser(
        "rehearse-selector-local-tar-fetch",
        help="Resolve selectors through fixtures and extract the matching member from a local tar",
    )
    rehearse_selector_tar.add_argument("--manifest-fixture", type=Path, required=True)
    rehearse_selector_tar.add_argument("--container-fixture", type=Path, help="If omitted, memberPath is inferred (shardId.cbor or payload/shardId.cbor)")
    rehearse_selector_tar.add_argument("--tar-path", type=Path, required=True)
    rehearse_selector_tar.add_argument(
        "--selector",
        action="append",
        dest="selectors",
        required=True,
        help="Selector key such as route-name=tenant or route-lang=en",
    )
    rehearse_selector_tar.add_argument("--output", type=Path)

    probe_hf = sub.add_parser(
        "probe-hf-ack",
        help="Probe a public HF resolve URL and record acknowledgement headers",
    )
    probe_hf.add_argument("--hf-uri", required=True)
    probe_hf.add_argument("--output", type=Path)

    fetch_hf = sub.add_parser(
        "fetch-hf-object",
        help="Fetch a public HF object and report digest/read-back metadata",
    )
    fetch_hf.add_argument("--hf-uri", required=True)
    fetch_hf.add_argument("--revision")
    fetch_hf.add_argument("--output", type=Path)

    publish_hf = sub.add_parser(
        "publish-hf-ack",
        help="Upload a local file to HF and emit a verified acknowledgement receipt",
    )
    publish_hf.add_argument("--local-path", type=Path, required=True)
    publish_hf.add_argument("--hf-uri", required=True)
    publish_hf.add_argument("--commit-message")
    publish_hf.add_argument("--output", type=Path)

    probe_ipfs = sub.add_parser(
        "probe-ipfs-ack",
        help="Probe an IPFS gateway URL and record acknowledgement headers",
    )
    probe_ipfs.add_argument("--ipfs-uri", required=True)
    probe_ipfs.add_argument("--gateway-base-url")
    probe_ipfs.add_argument("--output", type=Path)

    fetch_ipfs = sub.add_parser(
        "fetch-ipfs-object",
        help="Fetch an IPFS object through a gateway and report digest/read-back metadata",
    )
    fetch_ipfs.add_argument("--ipfs-uri", required=True)
    fetch_ipfs.add_argument("--gateway-base-url")
    fetch_ipfs.add_argument("--output", type=Path)

    publish_ipfs = sub.add_parser(
        "publish-ipfs-ack",
        help="Add a local file to IPFS and emit a bounded acknowledgement receipt",
    )
    publish_ipfs.add_argument("--local-path", type=Path, required=True)
    publish_ipfs.add_argument("--api-base-url", default="http://127.0.0.1:5001")
    publish_ipfs.add_argument("--no-pin", action="store_true")
    publish_ipfs.add_argument("--output", type=Path)

    rehearse_real_bundle = sub.add_parser(
        "rehearse-real-local-bundle",
        help="Use a real promoted manifest and tar bundle to resolve selector -> objectRef -> payload",
    )
    rehearse_real_bundle.add_argument("--manifest-path", type=Path, required=True)
    rehearse_real_bundle.add_argument("--tar-path", type=Path, required=True)
    rehearse_real_bundle.add_argument("--hf-uri", default="hf://datasets/local/erdfa-demo/container.tar")
    rehearse_real_bundle.add_argument("--ipfs-uri", default="ipfs://bafy-local-erdfa-demo")
    rehearse_real_bundle.add_argument(
        "--selector",
        action="append",
        dest="selectors",
        required=True,
        help="Selector key such as direct-shard=heading-1",
    )
    rehearse_real_bundle.add_argument("--prefer-sink", action="append", dest="preferred_sinks")
    rehearse_real_bundle.add_argument("--output", type=Path)

    rehearse_remote_hf = sub.add_parser(
        "rehearse-remote-hf-bundle",
        help="Resolve selector -> HF objectRef -> remote fetch -> payload using a real tar-backed manifest",
    )
    rehearse_remote_hf.add_argument("--manifest-path", type=Path, required=True)
    rehearse_remote_hf.add_argument("--tar-path", type=Path, required=True)
    rehearse_remote_hf.add_argument("--hf-uri", required=True)
    rehearse_remote_hf.add_argument("--hf-revision", required=True)
    rehearse_remote_hf.add_argument(
        "--selector",
        action="append",
        dest="selectors",
        required=True,
        help="Selector key such as direct-shard=heading-1",
    )
    rehearse_remote_hf.add_argument("--output", type=Path)

    rehearse_remote_ipfs = sub.add_parser(
        "rehearse-remote-ipfs-bundle",
        help="Resolve selector -> IPFS objectRef -> remote fetch -> payload using a real tar-backed manifest",
    )
    rehearse_remote_ipfs.add_argument("--manifest-path", type=Path, required=True)
    rehearse_remote_ipfs.add_argument("--tar-path", type=Path, required=True)
    rehearse_remote_ipfs.add_argument("--ipfs-uri", required=True)
    rehearse_remote_ipfs.add_argument("--gateway-base-url")
    rehearse_remote_ipfs.add_argument(
        "--selector",
        action="append",
        dest="selectors",
        required=True,
        help="Selector key such as direct-shard=heading-1",
    )
    rehearse_remote_ipfs.add_argument("--output", type=Path)

    build_zkperf = sub.add_parser(
        "build-zkperf-stream",
        help="Build a bounded zkperf stream tar/manifest bundle from a fixture",
    )
    build_zkperf.add_argument("--fixture", type=Path, required=True)
    build_zkperf.add_argument("--output", type=Path)

    publish_zkperf = sub.add_parser(
        "publish-zkperf-stream-hf",
        help="Publish a bounded zkperf stream bundle to HF and emit the acknowledged receipt",
    )
    publish_zkperf.add_argument("--fixture", type=Path, required=True)
    publish_zkperf.add_argument("--hf-uri", required=True)
    publish_zkperf.add_argument("--index-hf-uri")
    publish_zkperf.add_argument("--retain-latest-n", type=int)
    publish_zkperf.add_argument("--commit-message")
    publish_zkperf.add_argument("--artifact-output-root", type=Path)
    publish_zkperf.add_argument("--output", type=Path)

    resolve_zkperf = sub.add_parser(
        "resolve-zkperf-stream-window-hf",
        help="Resolve one zkperf stream window from a remote HF tar by acknowledged revision",
    )
    resolve_zkperf.add_argument("--fixture", type=Path, required=True)
    resolve_zkperf.add_argument("--hf-uri", required=True)
    resolve_zkperf.add_argument("--revision", required=True)
    resolve_zkperf.add_argument("--window-id", required=True)
    resolve_zkperf.add_argument("--output", type=Path)

    resolve_zkperf_range = sub.add_parser(
        "resolve-zkperf-stream-range-hf",
        help="Resolve the latest or a sequence range of zkperf stream windows from a remote HF tar",
    )
    resolve_zkperf_range.add_argument("--fixture", type=Path, required=True)
    resolve_zkperf_range.add_argument("--hf-uri", required=True)
    resolve_zkperf_range.add_argument("--revision", required=True)
    resolve_zkperf_range.add_argument("--latest", action="store_true")
    resolve_zkperf_range.add_argument("--sequence-start", type=int)
    resolve_zkperf_range.add_argument("--sequence-end", type=int)
    resolve_zkperf_range.add_argument("--window-id", action="append", dest="window_ids")
    resolve_zkperf_range.add_argument("--output", type=Path)

    resolve_zkperf_index = sub.add_parser(
        "resolve-zkperf-stream-from-index-hf",
        help="Resolve zkperf stream windows from the remote HF index object",
    )
    resolve_zkperf_index.add_argument("--fixture", type=Path, required=True)
    resolve_zkperf_index.add_argument("--index-hf-uri", required=True)
    resolve_zkperf_index.add_argument("--index-revision")
    resolve_zkperf_index.add_argument("--latest", action="store_true")
    resolve_zkperf_index.add_argument("--stream-revision")
    resolve_zkperf_index.add_argument("--window-id")
    resolve_zkperf_index.add_argument("--sequence-start", type=int)
    resolve_zkperf_index.add_argument("--sequence-end", type=int)
    resolve_zkperf_index.add_argument("--select-window-id", action="append", dest="window_ids")
    resolve_zkperf_index.add_argument("--output", type=Path)

    args = parser.parse_args(argv)

    if args.command == "resolve-bundle":
        bundle = build_runtime_bundle(
            paste_url=args.paste_url,
            base_url=args.base_url,
            paste_id=args.paste_id,
            erdfa_descriptor=args.erdfa_descriptor,
            erdfa_tar_path=args.erdfa_tar,
            verify_ipfs=bool(args.verify_ipfs),
        )
        _write_json(bundle["runtime_object"], args.object_output)
        _write_json(bundle["runtime_graph"], args.graph_output)
        _write_json(bundle["runtime_receipt"], args.receipt_output)
        return 0

    if args.command == "ingest-latest":
        payload = ingest_latest_pastes(
            base_url=args.base_url,
            limit=args.limit,
            concurrency=args.concurrency,
            request_spacing_seconds=max(args.request_spacing_ms, 0) / 1000.0,
            verify_ipfs=bool(args.verify_ipfs),
            ipfs_gateway_base_url=args.ipfs_gateway_base_url,
            allow_ipfs_cli_fallback=bool(args.allow_ipfs_cli_fallback),
        )
        _write_json(payload, args.output)
        return 1 if args.strict and payload["failure_count"] else 0

    if args.command == "inspect-latest-prototype":
        payload = inspect_latest_pastes_with_prototype(
            base_url=args.base_url,
            limit=args.limit,
            concurrency=args.concurrency,
            request_spacing_seconds=max(args.request_spacing_ms, 0) / 1000.0,
            verify_ipfs=bool(args.verify_ipfs),
            ipfs_gateway_base_url=args.ipfs_gateway_base_url,
            allow_ipfs_cli_fallback=bool(args.allow_ipfs_cli_fallback),
        )
        _write_json(payload, args.output)
        return 1 if args.strict and payload["failure_count"] else 0

    if args.command == "discover-capabilities":
        payload = discover_host_capabilities(base_url=args.base_url)
        _write_json(payload, args.output)
        return 0

    if args.command == "rehearse-hf-container":
        fixture = load_hf_container_fixture(args.fixture)
        payload = resolve_container_member(fixture, shard_id=args.shard_id)
        _write_json(payload, args.output)
        return 0

    if args.command == "rehearse-selector-fetch":
        manifest = load_erdfa_manifest_fixture(args.manifest_fixture)
        container_fixture = load_hf_container_fixture(args.container_fixture) if args.container_fixture else None
        payload = resolve_selector_to_container_member(
            manifest,
            container_fixture,
            selectors=list(args.selectors),
        )
        _write_json(payload, args.output)
        return 0

    if args.command == "rehearse-local-tar-extract":
        payload = {
            "memberPath": args.member_path,
            "payload": {
                "sizeBytes": len(extract_tar_member_bytes(args.tar_path, member_path=args.member_path)),
            },
        }
        _write_json(payload, args.output)
        return 0

    if args.command == "rehearse-selector-local-tar-fetch":
        manifest = load_erdfa_manifest_fixture(args.manifest_fixture)
        container_fixture = load_hf_container_fixture(args.container_fixture) if args.container_fixture else None
        payload = resolve_selector_to_local_member_payload(
            manifest,
            container_fixture,
            selectors=list(args.selectors),
            tar_path=args.tar_path,
        )
        _write_json(payload, args.output)
        return 0

    if args.command == "rehearse-real-local-bundle":
        manifest = load_erdfa_manifest_fixture(args.manifest_path)
        file_uri = f"file://{args.tar_path.resolve()}".replace(" ", "%20")
        container_index = build_container_index_from_tar(
            manifest,
            tar_path=args.tar_path,
            container_object_ref={
                "sink": "file",
                "uri": file_uri,
                "sizeBytes": args.tar_path.stat().st_size,
                "contentDigest": "sha256:pending",
            },
        )
        manifested = attach_object_refs_from_container(
            manifest,
            container_index,
            object_refs=[
                {"sink": "file", "uri": file_uri},
                {"sink": "hf", "uri": args.hf_uri},
                {"sink": "ipfs", "uri": args.ipfs_uri},
            ],
        )
        payload = resolve_selector_to_object_ref_payload(
            manifested,
            selectors=list(args.selectors),
            preferred_sinks=list(args.preferred_sinks) if args.preferred_sinks else None,
            hf_uri_map={args.hf_uri: str(args.tar_path)},
            ipfs_uri_map={args.ipfs_uri: str(args.tar_path)},
        )
        _write_json(payload, args.output)
        return 0

    if args.command == "rehearse-remote-hf-bundle":
        manifest = load_erdfa_manifest_fixture(args.manifest_path)
        container_index = build_container_index_from_tar(
            manifest,
            tar_path=args.tar_path,
            container_object_ref={
                "sink": "hf",
                "uri": args.hf_uri,
                "sizeBytes": args.tar_path.stat().st_size,
                "contentDigest": "sha256:pending",
            },
        )
        manifested = attach_object_refs_from_container(
            manifest,
            container_index,
            object_refs=[{"sink": "hf", "uri": args.hf_uri}],
        )
        payload = resolve_selector_to_remote_hf_payload(
            manifested,
            selectors=list(args.selectors),
            hf_revision=args.hf_revision,
        )
        _write_json(payload, args.output)
        return 0

    if args.command == "rehearse-remote-ipfs-bundle":
        manifest = load_erdfa_manifest_fixture(args.manifest_path)
        container_index = build_container_index_from_tar(
            manifest,
            tar_path=args.tar_path,
            container_object_ref={
                "sink": "ipfs",
                "uri": args.ipfs_uri,
                "sizeBytes": args.tar_path.stat().st_size,
                "contentDigest": "sha256:pending",
            },
        )
        manifested = attach_object_refs_from_container(
            manifest,
            container_index,
            object_refs=[{"sink": "ipfs", "uri": args.ipfs_uri}],
        )
        payload = resolve_selector_to_remote_ipfs_payload(
            manifested,
            selectors=list(args.selectors),
            gateway_base_url=args.gateway_base_url,
        )
        _write_json(payload, args.output)
        return 0

    if args.command == "probe-hf-ack":
        payload = probe_hf_resolve_acknowledgement(hf_uri=args.hf_uri)
        _write_json(payload, args.output)
        return 0

    if args.command == "fetch-hf-object":
        payload = fetch_hf_object(hf_uri=args.hf_uri, revision=args.revision)
        _write_json(payload, args.output)
        return 0

    if args.command == "publish-hf-ack":
        payload = upload_hf_file_with_ack(
            local_path=str(args.local_path),
            hf_uri=args.hf_uri,
            commit_message=args.commit_message,
        )
        _write_json(payload, args.output)
        return 0

    if args.command == "probe-ipfs-ack":
        payload = probe_ipfs_gateway_acknowledgement(
            ipfs_uri=args.ipfs_uri,
            base_url=args.gateway_base_url,
        )
        _write_json(payload, args.output)
        return 0

    if args.command == "fetch-ipfs-object":
        payload = fetch_ipfs_object(
            ipfs_uri=args.ipfs_uri,
            base_url=args.gateway_base_url,
        )
        _write_json(payload, args.output)
        return 0

    if args.command == "publish-ipfs-ack":
        payload = publish_ipfs_file_with_ack(
            local_path=str(args.local_path),
            api_base_url=args.api_base_url,
            pin=not args.no_pin,
        )
        _write_json(payload, args.output)
        return 0

    if args.command == "build-zkperf-stream":
        fixture = load_zkperf_stream_fixture(args.fixture)
        bundle = build_zkperf_stream_bundle(fixture)
        payload = {
            "streamManifest": bundle["streamManifest"],
            "tarDigest": bundle["tarDigest"],
            "tarSizeBytes": len(bundle["tarBytes"]),
        }
        _write_json(payload, args.output)
        return 0

    if args.command == "publish-zkperf-stream-hf":
        payload = publish_zkperf_stream_to_hf(
            fixture_path=args.fixture,
            hf_uri=args.hf_uri,
            index_hf_uri=args.index_hf_uri,
            retention_policy=(
                {
                    "policyVersion": "zkperf-retention/v1",
                    "mode": "retain-latest-n",
                    "maxRevisionCount": args.retain_latest_n,
                }
                if args.retain_latest_n
                else None
            ),
            commit_message=args.commit_message,
            artifact_output_root=args.artifact_output_root,
        )
        _write_json(payload, args.output)
        return 0

    if args.command == "resolve-zkperf-stream-window-hf":
        fixture = load_zkperf_stream_fixture(args.fixture)
        bundle = build_zkperf_stream_bundle(fixture)
        bundle["streamManifest"]["containerObjectRef"] = {
            "sink": "hf",
            "uri": args.hf_uri,
            "sizeBytes": bundle["streamManifest"]["containerObjectRef"]["sizeBytes"],
            "contentDigest": bundle["streamManifest"]["containerObjectRef"]["contentDigest"],
        }
        payload = resolve_remote_zkperf_stream_window(
            stream_manifest=bundle["streamManifest"],
            hf_revision=args.revision,
            window_id=args.window_id,
        )
        _write_json(payload, args.output)
        return 0

    if args.command == "resolve-zkperf-stream-range-hf":
        fixture = load_zkperf_stream_fixture(args.fixture)
        bundle = build_zkperf_stream_bundle(fixture)
        bundle["streamManifest"]["containerObjectRef"] = {
            "sink": "hf",
            "uri": args.hf_uri,
            "sizeBytes": bundle["streamManifest"]["containerObjectRef"]["sizeBytes"],
            "contentDigest": bundle["streamManifest"]["containerObjectRef"]["contentDigest"],
        }
        payload = resolve_remote_zkperf_stream_windows(
            stream_manifest=bundle["streamManifest"],
            hf_revision=args.revision,
            latest=args.latest,
            sequence_start=args.sequence_start,
            sequence_end=args.sequence_end,
            window_ids=args.window_ids,
        )
        _write_json(payload, args.output)
        return 0

    if args.command == "resolve-zkperf-stream-from-index-hf":
        payload = resolve_zkperf_stream_from_index_hf(
            fixture_path=args.fixture,
            index_hf_uri=args.index_hf_uri,
            index_revision=args.index_revision,
            latest=args.latest,
            stream_revision=args.stream_revision,
            window_id=args.window_id,
            sequence_start=args.sequence_start,
            sequence_end=args.sequence_end,
            window_ids=args.window_ids,
        )
        _write_json(payload, args.output)
        return 0

    payload = json.loads(args.runtime_object.read_text(encoding="utf-8"))
    _write_json(build_runtime_graph(payload), args.output)
    return 0
