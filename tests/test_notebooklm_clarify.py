from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "notebooklm_clarify.py"

spec = importlib.util.spec_from_file_location("notebooklm_clarify", SCRIPT_PATH)
module = importlib.util.module_from_spec(spec)
assert spec is not None and spec.loader is not None
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def test_extract_notebook_id_accepts_url_and_id() -> None:
    notebook_id = "85956e55-335c-4797-b13a-81e605a32311"
    url = f"https://notebooklm.google.com/notebook/{notebook_id}"

    assert module.extract_notebook_id(notebook_id) == notebook_id
    assert module.extract_notebook_id(url) == notebook_id


def test_build_clarify_prompt_with_context_and_agent_message() -> None:
    prompt = module.build_clarify_prompt(
        items=[
            ("supported", "row one"),
            ("ambiguous", "row two"),
        ],
        context="cross-document affidavit review",
        agent_message="focus on speaker attribution",
    )

    assert prompt.startswith("Please clarify:")
    assert "supported: row one" in prompt
    assert "ambiguous: row two" in prompt
    assert "\n\nContext:\ncross-document affidavit review" in prompt
    assert "\n\nAdditional request:\nfocus on speaker attribution" in prompt


def test_extract_visible_conversation_ids_reads_history_table() -> None:
    history_text = """
    ┌────┬────────────────────────────┬──────────────────────────────────────┐
    │ #  │ title                      │ id                                   │
    │ 1  │ Dad Court review           │ a7abb6dd-ba39-4374-9cbf-d0de4677d70d │
    │ 2  │ Other thread               │ 69be0356-1378-4a66-ad78-3586fe66a095 │
    └────┴────────────────────────────┴──────────────────────────────────────┘
    """

    assert module.extract_visible_conversation_ids(history_text) == [
        "a7abb6dd-ba39-4374-9cbf-d0de4677d70d",
        "69be0356-1378-4a66-ad78-3586fe66a095",
    ]


def test_pick_default_conversation_id_uses_history_when_available(monkeypatch) -> None:
    def fake_execute_command(cmd: list[str]) -> subprocess.CompletedProcess[str]:
        assert cmd == ["fake-notebooklm", "history", "--notebook", "nb_123"]
        return subprocess.CompletedProcess(
            cmd,
            0,
            stdout="│ 1 │ Dad Court │ a7abb6dd-ba39-4374-9cbf-d0de4677d70d │\n",
            stderr="",
        )

    monkeypatch.setattr(module, "execute_command", fake_execute_command)

    selected = module.pick_default_conversation_id(
        notebook_id="nb_123",
        notebooklm_cli="fake-notebooklm",
    )

    assert selected == "a7abb6dd-ba39-4374-9cbf-d0de4677d70d"


def test_cli_dry_run_defaults_to_persist_visible_conversation(monkeypatch, capsys) -> None:
    def fake_resolve_notebooklm_cli(explicit: str | None = None) -> str:
        return "/tmp/fake-notebooklm"

    def fake_pick_default_conversation_id(*, notebook_id: str, notebooklm_cli: str) -> str | None:
        assert notebook_id == "85956e55-335c-4797-b13a-81e605a32311"
        assert notebooklm_cli == "/tmp/fake-notebooklm"
        return "a7abb6dd-ba39-4374-9cbf-d0de4677d70d"

    monkeypatch.setattr(module, "resolve_notebooklm_cli", fake_resolve_notebooklm_cli)
    monkeypatch.setattr(module, "pick_default_conversation_id", fake_pick_default_conversation_id)

    exit_code = module.main(
        [
            "--notebook-url",
            "https://notebooklm.google.com/notebook/85956e55-335c-4797-b13a-81e605a32311",
            "--item",
            "supported:row one",
            "--item",
            "ambiguous:row two",
            "--dry-run",
        ]
    )

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == 0
    assert payload["conversation_strategy"] == "persist_visible"
    assert payload["selected_conversation_id"] == "a7abb6dd-ba39-4374-9cbf-d0de4677d70d"
    assert payload["command"][:5] == [
        "/tmp/fake-notebooklm",
        "ask",
        "--notebook",
        "85956e55-335c-4797-b13a-81e605a32311",
        "--conversation-id",
    ]
    assert "defaulting to visible conversation" in captured.err


def test_cli_dry_run_respects_new_conversation(monkeypatch, capsys) -> None:
    monkeypatch.setattr(module, "resolve_notebooklm_cli", lambda explicit=None: "/tmp/fake-notebooklm")

    exit_code = module.main(
        [
            "--notebook-id",
            "nb_123",
            "--question",
            "Please clarify: supported: row one",
            "--new",
            "--dry-run",
        ]
    )

    payload = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert payload["conversation_strategy"] == "new"
    assert payload["selected_conversation_id"] is None
    assert "--new" in payload["command"]

