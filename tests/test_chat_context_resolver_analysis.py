from __future__ import annotations

import datetime as dt
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import scripts.chat_context_resolver as resolver
from chat_context_resolver_lib.analysis import (
    analyze_thread_terms,
    parse_range_spec,
    parse_terms,
    top_terms,
)
from chat_context_resolver_lib.live_provider import load_session_token
from chat_context_resolver_lib.transcript import (
    build_stitched_transcript,
    filter_transcript_lines,
    latest_turn_datetime,
    truncate_text,
)


def _parse_message_ts(value: object):
    if value is None:
        return None
    text = str(value)
    return dt.datetime.fromisoformat(text.replace("Z", "+00:00"))


def _iso_utc_precise(value):
    if value is None:
        return None
    return value.astimezone(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def test_transcript_build_filter_and_analysis_are_stable():
    rows = [
        {
            "message_id": "m1",
            "ts": "2026-03-28T01:02:03Z",
            "role": "user",
            "text": "Alpha beta\nGamma alpha",
        },
        {
            "message_id": "m2",
            "ts": "2026-03-28T01:05:00Z",
            "role": "assistant",
            "text": "beta delta",
        },
    ]

    transcript = build_stitched_transcript(
        rows,
        parse_message_ts=_parse_message_ts,
        iso_utc_precise=_iso_utc_precise,
    )
    assert [line.thread_line for line in transcript] == [1, 2, 3]
    assert transcript[1].text == "Gamma alpha"
    assert transcript[2].ts_utc == "2026-03-28T01:05:00Z"

    filtered = filter_transcript_lines(transcript, thread_range=(2, 3), message_range=None)
    assert [line.thread_line for line in filtered] == [2, 3]

    analysis = analyze_thread_terms(
        transcript,
        terms=["alpha", "beta"],
        regex=False,
        case_sensitive=False,
        show_line_context=1,
    )
    term_stats = {item["term"]: item for item in analysis["term_stats"]}
    assert term_stats["alpha"]["raw_count"] == 2
    assert term_stats["beta"]["raw_count"] == 2
    assert analysis["mentions"][0]["line_context"][0]["thread_line"] == 1
    assert top_terms(transcript, 3)[0] == {"term": "alpha", "count": 2}


def test_helper_parsers_and_turn_datetime():
    assert truncate_text("abcdef", 3) == "abc\n...[truncated 3 chars]"
    assert parse_terms(["alpha, beta", "Alpha", "gamma"]) == ["alpha", "beta", "gamma"]
    assert parse_range_spec("2:5", "thread-range") == (2, 5)
    turns = [
        {"ts": "2026-03-28T01:02:03Z"},
        {"ts_utc": "2026-03-28T01:05:00Z"},
    ]
    assert latest_turn_datetime(turns, parse_message_ts=_parse_message_ts) == dt.datetime(
        2026, 3, 28, 1, 5, tzinfo=dt.timezone.utc
    )


def test_query_recent_turns_uses_shared_truncate_helper(tmp_path):
    db_path = tmp_path / "chat.sqlite"
    con = sqlite3.connect(db_path)
    con.execute(
        """
        CREATE TABLE messages (
            canonical_thread_id TEXT,
            ts TEXT,
            role TEXT,
            text TEXT
        )
        """
    )
    con.execute(
        """
        INSERT INTO messages (canonical_thread_id, ts, role, text)
        VALUES (?, ?, ?, ?)
        """,
        ("thread-1", "2026-03-28T01:02:03Z", "user", "abcdef"),
    )
    con.commit()
    con.close()

    turns = resolver._query_recent_turns(
        db_path,
        "thread-1",
        limit=5,
        max_text_chars=3,
    )

    assert len(turns) == 1
    assert turns[0]["text"] == "abc\n...[truncated 3 chars]"


def test_load_session_token_reads_chunked_new_session_file(monkeypatch, tmp_path):
    monkeypatch.delenv("CHATGPT_SESSION_TOKEN", raising=False)
    monkeypatch.setenv("HOME", str(tmp_path))
    (tmp_path / ".chatgpt_session_new").write_text("part-one\npart-two\n", encoding="utf-8")

    token = load_session_token()

    assert token == "part-onepart-two"


def test_load_session_token_prefers_config_ini_over_chunked_file(monkeypatch, tmp_path):
    monkeypatch.delenv("CHATGPT_SESSION_TOKEN", raising=False)
    monkeypatch.setenv("HOME", str(tmp_path))
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    (tmp_path / ".chatgpt_session_new").write_text("stale-token\n", encoding="utf-8")
    (repo_root / "config.ini").write_text("[session]\ntoken = fresh-config-token\n", encoding="utf-8")

    token = load_session_token(repo_root=repo_root)

    assert token == "fresh-config-token"
