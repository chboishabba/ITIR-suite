from __future__ import annotations

import json
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any, Mapping, Sequence

from .contracts import JsonDict, ToolInputError


DOCSTORE_CONFIG_VERSION = "itir.docstore.config.v1"
CACHE_METADATA_VERSION = "itir.docstore.cache_metadata.v1"

DEFAULT_SCAN_LIMITS: JsonDict = {
    "artifact_files": 80,
    "state_files": 40,
    "review_packet_files": 40,
    "markdown_files": 60,
    "vault_notes": 100,
    "question_limit": 100,
    "cache_entries": 256,
}

MAX_SCAN_LIMITS: JsonDict = {
    "artifact_files": 500,
    "state_files": 200,
    "review_packet_files": 200,
    "markdown_files": 300,
    "vault_notes": 300,
    "question_limit": 1000,
    "cache_entries": 4096,
}


@dataclass(frozen=True)
class ScanLimits:
    artifact_files: int = int(DEFAULT_SCAN_LIMITS["artifact_files"])
    state_files: int = int(DEFAULT_SCAN_LIMITS["state_files"])
    review_packet_files: int = int(DEFAULT_SCAN_LIMITS["review_packet_files"])
    markdown_files: int = int(DEFAULT_SCAN_LIMITS["markdown_files"])
    vault_notes: int = int(DEFAULT_SCAN_LIMITS["vault_notes"])
    question_limit: int = int(DEFAULT_SCAN_LIMITS["question_limit"])
    cache_entries: int = int(DEFAULT_SCAN_LIMITS["cache_entries"])

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any]) -> "ScanLimits":
        return cls(
            artifact_files=_payload_limit(payload, ("artifact_file_limit", "max_artifact_files"), "artifact_files"),
            state_files=_payload_limit(payload, ("state_file_limit", "max_state_files"), "state_files"),
            review_packet_files=_payload_limit(
                payload,
                ("review_packet_file_limit", "max_review_packet_files"),
                "review_packet_files",
            ),
            markdown_files=_payload_limit(payload, ("markdown_file_limit", "max_markdown_files"), "markdown_files"),
            vault_notes=_payload_limit(payload, ("vault_note_limit", "max_vault_notes", "max_notes"), "vault_notes"),
            question_limit=_payload_limit(payload, ("question_limit", "limit"), "question_limit"),
            cache_entries=_payload_limit(payload, ("cache_entries", "cache_max_entries"), "cache_entries"),
        )

    def as_dict(self) -> JsonDict:
        return {
            "artifact_files": self.artifact_files,
            "state_files": self.state_files,
            "review_packet_files": self.review_packet_files,
            "markdown_files": self.markdown_files,
            "vault_notes": self.vault_notes,
            "question_limit": self.question_limit,
            "cache_entries": self.cache_entries,
        }


@dataclass(frozen=True)
class IncludeFlags:
    artifacts: bool = True
    state_payloads: bool = True
    review_packets: bool = True
    todo_graph: bool = False
    markdown_hints: bool = False
    obsidian_vaults: bool = False
    default_discovery: bool = False
    display_fields: bool = False

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any]) -> "IncludeFlags":
        return cls(
            artifacts=_payload_bool(payload, "include_artifacts", True),
            state_payloads=_payload_bool(payload, "include_state_payloads", True),
            review_packets=_payload_bool(payload, "include_review_packets", True),
            todo_graph=_payload_bool(payload, "include_todo_graph", False),
            markdown_hints=_payload_bool(payload, "include_markdown_hints", False),
            obsidian_vaults=(
                _payload_bool(payload, "include_obsidian_vaults", False)
                or _payload_bool(payload, "include_obsidian", False)
            ),
            default_discovery=(
                _payload_bool(payload, "include_default_discovery", False)
                or _payload_bool(payload, "allow_default_discovery", False)
            ),
            display_fields=_payload_bool(payload, "include_display_fields", False),
        )

    def as_dict(self) -> JsonDict:
        return {
            "artifacts": self.artifacts,
            "state_payloads": self.state_payloads,
            "review_packets": self.review_packets,
            "todo_graph": self.todo_graph,
            "markdown_hints": self.markdown_hints,
            "obsidian_vaults": self.obsidian_vaults,
            "default_discovery": self.default_discovery,
            "display_fields": self.display_fields,
        }


@dataclass(frozen=True)
class CacheStrategy:
    enabled: bool = True
    namespace: str = "docstore"
    ttl_seconds: int = 300
    max_entries: int = int(DEFAULT_SCAN_LIMITS["cache_entries"])

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any], limits: ScanLimits) -> "CacheStrategy":
        ttl = _coerce_int(payload.get("cache_ttl_seconds"), default=300)
        return cls(
            enabled=_payload_bool(payload, "cache_enabled", True),
            namespace=str(payload.get("cache_namespace") or "docstore"),
            ttl_seconds=_clamp(ttl, minimum=0, maximum=86_400),
            max_entries=limits.cache_entries,
        )

    def as_dict(self) -> JsonDict:
        return {
            "enabled": self.enabled,
            "namespace": self.namespace,
            "ttl_seconds": self.ttl_seconds,
            "max_entries": self.max_entries,
        }


@dataclass(frozen=True)
class ScanPlan:
    roots: tuple[Path, ...] = ()
    artifact_paths: tuple[Path, ...] = ()
    state_paths: tuple[Path, ...] = ()
    review_packet_paths: tuple[Path, ...] = ()
    markdown_paths: tuple[Path, ...] = ()
    vault_roots: tuple[Path, ...] = ()
    bundle_paths: tuple[Path, ...] = ()

    def as_dict(self) -> JsonDict:
        return {
            "roots": _path_strings(self.roots),
            "artifact_paths": _path_strings(self.artifact_paths),
            "state_paths": _path_strings(self.state_paths),
            "review_packet_paths": _path_strings(self.review_packet_paths),
            "markdown_paths": _path_strings(self.markdown_paths),
            "vault_roots": _path_strings(self.vault_roots),
            "bundle_paths": _path_strings(self.bundle_paths),
        }


@dataclass(frozen=True)
class DocstoreConfig:
    version: str
    allowed_roots: tuple[Path, ...]
    limits: ScanLimits
    include: IncludeFlags
    scan_plan: ScanPlan
    cache: CacheStrategy

    def ensure_allowed(self, path: str | Path, *, label: str = "path") -> Path:
        return validate_allowlisted_path(path, self.allowed_roots, label=label)

    def cache_key(self, kind: str, extra: Mapping[str, Any] | None = None) -> str:
        return stable_cache_key(self, kind=kind, extra=extra)

    def cache_metadata(self, kind: str, extra: Mapping[str, Any] | None = None) -> JsonDict:
        return build_cache_metadata(self, kind=kind, extra=extra)

    def as_dict(self) -> JsonDict:
        return {
            "version": self.version,
            "allowed_roots": _path_strings(self.allowed_roots),
            "limits": self.limits.as_dict(),
            "include": self.include.as_dict(),
            "scan_plan": self.scan_plan.as_dict(),
            "cache": self.cache.as_dict(),
        }


def build_docstore_config(
    payload: Mapping[str, Any] | None = None,
    *,
    base_dir: str | Path | None = None,
    default_allowed_roots: Sequence[str | Path] = (),
) -> DocstoreConfig:
    """Build a bounded, allowlist-checked docstore scan configuration."""

    raw_payload: Mapping[str, Any] = payload or {}
    base = _base_dir(base_dir)
    limits = ScanLimits.from_payload(raw_payload)
    include = IncludeFlags.from_payload(raw_payload)
    allowed_roots = _allowed_roots(raw_payload, base=base, default_allowed_roots=default_allowed_roots)
    scan_plan = _scan_plan(raw_payload, base=base, allowed_roots=allowed_roots, include=include)
    cache = CacheStrategy.from_payload(raw_payload, limits)
    return DocstoreConfig(
        version=DOCSTORE_CONFIG_VERSION,
        allowed_roots=allowed_roots,
        limits=limits,
        include=include,
        scan_plan=scan_plan,
        cache=cache,
    )


def validate_allowlisted_path(path: str | Path, allowed_roots: Sequence[Path], *, label: str = "path") -> Path:
    resolved = _resolve_path(path)
    if not allowed_roots:
        raise ToolInputError(f"{label} requires an explicit allowed root", details={"path": str(resolved)})
    if not any(_is_relative_to(resolved, root) for root in allowed_roots):
        raise ToolInputError(
            f"{label} is outside allowed roots",
            details={"path": str(resolved), "allowed_roots": _path_strings(allowed_roots)},
        )
    return resolved


def stable_cache_key(config: DocstoreConfig, *, kind: str, extra: Mapping[str, Any] | None = None) -> str:
    material = {
        "version": DOCSTORE_CONFIG_VERSION,
        "kind": kind,
        "allowed_roots": sorted(_path_strings(config.allowed_roots)),
        "limits": config.limits.as_dict(),
        "include": config.include.as_dict(),
        "scan_plan": _sorted_scan_plan(config.scan_plan),
        "cache_namespace": config.cache.namespace,
        "extra": _jsonable(extra or {}),
    }
    serialized = json.dumps(material, sort_keys=True, separators=(",", ":"))
    return f"sha256:{sha256(serialized.encode('utf-8')).hexdigest()}"


def build_cache_metadata(config: DocstoreConfig, *, kind: str, extra: Mapping[str, Any] | None = None) -> JsonDict:
    return {
        "version": CACHE_METADATA_VERSION,
        "enabled": config.cache.enabled,
        "strategy": "memory_ttl" if config.cache.enabled else "disabled",
        "namespace": config.cache.namespace,
        "ttl_seconds": config.cache.ttl_seconds,
        "max_entries": config.cache.max_entries,
        "key": stable_cache_key(config, kind=kind, extra=extra),
        "kind": kind,
    }


def _scan_plan(
    payload: Mapping[str, Any],
    *,
    base: Path,
    allowed_roots: tuple[Path, ...],
    include: IncludeFlags,
) -> ScanPlan:
    roots = _validated_paths(_payload_path_list(payload, "roots", "root"), base=base, allowed_roots=allowed_roots, label="root")
    repo_roots = _validated_paths(
        _payload_path_list(payload, "repo_roots", "repo_root"),
        base=base,
        allowed_roots=allowed_roots,
        label="repo_root",
    )
    roots = _dedupe_paths((*roots, *repo_roots))

    markdown_paths: tuple[Path, ...] = ()
    vault_roots: tuple[Path, ...] = ()
    bundle_paths: tuple[Path, ...] = ()
    if include.markdown_hints:
        markdown_paths = _validated_paths(
            _payload_path_list(payload, "markdown_paths", "markdown_path"),
            base=base,
            allowed_roots=allowed_roots,
            label="markdown_path",
        )
    if include.obsidian_vaults:
        vault_roots = _validated_paths(
            _payload_path_list(payload, "vault_roots", "vault_root"),
            base=base,
            allowed_roots=allowed_roots,
            label="vault_root",
        )
        bundle_paths = _validated_paths(
            _payload_path_list(payload, "bundle_paths", "bundle_path"),
            base=base,
            allowed_roots=allowed_roots,
            label="bundle_path",
        )

    return ScanPlan(
        roots=roots,
        artifact_paths=(
            _validated_paths(
                _payload_path_list(payload, "artifact_paths", "artifact_path"),
                base=base,
                allowed_roots=allowed_roots,
                label="artifact_path",
            )
            if include.artifacts
            else ()
        ),
        state_paths=(
            _validated_paths(
                _payload_path_list(payload, "state_paths", "state_path"),
                base=base,
                allowed_roots=allowed_roots,
                label="state_path",
            )
            if include.state_payloads
            else ()
        ),
        review_packet_paths=(
            _validated_paths(
                _payload_path_list(payload, "review_packet_paths", "review_packet_path"),
                base=base,
                allowed_roots=allowed_roots,
                label="review_packet_path",
            )
            if include.review_packets
            else ()
        ),
        markdown_paths=markdown_paths,
        vault_roots=vault_roots,
        bundle_paths=bundle_paths,
    )


def _allowed_roots(
    payload: Mapping[str, Any],
    *,
    base: Path,
    default_allowed_roots: Sequence[str | Path],
) -> tuple[Path, ...]:
    roots = [
        _resolve_path(root, base=base)
        for root in (
            *_payload_path_list(payload, "allowed_roots", "allowed_root"),
            *_payload_path_list(payload, "root_allowlist", "allow_root"),
            *default_allowed_roots,
        )
    ]
    return _dedupe_paths(roots)


def _validated_paths(
    values: Sequence[str],
    *,
    base: Path,
    allowed_roots: tuple[Path, ...],
    label: str,
) -> tuple[Path, ...]:
    paths = [validate_allowlisted_path(_resolve_path(value, base=base), allowed_roots, label=label) for value in values]
    return _dedupe_paths(paths)


def _payload_limit(payload: Mapping[str, Any], keys: Sequence[str], limit_name: str) -> int:
    raw = next((payload[key] for key in keys if key in payload), None)
    default = int(DEFAULT_SCAN_LIMITS[limit_name])
    maximum = int(MAX_SCAN_LIMITS[limit_name])
    return _clamp(_coerce_int(raw, default=default), minimum=1, maximum=maximum)


def _payload_bool(payload: Mapping[str, Any], key: str, default: bool) -> bool:
    if key not in payload:
        return default
    value = payload[key]
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"1", "true", "yes", "on"}:
            return True
        if lowered in {"0", "false", "no", "off"}:
            return False
    return bool(value)


def _payload_path_list(payload: Mapping[str, Any], plural_key: str, singular_key: str | None = None) -> tuple[str, ...]:
    values: list[str] = []
    raw = payload.get(plural_key)
    if isinstance(raw, (str, Path)):
        values.append(str(raw))
    elif isinstance(raw, Sequence) and not isinstance(raw, (bytes, bytearray, str)):
        values.extend(str(item) for item in raw if str(item).strip())
    if singular_key and payload.get(singular_key):
        values.append(str(payload[singular_key]))
    return tuple(values)


def _base_dir(base_dir: str | Path | None) -> Path:
    return _resolve_path(base_dir or Path.cwd())


def _resolve_path(path: str | Path, *, base: Path | None = None) -> Path:
    candidate = Path(path).expanduser()
    if not candidate.is_absolute():
        candidate = (base or Path.cwd()) / candidate
    return candidate.resolve()


def _dedupe_paths(paths: Sequence[Path]) -> tuple[Path, ...]:
    out: list[Path] = []
    seen: set[Path] = set()
    for path in paths:
        if path not in seen:
            seen.add(path)
            out.append(path)
    return tuple(out)


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _coerce_int(value: Any, *, default: int) -> int:
    if isinstance(value, bool):
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _clamp(value: int, *, minimum: int, maximum: int) -> int:
    return max(minimum, min(maximum, value))


def _path_strings(paths: Sequence[Path]) -> list[str]:
    return [str(path) for path in paths]


def _sorted_scan_plan(plan: ScanPlan) -> JsonDict:
    return {key: sorted(value) for key, value in plan.as_dict().items()}


def _jsonable(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray, str)):
        return [_jsonable(item) for item in value]
    if isinstance(value, Path):
        return str(value)
    return value
