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
from itir_mcp.server import _register_fastmcp_tool
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


    def test_reference_materialization_receipt_round_trip(self):
        first = self.packet(max_messages=1, max_chars=100, packet_max_chars=24000)
        again = self.packet(max_messages=1, max_chars=100, packet_max_chars=24000)
        self.assertEqual(first, again)  # idempotent, byte-stable identity
        packet = first["packets"][0]
        receipt = packet["reference_materialization_receipt"]
        self.assertEqual(receipt["work_packet_ref"], packet["packet_id"])
        self.assertEqual(receipt["archive_thread_ref"], "thread")
        self.assertEqual(receipt["source_ref_count"], 1)
        self.assertEqual(receipt["governed_dispatch"]["state"], "not_dispatched")
        self.assertFalse(receipt["raw_body_persisted"])
        self.assertFalse(receipt["producer_verified_pnf"])
        self.assertEqual(len(receipt["pnf_projection_refs"]), 1)
        projection = receipt["pnf_projection_refs"][0]
        source = packet["source_refs"][0]
        self.assertEqual(projection["source_ref"]["message_id"], source["message_id"])
        self.assertEqual(projection["source_ref"]["archive_locator"], source["archive_locator"])
        self.assertEqual(projection["source_ref"]["body_sha256"], source["body_sha256"])
        self.assertIn("lexical_candidate_not_producer_verified_pnf", projection["residuals"])
        self.assertNotIn("lemma 5", json.dumps(first))
        self.assertLessEqual(len(json.dumps(first, sort_keys=True, separators=(",", ":"), ensure_ascii=False)), 24000)

    def test_registry_reference_receipt_and_packet_budget(self):
        response = build_default_registry().invoke("itir.pnf.work_packet", {
            "archive_db": str(self.archive),
            "proposals": self.proposals,
            "span_policy": {"max_messages": 2, "max_chars": 100,
                            "packet_max_chars": 3000},
        })
        self.assertTrue(response["ok"], response)
        result = response["result"]
        self.assertLessEqual(len(json.dumps(result, sort_keys=True,
                        separators=(",", ":"), ensure_ascii=False)), 3000)
        packet = result["packets"][0]
        for unit in packet["reference_materialization_receipt"]["pnf_projection_refs"]:
            self.assertIn(unit["source_ref"]["message_id"],
                          {r["message_id"] for r in packet["source_refs"]})

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

    def test_fastmcp_registered_transport_strips_reserved_kwargs(self):
        class FakeFastMCP:
            def __init__(self):
                self.handlers = {}

            def tool(self, *, name, description):
                def register(handler):
                    self.handlers[name] = handler
                    return handler
                return register

        server = FakeFastMCP()
        registry = build_default_registry()
        spec = registry.get_tool_spec("itir.pnf.work_packet")
        _register_fastmcp_tool(server, registry, spec)
        handler = server.handlers["itir.pnf.work_packet"]
        payload = {"archive_db": str(self.archive), "proposals": self.proposals}
        result = handler(arguments=payload, kwargs={})
        self.assertTrue(result["ok"], result)
        self.assertTrue(result["result"]["packets"][0]["source_refs"])
        # Genuine unknown tool fields still fail closed.
        rejected = handler(arguments={**payload, "unexpected": True}, kwargs={})
        self.assertFalse(rejected["ok"], rejected)
        self.assertEqual(rejected["error"]["code"], "input_error")

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
