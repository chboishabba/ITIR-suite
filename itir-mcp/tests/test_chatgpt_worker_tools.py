from __future__ import annotations

from itir_mcp import build_default_registry
from itir_mcp import chatgpt_worker_tools


def test_registry_exposes_governed_chatgpt_worker_tools() -> None:
    registry = build_default_registry()

    for name in (
        "itir.chatgpt.list_threads",
        "itir.chatgpt.session_status",
        "itir.chatgpt.get_access_token",
        "itir.chatgpt.cdp_capture",
        "itir.chatgpt.hydrate",
        "itir.chatgpt.revive",
        "itir.chatgpt.revive_multi",
        "itir.chatgpt.dispatch_worker",
        "itir.chatgpt.operation_status",
        "itir.chatgpt.reconcile",
        "itir.chatgpt.view_messages",
        "itir.chatgpt.fleet_status",
        "itir.chatgpt.fleet_opportunities",
        "itir.chatgpt.create_conversation",
    ):
        spec = registry.get_tool_spec(name)
        assert spec is not None
        assert spec.read_only is (name in {
            "itir.chatgpt.operation_status",
            "itir.chatgpt.list_threads",
            "itir.chatgpt.session_status",
            "itir.chatgpt.get_access_token",
            "itir.chatgpt.view_messages",
            "itir.chatgpt.fleet_status",
            "itir.chatgpt.fleet_opportunities",
        })


def test_create_conversation_forces_direct_async_and_returns_uncertain_receipt(monkeypatch) -> None:
    calls = []

    class FakeWorkerApi:
        @staticmethod
        def chatgpt_new(**kwargs):
            calls.append(kwargs)
            return {"operation_id": "op-new", "state": "commit_unknown", "conversation_id": "c-new"}

    monkeypatch.setattr(chatgpt_worker_tools, "_worker_api", lambda: FakeWorkerApi)
    result = build_default_registry().invoke(
        "itir.chatgpt.create_conversation", {"prompt": "fresh", "follow": False}
    )
    assert result["ok"] is True
    assert result["result"]["status"] == "uncertain"
    assert result["result"]["uncertain"] is True
    assert result["result"]["receipt"]["operation_id"] == "op-new"
    assert result["result"]["policy"]["dom_fallback"] is False
    assert result["result"]["policy"]["automatic_resend"] is False
    assert calls == [{"prompt": "fresh", "follow": False, "db_path": None}]


def test_create_conversation_rejects_empty_prompt_before_adapter(monkeypatch) -> None:
    called = False

    def fail_adapter():
        nonlocal called
        called = True
        raise AssertionError("adapter must not be resolved")

    monkeypatch.setattr(chatgpt_worker_tools, "_worker_api", fail_adapter)
    result = build_default_registry().invoke("itir.chatgpt.create_conversation", {"prompt": "  "})
    assert result["ok"] is False
    assert result["error"]["code"] == "input_error"
    assert called is False


def test_dispatch_forces_async_without_dom_fallback(monkeypatch) -> None:
    calls = []

    class FakeWorkerApi:
        @staticmethod
        def chatgpt_continue(**kwargs):
            calls.append(kwargs)
            return {"operation_id": "op-1", "state": "complete"}

        @staticmethod
        def chatgpt_hydrate(**kwargs):
            return {"hydrated_count": 1, "results": [{"conversation_id": "c1", "status": "ok"}]}

    monkeypatch.setattr(chatgpt_worker_tools, "_worker_api", lambda: FakeWorkerApi)

    hydrate_res = build_default_registry().invoke(
        "itir.chatgpt.hydrate",
        {"conversation_id": "c1"},
    )
    assert hydrate_res["ok"] is True
    assert hydrate_res["result"]["result"]["hydrated_count"] == 1

    result = build_default_registry().invoke(
        "itir.chatgpt.dispatch_worker",
        {"conversation_id": "thread-1", "prompt": "implement this", "follow": False},
    )

    assert result["ok"] is True
    assert result["result"]["operation"]["operation_id"] == "op-1"
    assert calls == [{
        "conversation_id": "thread-1",
        "prompt": f"{chatgpt_worker_tools.GOLDEN_AGDA_REMINDER}\n\nimplement this",
        "attachments": [],
        "follow": False,
        "write_transport": "async",
        "dom_fallback": False,
        "db_path": None,
        "reconcile_attempts": 3,
    }]


def test_revive_multi_validates_parents_and_delegates(monkeypatch) -> None:
    calls = []

    class FakeWorkerApi:
        @staticmethod
        def chatgpt_revive_multi(**kwargs):
            calls.append(kwargs)
            return {
                "operation_id": "op-bundle",
                "state": "complete",
                "parent_thread_ids": kwargs["parent_thread_ids"],
                "revived_conversation_id": "child-1",
            }

    monkeypatch.setattr(chatgpt_worker_tools, "_worker_api", lambda: FakeWorkerApi)

    registry = build_default_registry()
    rejected = registry.invoke(
        "itir.chatgpt.revive_multi",
        {
            "parent_thread_ids": ["thread-1"],
            "handoff_path": "/tmp/handoff.json",
            "prompt": "continue",
            "request_id": "req-1",
        },
    )
    assert rejected["ok"] is False

    result = registry.invoke(
        "itir.chatgpt.revive_multi",
        {
            "parent_thread_ids": ["thread-1", "thread-2"],
            "handoff_path": "/tmp/handoff.json",
            "prompt": "continue",
            "request_id": "req-1",
        },
    )
    assert result["ok"] is True
    assert result["result"]["operation"]["revived_conversation_id"] == "child-1"
    assert calls[0]["parent_thread_ids"] == ["thread-1", "thread-2"]
    assert calls[0]["handoff_path"] == "/tmp/handoff.json"
    assert calls[0]["request_id"] == "req-1"


def test_reconcile_never_constructs_re_gpt_service_with_none_db_path(monkeypatch) -> None:
    sentinel = object()

    class FakeMutationService:
        def __init__(self, *, db_path=sentinel):
            assert db_path is sentinel

        def reconcile(self, operation_id, **kwargs):
            assert operation_id == "op-1"
            assert kwargs["browser_fallback"] is False
            assert kwargs["direct_allowed"] is True
            return {"operation_id": operation_id, "state": "complete"}

    class FakeModule:
        MutationService = FakeMutationService

    monkeypatch.setattr(chatgpt_worker_tools.importlib, "import_module", lambda _: FakeModule)
    result = build_default_registry().invoke(
        "itir.chatgpt.reconcile",
        {"operation_id": "op-1", "prompt": "implement this"},
    )

    assert result["ok"] is True
    assert result["result"]["policy"]["browser_fallback"] is False


def test_dispatch_worker_expands_presets_and_strips_verbose_telemetry(monkeypatch) -> None:
    calls = []

    class FakeWorkerApi:
        @staticmethod
        def chatgpt_continue(**kwargs):
            calls.append(kwargs)
            return {
                "operation_id": "op-2",
                "state": "complete",
                "assistant_text": "done",
                "read_observations": [{"cookie_names": ["secret"]}],
                "write_observations": [{"header_names": ["Authorization"]}],
                "started_at": 1.0,
            }

    monkeypatch.setattr(chatgpt_worker_tools, "_worker_api", lambda: FakeWorkerApi)
    res = build_default_registry().invoke(
        "itir.chatgpt.dispatch_worker",
        {
            "conversation_id": "thread-1",
            "prompt": "@max_cut @grug_ste100 @zkp_qa Focus on formal referee wiring.",
        },
    )
    assert res["ok"] is True
    op = res["result"]["operation"]
    assert op == {"operation_id": "op-2", "state": "complete", "assistant_text": "done"}
    sent_prompt = calls[0]["prompt"]
    assert "pareto/snowball/ibrahim" in sent_prompt
    assert "ASD-STE100" in sent_prompt
    assert "O/R/C/S/L/P/G/F" in sent_prompt
    assert sent_prompt.endswith("Focus on formal referee wiring.")


def test_dispatch_worker_new_presets_and_golden_reminder(monkeypatch) -> None:
    calls = []

    class FakeWorkerApi:
        @staticmethod
        def chatgpt_continue(**kwargs):
            calls.append(kwargs)
            return {"operation_id": "op-3", "state": "complete", "assistant_text": "done"}

    monkeypatch.setattr(chatgpt_worker_tools, "_worker_api", lambda: FakeWorkerApi)

    for preset_name in ("rpd", "steelman", "lemmas", "surrounds", "docs", "snowball"):
        calls.clear()
        res = build_default_registry().invoke(
            "itir.chatgpt.dispatch_worker",
            {
                "conversation_id": "thread-1",
                "prompt": f"@{preset_name}",
            },
        )
        assert res["ok"] is True
        sent = calls[0]["prompt"]
        assert chatgpt_worker_tools.GOLDEN_AGDA_REMINDER in sent
        assert sent.startswith(chatgpt_worker_tools.GOLDEN_AGDA_REMINDER)

    # Verify hyphenated @max-cut in a multi-macro chain expands all macros and leaves no literal @ tokens
    calls.clear()
    res = build_default_registry().invoke(
        "itir.chatgpt.dispatch_worker",
        {
            "conversation_id": "thread-1",
            "prompt": "@docs @max-cut @rpd @steelman @lemmas @surrounds @snowball\nFormalise SensibLaw/SLR Agda boundary.",
        },
    )
    assert res["ok"] is True
    sent = calls[0]["prompt"]
    assert "@max-cut" not in sent
    assert "@docs" not in sent
    assert "@rpd" not in sent
    assert "@steelman" not in sent
    assert "@lemmas" not in sent
    assert "@surrounds" not in sent
    assert "@snowball" not in sent
    assert "Synchronize and update project documentation" in sent
    assert "Exactly complete all per max-cut" in sent
    assert "List every required lemma between here -> completed." in sent
    assert sent.endswith("Formalise SensibLaw/SLR Agda boundary.")


def test_cdp_capture_tool_invocable(monkeypatch) -> None:
    class FakeWorkerApi:
        @staticmethod
        def chatgpt_cdp_capture(**kwargs):
            return {"ok": True, "session": {"state": "ready"}}

    monkeypatch.setattr(chatgpt_worker_tools, "_worker_api", lambda: FakeWorkerApi)
    registry = build_default_registry()
    res = registry.invoke("itir.chatgpt.cdp_capture", {"cdp_url": "http://127.0.0.1:9222"})
    assert res["ok"] is True
    assert res["result"]["session"]["state"] == "ready"

