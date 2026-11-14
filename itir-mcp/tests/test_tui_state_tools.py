"""Direct app-state MCP contract tests (offline)."""
import pytest
from unittest.mock import patch
from itir_mcp import build_default_registry
from itir_mcp.tui_state_tools import call_live_tui
from itir_mcp.contracts import ToolPolicyError


def test_mcp_tools_registered_separately():
    reg = build_default_registry()
    assert reg.get_tool_spec("itir.terminal.state").read_only is True
    assert reg.get_tool_spec("itir.terminal.picker").read_only is False


def test_no_implicit_terminal_discovery(monkeypatch):
    monkeypatch.delenv("ITIR_TUI_CONTROL_SOCKET", raising=False)
    with pytest.raises(ToolPolicyError):
        call_live_tui({"action": "state"})


def test_socket_control_requires_opt_in(monkeypatch):
    monkeypatch.setenv("ITIR_TUI_CONTROL_SOCKET", "/tmp/nonexistent.sock")
    with pytest.raises(Exception):
        call_live_tui({"action": "select", "index": 0}, allow_control=False)
