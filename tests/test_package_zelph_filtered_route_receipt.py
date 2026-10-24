from __future__ import annotations

import importlib.util
import json
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "package_zelph_filtered_route_receipt.py"
spec = importlib.util.spec_from_file_location("package_zelph_filtered_route_receipt", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


def _request() -> dict:
    return {
        "request_ref": "nat-filtered-route-request:test",
        "filtered_request": True,
        "full_route_materialization_required": False,
        "qids": ["Q1", "Q2"],
        "source_manifest": {
            "manifest_version": "zelph-hf-layout/v2",
            "manifest_digest": "sha256:test",
            "manifest_revision": "rev",
            "node_route_index_observed": False,
        },
    }


def _route() -> dict:
    return {
        "routeVersion": "zelph-filtered-route/v1",
        "source": {"binPath": "/tmp/wd.bin", "binSizeBytes": 123},
        "language": "wikidata",
        "requestedQids": ["Q1", "Q2"],
        "qidToZelphNodeIds": {"Q1": 10, "Q2": 20},
        "qidToNodeOfNameChunks": {"Q1": 3, "Q2": 4},
        "nodeRoutes": {
            "10": {"left": [1], "right": [2], "nameOfNode": [5]},
            "20": {"left": [7], "right": [], "nameOfNode": [9]},
        },
        "resolvedQidCount": 2,
        "completeQidResolution": True,
        "fullRouteMaterializationPerformed": False,
    }


def _write_route(tmp_path: Path, route: dict) -> Path:
    path = tmp_path / "route.json"
    path.write_text(json.dumps(route, sort_keys=True), encoding="utf-8")
    return path


def test_complete_filtered_route_receipt_preserves_base_and_actual_producer_lineage(tmp_path: Path) -> None:
    route = _route()
    route_path = _write_route(tmp_path, route)
    receipt = module.build_receipt(
        request=_request(),
        route=route,
        route_path=route_path,
        actual_producer_commit="actual-commit",
    )
    assert receipt["schema_version"] == module.RECEIPT_SCHEMA
    assert receipt["complete_qid_resolution"] is True
    assert receipt["unresolved_qids"] == []
    assert receipt["missing_node_routes"] == []
    assert receipt["qid_to_zelph_node_ids"] == {"Q1": 10, "Q2": 20}
    assert receipt["producer_lineage"]["derived_from"]["commit"] == module.BASE_PRODUCER_COMMIT
    assert receipt["producer_lineage"]["actual_producer"]["commit"] == "actual-commit"
    assert receipt["route_artifact_content_address"].startswith("sha256:")
    assert receipt["source_support_paid"] is False
    assert receipt["consumer_verification_performed"] is False
    assert receipt["semantic_promotion_performed"] is False
    assert receipt["edits_performed"] is False


def test_unresolved_qid_keeps_receipt_incomplete(tmp_path: Path) -> None:
    route = _route()
    route["qidToZelphNodeIds"]["Q2"] = None
    route["nodeRoutes"].pop("20")
    route["completeQidResolution"] = False
    route_path = _write_route(tmp_path, route)
    receipt = module.build_receipt(
        request=_request(),
        route=route,
        route_path=route_path,
        actual_producer_commit="actual-commit",
    )
    assert receipt["complete_qid_resolution"] is False
    assert receipt["unresolved_qids"] == ["Q2"]
    assert receipt["source_support_paid"] is False


def test_route_qids_must_exactly_match_request(tmp_path: Path) -> None:
    route = _route()
    route["requestedQids"] = ["Q1"]
    route_path = _write_route(tmp_path, route)
    try:
        module.build_receipt(
            request=_request(),
            route=route,
            route_path=route_path,
            actual_producer_commit="actual-commit",
        )
    except ValueError as exc:
        assert "exactly match" in str(exc)
    else:
        raise AssertionError("expected QID mismatch to fail")


def test_full_route_materialization_is_rejected(tmp_path: Path) -> None:
    route = _route()
    route["fullRouteMaterializationPerformed"] = True
    route_path = _write_route(tmp_path, route)
    try:
        module.build_receipt(
            request=_request(),
            route=route,
            route_path=route_path,
            actual_producer_commit="actual-commit",
        )
    except ValueError as exc:
        assert "full route" in str(exc)
    else:
        raise AssertionError("expected full-route materialization to fail")
