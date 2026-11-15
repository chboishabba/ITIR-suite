"""A2-B immutable original source Bloom candidate routing, not guessed chunk math.

Mocks only the native C++ fixed binary output, independently native-fixture
tested in the same exact-head source acceptance checker.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import sys

import pytest

TOOLS=Path(__file__).resolve().parents[1]/"tools"
sys.path.insert(0,str(TOOLS))
from test_audit_zelph_native_original_lr_roots import inputs
from test_build_zelph_original_lr_bloom import fake_decoder
from audit_zelph_native_original_lr_roots import native_original_lr_plan
from build_zelph_original_lr_bloom import build_verified_lr_blooms
from query_zelph_original_lr_blooms import query_original_lr_blooms


def setup(tmp_path, *, missing_right=False):
    args, decoder=inputs(tmp_path,omit_right=missing_right)
    root=tmp_path/"native-blooms"
    plan=native_original_lr_plan(**args)
    build_verified_lr_blooms(
        plan=plan,decoder=decoder,out_root=root,
        max_new_chunks=8,runner=fake_decoder,execute=True)
    opts=dict(
        manifest=args["manifest"],
        original_index=args["original_index"],
        revision=args["revision"],
        manifest_sha256=args["manifest_sha256"],
        original_index_sha256=args["original_index_sha256"],
        decoder_sha256=sha256(decoder.read_bytes()).hexdigest(),
        positive_roots_receipt=args["positive_roots_receipt"],
        physical_receipts_dirs=args["physical_receipts_dirs"],
        bloom_root=root,
        numeric_nodes=[7,111111],
    )
    return opts,args,decoder


def test_only_possible_hits_are_reported_and_complete_original_sections_certify_absence(tmp_path):
    opts,args,decoder=setup(tmp_path)
    result=query_original_lr_blooms(**opts)
    assert result["all_original_adjacency_blooms_completed"] is True
    assert result["original_node_ids_not_ordered_by_chunk_index"] is True
    assert result["bloom_candidates_are_exact_native_routes"] is False
    assert result["twenty_relation_words_closed"] is False
    left=result["sections"]["left"]
    right=result["sections"]["right"]
    assert left["native_original_bloom_verified_chunk_count"]==2
    assert right["native_original_bloom_verified_chunk_count"]==1
    by_node={r["node_id"]:r for r in left["nodes"]}
    assert by_node[11]["possible_native_source_chunk_indices"]==[0,1]
    assert by_node[7]["possible_native_source_chunk_indices"]==[0]
    assert by_node[111111]["exact_no_adjacency_row_proved"] is True
    assert by_node[111111]["candidate_original_adjacency_rows_still_require_native_replay"] is False
    assert result["source_support_paid"] is False
    assert result["edit_authority"] is False


def test_sparse_original_section_missing_filter_is_UNKNOWN_not_global_negative(tmp_path):
    opts,args,decoder=setup(tmp_path,missing_right=True)
    result=query_original_lr_blooms(**opts)
    assert not result["all_original_adjacency_blooms_completed"]
    r=result["sections"]["right"]
    assert r["native_original_bloom_verified_chunk_count"]==0
    assert r["missing_bloom_chunk_indices"]==[0]
    assert all(not row["exact_no_adjacency_row_proved"] for row in r["nodes"])
    assert all(row["missing_original_chunks_are_unknown"] for row in r["nodes"])


def test_retained_native_bloom_does_not_require_raw_adjacency_shards_after_source_copy(tmp_path):
    opts,args,decoder=setup(tmp_path)
    for shard in args["shard_root"].rglob("*.capnp-packed"):
        shard.unlink()
    # Every Bloom remains authenticated by exact original source range
    # physical receipt; no need for 87.95GB bin or cached packed payload.
    result=query_original_lr_blooms(**opts)
    assert result["all_original_adjacency_blooms_completed"]


def test_forged_original_http206_receipt_sha_blocks_bloom_route(tmp_path):
    opts,args,_=setup(tmp_path)
    root=args["physical_receipts_dirs"][0]
    p=root/"left-000000.json"
    proof=json.loads(p.read_text())
    proof["published_shard_raw_sha256"]="f"*64
    proof["original_packed_range_raw_sha256"]="f"*64
    p.write_text(json.dumps(proof))
    with pytest.raises(ValueError,match="disagrees with source HTTP206"):
        query_original_lr_blooms(**opts)


def test_wrong_or_forged_native_decoder_identity_refused(tmp_path):
    opts,args,_=setup(tmp_path)
    with pytest.raises(ValueError,match="Bloom source/direction"):
        query_original_lr_blooms(**{**opts,"decoder_sha256":"f"*64})


def test_tampered_bloom_wire_and_missing_receipt_fail_closed(tmp_path):
    opts,args,_=setup(tmp_path)
    bitmap=opts["bloom_root"]/"left-000000.zlbloom"
    data=bytearray(bitmap.read_bytes())
    data[100]^=1
    bitmap.write_bytes(data)
    with pytest.raises(ValueError,match="digest"):
        query_original_lr_blooms(**opts)
    bitmap.unlink()
    with pytest.raises(ValueError,match="partially published"):
        query_original_lr_blooms(**opts)


def test_incomplete_source_cannot_mint_global_absence_with_all_zeros(tmp_path):
    opts,args,_=setup(tmp_path,missing_right=True)
    result=query_original_lr_blooms(**{**opts,"numeric_nodes":[0]})
    assert result["sections"]["right"]["nodes"][0]["exact_no_adjacency_row_proved"] is False
    assert result["sections"]["right"]["nodes"][0]["possible_native_source_chunk_indices"]==[]
    assert result["sections"]["right"]["nodes"][0]["missing_original_chunks_are_unknown"] is True
