from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from .contracts import JsonDict, ToolHandler, ToolInputError, ToolSpec
from .markdown_export import MARKDOWN_EXPORT_VERSION, render_markdown_projection, write_markdown_projection


MARKDOWN_RENDER_TOOL_VERSION = "itir.markdown.render_projection.v1"
MARKDOWN_WRITE_TOOL_VERSION = "itir.markdown.write_projection.v1"


def get_export_tools() -> list[tuple[ToolSpec, ToolHandler]]:
    return [
        (
            ToolSpec(
                name="itir.markdown.render_projection",
                title="ITIR Markdown projection render",
                description="Render an MCP response as a replaceable non-authoritative Markdown projection.",
                input_schema=_projection_input_schema(include_output_root=False),
                response_version=MARKDOWN_RENDER_TOOL_VERSION,
                read_only=True,
            ),
            render_projection_tool,
        ),
        (
            ToolSpec(
                name="itir.markdown.write_projection",
                title="ITIR Markdown projection write",
                description="Write a replaceable non-authoritative Markdown projection under an explicit output root.",
                input_schema=_projection_input_schema(include_output_root=True),
                response_version=MARKDOWN_WRITE_TOOL_VERSION,
                read_only=False,
            ),
            write_projection_tool,
        ),
    ]


def render_projection_tool(payload: Mapping[str, Any]) -> JsonDict:
    response = _response_payload(payload)
    projection = render_markdown_projection(
        response,
        refreshed_at=str(payload.get("refreshed_at") or "unspecified"),
        source_label=str(payload.get("source_label") or "MCP response"),
        max_items=_max_items(payload),
    )
    return _projection_result(MARKDOWN_RENDER_TOOL_VERSION, projection)


def write_projection_tool(payload: Mapping[str, Any]) -> JsonDict:
    output_root = str(payload.get("output_root") or "").strip()
    if not output_root:
        raise ToolInputError("output_root is required")
    response = _response_payload(payload)
    path = write_markdown_projection(
        response,
        output_root=output_root,
        refreshed_at=str(payload.get("refreshed_at") or "unspecified"),
        source_label=str(payload.get("source_label") or "MCP response"),
        max_items=_max_items(payload),
    )
    projection = render_markdown_projection(
        response,
        refreshed_at=str(payload.get("refreshed_at") or "unspecified"),
        source_label=str(payload.get("source_label") or "MCP response"),
        max_items=_max_items(payload),
    )
    result = _projection_result(MARKDOWN_WRITE_TOOL_VERSION, projection)
    result["written_path"] = str(path)
    result["output_root"] = str(Path(output_root).expanduser().resolve())
    return result


def _projection_result(version: str, projection) -> JsonDict:
    return {
        "version": version,
        "projection_version": MARKDOWN_EXPORT_VERSION,
        "payload_version": projection.payload_version,
        "block_id": projection.block_id,
        "relative_path": str(projection.relative_path),
        "title": projection.title,
        "block_text": projection.block_text,
        "page_text": projection.page_text,
        "authority_class": "generated_projection_non_authoritative",
    }


def _response_payload(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    response = payload.get("response", payload.get("payload"))
    if not isinstance(response, Mapping):
        raise ToolInputError("response object is required")
    return response


def _max_items(payload: Mapping[str, Any]) -> int:
    raw = payload.get("max_items", 50)
    try:
        value = int(raw)
    except (TypeError, ValueError):
        value = 50
    return max(1, min(500, value))


def _projection_input_schema(*, include_output_root: bool) -> JsonDict:
    properties: JsonDict = {
        "response": {"type": "object"},
        "payload": {"type": "object"},
        "refreshed_at": {"type": "string"},
        "source_label": {"type": "string"},
        "max_items": {"type": "integer", "minimum": 1},
    }
    required: list[str] = []
    if include_output_root:
        properties["output_root"] = {"type": "string"}
        required.append("output_root")
    return {
        "type": "object",
        "properties": properties,
        "required": required,
        "additionalProperties": True,
    }
