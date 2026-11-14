"""Offline terminal observation access-control contract."""
import pytest
from unittest.mock import Mock, patch
from itir_mcp import build_default_registry
from itir_mcp.tmux_observation_tools import observe_pane
from itir_mcp.contracts import ToolPolicyError, ToolInputError


def test_tool_registered_read_only():
    spec = build_default_registry().get_tool_spec("itir.terminal.observe")
    assert spec is not None and spec.read_only


def test_denies_unapproved_panes(monkeypatch):
    monkeypatch.delenv("ITIR_TMUX_ALLOWED_PANES", raising=False)
    with pytest.raises(ToolPolicyError):
        observe_pane({"pane": "%3"})


def test_rejects_pane_command_injection(monkeypatch):
    monkeypatch.setenv("ITIR_TMUX_ALLOWED_PANES", "%3")
    with pytest.raises(ToolInputError):
        observe_pane({"pane": "%3; rm -rf /"})


def test_observes_approved_pane_without_shell(monkeypatch):
    monkeypatch.setenv("ITIR_TMUX_ALLOWED_PANES", "%3")
    fake = Mock(returncode=0, stdout="No matching conversations\n", stderr="")
    with patch("itir_mcp.tmux_observation_tools.subprocess.run", return_value=fake) as run:
        result = observe_pane({"pane": "%3", "lines": 12})
    assert "No matching conversations" in result["text"]
    assert result["read_only"]
    args, kwargs = run.call_args
    assert args[0] == ["tmux", "capture-pane", "-p", "-J", "-t", "%3", "-S", "-12"]
    assert "shell" not in kwargs
