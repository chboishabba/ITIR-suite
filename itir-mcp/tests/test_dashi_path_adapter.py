from __future__ import annotations

from itir_mcp.dashi_path_adapter import run_cpu_numeric_adapter
from itir_mcp.dashi_vulkan_tools import probe_vulkan_path
from itir_mcp.pnf_numeric_abi import SCHEMA


def test_dashi_cpu_adapter_emits_matrix_ready_row() -> None:
    payload = {
        "schema": SCHEMA,
        "dtype": "float32",
        "z": [2.0],
        "A": [[3.0]],
        "row_map": [{"row": 0, "receipt_ids": ["r"]}],
    }
    row = run_cpu_numeric_adapter(payload)
    assert row["suite"] == "dashi_vulkan_adapter"
    assert row["active_backend"] == "cpu"
    assert row["result"] == [6.0]
    assert row["parity_hash"]


def test_vulkan_probe_is_skip_only_until_ready() -> None:
    row = probe_vulkan_path()
    assert row["suite"] == "dashi_vulkan_adapter"
    assert row["status"] in {"ok", "skipped"}
    assert "intent_gpu" in row
