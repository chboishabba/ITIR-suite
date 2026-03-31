from itir_mcp import build_default_registry


def test_default_registry_lists_expected_tools() -> None:
    registry = build_default_registry()
    names = {tool.name for tool in registry.list_tools()}
    assert names == {
        "chat_export_structurer.resolve_thread",
        "chat_export_structurer.search_threads",
        "chat_export_structurer.thread_messages",
        "sensiblaw.obligations_query",
        "sensiblaw.obligations_explain",
        "sensiblaw.obligations_alignment",
        "sensiblaw.obligations_projection",
        "sensiblaw.obligations_activate",
    }
