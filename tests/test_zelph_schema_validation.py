from __future__ import annotations

import json
from pathlib import Path

import pytest

jsonschema = pytest.importorskip("jsonschema")

from tools import prime_index as pi


def test_zelph_bundle_conforms_to_schema(tmp_path: Path) -> None:
    schema_path = Path("schemas/zelph_input.schema.json")
    schema = json.loads(schema_path.read_text(encoding="utf-8"))

    facts = [
        {
            "fact_id": "f1",
            "predicate": "applies",
            "arguments": {"subject": "contract", "object": "pet_policy"},
            "qualifiers": {"jurisdiction": "nsw"},
            "provenance": [{"doc_id": "doc1", "start": 10, "end": 20}],
            "promotion_receipt": "r1",
        }
    ]

    shards = pi.facts_to_shards(facts, artifact_revision="rev-schema")
    bundle = pi.build_zelph_input(facts, shards)

    jsonschema.validate(instance=bundle, schema=schema)
    assert bundle["facts"][0]["parse_tree"]["text"]
