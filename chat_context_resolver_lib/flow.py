from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from chat_context_resolver_lib.cli import RuntimeOptions


@dataclass(frozen=True)
class FlowDependencies:
    resolve_db_lookup: Callable[..., Any]
    looks_like_canonical_thread_id: Callable[[str], bool]
    looks_like_online_thread_id: Callable[[str], bool]
    query_recent_turns: Callable[..., list[dict]]
    fetch_web_recent_turns: Callable[..., dict[str, Any]]
    latest_turn_datetime: Callable[..., Any]
    run_web_view: Callable[..., dict[str, Any]]
    persist_selector_to_structurer: Callable[..., dict[str, Any]]
    db_payload: Callable[..., dict[str, Any]]
    cross_thread_analysis_payload: Callable[..., dict[str, Any]]
    thread_analysis_payload: Callable[..., dict[str, Any]]
    parse_message_ts: Callable[[object], Any]
    iso_utc: Callable[[Any], str | None]
    iso_utc_precise: Callable[[Any], str | None]
    split_paragraphs: Callable[[str], list[str]]
    truncate_text: Callable[[str, int], str]


def resolve_flow(
    args: Any,
    runtime: RuntimeOptions,
    *,
    repo_root: Path,
    deps: FlowDependencies,
) -> tuple[int, dict[str, Any]]:
    db_path = runtime.db_path
    venv_python_path = runtime.venv_python_path
    analysis_terms = runtime.analysis_terms
    selector_for_db = runtime.selector_for_db
    selector_for_web = runtime.selector_for_web
    thread_range = runtime.thread_range
    message_range = runtime.message_range
    analysis_requested = runtime.analysis_requested
    threshold = runtime.threshold

    db_lookup = deps.resolve_db_lookup(
        db_path,
        selector_for_db,
        candidate_limit=10,
        allow_canonical_match=deps.looks_like_canonical_thread_id(selector_for_db),
    )
    db_match = db_lookup.match
    db_error = db_lookup.warning
    db_candidates = db_lookup.candidates

    db_recent_turns: list[dict] = []
    if db_match is not None and args.recent_turns > 0:
        try:
            db_recent_turns = deps.query_recent_turns(
                db_path=db_path,
                thread_id=db_match.canonical_thread_id,
                limit=args.recent_turns,
                max_text_chars=args.max_text_chars,
            )
        except Exception as exc:
            extra = f"Unable to load recent turns: {exc}"
            db_error = f"{db_error}; {extra}" if db_error else extra

    needs_web = False
    reason = ""
    if db_match is None:
        if db_candidates:
            reason = "db_fts_candidates"
        else:
            needs_web = True
            reason = "not_found_in_db"
    elif threshold is not None:
        latest = db_match.latest_datetime
        if latest is None:
            needs_web = True
            reason = "db_timestamp_unparseable"
        elif threshold > latest:
            needs_web = True
            reason = "provided_datetime_newer_than_db"
        else:
            reason = "db_current_enough"
    else:
        reason = "db_match_found"

    preloaded_web_recent: dict[str, Any] | None = None
    if not needs_web and db_match is not None and args.check_web_newer and not args.no_web:
        web_selector: str | None = None
        if db_match.online_thread_id:
            web_selector = db_match.online_thread_id
        elif deps.looks_like_online_thread_id(selector_for_web):
            web_selector = selector_for_web
        elif db_match.title and db_match.title != "(no title)":
            web_selector = db_match.title
        if web_selector is None:
            extra = "Web freshness check skipped: no online id or title available"
            db_error = f"{db_error}; {extra}" if db_error else extra
        else:
            preloaded_web_recent = deps.fetch_web_recent_turns(
                selector=web_selector,
                repo_root=repo_root,
                limit=max(1, args.recent_turns),
                max_text_chars=args.max_text_chars,
                parse_message_ts=deps.parse_message_ts,
                iso_utc_precise=deps.iso_utc_precise,
                truncate_text=deps.truncate_text,
            )
            if preloaded_web_recent.get("ok"):
                web_turns = preloaded_web_recent.get("recent_turns") or []
                web_latest = deps.latest_turn_datetime(web_turns, parse_message_ts=deps.parse_message_ts)
                db_latest = db_match.latest_datetime
                if web_latest is not None and (db_latest is None or web_latest > db_latest):
                    needs_web = True
                    reason = "web_newer_than_db"
            else:
                extra = f"Web freshness check failed: {preloaded_web_recent.get('error')}"
                db_error = f"{db_error}; {extra}" if db_error else extra

    if args.cross_thread and db_path.exists():
        payload: dict[str, Any] = {
            "source": "db",
            "decision_reason": "cross_thread_analysis",
            "analysis": deps.cross_thread_analysis_payload(
                db_path,
                args.selector,
                terms=analysis_terms,
                regex=args.regex,
                case_sensitive=args.case_sensitive,
                limit=max(1, args.limit),
                max_text_chars=args.max_text_chars,
            ),
        }
        if db_candidates:
            payload["db_candidates"] = db_candidates
        if db_error:
            payload["db_warning"] = db_error
        return 0, payload

    if needs_web:
        if args.no_web:
            payload = {
                "source": "error",
                "decision_reason": reason,
                "error": "Web fallback disabled by --no-web.",
            }
            if db_error:
                payload["db_warning"] = db_error
            return 1, payload

        web_result = deps.run_web_view(
            selector_for_web,
            repo_root=repo_root,
            venv_python=venv_python_path,
            timeout=args.web_timeout,
        )
        if web_result.get("ok"):
            web_recent_turns: list[dict] = []
            web_recent_warning: str | None = None
            web_recent_meta: dict[str, Any] | None = None
            if args.recent_turns > 0:
                web_recent = preloaded_web_recent
                if not web_recent or not web_recent.get("ok") or len(web_recent.get("recent_turns") or []) < args.recent_turns:
                    web_recent = deps.fetch_web_recent_turns(
                        selector=selector_for_web,
                        repo_root=repo_root,
                        limit=args.recent_turns,
                        max_text_chars=args.max_text_chars,
                        parse_message_ts=deps.parse_message_ts,
                        iso_utc_precise=deps.iso_utc_precise,
                        truncate_text=deps.truncate_text,
                    )
                if web_recent.get("ok"):
                    web_recent_turns = web_recent.get("recent_turns") or []
                    web_recent_meta = {
                        "conversation_id": web_recent.get("conversation_id"),
                        "title": web_recent.get("title"),
                        "match_type": web_recent.get("match_type"),
                        "total_message_count": web_recent.get("total_message_count"),
                    }
                else:
                    web_recent_warning = web_recent.get("error")

            payload = {
                "source": "web",
                "decision_reason": reason,
                "web": web_result,
            }
            persist_result: dict[str, Any] | None = None
            if args.persist_web_miss:
                persist_result = deps.persist_selector_to_structurer(
                    selector_for_web,
                    repo_root=repo_root,
                    db_path=db_path,
                    venv_python=venv_python_path,
                    timeout=args.web_timeout,
                )
                if not persist_result.get("ok"):
                    extra = "Persistence pipeline failed (download and/or ingest)."
                    db_error = f"{db_error}; {extra}" if db_error else extra
            if web_recent_turns:
                payload["web_recent_turns"] = web_recent_turns
            if web_recent_meta is not None:
                payload["web_recent_turns_meta"] = web_recent_meta
            if web_recent_warning:
                payload["web_recent_turns_warning"] = web_recent_warning
            if persist_result is not None:
                payload["persist"] = persist_result
            if db_match is not None:
                payload["db_match"] = deps.db_payload(
                    db_match,
                    max_text_chars=args.max_text_chars,
                    latest_paragraphs=args.latest_paragraphs,
                    recent_turns=db_recent_turns,
                    truncate_text=deps.truncate_text,
                    split_paragraphs=deps.split_paragraphs,
                    iso_utc=deps.iso_utc,
                )
            if db_error:
                payload["db_warning"] = db_error
            return 0, payload

        payload = {
            "source": "error",
            "decision_reason": reason,
            "error": web_result.get("error") or "Web fallback failed.",
            "web": web_result,
        }
        if db_match is not None:
            payload["db_match"] = deps.db_payload(
                db_match,
                max_text_chars=args.max_text_chars,
                latest_paragraphs=args.latest_paragraphs,
                recent_turns=db_recent_turns,
                truncate_text=deps.truncate_text,
                split_paragraphs=deps.split_paragraphs,
                iso_utc=deps.iso_utc,
            )
        if db_error:
            payload["db_warning"] = db_error
        return 1, payload

    payload = {
        "source": "db",
        "decision_reason": reason,
    }
    if db_match is not None:
        payload["db_match"] = deps.db_payload(
            db_match,
            max_text_chars=args.max_text_chars,
            latest_paragraphs=args.latest_paragraphs,
            recent_turns=db_recent_turns,
            truncate_text=deps.truncate_text,
            split_paragraphs=deps.split_paragraphs,
            iso_utc=deps.iso_utc,
        )
    if db_candidates:
        payload["db_candidates"] = db_candidates
    if threshold is not None:
        payload["requested_threshold_utc"] = deps.iso_utc(threshold)
    if db_error:
        payload["db_warning"] = db_error
    if analysis_requested:
        if db_match is None:
            payload = {
                "source": "error",
                "decision_reason": reason,
                "error": "Thread-local analysis requires a resolved DB thread. Use --cross-thread for archive-wide ranking.",
            }
            if db_candidates:
                payload["db_candidates"] = db_candidates
            if db_error:
                payload["db_warning"] = db_error
            return 1, payload
        payload["analysis"] = deps.thread_analysis_payload(
            db_path,
            db_match.canonical_thread_id,
            terms=analysis_terms,
            regex=args.regex,
            case_sensitive=args.case_sensitive,
            thread_range=thread_range,
            message_range=message_range,
            show_lines=args.show_lines,
            show_line_context=max(0, args.show_line_context),
            top_terms_limit=max(0, args.top_terms),
            max_text_chars=args.max_text_chars,
        )
    return 0, payload
