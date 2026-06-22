from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping, Sequence
from urllib.parse import urlsplit, urlunsplit


PACK_LOADER_VERSION = "itir.zelph.pack_loader.v1"
DEFAULT_PLANNING_GLOB = "zelph_real_world_pack_v1*.manifest.json"
_DEFAULT_REPO_ROOT = Path(__file__).resolve().parents[3]
_REFERENCE_FIELD_NAMES = {
    "href",
    "hf_uri",
    "hf_url",
    "manifest_uri",
    "manifest_url",
    "object_uri",
    "object_url",
    "reference_uri",
    "reference_url",
    "source_uri",
    "source_url",
    "uri",
    "url",
}
_RECURSIVE_SKIP_KEYS = {"command", "commands"}


def discover_zelph_pack_manifest_paths(repo_root: Path | str | None = None) -> list[Path]:
    """Return the local Zelph real-world pack manifests in deterministic order."""

    root = _coerce_path(repo_root) if repo_root is not None else _DEFAULT_REPO_ROOT
    planning_dir = root / "docs" / "planning"
    if not planning_dir.exists():
        return []
    paths = sorted(planning_dir.glob(DEFAULT_PLANNING_GLOB), key=lambda path: path.name)
    return [path for path in paths if path.is_file()]


def load_zelph_pack_source_descriptor(
    repo_root: Path | str | None = None,
    *,
    manifest_paths: Sequence[Path | str] | None = None,
) -> dict[str, Any]:
    """Load Zelph pack manifests into a candidate-only shared-shard source descriptor."""

    root = _coerce_path(repo_root) if repo_root is not None else _DEFAULT_REPO_ROOT
    selected_manifests = (
        [_coerce_manifest_path(root, path) for path in manifest_paths]
        if manifest_paths is not None
        else discover_zelph_pack_manifest_paths(root)
    )
    if not selected_manifests:
        raise FileNotFoundError("no Zelph real-world pack manifests were found")

    manifest_summaries: list[dict[str, Any]] = []
    entries: list[dict[str, Any]] = []
    references: list[dict[str, Any]] = []
    for manifest_path in selected_manifests:
        manifest = _load_json_object(manifest_path)
        manifest_version = _required_str(manifest, "version", label=str(manifest_path))
        manifest_entries = manifest.get("entries")
        if not isinstance(manifest_entries, list):
            raise ValueError(f"{manifest_path}: entries must be an array")

        manifest_reference_count = 0
        for index, raw_entry in enumerate(manifest_entries):
            entry = _mapping(raw_entry, f"{manifest_path}:entries[{index}]")
            declared_path = _required_str(entry, "path", label=f"{manifest_path}:entries[{index}]")
            resolved_path = _resolve_repo_path(root, declared_path)
            if not resolved_path.exists():
                raise FileNotFoundError(
                    f"{manifest_path}: missing Zelph pack entry path: {declared_path}"
                )

            entry_references = _collect_entry_references(entry)
            manifest_reference_count += len(entry_references)
            references.extend(entry_references)

            entries.append(
                {
                    "descriptor_version": PACK_LOADER_VERSION,
                    "manifest_path": str(manifest_path.relative_to(root)),
                    "manifest_version": manifest_version,
                    "entry_index": index,
                    "path": declared_path,
                    "resolved_path": str(resolved_path.relative_to(root)),
                    "exists": True,
                    "source_kind": "local_path",
                    "candidate_only": True,
                    "non_authoritative": True,
                    "network_fetch": False,
                    "references": entry_references,
                }
            )

        manifest_summaries.append(
            {
                "path": str(manifest_path.relative_to(root)),
                "version": manifest_version,
                "entry_count": len(manifest_entries),
                "reference_count": manifest_reference_count,
            }
        )

    normalized_references = _dedupe_references(references)
    return {
        "version": PACK_LOADER_VERSION,
        "descriptor_kind": "shared-shard-source",
        "domain": "zelph",
        "candidate_only": True,
        "non_authoritative": True,
        "network_fetch": False,
        "manifest_count": len(manifest_summaries),
        "entry_count": len(entries),
        "reference_count": len(normalized_references),
        "manifests": manifest_summaries,
        "entries": entries,
        "references": normalized_references,
    }


def _collect_entry_references(value: Any) -> list[dict[str, Any]]:
    collected: list[dict[str, Any]] = []
    if isinstance(value, Mapping):
        for key, item in value.items():
            key_text = str(key)
            lowered = key_text.lower()
            if lowered in _RECURSIVE_SKIP_KEYS:
                continue
            if _is_reference_key(lowered):
                collected.extend(_coerce_reference_values(item, key_text))
                continue
            if isinstance(item, (Mapping, list)):
                collected.extend(_collect_entry_references(item))
    elif isinstance(value, list):
        for item in value:
            if isinstance(item, (Mapping, list)):
                collected.extend(_collect_entry_references(item))
    return collected


def _coerce_reference_values(value: Any, field_name: str) -> list[dict[str, Any]]:
    if isinstance(value, str):
        sanitized = _sanitize_reference_uri(value)
        if not sanitized:
            return []
        return [
            {
                "field": field_name,
                "uri": sanitized,
                "reference_only": True,
                "non_authoritative": True,
            }
        ]
    if isinstance(value, list):
        refs: list[dict[str, Any]] = []
        for item in value:
            refs.extend(_coerce_reference_values(item, field_name))
        return refs
    if isinstance(value, Mapping):
        refs: list[dict[str, Any]] = []
        for nested_key, nested_value in value.items():
            refs.extend(_coerce_reference_values(nested_value, str(nested_key)))
        return refs
    return []


def _dedupe_references(references: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[str, str]] = set()
    normalized: list[dict[str, Any]] = []
    for reference in references:
        field = str(reference.get("field") or "")
        uri = str(reference.get("uri") or "")
        key = (field, uri)
        if key in seen:
            continue
        seen.add(key)
        normalized.append(
            {
                "field": field,
                "uri": uri,
                "reference_only": True,
                "non_authoritative": True,
            }
        )
    normalized.sort(key=lambda item: (item["field"], item["uri"]))
    return normalized


def _is_reference_key(key: str) -> bool:
    if key in _REFERENCE_FIELD_NAMES:
        return True
    return key.endswith("_uri") or key.endswith("_url")


def _sanitize_reference_uri(raw: str) -> str:
    text = str(raw or "").strip()
    if not text:
        return ""
    parsed = urlsplit(text)
    if not parsed.scheme:
        return text
    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()
    if parsed.username or parsed.password:
        host = (parsed.hostname or "").lower()
        if parsed.port is not None:
            netloc = f"{host}:{parsed.port}"
        else:
            netloc = host
    elif parsed.hostname:
        host = parsed.hostname.lower()
        if parsed.port is not None:
            netloc = f"{host}:{parsed.port}"
        else:
            netloc = host
    return urlunsplit((scheme, netloc, parsed.path, "", ""))


def _coerce_manifest_path(repo_root: Path, manifest_path: Path | str) -> Path:
    path = _coerce_path(manifest_path)
    return path if path.is_absolute() else (repo_root / path)


def _resolve_repo_path(repo_root: Path, declared_path: str) -> Path:
    candidate = Path(declared_path)
    resolved = candidate if candidate.is_absolute() else (repo_root / candidate)
    resolved = resolved.resolve(strict=False)
    root = repo_root.resolve(strict=False)
    if not resolved.is_relative_to(root):
        raise ValueError(f"pack entry path escapes repo root: {declared_path}")
    return resolved


def _load_json_object(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return _mapping(data, str(path))


def _mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{label} must be an object")
    return dict(value)


def _required_str(mapping: Mapping[str, Any], key: str, *, label: str) -> str:
    value = mapping.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label}: {key} is required")
    return value.strip()


def _coerce_path(value: Path | str) -> Path:
    if isinstance(value, Path):
        return value
    return Path(value)
