"""Guarded creation of one fresh ChatGPT conversation."""
from __future__ import annotations

from typing import Any, Mapping

from .contracts import JsonDict, ToolExecutionError, ToolInputError, ToolSpec


SCHEMA_VERSION = "itir.chatgpt.create_conversation.v1"
UNCERTAIN_STATES = frozenset({"async_starting", "commit_unknown", "committed", "committed_pending"})


def _required_prompt(payload: Mapping[str, Any]) -> str:
    value = payload.get("prompt")
    if not isinstance(value, str) or not value.strip():
        raise ToolInputError("Expected non-empty string field: prompt")
    return value.strip()


def _db_path(payload: Mapping[str, Any]) -> str | None:
    value = payload.get("db_path")
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise ToolInputError("Expected non-empty string field: db_path")
    return value.strip()


def create_conversation(payload: Mapping[str, Any]) -> JsonDict:
    """Create exactly one fresh thread through native direct async transport.

    The re-gpt mutation service persists the operation receipt before POST. A
    non-complete state is returned as an explicit hold; callers must reconcile,
    never retry or resend the creation.
    """
    prompt = _required_prompt(payload)
    follow = payload.get("follow", False)
    if not isinstance(follow, bool):
        raise ToolInputError("Expected boolean field: follow")
    db_path = _db_path(payload)
    try:
        from .chatgpt_worker_tools import _worker_api

        raw = _worker_api().chatgpt_new(prompt=prompt, follow=follow, db_path=db_path)
    except ToolInputError:
        raise
    except Exception as exc:
        raise ToolExecutionError("direct async ChatGPT creation failed") from exc
    if not isinstance(raw, Mapping):
        raise ToolExecutionError("re-gpt creation returned an invalid receipt")

    operation_id = str(raw.get("operation_id") or "").strip()
    state = str(raw.get("state") or "commit_unknown")
    receipt = {
        "operation_id": operation_id or None,
        "state": state,
        "conversation_id": raw.get("conversation_id"),
        "transport": "async_curl_cffi",
        "dom_fallback": False,
    }
    uncertain = state in UNCERTAIN_STATES or state not in {"complete", "failed_precommit"}
    return {
        "version": SCHEMA_VERSION,
        "status": "complete" if state == "complete" else "uncertain",
        "uncertain": uncertain,
        "receipt": receipt,
        "operation": dict(raw),
        "policy": {
            "write_transport": "async",
            "dom_fallback": False,
            "automatic_resend": False,
            "uncertain_result_action": "reconcile_only" if uncertain else "none",
        },
    }


def get_chatgpt_creation_tools() -> list[tuple[ToolSpec, Any]]:
    return [
        (
            ToolSpec(
                name="itir.chatgpt.create_conversation",
                title="Create one fresh ChatGPT conversation",
                description=(
                    "Create one fresh conversation through direct async CFFI only. "
                    "The durable operation receipt is returned; uncertain results are holds and are never resent."
                ),
                input_schema={
                    "type": "object",
                    "required": ["prompt"],
                    "additionalProperties": False,
                    "properties": {
                        "prompt": {"type": "string", "minLength": 1},
                        "follow": {"type": "boolean"},
                        "db_path": {"type": "string", "minLength": 1},
                    },
                },
                response_version=SCHEMA_VERSION,
                read_only=False,
            ),
            create_conversation,
        ),
    ]
