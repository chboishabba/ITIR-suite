from __future__ import annotations

from itir_jmd_bridge.contracts import load_example, validate_payload


def test_runtime_object_example_validates() -> None:
    validate_payload(load_example("jmd_runtime_object_minimal.json"), "runtime_object")


def test_runtime_graph_example_validates() -> None:
    validate_payload(load_example("jmd_runtime_graph_minimal.json"), "runtime_graph")


def test_runtime_receipt_example_validates() -> None:
    validate_payload(load_example("jmd_runtime_receipt_minimal.json"), "runtime_receipt")
