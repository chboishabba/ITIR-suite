from __future__ import annotations

import argparse
import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import scripts.chat_context_resolver as resolver
from chat_context_resolver_lib.analysis import parse_range_spec, parse_terms
from chat_context_resolver_lib.cli import resolve_runtime_options
from chat_context_resolver_lib.formatters import print_result
from chat_context_resolver_lib.live_provider import extract_online_thread_id_from_url


def _args(**overrides) -> argparse.Namespace:
    defaults = {
        "selector": "  https://chatgpt.com/c/12345678-1234-1234-1234-123456789abc  ",
        "db": "sqlite/chat_archive.sqlite",
        "if_newer_than": None,
        "venv_python": ".venv/bin/python",
        "web_timeout": 120,
        "no_web": False,
        "persist_web_miss": False,
        "json": False,
        "max_text_chars": 1200,
        "latest_paragraphs": False,
        "recent_turns": 0,
        "check_web_newer": False,
        "analyze_term": [],
        "term_file": None,
        "case_sensitive": False,
        "regex": False,
        "thread_range": None,
        "message_range": None,
        "show_lines": False,
        "show_line_context": 0,
        "term_frequency": False,
        "mention_density": False,
        "top_terms": 0,
        "cross_thread": False,
        "limit": 10,
    }
    defaults.update(overrides)
    return argparse.Namespace(**defaults)


def test_resolve_runtime_options_normalizes_paths_and_flags(tmp_path: Path) -> None:
    term_file = tmp_path / "terms.txt"
    term_file.write_text("Alpha\nbeta\n", encoding="utf-8")
    args = _args(
        term_file=str(term_file.relative_to(tmp_path)),
        analyze_term=["gamma, delta"],
        thread_range="2:8",
        message_range="1:2",
        show_lines=True,
        if_newer_than="2026-03-29T00:00:00Z",
    )

    runtime = resolve_runtime_options(
        args,
        repo_root=tmp_path,
        parse_terms=parse_terms,
        parse_range_spec=parse_range_spec,
        parse_datetime=resolver._parse_datetime,
        extract_online_thread_id=extract_online_thread_id_from_url,
    )

    assert runtime.db_path == tmp_path / "sqlite/chat_archive.sqlite"
    assert runtime.venv_python_path == tmp_path / ".venv/bin/python"
    assert runtime.selector_for_db == "12345678-1234-1234-1234-123456789abc"
    assert runtime.selector_for_web == "12345678-1234-1234-1234-123456789abc"
    assert runtime.analysis_terms == ["gamma", "delta", "Alpha", "beta"]
    assert runtime.thread_range == (2, 8)
    assert runtime.message_range == (1, 2)
    assert runtime.analysis_requested is True
    assert runtime.threshold == dt.datetime(2026, 3, 29, 0, 0, tzinfo=dt.timezone.utc)


def test_resolve_runtime_options_reports_missing_term_file(tmp_path: Path) -> None:
    args = _args(term_file="missing-terms.txt")

    try:
        resolve_runtime_options(
            args,
            repo_root=tmp_path,
            parse_terms=parse_terms,
            parse_range_spec=parse_range_spec,
            parse_datetime=resolver._parse_datetime,
            extract_online_thread_id=extract_online_thread_id_from_url,
        )
    except ValueError as exc:
        assert str(exc) == f"Term file does not exist: {tmp_path / 'missing-terms.txt'}"
    else:
        raise AssertionError("Expected ValueError for missing --term-file")


def test_print_result_db_plaintext_still_includes_recent_turns(capsys) -> None:
    payload = {
        "source": "db",
        "decision_reason": "db_match_found",
        "db_match": {
            "match_type": "canonical_thread_id_exact",
            "title": "Example Thread",
            "online_thread_id": "12345678-1234-1234-1234-123456789abc",
            "canonical_thread_id": "a" * 40,
            "earliest_ts_utc": "2026-03-28T00:00:00+00:00",
            "latest_ts_utc": "2026-03-28T01:00:00+00:00",
            "latest_role": "assistant",
            "thread_message_count": 2,
            "matched_thread_count": 1,
            "latest_text": "Last message",
            "latest_paragraphs": ["p1", "p2"],
            "recent_turns": [
                {
                    "ts": "2026-03-28T01:00:00Z",
                    "ts_utc": "2026-03-28T01:00:00Z",
                    "role": "assistant",
                    "text": "turn text",
                }
            ],
        },
    }

    print_result(payload, as_json=False)
    out = capsys.readouterr().out
    assert "source: db" in out
    assert "latest_paragraphs:" in out
    assert "recent_turns:" in out
    assert "turn text" in out
