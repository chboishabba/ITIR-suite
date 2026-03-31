from __future__ import annotations

from typing import Any, Mapping

from .chat_export_structurer_tools import get_chat_export_structurer_tools
from .contracts import JsonDict, ToolError, ToolExecutionError, ToolHandler, ToolSpec, error_payload, success_payload
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


def build_default_registry() -> ToolRegistry:
    registry = ToolRegistry()
    for spec, handler in get_sensiblaw_tools():
        registry.register(spec, handler)
    for spec, handler in get_chat_export_structurer_tools():
        registry.register(spec, handler)
    return registry
