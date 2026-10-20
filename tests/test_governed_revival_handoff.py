"""Offline real-schema regression for governed canonical predecessor handoff."""
from __future__ import annotations

import hashlib
import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "itir-mcp" / "src"))

from itir_mcp.governed_revival import governed_handoff, operation_review, thread_view, _lexical_spans, _sensiblaw_tokenizer, TOKEN_RE
from itir_mcp.operation_receipt_lookup import operation_receipts
from unittest.mock import patch
from itir_mcp.registry import build_default_registry
from itir_mcp.pnf_work_packet_provider import REQUIRED


class GovernedRevivalTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.archive = Path(temp.name) / "canonical.sqlite"
        with sqlite3.connect(self.archive) as db:
            db.execute("CREATE TABLE messages (" +
                       ",".join(f"{name} TEXT" for name in sorted(REQUIRED)) + ")")
            for i in range(90):
                text = "ordinary message" if i < 89 else "Final decision: blocked lemma PR #42"
                if i == 5:
                    text = "formal proof gap Agda open lemma"
                db.execute(
                    "INSERT INTO messages (message_id,canonical_thread_id,source_thread_id,"
                    "source_message_id,node_id,parent_node_id,branch_membership,"
                    "ts,role,text,platform,account_id) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                    (str(i), "parent", "origin", f"source-{i}", f"node-{i}",
                     f"node-{i-1}" if i else None, "main", str(i).zfill(4),
                     "assistant", text, "chatgpt", "main"),
                )
        self.proposal = {"canonical_thread_id": "parent",
                         "task_atom": "proof gap lemma",
                         "formal_gap_receipts": ["gap:42"],
                         "repo_receipts": ["PR:42"]}

    def build(self, **kw):
        return governed_handoff(self.proposal, archive_db=str(self.archive), **kw)

    def test_full_span_and_tail_decision(self):
        def public_tokenizer(text):
            return [(match.group(), match.start(), match.end()) for match in TOKEN_RE.finditer(text)]

        with patch("itir_mcp.governed_revival._sensiblaw_tokenizer", return_value=public_tokenizer):
            packet = self.build(child_thread_id="child")
            repeat_packet = self.build(child_thread_id="child")
        ids = {r["message_id"] for r in packet["source_refs"]}
        self.assertIn("5", ids)
        self.assertIn("89", ids)
        self.assertIn("88", ids)
        self.assertEqual(packet["span_receipt"]["total_messages"], 90)
        self.assertTrue(packet["span_receipt"]["full_thread_scanned"])
        self.assertFalse(packet["span_receipt"]["first_30000_char_cutoff"])
        self.assertEqual(packet["lineage_receipt"]["child_thread_id"], "child")
        source = next(r for r in packet["source_refs"] if r["message_id"] == "89")
        self.assertEqual(source["parent_node_id"], "node-88")
        self.assertEqual(source["body_sha256"],
                         hashlib.sha256(b"Final decision: blocked lemma PR #42").hexdigest())
        self.assertNotIn("Final decision:", json.dumps(packet))
        self.assertEqual(packet["evidence_receipts"]["repo_receipts"], ["PR:42"])
        self.assertEqual(packet["packet_id"], repeat_packet["packet_id"])

    def test_ambiguous_operation_hold(self):
        for status in ("async_starting", "commit_unknown"):
            packet = self.build(operation_status=status)
            self.assertEqual(packet["governance"]["decision"], "hold_reconcile_no_resend")
            self.assertFalse(packet["governance"]["automatic_resend_allowed"])
        self.assertFalse(operation_review({"operation_status": "completed"})["dispatch_allowed"])

    def test_packet_bounds_and_missing_thread(self):
        packet = self.build(max_selected=2)
        self.assertEqual(len(packet["source_refs"]), 2)
        self.assertEqual(packet["span_receipt"]["omitted_messages"], 88)
        with self.assertRaises(ValueError):
            self.build(max_selected=81)
        with self.assertRaises(ValueError):
            self.build(max_packet_chars=1000, max_selected=80)
        with self.assertRaises(ValueError):
            governed_handoff({"canonical_thread_id": "missing", "task_atom": "proof"},
                             archive_db=str(self.archive))

    def test_public_tokenizer_and_degraded_abstention(self):
        _sensiblaw_tokenizer.cache_clear()
        with patch("itir_mcp.governed_revival._sensiblaw_tokenizer", return_value=None):
            self.assertEqual(_lexical_spans("lemma proof", frozenset({"lemma"})), [])
            packet = self.build()
            self.assertFalse(packet["producer_receipt"]["available"])
            self.assertEqual(packet["producer_receipt"]["fallback"],
                             "abstain_no_parser_authority")
        def public_tokenizer(text):
            return [("lemma", 0, 5)]
        with patch("itir_mcp.governed_revival._sensiblaw_tokenizer",
                   return_value=public_tokenizer):
            self.assertEqual(_lexical_spans("lemma", frozenset({"lemma"}))[0]["authority"],
                             "sensiblaw_public_token_span_candidate")

    def test_bounded_operation_receipt_lookup_and_review(self):
        receipt_db = self.archive.parent / "transport.sqlite"
        with sqlite3.connect(receipt_db) as db:
            db.execute(
                "CREATE TABLE mutation_attempts (operation_id TEXT,operation TEXT,"
                "conversation_id TEXT,requested_parent_node_id TEXT,"
                "prompt_digest TEXT,transport TEXT,state TEXT,started_at REAL,"
                "submitted_at REAL,committed_at REAL,completed_at REAL,"
                "user_node_id TEXT,assistant_node_id TEXT,error_detail TEXT)"
            )
            for index, state in enumerate(("complete", "commit_unknown", "async_starting")):
                db.execute(
                    "INSERT INTO mutation_attempts VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (str(index), "continue", "origin", None, "sha256", "async", state,
                     float(index), None, None, None, None, None, "private raw detail"),
                )
        payload = {"canonical_thread_id": "parent", "archive_db": str(self.archive),
                   "db_path": str(receipt_db), "limit": 1, "active_only": True}
        result = operation_receipts(payload)
        self.assertEqual(result["records"][0]["operation_id"], "2")
        self.assertEqual(result["records"][0]["governance_review"]["decision"],
                         "hold_reconcile_no_resend")
        self.assertTrue(result["truncation_receipt"]["more_available"])
        self.assertNotIn("private raw detail", json.dumps(result))
        registry_result = build_default_registry().invoke(
            "itir.chatgpt.operation_receipts", payload)
        self.assertTrue(registry_result["ok"], registry_result)
        self.assertIsNotNone(build_default_registry().get_tool_spec(
            "itir.chatgpt.operation_receipts"))
        with self.assertRaises(ValueError):
            operation_receipts({**payload, "unexpected": 1})
        with self.assertRaises(FileNotFoundError):
            operation_receipts({**payload, "db_path": str(self.archive.parent / "missing")})

    def test_view_and_registry(self):
        view = thread_view({"canonical_thread_id": "parent", "archive_db": str(self.archive)})
        self.assertEqual(view["version"], "itir.archive.thread_view.v1")
        registry = build_default_registry()
        for name in ("itir.pnf.governed_handoff", "itir.archive.thread_view",
                     "itir.ao.operation_review"):
            self.assertIsNotNone(registry.get_tool_spec(name))
        result = registry.invoke("itir.pnf.governed_handoff", {
            "proposal": self.proposal, "archive_db": str(self.archive),
            "operation_status": "commit_unknown"})
        self.assertTrue(result["ok"], result)
        self.assertTrue(result["result"]["source_refs"])
        self.assertEqual(result["result"]["governance"]["decision"],
                         "hold_reconcile_no_resend")


if __name__ == "__main__":
    unittest.main()
