from __future__ import annotations

import hashlib
import json
from typing import Any


SCHEMA = "itir.pnf.numeric_abi.v0_1"


def validate_numeric_abi(payload: dict[str, Any]) -> dict[str, Any]:
    if payload.get("schema") != SCHEMA:
        raise ValueError(f"schema must be {SCHEMA}")
    if payload.get("dtype", "float32") != "float32":
        raise ValueError("dtype must be float32")
    z = _vector(payload.get("z"), "z")
    matrix = payload.get("A")
    if not isinstance(matrix, list) or not matrix:
        raise ValueError("A must be a non-empty square row-major matrix")
    size = len(z)
    if len(matrix) != size:
        raise ValueError("A row count must match len(z)")
    for row in matrix:
        values = _vector(row, "A row")
        if len(values) != size:
            raise ValueError("A must be square and match len(z)")
    b = payload.get("b")
    if b is not None and len(_vector(b, "b")) != size:
        raise ValueError("b length must match len(z)")
    row_map = payload.get("row_map")
    if not isinstance(row_map, list) or len(row_map) != size:
        raise ValueError("row_map must be receipt-bearing and match rows")
    for index, row in enumerate(row_map):
        if not isinstance(row, dict) or not row.get("receipt_ids"):
            raise ValueError(f"row_map[{index}] requires receipt_ids")
    return {"schema": SCHEMA, "rows": size, "cols": size, "dtype": "float32", "parity_hash": parity_hash(payload)}


def cpu_gemv(payload: dict[str, Any]) -> list[float]:
    validate_numeric_abi(payload)
    z = [float(value) for value in payload["z"]]
    b = [float(value) for value in payload.get("b") or [0.0 for _ in z]]
    out: list[float] = []
    for row, bias in zip(payload["A"], b):
        out.append(float(sum(float(a) * value for a, value in zip(row, z)) + bias))
    return out


def parity_hash(payload: dict[str, Any]) -> str:
    canonical = {
        "schema": payload.get("schema"),
        "dtype": payload.get("dtype", "float32"),
        "z": payload.get("z"),
        "A": payload.get("A"),
        "b": payload.get("b"),
        "row_map": payload.get("row_map"),
    }
    return hashlib.sha256(json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def _vector(value: Any, label: str) -> list[float]:
    if not isinstance(value, list):
        raise ValueError(f"{label} must be a list")
    try:
        return [float(item) for item in value]
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} must contain numeric values") from exc
