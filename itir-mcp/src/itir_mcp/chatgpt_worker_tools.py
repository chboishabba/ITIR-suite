"""Governed re-gpt worker operations exposed through the ITIR MCP registry."""

from __future__ import annotations

import importlib
from typing import Any, Mapping

from .contracts import JsonDict, ToolExecutionError, ToolInputError, ToolSpec


SCHEMA_VERSION = "itir.chatgpt_worker.v1"


def _required_text(payload: Mapping[str, Any], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ToolInputError(f"Expected non-empty string field: {key}")
    return value.strip()


def _optional_db_path(payload: Mapping[str, Any]) -> str | None:
    value = payload.get("db_path")
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise ToolInputError("Expected non-empty string field: db_path")
    return value.strip()


def _worker_api() -> Any:
    try:
        return importlib.import_module("re_gpt.mcp_server")
    except Exception as exc:  # pragma: no cover - environment-specific import failure
        raise ToolExecutionError("re-gpt worker adapter is unavailable") from exc


def dispatch_worker(payload: Mapping[str, Any]) -> JsonDict:
    """Dispatch exactly one existing-thread worker turn through direct async re-gpt."""
    conversation_id = _required_text(payload, "conversation_id")
    prompt = _required_text(payload, "prompt")
    db_path = _optional_db_path(payload)
    follow = payload.get("follow", True)
    if not isinstance(follow, bool):
        raise ToolInputError("Expected boolean field: follow")
    attachments = payload.get("attachments", [])
    if not isinstance(attachments, list) or not all(isinstance(item, str) and item.strip() for item in attachments):
        raise ToolInputError("Expected attachments to be an array of non-empty path strings")

    result = _worker_api().chatgpt_continue(
        conversation_id=conversation_id,
        prompt=prompt,
        attachments=attachments,
        follow=follow,
        write_transport="async",
        dom_fallback=False,
        db_path=db_path,
    )
    return {
        "version": SCHEMA_VERSION,
        "operation": result,
        "policy": {
            "write_transport": "async",
            "dom_fallback": False,
            "automatic_resend": False,
        },
    }


def operation_status(payload: Mapping[str, Any]) -> JsonDict:
    operation_id = _required_text(payload, "operation_id")
    return {
        "version": SCHEMA_VERSION,
        "operation": _worker_api().chatgpt_operation_status(
            operation_id=operation_id,
            db_path=_optional_db_path(payload),
        ),
    }


def reconcile(payload: Mapping[str, Any]) -> JsonDict:
    """Reconcile exactly one operation using direct reads only; never resubmit."""
    operation_id = _required_text(payload, "operation_id")
    prompt = _required_text(payload, "prompt")
    not_before = payload.get("not_before", 0.0)
    if not isinstance(not_before, (int, float)):
        raise ToolInputError("Expected numeric field: not_before")

    try:
        mutation_service = importlib.import_module("re_gpt.mutation_service")
        db_path = _optional_db_path(payload)
        service = (
            mutation_service.MutationService(db_path=db_path)
            if db_path is not None
            else mutation_service.MutationService()
        )
        result = service.reconcile(
            operation_id,
            prompt=prompt,
            not_before=float(not_before),
            browser_fallback=False,
            direct_allowed=True,
        )
    except ToolInputError:
        raise
    except Exception as exc:
        raise ToolExecutionError("direct-only re-gpt reconciliation failed") from exc
    return {
        "version": SCHEMA_VERSION,
        "operation": result,
        "policy": {"browser_fallback": False, "automatic_resend": False},
    }


def recent_operation_receipts(payload: Mapping[str, Any]) -> JsonDict:
    """Resolve canonical thread identity, then review bounded transport receipts."""
    from .operation_receipt_lookup import operation_receipts

    try:
        return operation_receipts(payload)
    except (ValueError, RuntimeError, FileNotFoundError, TypeError) as exc:
        raise ToolInputError(str(exc)) from exc


def hydrate(payload: Mapping[str, Any]) -> JsonDict:
    """Hydrate one or more conversations into local SQLite using direct async transport (token-optimized)."""
    conversation_id = payload.get("conversation_id")
    if conversation_id is not None and (not isinstance(conversation_id, str) or not conversation_id.strip()):
        raise ToolInputError("Expected non-empty string field: conversation_id")
    limit = payload.get("limit", 1)
    if not isinstance(limit, int):
        raise ToolInputError("Expected integer field: limit")
    db_path = _optional_db_path(payload)
    return {
        "version": SCHEMA_VERSION,
        "result": _worker_api().chatgpt_hydrate(
            conversation_id=conversation_id.strip() if conversation_id else None,
            limit=limit,
            db_path=db_path,
        ),
    }


def get_chatgpt_worker_tools() -> list[tuple[ToolSpec, Any]]:
    return [
        (
            ToolSpec(
                name="itir.chatgpt.hydrate",
                title="Hydrate archived conversation messages",
                description="Hydrate one thread or the most recent unpulled threads into local SQLite using direct async transport (token-optimized).",
                input_schema={
                    "type": "object",
                    "properties": {
                        "conversation_id": {"type": "string"},
                        "limit": {"type": "integer", "minimum": 1, "maximum": 20},
                        "db_path": {"type": "string"},
                    },
                    "additionalProperties": False,
                },
                response_version=SCHEMA_VERSION,
                read_only=False,
            ),
            hydrate,
        ),
        (
            ToolSpec(
                name="itir.chatgpt.operation_receipts",
                title="Read recent canonical-thread operation receipts",
                description="Resolve canonical conversation to bounded re-gpt transport receipt state; no SQL or dispatch.",
                input_schema={
                    "type": "object", "required": ["canonical_thread_id"],
                    "additionalProperties": False,
                    "properties": {
                        "canonical_thread_id": {"type": "string", "minLength": 1},
                        "archive_db": {"type": "string"},
                        "db_path": {"type": "string"},
                        "limit": {"type": "integer", "minimum": 1, "maximum": 50},
                        "active_only": {"type": "boolean"},
                    },
                },
                response_version="itir.chatgpt.operation_receipts.v1",
                read_only=True,
            ),
            recent_operation_receipts,
        ),
        (
            ToolSpec(
                name="itir.chatgpt.dispatch_worker",
                title="Dispatch governed ChatGPT worker",
                description="Dispatch one existing-thread re-gpt worker turn through direct async transport only.",
                input_schema={
                    "type": "object",
                    "required": ["conversation_id", "prompt"],
                    "properties": {
                        "conversation_id": {"type": "string"},
                        "prompt": {"type": "string"},
                        "attachments": {"type": "array", "items": {"type": "string"}},
                        "follow": {"type": "boolean"},
                        "db_path": {"type": "string"},
                    },
                    "additionalProperties": False,
                },
                response_version=SCHEMA_VERSION,
                read_only=False,
            ),
            dispatch_worker,
        ),
        (
            ToolSpec(
                name="itir.chatgpt.operation_status",
                title="Read governed ChatGPT operation status",
                description="Read durable re-gpt operation status without dispatching a mutation.",
                input_schema={
                    "type": "object",
                    "required": ["operation_id"],
                    "properties": {"operation_id": {"type": "string"}, "db_path": {"type": "string"}},
                    "additionalProperties": False,
                },
                response_version=SCHEMA_VERSION,
                read_only=True,
            ),
            operation_status,
        ),
        (
            ToolSpec(
                name="itir.chatgpt.reconcile",
                title="Reconcile governed ChatGPT operation",
                description="Reconcile one uncertain worker operation through direct reads only; never resend.",
                input_schema={
                    "type": "object",
                    "required": ["operation_id", "prompt"],
                    "properties": {
                        "operation_id": {"type": "string"},
                        "prompt": {"type": "string"},
                        "not_before": {"type": "number"},
                        "db_path": {"type": "string"},
                    },
                    "additionalProperties": False,
                },
                response_version=SCHEMA_VERSION,
                read_only=False,
            ),
            reconcile,
        ),
    ]
