from __future__ import annotations

from typing import Any

from pydantic import ConfigDict

from .contracts import ToolSpec
from .registry import ToolRegistry, build_default_registry


class _DynamicArgModel:
    pass


def build_fastmcp_server(registry: ToolRegistry | None = None):
    """Return a FastMCP server when the optional transport dependency exists."""

    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError as exc:
        raise RuntimeError(
            "Optional MCP transport dependency missing. Install with "
            "`pip install -e itir-mcp[transport]`."
        ) from exc

    active_registry = registry or build_default_registry()
    server = FastMCP("itir-mcp")

    for spec in active_registry.list_tools():
        _register_fastmcp_tool(server, active_registry, spec)

    return server


def _register_fastmcp_tool(server, registry: ToolRegistry, spec: ToolSpec) -> None:
    from mcp.server.fastmcp.tools.base import Tool
    from mcp.server.fastmcp.utilities.func_metadata import ArgModelBase, FuncMetadata

    class DynamicArgModel(ArgModelBase):
        model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)

        def model_dump_one_level(self) -> dict[str, Any]:
            d = dict(self)
            if hasattr(self, "__pydantic_extra__") and self.__pydantic_extra__:
                d.update(self.__pydantic_extra__)
            return d

    def make_handler(name: str, desc: str):
        def _tool_handler(arguments: dict | None = None, **kwargs):
            payload = dict(kwargs)
            if isinstance(arguments, dict):
                payload.update(arguments)
            payload.pop("kwargs", None)
            return registry.invoke(name, payload)

        _tool_handler.__name__ = name.replace(".", "_")
        _tool_handler.__doc__ = desc
        return _tool_handler

    input_schema = spec.input_schema if spec.input_schema is not None else {"type": "object", "properties": {}}

    tool = Tool(
        fn=make_handler(spec.name, spec.description),
        name=spec.name,
        description=spec.description,
        parameters=input_schema,
        fn_metadata=FuncMetadata(arg_model=DynamicArgModel),
        is_async=False,
    )
    server._tool_manager._tools[spec.name] = tool


def main() -> None:
    server = build_fastmcp_server()
    server.run()

