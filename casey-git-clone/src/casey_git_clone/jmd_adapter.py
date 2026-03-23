"""Thin JMD runtime graph adapter for Casey.

This keeps JMD graph consumption outside Casey core runtime/storage logic by
exposing a read-only import preview payload only.
"""

from __future__ import annotations

from hashlib import sha256
from typing import Any


def build_casey_import_preview(graph_payload: dict[str, Any]) -> dict[str, Any]:
    generated_at = graph_payload.get("generated_at")
    paths = []
    for node in graph_payload.get("nodes", []):
        node_id = str(node["node_id"])
        fv_id = f"jmd-{sha256(node_id.encode('utf-8')).hexdigest()[:16]}"
        blob_id = str(node.get("cid") or sha256(node_id.encode("utf-8")).hexdigest()[:16])
        paths.append(
            {
                "path": f"jmd/{node_id}",
                "candidate_count": 1,
                "selected_fv_id": fv_id,
                "candidates": [
                    {
                        "fv_id": fv_id,
                        "blob_id": blob_id,
                        "author": "jmd_connector",
                        "created_at": generated_at,
                        "base_fv_id": None,
                        "summary": node.get("label"),
                        "features": {
                            "_version": "casey.features.v1",
                            "jmd.node_kind": node.get("kind"),
                            "jmd.ref": node.get("ref"),
                        },
                    }
                ],
            }
        )

    return {
        "casey_import_version": "casey.jmd.graph.v1",
        "source_graph_id": graph_payload["graph_id"],
        "source_object_id": graph_payload["source_object_id"],
        "generated_at": generated_at,
        "paths": paths,
        "dependencies": list(graph_payload.get("edges", [])),
    }
