"""Read-only observation of an explicitly allowed tmux pane.

No shell interpolation, browser/CDP, keystrokes, process spawning, or secrets.
Set ITIR_TMUX_ALLOWED_PANES to a comma-separated list of exact pane targets.
"""
from __future__ import annotations

import os
import re
import subprocess

from .contracts import ToolInputError, ToolPolicyError, ToolExecutionError, ToolSpec

PANE_RE = re.compile(r"^(?:%[0-9]+|[a-zA-Z0-9_.-]+:[0-9]+\.[0-9]+)$")


def observe_pane(payload):
    pane = payload.get("pane")
    if not isinstance(pane, str) or not PANE_RE.fullmatch(pane):
        raise ToolInputError("pane must be an exact tmux pane ID or session:window.pane")
    allowed = set(filter(None, (x.strip() for x in os.environ.get("ITIR_TMUX_ALLOWED_PANES", "").split(","))))
    if pane not in allowed:
        raise ToolPolicyError("pane is not explicitly allowed for observation")
    lines = payload.get("lines", 80)
    if type(lines) is not int or not 1 <= lines <= 300:
        raise ToolInputError("lines must be an integer between 1 and 300")
    try:
        result = subprocess.run(
            ["tmux", "capture-pane", "-p", "-J", "-t", pane, "-S", f"-{lines}"],
            text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            timeout=5, check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        raise ToolExecutionError("tmux capture unavailable")
    if result.returncode:
        raise ToolExecutionError("tmux pane capture failed")
    # Screen contents may contain private data. Do not persist, log, or broadcast.
    return {"pane": pane, "text": result.stdout[:50000], "read_only": True,
            "truncated": len(result.stdout) > 50000}


def get_tmux_observation_tools():
    spec = ToolSpec(
        name="itir.terminal.observe",
        title="Observe an authorized tmux pane",
        description="Read the current terminal display of a caller-allowlisted pane; never sends keys.",
        input_schema={"type": "object", "properties": {
            "pane": {"type": "string"}, "lines": {"type": "integer", "minimum": 1, "maximum": 300}},
            "required": ["pane"], "additionalProperties": False},
        read_only=True,
    )
    return [(spec, observe_pane)]
