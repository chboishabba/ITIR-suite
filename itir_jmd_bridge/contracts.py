from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "schemas"
EXAMPLE_DIR = ROOT / "examples" / "jmd_bridge"

SCHEMA_FILES = {
    "runtime_object": "jmd.runtime.object.v1.schema.json",
    "runtime_graph": "jmd.runtime.graph.v1.schema.json",
    "runtime_receipt": "jmd.runtime.receipt.v1.schema.json",
}


def load_schema(schema_name: str) -> dict[str, Any]:
    filename = SCHEMA_FILES[schema_name]
    return json.loads((SCHEMA_DIR / filename).read_text(encoding="utf-8"))


def load_example(filename: str) -> dict[str, Any]:
    return json.loads((EXAMPLE_DIR / filename).read_text(encoding="utf-8"))


def validate_payload(payload: dict[str, Any], schema_name: str) -> None:
    jsonschema.validate(payload, load_schema(schema_name))
