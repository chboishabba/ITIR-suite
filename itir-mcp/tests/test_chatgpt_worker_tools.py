from __future__ import annotations

from itir_mcp import build_default_registry
from itir_mcp import chatgpt_worker_tools


def test_registry_exposes_governed_chatgpt_worker_tools() -> None:
    registry = build_default_registry()

    for name in (
        "itir.chatgpt.hydrate",
        "itir.chatgpt.dispatch_worker",
        "itir.chatgpt.operation_status",
        "itir.chatgpt.reconcile",
    ):
        spec = registry.get_tool_spec(name)
        assert spec is not None
        assert spec.read_only is (name == "itir.chatgpt.operation_status")


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
        "prompt": "implement this",
        "attachments": [],
        "follow": False,
        "write_transport": "async",
        "dom_fallback": False,
        "db_path": None,
    }]


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
