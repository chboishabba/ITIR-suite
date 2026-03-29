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
    extract_tar_member_bytes,
    load_erdfa_manifest_fixture,
    load_hf_container_fixture,
    resolve_container_member,
    resolve_selector_to_local_member_payload,
    resolve_selector_to_container_member,
    resolve_selector_to_shard,
)


FIXTURE = Path("docs/planning/jmd_fixtures/hf_container_index_v1.example.json")
MANIFEST_FIXTURE = Path("docs/planning/jmd_fixtures/erdfa_manifest_promotion_v1.example.json")


def _build_test_tar(path: Path) -> None:
    with tarfile.open(path, "w") as handle:
        for member_name, payload in (
            ("payload/left-bucket-001.cbor", b"left-payload"),
            ("payload/nodeOfName-en-017.cbor", b"name-payload"),
        ):
            info = tarfile.TarInfo(name=member_name)
            info.size = len(payload)
            handle.addfile(info, fileobj=__import__("io").BytesIO(payload))


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
