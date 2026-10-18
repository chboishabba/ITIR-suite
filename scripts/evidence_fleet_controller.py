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
CREATE TABLE IF NOT EXISTS fleet_archive_receipts (
 work_id TEXT NOT NULL, receipt_digest TEXT NOT NULL, conversation_id TEXT NOT NULL,
 source_ref TEXT NOT NULL, source_digest TEXT NOT NULL,
 archive_delta INTEGER NOT NULL, duplicates INTEGER NOT NULL,
 parsed_messages INTEGER NOT NULL, fetched_messages INTEGER NOT NULL,
 artifacts_digest TEXT NOT NULL, observed_at TEXT NOT NULL,
 PRIMARY KEY(work_id,receipt_digest)
);
CREATE TABLE IF NOT EXISTS fleet_gap_receipts (
 work_id TEXT NOT NULL, archive_receipt_digest TEXT NOT NULL,
 gap_digest TEXT NOT NULL, pnf_ref TEXT NOT NULL, gap_ref TEXT NOT NULL,
 gap_score REAL NOT NULL, observed_at TEXT NOT NULL,
 PRIMARY KEY(work_id,archive_receipt_digest,gap_digest),
 FOREIGN KEY(work_id,archive_receipt_digest)
 REFERENCES fleet_archive_receipts(work_id,receipt_digest)
);
"""

class EvidenceDeferred(Exception):
    """Required exact-thread evidence is not yet available."""

def _validate_work(db: sqlite3.Connection, work_id: str, conversation_id: str) -> None:
    if not isinstance(conversation_id, str) or not UUID_PATTERN.fullmatch(conversation_id):
        raise ValueError("canonical conversation UUID required")
    migrate(db)
    row = db.execute("SELECT parent_ids,evidence_refs FROM fleet_work_units WHERE work_id=?",
                     (work_id,)).fetchone()
    if row is None:
        raise KeyError(work_id)
    if conversation_id not in json.loads(row[0]) + json.loads(row[1]):
        raise ValueError("conversation ID is not attached to work unit")

def _failure(db: sqlite3.Connection, work_id: str, conversation_id: str, exc: Exception,
             *, phase: str = "read", archive_receipt_digest: str | None = None) -> dict:
    stage = "deferred" if isinstance(exc, EvidenceDeferred) else "failed"
    key = digest([work_id,conversation_id,phase,archive_receipt_digest,stage,type(exc).__name__])
    now = datetime.now(timezone.utc).isoformat()
    db.execute("""INSERT OR IGNORE INTO fleet_evidence_receipts
      (work_id,receipt_digest,conversation_id,stage,observed_at,error_class)
      VALUES (?,?,?,?,?,?)""",
      (work_id,key,conversation_id,stage,now,type(exc).__name__))
    db.commit()
    return {"stage":stage,"phase":phase,"archive_receipt_digest":archive_receipt_digest,
            "receipt_digest":key,"error_class":type(exc).__name__,"replayed":False}

def _compact_string(value: Any) -> bool:
    return isinstance(value,str) and 0 < len(value) <= 256

def _store_gap(db: sqlite3.Connection, work_id: str, conversation_id: str,
               archive_key: str, gap: dict) -> dict:
    expected = {"pnf_ref","gap_ref","gap_digest","gap_score","observed_at"}
    if set(gap) != expected or not all(_compact_string(gap[k]) for k in
        ("pnf_ref","gap_ref","gap_digest","observed_at")):
        raise ValueError("invalid gap receipt")
    score_value = gap["gap_score"]
    if (not isinstance(score_value,(float,int)) or isinstance(score_value,bool)
        or not 0 <= score_value <= 1000000):
        raise ValueError("invalid gap score")
    gap_key = digest([gap["pnf_ref"],gap["gap_ref"],gap["gap_digest"]])
    exists = db.execute("""SELECT 1 FROM fleet_gap_receipts
      WHERE work_id=? AND archive_receipt_digest=? AND gap_digest=?""",
      (work_id,archive_key,gap_key)).fetchone()
    if not exists:
        db.execute("""INSERT INTO fleet_gap_receipts
          (work_id,archive_receipt_digest,gap_digest,pnf_ref,gap_ref,gap_score,observed_at)
          VALUES (?,?,?,?,?,?,?)""",
          (work_id,archive_key,gap_key,gap["pnf_ref"],gap["gap_ref"],
           float(score_value),gap["observed_at"]))
        latest = db.execute("""SELECT gap_score FROM fleet_gap_receipts
          WHERE work_id=? ORDER BY observed_at DESC,gap_digest DESC LIMIT 1""",
          (work_id,)).fetchone()
        db.execute("UPDATE fleet_work_units SET priority=?,updated_at=CURRENT_TIMESTAMP WHERE work_id=?",
                   (latest[0],work_id))
        db.commit()
    return {"stage":"rescored","stages":["reduced","rescored"],"archive_receipt_digest":archive_key,
            "gap_receipt_digest":gap_key,"replayed":bool(exists)}

def refresh_work_evidence(db: sqlite3.Connection, work_id: str, conversation_id: str,
                          provider: Any) -> dict:
    """One exact-ID provider call; persist archive receipt before optional reduction.

    Modern provider returns {"archive": compact_archive, "gap": compact_gap|None,
    "gap_deferred": bool}. Legacy nine-field injected providers remain supported.
    """
    _validate_work(db,work_id,conversation_id)
    db.executescript(EVIDENCE_SCHEMA)
    try:
        evidence = provider(conversation_id)
        if not isinstance(evidence,dict):
            raise EvidenceDeferred("missing evidence")
        if "archive" not in evidence:
            # Compatibility for existing injected-provider regression tests.
            if set(evidence) != {"receipt_ref","source_ref","source_digest","archive_delta",
                "pnf_ref","gap_ref","gap_digest","gap_score","observed_at"}:
                raise EvidenceDeferred("incomplete legacy receipt")
            evidence = {"archive":dict(receipt_ref=evidence["receipt_ref"],
                source_ref=evidence["source_ref"],source_digest=evidence["source_digest"],
                archive_delta=evidence["archive_delta"],duplicates=0,
                parsed_messages=evidence["archive_delta"],
                fetched_messages=evidence["archive_delta"],
                artifacts_digest=digest([]),observed_at=evidence["observed_at"]),
                "gap":{k:evidence[k] for k in ("pnf_ref","gap_ref","gap_digest",
                    "gap_score","observed_at")},"gap_deferred":False}
        if set(evidence) != {"archive","gap","gap_deferred"}:
            raise ValueError("unexpected provider evidence fields")
        archive=evidence["archive"]
        required={"receipt_ref","source_ref","source_digest","archive_delta","duplicates",
                  "parsed_messages","fetched_messages","artifacts_digest","observed_at"}
        if not isinstance(archive,dict) or set(archive) != required:
            raise ValueError("invalid archive receipt fields")
        if not all(_compact_string(archive[k]) for k in
            ("receipt_ref","source_ref","source_digest","artifacts_digest","observed_at")):
            raise ValueError("invalid archive refs")
        if not all(type(archive[k]) is int and archive[k] >= 0 for k in
            ("archive_delta","duplicates","parsed_messages","fetched_messages")):
            raise ValueError("invalid archive counts")
        archive_key=digest([conversation_id,archive["receipt_ref"],archive["source_digest"]])
        exists=db.execute("SELECT 1 FROM fleet_archive_receipts WHERE work_id=? AND receipt_digest=?",
                          (work_id,archive_key)).fetchone()
        if not exists:
            db.execute("""INSERT INTO fleet_archive_receipts
              (work_id,receipt_digest,conversation_id,source_ref,source_digest,archive_delta,
               duplicates,parsed_messages,fetched_messages,artifacts_digest,observed_at)
              VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
              (work_id,archive_key,conversation_id,archive["source_ref"],archive["source_digest"],
               archive["archive_delta"],archive["duplicates"],archive["parsed_messages"],
               archive["fetched_messages"],archive["artifacts_digest"],archive["observed_at"]))
            db.commit()
        # Archive ingestion is durable independently of the optional gap phase.
        if evidence["gap"] is None:
            return {"stage":"deferred","phase":"gap","stages":["refreshed","ingested","deferred"],
                    "archive_stage":"ingested","archive_receipt_digest":archive_key,
                    "archive_replayed":bool(exists),"error_class":"EvidenceDeferred"}
        try:
            result=_store_gap(db,work_id,conversation_id,archive_key,evidence["gap"])
            result["stages"]=["refreshed","ingested"]+result["stages"]
            result["archive_replayed"]=bool(exists)
            return result
        except Exception as exc:
            return _failure(db,work_id,conversation_id,exc,phase="gap",
                            archive_receipt_digest=archive_key)
    except Exception as exc:
        return _failure(db,work_id,conversation_id,exc)

def exact_async_archive_provider(
    puller: str, archive_db: str, account: str, *,
    formal_file: str | None = None, slrw_path: str | None = None,
    runner: Any = None, gap_compare: Any = None,
) -> Any:
    """Existing exact async puller and optional comparator; never retry."""
    import subprocess
    import sys
    from pathlib import Path
    puller_path, db_path = Path(puller).expanduser(), Path(archive_db).expanduser()
    if not puller_path.is_file() or not db_path.is_file() or not account:
        raise EvidenceDeferred("archive or puller prerequisite missing")
    def provider(conversation_id: str) -> dict:
        if not UUID_PATTERN.fullmatch(conversation_id):
            raise ValueError("canonical conversation UUID required")
        cmd=[sys.executable,str(puller_path),"--ids",conversation_id,
             "--db",str(db_path),"--account",account,"--engine","async",
             "--mode","pull","--concurrency","1","--no-progress","--json",
             "--no-skip-existing"]
        try:
            completed=(runner or subprocess.run)(cmd,capture_output=True,text=True,
                                                  timeout=240,check=False)
        except (subprocess.TimeoutExpired,OSError) as exc:
            raise EvidenceDeferred("exact async read unavailable") from exc
        if completed.returncode:
            raise EvidenceDeferred("exact async pull rejected or unavailable")
        try:
            summary=json.loads(completed.stdout)
            status=summary["async"]
            ingest=summary["ingest"]
            if (summary.get("requested_targets") != 1 or
                summary.get("selected_id_filters") != 1 or
                status["total"] != 1 or status["ok"] != 1 or status["failures"] != 0):
                raise EvidenceDeferred("exact identity/read failure")
            counts={k:ingest[k] for k in ("inserted","duplicates","parsed_messages")}
            if not all(type(v) is int and v >= 0 for v in counts.values()):
                raise ValueError("invalid ingest counts")
            fetched=status["messages"]
            if type(fetched) is not int or fetched < 0:
                raise ValueError("invalid fetched count")
            source=summary["source_id"]
            if not _compact_string(source):
                raise ValueError("invalid source ID")
            artifacts=ingest["artifacts"]
            if not isinstance(artifacts,(dict,list,int)):
                raise ValueError("invalid artifact receipt")
        except (KeyError,TypeError,ValueError,json.JSONDecodeError) as exc:
            raise EvidenceDeferred("missing or invalid canonical ingest receipt") from exc
        observed=datetime.now(timezone.utc).isoformat()
        immutable=digest([conversation_id,source,counts,artifacts])
        archive=dict(receipt_ref="ingest:"+immutable[:48],source_ref="pull:"+source,
            source_digest=immutable,archive_delta=counts["inserted"],
            duplicates=counts["duplicates"],parsed_messages=counts["parsed_messages"],
            fetched_messages=fetched,artifacts_digest=digest(artifacts),
            observed_at=observed)
        result={"archive":archive,"gap":None,"gap_deferred":True}
        if not formal_file or not slrw_path:
            return result
        if not Path(formal_file).is_file() or not Path(slrw_path).is_file():
            return result
        try:
            if gap_compare is None:
                from re_gpt.gap_comparator import ExactGapComparator
                gap=ExactGapComparator(slrw_path).compare(conversation_id,formal_file)
            else:
                gap=gap_compare(conversation_id,formal_file,slrw_path)
            result["gap"]=dict(pnf_ref="slrw:"+digest(str(slrw_path))[:48],
                gap_ref="formal:"+digest(str(formal_file))[:48],
                gap_digest=digest([gap.unmatched_informal_factors,
                    gap.unmatched_formal_factors,gap.matched_semantic_factors]),
                gap_score=float(gap.unmatched_informal_factors+gap.unmatched_formal_factors),
                observed_at=observed)
            result["gap_deferred"]=False
        except Exception:
            # Preserve archive success; classify gap failure at controller boundary.
            result["gap"]={"invalid":"comparator failure"}
            result["gap_deferred"]=False
        return result
    return provider

def attach_gap_to_archive(db: sqlite3.Connection, work_id: str, conversation_id: str,
                          archive_receipt_digest: str, formal_file: str, slrw_path: str,
                          gap_compare: Any = None) -> dict:
    """Explicit offline gap-only action; never invoke the archive puller."""
    from pathlib import Path
    _validate_work(db,work_id,conversation_id)
    db.executescript(EVIDENCE_SCHEMA)
    found=db.execute("""SELECT 1 FROM fleet_archive_receipts
      WHERE work_id=? AND conversation_id=? AND receipt_digest=?""",
      (work_id,conversation_id,archive_receipt_digest)).fetchone()
    if not found:
        raise ValueError("unknown canonical archive receipt")
    if not formal_file or not slrw_path or not Path(formal_file).is_file() or not Path(slrw_path).is_file():
        return {"stage":"deferred","phase":"gap","archive_receipt_digest":archive_receipt_digest}
    try:
        if gap_compare is None:
            from re_gpt.gap_comparator import ExactGapComparator
            gap=ExactGapComparator(slrw_path).compare(conversation_id,formal_file)
        else:
            gap=gap_compare(conversation_id,formal_file,slrw_path)
        now=datetime.now(timezone.utc).isoformat()
        return _store_gap(db,work_id,conversation_id,archive_receipt_digest,
            dict(pnf_ref="slrw:"+digest(str(slrw_path))[:48],
                 gap_ref="formal:"+digest(str(formal_file))[:48],
                 gap_digest=digest([gap.unmatched_informal_factors,
                     gap.unmatched_formal_factors,gap.matched_semantic_factors]),
                 gap_score=float(gap.unmatched_informal_factors+gap.unmatched_formal_factors),
                 observed_at=now))
    except Exception as exc:
        return _failure(db,work_id,conversation_id,exc,phase="gap",
                        archive_receipt_digest=archive_receipt_digest)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--db",required=True)
    mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--plan",action="store_true")
    mode.add_argument("--refresh-work",metavar="WORK_ID")
    parser.add_argument("--conversation-id")
    parser.add_argument("--puller")
    parser.add_argument("--archive-db")
    parser.add_argument("--account",default="main")
    parser.add_argument("--formal-file")
    parser.add_argument("--slrw")
    parser.add_argument("--gap-archive-receipt",help="offline gap-only receipt digest; no fetch")
    parser.add_argument("--limit",type=int,default=3)
    args=parser.parse_args()
    with sqlite3.connect(args.db) as db:
        if args.plan:
            result=plan(db,args.limit)
        else:
            if not args.conversation_id or not UUID_PATTERN.fullmatch(args.conversation_id):
                parser.error("--conversation-id must be an explicit canonical UUID")
            if not args.gap_archive_receipt and (not args.puller or not args.archive_db):
                parser.error("--puller and --archive-db required for refresh")
            # Guard work-unit membership before initializing any provider or session.
            migrate(db)
            row=db.execute("SELECT parent_ids,evidence_refs FROM fleet_work_units WHERE work_id=?",
                           (args.refresh_work,)).fetchone()
            if row is None: raise KeyError(args.refresh_work)
            if args.conversation_id not in json.loads(row[0])+json.loads(row[1]):
                parser.error("conversation UUID not attached to work unit")
            if args.gap_archive_receipt:
                if not args.formal_file or not args.slrw:
                    parser.error("--formal-file and --slrw required for offline gap")
                result=attach_gap_to_archive(db,args.refresh_work,args.conversation_id,
                    args.gap_archive_receipt,args.formal_file,args.slrw)
            else:
                provider=exact_async_archive_provider(args.puller,args.archive_db,args.account,
                    formal_file=args.formal_file,slrw_path=args.slrw)
                result=refresh_work_evidence(db,args.refresh_work,args.conversation_id,provider)
        print(json.dumps(result,indent=2))
if __name__ == "__main__": main()
