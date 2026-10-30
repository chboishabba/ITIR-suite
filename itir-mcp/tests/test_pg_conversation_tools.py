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
