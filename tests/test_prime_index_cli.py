from __future__ import annotations

import json
from pathlib import Path

import pytest

jsonschema = pytest.importorskip("jsonschema")

from tools import prime_index as pi
from tools import prime_index_cli


def test_prime_index_cli_builds_valid_zelph_bundle(tmp_path: Path) -> None:
    facts_path = tmp_path / "facts.json"
    facts = [
        {
            "fact_id": "f1",
            "predicate": "applies",
            "arguments": {"subject": "contract", "object": "pet_policy"},
            "provenance": [{"doc_id": "doc1", "start": 0, "end": 10}],
            "promotion_receipt": "r1",
        }
    ]
    facts_path.write_text(json.dumps(facts), encoding="utf-8")

    out_path = tmp_path / "out.json"
    rc = prime_index_cli.main([str(facts_path), "--artifact-revision", "rev-test", "-o", str(out_path)])
    assert rc == 0

    bundle = json.loads(out_path.read_text(encoding="utf-8"))
    schema = json.loads(Path("schemas/zelph_input.schema.json").read_text(encoding="utf-8"))
    jsonschema.validate(instance=bundle, schema=schema)

    assert bundle["semantic_overlays"], "expected overlays present"
    assert bundle["facts"][0]["fact_id"] == "f1"
    assert bundle["facts"][0]["parse_tree"]["sents"]
