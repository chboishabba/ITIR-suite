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
    extract_tar_member_bytes,
    load_erdfa_manifest_fixture,
    load_hf_container_fixture,
    resolve_container_member,
    resolve_selector_to_local_member_payload,
    resolve_selector_to_container_member,
    resolve_selector_to_shard,
)
from .transport import NullTransportPlugin, TransportPlugin, publish_bundle

__all__ = [
    "NullTransportPlugin",
    "TransportPlugin",
    "build_runtime_bundle",
    "build_runtime_graph",
    "build_runtime_object",
    "build_runtime_receipt",
    "extract_tar_member_bytes",
    "inspect_latest_pastes_with_prototype",
    "load_erdfa_manifest_fixture",
    "load_hf_container_fixture",
    "publish_bundle",
    "project_runtime_bundle_to_graph_input",
    "resolve_container_member",
    "resolve_selector_to_local_member_payload",
    "resolve_selector_to_container_member",
    "resolve_selector_to_shard",
    "run_runtime_bundle_pipeline",
]
