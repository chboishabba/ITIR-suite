"""Offline A1 physical-original-source -> exhaustive native name-row bridge tests.

These stub ONLY the executable's emitted JSON shape. The actual same-upstream
Capnp binary's new stream mode is compiled and tested separately by the
native physical roundtrip script (including a repeated name multi-fibre).
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import sys

import pytest

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))
from audit_zelph_native_name_rows import enumerate_authenticated_name_chunk
from verify_zelph_bin_shard_exact import _ARTIFACT, _manifest_index
from test_verify_zelph_hf_original_header import _fixture, REV

_DECODER = r'''#!/usr/bin/env python3
import json, os, sys
mode = os.getenv("FAKE_NATIVE_MODE", "good")
args = sys.argv
section = args[args.index("--section") + 1]
chunk = int(args[args.index("--chunk-index") + 1])
if "--stream-name-rows" not in args:
    sys.exit(4)
if mode == "exit_error":
    sys.exit(2)
rows = [("Q1", 7), ("Q1", 8), ("Q2", 9)]
for i, (name, node) in enumerate(rows):
    r = {"version": "itir.zelph.native_original_name_row.v1",
         "section": section, "chunk_index": chunk, "language": "wikidata",
         "row_index": i, "name": name, "node_id": node}
    if mode == "wrong_index" and i == 1:
        r["row_index"] = 0
    if mode == "wrong_section" and i == 1:
        r["section"] = "right"
    if mode == "forged_authority" and i == 0:
        r["edit_authority"] = True
    line = json.dumps(r)
    if mode == "duplicate_json" and i == 1:
        line = line[:-1] + ', "row_index": 1}'
    print(line, flush=True)
if mode != "missing_footer":
    f = {"version": "itir.zelph.native_original_name_rows_end.v1",
         "section": section, "chunk_index": chunk,
         "language": "wikidata", "rows_emitted": len(rows),
         "candidate_only": True, "authority": False}
    if mode == "wrong_count":
        f["rows_emitted"] += 1
    print(json.dumps(f), flush=True)
if mode == "after_footer":
    print(json.dumps({"version":"unexpected"}), flush=True)
'''


def inputs(tmp_path, section="nodeOfName"):
    manifest, original_index = _fixture()
    manifest_path, index_path = tmp_path / "manifest.json", tmp_path / "index.json"
    manifest_path.write_text(json.dumps(manifest, sort_keys=True))
    index_path.write_text(json.dumps(original_index, sort_keys=True))
    md, idx = sha256(manifest_path.read_bytes()).hexdigest(), sha256(index_path.read_bytes()).hexdigest()
    row = _manifest_index(manifest, _ARTIFACT)[(section, 0)]
    root = tmp_path / "shards"
    shard = root / row["relative"]
    shard.parent.mkdir(parents=True)
    shard.write_bytes(b"abcde")
    digest = sha256(shard.read_bytes()).hexdigest()
    receipt = {
        "version": "itir.zelph.direct_original_selected_chunk_equality.v1",
        "dataset_revision": REV, "section": section, "chunk_index": 0,
        "original_manifest_raw_sha256": md,
        "original_index_raw_sha256": idx,
        "source_bin_size_bytes": manifest["source"]["binSizeBytes"],
        "original_source_offset": row["offset"],
        "source_range_end_inclusive": row["offset"] + row["length"] - 1,
        "bytes_compared": row["length"],
        "published_object_uri": row["object_uri"],
        "original_binary_uri": "hf://datasets/acrion/zelph/wikidata-20260309-all.bin",
        "published_shard_http_status": 200,
        "original_source_http_status": 206,
        "original_packed_range_raw_sha256": digest,
        "published_shard_raw_sha256": digest,
        "exact_original_packed_bytes_equal_published_shard": True,
        "full_index_manifest_offset_cover_checked": True,
        "original_qid_route_verified": False, "whole_name_domain_enumerated": False,
        "all_query_frontiers_closed": False, "native_p854_source_support_paid": False,
        "s29_persistence_paid": False, "edit_authority": False,
    }
    receipt_path = tmp_path / "original-physical-proof.json"
    receipt_path.write_text(json.dumps(receipt))
    decoder = tmp_path / "native-decoder"
    decoder.write_text(_DECODER)
    decoder.chmod(0o700)
    return {
        "manifest_path": manifest_path,
        "original_index_path": index_path,
        "dataset_revision": REV,
        "manifest_sha256": md,
        "original_index_sha256": idx,
        "section": section,
        "chunk_index": 0,
        "receipt_path": receipt_path,
        "shard_root": root,
        "decoder_path": decoder,
        "target_qids": ("Q1", "Q2", "Q999"),
        "rows_output": tmp_path / "complete-native-rows.ndjson",
    }, receipt, shard


@pytest.mark.parametrize("section", ["nodeOfName", "nameOfNode"])
def test_original_equal_native_name_chunk_stream_preserves_full_multi_fibres(
    tmp_path, section
):
    kwargs, _, _ = inputs(tmp_path, section=section)
    result = enumerate_authenticated_name_chunk(**kwargs)
    assert result["native_packed_chunk_rows_enumerated"] == 3
    assert result["target_name_fibres"] == {"Q1": [7, 8], "Q2": [9], "Q999": []}
    assert result["name_duplicates_discarded"] is False
    assert result["complete_native_row_stream_for_this_chunk"] is True
    assert result["all_original_name_chunks_verified"] is False
    assert result["full_name_domain_A1_instantiated"] is False
    assert result["global_name_absence_proved"] is False
    assert result["edit_authority"] is False
    assert result["native_name_rows_stdout_sha256"] == sha256(
        kwargs["rows_output"].read_bytes()
    ).hexdigest()
    assert len(kwargs["rows_output"].read_text().splitlines()) == 4


@pytest.mark.parametrize("mode,error", [
    ("exit_error", "decoder failed"),
    ("wrong_index", "frame identity/order"),
    ("wrong_section", "frame identity/order"),
    ("forged_authority", "frame identity/order"),
    ("duplicate_json", "duplicate native name row"),
    ("missing_footer", "lacks final"),
    ("wrong_count", "count/authority mismatch"),
    ("after_footer", "not terminal"),
])
def test_partial_or_forged_native_frames_cannot_be_promoted(
    tmp_path, monkeypatch, mode, error
):
    kwargs, _, _ = inputs(tmp_path)
    monkeypatch.setenv("FAKE_NATIVE_MODE", mode)
    with pytest.raises(ValueError, match=error):
        enumerate_authenticated_name_chunk(**kwargs)
    assert not kwargs["rows_output"].exists()


@pytest.mark.parametrize("tamper", [
    "published_shard_raw_sha256", "original_index_raw_sha256",
    "exact_original_packed_bytes_equal_published_shard", "chunk_index",
])
def test_tampered_original_range_receipt_blocks_native_decoder(
    tmp_path, tamper
):
    kwargs, receipt, _ = inputs(tmp_path)
    receipt[tamper] = False if isinstance(receipt[tamper], bool) else "0" * 64
    kwargs["receipt_path"].write_text(json.dumps(receipt))
    with pytest.raises(ValueError, match="receipt|digest"):
        enumerate_authenticated_name_chunk(**kwargs)
    assert not kwargs["rows_output"].exists()


def test_original_source_shard_bytes_changed_after_receipt(tmp_path):
    kwargs, _, shard = inputs(tmp_path)
    shard.write_bytes(b"abcdf")
    with pytest.raises(ValueError, match="does not equal original HTTP206"):
        enumerate_authenticated_name_chunk(**kwargs)


def test_missing_full_section_is_not_claimed_from_one_native_chunk(tmp_path):
    kwargs, _, _ = inputs(tmp_path)
    result = enumerate_authenticated_name_chunk(**kwargs)
    assert result["all_original_name_chunks_verified"] is False
    assert result["full_name_domain_A1_instantiated"] is False
    assert result["global_name_absence_proved"] is False


def test_preexisting_native_rows_output_rejected(tmp_path):
    kwargs, _, _ = inputs(tmp_path)
    kwargs["rows_output"].write_text("old evidence")
    with pytest.raises(ValueError, match="refuse overwrite"):
        enumerate_authenticated_name_chunk(**kwargs)


def test_wrong_source_revision_fails_before_native_execution(tmp_path):
    kwargs, _, _ = inputs(tmp_path)
    kwargs["dataset_revision"] = "0" * 40
    with pytest.raises(ValueError, match="receipt|revision"):
        enumerate_authenticated_name_chunk(**kwargs)


def test_oversized_row_limit_rejected_before_native_execution(tmp_path):
    kwargs, _, _ = inputs(tmp_path)
    kwargs["max_name_rows"] = 100000001
    with pytest.raises(ValueError, match="bounded native"):
        enumerate_authenticated_name_chunk(**kwargs)


def test_previously_verified_original_range_can_hydrate_only_published_hf_object(
    tmp_path
):
    import io
    kwargs, receipt, shard = inputs(tmp_path)
    shard.unlink()
    seen = []
    class Response(io.BytesIO):
        status = 200
        headers = {"Content-Length": "5", "Content-Encoding": "identity"}
        def geturl(self):
            return "https://huggingface.co/pinned-immutable-standalone-shard"
    def opener(request, timeout):
        seen.append((request.full_url, request.get_header("Range")))
        assert request.get_header("Range") == "bytes=0-4"
        assert "wikidata-20260309-all.bin" not in request.full_url
        return Response(b"abcde")
    result = enumerate_authenticated_name_chunk(
        **kwargs, hydrate_missing_shard=True, opener=opener,
    )
    assert shard.read_bytes() == b"abcde"
    assert len(seen) == 1
    assert result["packed_shard_hydrated_from_pinned_hf_whole_object"] is True
    assert result["original_bin_requeried_for_hydration"] is False
    assert result["complete_native_row_stream_for_this_chunk"] is True


def test_hydration_tampering_never_publishes_forged_local_packed_file(tmp_path):
    import io
    kwargs, receipt, shard = inputs(tmp_path)
    shard.unlink()
    class Response(io.BytesIO):
        status = 200
        headers = {"Content-Length": "5"}
        def geturl(self):
            return "https://huggingface.co/pinned-immutable-standalone-shard"
    def opener(request, timeout):
        return Response(b"abcdf")
    with pytest.raises(ValueError, match="differs from original HTTP206 receipt"):
        enumerate_authenticated_name_chunk(
            **kwargs, hydrate_missing_shard=True, opener=opener,
        )
    assert not shard.exists()
    assert not kwargs["rows_output"].exists()


def test_existing_local_shard_never_triggers_extra_network_even_with_hydrate(tmp_path):
    kwargs, receipt, shard = inputs(tmp_path)
    def forbidden(*args, **kwargs):
        raise AssertionError("existing digest-matched original source file needs no fetch")
    out = enumerate_authenticated_name_chunk(
        **kwargs, hydrate_missing_shard=True, opener=forbidden,
    )
    assert out["packed_shard_hydrated_from_pinned_hf_whole_object"] is False


def test_hydrate_network_budget_checked_before_request(tmp_path):
    kwargs, receipt, shard = inputs(tmp_path)
    shard.unlink()
    kwargs["max_hydrate_mib"] = 0
    def forbidden(*args, **kwargs):
        raise AssertionError("invalid hydration budget must fail before HTTP")
    with pytest.raises(ValueError, match="bounded explicit"):
        enumerate_authenticated_name_chunk(
            **kwargs, hydrate_missing_shard=True, opener=forbidden,
        )
    assert not shard.exists()
