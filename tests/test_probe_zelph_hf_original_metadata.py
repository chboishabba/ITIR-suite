"""Metadata-only original HF P0 operator protocol; no actual network."""
from __future__ import annotations

from pathlib import Path
from hashlib import sha256
import sys

import pytest

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))
from probe_zelph_hf_original_metadata import (
    plan_metadata_header_probe, execute_metadata_header_probe,
)

REV = "a" * 40
M_SHA = "b" * 64


def _plan(tmp_path):
    local = tmp_path / "raw-metadata"
    receipts = tmp_path / "immutable-p0-receipts"
    plan = plan_metadata_header_probe(
        dataset_revision=REV, manifest_sha256=M_SHA,
        local_dir=local, receipt_dir=receipts,
    )
    return plan, local, receipts


def test_dry_run_only_two_immutable_small_metadata_objects_no_original_bin(tmp_path):
    plan, local, receipts = _plan(tmp_path)
    assert plan["selected_file_count"] == 2
    assert plan["network_executed"] is False
    assert plan["whole_original_bin_requested"] is False
    assert plan["all_name_shards_requested"] is False
    argv = plan["hf_download_argv"]
    assert argv[:3] == ["hf", "download", "acrion/zelph"]
    assert argv[3:5] == [
        "wikidata-20260309-all/wikidata-20260309-all.hf-v2.json",
        "wikidata-20260309-all/artifact.index.json",
    ]
    assert argv[argv.index("--revision") + 1] == REV
    assert "wikidata-20260309-all.bin" not in argv
    assert not local.exists()
    assert not receipts.exists()


def test_bad_revision_or_pinned_manifest_hash_fails_before_network(tmp_path):
    _, local, receipts = _plan(tmp_path)
    for rev, manifest in (("main", M_SHA), (REV, "not-a-sha")):
        with pytest.raises(ValueError, match="immutable revision"):
            plan_metadata_header_probe(
                dataset_revision=rev, manifest_sha256=manifest,
                local_dir=local, receipt_dir=receipts,
            )
    assert not local.exists()


def test_execute_reuses_hf_cli_and_preserves_only_real_header_receipt(tmp_path):
    plan, local, receipts = _plan(tmp_path)
    decoder = tmp_path / "upstream-schema-native-header-probe"
    decoder.write_text("synthetic executable presence")
    calls = []

    def fake_download(argv, *, check, timeout):
        calls.append(("download", argv, check, timeout))
        for relative in (plan["manifest_relative_path"],
                         plan["original_offset_index_relative_path"]):
            path = local / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('{"synthetic":"metadata"}')

    def fake_original_native_header_check(**kwargs):
        calls.append(("header", kwargs))
        assert kwargs["manifest_path"].is_file()
        assert kwargs["index_path"].is_file()
        assert kwargs["dataset_revision"] == REV
        assert kwargs["manifest_sha256"] == M_SHA
        # Test seam returns only a genuine-header-shaped packet; the native
        # parser is independently built/executed in the C++ roundtrip shell.
        kwargs["raw_header_output"].write_bytes(b"tiny-original-header")
        return {
            "version": "itir.zelph.remote_original_header_index_manifest_witness.v1",
            "dataset_revision": REV,
            "header_raw_sha256": sha256(b"tiny-original-header").hexdigest(),
            "header_bytes_received": len(b"tiny-original-header"),
            "original_source_http_status": 206,
            "native_original_header_matches_all_four_section_counts": True,
            "edit_authority": False,
        }

    output = execute_metadata_header_probe(
        plan=plan, local_dir=local, receipt_dir=receipts,
        native_header_decoder=decoder,
        run_download=fake_download,
        run_header_check=fake_original_native_header_check,
    )
    assert [x[0] for x in calls] == ["download", "header"]
    assert output["whole_original_bin_downloaded"] is False
    assert output["selected_original_chunk_payloads_compared"] is False
    assert output["metadata_hf_cli_invoked"] is True
    assert (receipts / "original-header.capnp-packed").read_bytes() == b"tiny-original-header"
    assert (receipts / "original-header-proof.json").is_file()


def test_existing_raw_header_refuses_overwrite_before_any_download(tmp_path):
    plan, local, receipts = _plan(tmp_path)
    receipts.mkdir()
    (receipts / "original-header.capnp-packed").write_bytes(b"existing")
    decoder = tmp_path / "probe"
    decoder.touch()
    def forbid(*args, **kwargs):
        raise AssertionError("must not download into old evidence")
    with pytest.raises(ValueError, match="refuse overwrite"):
        execute_metadata_header_probe(
            plan=plan, local_dir=local, receipt_dir=receipts,
            native_header_decoder=decoder,
            run_download=forbid,
        )
    assert (receipts / "original-header.capnp-packed").read_bytes() == b"existing"


def test_missing_native_decoder_refuses_network(tmp_path):
    plan, local, receipts = _plan(tmp_path)
    def forbid(*args, **kwargs):
        raise AssertionError("must have native schema probe")
    with pytest.raises(ValueError, match="decoder required"):
        execute_metadata_header_probe(
            plan=plan, local_dir=local, receipt_dir=receipts,
            native_header_decoder=tmp_path / "missing-probe", run_download=forbid,
        )
    assert not local.exists()


def test_forged_plan_revision_or_download_list_fails_closed(tmp_path):
    plan, local, receipts = _plan(tmp_path)
    decoder = tmp_path / "probe"
    decoder.touch()
    def forbid(*args, **kwargs):
        raise AssertionError("no forged download list should run")
    bad = {**plan, "hf_download_argv": [
        "hf", "download", "acrion/zelph",
        "wikidata-20260309-all.bin", "artifact.index.json",
        "--repo-type", "dataset", "--revision", REV,
        "--local-dir", str(local),
    ]}
    with pytest.raises(ValueError, match="non-approved HF files"):
        execute_metadata_header_probe(
            plan=bad, local_dir=local, receipt_dir=receipts,
            native_header_decoder=decoder, run_download=forbid,
        )


def test_detached_header_json_digest_cannot_be_promoted(tmp_path):
    plan, local, receipts = _plan(tmp_path)
    decoder = tmp_path / "probe"
    decoder.touch()
    def fake_download(argv, *, check, timeout):
        for relative in (plan["manifest_relative_path"],
                         plan["original_offset_index_relative_path"]):
            path = local / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('{"fixture":"metadata"}')
    def forged_header(**kwargs):
        kwargs["raw_header_output"].write_bytes(b"changed-header")
        return {
            "native_original_header_matches_all_four_section_counts": True,
            "original_source_http_status": 206,
            "header_bytes_received": len(b"changed-header"),
            "header_raw_sha256": "a"*64,
            "edit_authority": False,
        }
    with pytest.raises(ValueError, match="not bound to retained raw source bytes"):
        execute_metadata_header_probe(
            plan=plan, local_dir=local, receipt_dir=receipts,
            native_header_decoder=decoder,
            run_download=fake_download, run_header_check=forged_header,
        )
    assert not (receipts / "original-header-proof.json").exists()
