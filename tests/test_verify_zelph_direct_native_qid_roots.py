"""Source-equal native QID lookup join, preserving scoped-only authority."""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from types import SimpleNamespace
import sys

import pytest

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))
from verify_zelph_bin_shard_exact import _ARTIFACT, _manifest_index, _read_json
from verify_zelph_hf_selected_direct_matrix import plan_matrix, execute_matrix
from verify_zelph_direct_native_qid_roots import (
    parse_qid_selections, verify_native_qid_roots,
)
from test_verify_zelph_hf_selected_direct_matrix import pinned


def fixture(tmp_path):
    source = pinned(tmp_path)
    chosen = [("nodeOfName", 0)]
    plan = plan_matrix(**source, keys=chosen)
    item = _manifest_index(_read_json(source["manifest_path"], 1024**2), _ARTIFACT)[chosen[0]]
    data = b"n" * item["length"]
    digest = sha256(data).hexdigest()
    root = tmp_path / "shards"
    shard = root / item["relative"]
    shard.parent.mkdir(parents=True)
    shard.write_bytes(data)
    decoder = tmp_path / "selected-native"
    decoder.write_bytes(b"fixture-only-executable-id")

    def synthetic_http_witness(**kwargs):
        return {
            "version": "itir.zelph.direct_original_selected_chunk_equality.v1",
            "dataset_revision": source["dataset_revision"],
            "original_manifest_raw_sha256": source["manifest_sha256"],
            "original_index_raw_sha256": source["original_index_sha256"],
            "section": "nodeOfName", "chunk_index": 0,
            "original_source_offset": item["offset"],
            "source_range_end_inclusive": item["offset"] + item["length"] - 1,
            "bytes_compared": item["length"],
            "published_object_uri": item["object_uri"],
            "original_source_http_status": 206,
            "exact_original_packed_bytes_equal_published_shard": True,
            "full_index_manifest_offset_cover_checked": True,
            "published_shard_raw_sha256": digest,
            "original_packed_range_raw_sha256": digest,
            "original_bin_full_digest_verified": False,
            "original_qid_route_verified": False,
            "all_query_frontiers_closed": False,
            "native_p854_source_support_paid": False,
            "s29_persistence_paid": False,
            "edit_authority": False,
        }

    matrix_dir = tmp_path / "matrix"
    execute_matrix(plan=plan, evidence_dir=matrix_dir,
                   manifest_path=source["manifest_path"],
                   original_index_path=source["original_index_path"],
                   verify_one=synthetic_http_witness)
    return source, root, matrix_dir, shard, decoder


def native_runner(qid="Q42", node_id=123):
    def run(cmd, **kwargs):
        assert "--section" in cmd and "nodeOfName" in cmd
        assert "--chunk-index" in cmd and "--qid" in cmd
        wire = json.dumps({
            "version": "itir.zelph.selected_native_capnp_decode.v1",
            "section": "nodeOfName", "chunk_index": 0,
            "candidate_only": True, "authority": False,
            "rows": [{"name": qid, "node_id": node_id}],
        }).encode()
        return SimpleNamespace(returncode=0, stdout=wire, stderr=b"")
    return run


@pytest.mark.parametrize("invalid", [
    [], ["Q0:0"], ["Q42:-1"], ["Q42:foo"],
    ["Q42:0", "Q42:1"], ["Q42:4294967296"], [True],
])
def test_invalid_or_duplicate_native_qid_hint_refused(invalid):
    with pytest.raises(ValueError):
        parse_qid_selections(invalid)


def test_matching_real_physical_matrix_bytes_make_positive_native_name_witness(tmp_path):
    source, root, matrix, shard, decoder = fixture(tmp_path)
    result = verify_native_qid_roots(
        manifest_path=source["manifest_path"],
        manifest_sha256=source["manifest_sha256"],
        matrix_dir=matrix, shard_root=root, decoder=decoder,
        qid_chunks={"Q42": 0}, runner=native_runner())
    assert result["all_declared_qid_name_witnesses_positive"]
    assert result["native_exact_positive_name_to_node_rows"][0]["node_id"] == 123
    assert result["original_name_chunk_bytes_equal_source_bin_ranges"] is True
    for not_paid in (
        "selected_root_adjacency_verified", "left_right_finite_query_family_closed",
        "all_original_names_enumerated", "s29_review_persistence_paid",
        "source_support_paid", "edit_authority"):
        assert result[not_paid] is False


def test_unselected_name_chunk_cannot_be_promoted_into_a_root(tmp_path):
    source, root, matrix, shard, decoder = fixture(tmp_path)
    with pytest.raises(ValueError, match="lacks exact direct HTTP206"):
        verify_native_qid_roots(
            manifest_path=source["manifest_path"],
            manifest_sha256=source["manifest_sha256"],
            matrix_dir=matrix, shard_root=root, decoder=decoder,
            qid_chunks={"Q42": 1}, runner=native_runner())


def test_native_decoder_missing_or_ambiguous_qid_row_fails(tmp_path):
    source, root, matrix, shard, decoder = fixture(tmp_path)
    with pytest.raises(ValueError, match="missing/ambiguous"):
        verify_native_qid_roots(
            manifest_path=source["manifest_path"],
            manifest_sha256=source["manifest_sha256"],
            matrix_dir=matrix, shard_root=root, decoder=decoder,
            qid_chunks={"Q42": 0}, runner=native_runner(qid="Q43"))
    with pytest.raises(ValueError, match="missing/ambiguous"):
        verify_native_qid_roots(
            manifest_path=source["manifest_path"],
            manifest_sha256=source["manifest_sha256"],
            matrix_dir=matrix, shard_root=root, decoder=decoder,
            qid_chunks={"Q42": 0}, runner=native_runner(node_id=True))


def test_physical_shard_byte_tamper_and_receipt_drift_refused(tmp_path):
    source, root, matrix, shard, decoder = fixture(tmp_path)
    shard.write_bytes(b"z" * shard.stat().st_size)
    with pytest.raises(ValueError, match="differs"):
        verify_native_qid_roots(
            manifest_path=source["manifest_path"],
            manifest_sha256=source["manifest_sha256"],
            matrix_dir=matrix, shard_root=root, decoder=decoder,
            qid_chunks={"Q42": 0}, runner=native_runner())
    receipt = matrix / "nodeOfName-000000.json"
    receipt.write_text(receipt.read_text() + " ")
    with pytest.raises(ValueError, match="SHA drift"):
        verify_native_qid_roots(
            manifest_path=source["manifest_path"],
            manifest_sha256=source["manifest_sha256"],
            matrix_dir=matrix, shard_root=root, decoder=decoder,
            qid_chunks={"Q42": 0}, runner=native_runner())
