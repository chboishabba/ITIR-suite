from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
import tarfile

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from itir_jmd_bridge.hf_rehearsal import (
    attach_object_refs_from_container,
    build_container_index_from_tar,
    extract_tar_member_bytes,
    load_erdfa_manifest_fixture,
    load_hf_container_fixture,
    resolve_selector_to_object_ref_payload,
    resolve_selector_to_remote_hf_payload,
    resolve_selector_to_remote_ipfs_payload,
    resolve_container_member,
    resolve_selector_to_local_member_payload,
    resolve_selector_to_container_member,
    resolve_selector_to_shard,
)


FIXTURE = Path("docs/planning/jmd_fixtures/hf_container_index_v1.example.json")
MANIFEST_FIXTURE = Path("docs/planning/jmd_fixtures/erdfa_manifest_promotion_v1.example.json")
ERDFA_PUBLISH_RS = Path("/home/c/Documents/code/erdfa-publish-rs")
REAL_MANIFEST = Path("/tmp/erdfa-promoted-manifest.json")
REAL_TAR = Path("/tmp/erdfa-demo.tar")


def _build_test_tar(path: Path) -> None:
    with tarfile.open(path, "w") as handle:
        for member_name, payload in (
            ("payload/left-bucket-001.cbor", b"left-payload"),
            ("payload/nodeOfName-en-017.cbor", b"name-payload"),
        ):
            info = tarfile.TarInfo(name=member_name)
            info.size = len(payload)
            handle.addfile(info, fileobj=__import__("io").BytesIO(payload))


def _ensure_real_demo_outputs() -> None:
    subprocess.run(
        ["cargo", "run", "--example", "demo"],
        check=True,
        cwd=ERDFA_PUBLISH_RS,
    )
    assert REAL_MANIFEST.exists()
    assert REAL_TAR.exists()


def test_resolve_container_member_from_fixture() -> None:
    fixture = load_hf_container_fixture(FIXTURE)

    resolved = resolve_container_member(fixture, shard_id="nodeOfName-en-017")

    assert resolved["artifactId"] == "wikidata-2026-demo"
    assert resolved["containerObjectRef"]["sink"] == "hf"
    assert resolved["member"]["memberPath"] == "payload/nodeOfName-en-017.cbor"
    assert resolved["member"]["contentDigest"] == "sha256:nodeofname-en-017-example"


def test_resolve_container_member_raises_for_unknown_shard() -> None:
    fixture = load_hf_container_fixture(FIXTURE)

    try:
        resolve_container_member(fixture, shard_id="missing-shard")
    except KeyError as exc:
        assert "missing-shard" in str(exc)
    else:
        raise AssertionError("expected KeyError for unknown shardId")


def test_cli_rehearse_hf_container(tmp_path: Path) -> None:
    output_path = tmp_path / "resolved.json"
    subprocess.run(
        [
            sys.executable,
            "-m",
            "itir_jmd_bridge",
            "rehearse-hf-container",
            "--fixture",
            str(FIXTURE),
            "--shard-id",
            "left-bucket-001",
            "--output",
            str(output_path),
        ],
        check=True,
        cwd=REPO_ROOT,
    )

    resolved = json.loads(output_path.read_text(encoding="utf-8"))
    assert resolved["member"]["shardId"] == "left-bucket-001"
    assert resolved["containerId"] == "hf-container-0001"


def test_resolve_selector_to_shard_from_promoted_manifest_fixture() -> None:
    manifest = load_erdfa_manifest_fixture(MANIFEST_FIXTURE)

    resolved = resolve_selector_to_shard(
        manifest,
        selectors=["route-name=tenant", "route-lang=en"],
    )

    assert resolved["matchedBy"] == "routingKeys"
    assert resolved["shard"]["id"] == "nodeOfName-en-017"


def test_resolve_selector_to_container_member_from_fixtures() -> None:
    manifest = load_erdfa_manifest_fixture(MANIFEST_FIXTURE)
    fixture = load_hf_container_fixture(FIXTURE)

    resolved = resolve_selector_to_container_member(
        manifest,
        fixture,
        selectors=["route-left-node=Q123"],
    )

    assert resolved["shard"]["id"] == "left-bucket-001"
    assert resolved["member"]["memberPath"] == "payload/left-bucket-001.cbor"
    assert resolved["container"]["containerId"] == "hf-container-0001"


def test_cli_rehearse_selector_fetch(tmp_path: Path) -> None:
    output_path = tmp_path / "selector-resolved.json"

    subprocess.run(
        [
            sys.executable,
            "-m",
            "itir_jmd_bridge",
            "rehearse-selector-fetch",
            "--manifest-fixture",
            str(MANIFEST_FIXTURE),
            "--container-fixture",
            str(FIXTURE),
            "--selector",
            "route-name=tenant",
            "--selector",
            "route-lang=en",
            "--output",
            str(output_path),
        ],
        check=True,
        cwd=REPO_ROOT,
    )

    resolved = json.loads(output_path.read_text(encoding="utf-8"))
    assert resolved["shard"]["id"] == "nodeOfName-en-017"
    assert resolved["member"]["memberPath"] == "payload/nodeOfName-en-017.cbor"


def test_extract_tar_member_bytes(tmp_path: Path) -> None:
    tar_path = tmp_path / "fixture.tar"
    _build_test_tar(tar_path)

    payload = extract_tar_member_bytes(tar_path, member_path="payload/left-bucket-001.cbor")

    assert payload == b"left-payload"


def test_resolve_selector_to_local_member_payload(tmp_path: Path) -> None:
    tar_path = tmp_path / "fixture.tar"
    _build_test_tar(tar_path)
    manifest = load_erdfa_manifest_fixture(MANIFEST_FIXTURE)
    fixture = load_hf_container_fixture(FIXTURE)

    resolved = resolve_selector_to_local_member_payload(
        manifest,
        fixture,
        selectors=["route-name=tenant", "route-lang=en"],
        tar_path=tar_path,
    )

    assert resolved["member"]["memberPath"] == "payload/nodeOfName-en-017.cbor"
    assert resolved["payload"]["sizeBytes"] == len(b"name-payload")


def test_resolve_selector_to_local_member_payload_without_container(tmp_path: Path) -> None:
    # Fallback inference should handle missing container fixture by checking common member paths.
    tar_path = tmp_path / "fixture.tar"
    _build_test_tar(tar_path)
    manifest = load_erdfa_manifest_fixture(MANIFEST_FIXTURE)

    resolved = resolve_selector_to_local_member_payload(
        manifest,
        None,
        selectors=["route-name=tenant", "route-lang=en"],
        tar_path=tar_path,
    )

    assert resolved["member"]["memberPath"] == "payload/nodeOfName-en-017.cbor"
    assert resolved["payload"]["sizeBytes"] == len(b"name-payload")


def test_cli_rehearse_selector_local_tar_fetch(tmp_path: Path) -> None:
    tar_path = tmp_path / "fixture.tar"
    output_path = tmp_path / "selector-local.json"
    _build_test_tar(tar_path)

    subprocess.run(
        [
            sys.executable,
            "-m",
            "itir_jmd_bridge",
            "rehearse-selector-local-tar-fetch",
            "--manifest-fixture",
            str(MANIFEST_FIXTURE),
            "--container-fixture",
            str(FIXTURE),
            "--tar-path",
            str(tar_path),
            "--selector",
            "route-left-node=Q123",
            "--output",
            str(output_path),
        ],
        check=True,
        cwd=REPO_ROOT,
    )

    resolved = json.loads(output_path.read_text(encoding="utf-8"))
    assert resolved["member"]["memberPath"] == "payload/left-bucket-001.cbor"
    assert resolved["payload"]["sizeBytes"] == len(b"left-payload")


def test_cli_rehearse_selector_local_tar_fetch_without_container(tmp_path: Path) -> None:
    tar_path = tmp_path / "fixture.tar"
    output_path = tmp_path / "selector-local.json"
    _build_test_tar(tar_path)

    subprocess.run(
        [
            sys.executable,
            "-m",
            "itir_jmd_bridge",
            "rehearse-selector-local-tar-fetch",
            "--manifest-fixture",
            str(MANIFEST_FIXTURE),
            "--tar-path",
            str(tar_path),
            "--selector",
            "route-left-node=Q123",
            "--output",
            str(output_path),
        ],
        check=True,
        cwd=REPO_ROOT,
    )

    resolved = json.loads(output_path.read_text(encoding="utf-8"))
    assert resolved["member"]["memberPath"] == "payload/left-bucket-001.cbor"
    assert resolved["payload"]["sizeBytes"] == len(b"left-payload")


def test_real_emitted_bundle_selector_objectref_fetch_end_to_end() -> None:
    _ensure_real_demo_outputs()
    manifest = load_erdfa_manifest_fixture(REAL_MANIFEST)
    file_uri = f"file://{REAL_TAR.resolve()}".replace(" ", "%20")
    hf_uri = "hf://datasets/local/erdfa-demo/container.tar"
    ipfs_uri = "ipfs://bafy-local-erdfa-demo"

    container = build_container_index_from_tar(
        manifest,
        tar_path=REAL_TAR,
        container_object_ref={
            "sink": "file",
            "uri": file_uri,
            "sizeBytes": REAL_TAR.stat().st_size,
            "contentDigest": "sha256:pending",
        },
    )
    manifested = attach_object_refs_from_container(
        manifest,
        container,
        object_refs=[
            {"sink": "file", "uri": file_uri},
            {"sink": "hf", "uri": hf_uri},
            {"sink": "ipfs", "uri": ipfs_uri},
        ],
    )

    manifest_ids = {shard["id"] for shard in manifested["shards"]}
    container_ids = {member["shardId"] for member in container["members"]}
    assert manifest_ids == container_ids

    by_member = {member["shardId"]: member for member in container["members"]}
    for sink in ("file", "hf", "ipfs"):
        resolved = resolve_selector_to_object_ref_payload(
            manifested,
            selectors=["direct-shard=heading-1"],
            preferred_sinks=[sink],
            hf_uri_map={hf_uri: str(REAL_TAR)},
            ipfs_uri_map={ipfs_uri: str(REAL_TAR)},
        )
        assert resolved["shard"]["id"] == "heading-1"
        assert resolved["selectedObjectRef"]["sink"] == sink
        expected_digest = by_member["heading-1"]["contentDigest"].split(":", 1)[1]
        assert resolved["payload"]["sha256"] == expected_digest
        assert resolved["payload"]["sizeBytes"] == by_member["heading-1"]["sizeBytes"]


def test_cli_rehearse_real_local_bundle() -> None:
    _ensure_real_demo_outputs()
    output_path = Path("/tmp/itir-real-bundle-rehearsal.json")
    if output_path.exists():
        output_path.unlink()

    subprocess.run(
        [
            sys.executable,
            "-m",
            "itir_jmd_bridge",
            "rehearse-real-local-bundle",
            "--manifest-path",
            str(REAL_MANIFEST),
            "--tar-path",
            str(REAL_TAR),
            "--selector",
            "direct-shard=heading-1",
            "--prefer-sink",
            "ipfs",
            "--output",
            str(output_path),
        ],
        check=True,
        cwd=REPO_ROOT,
    )

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["shard"]["id"] == "heading-1"
    assert payload["selectedObjectRef"]["sink"] == "ipfs"
    assert payload["payload"]["sizeBytes"] > 0


def test_resolve_selector_to_remote_hf_payload(monkeypatch) -> None:
    _ensure_real_demo_outputs()
    manifest = load_erdfa_manifest_fixture(REAL_MANIFEST)
    hf_uri = "hf://datasets/chbwa/itir-zos-ack-probe/bundle-demo/erdfa-demo.tar"

    container = build_container_index_from_tar(
        manifest,
        tar_path=REAL_TAR,
        container_object_ref={
            "sink": "hf",
            "uri": hf_uri,
            "sizeBytes": REAL_TAR.stat().st_size,
            "contentDigest": "sha256:pending",
        },
    )
    manifested = attach_object_refs_from_container(
        manifest,
        container,
        object_refs=[{"sink": "hf", "uri": hf_uri}],
    )

    monkeypatch.setattr(
        "itir_jmd_bridge.hf_rehearsal.download_hf_object_bytes",
        lambda **kwargs: {
            "bytes": REAL_TAR.read_bytes(),
            "metadata": {"statusCode": 200, "revision": kwargs["revision"], "sha256": "demo"},
        },
    )
    payload = resolve_selector_to_remote_hf_payload(
        manifested,
        selectors=["direct-shard=heading-1"],
        hf_revision="rev-demo",
    )
    assert payload["selectedObjectRef"]["sink"] == "hf"
    assert payload["fetch"]["revision"] == "rev-demo"
    assert payload["payload"]["sizeBytes"] > 0


def test_cli_rehearse_remote_hf_bundle(monkeypatch, tmp_path: Path) -> None:
    _ensure_real_demo_outputs()
    output_path = tmp_path / "remote-hf.json"

    monkeypatch.setattr(
        "itir_jmd_bridge.hf_rehearsal.download_hf_object_bytes",
        lambda **kwargs: {
            "bytes": REAL_TAR.read_bytes(),
            "metadata": {"statusCode": 200, "revision": kwargs["revision"], "sha256": "demo"},
        },
    )
    from itir_jmd_bridge.cli import main as cli_main

    rc = cli_main(
        [
            "rehearse-remote-hf-bundle",
            "--manifest-path",
            str(REAL_MANIFEST),
            "--tar-path",
            str(REAL_TAR),
            "--hf-uri",
            "hf://datasets/chbwa/itir-zos-ack-probe/bundle-demo/erdfa-demo.tar",
            "--hf-revision",
            "rev-demo",
            "--selector",
            "direct-shard=heading-1",
            "--output",
            str(output_path),
        ]
    )
    assert rc == 0
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["fetch"]["revision"] == "rev-demo"
    assert payload["selectedObjectRef"]["sink"] == "hf"


def test_resolve_selector_to_remote_ipfs_payload(monkeypatch) -> None:
    _ensure_real_demo_outputs()
    manifest = load_erdfa_manifest_fixture(REAL_MANIFEST)
    ipfs_uri = "ipfs://bafy-demo-erdfa-tar"

    container = build_container_index_from_tar(
        manifest,
        tar_path=REAL_TAR,
        container_object_ref={
            "sink": "ipfs",
            "uri": ipfs_uri,
            "sizeBytes": REAL_TAR.stat().st_size,
            "contentDigest": "sha256:pending",
        },
    )
    manifested = attach_object_refs_from_container(
        manifest,
        container,
        object_refs=[{"sink": "ipfs", "uri": ipfs_uri}],
    )

    monkeypatch.setattr(
        "itir_jmd_bridge.hf_rehearsal.download_ipfs_object_bytes",
        lambda **kwargs: {
            "bytes": REAL_TAR.read_bytes(),
            "metadata": {"statusCode": 200, "cid": "bafy-demo-erdfa-tar", "sha256": "demo"},
        },
    )
    payload = resolve_selector_to_remote_ipfs_payload(
        manifested,
        selectors=["direct-shard=heading-1"],
    )
    assert payload["selectedObjectRef"]["sink"] == "ipfs"
    assert payload["fetch"]["metadata"]["cid"] == "bafy-demo-erdfa-tar"
    assert payload["payload"]["sizeBytes"] > 0


def test_cli_rehearse_remote_ipfs_bundle(monkeypatch, tmp_path: Path) -> None:
    _ensure_real_demo_outputs()
    output_path = tmp_path / "remote-ipfs.json"

    monkeypatch.setattr(
        "itir_jmd_bridge.hf_rehearsal.download_ipfs_object_bytes",
        lambda **kwargs: {
            "bytes": REAL_TAR.read_bytes(),
            "metadata": {"statusCode": 200, "cid": "bafy-demo-erdfa-tar", "sha256": "demo"},
        },
    )
    from itir_jmd_bridge.cli import main as cli_main

    rc = cli_main(
        [
            "rehearse-remote-ipfs-bundle",
            "--manifest-path",
            str(REAL_MANIFEST),
            "--tar-path",
            str(REAL_TAR),
            "--ipfs-uri",
            "ipfs://bafy-demo-erdfa-tar",
            "--selector",
            "direct-shard=heading-1",
            "--output",
            str(output_path),
        ]
    )
    assert rc == 0
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["selectedObjectRef"]["sink"] == "ipfs"
