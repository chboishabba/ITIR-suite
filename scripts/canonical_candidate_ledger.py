"""Evidence-first, canonical-archive-verified AO candidate ledger.

No re-gpt history queries, title ranking, ChatGPT submission or daemon.
"""
from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Any, Mapping, Sequence

def canonical_archive_path(explicit: str | None = None) -> Path:
    return Path(explicit or os.environ.get("ITIR_CANONICAL_CHAT_ARCHIVE")
                or "~/chat_archive.sqlite").expanduser()

def _canonical_threads(path: Path, ids: Sequence[str]) -> set[str]:
    if not path.is_file():
        raise FileNotFoundError(f"canonical archive unavailable: {path}")
    with sqlite3.connect(f"file:{path}?mode=ro",uri=True) as db:
        # Same producer-owned structurer messages table used by chat_archive_batch.
        return {str(row[0]) for row in db.execute(
            "SELECT DISTINCT canonical_thread_id FROM messages WHERE canonical_thread_id IN ("+
            ",".join("?" for _ in ids)+")",tuple(ids))} if ids else set()

def select_candidate_ledger(
    evidence: Sequence[Mapping[str,Any]], *,
    archive_db: str | None = None,
    archive_lookup=None, max_proposals: int = 4,
) -> dict[str,Any]:
    if not 1 <= max_proposals <= 4:
        raise ValueError("max_proposals must be 1..4")
    ids=[str(row.get("canonical_thread_id") or "") for row in evidence]
    if any(not x for x in ids):
        raise ValueError("every candidate needs canonical_thread_id")
    present=(archive_lookup or _canonical_threads)(canonical_archive_path(archive_db),ids)
    candidates=[]
    for item in evidence:
        tid=str(item["canonical_thread_id"])
        refs=[str(x) for x in item.get("evidence_refs",[]) if x]
        task=str(item.get("task_atom") or "").strip()
        formal=[str(x) for x in item.get("formal_gap_receipts",[]) if x]
        repo=[str(x) for x in item.get("repo_receipts",[]) if x]
        pnf=[str(x) for x in item.get("pnf_receipts",[]) if x]
        kind=str(item.get("kind") or "unclassified")
        explicit=item.get("explicit_promotion") is True
        if tid not in present:
            decision,reason="park","canonical_source_missing"
        elif kind in {"generic_chat","personal_admin","vague_ideation"} and not explicit:
            decision,reason="retire","nonimplementation_corpus"
        elif not task or not (formal or repo or pnf) and not explicit:
            decision,reason="park","no_task_atom_or_formalizable_evidence"
        else:
            decision,reason="admit","typed_evidence_and_task"
        candidates.append({"canonical_thread_id":tid,"task_atom":task,
            "evidence_refs":sorted(set(refs)),"formal_gap_receipts":sorted(set(formal)),
            "repo_receipts":sorted(set(repo)),"pnf_receipts":sorted(set(pnf)),
            "decision":decision,"reason":reason,
            "active":bool(item.get("outstanding_operation_receipt")),
            "outstanding_operation_receipt":item.get("outstanding_operation_receipt")})
    # Exact task atom + same evidence class may converge. Similarity alone does not merge.
    survivors={}
    for c in sorted(candidates,key=lambda c:(c["task_atom"],c["canonical_thread_id"])):
        if c["decision"]!="admit":continue
        key=(c["task_atom"],tuple(c["formal_gap_receipts"]),
             tuple(c["repo_receipts"]),tuple(c["pnf_receipts"]))
        if key in survivors:
            c["decision"]="merge"
            c["reason"]="exact_task_and_evidence_equivalence"
            c["survivor_ref"]=survivors[key]
        else:survivors[key]=c["canonical_thread_id"]
    admitted=[c for c in candidates if c["decision"]=="admit"]
    admitted.sort(key=lambda c:(-len(c["formal_gap_receipts"]),
         -len(c["repo_receipts"]),-len(c["pnf_receipts"]),c["canonical_thread_id"]))
    return {"schema":"itir.canonical_candidate_ledger.v1",
        "archive_db":str(canonical_archive_path(archive_db)),
        "authority":"evidence_only","promotion":False,
        "active_outstanding_operations":sum(c["active"] for c in candidates),
        "local_response_workers_default":20,
        "proposals":admitted[:max_proposals],
        "decisions":candidates}
