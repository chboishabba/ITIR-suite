from __future__ import annotations

from itir_jmd_bridge.prototype_mdl import project_runtime_bundle_to_graph_input, run_pipeline, run_runtime_bundle_pipeline
from itir_jmd_bridge.runtime import build_runtime_bundle


class _FakeResponse:
    def __init__(self, text: str, status_code: int = 200) -> None:
        self.text = text
        self.status_code = status_code

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise RuntimeError(self.status_code)


def _fake_get(url: str, timeout: float = 10.0) -> _FakeResponse:
    if url.endswith("/raw/repeat-0001"):
        return _FakeResponse(
            "--- repeat-0001 ---\n"
            "Title: repeat-0001\n"
            "CID: bafklocalrepeat\n"
            "Witness: " + "c" * 64 + "\n"
            "\n"
            "Alpha beta alpha beta alpha beta.\n"
        )
    raise AssertionError(url)


def test_run_pipeline_emits_transform_plan_and_proof() -> None:
    payload = run_pipeline(
        {
            "doc_id": "my-doc",
            "nodes": [
                {"id": "n1", "type": "Token", "text": "hello world hello world", "tags": ["cft"]},
                {"id": "n2", "type": "Token", "text": "hello world again", "tags": ["cft"]},
            ],
            "edges": [
                {"id": "e1", "source": "n1", "target": "n2", "morphism": "wf::next"},
            ],
        }
    )

    assert payload["candidate_transforms"]
    assert payload["transform_plan"]
    assert payload["dictionary"]["M0"] == "hello world"
    assert payload["normalized_graph"]["nodes"][0]["text"] == "M0 M0"
    assert payload["proof"]["type"] == "sl::MDLProof"
    assert payload["proof"]["search_family"] == "macro_subgraph_v1"
    assert payload["proof"]["normalized_cost"] <= payload["proof"]["base_cost"]


def test_project_runtime_bundle_to_graph_input_uses_runtime_bundle_fields() -> None:
    bundle = build_runtime_bundle(
        base_url="https://pastebin.xware.online",
        paste_id="repeat-0001",
        erdfa_descriptor={
            "provider": "erdfa-publish-rs",
            "shard_id": "repeat-0001",
            "cid": "bafkrepeat0001",
            "component_kind": "text",
            "component_type": "Paragraph",
            "tags": ["note"],
            "link_refs": ["jmd:erdfa:shard:repeat-0002"],
        },
        get=_fake_get,
    )

    projected = project_runtime_bundle_to_graph_input(bundle)

    assert projected["doc_id"] == bundle["runtime_graph"]["graph_id"]
    assert projected["nodes"][0]["id"] == bundle["runtime_graph"]["source_object_id"]
    assert "Alpha beta alpha beta alpha beta." in projected["nodes"][0]["text"]
    assert projected["edges"][0]["morphism"] == "link"


def test_run_runtime_bundle_pipeline_emits_transform_and_proof() -> None:
    bundle = build_runtime_bundle(
        base_url="https://pastebin.xware.online",
        paste_id="repeat-0001",
        erdfa_descriptor={
            "provider": "erdfa-publish-rs",
            "shard_id": "repeat-0001",
            "cid": "bafkrepeat0001",
            "component_kind": "text",
            "component_type": "Paragraph",
            "tags": ["note"],
        },
        get=_fake_get,
    )

    payload = run_runtime_bundle_pipeline(bundle)

    assert payload["candidate_transforms"]
    assert payload["transform_plan"]
    assert payload["proof"]["type"] == "sl::MDLProof"
    assert payload["proof"]["normalized_cost"] <= payload["proof"]["base_cost"]
