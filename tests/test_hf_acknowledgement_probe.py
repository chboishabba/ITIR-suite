from __future__ import annotations

import json
import os
import subprocess
import sys

import pytest

from itir_jmd_bridge.cli import main as cli_main
from itir_jmd_bridge.providers.hf import (
    fetch_hf_object,
    parse_hf_uri,
    probe_hf_resolve_acknowledgement,
    upload_hf_file_with_ack,
)


class _FakeResponse:
    def __init__(self, *, status_code: int, url: str, headers: dict[str, str], history: list["_FakeResponse"] | None = None) -> None:
        self.status_code = status_code
        self.url = url
        self.headers = headers
        self.history = history or []

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise RuntimeError(self.status_code)


def test_parse_hf_uri_dataset_object() -> None:
    parsed = parse_hf_uri("hf://datasets/chbwa/zelph-sharded/minimal-proof/manifest.json")
    assert parsed.repo_type == "datasets"
    assert parsed.repo_id == "chbwa/zelph-sharded"
    assert parsed.object_path == "minimal-proof/manifest.json"
    assert parsed.resolve_url.endswith("/datasets/chbwa/zelph-sharded/resolve/main/minimal-proof/manifest.json")


def test_probe_hf_resolve_acknowledgement_collects_redirect_and_headers() -> None:
    redirect = _FakeResponse(
        status_code=307,
        url="https://huggingface.co/datasets/chbwa/zelph-sharded/resolve/main/minimal-proof/manifest.json",
        headers={
            "location": "/api/resolve-cache/datasets/chbwa/zelph-sharded/rev/minimal-proof%2Fmanifest.json",
            "x-repo-commit": "rev",
            "etag": '"etag0"',
            "x-linked-etag": '"etag-linked"',
        },
    )
    final = _FakeResponse(
        status_code=200,
        url="https://huggingface.co/api/resolve-cache/datasets/chbwa/zelph-sharded/rev/minimal-proof%2Fmanifest.json",
        headers={
            "etag": '"etag1"',
            "x-repo-commit": "rev",
            "content-length": "2428",
            "accept-ranges": "bytes",
            "content-disposition": 'inline; filename="manifest.json";',
        },
        history=[redirect],
    )

    payload = probe_hf_resolve_acknowledgement(
        hf_uri="hf://datasets/chbwa/zelph-sharded/minimal-proof/manifest.json",
        head=lambda *args, **kwargs: final,
    )

    assert payload["statusCode"] == 200
    assert payload["xRepoCommit"] == "rev"
    assert payload["etag"] == '"etag1"'
    assert payload["redirectChain"][0]["status_code"] == 307
    assert payload["redirectChain"][0]["x_linked_etag"] == '"etag-linked"'


def test_cli_probe_hf_ack(tmp_path) -> None:
    output_path = tmp_path / "hf-ack.json"
    env = dict(os.environ)
    env["PYTHONPATH"] = str(__import__("pathlib").Path(__file__).resolve().parents[1])
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "itir_jmd_bridge",
            "probe-hf-ack",
            "--hf-uri",
            "hf://datasets/chbwa/zelph-sharded/minimal-proof/manifest.json",
            "--output",
            str(output_path),
        ],
        check=True,
        env=env,
    )
    assert result.returncode == 0
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["repoType"] == "datasets"


def test_fetch_hf_object_collects_digest() -> None:
    payload = fetch_hf_object(
        hf_uri="hf://datasets/chbwa/zelph-sharded/minimal-proof/manifest.json",
        revision="rev",
        get=lambda *args, **kwargs: _FakeResponse(
            status_code=200,
            url="https://huggingface.co/api/resolve-cache/datasets/chbwa/zelph-sharded/rev/minimal-proof%2Fmanifest.json",
            headers={
                "etag": '"etag1"',
                "x-repo-commit": "rev",
                "content-length": "7",
            },
            history=[],
        ),
    )
    # FakeResponse returns stringified body fallback bytes; verify metadata path still lands.
    assert payload["revision"] == "rev"
    assert payload["xRepoCommit"] == "rev"
    assert payload["etag"] == '"etag1"'


def test_cli_fetch_hf_object(tmp_path) -> None:
    output_path = tmp_path / "hf-fetch.json"
    env = dict(os.environ)
    env["PYTHONPATH"] = str(__import__("pathlib").Path(__file__).resolve().parents[1])
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "itir_jmd_bridge",
            "fetch-hf-object",
            "--hf-uri",
            "hf://datasets/chbwa/zelph-sharded/minimal-proof/manifest.json",
            "--output",
            str(output_path),
        ],
        check=True,
        env=env,
    )
    assert result.returncode == 0
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["repoType"] == "datasets"


def test_upload_hf_file_with_ack_parses_commit_and_verifies(tmp_path) -> None:
    local_path = tmp_path / "bundle.tar"
    local_path.write_bytes(b"demo-bytes")

    class _Completed:
        stdout = "https://huggingface.co/datasets/chbwa/itir-zos-ack-probe/commit/0123456789abcdef0123456789abcdef01234567\n"
        stderr = ""

    payload = upload_hf_file_with_ack(
        local_path=str(local_path),
        hf_uri="hf://datasets/chbwa/itir-zos-ack-probe/bundle-demo/erdfa-demo.tar",
        commit_message="demo",
        run=lambda *args, **kwargs: _Completed(),
        fetch=lambda **kwargs: {
            "statusCode": 200,
            "revision": "0123456789abcdef0123456789abcdef01234567",
            "sha256": "3957a235fae214722cb1521c7702aca6a4a6deefcbf5f7e221879662ed84cd4b",
            "sizeBytes": 10,
        },
    )

    assert payload["acknowledgedRevision"] == "0123456789abcdef0123456789abcdef01234567"
    assert payload["verified"] is True
    assert payload["fetch"]["statusCode"] == 200


def test_cli_publish_hf_ack(tmp_path, monkeypatch) -> None:
    local_path = tmp_path / "bundle.tar"
    local_path.write_bytes(b"demo-bytes")
    output_path = tmp_path / "receipt.json"

    def _fake_upload(**kwargs):
        return {
            "sink": "hf",
            "repoType": "datasets",
            "repoId": "chbwa/itir-zos-ack-probe",
            "objectPath": "bundle-demo/erdfa-demo.tar",
            "hfUri": kwargs["hf_uri"],
            "localPath": kwargs["local_path"],
            "acknowledgedRevision": "0123456789abcdef0123456789abcdef01234567",
            "localSha256": "hash",
            "localSizeBytes": 10,
            "fetch": {"statusCode": 200, "sha256": "hash"},
            "verified": True,
        }

    monkeypatch.setattr("itir_jmd_bridge.cli.upload_hf_file_with_ack", _fake_upload)
    rc = cli_main(
        [
            "publish-hf-ack",
            "--local-path",
            str(local_path),
            "--hf-uri",
            "hf://datasets/chbwa/itir-zos-ack-probe/bundle-demo/erdfa-demo.tar",
            "--output",
            str(output_path),
        ]
    )
    assert rc == 0
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["verified"] is True


@pytest.mark.skipif(
    os.environ.get("HF_LIVE_ACK") != "1",
    reason="set HF_LIVE_ACK=1 to run the live HF acknowledgement probe",
)
def test_live_hf_acknowledgement_probe() -> None:
    payload = probe_hf_resolve_acknowledgement(
        hf_uri=os.environ.get(
            "HF_LIVE_URI",
            "hf://datasets/chbwa/zelph-sharded/minimal-proof/manifest.json",
        )
    )
    assert payload["statusCode"] == 200
    assert payload["xRepoCommit"]
    assert payload["etag"]


@pytest.mark.skipif(
    os.environ.get("HF_LIVE_ACK") != "1",
    reason="set HF_LIVE_ACK=1 to run the live HF fetch probe",
)
def test_live_hf_fetch_probe() -> None:
    payload = fetch_hf_object(
        hf_uri=os.environ.get(
            "HF_LIVE_URI",
            "hf://datasets/chbwa/zelph-sharded/minimal-proof/manifest.json",
        )
    )
    assert payload["statusCode"] == 200
    assert payload["sha256"]
    assert payload["sizeBytes"] > 0
