"""Read-only export adapters for Casey exchange channels."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .runtime_sqlite import (
    load_build,
    load_current_tree_id,
    load_file_versions,
    load_tree,
    load_workspace,
)


def _candidate_ids_for_tree(tree) -> set[str]:
    return {fv_id for state in tree.paths.values() for fv_id in state.candidates}


def export_casey_facts(
    *,
    db_path: Path,
    workspace_id: str,
    tree_id: str | None = None,
    build_id: str | None = None,
) -> dict[str, Any]:
    """Export Casey runtime state as `casey.facts.v1`.

    The export is read-only, preserves candidate multiplicity, and omits blob
    bytes from the payload.
    """

    resolved_tree_id = tree_id or load_current_tree_id(db_path=db_path)
    tree = load_tree(db_path=db_path, tree_id=resolved_tree_id)
    workspace = load_workspace(db_path=db_path, ws_id=workspace_id)
    file_versions = load_file_versions(
        db_path=db_path,
        fv_ids=_candidate_ids_for_tree(tree),
    )

    selected_by_path = dict(workspace.selection)
    paths: list[dict[str, Any]] = []
    for path in sorted(tree.paths):
        candidates = list(tree.paths[path].candidates)
        selected_fv_id = selected_by_path.get(path)
        if selected_fv_id not in candidates:
            selected_fv_id = None
        paths.append(
            {
                "path": path,
                "candidate_count": len(candidates),
                "selected_fv_id": selected_fv_id,
                "candidates": [
                    {
                        "fv_id": fv_id,
                        "blob_id": file_versions[fv_id].blob_id,
                        "author": file_versions[fv_id].author,
                        "created_at": file_versions[fv_id].created_at,
                        "base_fv_id": file_versions[fv_id].base_fv_id,
                        "summary": file_versions[fv_id].summary,
                    }
                    for fv_id in candidates
                ],
            }
        )

    build_payload: dict[str, Any] | None = None
    if build_id is not None:
        build = load_build(db_path=db_path, build_id=build_id)
        build_payload = {
            "build_id": build.build_id,
            "tree_id": build.tree_id,
            "created_at": build.created_at,
            "selection": [
                {"path": path, "selected_fv_id": fv_id}
                for path, fv_id in sorted(build.selection.items())
            ],
        }

    return {
        "casey_export_version": "casey.facts.v1",
        "tree_id": tree.tree_id,
        "workspace": {
            "ws_id": workspace.ws_id,
            "user": workspace.user,
            "head_tree_id": workspace.head,
            "policy": {
                "prefer_author": workspace.policy.prefer_author,
                "tie_break": workspace.policy.tie_break,
            },
            "selection": [
                {"path": path, "selected_fv_id": fv_id}
                for path, fv_id in sorted(workspace.selection.items())
            ],
        },
        "paths": paths,
        "build": build_payload,
    }
