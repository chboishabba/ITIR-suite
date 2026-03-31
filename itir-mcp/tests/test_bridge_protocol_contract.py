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


def _fixture_rows(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _normalize_response(response: dict) -> dict:
    request_id = response.get("request_id")

    if response.get("ok") is True and "service" in response:
        normalized = {
            "ok": True,
            "protocol": response["protocol"],
            "service": response["service"],
            "version": response["version"],
        }
        if request_id is not None:
            normalized["request_id"] = request_id
        return normalized
    if response.get("ok") is True and "ready" in response:
        normalized = {
            "ok": True,
            "protocol": response["protocol"],
            "ready": response["ready"],
            "version": response["version"],
        }
        if request_id is not None:
            normalized["request_id"] = request_id
        return normalized
    if response.get("ok") is True and isinstance(response.get("tools"), list):
        normalized = {
            "ok": True,
            "tool_names": sorted(tool["name"] for tool in response["tools"]),
        }
        if request_id is not None:
            normalized["request_id"] = request_id
        return normalized
    if response.get("ok") is True and "result" in response:
        normalized = {
            "ok": True,
            "result_version": response["result"].get("version"),
        }
        if request_id is not None:
            normalized["request_id"] = request_id
        return normalized
    normalized = {
        "ok": response.get("ok"),
        "error_code": (response.get("error") or {}).get("code"),
    }
    if request_id is not None:
        normalized["request_id"] = request_id
    return normalized


def _run_fixture_session(fixture_path: Path) -> list[dict]:
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
    responses: list[dict] = []
    try:
        assert process.stdin is not None
        assert process.stdout is not None
        for row in _fixture_rows(fixture_path):
            if "raw" in row:
                process.stdin.write(str(row["raw"]) + "\n")
            else:
                process.stdin.write(json.dumps(row["request"]) + "\n")
            process.stdin.flush()
            response = json.loads(process.stdout.readline())
            responses.append(_normalize_response(response))
    finally:
        process.terminate()
        process.wait(timeout=5)
    return responses


def test_bridge_protocol_contract_fixture() -> None:
    fixture_path = _project_root() / "tests/fixtures/bridge_protocol/session_contract.jsonl"
    rows = _fixture_rows(fixture_path)
    responses = _run_fixture_session(fixture_path)
    assert responses == [row["expected"] for row in rows]


def test_bridge_protocol_error_fixture() -> None:
    fixture_path = _project_root() / "tests/fixtures/bridge_protocol/session_errors.jsonl"
    rows = _fixture_rows(fixture_path)
    responses = _run_fixture_session(fixture_path)
    assert responses == [row["expected"] for row in rows]
