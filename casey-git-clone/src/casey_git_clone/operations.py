"""Core superposition operations: publish, sync, collapse, build snapshot."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Mapping

from .models import (
    Blob,
    BuildView,
    FileVersion,
    PathState,
    TreeState,
    WorkspaceView,
    stable_hash,
    utc_now_iso,
)


def _parse_iso(ts: str) -> datetime:
    try:
        return datetime.fromisoformat(ts)
    except ValueError:
        return datetime.min


def _choose_by_policy(
    candidates: list[str],
    *,
    file_versions: Mapping[str, FileVersion],
    prefer_author: str | None,
    tie_break: str,
) -> str:
    pool = list(candidates)
    if prefer_author:
        preferred = [cid for cid in pool if file_versions.get(cid) and file_versions[cid].author == prefer_author]
        if preferred:
            pool = preferred

    if tie_break == "stable_hash":
        return sorted(pool)[0]

    if tie_break == "newest":
        return max(pool, key=lambda cid: _parse_iso(file_versions.get(cid, FileVersion(cid, "", "", "", None, None)).created_at))

    if tie_break == "oldest":
        return min(pool, key=lambda cid: _parse_iso(file_versions.get(cid, FileVersion(cid, "", "", "", None, None)).created_at))

    raise ValueError(f"Unsupported tie_break policy: {tie_break}")


@dataclass
class PublishResult:
    """Artifacts generated while publishing edits into tree state."""

    tree_state: TreeState
    blobs: Dict[str, Blob]
    file_versions: Dict[str, FileVersion]


def publish_edits(
    *,
    tree_state: TreeState,
    workspace: WorkspaceView,
    edits: Mapping[str, bytes | str],
    author: str,
    created_at: str | None = None,
) -> PublishResult:
    """Apply edits without blocking on divergence.

    If a path was a singleton in the workspace base, it is replaced.
    If divergence already exists, the new candidate is appended.
    """

    next_paths = {
        path: PathState(path=state.path, candidates=list(state.candidates))
        for path, state in tree_state.paths.items()
    }
    blobs: Dict[str, Blob] = {}
    versions: Dict[str, FileVersion] = {}
    created = created_at or utc_now_iso()

    for path, content in edits.items():
        raw = content.encode("utf-8") if isinstance(content, str) else content
        blob = Blob.from_bytes(raw)
        base_fv = workspace.selection.get(path)
        fv = FileVersion.create(
            blob_id=blob.blob_id,
            author=author,
            created_at=created,
            base_fv_id=base_fv,
        )
        blobs[blob.blob_id] = blob
        versions[fv.fv_id] = fv

        current = next_paths.get(path)
        if current is None:
            next_paths[path] = PathState(path=path, candidates=[fv.fv_id])
            continue

        replace_singleton = len(current.candidates) == 1 and (
            base_fv is None or current.candidates[0] == base_fv
        )
        if replace_singleton:
            next_paths[path] = PathState(path=path, candidates=[fv.fv_id])
            continue

        merged = list(current.candidates)
        if fv.fv_id not in merged:
            merged.append(fv.fv_id)
        next_paths[path] = PathState(path=path, candidates=merged)

    return PublishResult(tree_state=TreeState.from_paths(next_paths), blobs=blobs, file_versions=versions)


def sync_workspace(
    *,
    workspace: WorkspaceView,
    tree_state: TreeState,
    file_versions: Mapping[str, FileVersion],
) -> WorkspaceView:
    """Advance workspace head while preserving valid local selection."""

    next_selection: Dict[str, str] = {}
    workspace.policy.validate()

    for path, state in tree_state.paths.items():
        chosen = workspace.selection.get(path)
        if chosen in state.candidates:
            next_selection[path] = chosen
            continue
        if len(state.candidates) == 1:
            next_selection[path] = state.candidates[0]
            continue
        next_selection[path] = _choose_by_policy(
            state.candidates,
            file_versions=file_versions,
            prefer_author=workspace.policy.prefer_author,
            tie_break=workspace.policy.tie_break,
        )

    synced = WorkspaceView(
        ws_id=workspace.ws_id,
        user=workspace.user,
        head=tree_state.tree_id,
        selection=next_selection,
        policy=workspace.policy,
    )
    synced.validate_against(tree_state.paths)
    return synced


def collapse_conflict(
    *,
    tree_state: TreeState,
    path: str,
    author: str,
    file_versions: Mapping[str, FileVersion],
    chosen_fv_id: str | None = None,
    merged_content: bytes | str | None = None,
    created_at: str | None = None,
    summary: str | None = None,
) -> PublishResult:
    """Collapse a path superposition to one candidate."""

    if path not in tree_state.paths:
        raise ValueError(f"Path missing in tree: {path}")
    if chosen_fv_id is None and merged_content is None:
        raise ValueError("Provide chosen_fv_id or merged_content to collapse")

    next_paths = {
        p: PathState(path=s.path, candidates=list(s.candidates))
        for p, s in tree_state.paths.items()
    }
    state = next_paths[path]

    blobs: Dict[str, Blob] = {}
    versions: Dict[str, FileVersion] = {}

    if merged_content is not None:
        raw = merged_content.encode("utf-8") if isinstance(merged_content, str) else merged_content
        blob = Blob.from_bytes(raw)
        base = chosen_fv_id or state.candidates[0]
        fv = FileVersion.create(
            blob_id=blob.blob_id,
            author=author,
            created_at=created_at or utc_now_iso(),
            base_fv_id=base,
            summary=summary or "conflict collapse",
        )
        resolved_id = fv.fv_id
        blobs[blob.blob_id] = blob
        versions[fv.fv_id] = fv
    else:
        if chosen_fv_id not in state.candidates:
            raise ValueError(f"Chosen candidate not present on {path}: {chosen_fv_id}")
        resolved_id = chosen_fv_id

    next_paths[path] = PathState(path=path, candidates=[resolved_id])
    return PublishResult(tree_state=TreeState.from_paths(next_paths), blobs=blobs, file_versions=versions)


def build_snapshot(
    *,
    workspace: WorkspaceView,
    tree_state: TreeState,
    file_versions: Mapping[str, FileVersion],
    build_id: str | None = None,
    created_at: str | None = None,
) -> BuildView:
    """Freeze workspace selections into an immutable build view."""

    synced = sync_workspace(workspace=workspace, tree_state=tree_state, file_versions=file_versions)
    resolved_selection = dict(sorted(synced.selection.items()))
    resolved_build_id = build_id or stable_hash(
        {"tree_id": tree_state.tree_id, "selection": resolved_selection}
    )
    return BuildView(
        build_id=resolved_build_id,
        tree_id=tree_state.tree_id,
        selection=resolved_selection,
        created_at=created_at or utc_now_iso(),
    )

