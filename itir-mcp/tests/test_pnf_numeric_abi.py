from __future__ import annotations

import pytest

from itir_mcp.pnf_numeric_abi import SCHEMA, cpu_gemv, validate_numeric_abi


def _payload() -> dict:
    return {
        "schema": SCHEMA,
        "dtype": "float32",
        "z": [1.0, 2.0],
        "A": [[1.0, 0.0], [0.5, 1.0]],
        "b": [0.0, 1.0],
        "row_map": [{"row": 0, "receipt_ids": ["r0"]}, {"row": 1, "receipt_ids": ["r1"]}],
    }


def test_validate_numeric_abi_and_cpu_gemv() -> None:
    summary = validate_numeric_abi(_payload())
    assert summary["schema"] == SCHEMA
    assert cpu_gemv(_payload()) == [1.0, 3.5]


def test_validate_numeric_abi_requires_receipted_row_map() -> None:
    payload = _payload()
    payload["row_map"][0]["receipt_ids"] = []
    with pytest.raises(ValueError, match="receipt_ids"):
        validate_numeric_abi(payload)
