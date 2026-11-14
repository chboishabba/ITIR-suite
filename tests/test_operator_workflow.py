"""AO-OP-1 fixture acceptance; no live accounts, transport or mutation."""
from __future__ import annotations

import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "itir-mcp" / "src"))
from itir_mcp.operator_workflow import build_operator_workflow
from itir_mcp.registry import build_default_registry

COLUMNS = ("message_id canonical_thread_id platform account_id ts role text title "
           "source_id source_thread_id source_message_id source_path source_bucket "
           "provenance_json node_id parent_node_id branch_membership tool_kind "
           "citation_token filename mime_type asset_pointer body_storage_ref "
           "source_scope visibility").split()


class OperatorWorkflowTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.path = Path(temp.name) / "archive.sqlite"
        self.receipts = Path(temp.name) / "operations.sqlite"
        with sqlite3.connect(self.path) as db:
            db.execute("CREATE TABLE messages (" + ",".join(c + " TEXT" for c in COLUMNS) + ")")
            for tid, source in (("a", "source-a"), ("b", "source-b"),
                                ("amb", "source-1"), ("amb", "source-2")):
                db.execute("INSERT INTO messages (message_id,canonical_thread_id,platform,"
                           "account_id,ts,role,text,source_thread_id) VALUES (?,?,?,?,?,?,?,?)",
                           (tid + source, tid, "chatgpt", "main", "2026-10-20",
                            "assistant", "PRIVATE_API_TOKEN_ABC lemma", source))
        with sqlite3.connect(self.receipts) as db:
            db.execute("CREATE TABLE mutation_attempts (operation_id TEXT,conversation_id TEXT,"
                       "operation TEXT,state TEXT,started_at REAL,completed_at REAL,"
                       "user_node_id TEXT,assistant_node_id TEXT)")
            db.execute("INSERT INTO mutation_attempts VALUES (?,?,?,?,?,?,?,?)",
                       ("op1", "source-a", "continue", "complete", 1, 2, "u", "a"))

    def request(self, candidates=None, **kwargs):
        return {"archive_db": str(self.path), "candidates": candidates or [
            {"canonical_thread_id": "a", "task_atom": "review lemma",
             "pnf_receipts": ["pnf:fixture"]}], **kwargs}

    def test_valid_canonical_candidate_deterministic_and_no_promotion(self):
        result = build_operator_workflow(self.request())
        self.assertEqual(result["rows"][0]["candidate_disposition"], "admit")
        self.assertFalse(result["promotion"])
        self.assertFalse(result["dispatch_performed"])
        self.assertEqual(result["workflow_id"], build_operator_workflow(self.request())["workflow_id"])

    def test_unknown_held(self):
        r = build_operator_workflow(self.request([
            {"canonical_thread_id": "missing", "task_atom": "review",
             "pnf_receipts": ["pnf:fixture"]}]))
        self.assertEqual(r["rows"][0]["state"], "held")
        self.assertFalse(r["rows"][0]["selected"])

    def test_ambiguous_mapping_no_selection(self):
        r = build_operator_workflow(self.request([
            {"canonical_thread_id": "amb", "task_atom": "review",
             "pnf_receipts": ["pnf:fixture"]}]))
        self.assertIn("ambiguous_source_mapping", r["rows"][0]["holds"])
        self.assertFalse(r["rows"][0]["selected"])

    def test_unverified_repo_and_formal_held(self):
        r = build_operator_workflow(self.request([
            {"canonical_thread_id": "a", "task_atom": "review",
             "typed_refs": [{"kind": "repository", "ref": "x/y#1@" + "a" * 40},
                            {"kind": "formal", "ref": "x/y@" + "b" * 40 + ":A.agda"}]}]))
        self.assertIn("unverified_typed_reference", r["rows"][0]["holds"])
        self.assertFalse(r["promotion"])

    def test_missing_semantic_pnf_stays_candidate_only_not_promoted(self):
        r = build_operator_workflow(self.request())
        self.assertEqual(r["rows"][0]["state"], "candidate")
        self.assertEqual(r["rows"][0]["pnf_verification"], "unverified")
        self.assertTrue(r["rows"][0]["selected"])
        self.assertFalse(r["promotion"])

    def test_trusted_verified_pnf_is_actionable_without_pg(self):
        calls = []
        def verify(thread, refs):
            calls.append((thread, refs))
            return thread == "a" and refs == ("pnf:fixture",)
        r = build_operator_workflow(self.request(), verified_pnf_resolver=verify)
        row = r["rows"][0]
        self.assertEqual(calls, [("a", ("pnf:fixture",))])
        self.assertEqual(row["pnf_verification"], "verified")
        self.assertEqual(row["state"], "candidate")
        self.assertEqual(row["next_action"], "inspect_candidate_handoff")
        self.assertTrue(row["selected"])
        self.assertIsNotNone(row["pnf_packet_id"])
        self.assertFalse(r["promotion"])
        self.assertEqual(r["workflow_id"], build_operator_workflow(
            self.request(), verified_pnf_resolver=verify)["workflow_id"])

    def test_untrusted_pnf_label_does_not_claim_verified(self):
        r = build_operator_workflow(self.request())
        self.assertEqual(r["rows"][0]["pnf_verification"], "unverified")
        self.assertNotEqual(r["rows"][0]["authority"], "producer_verified_pnf_review_only")

    def test_verifier_failure_is_held_without_promotion(self):
        def unavailable(_thread, _refs):
            raise RuntimeError("PRIVATE_API_TOKEN_ABC")
        r = build_operator_workflow(self.request(), verified_pnf_resolver=unavailable)
        self.assertIn("pnf_verification_unavailable", r["rows"][0]["holds"])
        self.assertFalse(r["rows"][0]["selected"])
        self.assertNotIn("PRIVATE_API_TOKEN_ABC", json.dumps(r))

    def test_ambiguous_operation_states_hold_no_resend(self):
        for status in ("async_starting", "commit_unknown"):
            with self.subTest(status=status):
                r = build_operator_workflow(self.request([
                    {"canonical_thread_id": "a", "task_atom": "review",
                     "pnf_receipts": ["pnf:fixture"], "operation_status": status}]))
                self.assertIn("operation_requires_reconciliation", r["rows"][0]["holds"])
                self.assertFalse(r["automatic_resend_allowed"])

    def test_missing_receipt_locator_fails_closed(self):
        with self.assertRaises(ValueError):
            build_operator_workflow(self.request(operation_receipts=True))

    def test_bounded_selection_and_stable_order(self):
        rows = [{"canonical_thread_id": "a", "task_atom": "review",
                 "pnf_receipts": ["pnf:fixture"]},
                {"canonical_thread_id": "b", "task_atom": "review",
                 "pnf_receipts": ["pnf:fixture"]}]
        r = build_operator_workflow(self.request(list(reversed(rows)), max_items=1))
        self.assertTrue(r["truncation"]["candidate_limit_hit"])
        self.assertEqual(r["rows"][0]["canonical_thread_id"], "a")

    def test_no_secret_or_locator_disclosure(self):
        r = build_operator_workflow(self.request())
        text = json.dumps(r)
        self.assertNotIn("PRIVATE_API_TOKEN_ABC", text)
        self.assertNotIn(str(self.path), text)
        self.assertNotIn(str(self.receipts), text)

    def test_registry_production_tool(self):
        registry = build_default_registry()
        spec = registry.get_tool_spec("itir.ao.operator_workflow")
        self.assertIsNotNone(spec)
        self.assertFalse(spec.input_schema["additionalProperties"])
        r = registry.invoke("itir.ao.operator_workflow", self.request())
        self.assertTrue(r["ok"])

    def test_read_only_corpus_delta(self):
        with sqlite3.connect(self.path) as db:
            before = db.execute("SELECT * FROM messages ORDER BY message_id").fetchall()
        build_operator_workflow(self.request())
        with sqlite3.connect(self.path) as db:
            after = db.execute("SELECT * FROM messages ORDER BY message_id").fetchall()
        self.assertEqual(before, after)

    def test_strict_unknown_fields_and_explicit_location(self):
        with self.assertRaises(ValueError):
            build_operator_workflow({**self.request(), "model": "invented"})
        with self.assertRaises(ValueError):
            build_operator_workflow({"candidates": self.request()["candidates"]})


if __name__ == "__main__":
    unittest.main()
