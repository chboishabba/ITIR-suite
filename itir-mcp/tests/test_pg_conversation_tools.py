"""Independent PostgreSQL history MCP tool contract."""
from unittest.mock import Mock, patch
import pytest
from itir_mcp import build_default_registry
from itir_mcp import pg_conversation_tools


def test_registered_without_tui_socket():
    registry = build_default_registry()
    assert registry.get_tool_spec("itir.chatgpt.pg_search").read_only
    assert registry.get_tool_spec("itir.chatgpt.pg_read").read_only


def test_search_uses_shared_pg_adapter():
    provider = Mock()
    provider.list_pg_conversations.return_value = [{"id": "c1", "title": "T"}]
    with patch.object(pg_conversation_tools, "_provider", return_value=provider):
        result = pg_conversation_tools.search({"query": "T", "limit": 10})
    assert result["conversations"][0]["id"] == "c1"
    provider.list_pg_conversations.assert_called_once_with(query="T", limit=10, offset=0)


def test_read_rejects_missing_id():
    with pytest.raises(Exception):
        pg_conversation_tools.read({})

def test_hydration_tools_are_mutating_and_separate():
    registry = build_default_registry()
    for name in ("itir.chatgpt.pg_roster_sync",
                 "itir.chatgpt.pg_hydrate_selected",
                 "itir.chatgpt.pg_hydrate_pending"):
        assert registry.get_tool_spec(name).read_only is False


def test_explicit_selected_hydration_passes_exact_identity():
    provider = Mock()
    provider.hydrate_one.return_value = {"conversation_id": "cid", "state": "hydrated"}
    with patch("itir_mcp.pg_conversation_tools.importlib.import_module", return_value=provider):
        result = pg_conversation_tools.hydrate_selected({"conversation_id": "cid"})
    assert result["state"] == "hydrated"
    provider.hydrate_one.assert_called_once_with("cid")
