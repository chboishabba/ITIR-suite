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
from .transport import NullTransportPlugin, TransportPlugin, publish_bundle

__all__ = [
    "NullTransportPlugin",
    "TransportPlugin",
    "build_runtime_bundle",
    "build_runtime_graph",
    "build_runtime_object",
    "build_runtime_receipt",
    "inspect_latest_pastes_with_prototype",
    "publish_bundle",
    "project_runtime_bundle_to_graph_input",
    "run_runtime_bundle_pipeline",
]
