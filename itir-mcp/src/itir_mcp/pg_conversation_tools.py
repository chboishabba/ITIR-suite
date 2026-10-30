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


def sync_roster(payload):
    pages = payload.get("pages", 1)
    if type(pages) is not int or not 1 <= pages <= 20:
        raise ToolInputError("invalid page count")
    return importlib.import_module("re_gpt.pg_hydration").roster_page(pages=pages)


def hydrate_selected(payload):
    cid = payload.get("conversation_id")
    if not isinstance(cid, str) or not cid or len(cid) > 150:
        raise ToolInputError("invalid conversation ID")
    return importlib.import_module("re_gpt.pg_hydration").hydrate_one(cid)


def hydrate_queue(payload):
    limit = payload.get("limit", 5)
    if type(limit) is not int or not 1 <= limit <= 50:
        raise ToolInputError("invalid batch limit")
    return importlib.import_module("re_gpt.pg_hydration").hydrate_pending(limit=limit)


def get_pg_conversation_tools():
    return [
        (ToolSpec(name="itir.chatgpt.pg_roster_sync", title="Sync remote roster to canonical PG",
                  description="Explicit network roster observation and PG commit",
                  input_schema={"type": "object", "properties": {
                      "pages": {"type": "integer", "minimum": 1, "maximum": 20}},
                      "additionalProperties": False}, read_only=False), sync_roster),
        (ToolSpec(name="itir.chatgpt.pg_hydrate_selected", title="Hydrate selected conversation",
                  description="Fetch exact remote graph and ingest into canonical PostgreSQL",
                  input_schema={"type": "object", "properties": {
                      "conversation_id": {"type": "string"}},
                      "required": ["conversation_id"], "additionalProperties": False},
                  read_only=False), hydrate_selected),
        (ToolSpec(name="itir.chatgpt.pg_hydrate_pending", title="Hydrate bounded PG queue",
                  description="Explicit bounded pass over queued roster identities",
                  input_schema={"type": "object", "properties": {
                      "limit": {"type": "integer", "minimum": 1, "maximum": 50}},
                      "additionalProperties": False},
                  read_only=False), hydrate_queue),
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
