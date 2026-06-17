from __future__ import annotations

import sys
import types

from itir_mcp.sensiblaw_spectral_adapter import UNAVAILABLE, materialize_sensiblaw_spectral_payload


def test_sensiblaw_spectral_adapter_unavailable_has_no_fabricated_receipts(monkeypatch) -> None:
    before_path = list(sys.path)

    def fake_import(name: str):
        if name in {"SensibLaw", "sensiblaw"}:
            sys.modules["src.polluted_by_failed_adapter"] = types.ModuleType("src.polluted_by_failed_adapter")
            raise ImportError(name)
        raise AssertionError(name)

    monkeypatch.setattr("itir_mcp.sensiblaw_spectral_adapter.importlib.import_module", fake_import)
    result = materialize_sensiblaw_spectral_payload({"text": "candidate"})
    assert result["status"] == UNAVAILABLE
    assert result["receipt_ids"] == []
    assert result["diagnostic_only"] is True
    assert sys.path == before_path
    assert "src.polluted_by_failed_adapter" not in sys.modules
