#!/usr/bin/env python3
"""A2 original HTTP206 -> original Capnp native -> finite left/right word closure.

Consumes actual same-immutable-source native full-section-sweep RECEIPTS from
audit_zelph_native_original_lr_roots.py. A sweep not complete for all original
left/right chunks is never treated as exact node outgoing adjacency. Combines
root sweep + separately scanned numeric frontier sweeps with exact source SHA,
root QID, original index, decoder identity and neighbour-set agreement.

This checks only the DECLARED finite relation words. It does not prove
Wikibase property filters, all graph paths, negative source entity existence,
full-bin SHA, original formal Agda theorem or S29 reviewer authority.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import sys
from typing import Any

from audit_zelph_finite_query_family import _strict_json

_QID=re.compile(r"Q[1-9][0-9]*\Z")
_SHA=re.compile(r"[0-9a-f]{64}\Z")
_REV=re.compile(r"[0-9a-f]{40}\Z")


def original_http206_finite_words(
    *,query_family:dict,audits:list[tuple[dict,str]],
    max_frontier:int=200000,max_steps:int=16,
)->dict:
    if (not audits or len(audits)>64
            or type(max_frontier) is not int or not 0<max_frontier<=1000000
            or type(max_steps) is not int or not 0<max_steps<=64):
        raise ValueError("positive bounded finite original query closure required")
    if query_family.get("version")!="itir.zelph.finite_lr_query_family.v1":
        raise ValueError("explicit pinned original finite relation-word contract required")
    qids=query_family.get("qid_root_nodes")
    queries=query_family.get("queries")
    if (not isinstance(qids,dict) or not qids
            or not isinstance(queries,list) or not queries or len(queries)>10000):
        raise ValueError("nonempty root QIDs and bounded original finite query family required")
    reference=None
    row_map={}
    row_sources={}
    receipts=[]
    for item,raw_sha in audits:
        if type(raw_sha) is not str or not _SHA.fullmatch(raw_sha):
            raise ValueError("raw native scan receipt SHA invalid")
        direct=item.get("version")=="itir.zelph.original_lr_native_complete_chunk_scans.v1"
        bloom=item.get("version")=="itir.zelph.original_lr_bloom_pruned_exact_native_onehop.v1"
        if (not (direct or bloom) or item.get("edit_authority") is not False):
            raise ValueError("original-native source-equal adjacency audit receipt required")
        if bloom and (
            item.get("all_original_adjacency_blooms_completed") is not True
            or item.get("all_bloom_candidate_chunks_exact_native_replayed") is not True
            or item.get("every_original_chunk_adjacency_key_natively_scanned") is not True
            or item.get("unselected_noncandidate_chunks_omitted_only_by_complete_original_bloom") is not True
        ):
            raise ValueError("Bloom-pruned selected adjacency lacks full original source membership evidence")
        keys=("dataset_revision","manifest_sha256","original_index_sha256",
              "positive_roots_receipt_sha256","decoder_binary_sha256")
        identity=tuple(item.get(k) for k in keys)
        if (not _REV.fullmatch(identity[0] or "")
                or any(type(h) is not str or not _SHA.fullmatch(h)
                       for h in identity[1:])):
            raise ValueError("invalid immutable original graph/decoder/roots identity")
        if reference is None:
            reference=identity
        elif reference!=identity:
            raise ValueError("cross-source revision, manifest/index, roots or decoder drift")
        if ((direct and item.get("all_source_equal_original_chunks_natively_scanned") is not True)
                or item.get("all_selected_root_one_hop_adjacencies_complete") is not True
                or item.get("selected_root_adjacency_equal_exact_original_http206_bytes") is not True):
            # A partial scan may be passed, but never promote its rows into
            # exact source traversal. Record omitted node coverage via result.
            receipts.append({"sha256":raw_sha,"accepted_exact_scan":False})
            continue
        if item.get("root_qid_node_ids")!=audits[0][0].get("root_qid_node_ids"):
            raise ValueError("native QID roots changed across original adjacency sweeps")
        source_counts=item.get("source_section_chunk_counts")
        scanned=item.get("native_decoded_source_equal_chunks_by_section")
        if (type(source_counts) is not dict or type(scanned) is not dict
                or any(type(source_counts.get(direction)) is not int
                       or source_counts[direction]<=0
                       or type(scanned.get(direction)) is not int
                       or scanned[direction]!=source_counts[direction]
                       for direction in ("left","right"))):
            raise ValueError("native original left/right physical complete section count drift")
        declared=item.get("target_numeric_nodes")
        if (not isinstance(declared,list) or declared!=sorted(set(declared))
                or any(type(node) is not int or not 0<=node<=2**64-1
                       for node in declared)):
            raise ValueError("native declared original numeric roots malformed")
        records=item.get("native_original_selected_node_direction_rows")
        if type(records) is not list or len(records)!=2*len(declared):
            raise ValueError("original native scan missing declared node/direction rows")
        seen_local=set()
        replayed=set()
        if bloom:
            actual=item.get("bloom_candidate_exact_native_replays")
            if not isinstance(actual,list) or len(actual)>200000:
                raise ValueError("Bloom-pruned original native candidate replays missing")
            for source in actual:
                if type(source) is not dict:
                    raise ValueError("invalid original native candidate replay receipt")
                key=(source.get("section"),source.get("chunk_index"))
                if (key[0] not in ("left","right")
                        or type(key[1]) is not int
                        or not 0<=key[1]<source_counts[key[0]]
                        or key in replayed
                        or type(source.get("native_selected_output_sha256")) is not str
                        or not _SHA.fullmatch(source["native_selected_output_sha256"])
                        or type(source.get("original_equal_packed_sha256")) is not str
                        or not _SHA.fullmatch(source["original_equal_packed_sha256"])
                        or type(source.get("original_http206_receipt_sha256")) is not str
                        or not _SHA.fullmatch(source["original_http206_receipt_sha256"])):
                    raise ValueError("original source Bloom candidate replay has malformed provenance")
                replayed.add(key)
        declared_candidates=set()
        for row in records:
            node,dir=row.get("node_id"),row.get("direction")
            if (type(node) is not int or node not in declared or dir not in ("left","right")
                    or (node,dir) in seen_local
                    or row.get("complete_one_hop_adjacency") is not True
                    or row.get("unknown_outside_scanned_source_chunks") is not False
                    or row.get("source_equal_scanned_chunks")!=source_counts[dir]
                    or row.get("source_original_section_chunk_count")!=source_counts[dir]):
                raise ValueError("full original source node/direction scan malformed")
            seen_local.add((node,dir))
            if bloom:
                candidates=row.get("candidate_chunk_indices_tested")
                hits=row.get("native_packed_hit_chunk_indices")
                if (type(candidates) is not list or
                        any(type(x) is not int or not 0<=x<source_counts[dir]
                            for x in candidates) or
                        candidates!=sorted(set(candidates))
                        or type(hits) is not list or
                        any(type(x) is not int for x in hits) or
                        hits!=sorted(set(hits)) or
                        not set(hits).issubset(set(candidates)) or
                        row.get("negative_chunk_keys_excluded_by_original_source_bloom")!=
                            source_counts[dir]-len(candidates)):
                    raise ValueError("Bloom-pruned native source candidate/hit route incomplete")
                declared_candidates.update((dir,c) for c in candidates)
            neighbors=row.get("native_original_neighbors_sorted_unique")
            seen=row.get("native_original_values_seen")
            if (not isinstance(neighbors,list) or len(neighbors)>max_frontier
                    or neighbors!=sorted(set(neighbors))
                    or any(type(n) is not int or not 0<=n<=2**64-1
                           for n in neighbors)
                    or type(seen) is not int or seen<len(neighbors)):
                raise ValueError("noncanonical truncated original adjacency scope")
            key=(node,dir)
            if key in row_map and row_map[key]!=neighbors:
                raise ValueError("conflicting authentic source-equal native adjacency rows")
            row_map[key]=neighbors
            row_sources.setdefault(key,set()).add(raw_sha)
        if seen_local!={(n,d) for n in declared for d in ("left","right")}:
            raise ValueError("selected original native directional completeness missing")
        if bloom and declared_candidates!=replayed:
            raise ValueError("full original Bloom candidate set not exactly replayed")
        receipts.append({"sha256":raw_sha,"accepted_exact_scan":True,
                         "scan_method": "complete-original-bloom-candidates" if bloom else "complete-original-direct-sweep",
                         "nodes":len(declared)})
    roots=audits[0][0].get("root_qid_node_ids")
    if (not isinstance(roots,dict) or not roots
            or any(type(qid) is not str or not _QID.fullmatch(qid)
                   or type(node) is not int or not 0<=node<=2**64-1
                   for qid,node in roots.items())
            or qids!=roots):
        raise ValueError("finite family QIDs/roots differ from original source positive name rows")
    response=[]
    missing={}
    labels=set()
    distinct_relation_contracts=set()
    for item in queries:
        if type(item) is not dict:
            raise ValueError("original finite query row not object")
        label,qid,word=item.get("id"),item.get("qid"),item.get("word")
        if (type(label) is not str or not label or label in labels
                or type(qid) is not str or qid not in roots
                or type(word) is not list or len(word)>max_steps
                or any(dir not in ("left","right") for dir in word)):
            raise ValueError("invalid original finite relation query label/word")
        labels.add(label)
        contract=(qid,tuple(word))
        if contract in distinct_relation_contracts:
            raise ValueError("duplicate original QID/relation-word contract cannot count as a distinct finite query")
        distinct_relation_contracts.add(contract)
        frontier={roots[qid]}
        trace=[]
        gaps=[]
        for step,dir in enumerate(word):
            if len(frontier)>max_frontier:
                raise ValueError("original finite word frontier over resource budget")
            unseen=sorted(n for n in frontier if (n,dir) not in row_map)
            if unseen:
                for n in unseen:
                    missing.setdefault((n,dir),set()).add(label)
                    gaps.append({"step":step,"node_id":n,"direction":dir})
                break
            next_set=set()
            provenance=set()
            for node in frontier:
                next_set.update(row_map[(node,dir)])
                provenance.update(row_sources[(node,dir)])
            if len(next_set)>max_frontier:
                raise ValueError("expanded original graph numeric frontier over bound")
            trace.append({
                "step":step,"direction":dir,"input_nodes":sorted(frontier),
                "result_nodes":sorted(next_set),
                "source_equal_native_scan_receipt_shas":sorted(provenance),
            })
            frontier=next_set
        response.append({
            "id":label,"qid":qid,"relation_word":word,
            "status":"complete-for-declared-original-word" if not gaps
                     else "incomplete-unobserved-source-boundary",
            "trace":trace,
            "end_nodes":sorted(frontier) if not gaps else None,
            "missing_boundaries":gaps,
        })
    needed=[{"node_id":n,"direction":dir,"required_for_queries":sorted(labels)}
            for (n,dir),labels in sorted(missing.items())]
    return {
        "version":"itir.zelph.original_http206_native_lr_finite_words.v1",
        "dataset_revision":reference[0],
        "manifest_sha256":reference[1],
        "original_index_sha256":reference[2],
        "native_positive_roots_receipt_sha256":reference[3],
        "native_decoder_sha256":reference[4],
        "query_count":len(queries),
        "query_results":response,
        "observed_exact_node_direction_rows":len(row_map),
        "all_declared_original_lr_words_closed":not missing,
        "all_twenty_original_lr_words_closed":(
            len(queries)==20 and len(distinct_relation_contracts)==20 and not missing
        ),
        "distinct_declared_root_relation_word_count":len(distinct_relation_contracts),
        "twenty_word_scope_is_explicitly_declared_not_all_possible_paths":True,
        "original_qid_global_unique_name_fibres_verified":False,
        "closure_is_for_explicit_root_node_ids_only":True,
        "upstream_native_scan_receipts_replayed_in_this_evaluator":False,
        "full_bloom_candidate_source_stage_supported":True,
        "missing_source_numeric_frontiers":needed,
        "next_numeric_nodes_to_native_scan":sorted(set(row["node_id"] for row in needed)),
        "source_equal_native_full_section_sweep_receipts":receipts,
        "all_original_source_bin_bytes_hashed_in_one_full_binary_sha":False,
        "original_native_wikibase_property_filter_verified":False,
        "p854_source_support_paid":False,
        "s29_persistence_paid":False,"edit_authority":False,
    }


def main()->int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--query-family",type=Path,required=True)
    p.add_argument("--native-audit",type=Path,action="append",required=True)
    p.add_argument("--max-frontier",type=int,default=200000)
    p.add_argument("--max-steps",type=int,default=16)
    p.add_argument("--output",type=Path)
    args=p.parse_args()
    try:
        family,_=_strict_json(args.query_family)
        audits=[_strict_json(p) for p in args.native_audit]
        result=original_http206_finite_words(
            query_family=family,audits=audits,
            max_frontier=args.max_frontier,max_steps=args.max_steps)
        wire=json.dumps(result,sort_keys=True,indent=2)+"\n"
        if args.output:
            with args.output.open("x",encoding="utf-8") as out:out.write(wire)
        else:
            print(wire,end="")
        return 0 if result["all_declared_original_lr_words_closed"] else 3
    except (OSError,ValueError,KeyError,TypeError,json.JSONDecodeError) as exc:
        print(json.dumps({"status":"blocked","reason":str(exc),
                          "edit_authority":False}),file=sys.stderr)
        return 2


if __name__=="__main__":
    raise SystemExit(main())
