from __future__ import annotations

from .contracts import ToolSpec
from .registry import ToolRegistry, build_default_registry


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
    def _tool_handler(arguments: dict | None = None):
        return registry.invoke(spec.name, arguments or {})

    _tool_handler.__name__ = spec.name.replace(".", "_")
    _tool_handler.__doc__ = spec.description
    server.tool(name=spec.name, description=spec.description)(_tool_handler)


def main() -> None:
    server = build_fastmcp_server()
    server.run()
