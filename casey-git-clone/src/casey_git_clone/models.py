"""Core models for Casey-style superposition version control."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
import hashlib
import json
from types import MappingProxyType
from typing import Any, Dict, Mapping, Sequence


def utc_now_iso() -> str:
    """Return timezone-aware UTC timestamp string."""

    return datetime.now(UTC).isoformat()


def canonical_json(payload: Any) -> str:
    """Serialize payload with deterministic JSON key ordering."""

    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def stable_hash(payload: Any) -> str:
    """Return deterministic SHA-256 hex digest for payload."""

    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class Blob:
    """Content-addressed bytes."""

    blob_id: str
    size: int
    bytes: bytes

    @classmethod
    def from_bytes(cls, raw: bytes) -> Blob:
        blob_id = hashlib.sha256(raw).hexdigest()
        return cls(blob_id=blob_id, size=len(raw), bytes=raw)


@dataclass(frozen=True)
class FileVersion:
    """A concrete file candidate with lightweight provenance."""

    fv_id: str
    blob_id: str
    author: str
    created_at: str
    base_fv_id: str | None = None
    summary: str | None = None

    @classmethod
    def create(
        cls,
        *,
        blob_id: str,
        author: str,
        created_at: str | None = None,
        base_fv_id: str | None = None,
        summary: str | None = None,
    ) -> FileVersion:
        created = created_at or utc_now_iso()
        fv_payload = {
            "blob_id": blob_id,
            "author": author,
            "created_at": created,
            "base_fv_id": base_fv_id,
            "summary": summary,
        }
        return cls(
            fv_id=stable_hash(fv_payload),
            blob_id=blob_id,
            author=author,
            created_at=created,
            base_fv_id=base_fv_id,
            summary=summary,
        )


@dataclass
class PathState:
    """Candidate file versions for a single path."""

    path: str
    candidates: list[str] = field(default_factory=list)

    def validate(self) -> None:
        if not self.path:
            raise ValueError("PathState.path must be non-empty")
        if not self.candidates:
            raise ValueError("PathState.candidates must be non-empty")
        if len(set(self.candidates)) != len(self.candidates):
            raise ValueError("PathState.candidates must be deduplicated")

    def canonical_candidates(self) -> list[str]:
        """Return order-independent candidate representation for hashing."""

        self.validate()
        return sorted(set(self.candidates))


@dataclass
class TreeState:
    """Filesystem tree snapshot where each path can have multiple candidates."""

    tree_id: str
    paths: Dict[str, PathState] = field(default_factory=dict)

    @classmethod
    def from_paths(cls, paths: Mapping[str, PathState]) -> TreeState:
        payload_paths: dict[str, dict[str, list[str]]] = {}
        normalized: dict[str, PathState] = {}

        for path in sorted(paths):
            state = paths[path]
            state.validate()
            if path != state.path:
                raise ValueError(f"Path key mismatch: key={path} state.path={state.path}")
            payload_paths[path] = {"candidates": state.canonical_candidates()}
            normalized[path] = PathState(path=state.path, candidates=list(state.candidates))

        tree_id = stable_hash({"paths": payload_paths})
        return cls(tree_id=tree_id, paths=normalized)


@dataclass(frozen=True)
class Commit:
    """Durable tree snapshot plus parent links."""

    commit_id: str
    parents: tuple[str, ...]
    tree_id: str
    author: str
    created_at: str
    message: str | None = None

    @classmethod
    def create(
        cls,
        *,
        parents: Sequence[str],
        tree_id: str,
        author: str,
        created_at: str | None = None,
        message: str | None = None,
    ) -> Commit:
        created = created_at or utc_now_iso()
        parent_tuple = tuple(parents)
        payload = {
            "parents": parent_tuple,
            "tree_id": tree_id,
            "author": author,
            "created_at": created,
            "message": message,
        }
        return cls(
            commit_id=stable_hash(payload),
            parents=parent_tuple,
            tree_id=tree_id,
            author=author,
            created_at=created,
            message=message,
        )


@dataclass(frozen=True)
class WorkspacePolicy:
    """Policy used when a selected candidate disappears after sync."""

    prefer_author: str | None = None
    tie_break: str = "stable_hash"

    def validate(self) -> None:
        if self.tie_break not in {"stable_hash", "newest", "oldest"}:
            raise ValueError(f"Unsupported tie_break policy: {self.tie_break}")


@dataclass
class WorkspaceView:
    """Active candidate selection for a workspace."""

    ws_id: str
    user: str
    head: str
    selection: Dict[str, str] = field(default_factory=dict)
    policy: WorkspacePolicy = field(default_factory=WorkspacePolicy)

    def validate_against(self, path_states: Mapping[str, PathState]) -> None:
        self.policy.validate()
        for path, chosen in self.selection.items():
            if path not in path_states:
                raise ValueError(f"Selection path missing: {path}")
            if chosen not in path_states[path].candidates:
                raise ValueError(f"Invalid selection for {path}: {chosen}")


@dataclass(frozen=True)
class BuildView:
    """Immutable snapshot used to pin a buildable workspace view."""

    build_id: str
    tree_id: str
    selection: Mapping[str, str]
    created_at: str

    def __post_init__(self) -> None:
        frozen = MappingProxyType(dict(self.selection))
        object.__setattr__(self, "selection", frozen)

