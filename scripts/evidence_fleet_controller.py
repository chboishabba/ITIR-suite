"""Bounded evidence-first fleet planning. No network or conversation mutation."""
from __future__ import annotations
import argparse
import hashlib
import json
import sqlite3
from dataclasses import dataclass
from typing import Any

KINDS = ("revived_from", "synthesized_from", "supersedes", "corroborates")
SCHEMA = """
CREATE TABLE IF NOT EXISTS conversation_lineage_edges (
 child_id TEXT NOT NULL, parent_id TEXT NOT NULL,
 edge_kind TEXT NOT NULL CHECK(edge_kind IN ('revived_from','synthesized_from','supersedes','corroborates')),
 evidence_digest TEXT NOT NULL, recorded_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
 PRIMARY KEY(child_id,parent_id,edge_kind,evidence_digest)
);
CREATE TABLE IF NOT EXISTS fleet_work_units (
 work_id TEXT PRIMARY KEY, gap_key TEXT NOT NULL, evidence_refs TEXT NOT NULL,
 parent_ids TEXT NOT NULL, state TEXT NOT NULL DEFAULT 'proposed',
 priority REAL NOT NULL DEFAULT 0, receipt_refs TEXT NOT NULL DEFAULT '[]',
 updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""
def migrate(db: sqlite3.Connection) -> None:
    db.executescript(SCHEMA)

def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

def lineage(db: sqlite3.Connection, child: str, parents: list[str], kind: str, evidence: Any) -> None:
    if kind not in KINDS: raise ValueError("invalid lineage kind")
    if not child or not parents or child in parents: raise ValueError("invalid lineage")
    migrate(db)
    for parent in sorted(set(parents)):
        db.execute("INSERT OR IGNORE INTO conversation_lineage_edges(child_id,parent_id,edge_kind,evidence_digest) VALUES (?,?,?,?)",
                   (child,parent,kind,digest(evidence)))
    db.commit()

def packet(parents: list[dict], next_step: str) -> dict:
    if not next_step.strip(): raise ValueError("testable next step required")
    selected = []
    for p in sorted(parents, key=lambda x: x["conversation_id"]):
        selected.append({k:p.get(k, [] if k not in ("conversation_id","title") else "")
                         for k in ("conversation_id","title","atoms","pnf_factors","gap_residues","formal_refs","pr_commits","message_refs")})
    if len(selected) < 2 or len({p["conversation_id"] for p in selected}) != len(selected):
        raise ValueError("two distinct provenance parents required")
    return {"parents":selected,"next_testable_step":next_step,"evidence_digest":digest([selected,next_step])}

def score(a: dict, b: dict) -> dict:
    def shared(key):
        return sorted(set(a.get(key, [])) & set(b.get(key, [])))
    pnf, formal, gaps, prs = (shared(k) for k in ("pnf_factors","formal_refs","gap_residues","pr_commits"))
    complementary = bool(set(a.get("premises", [])) ^ set(b.get("premises", []))) and bool(pnf or formal or gaps)
    test = bool(a.get("next_testable_step") or b.get("next_testable_step"))
    recency = int(bool(a.get("recent") and b.get("recent")))
    value = 3*len(pnf)+4*len(formal)+5*len(gaps)+4*len(prs)+2*complementary+recency+2*test
    anchored = bool(pnf or formal or gaps or prs)
    action = "synthesize" if anchored and test and value >= 8 and complementary else ("continue" if anchored and test else "park")
    return {"action":action,"score":value,"reasons":{"pnf":pnf,"formal":formal,"gaps":gaps,"prs":prs,
      "complementary":complementary,"recent":bool(recency),"testable":test},
      "rejection": None if action != "park" else "no anchored, testable shared task/gap"}

def upsert_work(db: sqlite3.Connection, gap_key: str, parents: list[str], refs: list[str], priority: float) -> str:
    migrate(db)
    parents, refs = sorted(set(parents)), sorted(set(refs))
    if not gap_key or not parents or not refs: raise ValueError("work requires gap, parents and evidence")
    key = digest([gap_key,parents])
    db.execute("""INSERT INTO fleet_work_units(work_id,gap_key,evidence_refs,parent_ids,priority)
      VALUES (?,?,?,?,?) ON CONFLICT(work_id) DO UPDATE SET
      evidence_refs=excluded.evidence_refs, priority=excluded.priority, updated_at=CURRENT_TIMESTAMP""",
      (key,gap_key,json.dumps(refs),json.dumps(parents),priority))
    db.commit()
    return key

def plan(db: sqlite3.Connection, limit: int = 3) -> list[dict]:
    if limit not in (2,3,4): raise ValueError("dispatch cap must be 2..4")
    migrate(db)
    rows=db.execute("""SELECT work_id,gap_key,evidence_refs,parent_ids,priority FROM fleet_work_units
      WHERE state='proposed' ORDER BY priority DESC,work_id LIMIT ?""",(limit,)).fetchall()
    return [dict(zip(("work_id","gap_key","evidence_refs","parent_ids","priority"),r)) for r in rows]

def lifecycle() -> tuple[str,...]:
    return ("exact_conversation_refresh","incremental_archive_ingest","pnf_exact_gap_reduce","scheduler_rescore")

def validate_transport(write_transport: str, dom_fallback: bool) -> None:
    if write_transport != "async" or dom_fallback is not False:
        raise ValueError("direct async transport only; DOM fallback forbidden")

def attach_receipt(db: sqlite3.Connection, work_id: str, kind: str, ref: str) -> None:
    if kind not in ("pr","test","colab","formal") or not ref: raise ValueError("independent receipt required")
    migrate(db)
    row=db.execute("SELECT receipt_refs FROM fleet_work_units WHERE work_id=?",(work_id,)).fetchone()
    if row is None: raise KeyError(work_id)
    receipts=json.loads(row[0])
    receipt={"kind":kind,"ref":ref}
    if receipt not in receipts: receipts.append(receipt)
    db.execute("UPDATE fleet_work_units SET receipt_refs=?,updated_at=CURRENT_TIMESTAMP WHERE work_id=?",
               (json.dumps(receipts,sort_keys=True),work_id))
    db.commit()

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--db",required=True)
    parser.add_argument("--plan",action="store_true",required=True)
    parser.add_argument("--limit",type=int,default=3)
    args=parser.parse_args()
    with sqlite3.connect(args.db) as db: print(json.dumps(plan(db,args.limit),indent=2))
if __name__ == "__main__": main()
