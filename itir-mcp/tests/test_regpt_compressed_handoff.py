"""Regression for the historical re-gpt SQLite archive, not synthetic canonical columns."""
import sqlite3
import tempfile
import unittest
from pathlib import Path

from itir_mcp.governed_revival import governed_handoff, thread_view


class CompressedArchiveTest(unittest.TestCase):
    def test_old_archive_holds_graph_claims(self):
        with tempfile.TemporaryDirectory() as directory:
            dbpath = Path(directory) / "archive.sqlite3"
            with sqlite3.connect(dbpath) as db:
                db.executescript("""
                    CREATE TABLE conversations (
                      internal_id INTEGER PRIMARY KEY AUTOINCREMENT,
                      conversation_id TEXT NOT NULL UNIQUE,
                      conversation_key TEXT NOT NULL,
                      title TEXT, discovered_at REAL NOT NULL DEFAULT 0,
                      last_seen_at REAL NOT NULL DEFAULT 0,
                      remote_update_time REAL, cached_message_count INTEGER DEFAULT 0);
                    CREATE TABLE messages (
                      conversation_id TEXT NOT NULL,
                      message_index INTEGER NOT NULL,
                      author TEXT NOT NULL, content TEXT NOT NULL,
                      create_time REAL, message_key TEXT,
                      PRIMARY KEY (conversation_id, message_index, author));
                    CREATE TABLE conversation_lineage (
                      conversation_id TEXT PRIMARY KEY,
                      parent_conversation_id TEXT NOT NULL,
                      created_at REAL NOT NULL, revival_doc_path TEXT);
                """)
                db.execute("INSERT INTO conversations(conversation_id,conversation_key) VALUES (?,?)", ("parent", "key"))
                db.executemany(
                    "INSERT INTO messages VALUES (?,?,?,?,?,?)",
                    [("parent", 0, "user", "proof gap", 1.0, "k0"),
                     ("parent", 1, "assistant", "lemma pending", 2.0, "k1"),
                     ("parent", 2, "user", "review needed", 3.0, "k2")],
                )
            proposal = {"canonical_thread_id": "parent", "task_atom": "proof gap"}
            result = governed_handoff(proposal, archive_db=str(dbpath))
            self.assertEqual(result["lineage_receipt"]["status"], "exact_graph_coordinates_unavailable_hold")
            self.assertFalse(result["lineage_receipt"]["node_parent_pointers_preserved"])
            self.assertEqual(result["lineage_receipt"]["archive_schema"], "regpt_compressed_messages")
            self.assertEqual(result["span_receipt"]["total_messages"], 3)
            self.assertEqual(result["semantic_pnf_execution"]["status"], "abstained_producer_not_executed")
            self.assertFalse(result["authority"]["dispatch"])
            self.assertTrue(all(r["node_id"] is None and r["parent_node_id"] is None for r in result["source_refs"]))
            self.assertTrue(all(len(r["body_sha256"]) == 64 for r in result["source_refs"]))
            self.assertEqual(result["packet_id"], governed_handoff(proposal, archive_db=str(dbpath))["packet_id"])
            self.assertEqual(thread_view({"canonical_thread_id": "parent", "archive_db": str(dbpath)})["packet"]["lineage_receipt"]["status"], "exact_graph_coordinates_unavailable_hold")


if __name__ == "__main__":
    unittest.main()
