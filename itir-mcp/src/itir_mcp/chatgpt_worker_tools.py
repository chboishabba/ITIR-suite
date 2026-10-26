"""Governed re-gpt worker operations exposed through the ITIR MCP registry."""

from __future__ import annotations

import importlib
from typing import Any, Mapping

from .contracts import JsonDict, ToolExecutionError, ToolInputError, ToolSpec


SCHEMA_VERSION = "itir.chatgpt_worker.v1"

WORKER_PROMPT_PRESETS: dict[str, str] = {
    "max_cut": (
        "Exactly complete all per max-cut and continue per pareto/snowball/ibrahim. "
        "Check the web and latest PRs for inspiration and cross-pollination -- assume we "
        "already have everything we need in-repo. Keep following your nose until you hit "
        "a wall -- do not wait for approval, and remember our attribution rules."
    ),
    "grug_ste100": (
        "Apply Grug-brain simplicity and ASD-STE100 Simplified Technical English: one "
        "thought per sentence, active voice, approved unambiguous terms, zero speculative "
        "abstraction, no inline code dumps in prose, and normalize onto existing in-repo surfaces."
    ),
    "grug": (
        "Apply Grug-brain simplicity and ASD-STE100 Simplified Technical English: one "
        "thought per sentence, active voice, approved unambiguous terms, zero speculative "
        "abstraction, no inline code dumps in prose, and normalize onto existing in-repo surfaces."
    ),
    "zkp_qa": (
        "Frame via ZKP (O/R/C/S/L/P/G/F) with explicit preconditions, invariants, and "
        "postconditions. Converge toward normalized surfaces per ITIL, ISO 9000/42001/27001/"
        "27701/23894/9241, NIST AI RMF, Six Sigma, and C4/PlantUML. Assign one disjoint "
        "nonblocking lane per worker, no skeletons or stubs, and complete implementation + "
        "deterministic verification within the turn."
    ),
    "zkp": (
        "Frame via ZKP (O/R/C/S/L/P/G/F) with explicit preconditions, invariants, and "
        "postconditions. Converge toward normalized surfaces per ITIL, ISO 9000/42001/27001/"
        "27701/23894/9241, NIST AI RMF, Six Sigma, and C4/PlantUML. Assign one disjoint "
        "nonblocking lane per worker, no skeletons or stubs, and complete implementation + "
        "deterministic verification within the turn."
    ),
    "introspective_viz": (
        "Apply the introspective method: 1. Model the theory accurately per actual "
        "implementation. 2. Generate a plain-language, physically intuitive visual proof "
        "(Python/HTML/SVG). 3. Inspect the visualization. 4. Formalize new findings in "
        "Lean or Agda per repo convention."
    ),
    "converge_toe": (
        "Converge toward the DASHI TOE: dashi_agda DASHI/EverythingTOESymmetryResolved369.agda, "
        "DASHI/Unifier.agda and DASHI/Unified/. Assume the content already exists in-repo. "
        "Search first for existing, duplicate or near constructions (GitHub code search; the local "
        "referee confirms with dashi-agda-preflight related_symbols/discover/round_lineage). "
        "Order: reuse, then unify duplicates, then extend, then construct new. Attach every new "
        "result to the TOE import graph. Do not edit ESD surfaces (dashi_digital_esd repo, "
        "*digital_esd* and *ESD* modules); import only. Keep attribution for meta-introspector repos."
    ),
    "referee_pass": (
        "Local referee verification passed (0 errors, 0 warnings). Proceed immediately "
        "to the next highest-alpha vertical slice per max-cut and pareto/snowball/ibrahim; "
        "push commits and return SHAs + deterministic referee commands."
    ),
}

_VERBOSE_OPERATION_KEYS = {
    "read_diagnostic",
    "write_diagnostic",
    "read_diagnostics",
    "read_observations",
    "write_observations",
    "started_at",
    "authenticated_at",
    "hydrated_at",
    "attachment_ready_at",
    "submitted_at",
    "committed_at",
    "completed_at",
    "requested_parent_node_id",
    "attachment_ids",
    "attachments",
    "attempted_read_adapters",
    "rejected_read_adapters",
    "prompt_digest",
    "transport",
    "operation",
    "user_node_id",
    "assistant_node_id",
    "read_adapter",
    "new_messages",
    "total_messages",
}


def _compact_operation(result: Any) -> Any:
    if isinstance(result, dict):
        return {
            k: v
            for k, v in result.items()
            if k not in _VERBOSE_OPERATION_KEYS
            and not (k in {"error_class", "error_detail"} and v is None)
        }
    return result


def _resolve_prompt(payload: Mapping[str, Any]) -> str:
    raw_prompt = payload.get("prompt")
    if raw_prompt is not None and not isinstance(raw_prompt, str):
        raise ToolInputError("Expected string field: prompt")
    preset = payload.get("preset")
    if preset is not None and not isinstance(preset, str):
        raise ToolInputError("Expected string field: preset")
    parts: list[str] = []
    if preset:
        for key in preset.replace(",", " ").split():
            clean = key.lstrip("@").strip()
            if clean not in WORKER_PROMPT_PRESETS:
                raise ToolInputError(f"Unknown worker prompt preset: {clean}")
            parts.append(WORKER_PROMPT_PRESETS[clean])
    text = (raw_prompt or "").strip()
    if text:
        tokens = text.split()
        consumed = 0
        for tok in tokens:
            if tok.startswith("@") and tok[1:] in WORKER_PROMPT_PRESETS:
                parts.append(WORKER_PROMPT_PRESETS[tok[1:]])
                consumed += 1
            else:
                break
        remainder = "" if consumed == len(tokens) else (text.split(None, consumed)[-1] if consumed else text)
        if remainder:
            parts.append(remainder)
    resolved = "\n\n".join(p for p in parts if p)
    if not resolved:
        raise ToolInputError("Expected non-empty string field: prompt (or preset)")
    return resolved


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
        for mod_name in (
            "re_gpt.proof_of_work",
            "re_gpt.browser_session_replay",
            "re_gpt.async_mutation_probe",
            "re_gpt.mutation_receipt",
            "re_gpt.mutation_service",
            "re_gpt.mcp_server",
        ):
            if mod_name in importlib.sys.modules:
                importlib.reload(importlib.sys.modules[mod_name])
        return importlib.import_module("re_gpt.mcp_server")
    except Exception as exc:  # pragma: no cover - environment-specific import failure
        raise ToolExecutionError("re-gpt worker adapter is unavailable") from exc


def dispatch_worker(payload: Mapping[str, Any]) -> JsonDict:
    """Dispatch exactly one existing-thread worker turn through direct async re-gpt."""
    conversation_id = _required_text(payload, "conversation_id")
    prompt = _resolve_prompt(payload)
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
        "operation": _compact_operation(result),
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
        "operation": _compact_operation(
            _worker_api().chatgpt_operation_status(
                operation_id=operation_id,
                db_path=_optional_db_path(payload),
            )
        ),
    }


def reconcile(payload: Mapping[str, Any]) -> JsonDict:
    """Reconcile exactly one operation using direct reads only; never resubmit."""
    operation_id = _required_text(payload, "operation_id")
    prompt = _resolve_prompt(payload)
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
        "operation": _compact_operation(result),
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


def list_threads(payload: Mapping[str, Any]) -> JsonDict:
    """List or search archived conversations in local SQLite without raw SQL."""
    limit = payload.get("limit", 20)
    if not isinstance(limit, int):
        raise ToolInputError("Expected integer field: limit")
    query = payload.get("query")
    if query is not None and not isinstance(query, str):
        raise ToolInputError("Expected string field: query")
    db_path = _optional_db_path(payload)
    rows = _worker_api().chatgpt_list(limit=limit, query=query, db_path=db_path)
    return {
        "version": SCHEMA_VERSION,
        "count": len(rows),
        "threads": rows,
    }


def session_status(payload: Mapping[str, Any]) -> JsonDict:
    """Return redacted CFFI session and adapter health status."""
    db_path = _optional_db_path(payload)
    api = _worker_api()
    return {
        "version": SCHEMA_VERSION,
        "session": api.chatgpt_session_status(),
        "adapter_health": api.chatgpt_adapter_health(db_path=db_path, sample_limit=20),
    }


def view_messages(payload: Mapping[str, Any]) -> JsonDict:
    """Inspect recent or indexed messages in a conversation without raw SQLite queries."""
    conversation_id = _required_text(payload, "conversation_id")
    tail = payload.get("tail", 5)
    if not isinstance(tail, int) or tail < 0 or tail > 100:
        raise ToolInputError("Expected integer field: tail (0-100)")
    message_index = payload.get("message_index")
    if message_index is not None and not isinstance(message_index, int):
        raise ToolInputError("Expected integer field: message_index")
    author = payload.get("author")
    if author is not None and not isinstance(author, str):
        raise ToolInputError("Expected string field: author")
    max_chars = payload.get("max_chars", 0)
    if not isinstance(max_chars, int) or max_chars < 0:
        raise ToolInputError("Expected non-negative integer field: max_chars")
    db_path = _optional_db_path(payload)

    return _worker_api().chatgpt_view(
        conversation_id=conversation_id,
        tail=tail,
        message_index=message_index,
        author=author,
        max_chars=max_chars,
        db_path=db_path,
    )


def fleet_status(payload: Mapping[str, Any]) -> JsonDict:
    """Return cluster rollups, thread counts, and active leads across the multi-thread fleet."""
    db_path = _optional_db_path(payload)
    try:
        fleet_mod = importlib.import_module("re_gpt.fleet")
        orchestrator_cls = getattr(fleet_mod, "FleetOrchestrator")
        orchestrator = orchestrator_cls(db_path=db_path) if db_path else orchestrator_cls()
        summary = orchestrator.status_summary()
        clusters_summary = {}
        for c_id, c_data in summary.get("clusters", {}).items():
            lead = c_data.get("active_lead")
            clusters_summary[c_id] = {
                "name": c_data.get("name"),
                "thread_count": c_data.get("thread_count"),
                "active_lead": {
                    "conversation_id": lead.get("conversation_id"),
                    "title": lead.get("title"),
                    "message_count": lead.get("message_count"),
                    "referenced_prs": lead.get("referenced_prs", []),
                } if lead else None,
            }
        return {
            "version": SCHEMA_VERSION,
            "clusters": clusters_summary,
        }
    except Exception as exc:
        raise ToolExecutionError(f"fleet status failed: {exc}") from exc


def fleet_opportunities(payload: Mapping[str, Any]) -> JsonDict:
    """Find highest-alpha research and derivation opportunities across the fleet."""
    limit = payload.get("limit", 20)
    if not isinstance(limit, int) or limit < 1 or limit > 100:
        raise ToolInputError("Expected integer field: limit (1-100)")
    min_score = payload.get("min_score", 20.0)
    if not isinstance(min_score, (int, float)):
        raise ToolInputError("Expected numeric field: min_score")
    db_path = _optional_db_path(payload)
    try:
        import dataclasses
        fleet_mod = importlib.import_module("re_gpt.fleet")
        orchestrator_cls = getattr(fleet_mod, "FleetOrchestrator")
        orchestrator = orchestrator_cls(db_path=db_path) if db_path else orchestrator_cls()
        opps = orchestrator.find_high_alpha(limit=limit, min_score=float(min_score))
        return {
            "version": SCHEMA_VERSION,
            "count": len(opps),
            "opportunities": [dataclasses.asdict(o) for o in opps],
        }
    except Exception as exc:
        raise ToolExecutionError(f"fleet opportunities failed: {exc}") from exc


def get_chatgpt_worker_tools() -> list[tuple[ToolSpec, Any]]:
    return [
        (
            ToolSpec(
                name="itir.chatgpt.list_threads",
                title="List or search archived ChatGPT conversations",
                description="List recent conversations or search by title substring in local SQLite.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "limit": {"type": "integer", "minimum": 1, "maximum": 500},
                        "query": {"type": "string"},
                        "db_path": {"type": "string"},
                    },
                    "additionalProperties": False,
                },
                response_version=SCHEMA_VERSION,
                read_only=True,
            ),
            list_threads,
        ),
        (
            ToolSpec(
                name="itir.chatgpt.session_status",
                title="Read CFFI session and adapter health status",
                description="Check redacted local CFFI session freshness and adapter health telemetry.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "db_path": {"type": "string"},
                    },
                    "additionalProperties": False,
                },
                response_version=SCHEMA_VERSION,
                read_only=True,
            ),
            session_status,
        ),
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
                description=(
                    "Dispatch one existing-thread re-gpt worker turn through direct async transport only. "
                    "Supports @max_cut, @grug_ste100, @zkp_qa, @introspective_viz, @converge_toe, and @referee_pass presets."
                ),
                input_schema={
                    "type": "object",
                    "required": ["conversation_id"],
                    "properties": {
                        "conversation_id": {"type": "string"},
                        "prompt": {"type": "string"},
                        "preset": {
                            "type": "string",
                            "description": "Optional space/comma-separated presets: max_cut, grug_ste100, zkp_qa, introspective_viz, converge_toe, referee_pass",
                        },
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
        (
            ToolSpec(
                name="itir.chatgpt.view_messages",
                title="Inspect messages in ChatGPT conversation",
                description="View recent tail or exact message index in a conversation from local SQLite archive without raw SQL.",
                input_schema={
                    "type": "object",
                    "required": ["conversation_id"],
                    "properties": {
                        "conversation_id": {"type": "string"},
                        "tail": {"type": "integer", "minimum": 0, "maximum": 100},
                        "message_index": {"type": "integer"},
                        "author": {"type": "string"},
                        "max_chars": {"type": "integer", "minimum": 0},
                        "db_path": {"type": "string"},
                    },
                    "additionalProperties": False,
                },
                response_version=SCHEMA_VERSION,
                read_only=True,
            ),
            view_messages,
        ),
        (
            ToolSpec(
                name="itir.chatgpt.fleet_status",
                title="Read fleet status summary",
                description="Summarize cluster rollups, thread counts, and active leads across the multi-thread fleet.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "db_path": {"type": "string"},
                    },
                    "additionalProperties": False,
                },
                response_version=SCHEMA_VERSION,
                read_only=True,
            ),
            fleet_status,
        ),
        (
            ToolSpec(
                name="itir.chatgpt.fleet_opportunities",
                title="Find high-alpha fleet opportunities",
                description="Scan the fleet for high-alpha research opportunities, target PRs, and recommended continuations.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "limit": {"type": "integer", "minimum": 1, "maximum": 100},
                        "min_score": {"type": "number", "minimum": 0.0},
                        "db_path": {"type": "string"},
                    },
                    "additionalProperties": False,
                },
                response_version=SCHEMA_VERSION,
                read_only=True,
            ),
            fleet_opportunities,
        ),
    ]
