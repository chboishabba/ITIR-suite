from itir_mcp import build_default_registry


def test_obligations_query_returns_deterministic_payload() -> None:
    registry = build_default_registry()
    result = registry.invoke(
        "sensiblaw.obligations_query",
        {
            "text": "The tenant must pay rent on time.",
            "source_id": "demo",
        },
    )
    assert result["ok"] is True
    payload = result["result"]
    assert payload["version"] == "obligation.query.v1"
    assert payload["results"]
    assert payload["results"][0]["modality"] == "must"


def test_unknown_tool_returns_contract_error() -> None:
    registry = build_default_registry()
    result = registry.invoke("sensiblaw.unknown_tool", {"text": "abc"})

    assert result["ok"] is False
    assert result["error"]["code"] == "tool_error"
    assert "Unknown tool" in result["error"]["message"]
