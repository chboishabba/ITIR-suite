from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "SensibLaw"
sys.path.insert(0, str(ROOT))

from src.ontology.wikidata import build_slice_from_entity_exports


def _statement(value: object, *, rank: str = "normal", qualifiers: dict | None = None, references: list | None = None) -> dict:
    statement: dict[str, object] = {
        "mainsnak": {"datavalue": {"value": value}},
        "rank": rank,
    }
    if qualifiers is not None:
        statement["qualifiers"] = qualifiers
    if references is not None:
        statement["references"] = references
    return statement


def _entity_export(entities: dict[str, dict], *, source_path: str) -> dict:
    return {
        "_source_path": source_path,
        "entities": {qid: {"id": qid, **entity} for qid, entity in entities.items()},
    }


def test_build_slice_from_entity_exports_normalizes_single_object_claim_map() -> None:
    payload = build_slice_from_entity_exports(
        {
            "window-1": [
                _entity_export(
                    {
                        "Q1": {
                            "claims": {
                                "P31": [
                                    _statement({"id": "Q5"}, rank="preferred"),
                                ]
                            }
                        }
                    },
                    source_path="single-object.json",
                )
            ]
        },
        property_filter=("P31",),
    )

    assert payload["metadata"] == {
        "generated_by": "build_slice_from_entity_exports",
        "properties": ["P31"],
    }
    assert payload["windows"][0]["source_files"] == ["single-object.json"]
    assert payload["windows"][0]["statement_bundles"] == [
        {
            "subject": "Q1",
            "property": "P31",
            "value": "Q5",
            "rank": "preferred",
            "unit": None,
            "qualifiers": {},
            "references": [],
        }
    ]


def test_build_slice_from_entity_exports_accepts_list_of_sources() -> None:
    payload = build_slice_from_entity_exports(
        {
            "window-1": [
                _entity_export(
                    {
                        "Q2": {
                            "claims": {
                                "P31": [_statement({"id": "Q5"})],
                            }
                        }
                    },
                    source_path="a.json",
                ),
                _entity_export(
                    {
                        "Q1": {
                            "claims": {
                                "P31": [_statement({"id": "Q5"})],
                            }
                        }
                    },
                    source_path="b.json",
                ),
            ]
        },
        property_filter=("P31",),
    )

    assert [bundle["subject"] for bundle in payload["windows"][0]["statement_bundles"]] == ["Q2", "Q1"]
    assert payload["windows"][0]["source_files"] == ["a.json", "b.json"]


def test_build_slice_from_entity_exports_handles_qid_keyed_entity_maps() -> None:
    payload = build_slice_from_entity_exports(
        {
            "window-1": [
                _entity_export(
                    {
                        "Q10": {
                            "claims": {
                                "P31": [_statement({"id": "Q5"})],
                            }
                        },
                        "Q2": {
                            "claims": {
                                "P31": [_statement({"id": "Q1"})],
                            }
                        },
                    },
                    source_path="qid-keyed.json",
                )
            ]
        },
        property_filter=("P31",),
    )

    assert [bundle["subject"] for bundle in payload["windows"][0]["statement_bundles"]] == ["Q10", "Q2"]
    assert [bundle["value"] for bundle in payload["windows"][0]["statement_bundles"]] == ["Q5", "Q1"]


def test_build_slice_from_entity_exports_normalizes_simplified_claim_rows() -> None:
    payload = build_slice_from_entity_exports(
        {
            "window-1": [
                _entity_export(
                    {
                        "Q1": {
                            "claims": {
                                "P106": [
                                    _statement({"id": "writer"}, rank="preferred"),
                                ]
                            }
                        }
                    },
                    source_path="simplified.json",
                )
            ]
        },
        property_filter=("P106",),
    )

    assert payload["windows"][0]["statement_bundles"] == [
        {
            "subject": "Q1",
            "property": "P106",
            "value": "writer",
            "rank": "preferred",
            "unit": None,
            "qualifiers": {},
            "references": [],
        }
    ]


def test_build_slice_from_entity_exports_normalizes_realish_wikidata_claim_shapes() -> None:
    payload = build_slice_from_entity_exports(
        {
            "window-1": [
                _entity_export(
                    {
                        "Q42": {
                            "claims": {
                                "P31": [
                                    _statement(
                                        {"id": "Q5"},
                                        qualifiers={
                                            "P580": [
                                                {"datavalue": {"value": {"time": "+2000-01-01T00:00:00Z"}}}
                                            ]
                                        },
                                        references=[
                                            {
                                                "snaks": {
                                                    "P248": [
                                                        {"datavalue": {"value": {"id": "Q123"}}}
                                                    ],
                                                    "P813": [
                                                        {"datavalue": {"value": {"time": "+2024-01-01T00:00:00Z"}}}
                                                    ],
                                                }
                                            }
                                        ],
                                    )
                                ]
                            }
                        }
                    },
                    source_path="realish.json",
                )
            ]
        },
        property_filter=("P31",),
    )

    assert payload["windows"][0]["statement_bundles"] == [
        {
            "subject": "Q42",
            "property": "P31",
            "value": "Q5",
            "rank": "normal",
            "unit": None,
            "qualifiers": {"P580": ("+2000-01-01T00:00:00Z",)},
            "references": [{"P248": ["Q123"], "P813": ["+2024-01-01T00:00:00Z"]}],
        }
    ]
