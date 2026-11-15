#!/usr/bin/env python3
"""A2-B original-source native adjacency Bloom *candidate* routing.

Requires pinned exact original manifest/index; each retained Bloom filter is
tied to (a) a physical HTTP206 == published Capnp shard receipt, (b) actual
same-schema native full-AdjPair extraction through exact packed EOF, and (c)
the same compiled decoder SHA. A Bloom candidate MUST be replayed natively.
Only a complete section of independently verified Bloom negatives can prove
that a requested numeric node has no adjacency row in that direction.

The upstream producer serializes an *unordered segmented_map*, so never
infer node routes by chunk ordinals, first/last key ranges, or modulo.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import sys

from audit_zelph_hf_name_section_bytes import _check_receipt,_read_receipt
from audit_zelph_native_name_fibres import _strict,_file_sha
from build_zelph_original_lr_bloom import (
    WIRE_BYTES,_VERSION,bloom_possible,validate_wire,
)
from verify_zelph_bin_shard_exact import _ARTIFACT,_manifest_index,_read_json
from verify_zelph_index_manifest_original import verify_index_manifest_files

_REV=re.compile(r"[0-9a-f]{40}\Z")
_SHA=re.compile(r"[0-9a-f]{64}\Z")


def query_original_lr_blooms(
    *,manifest:Path,original_index:Path,revision:str,
    manifest_sha256:str,original_index_sha256:str,
    positive_roots_receipt:Path,decoder_sha256:str,
    physical_receipts_dirs:list[Path],bloom_root:Path,
    numeric_nodes:list[int]|None=None,
)->dict:
    if (type(revision) is not str or not _REV.fullmatch(revision)
            or any(type(x) is not str or not _SHA.fullmatch(x)
                   for x in (manifest_sha256,original_index_sha256,decoder_sha256))):
        raise ValueError("original native decoder and immutable raw source SHA pins required")
    if (not bloom_root.is_dir() or bloom_root.is_symlink()
            or not physical_receipts_dirs or len(physical_receipts_dirs)>16
            or any(not d.is_dir() or d.is_symlink() for d in physical_receipts_dirs)):
        raise ValueError("original native Bloom and genuine physical receipt directories required")
    roots=_strict(positive_roots_receipt.read_bytes())
    if (roots.get("version")!="itir.zelph.original_direct_native_positive_qid_roots.v1"
            or roots.get("dataset_revision")!=revision
            or roots.get("manifest_sha256")!=manifest_sha256
            or roots.get("original_index_sha256")!=original_index_sha256
            or roots.get("all_declared_qid_name_witnesses_positive") is not True
            or roots.get("edit_authority") is not False):
        raise ValueError("selected original QID roots have not been authenticated")
    named=roots.get("native_exact_positive_name_to_node_rows")
    if not isinstance(named,list) or not named or len(named)>256:
        raise ValueError("bounded exact source QID root receipt required")
    qid_nodes={}
    for row in named:
        q,n=row.get("qid"),row.get("node_id")
        if (type(q) is not str or not re.fullmatch(r"Q[1-9][0-9]*",q)
                or type(n) is not int or not 0<=n<=2**64-1 or q in qid_nodes):
            raise ValueError("invalid or duplicate genuine original QID/node root")
        qid_nodes[q]=n
    extra=numeric_nodes or []
    if (not isinstance(extra,list) or len(extra)>256
            or any(type(n) is not int or not 0<=n<=2**64-1 for n in extra)
            or extra!=sorted(set(extra))):
        raise ValueError("bounded ordered distinct extra numeric graph nodes required")
    requested=sorted(set(qid_nodes.values())|set(extra))
    if len(requested)>256:
        raise ValueError("native original Bloom query target bound exceeded")
    root_sha=_file_sha(positive_roots_receipt,16*1024*1024)
    verified=verify_index_manifest_files(
        manifest_path=manifest,index_path=original_index,
        manifest_sha256=manifest_sha256,index_sha256=original_index_sha256)
    index=_manifest_index(_read_json(manifest,16*1024*1024),_ARTIFACT)
    stats={}
    for section in ("left","right"):
        source=sorted((n,row) for (s,n),row in index.items() if s==section)
        expected=verified["section_chunk_counts"][section+"ChunkCount"]
        if len(source)!=expected or [n for n,_ in source]!=list(range(expected)):
            raise ValueError("invalid full original adjacency section domain")
        candidates={n:[] for n in requested}
        unobserved=[]
        present=0
        indexed_rows=0
        for chunk,item in source:
            bitmap_path=bloom_root/f"{section}-{chunk:06d}.zlbloom"
            proof_path=bloom_root/f"{section}-{chunk:06d}.json"
            if bitmap_path.is_symlink() or proof_path.is_symlink():
                raise ValueError("symlinked original native adjacency Bloom")
            if not bitmap_path.exists() and not proof_path.exists():
                unobserved.append(chunk)
                continue
            if not bitmap_path.is_file() or not proof_path.is_file():
                raise ValueError("partially published native original Bloom is not evidence")
            saved=_strict(proof_path.read_bytes())
            if (saved.get("version")!=_VERSION
                    or saved.get("dataset_revision")!=revision
                    or saved.get("manifest_sha256")!=manifest_sha256
                    or saved.get("original_index_sha256")!=original_index_sha256
                    or saved.get("positive_roots_receipt_sha256")!=root_sha
                    or saved.get("native_decoder_sha256")!=decoder_sha256
                    or saved.get("section")!=section
                    or type(saved.get("chunk_index")) is not int
                    or saved["chunk_index"]!=chunk
                    or saved.get("original_packed_source_offset")!=item["offset"]
                    or saved.get("original_packed_size_bytes")!=item["length"]
                    or saved.get("native_original_packed_eof_checked_before_bloom_emission") is not True
                    or saved.get("a_bloom_positive_requires_original_native_row_replay") is not True
                    or saved.get("edit_authority") is not False):
                raise ValueError("Bloom source/direction/native identity mismatch")
            raw=bitmap_path.read_bytes()
            bitmap,rows=validate_wire(raw,section=section,chunk_index=chunk)
            if (saved.get("native_bloom_wire_sha256")!=sha256(raw).hexdigest()
                    or type(saved.get("native_adjacency_key_rows_seen")) is not int
                    or saved["native_adjacency_key_rows_seen"]!=rows):
                raise ValueError("Bloom wire digest or complete original row count mismatched")
            accepted=[]
            for directory in physical_receipts_dirs:
                source_proof=directory/f"{section}-{chunk:06d}.json"
                if source_proof.is_symlink():
                    raise ValueError("original physical source receipt symlink")
                if not source_proof.is_file():
                    continue
                prior=_read_receipt(source_proof)
                _check_receipt(
                    prior,row=item,number=chunk,section=section,
                    rev=revision,manifest_sha=manifest_sha256,
                    index_sha=original_index_sha256,
                    bin_size=verified["original_bin_size_bytes"])
                if (prior["published_shard_raw_sha256"]!=saved.get(
                        "original_equal_packed_shard_sha256")):
                    raise ValueError("Bloom original packed digest disagrees with source HTTP206")
                accepted.append(_file_sha(source_proof,1024*1024))
            if saved.get("physical_http206_receipt_sha256") not in accepted:
                raise ValueError("native original Bloom lacks unchanged actual HTTP206 source receipt")
            for node in requested:
                if bloom_possible(bitmap,node):
                    candidates[node].append(chunk)
            indexed_rows+=rows
            present+=1
        complete=present==expected
        stats[section]={
            "section":section,
            "original_source_chunk_count":expected,
            "native_original_bloom_verified_chunk_count":present,
            "complete_original_bloom_section_cover":complete,
            "native_original_adj_pair_key_rows_indexed":indexed_rows,
            "missing_bloom_chunk_indices":unobserved,
            "nodes":[{
                "node_id":node,
                "possible_native_source_chunk_indices":candidates[node],
                "definitely_absent_from_verified_chunk_count":
                    present-len(candidates[node]),
                "unverified_chunk_count":len(unobserved),
                "exact_no_adjacency_row_proved":
                    complete and not candidates[node],
                "candidate_original_adjacency_rows_still_require_native_replay":
                    bool(candidates[node]),
                "global_node_direction_coverage_complete":complete,
                "missing_original_chunks_are_unknown":bool(unobserved),
            } for node in requested],
        }
    return {
        "version":"itir.zelph.original_lr_bloom_candidate_route.v1",
        "dataset_revision":revision,
        "manifest_sha256":manifest_sha256,
        "original_index_sha256":original_index_sha256,
        "positive_roots_receipt_sha256":root_sha,
        "native_decoder_sha256":decoder_sha256,
        "qid_positive_original_nodes":qid_nodes,
        "queried_numeric_nodes":requested,
        "sections":stats,
        "all_original_adjacency_blooms_completed":
            all(s["complete_original_bloom_section_cover"] for s in stats.values()),
        "bloom_candidates_are_exact_native_routes":False,
        "bloom_negative_valid_for_original_chunks_only":True,
        "original_node_ids_not_ordered_by_chunk_index":True,
        "twenty_relation_words_closed":False,
        "source_support_paid":False,"edit_authority":False,
    }


def main()->int:
    p=argparse.ArgumentParser(description=__doc__)
    for name in ("manifest","original-index","positive-roots-receipt","bloom-root"):
        p.add_argument("--"+name,type=Path,required=True)
    p.add_argument("--dataset-revision",required=True)
    p.add_argument("--manifest-sha256",required=True)
    p.add_argument("--original-index-sha256",required=True)
    p.add_argument("--decoder-sha256",required=True)
    p.add_argument("--physical-receipts-dir",type=Path,action="append",required=True)
    p.add_argument("--extra-node",type=int,action="append",default=[])
    p.add_argument("--output",type=Path)
    args=p.parse_args()
    try:
        result=query_original_lr_blooms(
            manifest=args.manifest,original_index=args.original_index,
            revision=args.dataset_revision,
            manifest_sha256=args.manifest_sha256,
            original_index_sha256=args.original_index_sha256,
            positive_roots_receipt=args.positive_roots_receipt,
            decoder_sha256=args.decoder_sha256,
            physical_receipts_dirs=args.physical_receipts_dir,
            bloom_root=args.bloom_root,
            numeric_nodes=sorted(set(args.extra_node)))
        wire=json.dumps(result,sort_keys=True,indent=2)+"\n"
        if args.output:
            with args.output.open("x",encoding="utf-8") as out:out.write(wire)
        else:
            print(wire,end="")
        return 0
    except (OSError,ValueError,KeyError,TypeError,json.JSONDecodeError) as exc:
        print(json.dumps({"status":"blocked","reason":str(exc),
                          "edit_authority":False}),file=sys.stderr)
        return 2


if __name__=="__main__":
    raise SystemExit(main())
