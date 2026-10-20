"""Source-bound operation candidates and typed frontier holds; no message body reads."""
from __future__ import annotations

import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "itir-mcp" / "src"))

from itir_mcp.frontier_reference_validation import (  # noqa: E402
    completed_operation_candidates, validate_typed_references,
)
from itir_mcp.frontier_evidence import build_frontier  # noqa: E402
from itir_mcp.registry import build_default_registry  # noqa: E402


class TypedReferenceTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.archive = Path(temp.name) / "archive.sqlite"
        self.transport = Path(temp.name) / "transport.sqlite"
        with sqlite3.connect(self.archive) as db:
            db.execute("CREATE TABLE messages (canonical_thread_id TEXT,source_thread_id TEXT,"
                       "account_id TEXT,platform TEXT,ts TEXT,role TEXT,text TEXT)")
            for tid, source in (("a", "source-a"), ("b", "source-b"),
                                ("c", "source-c"), ("d", "source-c")):
                db.execute("INSERT INTO messages VALUES (?,?,?,?,?,?,?)",
                           (tid, source, "main", "chatgpt", "2026-10-20", "user",
                            "PRIVATE RAW MESSAGE"))
        with sqlite3.connect(self.transport) as db:
            db.execute("CREATE TABLE mutation_attempts (operation_id TEXT,conversation_id TEXT,"
                       "operation TEXT,state TEXT,started_at REAL,completed_at REAL,"
                       "user_node_id TEXT,assistant_node_id TEXT)")
            for row in (("op1", "source-a", "continue", "complete", 1, 2, "u1", "a1"),
                        ("op2", "source-b", "continue", "async_starting", 3, None, None, None),
                        ("op3", "source-c", "continue", "complete", 4, 5, "u3", "a3"),
                        ("op4", "unknown", "continue", "complete", 6, 7, "u4", "a4")):
                db.execute("INSERT INTO mutation_attempts VALUES (?,?,?,?,?,?,?,?)", row)

    def test_completed_source_mapping_and_holds(self):
        result = completed_operation_candidates(archive_db=str(self.archive),
                                                 db_path=str(self.transport))
        self.assertEqual([x["operation_id"] for x in result["candidates"]], ["op1"])
        self.assertEqual({x["reason"] for x in result["holds"]},
                         {"unmapped_source", "ambiguous_source_mapping"})
        self.assertNotIn("PRIVATE RAW MESSAGE", json.dumps(result))

    def test_typed_operation_and_unverified_formal_repo(self):
        discovered = completed_operation_candidates(archive_db=str(self.archive),
                                                     db_path=str(self.transport))
        refs = [{"kind": "operation", "ref": "op:op1"},
                {"kind": "repository", "ref": "chboishabba/slr#12@" + "a" * 40},
                {"kind": "formal", "ref": "chboishabba/slr@" + "b" * 40 + ":Proof.agda"}]
        result = validate_typed_references("a", refs, operation_candidates=discovered)
        self.assertEqual(result["verified_count"], 1)
        self.assertEqual(result["held_count"], 2)
        wrong = validate_typed_references("b", refs[:1], operation_candidates=discovered)
        self.assertEqual(wrong["verified_count"], 0)
        with self.assertRaises(ValueError):
            validate_typed_references("a", [{"kind": "repository", "ref": "pr:12"}])

    def test_frontier_discovery_and_registry(self):
        result = build_frontier(archive_db=str(self.archive),
                                completed_operations=True, receipt_db=str(self.transport))
        self.assertEqual(result["evaluated_threads"], 1)
        self.assertEqual(result["proposals"], [])
        self.assertEqual(result["evidence_rows"][0]["source_bound_operation_receipts"],
                         ["op:op1"])
        self.assertNotIn("PRIVATE RAW MESSAGE", json.dumps(result))
        names = [x.name for x in build_default_registry().list_tools()]
        self.assertIn("itir.ao.completed_operation_candidates", names)

    def test_unverified_typed_reference_does_not_admit_opaque_labels(self):
        result = build_frontier(
            archive_db=str(self.archive),
            evidence=[{"canonical_thread_id": "a", "task_atom": "prove",
                       "kind": "formal", "formal_gap_receipts": ["formal:opaque"],
                       "typed_refs": [{"kind": "formal",
                                       "ref": "chboishabba/slr@" + "a" * 40 + ":Proof.agda"}]}],
        )
        self.assertEqual(result["proposals"], [])
        self.assertEqual(result["evidence_rows"][0]["formal_gap_receipts"], [])
        self.assertEqual(result["abstentions"][0]["reason"], "typed_reference_hold")


if __name__ == "__main__":
    unittest.main()
