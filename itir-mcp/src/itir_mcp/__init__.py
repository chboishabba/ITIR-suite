"""Suite-level MCP adapter scaffold for ITIR-suite."""

from .contracts import (
    ITIR_MCP_PROTOCOL_VERSION,
    ITIR_MCP_VERSION,
    ToolError,
    ToolExecutionError,
    ToolInputError,
    ToolPolicyError,
    ToolSpec,
    success_payload,
    error_payload,
)
from .registry import ToolRegistry, build_default_registry

__version__ = ITIR_MCP_VERSION

__all__ = [
    "ITIR_MCP_PROTOCOL_VERSION",
    "ITIR_MCP_VERSION",
    "ToolError",
    "ToolExecutionError",
    "ToolInputError",
    "ToolPolicyError",
    "error_payload",
    "success_payload",
    "ToolRegistry",
    "ToolSpec",
    "build_default_registry",
    "__version__",
]
