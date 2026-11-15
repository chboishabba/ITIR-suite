#!/usr/bin/env python3
"""A2-B: full ORIGINAL source Bloom cover -> exact selected native adjacency.

When *all* 984+984 original adjacency chunks have physically witnessed bytes
and full native membership Bloom receipts, only Bloom-positive candidate
chunks need actual selected native adjacency replay. Bloom false positives
merely cost an extra decode; they may NEVER create an edge. To avoid retaining
the complete 87.95GB original source bin, the required packed candidate shard
can be materialized as a single pinned immutable HF object, rehashed to its
already accepted original HTTP206 equality SHA (NO new original-bin request).

All requested numeric roots are bounded and present in the same pinned
positive-QID receipt. Missing filters/candidate replay => UNKNOWN, not
negative. This is exactly the proof boundary needed by finite-word closure.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import resource
import sqlite3
import subprocess
import sys
import tempfile
from typing import Any,Callable

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"itir-mcp"/"src"))
from itir_mcp.shard_transport import open_pinned_zelph_complete_object
from audit_zelph_hf_name_section_bytes import _read_receipt,_check_receipt
from audit_zelph_native_name_fibres import _strict,_file_sha
from query_zelph_original_lr_blooms import query_original_lr_blooms
from verify_zelph_bin_shard_exact import _ARTIFACT,_manifest_index,_read_json
from verify_zelph_index_manifest_original import verify_index_manifest_files

_NATIVE="itir.zelph.selected_native_capnp_decode.v1"
_VERSION="itir.zelph.original_lr_bloom_pruned_exact_native_onehop.v1"
_MIB=1024*1024


def _immutable_original_equal_shard(*, item:dict, physical_sha:str,
                                    revision:str, shard_root:Path,
                                    hydrate:bool, opener:Callable[...,Any]|None) -> tuple[Path,bool]:
    root=shard_root.resolve(strict=True)
    if not root.is_dir() or shard_root.is_symlink():
        raise ValueError("real source-equal native shard cache root required")
    file=(root/item["relative"]).resolve(strict=False)
    if not file.is_relative_to(root) or file.is_symlink():
        raise ValueError("original candidate native packed path escapes trusted root")
    if file.exists():
        if (not file.is_file() or file.stat().st_size!=item["length"]
                or _file_sha(file)!=physical_sha):
            raise ValueError("retained candidate packed bytes do not match original source")
        return file,False
    if not hydrate:
        raise ValueError("missing candidate original packed bytes: rerun with explicit bounded hydration")
    file.parent.mkdir(parents=True,exist_ok=True)
    if file.parent.is_symlink():
        raise ValueError("native candidate shard directory symlink refused")
    scratch=None
    try:
        with tempfile.NamedTemporaryFile(mode="wb",dir=file.parent,
                                         prefix=".candidate-original-equal-",
                                         delete=False) as out:
            scratch=Path(out.name)
            params=dict(
                hf_uri=item["object_uri"],revision=revision,
                expected_size=item["length"],max_bytes=item["length"])
            if opener is not None:
                params["opener"]=opener
            with open_pinned_zelph_complete_object(**params) as source:
                digest=sha256()
                n=0
                while n<item["length"]:
                    part=source.read(min(_MIB,item["length"]-n))
                    if not part:
                        raise ValueError("original candidate standalone source truncated")
                    out.write(part)
                    digest.update(part)
                    n+=len(part)
                if source.read(1) or digest.hexdigest()!=physical_sha:
                    raise ValueError("original candidate standalone shard differs from prior HTTP206 range")
            out.flush()
            os.fsync(out.fileno())
        os.link(scratch,file,follow_symlinks=False)
        return file,True
    finally:
        if scratch is not None:
            scratch.unlink(missing_ok=True)


def _native_decode_candidate(*, decoder:Path,file:Path,section:str,chunk:int,
                             nodes:list[int],max_neighbors:int,
                             max_stdout_mib:int,timeout_seconds:int,
                             runner:Callable[...,Any]|None) -> tuple[dict[int,dict],str]:
    cmd=[str(decoder),"--file",str(file),"--section",section,
         "--chunk-index",str(chunk),"--max-neighbors",str(max_neighbors)]
    for node in nodes:
        cmd+=["--node",str(node)]
    if runner is None:
        size=max_stdout_mib*_MIB
        def limit():
            resource.setrlimit(resource.RLIMIT_FSIZE,(size,size))
        with tempfile.TemporaryFile(mode="w+b") as stdout:
            outcome=subprocess.run(cmd,stdout=stdout,stderr=subprocess.PIPE,
                                   timeout=timeout_seconds,check=False,preexec_fn=limit)
            if outcome.returncode!=0:
                raise ValueError("original native candidate decoder failed/truncated/oversized")
            stdout.seek(0)
            wire=stdout.read(size+1)
    else:
        outcome=runner(cmd,capture_output=True,timeout=timeout_seconds,check=False)
        wire=outcome.stdout
    if (outcome.returncode!=0 or type(wire) is not bytes
            or len(wire)>max_stdout_mib*_MIB):
        raise ValueError("bounded original selected native candidate replay failed")
    doc=_strict(wire)
    if (doc.get("version")!=_NATIVE or doc.get("section")!=section
            or type(doc.get("chunk_index")) is not int or doc["chunk_index"]!=chunk
            or doc.get("candidate_only") is not True
            or doc.get("authority") is not False):
        raise ValueError("native candidate original source schema/authority mismatch")
    records=doc.get("rows")
    if type(records) is not list or len(records)>len(nodes):
        raise ValueError("native candidate output exceeded requested root domain")
    found={}
    for row in records:
        if type(row) is not dict or set(row)!={
            "node_id","neighbors","values_seen","truncated"}:
            raise ValueError("original selected native candidate record shape invalid")
        node,edges,count=row["node_id"],row["neighbors"],row["values_seen"]
        if (type(node) is not int or node not in nodes or node in found
                or not isinstance(edges,list) or len(edges)>max_neighbors
                or edges!=sorted(set(edges))
                or any(type(edge) is not int or not 0<=edge<=2**64-1 for edge in edges)
                or type(count) is not int or count<len(edges)
                or row.get("truncated") is not False):
            raise ValueError("ambiguous or truncated native original candidate adjacency")
        found[node]={"neighbors":edges,"values_seen":count}
    return found,sha256(wire).hexdigest()


def plan_exact_original_bloom_replay(*, route:dict,
                                     manifest:Path,original_index:Path,
                                     max_hydrate_mib:int=512,
                                     shard_root:Path) -> dict:
    if (route.get("version")!="itir.zelph.original_lr_bloom_candidate_route.v1"
            or type(max_hydrate_mib) is not int
            or not 0<=max_hydrate_mib<=65536):
        raise ValueError("pinned full original Bloom route and hydrate budget required")
    indexed=_manifest_index(_read_json(manifest,16*_MIB),_ARTIFACT)
    chunks={}
    nodes=route["queried_numeric_nodes"]
    if type(nodes) is not list or len(nodes)>256:
        raise ValueError("bounded native source frontier required")
    complete=route["all_original_adjacency_blooms_completed"] is True
    if complete:
        for section in ("left","right"):
            sec=route["sections"][section]
            if not sec["complete_original_bloom_section_cover"]:
                raise ValueError("original Bloom section missing native-key coverage")
            for row in sec["nodes"]:
                node=row["node_id"]
                for chunk in row["possible_native_source_chunk_indices"]:
                    if (section,chunk) not in indexed:
                        raise ValueError("candidate chunk outside original source manifest")
                    chunks.setdefault((section,chunk),set()).add(node)
    target=shard_root.resolve(strict=False)
    hydrating=[]
    planned=[]
    for (section,n),nodeset in sorted(chunks.items()):
        item=indexed[(section,n)]
        path=(target/item["relative"]).resolve(strict=False)
        if not path.is_relative_to(target) or path.is_symlink():
            raise ValueError("untrusted original candidate packed shard path")
        if not path.exists():
            hydrating.append({"section":section,"chunk_index":n,"bytes":item["length"]})
        planned.append({"section":section,"chunk_index":n,
                        "node_ids":sorted(nodeset),"packed_size_bytes":item["length"]})
    to_hydrate=sum(item["bytes"] for item in hydrating)
    if to_hydrate>max_hydrate_mib*_MIB:
        raise ValueError("original candidate one-sided HF hydration budget exceeded")
    return {
        "version":"itir.zelph.original_lr_bloom_candidate_replay_plan.v1",
        "dataset_revision":route["dataset_revision"],
        "source_name_qid_roots":route["qid_positive_original_nodes"],
        "full_source_bloom_coverage":complete,
        "candidate_packed_chunks":planned,
        "native_candidate_chunk_count":len(planned),
        "missing_saved_original_equal_candidate_chunks":hydrating,
        "one_sided_hf_hydration_bytes":to_hydrate,
        "original_binary_requery_required":False,
        "all_selected_node_directions_complete_before_native_replay":False,
        "edit_authority":False,
    }


def replay_exact_original_bloom_candidates(*,route:dict,manifest:Path,
    original_index:Path,decoder:Path,shard_root:Path,bloom_root:Path,
    physical_receipts_dirs:list[Path],positive_roots_receipt:Path,
    max_hydrate_mib:int=512,max_neighbors:int=200000,
    max_stdout_mib:int=64,timeout_seconds:int=900,
    hydrate:bool=False,runner:Callable[...,Any]|None=None,
    opener:Callable[...,Any]|None=None) ->dict:
    if (not decoder.is_file() or decoder.is_symlink()
            or _file_sha(decoder)!=route.get("native_decoder_sha256")
            or type(max_neighbors) is not int or not 0<max_neighbors<=1000000
            or type(max_stdout_mib) is not int or not 0<max_stdout_mib<=1024
            or type(timeout_seconds) is not int or not 0<timeout_seconds<=7200):
        raise ValueError("exact pinned native Capnp decoder/selected-root limits required")
    # A source-route dict alone is NOT a proof. Re-read every current
    # original-equal membership filter and original HTTP206 receipt before
    # allowing any claimed missing candidate to become an exact negative.
    # The CLI also validates at preflight, but the callable API must never
    # trust an externally constructed or mutated route object.
    genuine_roots=_strict(positive_roots_receipt.read_bytes())
    genuine_qids=genuine_roots.get("native_exact_positive_name_to_node_rows")
    if type(genuine_qids) is not list:
        raise ValueError("original positive QID roots absent from exact source receipt")
    known={r.get("node_id") for r in genuine_qids if type(r) is dict}
    if any(type(n) is not int for n in known):
        raise ValueError("invalid genuine source-positive QID node")
    targets=route.get("queried_numeric_nodes")
    if not isinstance(targets,list):
        raise ValueError("original source Bloom query target set missing")
    extras=sorted(set(targets)-known)
    fresh=query_original_lr_blooms(
        manifest=manifest,original_index=original_index,
        revision=route["dataset_revision"],
        manifest_sha256=route["manifest_sha256"],
        original_index_sha256=route["original_index_sha256"],
        positive_roots_receipt=positive_roots_receipt,
        decoder_sha256=_file_sha(decoder),
        physical_receipts_dirs=physical_receipts_dirs,
        bloom_root=bloom_root,numeric_nodes=extras)
    if route!=fresh:
        raise ValueError("claimed original complete Bloom candidate route disagrees with current physical/source evidence")
    plan=plan_exact_original_bloom_replay(
        route=fresh,manifest=manifest,original_index=original_index,
        shard_root=shard_root,max_hydrate_mib=max_hydrate_mib)
    if not plan["full_source_bloom_coverage"]:
        raise ValueError("unverified source Bloom sections: absent adjacency must remain UNKNOWN")
    if plan["one_sided_hf_hydration_bytes"] and not hydrate:
        raise ValueError("original candidate native shard(s) missing: explicit --hydrate required")
    root=shard_root.resolve(strict=True)
    idx=_manifest_index(_read_json(manifest,16*_MIB),_ARTIFACT)
    cross=verify_index_manifest_files(
        manifest_path=manifest,index_path=original_index,
        manifest_sha256=route["manifest_sha256"],
        index_sha256=route["original_index_sha256"])
    observed={}
    consulted=[]
    hydrated=[]
    for e in plan["candidate_packed_chunks"]:
        section,n,nodes=e["section"],e["chunk_index"],e["node_ids"]
        item=idx[(section,n)]
        receipts=[]
        for d in physical_receipts_dirs:
            p=d/f"{section}-{n:06d}.json"
            if p.is_symlink():
                raise ValueError("symlinked original HTTP206 adjacency source receipt")
            if p.is_file():
                proof=_read_receipt(p)
                _check_receipt(proof,row=item,number=n,section=section,
                               rev=route["dataset_revision"],
                               manifest_sha=route["manifest_sha256"],
                               index_sha=route["original_index_sha256"],
                               bin_size=cross["original_bin_size_bytes"])
                receipts.append((p,proof))
        if not receipts:
            raise ValueError("bloom-positive original source candidate lacks HTTP206 equality")
        expected=receipts[0][1]["published_shard_raw_sha256"]
        if any(proof["published_shard_raw_sha256"]!=expected
               for _,proof in receipts):
            raise ValueError("cross-auditor source-original candidate hash disagreement")
        file,restored=_immutable_original_equal_shard(
            item=item,physical_sha=expected,
            revision=route["dataset_revision"],shard_root=shard_root,
            hydrate=hydrate,opener=opener)
        if restored:
            hydrated.append({"section":section,"chunk_index":n,
                             "bytes":item["length"]})
        rows,raw_sha=_native_decode_candidate(
            decoder=decoder,file=file,section=section,chunk=n,nodes=nodes,
            max_neighbors=max_neighbors,
            max_stdout_mib=max_stdout_mib,
            timeout_seconds=timeout_seconds,runner=runner)
        consulted.append({
            "section":section,"chunk_index":n,"original_equal_packed_sha256":expected,
            "original_http206_receipt_sha256":_file_sha(receipts[0][0],1024*1024),
            "native_selected_output_sha256":raw_sha,
            "bloom_candidate_node_count":len(nodes),
            "native_actual_node_row_count":len(rows),
            "bloom_false_positive_node_ids":sorted(set(nodes)-set(rows)),
        })
        for node,data in rows.items():
            observed[(node,section,n)]=data
    # Even a filter full-cover is never equivalent to a row read. Every
    # possible hit must appear in consulted with a genuine native output,
    # including explicitly recorded Bloom false positives.
    records=[]
    for node in route["queried_numeric_nodes"]:
        for section in ("left","right"):
            source=route["sections"][section]
            node_filter=next(row for row in source["nodes"] if row["node_id"]==node)
            maybes=node_filter["possible_native_source_chunk_indices"]
            hits=[(n,observed[(node,section,n)]) for n in maybes
                  if (node,section,n) in observed]
            edges=sorted({target for _,row in hits for target in row["neighbors"]})
            count=sum(row["values_seen"] for _,row in hits)
            records.append({
                "node_id":node,"direction":section,
                "original_complete_direction_chunk_scan":True,
                "source_equal_scanned_chunks":source["original_source_chunk_count"],
                "source_original_section_chunk_count":source["original_source_chunk_count"],
                "native_packed_hit_chunk_indices":[n for n,_ in hits],
                "candidate_chunk_indices_tested":maybes,
                "native_original_neighbors_sorted_unique":edges,
                "native_original_values_seen":count,
                "complete_one_hop_adjacency":True,
                "unknown_outside_scanned_source_chunks":False,
                "negative_chunk_keys_excluded_by_original_source_bloom":(
                    source["original_source_chunk_count"]-len(maybes)),
            })
    return {
        "version":_VERSION,
        "dataset_revision":route["dataset_revision"],
        "manifest_sha256":route["manifest_sha256"],
        "original_index_sha256":route["original_index_sha256"],
        "positive_roots_receipt_sha256":route["positive_roots_receipt_sha256"],
        "decoder_binary_sha256":route["native_decoder_sha256"],
        "root_qid_node_ids":route["qid_positive_original_nodes"],
        "target_numeric_nodes":route["queried_numeric_nodes"],
        "source_section_chunk_counts":{
            sec:route["sections"][sec]["original_source_chunk_count"]
            for sec in ("left","right")},
        "native_decoded_source_equal_chunks_by_section":{
            sec:route["sections"][sec]["original_source_chunk_count"]
            for sec in ("left","right")},
        "native_original_selected_node_direction_rows":records,
        "bloom_candidate_exact_native_replays":consulted,
        "one_sided_hydrated_original_equal_candidate_shards":hydrated,
        "all_original_adjacency_blooms_completed":True,
        "all_bloom_candidate_chunks_exact_native_replayed":True,
        "all_selected_root_one_hop_adjacencies_complete":True,
        "selected_root_adjacency_equal_exact_original_http206_bytes":True,
        "every_original_chunk_adjacency_key_natively_scanned":True,
        "unselected_noncandidate_chunks_omitted_only_by_complete_original_bloom":True,
        "all_original_source_bin_sha256_verified":False,
        "all_twenty_finite_relation_words_closed":False,
        "native_wikibase_p854_support_verified":False,
        "s29_review_persistence_paid":False,
        "edit_authority":False,
    }


def main()->int:
    p=argparse.ArgumentParser(description=__doc__)
    for name in ("manifest","original-index","positive-roots-receipt",
                 "bloom-root","decoder","shard-root"):
        p.add_argument("--"+name,type=Path,required=True)
    p.add_argument("--dataset-revision",required=True)
    p.add_argument("--manifest-sha256",required=True)
    p.add_argument("--original-index-sha256",required=True)
    p.add_argument("--physical-receipts-dir",type=Path,action="append",required=True)
    p.add_argument("--extra-node",type=int,action="append",default=[])
    p.add_argument("--max-hydrate-mib",type=int,default=512)
    p.add_argument("--max-neighbors",type=int,default=200000)
    p.add_argument("--max-stdout-mib",type=int,default=64)
    p.add_argument("--timeout-seconds",type=int,default=900)
    p.add_argument("--hydrate",action="store_true")
    p.add_argument("--execute",action="store_true")
    p.add_argument("--output",type=Path)
    args=p.parse_args()
    try:
        route=query_original_lr_blooms(
            manifest=args.manifest,original_index=args.original_index,
            revision=args.dataset_revision,
            manifest_sha256=args.manifest_sha256,
            original_index_sha256=args.original_index_sha256,
            positive_roots_receipt=args.positive_roots_receipt,
            physical_receipts_dirs=args.physical_receipts_dir,
            bloom_root=args.bloom_root,decoder_sha256=_file_sha(args.decoder),
            numeric_nodes=sorted(set(args.extra_node)))
        if args.execute:
            result=replay_exact_original_bloom_candidates(
                route=route,manifest=args.manifest,original_index=args.original_index,
                decoder=args.decoder,shard_root=args.shard_root,bloom_root=args.bloom_root,
                physical_receipts_dirs=args.physical_receipts_dir,
                positive_roots_receipt=args.positive_roots_receipt,
                max_hydrate_mib=args.max_hydrate_mib,
                max_neighbors=args.max_neighbors,max_stdout_mib=args.max_stdout_mib,
                timeout_seconds=args.timeout_seconds,hydrate=args.hydrate)
        else:
            result=plan_exact_original_bloom_replay(
                route=route,manifest=args.manifest,original_index=args.original_index,
                shard_root=args.shard_root,max_hydrate_mib=args.max_hydrate_mib)
        wire=json.dumps(result,sort_keys=True,indent=2)+"\n"
        if args.output:
            with args.output.open("x",encoding="utf-8") as out:
                out.write(wire)
        else:
            print(wire,end="")
        return 0 if (not args.execute or
                     result["all_selected_root_one_hop_adjacencies_complete"]) else 3
    except (OSError,ValueError,TypeError,KeyError,json.JSONDecodeError,
            subprocess.TimeoutExpired,sqlite3.DatabaseError) as exc:
        print(json.dumps({"status":"blocked","reason":str(exc),
                          "edit_authority":False}),file=sys.stderr)
        return 2


if __name__=="__main__":
    raise SystemExit(main())
