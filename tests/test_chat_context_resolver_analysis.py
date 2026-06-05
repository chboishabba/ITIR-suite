from __future__ import annotations

import datetime as dt
import json
import sqlite3
import subprocess
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
from chat_context_resolver_lib import live_provider
from chat_context_resolver_lib.cli import build_parser
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


def test_resolver_parser_exposes_opt_in_mca_flags():
    parser = build_parser()

    default_args = parser.parse_args(["needle"])
    provider_args = parser.parse_args(["needle", "--provider", "perplexity"])
    semantic_args = parser.parse_args(
        [
            "needle",
            "--semantic",
            "--mca-db",
            "/tmp/mca.sqlite",
            "--mca-limit",
            "7",
        ]
    )
    hybrid_args = parser.parse_args(["needle", "--hybrid"])

    assert default_args.semantic is False
    assert default_args.hybrid is False
    assert default_args.provider == "auto"
    assert default_args.mca_db is None
    assert default_args.mca_limit == 10
    assert provider_args.provider == "perplexity"
    assert semantic_args.semantic is True
    assert semantic_args.mca_db == "/tmp/mca.sqlite"
    assert semantic_args.mca_limit == 7
    assert hybrid_args.hybrid is True
    assert default_args.progress is False
    assert default_args.progress_interval == 2.0


def _make_fts_db(db_path: Path) -> None:
    con = sqlite3.connect(db_path)
    con.executescript(
        """
        CREATE TABLE messages (
          message_id TEXT PRIMARY KEY,
          canonical_thread_id TEXT NOT NULL,
          ts TEXT NOT NULL,
          role TEXT NOT NULL,
          text TEXT NOT NULL,
          title TEXT
        );
        CREATE VIRTUAL TABLE messages_fts USING fts5(text, content='');
        CREATE TABLE messages_fts_docids (
          rowid INTEGER PRIMARY KEY,
          message_id TEXT NOT NULL
        );
        """
    )
    con.execute(
        """
        INSERT INTO messages (message_id, canonical_thread_id, ts, role, text, title)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        ("dummy", "dummy-thread", "2026-01-01T00:00:00Z", "user", "wrong dart", "dummy"),
    )
    con.execute(
        """
        INSERT INTO messages (message_id, canonical_thread_id, ts, role, text, title)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        ("real-1", "real-thread", "2026-01-02T00:00:00Z", "assistant", "Dart dart\nother", "real"),
    )
    con.execute("INSERT INTO messages_fts (text) VALUES (?)", ("Dart dart\nother",))
    fts_rowid = con.execute("SELECT max(rowid) FROM messages_fts").fetchone()[0]
    con.execute(
        "INSERT INTO messages_fts_docids (rowid, message_id) VALUES (?, ?)",
        (fts_rowid, "real-1"),
    )
    con.commit()
    con.close()


def test_fts_candidates_use_docid_mapping_not_message_rowid(tmp_path):
    from chat_context_resolver_lib.db_lookup import connect_sqlite_ro, query_db_fts_candidates

    db_path = tmp_path / "chat.sqlite"
    _make_fts_db(db_path)
    con = connect_sqlite_ro(db_path)
    rows = query_db_fts_candidates(con.cursor(), "dart", limit=5)
    con.close()

    assert rows[0]["canonical_thread_id"] == "real-thread"
    assert rows[0]["title"] == "real"


def test_cross_thread_analysis_uses_fast_fts_hit_aggregation(tmp_path):
    db_path = tmp_path / "chat.sqlite"
    _make_fts_db(db_path)

    payload = resolver._cross_thread_analysis_payload(
        db_path,
        "dart",
        terms=["dart"],
        regex=False,
        case_sensitive=False,
        limit=5,
        max_text_chars=120,
    )

    assert payload["mode"] == "fts_hit_aggregation"
    assert payload["performance"]["fts_hit_rows"] == 1
    assert payload["results"][0]["canonical_thread_id"] == "real-thread"
    assert payload["results"][0]["raw_count"] == 2
    assert payload["results"][0]["line_hit_count"] == 1
    assert payload["results"][0]["first_hits"][0]["message_id"] == "real-1"


def test_resolver_progress_goes_to_stderr_and_json_to_stdout(tmp_path, capsys, monkeypatch):
    db_path = tmp_path / "chat.sqlite"
    _make_fts_db(db_path)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "chat_context_resolver.py",
            "dart",
            "--db",
            str(db_path),
            "--analyze-term",
            "dart",
            "--cross-thread",
            "--progress",
            "--json",
        ],
    )

    assert resolver.main() == 0
    captured = capsys.readouterr()
    stdout_payload = json.loads(captured.out)
    stderr_events = [json.loads(line) for line in captured.err.splitlines()]

    assert stdout_payload["analysis"]["mode"] == "fts_hit_aggregation"
    assert all(event["type"] == "progress" for event in stderr_events)
    assert any(event["stage"] == "hit_aggregation" for event in stderr_events)


def test_mca_retrieval_reports_missing_wrapper_without_subprocess(tmp_path, monkeypatch):
    def fail_run(*args, **kwargs):
        raise AssertionError("subprocess should not run when wrapper script is missing")

    monkeypatch.setattr(resolver.subprocess, "run", fail_run)

    result = resolver._run_mca_retrieval(
        mode="semantic",
        selector="database architecture",
        repo_root=tmp_path,
        db_path=tmp_path / "chat.sqlite",
        mca_db=None,
        limit=5,
        venv_python=tmp_path / ".venv/bin/python",
        timeout=1,
        max_text_chars=120,
    )

    assert result["ok"] is False
    assert "mca_semantic_search.py" in result["error"]
    assert result["requested"]["mode"] == "semantic"
    assert result["candidates"] == []


def test_mca_retrieval_invokes_lane_two_wrapper_contract(tmp_path, monkeypatch):
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir()
    (scripts_dir / "mca_hybrid_search.py").write_text("# placeholder\n", encoding="utf-8")
    seen = {}

    def fake_run(cmdline, **kwargs):
        seen["cmdline"] = cmdline
        return subprocess.CompletedProcess(
            cmdline,
            0,
            stdout='{"candidates": [{"canonical_thread_id": "abc", "score": 0.9}]}',
            stderr="",
        )

    monkeypatch.setattr(resolver.subprocess, "run", fake_run)

    result = resolver._run_mca_retrieval(
        mode="hybrid",
        selector="database architecture",
        repo_root=tmp_path,
        db_path=tmp_path / "chat.sqlite",
        mca_db=tmp_path / "mca.sqlite",
        limit=5,
        venv_python=tmp_path / ".venv/bin/python",
        timeout=1,
        max_text_chars=120,
    )

    assert result["ok"] is True
    assert "--canonical-db" in seen["cmdline"]
    assert str(tmp_path / "chat.sqlite") in seen["cmdline"]
    assert "--mca-db" in seen["cmdline"]
    assert str(tmp_path / "mca.sqlite") in seen["cmdline"]
    assert result["candidates"] == [{"canonical_thread_id": "abc", "score": 0.9, "rank": 1}]


def test_extract_mca_candidates_accepts_lane_two_result_shapes():
    assert resolver._extract_mca_candidates(
        {"results": [{"canonical_thread_id": "abc", "score": 0.9}]}
    ) == [{"canonical_thread_id": "abc", "score": 0.9, "rank": 1}]
    assert resolver._extract_mca_candidates(
        {"candidates": [{"source_thread_id": "online", "distance": 0.1}]}
    ) == [{"source_thread_id": "online", "distance": 0.1, "rank": 1}]
    assert resolver._extract_mca_candidates(["raw"]) == [{"value": "raw", "rank": 1}]


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
    (repo_root / "config.ini").write_text(
        "[session]\ntoken = fresh-config-token\n",
        encoding="utf-8",
    )

    token = load_session_token(repo_root=repo_root)

    assert token == "fresh-config-token"


def test_provider_detection_and_source_id_extraction():
    perplexity_url = (
        "https://www.perplexity.ai/search/"
        "8daefbbb-e5e4-4c27-92c2-9cf7e9de0aa3"
    )
    chatgpt_url = (
        "https://chatgpt.com/c/"
        "69fadea6-bd2c-8399-b430-ae4f29b50293"
    )

    assert live_provider.detect_provider(perplexity_url) == "perplexity"
    assert live_provider.detect_provider(chatgpt_url) == "chatgpt"
    assert live_provider.detect_provider("8daefbbb-e5e4-4c27-92c2-9cf7e9de0aa3") is None
    assert (
        live_provider.extract_source_thread_id_from_url(perplexity_url, "perplexity")
        == "8daefbbb-e5e4-4c27-92c2-9cf7e9de0aa3"
    )
    assert (
        live_provider.build_provider_selector(
            "8daefbbb-e5e4-4c27-92c2-9cf7e9de0aa3",
            "perplexity",
        )
        == perplexity_url
    )


def test_run_perplexity_export_invokes_single_thread_cli(monkeypatch, tmp_path):
    export_repo = tmp_path / "perplexity-ai-export"
    export_repo.mkdir()
    (export_repo / "package.json").write_text('{"scripts": {}}\n', encoding="utf-8")
    monkeypatch.setenv("PERPLEXITY_AI_EXPORT_DIR", str(export_repo))
    seen = {}

    def fake_run(cmdline, **kwargs):
        seen["cmdline"] = cmdline
        seen["env"] = kwargs["env"]
        out_path = Path(cmdline[cmdline.index("--out") + 1])
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text('{"schema":"itir.perplexity.thread.v1"}\n', encoding="utf-8")
        return subprocess.CompletedProcess(
            cmdline,
            0,
            stdout='{"ok": true}\n',
            stderr="",
        )

    monkeypatch.setattr(live_provider.subprocess, "run", fake_run)

    result = live_provider.run_perplexity_export(
        "8daefbbb-e5e4-4c27-92c2-9cf7e9de0aa3",
        repo_root=tmp_path / "ITIR-suite",
        timeout=5,
        scroll_mode="step",
    )

    assert result["ok"] is True
    assert seen["cmdline"][:3] == ["npm", "run", "export:thread"]
    assert "--url" in seen["cmdline"]
    assert seen["env"]["HEADLESS"] == "true"
    assert seen["env"]["PERPLEXITY_SCROLL_MODE"] == "step"
    assert (
        "https://www.perplexity.ai/search/8daefbbb-e5e4-4c27-92c2-9cf7e9de0aa3"
        in seen["cmdline"]
    )
    assert result["output_path"].endswith("8daefbbb-e5e4-4c27-92c2-9cf7e9de0aa3.itir.perplexity.json")


def test_run_perplexity_export_rejects_partial_app_api_export(monkeypatch, tmp_path):
    export_repo = tmp_path / "perplexity-ai-export"
    export_repo.mkdir()
    (export_repo / "package.json").write_text('{"scripts": {}}\n', encoding="utf-8")
    monkeypatch.setenv("PERPLEXITY_AI_EXPORT_DIR", str(export_repo))

    def fake_run(cmdline, **kwargs):
        out_path = Path(cmdline[cmdline.index("--out") + 1])
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(
            json.dumps(
                {
                    "schema": "itir.perplexity.thread.v1",
                    "source": "perplexity",
                    "messages": [{"role": "user", "content": "partial"}],
                    "raw": {
                        "entries": [{"query_str": "partial"}],
                        "api_response": {"has_next_page": True},
                    },
                }
            ),
            encoding="utf-8",
        )
        return subprocess.CompletedProcess(cmdline, 0, stdout='{"ok": true}\n', stderr="")

    monkeypatch.setattr(live_provider.subprocess, "run", fake_run)

    result = live_provider.run_perplexity_export(
        "8daefbbb-e5e4-4c27-92c2-9cf7e9de0aa3",
        repo_root=tmp_path / "ITIR-suite",
        timeout=5,
    )

    assert result["ok"] is False
    assert result["export_diagnostic"]["partial"] is True
    assert "appears partial" in result["error"]


def test_persist_skips_ingest_when_perplexity_export_is_partial(monkeypatch, tmp_path):
    def fake_download(*args, **kwargs):
        return {
            "ok": False,
            "error": "partial",
            "output_path": str(tmp_path / "partial.itir.perplexity.json"),
        }

    def fail_ingest(*args, **kwargs):
        raise AssertionError("partial exports must not be ingested")

    monkeypatch.setattr(resolver, "_run_live_download", fake_download)
    monkeypatch.setattr(resolver, "_ingest_exports_to_structurer", fail_ingest)

    result = resolver._persist_selector_to_structurer(
        selector="https://www.perplexity.ai/search/8daefbbb-e5e4-4c27-92c2-9cf7e9de0aa3",
        repo_root=tmp_path,
        db_path=tmp_path / "chat.sqlite",
        venv_python=tmp_path / ".venv/bin/python",
        timeout=5,
        provider="perplexity",
    )

    assert result["ok"] is False
    assert result["ingest"]["ingested_count"] == 0
    assert "ingest skipped" in result["ingest"]["error"]


def test_ingest_exports_uses_provider_specific_format(monkeypatch, tmp_path):
    ingest_script = tmp_path / "chat-export-structurer/src/ingest.py"
    ingest_script.parent.mkdir(parents=True)
    ingest_script.write_text("# placeholder\n", encoding="utf-8")
    export_json = tmp_path / "thread.itir.perplexity.json"
    export_json.write_text('{"schema":"itir.perplexity.thread.v1"}\n', encoding="utf-8")
    seen = {}

    def fake_run(cmdline, **kwargs):
        seen["cmdline"] = cmdline
        return subprocess.CompletedProcess(cmdline, 0, stdout="ok\n", stderr="")

    monkeypatch.setattr(resolver.subprocess, "run", fake_run)

    result = resolver._ingest_exports_to_structurer(
        json_paths=[export_json],
        db_path=tmp_path / "chat.sqlite",
        venv_python=tmp_path / ".venv/bin/python",
        repo_root=tmp_path,
        timeout=5,
        provider="perplexity",
    )

    assert result["ok"] is True
    assert seen["cmdline"][seen["cmdline"].index("--format") + 1] == "perplexity"
    assert seen["cmdline"][seen["cmdline"].index("--account") + 1] == "perplexity"
    assert result["source_id"].startswith("resolver_perplexity_")


def test_run_web_view_treats_catalog_miss_as_auth_diagnostic(monkeypatch, tmp_path):
    monkeypatch.delenv("CHATGPT_SESSION_TOKEN", raising=False)
    monkeypatch.setenv("HOME", str(tmp_path))
    (tmp_path / ".chatgpt_session_new").write_text("known-good-token\n", encoding="utf-8")

    def fake_run(cmdline, **kwargs):
        return subprocess.CompletedProcess(
            cmdline,
            0,
            stdout=(
                "Storage disabled; conversations will not be saved locally.\n"
                "Could not fetch by ID, trying to match by title...\n"
                "Fetching conversation catalog in pages...\n"
                "No more conversation pages to fetch.\n"
                "Failed to find conversation matching 'missing-id'.\n"
            ),
            stderr="",
        )

    monkeypatch.setattr(live_provider.subprocess, "run", fake_run)

    result = live_provider.run_web_view(
        "missing-id",
        repo_root=tmp_path,
        venv_python=tmp_path / "missing-python",
        timeout=1,
    )

    assert result["ok"] is False
    assert result["auth_diagnostic"]["reason"] == "catalog_miss_with_known_good_token"
    assert result["error"].startswith("re_gpt did not fetch the conversation")


def test_run_web_view_retries_known_good_token_after_stale_catalog_miss(monkeypatch, tmp_path):
    monkeypatch.setenv("CHATGPT_SESSION_TOKEN", "stale-token")
    monkeypatch.setenv("HOME", str(tmp_path))
    (tmp_path / ".chatgpt_session_new").write_text("known-good-token\n", encoding="utf-8")
    seen_keys = []

    def fake_run(cmdline, **kwargs):
        seen_keys.append(cmdline[cmdline.index("--key") + 1])
        if seen_keys[-1] == "stale-token":
            return subprocess.CompletedProcess(
                cmdline,
                0,
                stdout=(
                    "Storage disabled; conversations will not be saved locally.\n"
                    "Could not fetch by ID, trying to match by title...\n"
                    "Fetching conversation catalog in pages...\n"
                    "No more conversation pages to fetch.\n"
                    "Failed to find conversation matching "
                    "'69fadea6-bd2c-8399-b430-ae4f29b50293'.\n"
                ),
                stderr="",
            )
        return subprocess.CompletedProcess(
            cmdline,
            0,
            stdout="Fetched conversation 69fadea6-bd2c-8399-b430-ae4f29b50293\n",
            stderr="",
        )

    monkeypatch.setattr(live_provider.subprocess, "run", fake_run)

    result = live_provider.run_web_view(
        "69fadea6-bd2c-8399-b430-ae4f29b50293",
        repo_root=tmp_path,
        venv_python=tmp_path / "missing-python",
        timeout=1,
    )

    assert result["ok"] is True
    assert seen_keys == ["stale-token", "known-good-token"]
    assert result["retried_with_known_good_token"] == "file:~/.chatgpt_session_new"


def test_run_web_view_retries_known_good_token_after_auth_bootstrap_block(monkeypatch, tmp_path):
    monkeypatch.setenv("CHATGPT_SESSION_TOKEN", "stale-token")
    monkeypatch.setenv("HOME", str(tmp_path))
    (tmp_path / ".chatgpt_session_new").write_text("known-good-token\n", encoding="utf-8")
    seen_keys = []

    def fake_run(cmdline, **kwargs):
        seen_keys.append(cmdline[cmdline.index("--key") + 1])
        if seen_keys[-1] == "stale-token":
            return subprocess.CompletedProcess(
                cmdline,
                1,
                stdout="",
                stderr=(
                    "re_gpt.errors.UnexpectedResponseError: Unable to retrieve ChatGPT "
                    "home page due to Cloudflare blocking the request."
                ),
            )
        return subprocess.CompletedProcess(
            cmdline,
            0,
            stdout="Fetched conversation 69fadea6-bd2c-8399-b430-ae4f29b50293\n",
            stderr="",
        )

    monkeypatch.setattr(live_provider.subprocess, "run", fake_run)

    result = live_provider.run_web_view(
        "69fadea6-bd2c-8399-b430-ae4f29b50293",
        repo_root=tmp_path,
        venv_python=tmp_path / "missing-python",
        timeout=1,
    )

    assert result["ok"] is True
    assert seen_keys == ["stale-token", "known-good-token"]
    assert result["retried_with_known_good_token"] == "file:~/.chatgpt_session_new"
