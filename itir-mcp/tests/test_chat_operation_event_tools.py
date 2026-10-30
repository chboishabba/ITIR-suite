"""MCP server jobs and replay must work without any TUI process."""
from unittest.mock import patch
import pytest
from itir_mcp import build_default_registry
from itir_mcp import chat_operation_event_tools as tool

def test_registration_and_authority():
    reg=build_default_registry()
    assert reg.get_tool_spec("itir.chatgpt.operation_events").read_only
    assert reg.get_tool_spec("itir.chatgpt.job_status").read_only
    assert not reg.get_tool_spec("itir.chatgpt.queue_turn").read_only
    assert not reg.get_tool_spec("itir.chatgpt.cancel_queued").read_only

def test_invalid_replay_cursor_rejected():
    with pytest.raises(Exception):
        tool.replay({"conversation_id":"x","after":-1})

def test_replay_calls_pg_without_tui():
    result={"events":[{"event_id":7,"operation_id":"job"}],"next_cursor":7}
    with patch("re_gpt.pg_operation_events.events_after",return_value=result) as read:
        assert tool.replay({"conversation_id":"thread-A","after":6})==result
    read.assert_called_once_with("thread-A",after=6,limit=100)

def test_queue_provider_is_explicit():
    with patch("re_gpt.pg_turn_worker.queue_turn",return_value={"job_id":"local-id"}) as submit:
        assert tool.queue_turn({"conversation_id":"A","prompt":"check","provider":"local"})["job_id"]=="local-id"
    submit.assert_called_once_with("A","check",actor="agent",job_id=None,provider="local")
