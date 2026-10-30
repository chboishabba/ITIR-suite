"""MCP bridge to a live TUI's explicit Unix-domain application-state socket.

No tmux, Chrome, DOM, credential access or free-form shell commands.
State-only is read authority. Picker actions are separately enabled.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import socket
import stat

from .contracts import ToolSpec, ToolInputError, ToolPolicyError, ToolExecutionError


def call_live_tui(payload, *, allow_control=False):
    socket_name = os.environ.get("ITIR_TUI_CONTROL_SOCKET", "")
    if not socket_name:
        raise ToolPolicyError("ITIR_TUI_CONTROL_SOCKET not configured")
    path = Path(socket_name)
    try:
        info = path.lstat()
        parent = path.parent.stat()
    except OSError:
        raise ToolExecutionError("TUI state socket is unavailable")
    if not stat.S_ISSOCK(info.st_mode) or info.st_uid != os.getuid():
        raise ToolPolicyError("not an owner-operated Unix socket")
    if info.st_mode & 0o077 or parent.st_mode & 0o077:
        raise ToolPolicyError("TUI socket permissions are too broad")
    action = payload.get("action", "state")
    if action not in {"state", "open_picker", "set_query", "select"}:
        raise ToolInputError("unsupported application-state action")
    if action != "state" and not allow_control:
        raise ToolPolicyError("picker control requires ITIR_TUI_ALLOW_CONTROL=1")
    request = {"action": action}
    if action == "set_query":
        query = payload.get("query")
        if not isinstance(query, str) or len(query) > 200:
            raise ToolInputError("query must be at most 200 characters")
        request["query"] = query
    elif action == "select":
        index = payload.get("index")
        if type(index) is not int or index < 0:
            raise ToolInputError("invalid index")
        request["index"] = index
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
            client.settimeout(3)
            client.connect(str(path))
            client.sendall(json.dumps(request).encode("utf-8"))
            raw = client.recv(65536)
        response = json.loads(raw)
        if not isinstance(response, dict):
            raise ValueError("invalid response")
        return response
    except (OSError, ValueError, TimeoutError):
        raise ToolExecutionError("TUI state request failed")


def get_tui_state_tools():
    common = {"type": "object", "properties": {
        "action": {"type": "string", "enum": ["state", "open_picker", "set_query", "select"]},
        "query": {"type": "string", "maxLength": 200}, "index": {"type": "integer", "minimum": 0}},
        "additionalProperties": False}
    return [
        (ToolSpec(name="itir.terminal.state", title="Live TUI application state",
                  description="Read picker, result, selection and loading state without terminal capture",
                  input_schema={"type": "object", "properties": {}, "additionalProperties": False},
                  read_only=True),
         lambda _: call_live_tui({"action": "state"})),
        (ToolSpec(name="itir.terminal.picker", title="Control TUI conversation picker",
                  description="Opt-in picker open/query/selection; no sending of ChatGPT messages",
                  input_schema=common, read_only=False),
         lambda payload: call_live_tui(payload,
             allow_control=os.environ.get("ITIR_TUI_ALLOW_CONTROL") == "1")),
    ]
