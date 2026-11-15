#!/usr/bin/env python3
"""A2: original-bin source-equal left/right native adjacency over selected nodes.

Only accepts local original packed adjacency bytes already matched byte-for-byte
to exact pinned original .bin HTTP206 ranges, with every original chunk
identified by the original full manifest/index partition. Streaming discovery
is bounded/resumable in SQLite. A row not seen in an incomplete source section
is UNKNOWN, never a negative graph observation. Exact selected-node direction
adjacency is certified ONLY after all source chunks in that direction have
both original-byte receipts AND native selected-node decoder receipts.

No P31/P279/P854 property semantics, no SPARQL/entire-world negative or edits.
SQLite is scratch, NOT SLR S29 production persistence.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import sqlite3
import subprocess
import sys
from typing import Any, Callable

from audit_zelph_hf_name_section_bytes import _check_receipt, _read_receipt
from verify_zelph_bin_shard_exact import _ARTIFACT, _manifest_index, _read_json
from verify_zelph_index_manifest_original import verify_index_manifest_files
from audit_zelph_native_name_fibres import _strict, _file_sha

_SHA=re.compile(r"[0-9a-f]{64}\Z")
_REV=re.compile(r"[0-9a-f]{40}\Z")
_QID=re.compile(r"Q[1-9][0-9]*\Z")
_NATIVE="itir.zelph.selected_native_capnp_decode.v1"
_DDL=(
    "CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY,value TEXT NOT NULL)",
    """CREATE TABLE IF NOT EXISTS completed_chunks(
      section TEXT NOT NULL, chunk_index INTEGER NOT NULL,
      receipt_sha256 TEXT NOT NULL, packed_sha256 TEXT NOT NULL,
      native_stdout_sha256 TEXT NOT NULL, matched_rows INTEGER NOT NULL,
      PRIMARY KEY(section,chunk_index))""",
    """CREATE TABLE IF NOT EXISTS observed_rows(
      section TEXT NOT NULL, chunk_index INTEGER NOT NULL, node_id TEXT NOT NULL,
      neighbors_json TEXT NOT NULL, values_seen INTEGER NOT NULL,
      PRIMARY KEY(section,chunk_index,node_id))""",
    "CREATE INDEX IF NOT EXISTS observed_by_node ON observed_rows(node_id,section)",
)


def _roots_from_receipt(path: Path) -> tuple[dict[str,int],dict]:
    data=_strict(path.read_bytes())
    if (data.get("version")!="itir.zelph.original_direct_native_positive_qid_roots.v1"
            or data.get("all_declared_qid_name_witnesses_positive") is not True
            or data.get("edit_authority") is not False):
        raise ValueError("actual source-equal native positive QID receipt required")
    entries=data.get("native_exact_positive_name_to_node_rows")
    if not isinstance(entries,list) or not entries or len(entries)>10000:
        raise ValueError("bounded nonempty original QID root records required")
    roots={}
    for row in entries:
        qid,node=row.get("qid"),row.get("node_id")
        if (type(qid) is not str or not _QID.fullmatch(qid)
                or qid in roots or type(node) is not int or
                not 0<=node<=2**64-1):
            raise ValueError("duplicate/noncanonical QID or invalid original node")
        roots[qid]=node
    return roots,data


def native_original_lr_plan(
    *, manifest:Path,original_index:Path,manifest_sha256:str,
    original_index_sha256:str,revision:str,physical_receipts_dirs:list[Path],
    shard_root:Path,positive_roots_receipt:Path,
    extra_numeric_nodes:list[int]|None=None,
    max_chunk_mib:int=256,
) -> dict:
    if (type(revision) is not str or not _REV.fullmatch(revision)
            or type(manifest_sha256) is not str or not _SHA.fullmatch(manifest_sha256)
            or type(original_index_sha256) is not str or not _SHA.fullmatch(original_index_sha256)
            or type(max_chunk_mib) is not int or not 0<max_chunk_mib<=16384):
        raise ValueError("pinned original source identity and chunk cap required")
    if not physical_receipts_dirs or len(physical_receipts_dirs)>16 or any(
        not p.is_dir() or p.is_symlink() for p in physical_receipts_dirs):
        raise ValueError("genuine original HTTP206 adjacency receipt roots required")
    if not shard_root.is_dir() or shard_root.is_symlink():
        raise ValueError("source-equal original adjacency packed shard root required")
    roots,native=_roots_from_receipt(positive_roots_receipt)
    if (native.get("dataset_revision")!=revision
            or native.get("manifest_sha256")!=manifest_sha256
            or native.get("original_index_sha256")!=original_index_sha256):
        raise ValueError("original source QID root identity disagrees with adjacency pins")
    extra=extra_numeric_nodes or []
    if (not isinstance(extra,list) or len(extra)>200000 or
            any(type(v) is not int or not 0<=v<=2**64-1 for v in extra)
            or extra!=sorted(set(extra))):
        raise ValueError("bounded sorted distinct extra original numeric nodes required")
    targets=sorted(set(roots.values())|set(extra))
    if not 0<len(targets)<=200000:
        raise ValueError("bounded selected original native roots required")
    meta=verify_index_manifest_files(
        manifest_path=manifest,index_path=original_index,
        manifest_sha256=manifest_sha256,index_sha256=original_index_sha256)
    index=_manifest_index(_read_json(manifest,16*1024*1024),_ARTIFACT)
    root=shard_root.resolve(strict=True)
    possible={}
    available=[]
    for section in ("left","right"):
        keys=sorted((n,item) for (s,n),item in index.items() if s==section)
        total=meta["section_chunk_counts"][section+"ChunkCount"]
        if len(keys)!=total or [n for n,_ in keys]!=list(range(total)):
            raise ValueError("original complete left/right section indices not reconciled")
        possible[section]=total
        for n,item in keys:
            matches=[]
            for physical in physical_receipts_dirs:
                receipt_path=physical/f"{section}-{n:06d}.json"
                if receipt_path.is_symlink():
                    raise ValueError("symlinked prior original adjacency proof")
                if receipt_path.is_file():
                    proof=_read_receipt(receipt_path)
                    _check_receipt(proof,row=item,number=n,section=section,
                                   rev=revision,manifest_sha=manifest_sha256,
                                   index_sha=original_index_sha256,
                                   bin_size=meta["original_bin_size_bytes"])
                    matches.append((receipt_path,proof))
            if not matches:
                continue
            if any(p["published_shard_raw_sha256"]!=matches[0][1]["published_shard_raw_sha256"]
                   for _,p in matches[1:]):
                raise ValueError("conflicting original HTTP206 adjacency SHA")
            if item["length"]>max_chunk_mib*1024**2:
                raise ValueError("original source-equal adjacency shard exceeds cap")
            shard=(root/item["relative"]).resolve(strict=False)
            if not shard.is_relative_to(root) or shard.is_symlink():
                raise ValueError("source-equal adjacency shard escapes root")
            if not shard.is_file():
                continue # source receipt alone cannot attest local native decoding
            if (shard.stat().st_size!=item["length"]
                    or _file_sha(shard)!=matches[0][1]["published_shard_raw_sha256"]):
                raise ValueError("local native adjacency does not match pinned original bin")
            available.append({
                "section":section,"chunk_index":n,
                "saved_original_equal_packed_file":str(shard),
                "packed_sha256":matches[0][1]["published_shard_raw_sha256"],
                "receipt_sha256":_file_sha(matches[0][0],1024*1024),
                "original_source_offset":item["offset"],
                "packed_size_bytes":item["length"],
            })
    return {
        "version":"itir.zelph.original_lr_native_plan.v1",
        "dataset_revision":revision,
        "manifest_sha256":manifest_sha256,
        "original_index_sha256":original_index_sha256,
        "positive_roots_receipt_sha256":_file_sha(positive_roots_receipt,16*1024*1024),
        "root_qid_node_ids":roots,
        "target_numeric_nodes":targets,
        "original_full_section_chunk_counts":possible,
        "available_native_source_equal_chunks":available,
        "available_native_chunk_count":len(available),
        "all_original_adjacency_chunks_physically_materialized":all(
            sum(x["section"]==sec for x in available)==n for sec,n in possible.items()),
        "no_unverified_chunk_can_be_negative_evidence":True,
        "all_query_words_closed":False,
        "source_support_paid":False,"edit_authority":False,
    }


def _decode_adjacency(*,entry:dict,targets:list[int],decoder:Path,
                      max_neighbors:int,max_stdout_mib:int,timeout_seconds:int,
                      runner:Callable[...,Any]) -> tuple[list[dict],str]:
    section,n=entry["section"],entry["chunk_index"]
    cmd=[str(decoder),"--file",entry["saved_original_equal_packed_file"],
         "--section",section,"--chunk-index",str(n),
         "--max-neighbors",str(max_neighbors)]
    for node in targets:
        cmd.extend(["--node",str(node)])
    proc=runner(cmd,capture_output=True,timeout=timeout_seconds,check=False)
    if (proc.returncode!=0 or type(proc.stdout) is not bytes
            or len(proc.stdout)>max_stdout_mib*1024*1024):
        raise ValueError("upstream native selected adjacency decoder failed/overflowed")
    payload=_strict(proc.stdout)
    if (payload.get("version")!=_NATIVE or payload.get("section")!=section
            or type(payload.get("chunk_index")) is not int
            or payload["chunk_index"]!=n
            or payload.get("candidate_only") is not True
            or payload.get("authority") is not False):
        raise ValueError("upstream native adjacency schema/section/authority mismatch")
    rows=payload.get("rows")
    if not isinstance(rows,list) or len(rows)>len(targets):
        raise ValueError("bounded native adjacency root rows required")
    seen=set()
    processed=[]
    target=set(targets)
    for row in rows:
        if not isinstance(row,dict):
            raise ValueError("nonobject source native adjacency row")
        node,adj,count=row.get("node_id"),row.get("neighbors"),row.get("values_seen")
        if (type(node) is not int or node not in target or node in seen
                or type(adj) is not list or len(adj)>max_neighbors
                or any(type(x) is not int or not 0<=x<=2**64-1 for x in adj)
                or adj!=sorted(set(adj))
                or type(count) is not int or count<len(adj)
                or row.get("truncated") is not False):
            raise ValueError("ambiguous/truncated original native adjacency row")
        seen.add(node)
        processed.append({"node_id":node,"neighbors":adj,"source_values_seen":count})
    return processed,sha256(proc.stdout).hexdigest()


def run_native_original_lr(*,plan:dict,decoder:Path,sqlite_index:Path,
    max_new_chunks:int=8,max_neighbors:int=200000,
    max_stdout_mib:int=64,timeout_seconds:int=900,
    runner:Callable[...,Any]=subprocess.run,
) -> dict:
    if (plan.get("version")!="itir.zelph.original_lr_native_plan.v1"
            or type(max_new_chunks) is not int or not 0<=max_new_chunks<=4096
            or type(max_neighbors) is not int or not 0<max_neighbors<=1000000
            or type(max_stdout_mib) is not int or not 0<max_stdout_mib<=1024
            or type(timeout_seconds) is not int or not 0<timeout_seconds<=7200):
        raise ValueError("valid pinned original native adjacency plan and resource caps required")
    if not decoder.is_file() or decoder.is_symlink() or sqlite_index.is_symlink():
        raise ValueError("real source Capnp decoder and non-symlink SQLite scratch required")
    if not sqlite_index.parent.is_dir() or sqlite_index.parent.is_symlink():
        raise ValueError("native adjacency scratch parent missing/symlink")
    decoder_sha=_file_sha(decoder)
    nodes=plan["target_numeric_nodes"]
    pins={
        "version":plan["version"],"revision":plan["dataset_revision"],
        "manifest":plan["manifest_sha256"],"index":plan["original_index_sha256"],
        "roots":plan["positive_roots_receipt_sha256"],
        "nodes":sha256(json.dumps(nodes).encode()).hexdigest(),
        "decoder":decoder_sha,
        "neighbor_limit":str(max_neighbors),
    }
    with sqlite3.connect(sqlite_index) as db:
        for stmt in _DDL:
            db.execute(stmt)
        prior=dict(db.execute("SELECT key,value FROM metadata"))
        if prior and prior!=pins:
            raise ValueError("mixed source revisions/target nodes/decoder in native adjacency scratch")
        if not prior:
            if (db.execute("SELECT COUNT(*) FROM observed_rows").fetchone()[0]
                    or db.execute("SELECT COUNT(*) FROM completed_chunks").fetchone()[0]):
                raise ValueError("unidentified foreign native adjacency observations")
            db.executemany("INSERT INTO metadata VALUES (?,?)",pins.items())
        available={(x["section"],x["chunk_index"]):x
                   for x in plan["available_native_source_equal_chunks"]}
        complete={}
        for s,n,r,p in db.execute(
            "SELECT section,chunk_index,receipt_sha256,packed_sha256 FROM completed_chunks"):
            k=(s,n)
            if k not in available or (r,p)!=(
                available[k]["receipt_sha256"],available[k]["packed_sha256"]):
                raise ValueError("previous original adjacency native chunk lost source evidence")
            complete[k]=True
        added=[]
        for entry in plan["available_native_source_equal_chunks"]:
            k=(entry["section"],entry["chunk_index"])
            if k in complete or len(added)>=max_new_chunks:
                continue
            # Prevent previously saved file drift before EVERY native replay.
            file=Path(entry["saved_original_equal_packed_file"])
            if _file_sha(file)!=entry["packed_sha256"]:
                raise ValueError("previously verified original adjacency packed data drift")
            rows,stdout_sha=_decode_adjacency(
                entry=entry,targets=nodes,decoder=decoder,
                max_neighbors=max_neighbors,max_stdout_mib=max_stdout_mib,
                timeout_seconds=timeout_seconds,runner=runner)
            with db:
                for row in rows:
                    db.execute("INSERT INTO observed_rows VALUES (?,?,?,?,?)",
                        (k[0],k[1],str(row["node_id"]),
                         json.dumps(row["neighbors"],separators=(",",":")),
                         row["source_values_seen"]))
                db.execute("INSERT INTO completed_chunks VALUES (?,?,?,?,?,?)",
                    (k[0],k[1],entry["receipt_sha256"],entry["packed_sha256"],
                     stdout_sha,len(rows)))
            added.append({"section":k[0],"chunk_index":k[1],
                          "observed_selected_node_rows":len(rows),
                          "native_stdout_sha256":stdout_sha})
        counts=dict(db.execute(
            "SELECT section,COUNT(*) FROM completed_chunks GROUP BY section"))
        all_sections={
            sec:counts.get(sec,0)==original
            for sec,original in plan["original_full_section_chunk_counts"].items()}
        node_rows=[]
        for node in nodes:
            for direction in ("left","right"):
                observed=[]
                total_values=0
                seen_chunks=[]
                for chunk,adj,count in db.execute(
                    "SELECT chunk_index,neighbors_json,values_seen FROM observed_rows "
                    "WHERE section=? AND node_id=? ORDER BY chunk_index",
                    (direction,str(node))):
                    observed.extend(json.loads(adj))
                    total_values+=count
                    seen_chunks.append(chunk)
                node_rows.append({
                    "node_id":node,"direction":direction,
                    "original_complete_direction_chunk_scan":all_sections[direction],
                    "source_equal_scanned_chunks":counts.get(direction,0),
                    "source_original_section_chunk_count":
                        plan["original_full_section_chunk_counts"][direction],
                    "native_packed_hit_chunk_indices":seen_chunks,
                    "native_original_neighbors_sorted_unique":sorted(set(observed)),
                    "native_original_values_seen":total_values,
                    "complete_one_hop_adjacency":all_sections[direction],
                    "unknown_outside_scanned_source_chunks":not all_sections[direction],
                })
        return {
            "version":"itir.zelph.original_lr_native_complete_chunk_scans.v1",
            "dataset_revision":plan["dataset_revision"],
            "manifest_sha256":plan["manifest_sha256"],
            "original_index_sha256":plan["original_index_sha256"],
            "positive_roots_receipt_sha256":plan["positive_roots_receipt_sha256"],
            "root_qid_node_ids":plan["root_qid_node_ids"],
            "target_numeric_nodes":nodes,
            "decoder_binary_sha256":decoder_sha,
            "source_section_chunk_counts":plan["original_full_section_chunk_counts"],
            "native_decoded_source_equal_chunks_by_section":
                {s:counts.get(s,0) for s in ("left","right")},
            "newly_decoded_chunks":added,
            "native_original_selected_node_direction_rows":node_rows,
            "all_source_equal_original_chunks_natively_scanned":
                all(all_sections.values()),
            "all_selected_root_one_hop_adjacencies_complete":
                all(all_sections.values()),
            "selected_root_adjacency_equal_exact_original_http206_bytes":
                all(all_sections.values()),
            "original_entire_bin_sha256_verified":False,
            "all_twenty_finite_relation_words_closed":False,
            "native_p854_source_support_paid":False,
            "s29_persistence_paid":False,"edit_authority":False,
        }


def main()->int:
    p=argparse.ArgumentParser(description=__doc__)
    for a in ("manifest","original-index","positive-roots-receipt","shard-root",
              "decoder","sqlite-index"):
        p.add_argument("--"+a,type=Path,required=True)
    p.add_argument("--dataset-revision",required=True)
    p.add_argument("--manifest-sha256",required=True)
    p.add_argument("--original-index-sha256",required=True)
    p.add_argument("--physical-receipts-dir",type=Path,action="append",required=True)
    p.add_argument("--extra-node",type=int,action="append",default=[])
    p.add_argument("--max-new-chunks",type=int,default=8)
    p.add_argument("--max-chunk-mib",type=int,default=256)
    p.add_argument("--max-neighbors",type=int,default=200000)
    p.add_argument("--max-stdout-mib",type=int,default=64)
    p.add_argument("--timeout-seconds",type=int,default=900)
    p.add_argument("--execute",action="store_true")
    p.add_argument("--output",type=Path)
    args=p.parse_args()
    try:
        plan=native_original_lr_plan(
            manifest=args.manifest,original_index=args.original_index,
            manifest_sha256=args.manifest_sha256,
            original_index_sha256=args.original_index_sha256,
            revision=args.dataset_revision,
            physical_receipts_dirs=args.physical_receipts_dir,
            shard_root=args.shard_root,
            positive_roots_receipt=args.positive_roots_receipt,
            extra_numeric_nodes=sorted(set(args.extra_node)),
            max_chunk_mib=args.max_chunk_mib)
        if not args.execute:
            print(json.dumps(plan,sort_keys=True,indent=2))
            return 0
        result=run_native_original_lr(
            plan=plan,decoder=args.decoder,sqlite_index=args.sqlite_index,
            max_new_chunks=args.max_new_chunks,
            max_neighbors=args.max_neighbors,
            max_stdout_mib=args.max_stdout_mib,
            timeout_seconds=args.timeout_seconds)
        wire=json.dumps(result,sort_keys=True,indent=2)+"\n"
        if args.output:
            with args.output.open("x",encoding="utf-8") as out:out.write(wire)
        else:
            print(wire,end="")
        return 0
    except (OSError,ValueError,KeyError,TypeError,json.JSONDecodeError,
            sqlite3.DatabaseError,subprocess.TimeoutExpired) as exc:
        print(json.dumps({"status":"blocked","reason":str(exc),
                          "edit_authority":False}),file=sys.stderr)
        return 2


if __name__=="__main__":
    raise SystemExit(main())
