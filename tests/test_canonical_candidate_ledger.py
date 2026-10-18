import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from scripts.canonical_candidate_ledger import canonical_archive_path,select_candidate_ledger

class CandidateTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path=Path(self.tmp.name)/"chat_archive.sqlite"
        with sqlite3.connect(self.path) as db:
            db.execute("CREATE TABLE messages (canonical_thread_id TEXT)")
            db.executemany("INSERT INTO messages VALUES (?)",
                [("a",),("b",),("c",),("d",)])
    def test_canonical_default(self):
        with patch.dict("os.environ",{},clear=True):
            self.assertEqual(canonical_archive_path(),Path.home()/"chat_archive.sqlite")
    def test_exclusion_convergence_and_active_not_capped(self):
        evidence=[
            {"canonical_thread_id":"a","task_atom":"lemma A","formal_gap_receipts":["gap:1"],
             "outstanding_operation_receipt":"op:1"},
            {"canonical_thread_id":"b","task_atom":"lemma A","formal_gap_receipts":["gap:1"]},
            {"canonical_thread_id":"c","kind":"personal_admin","task_atom":"notes",
             "repo_receipts":["repo:1"]},
            {"canonical_thread_id":"d","kind":"vague_ideation"}]
        out=select_candidate_ledger(evidence,archive_db=str(self.path))
        decisions={r["canonical_thread_id"]:r for r in out["decisions"]}
        self.assertEqual(decisions["a"]["decision"],"admit")
        self.assertEqual(decisions["b"]["decision"],"merge")
        self.assertEqual(decisions["b"]["survivor_ref"],"a")
        self.assertEqual(decisions["c"]["decision"],"retire")
        self.assertEqual(decisions["d"]["decision"],"retire")
        self.assertEqual(out["active_outstanding_operations"],1)
        self.assertFalse(out["promotion"])
    def test_missing_source_and_no_evidence(self):
        out=select_candidate_ledger([
            {"canonical_thread_id":"missing","task_atom":"x","repo_receipts":["r"]},
            {"canonical_thread_id":"a","task_atom":"x"}],archive_db=str(self.path))
        self.assertEqual([r["reason"] for r in out["decisions"]],
                         ["canonical_source_missing","no_task_atom_or_formalizable_evidence"])
    def test_cap(self):
        with self.assertRaises(ValueError):
            select_candidate_ledger([],archive_db=str(self.path),max_proposals=20)

if __name__=="__main__":unittest.main()
