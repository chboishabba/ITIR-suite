"""Dependency-free fleet MCP registry and guard tests."""
import os
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from itir_mcp.registry import build_default_registry
from scripts.evidence_fleet_controller import upsert_work


class FleetMCPTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.db = str(Path(self.temp.name) / "control.sqlite")
        self.cid = "123e4567-e89b-42d3-a456-426614174000"
        with sqlite3.connect(self.db) as db:
            self.work = upsert_work(db, "gap", [self.cid], ["node"], 1)
        self.registry = build_default_registry()

    def test_specs_and_bounded_plan(self):
        for name in ("plan", "refresh_evidence", "attach_gap"):
            spec = self.registry.get_tool_spec("itir.fleet." + name)
            self.assertIsNotNone(spec)
            self.assertFalse(spec.input_schema["additionalProperties"])
        for limit in (2, 3, 4):
            r = self.registry.invoke("itir.fleet.plan", {"control_db": self.db, "limit": limit})
            self.assertTrue(r["ok"], r)
            self.assertFalse(r["result"]["authoritative"])
        self.assertFalse(self.registry.invoke("itir.fleet.plan",
            {"control_db": self.db, "limit": 5})["ok"])

    def test_unauthorized_before_adapter(self):
        with patch("itir_mcp.fleet_tools._controller", side_effect=AssertionError("imported")):
            for authorization in (False, None):
                payload = dict(authorized=authorization, control_db=self.db,
                    work_id=self.work, conversation_id=self.cid,
                    puller="/no/puller", archive_db="/no/archive")
                self.assertFalse(self.registry.invoke("itir.fleet.refresh_evidence",payload)["ok"])

    def test_authorized_delegates_once_and_safe_envelope(self):
        from unittest.mock import Mock
        puller = Path(self.temp.name) / "pull.py"
        archive = Path(self.temp.name) / "archive.db"
        puller.touch()
        archive.touch()
        import scripts.evidence_fleet_controller as controller
        provider = Mock(return_value={"archive_receipt_digest":"receipt","stage":"deferred",
                                      "archive_stage":"ingested","phase":"gap"})
        with patch.object(controller,"exact_async_archive_provider",return_value=provider) as factory, \
             patch.object(controller,"refresh_work_evidence",return_value={
                 "stage":"deferred","archive_stage":"ingested","phase":"gap"}) as refresh:
            payload=dict(authorized=True,control_db=self.db,work_id=self.work,
                         conversation_id=self.cid,puller=str(puller),archive_db=str(archive))
            result=self.registry.safe_invoke("itir.fleet.refresh_evidence",payload)
            self.assertTrue(result["ok"],result)
            self.assertEqual(factory.call_count,1)
            self.assertEqual(refresh.call_count,1)
            self.assertEqual(result["result"]["result"]["evidence"]["archive_stage"],"ingested")
            self.assertNotEqual(result["result"]["decision"],"promoted")

    def test_offline_gap_no_puller(self):
        import scripts.evidence_fleet_controller as controller
        formal=Path(self.temp.name)/"formal.agda";formal.touch()
        slrw=Path(self.temp.name)/"world.slrw";slrw.touch()
        with patch.object(controller,"exact_async_archive_provider",
                          side_effect=AssertionError("puller used")), \
             patch.object(controller,"attach_gap_to_archive",return_value={
                 "stage":"rescored","gap_receipt_digest":"gap"}) as attach:
            result=self.registry.invoke("itir.fleet.attach_gap",dict(
                control_db=self.db,work_id=self.work,conversation_id=self.cid,
                archive_receipt_digest="archive",formal_file=str(formal),slrw=str(slrw)))
            self.assertTrue(result["ok"],result)
            self.assertEqual(attach.call_count,1)
            self.assertFalse(result["result"]["authoritative"])


if __name__ == "__main__":
    unittest.main()
