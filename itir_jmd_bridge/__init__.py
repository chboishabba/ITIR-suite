"""Top-level JMD runtime bridge for ITIR-suite.

This package owns provider/runtime code for JMD-facing integration surfaces.
Consumer packages should depend on the normalized bridge contracts rather than
directly on pastebin, ERDFA, or transport-specific code.
"""

from .runtime import (
    build_runtime_bundle,
    build_runtime_graph,
    build_runtime_object,
    build_runtime_receipt,
    inspect_latest_pastes_with_prototype,
)
from .prototype_mdl import project_runtime_bundle_to_graph_input, run_runtime_bundle_pipeline
from .hf_rehearsal import (
    attach_object_refs_from_container,
    build_container_index_from_tar,
    extract_tar_member_bytes,
    fetch_payload_from_object_ref,
    load_erdfa_manifest_fixture,
    load_hf_container_fixture,
    resolve_container_member,
    resolve_selector_to_object_ref,
    resolve_selector_to_object_ref_payload,
    resolve_selector_to_remote_hf_payload,
    resolve_selector_to_remote_ipfs_payload,
    resolve_selector_to_local_member_payload,
    resolve_selector_to_container_member,
    resolve_selector_to_shard,
)
from .transport import NullTransportPlugin, TransportPlugin, publish_bundle
from .zkperf_stream import (
    build_zkperf_stream_bundle,
    build_zkperf_stream_index,
    build_zkperf_stream_latest,
    apply_zkperf_stream_retention_policy,
    get_zkperf_stream_index_record,
    load_zkperf_stream_fixture,
    load_remote_zkperf_stream_index,
    publish_zkperf_stream_index_to_hf,
    publish_zkperf_stream_to_hf,
    resolve_zkperf_stream_from_index_hf,
    resolve_remote_zkperf_stream_window,
    resolve_remote_zkperf_stream_windows,
    select_zkperf_stream_windows,
    update_zkperf_stream_index,
    write_zkperf_stream_publish_artifacts,
)
from .providers.hf import (
    download_hf_object_bytes,
    fetch_hf_object,
    parse_hf_uri,
    probe_hf_resolve_acknowledgement,
    upload_hf_file_with_ack,
)
from .providers.ipfs import (
    download_ipfs_object_bytes,
    fetch_ipfs_object,
    parse_ipfs_uri,
    probe_ipfs_gateway_acknowledgement,
    publish_ipfs_file_with_ack,
)
from .zkperf_viz import (
    build_zkperf_feature_spectrogram_payload,
    render_zkperf_feature_spectrogram,
    render_zkperf_pca_spectrogram,
)

__all__ = [
    "NullTransportPlugin",
    "TransportPlugin",
    "attach_object_refs_from_container",
    "build_runtime_bundle",
    "build_runtime_graph",
    "build_runtime_object",
    "build_runtime_receipt",
    "apply_zkperf_stream_retention_policy",
    "build_zkperf_stream_bundle",
    "build_zkperf_stream_index",
    "build_zkperf_stream_latest",
    "build_container_index_from_tar",
    "extract_tar_member_bytes",
    "download_hf_object_bytes",
    "download_ipfs_object_bytes",
    "fetch_hf_object",
    "fetch_ipfs_object",
    "fetch_payload_from_object_ref",
    "inspect_latest_pastes_with_prototype",
    "get_zkperf_stream_index_record",
    "load_erdfa_manifest_fixture",
    "load_hf_container_fixture",
    "load_zkperf_stream_fixture",
    "load_remote_zkperf_stream_index",
    "publish_bundle",
    "publish_zkperf_stream_index_to_hf",
    "publish_zkperf_stream_to_hf",
    "resolve_selector_to_object_ref",
    "resolve_selector_to_object_ref_payload",
    "resolve_selector_to_remote_hf_payload",
    "resolve_selector_to_remote_ipfs_payload",
    "project_runtime_bundle_to_graph_input",
    "probe_hf_resolve_acknowledgement",
    "resolve_container_member",
    "resolve_selector_to_local_member_payload",
    "resolve_selector_to_container_member",
    "resolve_selector_to_shard",
    "resolve_remote_zkperf_stream_window",
    "resolve_remote_zkperf_stream_windows",
    "resolve_zkperf_stream_from_index_hf",
    "select_zkperf_stream_windows",
    "update_zkperf_stream_index",
    "run_runtime_bundle_pipeline",
    "parse_hf_uri",
    "parse_ipfs_uri",
    "probe_ipfs_gateway_acknowledgement",
    "publish_ipfs_file_with_ack",
    "upload_hf_file_with_ack",
    "write_zkperf_stream_publish_artifacts",
    "build_zkperf_feature_spectrogram_payload",
    "render_zkperf_feature_spectrogram",
    "render_zkperf_pca_spectrogram",
]
