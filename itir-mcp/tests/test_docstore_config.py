from __future__ import annotations

from pathlib import Path

import pytest

from itir_mcp import build_default_registry
from itir_mcp.contracts import ToolInputError
from itir_mcp.docstore_config import (
    MAX_SCAN_LIMITS,
    build_docstore_config,
    validate_allowlisted_path,
)


def test_rejects_scan_root_outside_explicit_allowlist(tmp_path: Path) -> None:
    allowed = tmp_path / "allowed"
    outside = tmp_path / "outside"
    allowed.mkdir()
    outside.mkdir()

    with pytest.raises(ToolInputError, match="outside allowed roots"):
        build_docstore_config(
            {"allowed_roots": [str(allowed)], "roots": [str(outside)]},
            base_dir=tmp_path,
        )


def test_accepts_paths_under_allowed_root(tmp_path: Path) -> None:
    allowed = tmp_path / "allowed"
    nested = allowed / "project"
    nested.mkdir(parents=True)

    config = build_docstore_config(
        {"allowed_roots": [str(allowed)], "roots": [str(nested)]},
        base_dir=tmp_path,
    )

    assert config.scan_plan.roots == (nested.resolve(),)
    assert validate_allowlisted_path(nested, config.allowed_roots) == nested.resolve()


def test_scan_limits_use_conservative_defaults_and_clamp_payload_values(tmp_path: Path) -> None:
    allowed = tmp_path / "allowed"
    allowed.mkdir()

    config = build_docstore_config(
        {
            "allowed_roots": [str(allowed)],
            "artifact_file_limit": 999_999,
            "state_file_limit": 0,
            "markdown_file_limit": "not-an-int",
            "cache_ttl_seconds": 999_999,
            "cache_max_entries": -4,
        },
        base_dir=tmp_path,
    )

    assert config.limits.artifact_files == MAX_SCAN_LIMITS["artifact_files"]
    assert config.limits.state_files == 1
    assert config.limits.markdown_files == 60
    assert config.limits.cache_entries == 1
    assert config.cache.ttl_seconds == 86_400
    assert config.include.markdown_hints is False
    assert config.include.obsidian_vaults is False
    assert config.include.default_discovery is False


def test_cache_key_and_metadata_are_deterministic(tmp_path: Path) -> None:
    root_a = tmp_path / "a"
    root_b = tmp_path / "b"
    root_a.mkdir()
    root_b.mkdir()

    left = build_docstore_config(
        {
            "allowed_roots": [str(tmp_path)],
            "roots": [str(root_a), str(root_b)],
            "limit": 42,
            "cache_namespace": "suite",
        },
        base_dir=tmp_path,
    )
    right = build_docstore_config(
        {
            "cache_namespace": "suite",
            "limit": 42,
            "roots": [str(root_b), str(root_a)],
            "allowed_roots": [str(tmp_path)],
        },
        base_dir=tmp_path,
    )

    assert left.cache_key("open_questions", {"b": 2, "a": 1}) == right.cache_key(
        "open_questions",
        {"a": 1, "b": 2},
    )
    assert left.cache_metadata("open_questions") == left.cache_metadata("open_questions")
    assert left.cache_metadata("open_questions")["key"].startswith("sha256:")


def test_markdown_and_obsidian_inputs_require_explicit_include_flags(tmp_path: Path) -> None:
    allowed = tmp_path / "allowed"
    allowed.mkdir()
    markdown_path = allowed / "plan.md"
    vault_root = allowed / "vault"
    bundle_path = allowed / "bundle.jsonl"

    closed = build_docstore_config(
        {
            "allowed_roots": [str(allowed)],
            "markdown_paths": [str(markdown_path)],
            "vault_roots": [str(vault_root)],
            "bundle_paths": [str(bundle_path)],
        },
        base_dir=tmp_path,
    )

    assert closed.scan_plan.markdown_paths == ()
    assert closed.scan_plan.vault_roots == ()
    assert closed.scan_plan.bundle_paths == ()

    open_config = build_docstore_config(
        {
            "allowed_roots": [str(allowed)],
            "include_markdown_hints": True,
            "include_obsidian_vaults": True,
            "markdown_paths": [str(markdown_path)],
            "vault_roots": [str(vault_root)],
            "bundle_paths": [str(bundle_path)],
        },
        base_dir=tmp_path,
    )

    assert open_config.scan_plan.markdown_paths == (markdown_path.resolve(),)
    assert open_config.scan_plan.vault_roots == (vault_root.resolve(),)
    assert open_config.scan_plan.bundle_paths == (bundle_path.resolve(),)


def test_config_plan_tool_exposes_bounded_scan_plan(tmp_path: Path) -> None:
    allowed = tmp_path / "allowed"
    allowed.mkdir()
    root = allowed / "repo"
    root.mkdir()

    registry = build_default_registry()
    result = registry.invoke(
        "itir.docstore.config_plan",
        {
            "allowed_roots": [str(allowed)],
            "roots": [str(root)],
            "limit": 12,
            "cache_namespace": "test",
        },
    )

    assert result["ok"] is True
    payload = result["result"]
    assert payload["version"] == "itir.docstore.config_plan.v1"
    assert payload["config"]["scan_plan"]["roots"] == [str(root.resolve())]
    assert payload["config"]["limits"]["question_limit"] == 12
    assert payload["cache_metadata"]["key"].startswith("sha256:")
