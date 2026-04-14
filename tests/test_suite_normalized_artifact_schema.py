from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPO_ROOT / "schemas" / "itir.normalized.artifact.v1.schema.json"
EXAMPLE_PATH = REPO_ROOT / "examples" / "itir.normalized_artifact.minimal.json"


def _load_schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def _validator() -> jsonschema.Draft202012Validator:
    return jsonschema.Draft202012Validator(_load_schema())


def test_suite_normalized_artifact_example_validates() -> None:
    payload = json.loads(EXAMPLE_PATH.read_text(encoding="utf-8"))
    _validator().validate(payload)


def test_promoted_record_requires_receipt_and_promoted_truth_authority() -> None:
    payload = json.loads(EXAMPLE_PATH.read_text(encoding="utf-8"))
    payload["artifact_role"] = "promoted_record"
    payload["authority"] = {
        "authority_class": "review",
        "derived": False,
        "promotion_receipt_ref": None,
    }
    payload["follow_obligation"] = None
    payload["unresolved_pressure_status"] = "none"

    with pytest.raises(jsonschema.ValidationError):
        _validator().validate(payload)


def test_follow_obligation_requires_non_none_pressure_state() -> None:
    payload = json.loads(EXAMPLE_PATH.read_text(encoding="utf-8"))
    payload["unresolved_pressure_status"] = "none"

    with pytest.raises(jsonschema.ValidationError):
        _validator().validate(payload)


def test_join_semantics_surface_is_admissible() -> None:
    payload = json.loads(EXAMPLE_PATH.read_text(encoding="utf-8"))
    payload["join_semantics"] = {
        "modality": "must not",
        "priority_rank": 7,
        "exception_active": False,
        "override_active": True,
    }

    _validator().validate(payload)
