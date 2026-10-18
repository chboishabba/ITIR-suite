"""Canonical live-schema fixture for bounded reference-only work packets."""
import hashlib
import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "itir-mcp" / "src"))
from itir_mcp.registry import build_default_registry
from itir_mcp.pnf_work_packet_provider import build_work_packet, postgres_reference_adapter

LIVE_COLUMNS = (
    "message_id canonical_thread_id platform account_id ts role text title source_id "
    "source_thread_id source_message_id source_path source_bucket provenance_json "
    "node_id parent_node_id branch_membership tool_kind citation_token filename "
    "mime_type asset_pointer body_storage_ref source_scope visibility"
).split()


class PacketTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.archive = Path(self.temp.name) / "chat_archive.sqlite"
        with sqlite3.connect(self.archive) as db:
            db.execute("CREATE TABLE messages (" + ",".join(c + " TEXT" for c in LIVE_COLUMNS) + ")")
            for i in range(6):
                db.execute(
                    "INSERT INTO messages (message_id,canonical_thread_id,platform,account_id,"
                    "ts,role,text,source_message_id,node_id) VALUES (?,?,?,?,?,?,?,?,?)",
                    (str(i), "thread", "chatgpt", "main", str(i).zfill(4),
                     "assistant", f"lemma {i}", f"source-{i}", f"node-{i}"),
                )
        self.proposals = [{"canonical_thread_id": "thread", "task_atom": "formalise lemma",
                           "formal_gap_receipts": ["gap:1"]}]

    def packet(self, **policy):
        return build_work_packet(self.proposals, archive_db=str(self.archive),
                                 span_policy=policy or None)

    def test_live_schema_digest_and_tail(self):
        result = self.packet(max_messages=3, max_chars=100, packet_max_chars=24000)
        packet = result["packets"][0]
        self.assertEqual(len(packet["source_refs"]), 3)
        self.assertEqual(packet["source_refs"][0]["message_id"], "3")
        self.assertEqual(packet["source_refs"][-1]["body_sha256"],
                         hashlib.sha256(b"lemma 5").hexdigest())
        self.assertTrue(packet["truncation_receipt"]["thread_tail_truncated"])
        self.assertEqual(packet["truncation_receipt"]["total_messages"], 6)
        self.assertEqual(packet["evidence_receipts"]["formal_gap_receipts"], ["gap:1"])
        self.assertNotIn("lemma 5", json.dumps(result))
        self.assertFalse(packet["reference_projection"]["raw_body_persisted"])
        self.assertEqual(packet["packet_id"], self.packet(
            max_messages=3, max_chars=100, packet_max_chars=24000)["packets"][0]["packet_id"])

    def test_char_truncation_and_size(self):
        packet = self.packet(max_messages=6, max_chars=14)["packets"][0]
        self.assertEqual(packet["truncation_receipt"]["selected_messages"], 2)
        self.assertTrue(packet["truncation_receipt"]["span_char_truncated"])
        self.assertLessEqual(len(json.dumps(self.packet(), sort_keys=True,
                                           separators=(",", ":"), ensure_ascii=False)), 24000)

    def test_missing_thread_and_policy_fail_closed(self):
        with self.assertRaises(ValueError):
            build_work_packet([{"canonical_thread_id": "missing", "task_atom": "task"}],
                              archive_db=str(self.archive))
        with self.assertRaises(ValueError):
            self.packet(max_messages=201)
        with self.assertRaises(ValueError):
            self.packet(packet_max_chars=20)
        with self.assertRaises(FileNotFoundError):
            build_work_packet(self.proposals, archive_db="/missing/canonical.sqlite")

    def test_postgres_stub(self):
        with self.assertRaises(NotImplementedError):
            postgres_reference_adapter()
        self.assertEqual(self.packet()["packets"][0]["reference_projection"]["postgres_adapter"],
                         "unavailable_stub")

    def test_production_server_import_isolated(self):
        import os
        import subprocess

        package_src = Path(__file__).resolve().parents[1] / "itir-mcp" / "src"
        snippet = (
            "from itir_mcp.registry import build_default_registry; "
            "import sys; "
            "r=build_default_registry().invoke('itir.pnf.work_packet', "
            "{'archive_db':sys.argv[1], "
            "'proposals':[{'canonical_thread_id':'thread','task_atom':'lemma'}]}); "
            "assert r['ok'], r; assert r['result']['packets'][0]['source_refs']"
        )
        proc = subprocess.run(
            [sys.executable, "-c", snippet, str(self.archive)],
            cwd=package_src.parent,
            env={**os.environ, "PYTHONPATH": str(package_src)},
            capture_output=True, text=True, check=False, timeout=30,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)

    def test_registry(self):
        spec = build_default_registry().get_tool_spec("itir.pnf.work_packet")
        self.assertIsNotNone(spec)
        self.assertEqual(spec.response_version, "itir.pnf.work_packet.v1")
        self.assertTrue(spec.read_only)
        self.assertFalse(spec.input_schema["additionalProperties"])
        response = build_default_registry().invoke("itir.pnf.work_packet", {
            "archive_db": str(self.archive), "proposals": self.proposals})
        self.assertTrue(response["ok"], response)


if __name__ == "__main__":
    unittest.main()
