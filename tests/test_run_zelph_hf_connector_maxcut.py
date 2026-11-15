"""P0 one-command connector orchestration tests; all HTTP is stubbed."""
from __future__ import annotations

import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import run_zelph_hf_connector_maxcut as runner

REV = "a" * 40
MANIFEST = "b" * 64


def test_default_is_zero_network_and_zero_files(tmp_path):
    workspace = tmp_path / "p0"
    value = runner.run_hf_connector_maxcut(
        revision=REV, manifest_sha256=MANIFEST, workspace=workspace,
    )
    assert value["metadata_fetched"] is False
    assert value["original_header_verified"] is False
    assert value["original_bin_requested_whole"] is False
    assert value["edit_authority"] is False
    assert not workspace.exists()


def _mock_header(monkeypatch):
    def fake_probe(*, receipt_dir, **kwargs):
        assert kwargs["plan"]["dataset_revision"] == REV
        receipt_dir.mkdir(parents=True, exist_ok=True)
        (receipt_dir / "original-header-proof.json").write_text('{"physical":"stub"}')
        return {
            "original_source_http_status": 206,
            "native_original_header_matches_all_four_section_counts": True,
            "full_original_index_manifest_geometry_checked": True,
            "header_raw_sha256": "c" * 64,
            "edit_authority": False,
        }
    monkeypatch.setattr(runner, "execute_metadata_header_probe", fake_probe)


def test_original_header_only_never_demands_full_bin_or_route(tmp_path, monkeypatch):
    _mock_header(monkeypatch)
    binary = tmp_path / "real-native-header-probe"
    binary.touch()
    workspace = tmp_path / "new-evidence"
    value = runner.run_hf_connector_maxcut(
        revision=REV, manifest_sha256=MANIFEST,
        workspace=workspace, execute=True, header_decoder=binary,
    )
    assert value["header_from_original_http206"] is True
    assert value["selected_original_source_byte_ranges_verified"] is False
    assert value["selected_route_origin_independently_authenticated_here"] is False
    assert value["entire_original_binary_downloaded"] is False
    assert (workspace / "physical-p0-disposition.json").is_file()


def test_missing_compiled_original_header_probe_fails_before_any_side_effect(tmp_path):
    workspace = tmp_path / "new-evidence"
    with pytest.raises(ValueError, match="compiled native original header"):
        runner.run_hf_connector_maxcut(
            revision=REV, manifest_sha256=MANIFEST,
            workspace=workspace, execute=True,
            header_decoder=tmp_path / "no-native",
        )
    assert not workspace.exists()


def test_existing_workspace_is_not_overwritten(tmp_path):
    workspace = tmp_path / "old-evidence"
    workspace.mkdir()
    binary = tmp_path / "header-probe"
    binary.touch()
    with pytest.raises(ValueError, match="refuse overwrite"):
        runner.run_hf_connector_maxcut(
            revision=REV, manifest_sha256=MANIFEST,
            workspace=workspace, execute=True, header_decoder=binary,
        )


def test_optional_selected_http206_equality_stays_separate_from_route_authentication(
    tmp_path, monkeypatch
):
    _mock_header(monkeypatch)
    binary = tmp_path / "probe"
    binary.touch()
    route = tmp_path / "externally-reviewed-source-route.json"
    route.write_text('{"routeVersion":"zelph-filtered-route/v1"}')
    workspace = tmp_path / "p0"

    def fake_plan(**kwargs):
        assert kwargs["route_path"] == route
        assert kwargs["dataset_revision"] == REV
        return {"selected_object_count": 4}
    def fake_selected(*, plan, **kwargs):
        assert plan["selected_object_count"] == 4
        return {"selected_original_hf_objects_bytes_observed": True,
                "source_bin_to_shard_ranges_verified": False}
    def fake_ranges(**kwargs):
        assert kwargs["route_path"] == route
        return {
            "selected_raw_remote_bin_ranges_equal_local_shard_bytes": True,
            "selected_object_count": 4,
            "selected_byte_count": 28,
        }
    monkeypatch.setattr(runner, "selected_fetch_plan", fake_plan)
    monkeypatch.setattr(runner, "execute_selected_fetch", fake_selected)
    monkeypatch.setattr(runner, "verify_pinned_remote_ranges", fake_ranges)
    result = runner.run_hf_connector_maxcut(
        revision=REV, manifest_sha256=MANIFEST,
        workspace=workspace, execute=True, header_decoder=binary,
        source_backed_route=route,
    )
    assert result["selected_original_source_byte_ranges_verified"] is True
    assert result["selected_route_origin_independently_authenticated_here"] is False
    assert result["selected_object_count"] == 4
    assert result["name_domain_complete"] is False
    assert result["full_query_family_closed"] is False
    assert result["p854_support_paid"] is False
    assert (workspace / "selected-shard-objects.json").is_file()
    assert (workspace / "original-selected-byte-equality.json").is_file()


def test_selected_comparator_can_fail_without_paying_a_false_physical_receipt(
    tmp_path, monkeypatch
):
    _mock_header(monkeypatch)
    binary = tmp_path / "probe"
    binary.touch()
    route = tmp_path / "source-route.json"
    route.write_text('{"routeVersion":"zelph-filtered-route/v1"}')
    workspace = tmp_path / "p0"
    monkeypatch.setattr(runner, "selected_fetch_plan", lambda **_kw: {})
    monkeypatch.setattr(runner, "execute_selected_fetch", lambda **_kw: {
        "selected_original_hf_objects_bytes_observed": True})
    monkeypatch.setattr(runner, "verify_pinned_remote_ranges", lambda **_kw: {
        "selected_raw_remote_bin_ranges_equal_local_shard_bytes": False})
    with pytest.raises(ValueError, match="not identical"):
        runner.run_hf_connector_maxcut(
            revision=REV, manifest_sha256=MANIFEST,
            workspace=workspace, execute=True, header_decoder=binary,
            source_backed_route=route,
        )
    assert not (workspace / "physical-p0-disposition.json").exists()
