from __future__ import annotations

import json
import sys
from typing import Any

from . import ITIR_MCP_PROTOCOL_VERSION, ITIR_MCP_VERSION, build_default_registry
from .contracts import BridgeResponse, error_payload


def _to_json(message: dict[str, Any]) -> str:
    return json.dumps(message, ensure_ascii=False, sort_keys=True)


def _registry_envelope() -> BridgeResponse:
    try:
        registry = build_default_registry()
        tools = sorted(registry.list_tools(), key=lambda spec: spec.name)
        return {
            "ok": True,
            "tools": [
                {
                    "name": spec.name,
                    "title": spec.title,
                    "description": spec.description,
                    "input_schema": spec.input_schema,
                    "response_version": spec.response_version,
                    "read_only": spec.read_only,
                }
                for spec in tools
            ],
        }
    except Exception as exc:  # pragma: no cover - one-time bootstrap hardening
        return error_payload(exc)  # type: ignore[arg-type]


def _with_request_id(response: BridgeResponse, request: dict[str, Any]) -> BridgeResponse:
    if "request_id" in request:
        response = dict(response)
        response["request_id"] = request["request_id"]
    return response


def _call_tool(name: str, payload: dict[str, Any]) -> BridgeResponse:
    if not isinstance(name, str) or not name.strip():
        return {
            "ok": False,
            "error": {"code": "input_error", "message": "tool name is required", "details": {}},
        }

    registry = build_default_registry()
    return registry.invoke(name, payload)


def _health() -> BridgeResponse:
    return {
        "ok": True,
        "service": "itir-mcp-bridge",
        "version": ITIR_MCP_VERSION,
        "protocol": ITIR_MCP_PROTOCOL_VERSION,
    }


def run() -> int:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            request = json.loads(line)
        except json.JSONDecodeError:
            print(
                _to_json(
                    {
                        "ok": False,
                        "error": {"code": "protocol_error", "message": "invalid json", "details": {}},
                    }
                ),
                flush=True,
            )
            continue
        if not isinstance(request, dict):
            print(
                _to_json(
                    {
                        "ok": False,
                        "error": {"code": "protocol_error", "message": "invalid request object", "details": {}},
                    }
                ),
                flush=True,
            )
            continue

        op = request.get("op")

        if op == "health":
            print(_to_json(_with_request_id(_health(), request)), flush=True)
            continue
        if op == "list":
            print(_to_json(_with_request_id(_registry_envelope(), request)), flush=True)
            continue
        if op == "info":
            print(
                _to_json(
                    _with_request_id(
                        {
                            "ok": True,
                            "version": ITIR_MCP_VERSION,
                            "protocol": ITIR_MCP_PROTOCOL_VERSION,
                            "tools": len(build_default_registry().list_tools()),
                            "ready": True,
                        },
                        request,
                    )
                ),
                flush=True,
            )
            continue
        if op == "call":
            payload = request.get("payload", {})
            if not isinstance(payload, dict):
                payload = {}
            name = request.get("name", "")
            print(_to_json(_with_request_id(_call_tool(name, payload), request)), flush=True)
            continue

        print(
            _to_json(
                _with_request_id(
                    {
                        "ok": False,
                        "error": {"code": "invalid_operation", "message": f"unknown op: {op}", "details": {}},
                    },
                    request,
                )
            ),
            flush=True,
        )

    return 0


def main() -> int:
    return run()


if __name__ == "__main__":
    raise SystemExit(run())
