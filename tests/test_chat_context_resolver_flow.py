from __future__ import annotations

import argparse
import datetime as dt
from pathlib import Path

from chat_context_resolver_lib.cli import RuntimeOptions
from chat_context_resolver_lib.flow import FlowDependencies, resolve_flow


class _Match:
    def __init__(self, *, canonical_thread_id: str = "thread-1", online_thread_id: str | None = None, title: str = "Example", latest_datetime=None):
        self.canonical_thread_id = canonical_thread_id
        self.online_thread_id = online_thread_id
        self.title = title
        self.latest_datetime = latest_datetime


class _Lookup:
    def __init__(self, *, match=None, warning=None, candidates=None):
        self.match = match
        self.warning = warning
        self.candidates = candidates or []


def _args(**overrides):
    defaults = {
        "selector": "selector",
        "web_timeout": 30,
        "no_web": False,
        "persist_web_miss": False,
        "recent_turns": 0,
        "max_text_chars": 1200,
        "latest_paragraphs": False,
        "check_web_newer": False,
        "cross_thread": False,
        "json": False,
        "regex": False,
        "case_sensitive": False,
        "limit": 10,
        "show_lines": False,
        "show_line_context": 0,
        "top_terms": 0,
    }
    defaults.update(overrides)
    return argparse.Namespace(**defaults)


def _runtime(tmp_path: Path, **overrides):
    defaults = {
        "selector_input": "selector",
        "selector_for_db": "selector",
        "selector_for_web": "selector",
        "db_path": tmp_path / "archive.sqlite",
        "venv_python_path": tmp_path / ".venv/bin/python",
        "analysis_terms": [],
        "thread_range": None,
        "message_range": None,
        "analysis_requested": False,
        "threshold": None,
    }
    defaults.update(overrides)
    return RuntimeOptions(**defaults)


def _deps(**overrides) -> FlowDependencies:
    defaults = {
        "resolve_db_lookup": lambda *args, **kwargs: _Lookup(),
        "looks_like_canonical_thread_id": lambda value: False,
        "looks_like_online_thread_id": lambda value: False,
        "query_recent_turns": lambda **kwargs: [],
        "fetch_web_recent_turns": lambda **kwargs: {"ok": True, "recent_turns": []},
        "latest_turn_datetime": lambda turns, parse_message_ts=None: None,
        "run_web_view": lambda selector, repo_root, venv_python, timeout: {"ok": True, "stdout": "ok"},
        "persist_selector_to_structurer": lambda **kwargs: {"ok": True},
        "db_payload": lambda match, **kwargs: {"canonical_thread_id": match.canonical_thread_id},
        "cross_thread_analysis_payload": lambda *args, **kwargs: {"analysis_scope": "cross_thread", "results": []},
        "thread_analysis_payload": lambda *args, **kwargs: {"analysis_scope": "thread_local"},
        "parse_message_ts": lambda value: value,
        "iso_utc": lambda value: value.isoformat() if hasattr(value, "isoformat") else value,
        "iso_utc_precise": lambda value: value.isoformat() if hasattr(value, "isoformat") else value,
        "split_paragraphs": lambda value: [value],
        "truncate_text": lambda text, limit: text,
    }
    defaults.update(overrides)
    return FlowDependencies(**defaults)


def test_resolve_flow_returns_db_payload_for_db_match(tmp_path: Path) -> None:
    runtime = _runtime(tmp_path)
    args = _args()
    deps = _deps(resolve_db_lookup=lambda *args, **kwargs: _Lookup(match=_Match()))

    exit_code, payload = resolve_flow(args, runtime, repo_root=tmp_path, deps=deps)

    assert exit_code == 0
    assert payload["source"] == "db"
    assert payload["decision_reason"] == "db_match_found"
    assert payload["db_match"]["canonical_thread_id"] == "thread-1"


def test_resolve_flow_returns_no_web_error_when_web_disabled(tmp_path: Path) -> None:
    runtime = _runtime(tmp_path)
    args = _args(no_web=True)
    deps = _deps(resolve_db_lookup=lambda *args, **kwargs: _Lookup())

    exit_code, payload = resolve_flow(args, runtime, repo_root=tmp_path, deps=deps)

    assert exit_code == 1
    assert payload["source"] == "error"
    assert payload["decision_reason"] == "not_found_in_db"
    assert payload["error"] == "Web fallback disabled by --no-web."


def test_resolve_flow_routes_cross_thread_analysis(tmp_path: Path) -> None:
    db_path = tmp_path / "archive.sqlite"
    db_path.write_text("", encoding="utf-8")
    runtime = _runtime(tmp_path, db_path=db_path, analysis_terms=["alpha"], analysis_requested=True)
    args = _args(cross_thread=True, limit=3, regex=True)
    deps = _deps(
        resolve_db_lookup=lambda *args, **kwargs: _Lookup(candidates=[{"canonical_thread_id": "thread-1"}]),
        cross_thread_analysis_payload=lambda *args, **kwargs: {"analysis_scope": "cross_thread", "results": [{"id": "thread-1"}]},
    )

    exit_code, payload = resolve_flow(args, runtime, repo_root=tmp_path, deps=deps)

    assert exit_code == 0
    assert payload["decision_reason"] == "cross_thread_analysis"
    assert payload["analysis"]["analysis_scope"] == "cross_thread"


def test_main_uses_shared_flow_owner() -> None:
    source = (Path(__file__).resolve().parents[1] / "scripts" / "chat_context_resolver.py").read_text(encoding="utf-8")
    assert "from chat_context_resolver_lib.flow import (" in source
    assert "_resolve_flow(" in source
    assert "return exit_code" in source
