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


# Read-only evidence lifecycle. Providers return metadata, never transcript bodies.
import re
from datetime import datetime, timezone

UUID_PATTERN = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$", re.I)
STAGES = ("refreshed", "ingested", "reduced", "rescored", "deferred", "failed")
EVIDENCE_SCHEMA = """
CREATE TABLE IF NOT EXISTS fleet_evidence_receipts (
 work_id TEXT NOT NULL, receipt_digest TEXT NOT NULL, conversation_id TEXT NOT NULL,
 stage TEXT NOT NULL, source_ref TEXT, source_digest TEXT,
 archive_delta INTEGER, pnf_ref TEXT, gap_ref TEXT, gap_digest TEXT,
 gap_score REAL, observed_at TEXT NOT NULL, error_class TEXT,
 PRIMARY KEY(work_id,receipt_digest),
 FOREIGN KEY(work_id) REFERENCES fleet_work_units(work_id)
);
"""

class EvidenceDeferred(Exception):
    """Required exact-thread evidence is not yet available."""

def refresh_work_evidence(db: sqlite3.Connection, work_id: str, conversation_id: str, provider: Any) -> dict:
    """Call one injected read-only exact-ID provider and store metadata only.

    provider(conversation_id) must return a dict with receipt_ref, source_ref,
    source_digest, archive_delta, pnf_ref, gap_ref, gap_digest, gap_score,
    observed_at. It must not return bodies, nor perform account writes.
    """
    migrate(db)
    db.executescript(EVIDENCE_SCHEMA)
    row = db.execute("SELECT parent_ids,evidence_refs,state,priority FROM fleet_work_units WHERE work_id=?",
                     (work_id,)).fetchone()
    if row is None:
        raise KeyError(work_id)
    parents, refs = json.loads(row[0]), json.loads(row[1])
    if not isinstance(conversation_id, str) or not UUID_PATTERN.fullmatch(conversation_id):
        raise ValueError("canonical conversation UUID required")
    if conversation_id not in parents and conversation_id not in refs:
        raise ValueError("conversation ID is not attached to work unit")
    now = datetime.now(timezone.utc).isoformat()
    try:
        evidence = provider(conversation_id)
        if not isinstance(evidence, dict):
            raise EvidenceDeferred("missing metadata")
        required = ("receipt_ref","source_ref","source_digest","archive_delta",
                    "pnf_ref","gap_ref","gap_digest","gap_score","observed_at")
        if any(k not in evidence for k in required):
            raise EvidenceDeferred("incomplete evidence metadata")
        if set(evidence) != set(required):
            raise ValueError("unexpected evidence fields (potential body material)")
        for key in ("receipt_ref","source_ref","source_digest","pnf_ref","gap_ref","gap_digest","observed_at"):
            if not isinstance(evidence[key], str) or not evidence[key] or len(evidence[key]) > 256:
                raise ValueError("invalid compact evidence reference")
        if not isinstance(evidence["archive_delta"], int) or isinstance(evidence["archive_delta"], bool) or evidence["archive_delta"] < 0:
            raise ValueError("invalid archive delta")
        if not isinstance(evidence["gap_score"], (int,float)) or isinstance(evidence["gap_score"], bool) or not 0 <= evidence["gap_score"] <= 1000000:
            raise ValueError("invalid gap score")
        receipt_id = digest([conversation_id,evidence["receipt_ref"]])
        previous = db.execute("SELECT stage FROM fleet_evidence_receipts WHERE work_id=? AND receipt_digest=?",
                              (work_id,receipt_id)).fetchone()
        if previous:
            return {"stage":previous[0],"receipt_digest":receipt_id,"replayed":True}
        stage = "rescored"
        db.execute("""INSERT INTO fleet_evidence_receipts
          (work_id,receipt_digest,conversation_id,stage,source_ref,source_digest,archive_delta,
           pnf_ref,gap_ref,gap_digest,gap_score,observed_at)
          VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
          (work_id,receipt_id,conversation_id,stage,evidence["source_ref"],evidence["source_digest"],
           evidence["archive_delta"],evidence["pnf_ref"],evidence["gap_ref"],
           evidence["gap_digest"],float(evidence["gap_score"]),evidence["observed_at"]))
        # No mutation/execution state transition: priority is a deterministic projection
        # of the most recent evidence score; ties break by digest.
        scores = db.execute("""SELECT gap_score FROM fleet_evidence_receipts
          WHERE work_id=? AND stage='rescored'
          ORDER BY observed_at DESC, receipt_digest DESC LIMIT 1""",(work_id,)).fetchone()
        db.execute("UPDATE fleet_work_units SET priority=?,updated_at=CURRENT_TIMESTAMP WHERE work_id=?",
                   (scores[0],work_id))
        db.commit()
        return {"stage":stage,"stages":["refreshed","ingested","reduced","rescored"],
                "receipt_digest":receipt_id,"replayed":False}
    except (EvidenceDeferred, Exception) as exc:
        stage = "deferred" if isinstance(exc,EvidenceDeferred) else "failed"
        error_class = type(exc).__name__
        receipt_id = digest([work_id,conversation_id,stage,error_class])
        db.execute("""INSERT OR IGNORE INTO fleet_evidence_receipts
          (work_id,receipt_digest,conversation_id,stage,observed_at,error_class)
          VALUES (?,?,?,?,?,?)""",(work_id,receipt_id,conversation_id,stage,now,error_class))
        db.commit()
        return {"stage":stage,"receipt_digest":receipt_id,"error_class":error_class,"replayed":False}


def exact_async_archive_provider(
    puller: str, archive_db: str, account: str, *,
    formal_file: str | None = None, slrw_path: str | None = None,
    runner: Any = None, gap_compare: Any = None,
) -> Any:
    """Factory for one explicit existing pull_to_structurer.py async exact-ID invocation.

    Subprocess isolates puller's asyncio.run from an existing event loop.
    Runner and comparator are injectable for token-free tests. No retries.
    """
    import subprocess
    import sys
    from pathlib import Path
    puller_path, db_path = Path(puller).expanduser(), Path(archive_db).expanduser()
    if not puller_path.is_file() or not db_path.is_file() or not account:
        raise EvidenceDeferred("archive or puller prerequisite missing")
    def provider(conversation_id: str) -> dict:
        if not UUID_PATTERN.fullmatch(conversation_id):
            raise ValueError("canonical conversation UUID required")
        cmd = [sys.executable, str(puller_path), "--ids", conversation_id,
               "--db", str(db_path), "--account", account,
               "--engine", "async", "--mode", "pull", "--concurrency", "1",
               "--no-progress", "--json", "--no-skip-existing"]
        run = runner or subprocess.run
        try:
            completed = run(cmd, capture_output=True, text=True, timeout=240, check=False)
        except (subprocess.TimeoutExpired, OSError) as exc:
            raise EvidenceDeferred("exact async read unavailable") from exc
        if completed.returncode != 0:
            raise EvidenceDeferred("exact async pull rejected or unavailable")
        try:
            summary = json.loads(completed.stdout)
            async_status = summary["async"]
            if (summary.get("requested_targets") != 1 or
                summary.get("selected_id_filters") != 1 or
                async_status["total"] != 1 or async_status["ok"] != 1 or
                async_status["failures"] != 0 or "ingest" not in summary):
                raise EvidenceDeferred("exact fetch rejected, identity invalid, or ingest missing")
            source_id = summary["source_id"]
            count = async_status["messages"]
            if not isinstance(count,int) or count < 0:
                raise ValueError("invalid message count")
        except (KeyError, TypeError, json.JSONDecodeError, ValueError) as exc:
            raise EvidenceDeferred("invalid exact fetch receipt") from exc
        if not formal_file or not slrw_path:
            raise EvidenceDeferred("explicit formal file and SLRW required for gap score")
        if not Path(formal_file).is_file() or not Path(slrw_path).is_file():
            raise EvidenceDeferred("formal or SLRW prerequisite missing")
        if gap_compare is None:
            # Reuse the existing owner implementation, never parse formal bodies here.
            from re_gpt.gap_comparator import ExactGapComparator
            gap = ExactGapComparator(slrw_path).compare(conversation_id,formal_file)
        else:
            gap = gap_compare(conversation_id,formal_file,slrw_path)
        observed = datetime.now(timezone.utc).isoformat()
        return dict(receipt_ref="ingest:"+digest([conversation_id,source_id])[:48],
            source_ref="pull:"+source_id,source_digest=digest([conversation_id,source_id,count]),
            archive_delta=count,pnf_ref="slrw:"+digest(str(slrw_path))[:48],
            gap_ref="formal:"+digest(str(formal_file))[:48],
            gap_digest=digest([gap.unmatched_informal_factors,gap.unmatched_formal_factors,
                               gap.matched_semantic_factors]),
            gap_score=float(gap.unmatched_informal_factors+gap.unmatched_formal_factors),
            observed_at=observed)
    return provider

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--db",required=True)
    parser.add_argument("--plan",action="store_true",required=True)
    parser.add_argument("--limit",type=int,default=3)
    args=parser.parse_args()
    with sqlite3.connect(args.db) as db: print(json.dumps(plan(db,args.limit),indent=2))
if __name__ == "__main__": main()
