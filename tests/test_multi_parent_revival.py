from __future__ import annotations

import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "itir-mcp" / "src"))

from itir_mcp.governed_revival import governed_multi_parent_handoff
from itir_mcp.pnf_work_packet_provider import REQUIRED
from itir_mcp.registry import build_default_registry


class MultiParentRevivalTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.archive = Path(self.temp.name) / "canonical.sqlite"
        with sqlite3.connect(self.archive) as db:
            db.execute("CREATE TABLE messages (" + ",".join(f"{name} TEXT" for name in sorted(REQUIRED)) + ")")
            for parent in ("p1", "p2", "p3"):
                for index in range(5):
                    body = f"source material {parent} item {index}"
                    db.execute(
                        "INSERT INTO messages (message_id,canonical_thread_id,source_thread_id,"
                        "source_message_id,node_id,parent_node_id,branch_membership,ts,role,text,"
                        "platform,account_id) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                        (f"{parent}-{index}", parent, f"source-{parent}", f"sm-{index}",
                         f"node-{parent}-{index}", f"node-{parent}-{index-1}" if index else None,
                         "main", f"{index:04d}", "assistant", body, "chatgpt", "account"),
                    )

    @staticmethod
    def tokenizer(text: str):
        result = []
        offset = 0
        for token in text.split():
            start = text.find(token, offset)
            result.append((token.casefold(), start, start + len(token)))
            offset = start + len(token)
        return result

    def proposals(self, *parents: str):
        return [{"canonical_thread_id": parent, "task_atom": "source material"}
                for parent in parents]

    def test_two_to_ten_contract_and_independent_lineage(self):
        with patch("itir_mcp.governed_revival._sensiblaw_tokenizer", return_value=self.tokenizer):
            result = governed_multi_parent_handoff(
                self.proposals("p1", "p2"), archive_db=str(self.archive),
                child_thread_id="child-1")
        self.assertEqual(result["parent_count"], 2)
        self.assertEqual([p["canonical_thread_id"] for p in result["parents"]], ["p1", "p2"])
        self.assertTrue(result["lineage_receipt"]["parents_remain_independent_authorities"])
        self.assertFalse(result["lineage_receipt"]["parent_retirement"])
        self.assertEqual(result["candidate_world"]["cross_parent_equivalences"], [])
        self.assertFalse(result["candidate_world"]["reviewed_world_model"])
        self.assertFalse(result["candidate_world"]["formal_proof"])
        self.assertFalse(result["formal_gap"]["selected_context_sufficiency_proved"])
        self.assertNotIn("source material p1", json.dumps(result))

    def test_parent_count_duplicate_and_total_budget_gates(self):
        with patch("itir_mcp.governed_revival._sensiblaw_tokenizer", return_value=self.tokenizer):
            for count in (2, 3, 10):
                result = governed_multi_parent_handoff(
                    self.proposals(*(f"p{i}" for i in range(1, count + 1))),
                    archive_db=str(self.archive), max_selected_per_parent=2,
                    max_total_selected=20)
                self.assertEqual(result["parent_count"], count)
            with self.assertRaises(ValueError):
                governed_multi_parent_handoff(self.proposals("p1"), archive_db=str(self.archive))
            with self.assertRaises(ValueError):
                governed_multi_parent_handoff(self.proposals("p1", "p1"), archive_db=str(self.archive))
            with self.assertRaises(ValueError):
                governed_multi_parent_handoff(self.proposals("p1", "p2"),
                    archive_db=str(self.archive), max_selected_per_parent=5,
                    max_total_selected=2)

    def test_registry_exposes_read_only_tool(self):
        registry = build_default_registry()
        spec = registry.get_tool_spec("itir.pnf.multi_parent_handoff")
        self.assertIsNotNone(spec)
        result = registry.invoke("itir.pnf.multi_parent_handoff", {
            "proposals": self.proposals("p1", "p2"),
            "archive_db": str(self.archive),
        })
        self.assertTrue(result["ok"], result)
        self.assertFalse(result["result"]["authority"]["dispatch"])

    def test_operational_store_is_not_accepted_as_corpus(self):
        legacy = Path(self.temp.name) / "regpt.sqlite"
        with sqlite3.connect(legacy) as db:
            db.execute("CREATE TABLE messages (conversation_id TEXT, message_index INTEGER,"
                       "author TEXT, content TEXT, create_time REAL)")
            db.execute("INSERT INTO messages VALUES ('p1',0,'user','not corpus',0)")
        with patch("itir_mcp.governed_revival._sensiblaw_tokenizer", return_value=self.tokenizer):
            with self.assertRaises(RuntimeError):
                governed_multi_parent_handoff(
                    self.proposals("p1", "p2"), archive_db=str(legacy))


if __name__ == "__main__":
    unittest.main()
