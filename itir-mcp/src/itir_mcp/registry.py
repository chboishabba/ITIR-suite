from __future__ import annotations

from typing import Any, Mapping

from .config_tools import get_config_tools
from .comparison_tools import get_comparison_tools
from .contracts import JsonDict, ToolError, ToolExecutionError, ToolHandler, ToolSpec, error_payload, success_payload
from .docstore_tools import get_docstore_tools
from .export_tools import get_export_tools
from .guardrails import safe_tool_call
from .promotion_tools import get_promotion_tools
from .pnf_tools import get_pnf_tools
from .sensiblaw_tools import get_sensiblaw_tools


class ToolRegistry:
    """Simple in-process registry for namespaced suite tools."""

    def __init__(self) -> None:
        self._tools: dict[str, tuple[ToolSpec, ToolHandler]] = {}

    def register(self, spec: ToolSpec, handler: ToolHandler) -> None:
        self._tools[spec.name] = (spec, handler)

    def list_tools(self) -> list[ToolSpec]:
        return [spec for spec, _ in self._tools.values()]

    def invoke(self, name: str, payload: Mapping[str, Any]) -> JsonDict:
        try:
            _, handler = self._tools[name]
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
    return registry
