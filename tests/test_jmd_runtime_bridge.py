from __future__ import annotations

import io
import tarfile
from pathlib import Path
import pytest

from itir_jmd_bridge.contracts import validate_payload
from itir_jmd_bridge.providers.pastebin import discover_host_capabilities, fetch_browse_listing, parse_browse_html
from itir_jmd_bridge.providers.ipfs import fetch_ipfs_content
from itir_jmd_bridge.runtime import build_runtime_bundle, ingest_latest_pastes, inspect_latest_pastes_with_prototype
from itir_jmd_bridge.transport import NullTransportPlugin, publish_bundle


class _FakeResponse:
    def __init__(self, text: str, status_code: int = 200) -> None:
        self.text = text
        self.status_code = status_code

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise RuntimeError(self.status_code)


def _fake_get(url: str, timeout: float = 10.0) -> _FakeResponse:
    if url.endswith("/raw/note-0001"):
        return _FakeResponse(
            "--- note-0001 ---\n"
            "Title: note-0001\n"
            "CID: bafklocalnote\n"
            "Witness: " + "a" * 64 + "\n"
            "IPFS: bafkreigh2akiscaildcjexample000000000000000000000000000000\n"
            "DASL: 0xda5132a082861406\n"
            "Reply-To: parent-0001\n"
            "\n"
            "Alice paid Bob on 2026-03-19. Receipt hash: abc123.\n"
        )
    if url.endswith("/raw/doc-0001"):
        return _FakeResponse(
            "--- doc-0001 ---\n"
            "Title: doc-0001\n"
            "CID: bafklocaldoc\n"
            "Witness: " + "b" * 64 + "\n"
            "\n"
            "Hello world\n\nSecond paragraph.\n"
        )
    assert "/ipfs/" in url
    return _FakeResponse("Alice paid Bob on 2026-03-19. Receipt hash: abc123.\n")


def _cbor_uint(major: int, value: int) -> bytes:
    prefix = major << 5
    if value < 24:
        return bytes([prefix | value])
    if value <= 0xFF:
        return bytes([prefix | 24, value])
    if value <= 0xFFFF:
        return bytes([prefix | 25]) + value.to_bytes(2, "big")
    if value <= 0xFFFFFFFF:
        return bytes([prefix | 26]) + value.to_bytes(4, "big")
    return bytes([prefix | 27]) + value.to_bytes(8, "big")


def _cbor_encode(value: object) -> bytes:
    if isinstance(value, bool):
        return b"\xf5" if value else b"\xf4"
    if value is None:
        return b"\xf6"
    if isinstance(value, int):
        if value >= 0:
            return _cbor_uint(0, value)
        return _cbor_uint(1, -1 - value)
    if isinstance(value, bytes):
        return _cbor_uint(2, len(value)) + value
    if isinstance(value, str):
        data = value.encode("utf-8")
        return _cbor_uint(3, len(data)) + data
    if isinstance(value, list):
        return _cbor_uint(4, len(value)) + b"".join(_cbor_encode(item) for item in value)
    if isinstance(value, dict):
        encoded = _cbor_uint(5, len(value))
        for key, item in value.items():
            encoded += _cbor_encode(str(key))
            encoded += _cbor_encode(item)
        return encoded
    raise TypeError(f"unsupported test CBOR type: {type(value)!r}")


def _da51_tag(payload: object) -> bytes:
    return _cbor_uint(6, 0xDA51) + _cbor_encode(payload)


def _shard_bytes(*, shard_id: str, cid: str, component_type: str, pairs: list[list[str]] | None = None, tags: list[str] | None = None) -> bytes:
    payload = {
        "id": shard_id,
        "cid": cid,
        "component": {"type": component_type},
        "tags": tags or [],
    }
    if pairs is not None:
        payload["component"]["pairs"] = pairs
    return _da51_tag(payload)


def _manifest_bytes(name: str, shards: list[dict[str, object]]) -> bytes:
    return _da51_tag({"name": name, "shards": shards})


def _browse_html(*paste_ids: str) -> str:
    rows = "".join(
        f'<div style="border-bottom:1px solid #333;padding:10px"><a href="/paste/{paste_id}">{paste_id}</a> <span style="color:#666">{paste_id[:15]}</span></div>'
        for paste_id in paste_ids
    )
    return f"<!DOCTYPE html><html><body><div>{rows}</div></body></html>"


def test_build_runtime_bundle_from_paste_and_erdfa_descriptor() -> None:
    descriptor = {
        "provider": "erdfa-publish-rs",
        "shard_id": "note-0001",
        "cid": "bafkreigh2akiscaildcjexample000000000000000000000000000000",
        "component_kind": "text",
        "component_type": "Paragraph",
        "tags": ["note", "financial-event"],
        "link_refs": ["jmd:erdfa:shard:receipt-0001"],
    }

    bundle = build_runtime_bundle(
        base_url="https://pastebin.xware.online",
        paste_id="note-0001",
        erdfa_descriptor=descriptor,
        get=_fake_get,
        downstream_handoffs=[{"target": "SensibLaw", "kind": "object_to_corpus_bridge", "status": "planned"}],
    )

    runtime_object = bundle["runtime_object"]
    runtime_graph = bundle["runtime_graph"]
    runtime_receipt = bundle["runtime_receipt"]

    assert runtime_object["object"]["text"] == "Alice paid Bob on 2026-03-19. Receipt hash: abc123."
    assert runtime_object["object"]["content_ref"]["paste_ref"]["raw_url"].endswith("/raw/note-0001")
    assert runtime_object["object"]["erdfa"]["dasl"]["type_code"] == 3
    assert runtime_object["object"]["erdfa"]["reply_to"] == "parent-0001"
    assert runtime_graph["source_object_id"] == "jmd:erdfa:shard:note-0001"
    assert runtime_graph["edges"][0]["kind"] == "link"
    assert runtime_receipt["graph_refs"][0]["graph_id"] == runtime_graph["graph_id"]

    validate_payload(runtime_object, "runtime_object")
    validate_payload(runtime_graph, "runtime_graph")
    validate_payload(runtime_receipt, "runtime_receipt")


def test_inspect_latest_pastes_with_prototype_summarizes_proof_output() -> None:
    def fake_get(url: str, timeout: float = 10.0, headers: dict[str, str] | None = None) -> _FakeResponse:
        if url.endswith("/openapi.json"):
            return _FakeResponse(
                '{"openapi":"3.1.0","info":{"title":"kant-pastebin","version":"0.1.0"},"paths":{"/browse":{},"/paste":{},"/paste/{id}":{}}}'
            )
        if url.endswith("/browse"):
            return _FakeResponse(_browse_html("repeat-0001"))
        if url.endswith("/raw/repeat-0001"):
            return _FakeResponse(
                "--- repeat-0001 ---\n"
                "Title: repeat-0001\n"
                "CID: bafklocalrepeat\n"
                "Witness: " + "c" * 64 + "\n"
                "\n"
                "Alpha beta alpha beta alpha beta.\n"
            )
        if url.endswith("/raw/example-probe"):
            return _FakeResponse("--- example-probe ---\n\nprobe\n")
        raise AssertionError(url)

    payload = inspect_latest_pastes_with_prototype(
        base_url="https://pastebin.xware.online",
        limit=1,
        get=fake_get,
    )

    assert payload["resolved_count"] == 1
    assert payload["failure_count"] == 0
    assert payload["results"][0]["status"] == "ok"
    assert payload["results"][0]["candidate_count"] >= 1
    assert payload["results"][0]["transform_count"] >= 1
    assert payload["results"][0]["proof_normalized_cost"] <= payload["results"][0]["proof_base_cost"]


def test_parse_browse_html_extracts_latest_entries() -> None:
    entries = parse_browse_html(
        "https://pastebin.xware.online",
        _browse_html("20260321_152013_latest", "20260320_032035_previous"),
        limit=1,
    )
    assert len(entries) == 1
    assert entries[0].paste_id == "20260321_152013_latest"
    assert entries[0].paste_url.endswith("/paste/20260321_152013_latest")
    assert entries[0].raw_url.endswith("/raw/20260321_152013_latest")


def test_fetch_browse_listing_falls_back_to_trailing_slash() -> None:
    class _BrowseResponse(_FakeResponse):
        pass

    def fake_get(url: str, timeout: float = 10.0, headers: dict[str, str] | None = None) -> _BrowseResponse:
        if url.endswith("/browse"):
            return _BrowseResponse("missing", status_code=404)
        assert headers is not None
        return _BrowseResponse(_browse_html("20260321_152013_latest"))

    listing = fetch_browse_listing(
        base_url="https://pastebin.xware.online",
        limit=1,
        get=fake_get,
    )

    assert listing["browse_url"].endswith("/browse/")
    assert listing["entries"][0]["paste_id"] == "20260321_152013_latest"
    assert listing["attempts"][0]["status_code"] == 404


def test_fetch_browse_listing_records_errors_without_index_error() -> None:
    def fake_get(url: str, timeout: float = 10.0, headers: dict[str, str] | None = None) -> _FakeResponse:
        raise TimeoutError("simulated timeout")

    with pytest.raises(RuntimeError):
        fetch_browse_listing(
            base_url="https://pastebin.xware.online",
            limit=1,
            get=fake_get,
            timeout=0.1,
        )


def test_discover_host_capabilities_marks_undeclared_surfaces() -> None:
    class _JsonResponse(_FakeResponse):
        def json(self) -> dict[str, object]:
            return {
                "info": {"title": "kant-pastebin", "version": "0.1.0"},
                "paths": {"/browse": {}, "/paste": {}, "/paste/{id}": {}},
            }

    def fake_get(url: str, timeout: float = 10.0, headers: dict[str, str] | None = None) -> _FakeResponse:
        if url.endswith("/openapi.json"):
            return _JsonResponse("{}", status_code=200)
        if url.endswith("/browse"):
            return _FakeResponse(_browse_html("note-0001"), status_code=200)
        if url.endswith("/raw/example-probe"):
            return _FakeResponse("missing", status_code=404)
        if url.endswith("/ipfs/example-probe"):
            return _FakeResponse("forbidden", status_code=403)
        if url.endswith("/index.jsonl"):
            return _FakeResponse("missing", status_code=404)
        raise AssertionError(url)

    payload = discover_host_capabilities(
        base_url="https://pastebin.xware.online",
        get=fake_get,
    )

    assert payload["documented_paths"] == ["/browse", "/paste", "/paste/{id}"]
    assert any(item["path"] == "/browse" and item["documented"] for item in payload["observed_surfaces"])
    assert any(item["path"] == "/ipfs/example-probe" and not item["documented"] for item in payload["observed_surfaces"])
    assert "undeclared_surface:/ipfs/example-probe" in payload["warnings"]


def test_ingest_latest_pastes_runs_over_browse_listing() -> None:
    def fake_get(url: str, timeout: float = 10.0, headers: dict[str, str] | None = None) -> _FakeResponse:
        if url.endswith("/openapi.json"):
            class _JsonResponse(_FakeResponse):
                def json(self) -> dict[str, object]:
                    return {
                        "info": {"title": "kant-pastebin", "version": "0.1.0"},
                        "paths": {"/browse": {}, "/paste": {}, "/paste/{id}": {}},
                    }

            return _JsonResponse("{}", status_code=200)
        if url.endswith("/browse") or url.endswith("/browse/"):
            return _FakeResponse(_browse_html("note-0001", "doc-0001"))
        return _fake_get(url, timeout)

    payload = ingest_latest_pastes(
        base_url="https://pastebin.xware.online",
        limit=2,
        get=fake_get,
        verify_ipfs=True,
    )

    assert payload["resolved_count"] == 2
    assert payload["failure_count"] == 0
    assert payload["capabilities"]["documented_paths"] == ["/browse", "/paste", "/paste/{id}"]
    assert payload["adaptive_settings"]["effective_concurrency"] == 1
    assert payload["adaptive_settings"]["reasons"] == ["raw_surface_not_confirmed"]
    assert payload["results"][0]["paste_id"] == "note-0001"
    assert payload["results"][0]["status"] == "ok"
    assert payload["results"][0]["ipfs_verified"] is True
    assert payload["results"][0]["dependency_metadata"]["undeclared_dependency_count"] == 2
    assert payload["results"][1]["paste_id"] == "doc-0001"


def test_fetch_ipfs_content_uses_custom_get() -> None:
    def fake_get(url: str, timeout: float = 10.0, headers: dict[str, str] | None = None) -> _FakeResponse:
        assert url.endswith("/ipfs/QmExample")
        return _FakeResponse("hello world", status_code=200)

    result = fetch_ipfs_content(cid="QmExample", base_url="https://gateway.test", get=fake_get)
    assert result["provider"] == "ipfs_http"
    assert result["sha256"].startswith("b94d27b9934d3e08")


def test_build_runtime_bundle_with_erdfa_tar_adds_archive_receipt(tmp_path: Path) -> None:
    tar_path = tmp_path / "note-0001.tar"

    with tarfile.open(tar_path, "w") as archive:
        data = b"dummy"
        info = tarfile.TarInfo("note-0001.cbor")
        info.size = len(data)
        archive.addfile(info, io.BytesIO(data))
        manifest = tarfile.TarInfo("manifest.cbor")
        manifest.size = len(data)
        archive.addfile(manifest, io.BytesIO(data))

    bundle = build_runtime_bundle(
        base_url="https://pastebin.xware.online",
        paste_id="note-0001",
        erdfa_tar_path=tar_path,
        get=_fake_get,
    )

    actions = bundle["runtime_receipt"]["actions"]
    assert any(action["kind"] == "inspect_erdfa_archive" for action in actions)
    archive = bundle["runtime_object"]["object"]["erdfa"]["archive"]
    assert archive["manifest_present"] is True
    assert archive["shard_members"] == ["note-0001"]


def test_build_runtime_bundle_with_decoded_erdfa_tar_graph(tmp_path: Path) -> None:
    tar_path = tmp_path / "doc-0001.tar"
    post_bytes = _shard_bytes(
        shard_id="doc_post",
        cid="bafkdocpost",
        component_type="KeyValue",
        pairs=[["scale", "0"], ["content", "Hello world\n\nSecond paragraph."]],
        tags=["cft", "cft.post"],
    )
    para_bytes = _shard_bytes(
        shard_id="doc_p0",
        cid="bafkdocp0",
        component_type="KeyValue",
        pairs=[["scale", "1"], ["parent", "doc_post"], ["content", "Hello world"]],
        tags=["cft", "cft.paragraph"],
    )
    arrow_bytes = _shard_bytes(
        shard_id="doc_post→doc_p0",
        cid="bafkdocarrow",
        component_type="KeyValue",
        pairs=[
            ["from", "doc_post"],
            ["to", "doc_p0"],
            ["scale_from", "0"],
            ["scale_to", "1"],
            ["morphism", "cft.post→cft.paragraph"],
        ],
        tags=["cft", "arrow"],
    )
    manifest_bytes = _manifest_bytes(
        "doc",
        [
            {"id": "doc_post", "cid": "bafkdocpost", "tags": ["cft", "cft.post"]},
            {"id": "doc_p0", "cid": "bafkdocp0", "tags": ["cft", "cft.paragraph"]},
            {"id": "doc_post→doc_p0", "cid": "bafkdocarrow", "tags": ["cft", "arrow"]},
        ],
    )

    with tarfile.open(tar_path, "w") as archive:
        for name, payload in (
            ("doc_post.cbor", post_bytes),
            ("doc_p0.cbor", para_bytes),
            ("doc_post→doc_p0.cbor", arrow_bytes),
            ("manifest.cbor", manifest_bytes),
        ):
            info = tarfile.TarInfo(name)
            info.size = len(payload)
            archive.addfile(info, io.BytesIO(payload))

    bundle = build_runtime_bundle(
        base_url="https://pastebin.xware.online",
        paste_id="doc-0001",
        erdfa_tar_path=tar_path,
        get=_fake_get,
    )

    archive = bundle["runtime_object"]["object"]["erdfa"]["archive"]
    graph = bundle["runtime_graph"]

    assert bundle["runtime_object"]["object"]["object_id"] == "jmd:erdfa:shard:doc_post"
    assert archive["manifest"]["name"] == "doc"
    assert archive["manifest"]["shard_count"] == 3
    assert archive["primary_shard_id"] == "doc_post"
    assert any(node["node_id"] == "jmd:erdfa:manifest:doc" for node in graph["nodes"])
    assert any(edge["kind"] == "contains" for edge in graph["edges"])
    assert any(edge["kind"] == "cft_arrow" for edge in graph["edges"])
    assert any(edge["kind"] == "parent" for edge in graph["edges"])


def test_null_transport_plugin_publishes_noop_receipt() -> None:
    bundle = build_runtime_bundle(
        base_url="https://pastebin.xware.online",
        paste_id="note-0001",
        get=_fake_get,
    )
    result = publish_bundle(
        plugin=NullTransportPlugin(),
        runtime_receipt=bundle["runtime_receipt"],
        runtime_graph=bundle["runtime_graph"],
    )
    assert result["transport"] == "null"
    assert result["status"] == "skipped"
    assert result["receipt_id"] == bundle["runtime_receipt"]["receipt_id"]


def test_build_runtime_bundle_with_ipfs_verification_records_receipt_action() -> None:
    capabilities = {
        "documented_paths": ["/browse", "/paste", "/paste/{id}"],
        "observed_surfaces": [
            {"path": "/browse", "surface": "browse_html", "status_code": 200, "documented": True},
            {"path": "/raw/example-probe", "surface": "raw_template", "status_code": 200, "documented": False},
            {"path": "/ipfs/example-probe", "surface": "ipfs_template", "status_code": 200, "documented": False},
        ],
        "warnings": ["undeclared_surface:/raw/example-probe", "undeclared_surface:/ipfs/example-probe"],
    }
    bundle = build_runtime_bundle(
        base_url="https://pastebin.xware.online",
        paste_id="note-0001",
        get=_fake_get,
        verify_ipfs=True,
        capabilities=capabilities,
    )
    verification = bundle["runtime_object"]["object"]["provenance"]["ipfs_verification"]
    assert verification["matches_body_text"] is True
    assert any(action["kind"] == "verify_ipfs_proxy" for action in bundle["runtime_receipt"]["actions"])
    assert bundle["runtime_receipt"]["dependency_metadata"]["undeclared_dependency_count"] == 2
