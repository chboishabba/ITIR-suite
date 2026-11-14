from unittest.mock import Mock, patch
from itir_mcp import build_default_registry
from itir_mcp import chatgpt_worker_tools


def test_cffi_refresh_registered_separately():
    registry = build_default_registry()
    assert registry.get_tool_spec("itir.chatgpt.session_refresh_cffi").read_only is False
    assert registry.get_tool_spec("itir.chatgpt.session_refresh") is not None


def test_cffi_tool_returns_no_secrets():
    backend = Mock()
    backend.chatgpt_session_refresh_cffi.return_value = {
        "renewed": True, "browser_used": False, "transport": "curl_cffi",
        "session": {"state": "ready"}}
    with patch.object(chatgpt_worker_tools, "_worker_api", return_value=backend):
        result = chatgpt_worker_tools.session_refresh_cffi({})
    assert result["session"]["browser_used"] is False
    assert "access_token" not in result
    backend.chatgpt_session_refresh_cffi.assert_called_once_with(
        profile_dir=None, snapshot_path=None)


def test_session_refresh_is_cffi_only_and_rejects_browser_mode():
    spec = build_default_registry().get_tool_spec("itir.chatgpt.session_refresh")
    assert "browser_mode" not in spec.input_schema["properties"]

    backend = Mock()
    backend.chatgpt_session_refresh.return_value = {
        "renewed": True, "browser_used": False, "transport": "curl_cffi",
        "session": {"state": "ready"}}
    with patch.object(chatgpt_worker_tools, "_worker_api", return_value=backend):
        result = chatgpt_worker_tools.session_refresh({})
    assert result["session"]["browser_used"] is False
    backend.chatgpt_session_refresh.assert_called_once_with(
        profile_dir=None, snapshot_path=None)
