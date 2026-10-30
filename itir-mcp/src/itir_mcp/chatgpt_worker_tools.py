"""Governed re-gpt worker operations exposed through the ITIR MCP registry."""

from __future__ import annotations

import importlib
from typing import Any, Mapping

from .contracts import JsonDict, ToolExecutionError, ToolInputError, ToolSpec


SCHEMA_VERSION = "itir.chatgpt_worker.v1"

GOLDEN_AGDA_REMINDER = (
    "Check dashi_lean4 and dashi_agda and formalise the current problem in terms of "
    "relevant in-repo machinery. and ensure to keep the formalism and docs in-step with the impl. "
    "recall the agdas are the golden."
)

WORKER_PROMPT_PRESETS: dict[str, str] = {
    "max_cut": (
        f"{GOLDEN_AGDA_REMINDER} Exactly complete all per max-cut and continue per "
        "pareto/snowball/ibrahim. Check the web and latest PRs for inspiration and "
        "cross-pollination -- assume we already have everything we need in-repo. "
        "Keep following your nose until you hit a wall -- do not wait for approval, "
        "and remember our attribution rules."
    ),
    "grug_ste100": (
        f"{GOLDEN_AGDA_REMINDER} Apply Grug-brain simplicity and ASD-STE100 Simplified "
        "Technical English: one thought per sentence, active voice, approved unambiguous terms, "
        "zero speculative abstraction, no inline code dumps in prose, and normalize onto "
        "existing in-repo surfaces."
    ),
    "grug": (
        f"{GOLDEN_AGDA_REMINDER} Apply Grug-brain simplicity and ASD-STE100 Simplified "
        "Technical English: one thought per sentence, active voice, approved unambiguous terms, "
        "zero speculative abstraction, no inline code dumps in prose, and normalize onto "
        "existing in-repo surfaces."
    ),
    "zkp_qa": (
        f"{GOLDEN_AGDA_REMINDER} Frame via ZKP (O/R/C/S/L/P/G/F) with explicit "
        "preconditions, invariants, and postconditions. Converge toward normalized surfaces "
        "per ITIL, ISO 9000/42001/27001/27701/23894/9241, NIST AI RMF, Six Sigma, and "
        "C4/PlantUML. Assign one disjoint nonblocking lane per worker, no skeletons or stubs, "
        "and complete implementation + deterministic verification within the turn."
    ),
    "zkp": (
        f"{GOLDEN_AGDA_REMINDER} Frame via ZKP (O/R/C/S/L/P/G/F) with explicit "
        "preconditions, invariants, and postconditions. Converge toward normalized surfaces "
        "per ITIL, ISO 9000/42001/27001/27701/23894/9241, NIST AI RMF, Six Sigma, and "
        "C4/PlantUML. Assign one disjoint nonblocking lane per worker, no skeletons or stubs, "
        "and complete implementation + deterministic verification within the turn."
    ),
    "introspective_viz": (
        f"{GOLDEN_AGDA_REMINDER} Apply the introspective method: 1. Model the theory "
        "accurately per actual implementation. 2. Generate a plain-language, physically "
        "intuitive visual proof (Python/HTML/SVG). 3. Inspect the visualization. "
        "4. Formalize new findings in Lean or Agda per repo convention."
    ),
    "converge_toe": (
        f"{GOLDEN_AGDA_REMINDER} Converge toward the DASHI TOE: dashi_agda "
        "DASHI/EverythingTOESymmetryResolved369.agda, DASHI/Unifier.agda and DASHI/Unified/. "
        "Assume the content already exists in-repo. Search first for existing, duplicate or near "
        "constructions (GitHub code search; the local referee confirms with dashi-agda-preflight "
        "related_symbols/discover/round_lineage). Order: reuse, then unify duplicates, then extend, "
        "then construct new. Attach every new result to the TOE import graph. Do not edit ESD "
        "surfaces (dashi_digital_esd repo, *digital_esd* and *ESD* modules); import only. "
        "Keep attribution for meta-introspector repos."
    ),
    "referee_pass": (
        f"{GOLDEN_AGDA_REMINDER} Local referee verification passed (0 errors, 0 warnings). "
        "Proceed immediately to the next highest-alpha vertical slice per max-cut and "
        "pareto/snowball/ibrahim; push commits and return SHAs + deterministic referee commands."
    ),
    "rpd": (
        f"{GOLDEN_AGDA_REMINDER} So where does that leave us re roadmap/phase/deliverables? "
        "Please check agdas/repo docs/planning etc."
    ),
    "steelman": (
        f"{GOLDEN_AGDA_REMINDER} So what does the dream/steelman solution look like?"
    ),
    "lemmas": (
        f"{GOLDEN_AGDA_REMINDER} List every required lemma between here -> completed. "
        "Please check agdas/repo docs/planning etc."
    ),
    "surrounds": (
        f"{GOLDEN_AGDA_REMINDER} Check the parent/child/surrounding/related "
        "formalisms/repos/docs relevant to our current task and contextualise our "
        "requirements/goals/situation in terms of our prior-art."
    ),
    "docs": (
        f"{GOLDEN_AGDA_REMINDER} Synchronize and update project documentation, "
        "ROADMAP.md, planning docs, TODO items, and changelogs per "
        "update-docs-todo-implement doctrine (Docs → TODOs → Code → Changelog). "
        "Ensure all planning is up to date, reflect intended behaviors, and verify strict "
        "alignment across docs, tasks, and implementation."
    ),
    "snowball": (
        f"{GOLDEN_AGDA_REMINDER} Exactly complete all per max-cut and continue per "
        "pareto/snowball/ibrahim check the web and latest PRs for inspo -- assume we "
        "already have everything we need in-repo. keep following your nose until you hit "
        "a wall -- don't wait for my approval re all this and remember our attribution rules "
        "ensure we have covered all the requested topics then keep going more.. dont worry "
        "about CI - ensure you have a roadmap doc to keep track of all these."
    ),
    "max_cut_snowball": (
        f"{GOLDEN_AGDA_REMINDER} Exactly complete all per max-cut and continue per "
        "pareto/snowball/ibrahim check the web and latest PRs for inspo -- assume we "
        "already have everything we need in-repo. keep following your nose until you hit "
        "a wall -- don't wait for my approval re all this and remember our attribution rules "
        "ensure we have covered all the requested topics then keep going more.. dont worry "
        "about CI - ensure you have a roadmap doc to keep track of all these."
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
    if not resolved.startswith(GOLDEN_AGDA_REMINDER):
        resolved = f"{GOLDEN_AGDA_REMINDER}\n\n{resolved}"
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
    auto_latex_bridge = payload.get("auto_latex_bridge", False)
    if not isinstance(auto_latex_bridge, bool):
        raise ToolInputError("Expected boolean field: auto_latex_bridge")
    pnf_mode = payload.get("pnf_mode", False)
    if not isinstance(pnf_mode, bool):
        raise ToolInputError("Expected boolean field: pnf_mode")
    reconcile_attempts = payload.get("reconcile_attempts", 3)
    if not isinstance(reconcile_attempts, int) or reconcile_attempts < 0:
        raise ToolInputError("Expected non-negative integer field: reconcile_attempts")

    bridge_capsule: dict[str, Any] | None = None
    if pnf_mode or auto_latex_bridge:
        from .latex_math_bridge import distill_pnf_capsule

        capsule = distill_pnf_capsule(prompt, conversation_id=conversation_id)
        bridge_capsule = capsule.to_dict()
        if pnf_mode:
            prompt = capsule.condensed_prompt_text

    result = _worker_api().chatgpt_continue(
        conversation_id=conversation_id,
        prompt=prompt,
        attachments=attachments,
        follow=follow,
        write_transport="async",
        dom_fallback=False,
        db_path=db_path,
        reconcile_attempts=reconcile_attempts,
    )
    ret = {
        "version": SCHEMA_VERSION,
        "operation": _compact_operation(result),
        "policy": {
            "write_transport": "async",
            "dom_fallback": False,
            "automatic_resend": False,
        },
    }
    if bridge_capsule is not None:
        ret["latex_bridge"] = bridge_capsule
    return ret


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
    keywords = payload.get("keywords")
    if keywords is not None and (not isinstance(keywords, list) or not all(isinstance(k, str) for k in keywords)):
        raise ToolInputError("Expected list of strings: keywords")
    order_by = payload.get("order_by", "recent")
    if not isinstance(order_by, str) or order_by not in {"recent", "turns"}:
        raise ToolInputError("Expected order_by to be 'recent' or 'turns'")
    min_turns = payload.get("min_turns", 0)
    if not isinstance(min_turns, int) or min_turns < 0:
        raise ToolInputError("Expected non-negative integer field: min_turns")
    db_path = _optional_db_path(payload)
    rows = _worker_api().chatgpt_list(
        limit=limit,
        query=query,
        keywords=keywords,
        order_by=order_by,
        min_turns=min_turns,
        db_path=db_path,
    )
    return {
        "version": SCHEMA_VERSION,
        "count": len(rows),
        "threads": rows,
    }


def revive(payload: Mapping[str, Any]) -> JsonDict:
    """Revive an existing long-running thread into a fresh thread with clean context and recorded lineage."""
    conversation_id = _required_text(payload, "conversation_id")
    prompt = _resolve_prompt(payload)
    attachments = payload.get("attachments", [])
    if not isinstance(attachments, list) or not all(isinstance(p, str) for p in attachments):
        raise ToolInputError("Expected list of string paths: attachments")
    follow = payload.get("follow", False)
    if not isinstance(follow, bool):
        raise ToolInputError("Expected boolean field: follow")
    output = payload.get("output")
    if output is not None and not isinstance(output, str):
        raise ToolInputError("Expected string field: output")
    db_path = _optional_db_path(payload)
    result = _worker_api().chatgpt_revive(
        conversation_id=conversation_id,
        prompt=prompt,
        attachments=attachments,
        follow=follow,
        output=output,
        db_path=db_path,
    )
    return {
        "version": SCHEMA_VERSION,
        "operation": _compact_operation(result),
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


def session_refresh(payload: Mapping[str, Any]) -> JsonDict:
    """Refresh the saved ChatGPT session snapshot using displayless browser replay."""
    profile_dir = payload.get("profile_dir")
    if profile_dir is not None and not isinstance(profile_dir, str):
        raise ToolInputError("Expected string field: profile_dir")
    snapshot_path = payload.get("snapshot_path")
    if snapshot_path is not None and not isinstance(snapshot_path, str):
        raise ToolInputError("Expected string field: snapshot_path")
    browser_mode = payload.get("browser_mode", "displayless")
    if not isinstance(browser_mode, str):
        raise ToolInputError("Expected string field: browser_mode")
    api = _worker_api()
    try:
        refreshed = api.chatgpt_session_refresh(
            profile_dir=profile_dir,
            snapshot_path=snapshot_path,
            browser_mode=browser_mode,
        )
        return {
            "version": SCHEMA_VERSION,
            "session": refreshed,
        }
    except Exception as exc:
        raise ToolExecutionError(f"Session refresh failed: {exc}") from exc


def get_access_token_tool(payload: Mapping[str, Any]) -> JsonDict:
    """Retrieve active ChatGPT access token using automatic session resolution."""
    api = _worker_api()
    try:
        if hasattr(api, "chatgpt_get_access_token"):
            result = api.chatgpt_get_access_token()
            return {
                "version": SCHEMA_VERSION,
                **result,
            }
        from re_gpt.async_chatgpt import AsyncChatGPT
        from re_gpt.async_bridge import run_async_sync

        async def run() -> str:
            async with AsyncChatGPT() as client:
                return await client.fetch_auth_token()

        token = run_async_sync(run)
        return {
            "version": SCHEMA_VERSION,
            "ok": bool(token),
            "access_token": token,
            "token_length": len(token) if token else 0,
        }
    except Exception as exc:
        raise ToolExecutionError(f"Failed to retrieve access token: {exc}") from exc


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


def tranche_status(payload: Mapping[str, Any]) -> JsonDict:
    """Query tranche candidates and completed attempt counts across the fleet archive."""
    prefix = str(payload.get("prefix") or "6a")
    min_turns = payload.get("min_turns", 50)
    if not isinstance(min_turns, int) or min_turns < 1:
        min_turns = 50
    db_path = _optional_db_path(payload)
    try:
        from re_gpt.mcp_server import chatgpt_tranche_status
        return chatgpt_tranche_status(prefix=prefix, min_turns=min_turns, db_path=db_path)
    except Exception as exc:
        raise ToolExecutionError(f"tranche status failed: {exc}") from exc


def fleet_telemetry(payload: Mapping[str, Any]) -> JsonDict:
    """Query live multi-thread fleet activity across the active operations window."""
    window_seconds = payload.get("window_seconds", 120)
    if not isinstance(window_seconds, int) or window_seconds < 1:
        window_seconds = 120
    limit = payload.get("limit", 20)
    if not isinstance(limit, int) or limit < 1 or limit > 100:
        limit = 20
    db_path = _optional_db_path(payload)
    try:
        from re_gpt.mcp_server import chatgpt_fleet_telemetry
        return chatgpt_fleet_telemetry(window_seconds=window_seconds, limit=limit, db_path=db_path)
    except Exception as exc:
        raise ToolExecutionError(f"fleet telemetry failed: {exc}") from exc


def formal_latex_bridge(payload: Mapping[str, Any]) -> JsonDict:
    """Extract LaTeX math AST without regex, search in-repo formal definitions, and generate proof stub."""
    text = _required_text(payload, "text")
    root_dir = payload.get("root_dir")
    from .latex_math_bridge import distill_pnf_capsule

    capsule = distill_pnf_capsule(text, root_dir=root_dir)
    return {
        "version": SCHEMA_VERSION,
        **capsule.to_dict(),
    }


def pnf_distill_prompt(payload: Mapping[str, Any]) -> JsonDict:
    """Condense research text into pure PNF predicate atoms and in-repo formal links (~99% token reduction)."""
    text = _required_text(payload, "text")
    conversation_id = payload.get("conversation_id")
    root_dir = payload.get("root_dir")
    from .latex_math_bridge import distill_pnf_capsule

    capsule = distill_pnf_capsule(text, conversation_id=conversation_id, root_dir=root_dir)
    return {
        "version": SCHEMA_VERSION,
        "distilled_prompt": capsule.condensed_prompt_text,
        "compression_ratio": capsule.compression_ratio,
        "original_chars": capsule.original_char_count,
        "distilled_chars": capsule.distilled_char_count,
        "pnf_atoms": capsule.pnf_atoms,
        "math_expressions": capsule.math_expressions,
        "matched_symbols": capsule.matched_repo_symbols,
        "proof_linkage_stub": capsule.proof_linkage_stub,
    }


def get_chatgpt_worker_tools() -> list[tuple[ToolSpec, Any]]:
    return [
        (
            ToolSpec(
                name="itir.chatgpt.list_threads",
                title="List or search archived ChatGPT conversations",
                description="List recent conversations or search by query substring or multi-keywords in local SQLite, ordered by recency or turns.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "limit": {"type": "integer", "minimum": 1, "maximum": 500},
                        "query": {"type": "string"},
                        "keywords": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Multi-keyword filter (matches any of the supplied keywords in title).",
                        },
                        "order_by": {
                            "type": "string",
                            "enum": ["recent", "turns"],
                            "description": "Sort order: 'recent' (default) or 'turns' (descending message count).",
                        },
                        "min_turns": {
                            "type": "integer",
                            "minimum": 0,
                            "description": "Minimum turns threshold (e.g. 50).",
                        },
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
                name="itir.chatgpt.revive",
                title="Revive long-running thread with clean context and recorded lineage",
                description="Revive a predecessor conversation into a fresh thread, attaching structured history memo and recording lineage.",
                input_schema={
                    "type": "object",
                    "required": ["conversation_id"],
                    "properties": {
                        "conversation_id": {"type": "string"},
                        "prompt": {"type": "string"},
                        "preset": {"type": "string"},
                        "attachments": {"type": "array", "items": {"type": "string"}},
                        "follow": {"type": "boolean"},
                        "output": {"type": "string"},
                        "db_path": {"type": "string"},
                    },
                    "additionalProperties": False,
                },
                response_version=SCHEMA_VERSION,
                read_only=False,
            ),
            revive,
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
                name="itir.chatgpt.session_refresh",
                title="Refresh CFFI session snapshot headless",
                description="Refresh the saved ChatGPT session snapshot via displayless browser replay, renewing access token and fresh cookies.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "profile_dir": {"type": "string"},
                        "snapshot_path": {"type": "string"},
                        "browser_mode": {"type": "string", "default": "displayless"},
                    },
                    "additionalProperties": False,
                },
                response_version=SCHEMA_VERSION,
                read_only=False,
            ),
            session_refresh,
        ),
        (
            ToolSpec(
                name="itir.chatgpt.get_access_token",
                title="Get active ChatGPT access token",
                description="Retrieve active ChatGPT access token automatically loaded from ~/.chatgpt_session or local session snapshot.",
                input_schema={
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False,
                },
                response_version=SCHEMA_VERSION,
                read_only=True,
            ),
            get_access_token_tool,
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
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "conversation_id": {"type": "string", "minLength": 1},
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
                        "auto_latex_bridge": {"type": "boolean", "description": "Auto-extract LaTeX math and link to in-repo formal symbols."},
                        "pnf_mode": {"type": "boolean", "description": "Distill prompt through PNF reduction before dispatch (~99% token reduction)."},
                        "reconcile_attempts": {"type": "integer", "minimum": 0, "maximum": 10, "description": "Number of full-graph reconciliation attempts. Set 0 for fast submission mode without multi-MB graph pulls."},
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
        (
            ToolSpec(
                name="itir.formal.latex_bridge",
                title="Extract LaTeX Math & Link to Formal In-Repo Symbols",
                description="Extract LaTeX math AST via pylatexenc/sympy without regex, search in-repo formal definitions, and generate an Agda/Lean4 proof stub.",
                input_schema={
                    "type": "object",
                    "required": ["text"],
                    "properties": {
                        "text": {"type": "string", "description": "Text containing LaTeX math formulas to parse."},
                        "root_dir": {"type": "string", "description": "Optional repository root path."},
                    },
                    "additionalProperties": False,
                },
                response_version=SCHEMA_VERSION,
                read_only=True,
            ),
            formal_latex_bridge,
        ),
        (
            ToolSpec(
                name="itir.pnf.distill_prompt",
                title="Distill Text into Pure PNF Submission Capsule",
                description="Condense research text into pure PNF predicate atoms and in-repo formal links (~99% token reduction).",
                input_schema={
                    "type": "object",
                    "required": ["text"],
                    "properties": {
                        "text": {"type": "string", "description": "Informal text or prompt to distill into pure PNF."},
                        "conversation_id": {"type": "string", "description": "Optional target conversation ID."},
                        "root_dir": {"type": "string", "description": "Optional repository root path."},
                    },
                    "additionalProperties": False,
                },
                response_version=SCHEMA_VERSION,
                read_only=True,
            ),
            pnf_distill_prompt,
        ),
        (
            ToolSpec(
                name="itir.chatgpt.tranche_status",
                title="Query tranche burndown candidates and counts",
                description="Query tranche candidates and completed attempt counts across the fleet archive.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "prefix": {"type": "string", "default": "6a"},
                        "min_turns": {"type": "integer", "default": 50},
                        "db_path": {"type": "string"},
                    },
                    "additionalProperties": False,
                },
                response_version=SCHEMA_VERSION,
                read_only=True,
            ),
            tranche_status,
        ),
        (
            ToolSpec(
                name="itir.chatgpt.fleet_telemetry",
                title="Query live multi-thread fleet telemetry",
                description="Query live multi-thread fleet activity across the active operations window.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "window_seconds": {"type": "integer", "default": 120},
                        "limit": {"type": "integer", "default": 20},
                        "db_path": {"type": "string"},
                    },
                    "additionalProperties": False,
                },
                response_version=SCHEMA_VERSION,
                read_only=True,
            ),
            fleet_telemetry,
        ),
    ]
