from __future__ import annotations

from typing import Any, Mapping

from .contracts import JsonDict, ToolHandler, ToolSpec
from .docstore_config import build_docstore_config


DOCSTORE_CONFIG_PLAN_VERSION = "itir.docstore.config_plan.v1"


def get_config_tools() -> list[tuple[ToolSpec, ToolHandler]]:
    return [
        (
            ToolSpec(
                name="itir.docstore.config_plan",
                title="ITIR docstore config plan",
                description="Build a bounded docstore scan/config/cache plan without scanning producer content.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "allowed_roots": {"type": "array", "items": {"type": "string"}},
                        "allowed_root": {"type": "string"},
                        "roots": {"type": "array", "items": {"type": "string"}},
                        "repo_root": {"type": "string"},
                        "include_markdown_hints": {"type": "boolean"},
                        "include_obsidian_vaults": {"type": "boolean"},
                        "allow_default_discovery": {"type": "boolean"},
                        "limit": {"type": "integer", "minimum": 1},
                        "max_notes": {"type": "integer", "minimum": 1},
                        "cache_enabled": {"type": "boolean"},
                        "cache_ttl_seconds": {"type": "integer", "minimum": 0},
                    },
                    "required": [],
                    "additionalProperties": True,
                },
                response_version=DOCSTORE_CONFIG_PLAN_VERSION,
                read_only=True,
            ),
            docstore_config_plan,
        )
    ]


def docstore_config_plan(payload: Mapping[str, Any]) -> JsonDict:
    config = build_docstore_config(payload)
    return {
        "version": DOCSTORE_CONFIG_PLAN_VERSION,
        "config": config.as_dict(),
        "cache_metadata": config.cache_metadata("docstore_config_plan"),
        "authority_class": "configuration_plan",
    }
