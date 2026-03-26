from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


def _project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _bridge_env() -> dict[str, str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(_project_root() / "src")
    return env


def _read_json_line(handle) -> dict:
    line = handle.readline()
    return json.loads(line)


def test_bridge_protocol_smoke() -> None:
    command = [sys.executable, "-m", "itir_mcp", "--bridge"]
    process = subprocess.Popen(
        command,
        cwd=_project_root(),
        env=_bridge_env(),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    try:
        assert process.stdin is not None
        assert process.stdout is not None

        process.stdin.write(json.dumps({"op": "health"}) + "\n")
        process.stdin.flush()
        health = _read_json_line(process.stdout)
        assert health["ok"] is True
        assert "version" in health

        process.stdin.write(json.dumps({"op": "list"}) + "\n")
        process.stdin.flush()
        listed = _read_json_line(process.stdout)
        assert listed["ok"] is True
        tool_names = [tool["name"] for tool in listed["tools"]]
        assert "sensiblaw.obligations_query" in tool_names

        payload = {
            "op": "call",
            "name": "sensiblaw.obligations_query",
            "payload": {
                "text": "The tenant must pay rent on time.",
            },
        }
        process.stdin.write(json.dumps(payload) + "\n")
        process.stdin.flush()
        called = _read_json_line(process.stdout)
        assert called["ok"] is True
        assert called["result"]["version"] == "obligation.query.v1"
    finally:
        process.terminate()
        process.wait(timeout=5)
