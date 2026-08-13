from __future__ import annotations

import json
from pathlib import Path
import sqlite3
import sys

import pytest

jsonschema = pytest.importorskip("jsonschema")

from scripts import export_sl_facts_to_zelph

sys.path.insert(0, str(Path("SensibLaw").resolve()))

from src.fact_intake import build_fact_intake_payload_from_text_units, build_fact_review_workbench_payload, persist_fact_intake_payload
from src.reporting.structure_report import TextUnit


def test_export_script_accepts_jsonl_and_emits_valid_bundle(tmp_path: Path) -> None:
    input_path = tmp_path / "facts.jsonl"
    input_path.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "fact_id": "f1",
                        "predicate": "applies",
                        "arguments": {"subject": "contract", "object": "pet_policy"},
                        "provenance": [{"doc_id": "doc1", "start": 0, "end": 10}],
                        "promotion_receipt": "r1",
                    }
                ),
                json.dumps(
                    {
                        "fact_id": "f2",
                        "predicate": "requires",
                        "arguments": {"subject": "lease", "object": "bond_payment"},
                        "provenance": [{"doc_id": "doc2", "start": 10, "end": 20}],
                        "promotion_receipt": "r2",
                    }
                ),
            ]
        ),
        encoding="utf-8",
    )

    out_path = tmp_path / "zelph.json"
    rc = export_sl_facts_to_zelph.main([str(input_path), "-o", str(out_path), "--artifact-revision", "rev-job"])
    assert rc == 0

    bundle = json.loads(out_path.read_text(encoding="utf-8"))
    schema = json.loads(Path("schemas/zelph_input.schema.json").read_text(encoding="utf-8"))
    jsonschema.validate(instance=bundle, schema=schema)
    assert [fact["fact_id"] for fact in bundle["facts"]] == ["f1", "f2"]
    assert bundle["facts"][0]["parse_tree"]["sents"]


def test_export_script_accepts_workbench_payload_and_preserves_spacy_tree(tmp_path: Path) -> None:
    conn = sqlite3.connect(":memory:")
    payload = build_fact_intake_payload_from_text_units(
        [
            TextUnit(
                unit_id="u1",
                source_id="src1",
                source_type="context_file",
                text="George Bush nominated John Roberts.",
            )
        ],
        source_label="prime_export",
    )
    persist_fact_intake_payload(conn, payload)
    workbench = build_fact_review_workbench_payload(conn, run_id=payload["run"]["run_id"], include_zelph=False)

    input_path = tmp_path / "workbench.json"
    input_path.write_text(json.dumps(workbench), encoding="utf-8")
    out_path = tmp_path / "zelph_from_workbench.json"

    rc = export_sl_facts_to_zelph.main([str(input_path), "-o", str(out_path), "--artifact-revision", "rev-wb"])
    assert rc == 0

    bundle = json.loads(out_path.read_text(encoding="utf-8"))
    schema = json.loads(Path("schemas/zelph_input.schema.json").read_text(encoding="utf-8"))
    jsonschema.validate(instance=bundle, schema=schema)

    fact = bundle["facts"][0]
    assert fact["predicate"] == "statement_capture"
    assert fact["arguments"]["text"] == "George Bush nominated John Roberts."
    assert fact["parse_tree"]["text"] == "George Bush nominated John Roberts."
    assert fact["parse_tree"]["sents"][0]["tokens"]
