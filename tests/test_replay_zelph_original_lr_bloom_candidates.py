"""Original A2-B: full source key coverage + only native-positive candidate replay.

Synthetic physical HTTP206 receipts are fixtures. Real C++ source-key Bloom
and selected-AdjPair decoding are separately accepted by native Capnp suite.
"""
from __future__ import annotations

from hashlib import sha256
import io
import json
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest

TOOLS=Path(__file__).resolve().parents[1]/"tools"
sys.path.insert(0,str(TOOLS))
from test_audit_zelph_native_original_lr_roots import inputs
from test_build_zelph_original_lr_bloom import fake_decoder
from audit_zelph_native_original_lr_roots import native_original_lr_plan
from build_zelph_original_lr_bloom import build_verified_lr_blooms
from query_zelph_original_lr_blooms import query_original_lr_blooms
import replay_zelph_original_lr_bloom_candidates as replay
from close_original_http206_lr_finite_words import original_http206_finite_words


def source(tmp_path):
    args,decoder=inputs(tmp_path)
    plan=native_original_lr_plan(**args)
    blooms=tmp_path/"native-blooms"
    build_verified_lr_blooms(plan=plan,decoder=decoder,out_root=blooms,
                             max_new_chunks=5,runner=fake_decoder,execute=True)
    route=query_original_lr_blooms(
        manifest=args["manifest"],original_index=args["original_index"],
        revision=args["revision"],
        manifest_sha256=args["manifest_sha256"],
        original_index_sha256=args["original_index_sha256"],
        decoder_sha256=sha256(decoder.read_bytes()).hexdigest(),
        positive_roots_receipt=args["positive_roots_receipt"],
        physical_receipts_dirs=args["physical_receipts_dirs"],
        bloom_root=blooms)
    return args,decoder,route,blooms


def source_native(cmd,**_kwargs):
    section=cmd[cmd.index("--section")+1]
    number=int(cmd[cmd.index("--chunk-index")+1])
    nodes=[int(cmd[i+1]) for i,v in enumerate(cmd[:-1]) if v=="--node"]
    source_rows={
        ("left",0):{11:[7,8],7:[100],9:[99],99:[]},
        ("left",1):{11:[9],15:[]},
        ("right",0):{11:[17],8:[50],12:[]},
    }
    observed=[]
    for node in nodes:
        if node in source_rows[(section,number)]:
            edges=source_rows[(section,number)][node]
            observed.append({"node_id":node,"neighbors":edges,
                             "values_seen":len(edges),"truncated":False})
    return SimpleNamespace(returncode=0,stdout=json.dumps({
        "version":"itir.zelph.selected_native_capnp_decode.v1",
        "section":section,"chunk_index":number,
        "rows":observed,"candidate_only":True,"authority":False}).encode(),
        stderr=b"")


def run(args,decoder,route,**kwargs):
    return replay.replay_exact_original_bloom_candidates(
        route=route,manifest=args["manifest"],original_index=args["original_index"],
        decoder=decoder,shard_root=args["shard_root"],
        physical_receipts_dirs=args["physical_receipts_dirs"],
        positive_roots_receipt=args["positive_roots_receipt"],
        runner=source_native,**kwargs)


def test_full_source_bloom_keys_plus_exact_candidate_replay_close_selected_one_hop(tmp_path):
    args,decoder,route,blooms=source(tmp_path)
    plan=replay.plan_exact_original_bloom_replay(
        route=route,manifest=args["manifest"],original_index=args["original_index"],
        shard_root=args["shard_root"])
    assert plan["full_source_bloom_coverage"]
    assert plan["native_candidate_chunk_count"]==3
    assert plan["one_sided_hf_hydration_bytes"]==0
    result=run(args,decoder,route)
    assert result["all_selected_root_one_hop_adjacencies_complete"]
    assert result["all_bloom_candidate_chunks_exact_native_replayed"]
    assert result["every_original_chunk_adjacency_key_natively_scanned"]
    assert result["native_decoded_source_equal_chunks_by_section"]=={"left":2,"right":1}
    assert len(result["bloom_candidate_exact_native_replays"])==3
    by_dir={r["direction"]:r for r in
            result["native_original_selected_node_direction_rows"]}
    assert by_dir["left"]["native_original_neighbors_sorted_unique"]==[7,8,9]
    assert by_dir["right"]["native_original_neighbors_sorted_unique"]==[17]
    assert by_dir["left"]["candidate_chunk_indices_tested"]==[0,1]
    assert by_dir["right"]["candidate_chunk_indices_tested"]==[0]
    assert not result["all_twenty_finite_relation_words_closed"]
    assert not result["native_wikibase_p854_support_verified"]


def test_original_finite_words_accept_full_source_bloom_candidate_replay(tmp_path):
    args,decoder,route,blooms=source(tmp_path)
    result=run(args,decoder,route)
    queries={"version":"itir.zelph.finite_lr_query_family.v1",
             "qid_root_nodes":{"Q42":11},
             "queries":[
                 {"id":"left","qid":"Q42","word":["left"]},
                 {"id":"right","qid":"Q42","word":["right"]},
                 {"id":"left-right","qid":"Q42","word":["left","right"]},
             ]}
    first=original_http206_finite_words(
        query_family=queries,audits=[(result,sha256(b"root").hexdigest())])
    assert not first["all_declared_original_lr_words_closed"]
    assert first["next_numeric_nodes_to_native_scan"]==[7,8,9]
    # The finite-word evaluator must not claim unknown direction records
    # were checked just because their root QID has a native name witness.
    assert first["source_equal_native_full_section_sweep_receipts"][0][
        "scan_method"]=="complete-original-bloom-candidates"


def test_unmaterialized_original_candidate_can_be_hydrated_only_from_pinned_same_sha(
    tmp_path,monkeypatch
):
    args,decoder,route,blooms=source(tmp_path)
    original=next(args["shard_root"].rglob("chunk-000000.capnp-packed"))
    raw=original.read_bytes()
    original.unlink()
    with pytest.raises(ValueError,match="explicit --hydrate"):
        run(args,decoder,route)
    def published(**kwargs):
        # Match this exact published original standalone object only.
        section="left" if "/left/" in kwargs["hf_uri"] else "right"
        chunk=int(kwargs["hf_uri"].split("chunk-")[1][:6])
        payload=(section[0]+str(chunk)).encode()
        return io.BytesIO(
            (payload*(kwargs["expected_size"]//len(payload)+1))[
                :kwargs["expected_size"]])
    monkeypatch.setattr(replay,"open_pinned_zelph_complete_object",published)
    done=run(args,decoder,route,hydrate=True)
    assert done["all_selected_root_one_hop_adjacencies_complete"]
    assert original.is_file()
    assert len(done["one_sided_hydrated_original_equal_candidate_shards"])==1


def test_bloom_complete_required_even_if_any_first_root_has_positive_hit(tmp_path):
    args,decoder,route,blooms=source(tmp_path)
    modified=json.loads(json.dumps(route))
    modified["all_original_adjacency_blooms_completed"]=False
    modified["sections"]["right"]["complete_original_bloom_section_cover"]=False
    plan=replay.plan_exact_original_bloom_replay(
        route=modified,manifest=args["manifest"],
        original_index=args["original_index"],shard_root=args["shard_root"])
    assert not plan["full_source_bloom_coverage"]
    with pytest.raises(ValueError,match="unverified source Bloom"):
        run(args,decoder,modified)


def test_truncated_native_exact_adjacency_cannot_become_source_complete(tmp_path):
    args,decoder,route,blooms=source(tmp_path)
    def truncated(cmd,**kwargs):
        native=source_native(cmd,**kwargs)
        value=json.loads(native.stdout)
        if value["rows"]:
            value["rows"][0]["truncated"]=True
        native.stdout=json.dumps(value).encode()
        return native
    with pytest.raises(ValueError,match="ambiguous or truncated"):
        replay.replay_exact_original_bloom_candidates(
            route=route,manifest=args["manifest"],
            original_index=args["original_index"],
            decoder=decoder,shard_root=args["shard_root"],
            physical_receipts_dirs=args["physical_receipts_dirs"],
            positive_roots_receipt=args["positive_roots_receipt"],
            runner=truncated)


def test_finite_word_checker_rejects_forged_bloom_missing_one_candidate_replay(tmp_path):
    args,decoder,route,blooms=source(tmp_path)
    audit=run(args,decoder,route)
    forged=json.loads(json.dumps(audit))
    forged["bloom_candidate_exact_native_replays"].pop()
    queries={"version":"itir.zelph.finite_lr_query_family.v1",
             "qid_root_nodes":{"Q42":11},
             "queries":[{"id":"root-left","qid":"Q42","word":["left"]}]}
    with pytest.raises(ValueError,match="candidate set not exactly replayed"):
        original_http206_finite_words(
            query_family=queries,audits=[(forged,sha256(b"forged").hexdigest())])
