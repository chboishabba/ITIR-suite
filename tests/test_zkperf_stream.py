from __future__ import annotations

import io
import json
import tarfile
from pathlib import Path

from itir_jmd_bridge.zkperf_stream_core import (
    build_zkperf_stream_bundle,
    load_zkperf_stream_fixture,
)
from itir_jmd_bridge.zkperf_stream_index import (
    apply_zkperf_stream_retention_policy,
    build_zkperf_stream_index,
    build_zkperf_stream_latest,
    get_zkperf_stream_index_record,
    update_zkperf_stream_index,
    write_zkperf_stream_publish_artifacts,
)

FIXTURE = Path("docs/planning/jmd_fixtures/zkperf_stream_v1.example.json")


def test_build_zkperf_stream_bundle() -> None:
    fixture = load_zkperf_stream_fixture(FIXTURE)
    bundle = build_zkperf_stream_bundle(fixture)
    assert bundle["streamManifest"]["streamId"] == "zkperf-stream-demo"
    assert len(bundle["streamManifest"]["windows"]) == 2
    assert bundle["streamManifest"]["latestWindowId"] == "window-0002"
    assert bundle["streamManifest"]["observationCount"] == 2
    index = bundle["streamManifest"]["observationIndex"]
    assert len(index) == 2
    assert index[0]["observationId"]
    assert index[0]["runId"]
    assert index[0]["traceId"]
    assert index[0]["hash"]
    assert bundle["tarDigest"]

    payload = {}
    with tarfile.open(fileobj=io.BytesIO(bundle["tarBytes"]), mode="r:*") as handle:
        member = handle.getmember("windows/window-0001.json")
        extracted = handle.extractfile(member)
        assert extracted is not None
        payload = json.loads(extracted.read().decode("utf-8"))
    metrics = payload["observations"][0]["metrics"]
    metric_keys = {item.get("metric") or item.get("name") for item in metrics}
    assert "stream_window_count" in metric_keys
    assert "stream_observation_count" in metric_keys
    assert "window_observation_count" in metric_keys
    assert "window_sequence" in metric_keys


def test_update_zkperf_stream_index_append() -> None:
    fixture = load_zkperf_stream_fixture(FIXTURE)
    bundle = build_zkperf_stream_bundle(fixture)
    index = update_zkperf_stream_index(
        existing_index=build_zkperf_stream_index(
            stream_id="zkperf-stream-demo",
            index_hf_uri="hf://datasets/chbwa/itir-zos-ack-probe/zkperf-stream/zkperf-stream-demo.index.json",
            created_at="2026-03-30T10:00:00Z",
        ),
        stream_manifest=bundle["streamManifest"],
        hf_receipt={"acknowledgedRevision": "rev-demo", "verified": True},
        index_hf_uri="hf://datasets/chbwa/itir-zos-ack-probe/zkperf-stream/zkperf-stream-demo.index.json",
    )
    assert index["latestRevision"] == "rev-20260330-a"
    assert index["revisionCount"] == 1
    assert index["revisions"][0]["latestWindowId"] == "window-0002"
    assert index["revisions"][0]["windows"][1]["windowId"] == "window-0002"


def test_update_zkperf_stream_index_preserves_prior_revision() -> None:
    fixture = load_zkperf_stream_fixture(FIXTURE)
    bundle_a = build_zkperf_stream_bundle(fixture)
    index = update_zkperf_stream_index(
        existing_index=None,
        stream_manifest=bundle_a["streamManifest"],
        hf_receipt={"acknowledgedRevision": "rev-a", "verified": True},
        index_hf_uri="hf://datasets/chbwa/itir-zos-ack-probe/zkperf-stream/zkperf-stream-demo.index.json",
    )
    fixture_b = json.loads(json.dumps(fixture))
    fixture_b["streamRevision"] = "rev-20260330-b"
    fixture_b["createdAtUtc"] = "2026-03-30T11:00:00Z"
    fixture_b["windows"].append(
        {
            "windowId": "window-0003",
            "sequence": 3,
            "runId": "run-20260330-b",
            "traceId": "trace-20260330-0003",
            "observationIds": ["zkperf-obsv-0003"],
            "startedAtUtc": "2026-03-30T11:00:00Z",
            "endedAtUtc": "2026-03-30T11:00:03Z",
            "payload": {"observations": []},
        }
    )
    bundle_b = build_zkperf_stream_bundle(fixture_b)
    updated = update_zkperf_stream_index(
        existing_index=index,
        stream_manifest=bundle_b["streamManifest"],
        hf_receipt={"acknowledgedRevision": "rev-b", "verified": True},
        index_hf_uri="hf://datasets/chbwa/itir-zos-ack-probe/zkperf-stream/zkperf-stream-demo.index.json",
    )
    assert updated["latestRevision"] == "rev-20260330-b"
    assert updated["revisionCount"] == 2
    assert [item["streamRevision"] for item in updated["revisions"]] == ["rev-20260330-a", "rev-20260330-b"]
    assert updated["revisions"][1]["windows"][-1]["windowId"] == "window-0003"


def test_apply_zkperf_stream_retention_policy_latest_n() -> None:
    kept = apply_zkperf_stream_retention_policy(
        [
            {"streamRevision": "rev-a"},
            {"streamRevision": "rev-b"},
            {"streamRevision": "rev-c"},
        ],
        {
            "policyVersion": "zkperf-retention/v1",
            "mode": "retain-latest-n",
            "maxRevisionCount": 2,
        },
    )
    assert [item["streamRevision"] for item in kept] == ["rev-b", "rev-c"]


def test_update_zkperf_stream_index_enforces_retention() -> None:
    policy = {
        "policyVersion": "zkperf-retention/v1",
        "mode": "retain-latest-n",
        "maxRevisionCount": 2,
    }
    base = build_zkperf_stream_index(
        stream_id="zkperf-stream-demo",
        index_hf_uri="hf://datasets/chbwa/itir-zos-ack-probe/zkperf-stream/zkperf-stream-demo.index.json",
        created_at="2026-03-30T10:00:00Z",
        retention_policy=policy,
    )
    revisions = []
    for suffix, seq in [("a", 2), ("b", 3), ("c", 4)]:
        fixture = load_zkperf_stream_fixture(FIXTURE)
        fixture["streamRevision"] = f"rev-20260330-{suffix}"
        fixture["windows"] = fixture["windows"][:]
        fixture["windows"][-1]["sequence"] = seq
        fixture["windows"][-1]["windowId"] = f"window-000{seq}"
        bundle = build_zkperf_stream_bundle(fixture)
        base = update_zkperf_stream_index(
            existing_index=base,
            stream_manifest=bundle["streamManifest"],
            hf_receipt={"acknowledgedRevision": f"ack-{suffix}", "verified": True},
            retention_policy=policy,
        )
        revisions = [item["streamRevision"] for item in base["revisions"]]
    assert revisions == ["rev-20260330-b", "rev-20260330-c"]
    assert base["revisionCount"] == 2
    assert base["latestRevision"] == "rev-20260330-c"


def test_get_zkperf_stream_index_record_latest() -> None:
    record = get_zkperf_stream_index_record(
        {
            "latestRevision": "rev-b",
            "revisions": [
                {"streamRevision": "rev-a"},
                {"streamRevision": "rev-b"},
            ],
        },
        latest=True,
    )
    assert record["streamRevision"] == "rev-b"


def test_write_zkperf_stream_publish_artifacts(tmp_path: Path) -> None:
    fixture = load_zkperf_stream_fixture(FIXTURE)
    bundle = build_zkperf_stream_bundle(fixture)
    latest = build_zkperf_stream_latest(
        bundle["streamManifest"],
        {"acknowledgedRevision": "rev-demo", "verified": True},
    )
    paths = write_zkperf_stream_publish_artifacts(
        output_root=tmp_path,
        publish_payload={
            "streamManifest": bundle["streamManifest"],
            "streamLatest": latest,
            "hfReceipt": {"acknowledgedRevision": "rev-demo", "verified": True},
            "streamIndex": {"latestRevision": "rev-20260330-a"},
            "streamIndexReceipt": {"acknowledgedRevision": "rev-index", "verified": True},
        },
    )
    assert Path(paths["streamManifest"]).exists()
    assert Path(paths["streamLatest"]).exists()
    assert Path(paths["hfReceipt"]).exists()
    assert Path(paths["streamIndex"]).exists()
    assert Path(paths["streamIndexReceipt"]).exists()
