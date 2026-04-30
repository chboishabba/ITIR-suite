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
        assert "itir.compare_observations" in tool_names

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

        compare_payload = {
            "op": "call",
            "name": "itir.compare_observations",
            "payload": {
                "left": {
                    "obs_id": "wm:1",
                    "source_system": "worldmonitor",
                    "source_scope": "external",
                    "observed_time": "2026-04-06T00:00:00+00:00",
                    "text": "Explosion reported near Odesa port after overnight drone attack",
                    "geometry": {"lat": 46.48, "lon": 30.72},
                },
                "right": {
                    "obs_id": "or:1",
                    "source_system": "openrecall",
                    "source_scope": "internal",
                    "observed_time": "2026-04-06T00:30:00+00:00",
                    "text": "Odesa port explosion noted after overnight drone strike",
                    "geometry": {"lat": 46.47, "lon": 30.73},
                },
            },
        }
        process.stdin.write(json.dumps(compare_payload) + "\n")
        process.stdin.flush()
        compared = _read_json_line(process.stdout)
        assert compared["ok"] is True
        assert compared["result"]["version"] == "itir.compare_observations.v1"

        safe_compare_payload = {
            "op": "safe_call",
            "name": "itir.compare_observations",
            "payload": compare_payload["payload"],
        }
        process.stdin.write(json.dumps(safe_compare_payload) + "\n")
        process.stdin.flush()
        safe_compared = _read_json_line(process.stdout)
        assert safe_compared["ok"] is True
        assert safe_compared["result"]["decision"] == "verified"
        assert safe_compared["result"]["status_explanation"]["status_value"] == "verified"
        assert safe_compared["result"]["receipt"]["event"] == "tool_output_verified"
    finally:
        process.terminate()
        process.wait(timeout=5)
