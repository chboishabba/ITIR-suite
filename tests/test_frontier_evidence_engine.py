"""Metadata-only AO frontier fixture and registry regression."""
from __future__ import annotations

import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "itir-mcp" / "src"
sys.path.insert(0, str(SRC))

from itir_mcp.frontier_evidence import build_frontier, transition_roster  # noqa: E402
from itir_mcp.registry import build_default_registry  # noqa: E402

COLUMNS = (
    "message_id canonical_thread_id platform account_id ts role text title source_id "
    "source_thread_id source_message_id source_path source_bucket provenance_json "
    "node_id parent_node_id branch_membership tool_kind citation_token filename "
    "mime_type asset_pointer body_storage_ref source_scope visibility"
).split()


class FrontierTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.archive = Path(temp.name) / "canonical.sqlite"
        self.roster = Path(temp.name) / "roster.sqlite"
        with sqlite3.connect(self.archive) as db:
            db.execute("CREATE TABLE messages (" + ",".join(c + " TEXT" for c in COLUMNS) + ")")
            for i in range(6):
                tid = f"canonical-{i}"
                db.execute(
                    "INSERT INTO messages (message_id, canonical_thread_id, platform, account_id, "
                    "ts, role, text, source_thread_id) VALUES (?,?,?,?,?,?,?,?)",
                    (str(i), tid, "chatgpt", "main", f"2026-10-{i + 10:02d}",
                     "assistant", "SECRET TRANSCRIPT BODY", f"re-gpt-{i}"),
                )
        self.evidence = [
            {"canonical_thread_id": "canonical-0", "task_atom": "prove alpha",
             "kind": "formal", "formal_gap_receipts": ["formal:alpha"],
             "repo_receipts": ["repo:alpha"], "evidence_refs": ["sha256:alpha"]},
            {"canonical_thread_id": "canonical-1", "task_atom": "prove alpha",
             "kind": "formal", "formal_gap_receipts": ["formal:alpha"],
             "repo_receipts": ["repo:alpha"], "evidence_refs": ["sha256:beta"]},
            {"canonical_thread_id": "canonical-2", "task_atom": "",
             "kind": "personal_admin"},
            {"canonical_thread_id": "canonical-3", "task_atom": "vague idea",
             "kind": "vague_ideation"},
            {"canonical_thread_id": "canonical-4", "task_atom": "prove beta",
             "kind": "formal", "formal_artifact": "DASHI/Beta.agda"},
        ]

    def test_metadata_only_ledger_merge_and_exclusion(self):
        result = build_frontier(archive_db=str(self.archive), evidence=self.evidence,
                                max_evaluated=5, roster_db=str(self.roster))
        self.assertEqual(result["schema"], "itir.ao.frontier_evidence.v1")
        self.assertEqual(result["enumerated_threads"], 6)
        decisions = {x["canonical_thread_id"]: x["decision"] for x in result["decisions"]}
        self.assertEqual(decisions["canonical-0"], "admit")
        self.assertEqual(decisions["canonical-1"], "merge")
        self.assertEqual(decisions["canonical-2"], "retire")
        self.assertEqual(decisions["canonical-3"], "retire")
        self.assertEqual(decisions["canonical-4"], "park")
        self.assertEqual(len(result["comparison_receipts"]), 10)
        self.assertTrue(any(x["reason"] == "gap_evaluator_unavailable" for x in result["abstentions"]))
        self.assertNotIn("SECRET TRANSCRIPT BODY", json.dumps(result))
        self.assertEqual(result["proposals"][0]["source_thread_id"], "re-gpt-0")
        with sqlite3.connect(self.roster) as db:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM frontier_roster").fetchone()[0], 5)

    def test_fresh_merge_receipt_and_idempotent_replay(self):
        result = build_frontier(archive_db=str(self.archive), evidence=self.evidence,
                                max_evaluated=5, roster_db=str(self.roster))
        first = next(r for r in result["roster"]
                     if r["canonical_thread_id"] == "canonical-1")
        self.assertEqual(first["next_state"], "merged")
        self.assertIsNone(first["previous_state"])
        with sqlite3.connect(self.roster) as db:
            self.assertEqual(
                db.execute("SELECT previous_state FROM frontier_transitions "
                           "WHERE receipt_id=?", (first["receipt_id"],)).fetchone(),
                (None,),
            )
            count_before = db.execute(
                "SELECT COUNT(*) FROM frontier_transitions"
            ).fetchone()[0]
        repeated = build_frontier(archive_db=str(self.archive), evidence=self.evidence,
                                  max_evaluated=5, roster_db=str(self.roster))
        second = next(r for r in repeated["roster"]
                      if r["canonical_thread_id"] == "canonical-1")
        self.assertEqual(first, second)
        with sqlite3.connect(self.roster) as db:
            self.assertEqual(
                db.execute("SELECT COUNT(*) FROM frontier_transitions").fetchone()[0],
                count_before,
            )

    def test_injected_gap_receipt_and_bounded_selection(self):
        calls = []
        def evaluator(tid, artifact, meta):
            calls.append((tid, artifact))
            return {"gap": "open", "formal_ref": artifact, "count": meta["message_count"]}
        result = build_frontier(archive_db=str(self.archive), evidence=self.evidence,
                                max_evaluated=5, gap_evaluator=evaluator)
        self.assertEqual(calls, [("canonical-4", "DASHI/Beta.agda")])
        self.assertEqual(len(result["gap_receipts"]), 1)
        self.assertEqual(len(result["proposals"]), 2)
        capped = build_frontier(archive_db=str(self.archive), evidence=self.evidence,
                                max_evaluated=1)
        self.assertTrue(capped["truncation"]["candidate_limit_hit"])
        self.assertEqual(capped["evaluated_threads"], 1)

    def test_roster_transition_and_conflict(self):
        first = transition_roster(str(self.roster), "canonical-0", "re-gpt-0",
                                  "candidate", "discovered")
        second = transition_roster(str(self.roster), "canonical-0", "re-gpt-0",
                                   "processing", "approved", ["receipt:1"])
        self.assertNotEqual(first["receipt_id"], second["receipt_id"])
        with self.assertRaises(ValueError):
            transition_roster(str(self.roster), "canonical-0", "other-source",
                              "parked", "invalid")
        with self.assertRaises(ValueError):
            transition_roster(str(self.roster), "canonical-0", "re-gpt-0",
                              "candidate", "invalid")

    def test_registry_and_production_cwd_import(self):
        registry = build_default_registry()
        self.assertIn("itir.ao.frontier_evidence", [x.name for x in registry.list_tools()])
        result = registry.invoke("itir.ao.frontier_evidence", {
            "archive_db": str(self.archive), "evidence": self.evidence, "max_evaluated": 5,
        })
        self.assertTrue(result["ok"], result)
        snippet = (
            "from itir_mcp.registry import build_default_registry; import sys; "
            "r=build_default_registry().invoke('itir.ao.frontier_evidence', "
            "{'archive_db':sys.argv[1],'evidence':["
            "{'canonical_thread_id':'canonical-0','task_atom':'prove alpha',"
            "'formal_gap_receipts':['formal:alpha']}]}); "
            "assert r['ok'], r"
        )
        proc = subprocess.run(
            [sys.executable, "-c", snippet, str(self.archive)],
            cwd=ROOT / "itir-mcp", env={**os.environ, "PYTHONPATH": str(SRC)},
            capture_output=True, text=True, check=False, timeout=30,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)


if __name__ == "__main__":
    unittest.main()
