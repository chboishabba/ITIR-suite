#!/usr/bin/env python3
"""A2 physical prerequisite: resumable original HTTP206 left/right sections.

For each original section-global chunk, reuse the exact existing ITIR
HTTP206-original .bin vs pinned published packed shard streaming comparator.
A one-sided retained physical receipt is never evidence of all node routes.
No global adjacency/negative/20-word claims until *every* 984 per-section
chunk is source-byte verified and natively decoded with a declared root set.

Can import prior individual physical receipts and retain the exact packed
Cap'n Proto shard in the SAME original-range equality stream. No whole .bin.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import sys
from typing import Any, Callable

from audit_zelph_hf_name_section_bytes import _read_receipt, _check_receipt
from verify_zelph_bin_shard_exact import _ARTIFACT, _manifest_index, _read_json
from verify_zelph_hf_direct_original_chunk import verify_direct_original_chunk
from verify_zelph_index_manifest_original import verify_index_manifest_files

_SHA = re.compile(r"[0-9a-f]{64}\Z")
_REV = re.compile(r"[0-9a-f]{40}\Z")
_MIB = 1024 * 1024


def audit_adjacency_section(
    *, manifest_path: Path, original_index_path: Path,
    dataset_revision: str, manifest_sha256: str, original_index_sha256: str,
    section: str, receipts_dir: Path,
    max_new_chunks: int = 8, max_transfer_mib: int = 1024,
    max_chunk_mib: int = 256, execute: bool = False,
    save_published_root: Path | None = None,
    import_physical_receipts_dirs: list[Path] | None = None,
    opener: Callable[..., Any] | None = None,
    compare: Callable[..., dict[str, Any]] = verify_direct_original_chunk,
) -> dict[str, Any]:
    if (type(dataset_revision) is not str or not _REV.fullmatch(dataset_revision)
            or type(manifest_sha256) is not str or not _SHA.fullmatch(manifest_sha256)
            or type(original_index_sha256) is not str or not _SHA.fullmatch(original_index_sha256)):
        raise ValueError("40-hex original revision and two independent 64-hex raw SHA pins required")
    if section not in ("left","right"):
        raise ValueError("only original physical adjacency sections left/right supported")
    if (type(max_new_chunks) is not int or not 0 <= max_new_chunks <= 4096
            or type(max_transfer_mib) is not int or not 0 < max_transfer_mib <= 65536
            or type(max_chunk_mib) is not int or not 0 < max_chunk_mib <= 16384):
        raise ValueError("positive bounded original source section budgets required")
    if receipts_dir.is_symlink() or (receipts_dir.exists() and not receipts_dir.is_dir()):
        raise ValueError("physical original section receipts must be a real directory")
    imports = import_physical_receipts_dirs or []
    if (not isinstance(imports,list) or len(imports)>16
            or any(not d.is_dir() or d.is_symlink() for d in imports)):
        raise ValueError("untrusted prior physical receipts import directory")
    if save_published_root is not None:
        if (save_published_root.is_symlink()
                or (save_published_root.exists() and not save_published_root.is_dir())
                or not save_published_root.parent.is_dir()):
            raise ValueError("invalid saved original-equal packed shard root")
        if (save_published_root.resolve()==receipts_dir.resolve()
                or save_published_root.resolve().is_relative_to(receipts_dir.resolve())
                or receipts_dir.resolve().is_relative_to(save_published_root.resolve())):
            raise ValueError("original adjacency packed and physical evidence roots must differ")
    metadata=verify_index_manifest_files(
        manifest_path=manifest_path, index_path=original_index_path,
        manifest_sha256=manifest_sha256, index_sha256=original_index_sha256)
    if (metadata.get("all_manifest_chunk_offsets_equal_original_index") is not True
            or metadata.get("entire_index_partition_gap_free") is not True
            or metadata.get("entire_index_partition_nonoverlapping") is not True):
        raise ValueError("original adjacency full index/manifest partition not verified")
    full=_manifest_index(_read_json(manifest_path,16*_MIB),_ARTIFACT)
    original=sorted((n,r) for (s,n),r in full.items() if s==section)
    if (not original or [n for n,_ in original]!=list(range(len(original)))
            or metadata["section_chunk_counts"][section+"ChunkCount"]!=len(original)):
        raise ValueError("original adjacency section indices are not the complete source domain")
    covered=[]
    missing=[]
    imported=[]
    planned_imports=[]
    for n,item in original:
        dest=receipts_dir/f"{section}-{n:06d}.json"
        if dest.is_symlink():
            raise ValueError("symlinked original adjacency receipt")
        if dest.is_file():
            proof=_read_receipt(dest)
            _check_receipt(proof,row=item,number=n,section=section,rev=dataset_revision,
                           manifest_sha=manifest_sha256,index_sha=original_index_sha256,
                           bin_size=metadata["original_bin_size_bytes"])
            covered.append((n,item,dest))
            continue
        candidate=[]
        for d in imports:
            p=d/f"{section}-{n:06d}.json"
            if p.is_symlink():
                raise ValueError("symlinked imported original adjacency receipt")
            if p.is_file():
                proof=_read_receipt(p)
                _check_receipt(proof,row=item,number=n,section=section,rev=dataset_revision,
                               manifest_sha=manifest_sha256,index_sha=original_index_sha256,
                               bin_size=metadata["original_bin_size_bytes"])
                candidate.append((p,proof))
        if candidate:
            if any(c[1]["published_shard_raw_sha256"]!=candidate[0][1]["published_shard_raw_sha256"]
                   for c in candidate[1:]):
                raise ValueError("conflicting original source-equal adjacency physical receipts")
            planned_imports.append(n)
            if execute:
                receipts_dir.mkdir(parents=True,exist_ok=True)
                raw=candidate[0][0].read_bytes()
                with dest.open("xb") as out:
                    out.write(raw)
                if sha256(raw).hexdigest()!=sha256(dest.read_bytes()).hexdigest():
                    raise ValueError("imported original adjacency physical evidence drifted")
                covered.append((n,item,dest))
                imported.append(n)
            continue
        missing.append((n,item,dest))
    newly=[]
    deferred=[]
    total=0
    for n,item,dest in missing:
        network=2*item["length"]
        if (len(newly)>=max_new_chunks
                or item["length"]>max_chunk_mib*_MIB
                or total+network>max_transfer_mib*_MIB):
            deferred.append(n)
            continue
        newly.append((n,item,dest))
        total+=network
    fetched=[]
    if execute and newly:
        receipts_dir.mkdir(parents=True,exist_ok=True)
        if save_published_root is not None:
            save_published_root.mkdir(parents=True,exist_ok=True)
        for n,item,dest in newly:
            local=None
            options={}
            if save_published_root is not None:
                local=(save_published_root/item["relative"]).resolve(strict=False)
                if (not local.is_relative_to(save_published_root.resolve())
                        or local.exists() or local.is_symlink()):
                    raise ValueError("refuse overwrite/escape saved original adjacency shard")
                local.parent.mkdir(parents=True,exist_ok=True)
                if local.parent.is_symlink():
                    raise ValueError("saved original adjacency chunk parent symlink")
                options["save_published_copy"]=local
            result=compare(
                manifest_path=manifest_path,original_index_path=original_index_path,
                dataset_revision=dataset_revision,manifest_sha256=manifest_sha256,
                original_index_sha256=original_index_sha256,
                section=section,chunk_index=n,
                max_chunk_mib=max_chunk_mib,opener=opener,**options)
            _check_receipt(result,row=item,number=n,section=section,
                           rev=dataset_revision,manifest_sha=manifest_sha256,
                           index_sha=original_index_sha256,
                           bin_size=metadata["original_bin_size_bytes"])
            if local is not None:
                if (result.get("saved_original_equal_published_copy")!=str(local)
                        or sha256(local.read_bytes()).hexdigest()!=result["published_shard_raw_sha256"]
                        or local.stat().st_size!=item["length"]):
                    raise ValueError("saved original adjacency bytes differ from original-range witness")
            with dest.open("x",encoding="utf-8") as out:
                json.dump(result,out,indent=2,sort_keys=True)
                out.write("\n")
            covered.append((n,item,dest))
            fetched.append(n)
    checked=sorted(n for n,_,_ in covered)
    complete=len(checked)==len(original)
    return {
        "version":"itir.zelph.original_lr_section_physical_http206.v1",
        "dataset_revision":dataset_revision,
        "manifest_sha256":manifest_sha256,
        "original_index_sha256":original_index_sha256,
        "section":section,
        "original_section_chunk_count":len(original),
        "original_section_packed_bytes":sum(r["length"] for _,r in original),
        "physically_verified_chunk_count":len(checked),
        "physically_verified_chunk_indices":checked,
        "planned_import_indices":planned_imports,
        "new_imported_chunk_indices":imported,
        "planned_new_http206_chunk_indices":[n for n,_,_ in newly],
        "new_http206_chunk_indices":fetched,
        "deferred_chunk_indices":deferred,
        "planned_two_source_bytes":total,
        "all_original_adjacency_section_packed_bytes_verified":complete,
        "every_selected_chunk_has_individual_http206_equality_receipt":True,
        "all_original_adjacency_nodes_decoded":False,
        "all_selected_root_routes_complete":False,
        "all_declared_query_words_closed":False,
        "original_full_bin_digest_verified":False,
        "native_p854_source_support_paid":False,
        "s29_persistence_paid":False,"edit_authority":False,
    }


def main()->int:
    p=argparse.ArgumentParser(description=__doc__)
    for key in ("manifest","original-index","receipts-dir"):
        p.add_argument("--"+key,type=Path,required=True)
    p.add_argument("--dataset-revision",required=True)
    p.add_argument("--manifest-sha256",required=True)
    p.add_argument("--original-index-sha256",required=True)
    p.add_argument("--section",choices=("left","right"),required=True)
    p.add_argument("--import-physical-receipts-dir",type=Path,action="append")
    p.add_argument("--save-published-root",type=Path)
    p.add_argument("--max-new-chunks",type=int,default=8)
    p.add_argument("--max-transfer-mib",type=int,default=1024)
    p.add_argument("--max-chunk-mib",type=int,default=256)
    p.add_argument("--execute",action="store_true")
    p.add_argument("--output",type=Path)
    args=p.parse_args()
    try:
        result=audit_adjacency_section(
            manifest_path=args.manifest,original_index_path=args.original_index,
            dataset_revision=args.dataset_revision,
            manifest_sha256=args.manifest_sha256,
            original_index_sha256=args.original_index_sha256,
            section=args.section,receipts_dir=args.receipts_dir,
            import_physical_receipts_dirs=args.import_physical_receipts_dir,
            save_published_root=args.save_published_root,
            max_new_chunks=args.max_new_chunks,
            max_transfer_mib=args.max_transfer_mib,
            max_chunk_mib=args.max_chunk_mib,execute=args.execute)
        raw=json.dumps(result,sort_keys=True,indent=2)+"\n"
        if args.output is None:
            print(raw,end="")
        else:
            with args.output.open("x",encoding="utf-8") as out:out.write(raw)
        return 0
    except (OSError,ValueError,TypeError,KeyError,json.JSONDecodeError) as e:
        print(json.dumps({"status":"blocked","reason":str(e),
                          "edit_authority":False}),file=sys.stderr)
        return 2


if __name__=="__main__":
    raise SystemExit(main())
