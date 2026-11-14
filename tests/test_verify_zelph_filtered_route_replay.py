"""Adversarial raw-byte replay tests: each independent identity axis must agree."""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


verifier = _load("verify_zelph_filtered_route_replay", ROOT / "tools" / "verify_zelph_filtered_route_replay.py")
packager = _load("package_zelph_filtered_route_receipt_replay_test", ROOT / "tools" / "package_zelph_filtered_route_receipt.py")
DATASET_SHA = "a" * 40


def _save(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def _inputs(tmp_path: Path) -> dict:
    paths = {name: tmp_path / f"{name}.json" for name in ("manifest", "request", "route", "receipt")}
    manifest = {
        "manifestVersion": 2,
        "storageMode": "split-by-direction-and-section",
        "source": {"artifactName": "wikidata-20260309-all"},
        "sections": {"nodeOfName": {"chunks": [
            {"chunkIndex": 1, "lang": "wikidata", "length": 42},
        ]}},
    }
    _save(paths["manifest"], manifest)
    manifest_sha = sha256(paths["manifest"].read_bytes()).hexdigest()
    request = {
        "request_ref": "nat:pinned-tranche",
        "filtered_request": True,
        "full_route_materialization_required": False,
        "qids": ["Q10403939"],
        "source_manifest": {
            "manifest_version": "zelph-hf-layout/v2",
            "manifest_digest": "sha256:" + manifest_sha,
            "manifest_revision": DATASET_SHA,
        },
    }
    route = {
        "routeVersion": "zelph-filtered-route/v1",
        "requestedQids": ["Q10403939"],
        "source": {
            "binPath": "/frozen/original.bin", "binSizeBytes": 100,
            "leftChunkCount": 1, "rightChunkCount": 1,
            "nameOfNodeChunkCount": 1, "nodeOfNameChunkCount": 1,
        },
        "language": "wikidata",
        "qidToZelphNodeIds": {"Q10403939": 24721153},
        "qidToNodeOfNameChunks": {"Q10403939": 1},
        "nodeRoutes": {"24721153": {"left": [0], "right": [0], "nameOfNode": [0]}},
        "resolvedQidCount": 1,
        "completeQidResolution": True,
        "fullRouteMaterializationPerformed": False,
    }
    _save(paths["request"], request)
    _save(paths["route"], route)
    receipt = packager.build_receipt(
        request=request,
        route=route,
        route_path=paths["route"],
        actual_producer_commit="c" * 40,
    )
    _save(paths["receipt"], receipt)
    return {**paths, "manifest_sha256": manifest_sha}


def _run(paths: dict, *, digest: str | None = None):
    return verifier.verify_local_replay(
        request_path=paths["request"],
        manifest_path=paths["manifest"],
        route_path=paths["route"],
        receipt_path=paths["receipt"],
        expected_dataset_sha=DATASET_SHA,
        expected_manifest_sha256=digest or paths["manifest_sha256"],
    )


def test_pinned_four_object_replay_succeeds_but_not_physical_or_source_complete(tmp_path):
    paths = _inputs(tmp_path)
    output = _run(paths)
    assert output["status"] == "local-byte-and-semantic-replay-verified"
    assert output["resolved_qid_count"] == 1
    assert output["receipt_payload_digest_verified"]
    assert not output["physical_chunk_bytes_verified"]
    assert not output["graph_query_closure_proved"]
    assert not output["source_bin_to_hf_dataset_identity_proved"]
    assert not output["remote_response_origin_authenticated"]
    assert not output["production_accepted"]


@pytest.mark.parametrize("mutate", ["manifest", "route", "request", "receipt"])
def test_independent_raw_byte_tamper_is_rejected(tmp_path, mutate):
    paths = _inputs(tmp_path)
    data = json.loads(paths[mutate].read_text())
    if mutate == "manifest":
        data["source"]["artifactName"] = "other"
    elif mutate == "route":
        data["qidToZelphNodeIds"]["Q10403939"] = 1
    elif mutate == "request":
        data["source_manifest"]["manifest_revision"] = "b" * 40
    else:
        data["source_support_paid"] = True
    _save(paths[mutate], data)
    with pytest.raises(ValueError):
        _run(paths)


def test_rehashed_receipt_cannot_change_qid_or_physical_route(tmp_path):
    paths = _inputs(tmp_path)
    receipt = json.loads(paths["receipt"].read_text())
    receipt["qid_to_node_of_name_chunks"]["Q10403939"] = 75
    unsigned = dict(receipt)
    unsigned.pop("receipt_digest_sha256")
    receipt["receipt_digest_sha256"] = sha256(json.dumps(
        unsigned, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode()).hexdigest()
    _save(paths["receipt"], receipt)
    with pytest.raises(ValueError, match="decoded QID mapping"):
        _run(paths)


def test_duplicate_json_key_fail_closed(tmp_path):
    paths = _inputs(tmp_path)
    paths["manifest"].write_text('{"manifestVersion":2,"manifestVersion":3}')
    with pytest.raises(ValueError, match="duplicate JSON key"):
        _run(paths)


def test_unpinned_revision_and_external_manifest_digest_fail(tmp_path):
    paths = _inputs(tmp_path)
    with pytest.raises(ValueError, match="invalid pinned dataset SHA"):
        verifier.verify_local_replay(
            request_path=paths["request"], manifest_path=paths["manifest"],
            route_path=paths["route"], receipt_path=paths["receipt"],
            expected_dataset_sha="main", expected_manifest_sha256=paths["manifest_sha256"],
        )
    with pytest.raises(ValueError, match="raw manifest SHA256 mismatch"):
        _run(paths, digest="f" * 64)


def test_missing_physical_route_and_extra_qid_refused_even_with_valid_receipt_hash(tmp_path):
    paths = _inputs(tmp_path)
    route = json.loads(paths["route"].read_text())
    route["nodeRoutes"] = {}
    _save(paths["route"], route)
    receipt = packager.build_receipt(
        request=json.loads(paths["request"].read_text()),
        route=route, route_path=paths["route"], actual_producer_commit="c" * 40
    )
    _save(paths["receipt"], receipt)
    with pytest.raises(ValueError, match="nodeRoutes"):
        _run(paths)
