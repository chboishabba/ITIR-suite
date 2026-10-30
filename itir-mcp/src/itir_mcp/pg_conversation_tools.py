"""Canonical history MCP reads, independent of a running TUI.

Reuses re-gpt's PostgreSQL read adapter; no network roster, tmux or socket.
"""
from __future__ import annotations
import importlib
from .contracts import ToolExecutionError, ToolInputError, ToolSpec


def _provider():
    try:
        return importlib.import_module("re_gpt.pg_conversation_read")
    except ImportError as exc:
        raise ToolExecutionError("re-gpt PostgreSQL history provider unavailable") from exc


def search(payload):
    query = payload.get("query", "")
    limit = payload.get("limit", 100)
    offset = payload.get("offset", 0)
    if not isinstance(query, str) or len(query) > 500:
        raise ToolInputError("invalid query")
    if type(limit) is not int or not 1 <= limit <= 500:
        raise ToolInputError("invalid limit")
    if type(offset) is not int or not 0 <= offset <= 1000000:
        raise ToolInputError("invalid offset")
    rows = _provider().list_pg_conversations(query=query, limit=limit, offset=offset)
    return {"source": "itir_postgresql_corpus", "conversations": rows,
            "has_more_possible": len(rows) == limit}


def read(payload):
    cid = payload.get("conversation_id")
    if not isinstance(cid, str) or not cid or len(cid) > 150:
        raise ToolInputError("invalid conversation ID")
    limit = payload.get("limit", 1000)
    if type(limit) is not int or not 1 <= limit <= 10000:
        raise ToolInputError("invalid message limit")
    return _provider().read_pg_conversation(cid, limit=limit)


def get_pg_conversation_tools():
    return [
        (ToolSpec(name="itir.chatgpt.pg_search", title="Search canonical PG conversations",
                  description="Offline PostgreSQL-backed conversation titles and IDs",
                  input_schema={"type": "object", "properties": {
                      "query": {"type": "string"}, "limit": {"type": "integer"},
                      "offset": {"type": "integer"}}, "additionalProperties": False},
                  read_only=True), search),
        (ToolSpec(name="itir.chatgpt.pg_read", title="Read canonical PG conversation",
                  description="Source-preserving archived conversation bodies and provenance",
                  input_schema={"type": "object", "properties": {
                      "conversation_id": {"type": "string"}, "limit": {"type": "integer"}},
                      "required": ["conversation_id"], "additionalProperties": False},
                  read_only=True), read),
    ]
