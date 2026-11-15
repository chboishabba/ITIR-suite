"""A2 original adjacency chunk native Bloom: genuine source-equal provenance
and exact no-false-negative key coverage, mock binary only in offline Python.
Original upstream-schema C++ decoder separately checked by native roundtrip.
"""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest

TOOLS=Path(__file__).resolve().parents[1]/"tools"
sys.path.insert(0,str(TOOLS))
from test_audit_zelph_native_original_lr_roots import inputs
from audit_zelph_native_original_lr_roots import native_original_lr_plan
from build_zelph_original_lr_bloom import (
    BYTES,WIRE_BYTES,bit_positions,bloom_possible,build_verified_lr_blooms,
    create_test_wire,validate_wire,
)


def fake_decoder(cmd,**_kwargs):
    section=cmd[cmd.index("--section")+1]
    chunk=int(cmd[cmd.index("--chunk-index")+1])
    assert "--adjacency-bloom" in cmd
    # Test both key identity and repeated same-node source pair.
    keys=( [11,11,7,9,99] if section=="left" and chunk==0 else
           [11,15] if section=="left" else [11,8,8,12] )
    return SimpleNamespace(
        returncode=0,stdout=create_test_wire(
            section=section,chunk_index=chunk,nodes=keys),stderr=b"")


def test_uint64_bloom_fixed_hash_bits_and_no_false_negatives():
    points=[0,1,2,7,8,11,13,2**32,2**64-1]
    raw=create_test_wire(section="left",chunk_index=5,nodes=points)
    assert len(raw)==WIRE_BYTES
    bitmap,count=validate_wire(raw,section="left",chunk_index=5)
    assert count==len(points)
    assert len(bitmap)==BYTES
    assert all(bloom_possible(bitmap,node) for node in points)
    assert all(0<=p<BYTES*8 for node in points for p in bit_positions(node))
    assert not bloom_possible(bitmap,10_000_000_007)
    assert not bloom_possible(bitmap,234_567_891_011)


def test_original_source_equal_native_blooms_resume_and_bound_candidate_scope(tmp_path):
    config,decoder=inputs(tmp_path)
    plan=native_original_lr_plan(**config)
    target=tmp_path/"native-blooms"
    first=build_verified_lr_blooms(
        plan=plan,decoder=decoder,out_root=target,
        max_new_chunks=1,runner=fake_decoder,execute=True)
    assert len(first["newly_bloom_indexed_chunks"])==1
    assert not first["all_original_source_chunk_blooms_complete"]
    second=build_verified_lr_blooms(
        plan=plan,decoder=decoder,out_root=target,
        max_new_chunks=5,runner=fake_decoder,execute=True)
    assert len(second["newly_bloom_indexed_chunks"])==2
    assert second["all_original_source_chunk_blooms_complete"]
    again=build_verified_lr_blooms(
        plan=plan,decoder=decoder,out_root=target,
        max_new_chunks=5,runner=lambda *_a,**_k: (_ for _ in ()).throw(
            AssertionError("do not re-decode original packed source chunk")),
        execute=True)
    assert again["newly_bloom_indexed_chunks"]==[]
    assert len(again["previously_bloom_indexed_chunks"])==3
    for section,index in (("left",0),("left",1),("right",0)):
        payload=(target/f"{section}-{index:06d}.zlbloom").read_bytes()
        bitmap,count=validate_wire(payload,section=section,chunk_index=index)
        assert bloom_possible(bitmap,11)
        proof=json.loads((target/f"{section}-{index:06d}.json").read_text())
        assert proof["original_equal_packed_shard_sha256"]
        assert proof["native_bloom_wire_sha256"]==sha256(payload).hexdigest()
        assert proof["a_bloom_positive_requires_original_native_row_replay"] is True
        assert proof["all_original_chunks_indexed"] is False
        assert proof["edit_authority"] is False


@pytest.mark.parametrize("tamper",[
    "wrong_magic","wrong_section","wrong_chunk","wrong_footer",
    "truncated","extra","wrong_hash_count","wrong_bit_power","missing_rows",
])
def test_corrupt_native_membership_wire_cannot_publish(tmp_path,tamper):
    cfg,decoder=inputs(tmp_path)
    plan=native_original_lr_plan(**cfg)
    def bad(cmd,**kwargs):
        result=fake_decoder(cmd,**kwargs)
        raw=bytearray(result.stdout)
        if tamper=="wrong_magic":raw[0]^=1
        elif tamper=="wrong_section":raw[12]^=1
        elif tamper=="wrong_chunk":raw[8]^=1
        elif tamper=="wrong_footer":raw[-16]^=1
        elif tamper=="wrong_hash_count":raw[13]=1
        elif tamper=="wrong_bit_power":raw[14]=12
        elif tamper=="truncated":raw.pop()
        elif tamper=="extra":raw.extend(b"X")
        elif tamper=="missing_rows":raw[-8:]=bytes(8)
        return SimpleNamespace(returncode=0,stdout=bytes(raw),stderr=b"")
    with pytest.raises(ValueError):
        build_verified_lr_blooms(
            plan=plan,decoder=decoder,out_root=tmp_path/"bad-bloom",
            runner=bad,max_new_chunks=1,execute=True)
    assert not list((tmp_path/"bad-bloom").glob("*.json"))


def test_original_physical_shard_sha_drift_rejected_before_bloom(tmp_path):
    cfg,decoder=inputs(tmp_path)
    plan=native_original_lr_plan(**cfg)
    file=Path(plan["available_native_source_equal_chunks"][0][
        "saved_original_equal_packed_file"])
    file.write_bytes(b"wrong")
    with pytest.raises(ValueError,match="physical evidence drift"):
        build_verified_lr_blooms(
            plan=plan,decoder=decoder,out_root=tmp_path/"bloom",
            runner=fake_decoder,max_new_chunks=1,execute=True)


def test_existing_bloom_wire_tamper_refused_instead_of_silent_resume(tmp_path):
    cfg,decoder=inputs(tmp_path)
    plan=native_original_lr_plan(**cfg)
    root=tmp_path/"bloom"
    build_verified_lr_blooms(
        plan=plan,decoder=decoder,out_root=root,
        runner=fake_decoder,max_new_chunks=1,execute=True)
    wire=next(root.glob("*.zlbloom"))
    raw=bytearray(wire.read_bytes())
    raw[100]^=1
    wire.write_bytes(raw)
    with pytest.raises(ValueError,match="changed source/decoder/bitmap"):
        build_verified_lr_blooms(
            plan=plan,decoder=decoder,out_root=root,
            runner=fake_decoder,max_new_chunks=0,execute=False)


def test_missing_source_equal_section_chunk_is_not_source_negative(tmp_path):
    cfg,decoder=inputs(tmp_path,omit_right=True)
    plan=native_original_lr_plan(**cfg)
    result=build_verified_lr_blooms(
        plan=plan,decoder=decoder,out_root=tmp_path/"partial",
        runner=fake_decoder,max_new_chunks=2,execute=True)
    assert not result["all_original_source_chunk_blooms_complete"]
    assert result["unobserved_original_chunks_are_unknown"]
