from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "probe_zelph_hf_nat_routes.py"


def _write_fixture(tmp_path: Path) -> tuple[Path, Path]:
    manifest = {
        "manifestVersion": "zelph-hf-layout/v2",
        "createdAtUtc": "2026-11-14T00:00:00Z",
        "source": {"artifactName": "local-proof"},
        "selectorModel": {"unit": "section-chunk", "supportedOperations": ["node-route"]},
        "hfObjects": {"nodeRouteIndex": {"path": "hf://datasets/acrion/zelph/fixture/route.json"}},
        "sections": {
            "nodeOfName": {"chunks": [
                {"chunkIndex": 0, "length": 123, "lang": "wikidata", "objectPath": "hf://datasets/acrion/zelph/fixture/shards/nodeOfName/chunk-000000-wikidata.capnp-packed"},
                {"chunkIndex": 1, "length": 200, "lang": "en", "objectPath": "hf://datasets/acrion/zelph/fixture/shards/nodeOfName/chunk-000001-en.capnp-packed"},
            ]},
        },
    }
    route = {
        "routing": {"nodeOfName": [
            {"chunkIndex": 0, "lang": "wikidata", "names": ["Q10403939", "Q10416948", "Q10422059", "Q10651551", "Q56404383"]},
            {"chunkIndex": 1, "lang": "en", "names": ["Q10403939"]},
        ]},
    }
    manifest_path = tmp_path / "manifest.json"
    route_path = tmp_path / "route.json"
    manifest_path.write_text(json.dumps(manifest))
    route_path.write_text(json.dumps(route))
    return manifest_path, route_path


def _run(tmp_path: Path, *extra: str) -> subprocess.CompletedProcess:
    m, r = _write_fixture(tmp_path)
    return subprocess.run(
        [sys.executable, str(SCRIPT),
         "--manifest-file", str(m),
         "--sidecar-file", str(r),
         "--revision", "f" * 40,
         *extra],
        text=True, capture_output=True, check=False, timeout=12,
    )


def test_offline_five_nat_routes_are_plans_not_decoded_results(tmp_path: Path):
    proc = _run(tmp_path)
    assert proc.returncode == 0, proc.stderr + proc.stdout
    receipt = json.loads(proc.stdout)
    assert receipt["status"] == "metadata-only"
    assert receipt["source"] == "offline-local-fixture"
    assert receipt["exact_route_count"] == 5
    assert receipt["dataset_sha"] == "f" * 40
    assert all(x["selected_shard_id"] == "nodeOfName-chunk-000000-wikidata" for x in receipt["route_receipts"])
    assert receipt["payload_fetch"] is False
    assert receipt["payload_decode"] is False
    assert receipt["production_accepted"] is False


def test_offline_unmatched_qid_is_not_absence(tmp_path: Path):
    proc = _run(tmp_path, "--qid", "Q99999")
    assert proc.returncode == 2
    receipt = json.loads(proc.stdout)
    assert receipt["status"] == "partial-or-blocked"
    assert receipt["route_receipts"][0]["status"] == "route-unresolved"
    assert receipt["native_wikidata_statement_proved"] is False
    assert receipt["production_accepted"] is False


def test_offline_missing_source_route_is_a_blocker(tmp_path: Path):
    proc = subprocess.run(
        [sys.executable, str(SCRIPT),
         "--manifest-file", str(tmp_path / "does-not-exist.json"),
         "--sidecar-file", str(tmp_path / "does-not-exist.route.json"),
         "--revision", "f" * 40],
        text=True, capture_output=True, check=False, timeout=12,
    )
    assert proc.returncode == 2
    assert json.loads(proc.stdout)["status"] == "blocked"
