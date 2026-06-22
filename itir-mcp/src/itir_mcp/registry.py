from __future__ import annotations

from typing import Any, Mapping

from .config_tools import get_config_tools
from .comparison_tools import get_comparison_tools
from .contracts import JsonDict, ToolError, ToolExecutionError, ToolHandler, ToolSpec, error_payload, success_payload
from .docstore_tools import get_docstore_tools
from .export_tools import get_export_tools
from .guardrails import safe_tool_call
from .governance_tools import get_governance_tools
from .promotion_tools import get_promotion_tools
from .pnf_tools import get_pnf_tools
from .sensiblaw_tools import get_sensiblaw_tools
from .tool_authority_profiles import DEFAULT_REGISTRY_TOOL_AUTHORITY_PROFILES, validate_tool_authority_profile


class ToolRegistry:
    """Simple in-process registry for namespaced suite tools."""

    def __init__(self) -> None:
        self._tools: dict[str, tuple[ToolSpec, ToolHandler, str | None, JsonDict | None]] = {}

    def register(
        self,
        spec: ToolSpec,
        handler: ToolHandler,
        *,
        authority_profile_key: str | None = None,
        authority_profile: Mapping[str, Any] | None = None,
    ) -> None:
        profile_key = authority_profile_key
        profile: JsonDict | None = None
        if authority_profile is not None:
            profile = validate_tool_authority_profile(authority_profile)
            profile_key = profile_key or str(profile["tool_id"])
        if profile_key is not None:
            object.__setattr__(spec, "authority_profile_key", profile_key)
        if profile is not None:
            object.__setattr__(spec, "authority_profile", profile)
        self._tools[spec.name] = (spec, handler, profile_key, profile)

    def list_tools(self) -> list[ToolSpec]:
        return [spec for spec, _, _, _ in self._tools.values()]

    def get_tool_spec(self, name: str) -> ToolSpec | None:
        tool = self._tools.get(name)
        if tool is None:
            return None
        return tool[0]

    def get_tool_authority_profile_key(self, name: str) -> str | None:
        tool = self._tools.get(name)
        if tool is None:
            return None
        return tool[2]

    def get_tool_authority_profile(self, name: str) -> JsonDict | None:
        tool = self._tools.get(name)
        if tool is None:
            return None
        return tool[3]

    def list_tool_authority_profiles(self) -> dict[str, JsonDict]:
        return {name: profile for name, (_, _, _, profile) in self._tools.items() if profile is not None}

    def invoke(self, name: str, payload: Mapping[str, Any]) -> JsonDict:
        try:
            _, handler, _, _ = self._tools[name]
        except KeyError as exc:
            return error_payload(ToolError(f"Unknown tool: {name}"))
        try:
            return success_payload(handler(payload))
        except ToolError as exc:
            return error_payload(exc)
        except Exception as exc:
            return error_payload(ToolExecutionError(str(exc), details={"tool": name}))

    def safe_invoke(self, name: str, payload: Mapping[str, Any]) -> JsonDict:
        try:
            return success_payload(safe_tool_call(self, name, payload))
        except ToolError as exc:
            return error_payload(exc)
        except Exception as exc:
            return error_payload(ToolExecutionError(str(exc), details={"tool": name}))


def build_default_registry() -> ToolRegistry:
    registry = ToolRegistry()
    for spec, handler in get_sensiblaw_tools():
        registry.register(spec, handler)
    for spec, handler in get_comparison_tools():
        registry.register(spec, handler)
    for spec, handler in get_docstore_tools():
        registry.register(spec, handler)
    for spec, handler in get_promotion_tools():
        registry.register(spec, handler)
    for spec, handler in get_pnf_tools():
        registry.register(spec, handler)
    for spec, handler in get_export_tools():
        registry.register(spec, handler)
    for spec, handler in get_config_tools():
        registry.register(spec, handler)
    for spec, handler in get_governance_tools():
        registry.register(
            spec,
            handler,
            authority_profile_key=spec.name if spec.name in DEFAULT_REGISTRY_TOOL_AUTHORITY_PROFILES else None,
            authority_profile=DEFAULT_REGISTRY_TOOL_AUTHORITY_PROFILES.get(spec.name),
        )
    return registry
