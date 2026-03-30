from __future__ import annotations

import json

from itir_jmd_bridge.cli import main as cli_main
from itir_jmd_bridge.providers.ipfs import (
    fetch_ipfs_object,
    parse_ipfs_uri,
    probe_ipfs_gateway_acknowledgement,
    publish_ipfs_file_with_ack,
)


class _FakeResponse:
    def __init__(self, *, status_code: int, url: str, headers: dict[str, str], content: bytes = b"", history=None) -> None:
        self.status_code = status_code
        self.url = url
        self.headers = headers
        self.content = content
        self.text = content.decode("utf-8", "replace")
        self.history = history or []

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise RuntimeError(self.status_code)


def test_parse_ipfs_uri() -> None:
    parsed = parse_ipfs_uri("ipfs://bafybeigdyrzt/path/to/object.tar")
    assert parsed["cid"] == "bafybeigdyrzt"
    assert parsed["path"] == "path/to/object.tar"


def test_probe_ipfs_gateway_acknowledgement() -> None:
    redirect = _FakeResponse(
        status_code=302,
        url="https://ipfs.io/ipfs/bafy-demo/object.tar",
        headers={"location": "https://gateway.example/ipfs/bafy-demo/object.tar", "etag": '"etag0"'},
    )
    final = _FakeResponse(
        status_code=200,
        url="https://gateway.example/ipfs/bafy-demo/object.tar",
        headers={"etag": '"etag1"', "content-length": "7", "content-type": "application/x-tar"},
        history=[redirect],
    )
    payload = probe_ipfs_gateway_acknowledgement(
        ipfs_uri="ipfs://bafy-demo/object.tar",
        head=lambda *args, **kwargs: final,
    )
    assert payload["cid"] == "bafy-demo"
    assert payload["statusCode"] == 200
    assert payload["etag"] == '"etag1"'
    assert payload["redirectChain"][0]["status_code"] == 302


def test_fetch_ipfs_object() -> None:
    payload = fetch_ipfs_object(
        ipfs_uri="ipfs://bafy-demo/object.txt",
        get=lambda *args, **kwargs: _FakeResponse(
            status_code=200,
            url="https://ipfs.io/ipfs/bafy-demo/object.txt",
            headers={"content-length": "11", "content-type": "text/plain"},
            content=b"hello world",
        ),
    )
    assert payload["sha256"]
    assert payload["sizeBytes"] == 11
    assert payload["text"] == "hello world"


def test_publish_ipfs_file_with_ack(tmp_path) -> None:
    local_path = tmp_path / "bundle.tar"
    local_path.write_bytes(b"demo-bytes")

    class _FakeResponse:
        def __init__(self, text: str) -> None:
            self.text = text

        def raise_for_status(self) -> None:
            return None

    calls = []

    def _fake_post(url, **kwargs):
        calls.append(url)
        if url.endswith("/version"):
            return _FakeResponse('{"Version":"0.40.1"}')
        if url.endswith("/add"):
            return _FakeResponse('{"Name":"bundle.tar","Hash":"bafybeigdyrzt6examplecid","Size":"10"}')
        if url.endswith("/pin/add"):
            return _FakeResponse('{"Pins":["bafybeigdyrzt6examplecid"]}')
        raise AssertionError(url)

    payload = publish_ipfs_file_with_ack(
        local_path=str(local_path),
        post=_fake_post,
    )
    assert payload["cid"] == "bafybeigdyrzt6examplecid"
    assert payload["verified"] is False
    assert any(url.endswith("/add") for url in calls)


def test_cli_probe_ipfs_ack(tmp_path, monkeypatch) -> None:
    output_path = tmp_path / "ipfs-ack.json"
    monkeypatch.setattr(
        "itir_jmd_bridge.cli.probe_ipfs_gateway_acknowledgement",
        lambda **kwargs: {
            "cid": "bafy-demo",
            "path": "object.tar",
            "gatewayUrl": "https://ipfs.io/ipfs/bafy-demo/object.tar",
            "statusCode": 200,
            "finalUrl": "https://ipfs.io/ipfs/bafy-demo/object.tar",
            "etag": '"etag"',
            "contentLength": "7",
            "contentType": "application/x-tar",
            "redirectChain": [],
            "fetchedAt": "2026-03-30T00:00:00Z",
        },
    )
    rc = cli_main(
        [
            "probe-ipfs-ack",
            "--ipfs-uri",
            "ipfs://bafy-demo/object.tar",
            "--output",
            str(output_path),
        ]
    )
    assert rc == 0
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["cid"] == "bafy-demo"


def test_cli_publish_ipfs_ack(tmp_path, monkeypatch) -> None:
    local_path = tmp_path / "bundle.tar"
    local_path.write_bytes(b"demo-bytes")
    output_path = tmp_path / "ipfs-publish.json"
    monkeypatch.setattr(
        "itir_jmd_bridge.cli.publish_ipfs_file_with_ack",
        lambda **kwargs: {
            "sink": "ipfs",
            "ipfsUri": "ipfs://bafy-demo",
            "cid": "bafy-demo",
            "localPath": kwargs["local_path"],
            "localSha256": "hash",
            "localSizeBytes": 10,
            "pinStatus": "pinned",
            "verified": False,
        },
    )
    rc = cli_main(
        [
            "publish-ipfs-ack",
            "--local-path",
            str(local_path),
            "--output",
            str(output_path),
        ]
    )
    assert rc == 0
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["cid"] == "bafy-demo"
