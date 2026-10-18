import sqlite3
import unittest
from scripts.evidence_fleet_controller import (migrate,lineage,packet,score,upsert_work,plan,lifecycle,validate_transport,attach_receipt,refresh_work_evidence,EvidenceDeferred)

class FleetTest(unittest.TestCase):
    def setUp(self):
        self.db=sqlite3.connect(":memory:")
    def tearDown(self):
        self.db.close()
    def test_migration_lineage_idempotent(self):
        migrate(self.db); migrate(self.db)
        lineage(self.db,"child",["p2","p1"],"synthesized_from",{"ref":"m1"})
        lineage(self.db,"child",["p1","p2"],"synthesized_from",{"ref":"m1"})
        self.assertEqual(self.db.execute("SELECT count(*) FROM conversation_lineage_edges").fetchone()[0],2)
    def test_packet_provenance(self):
        p=packet([{"conversation_id":"b","message_refs":["n2"]},{"conversation_id":"a","message_refs":["n1"]}],"run test")
        self.assertEqual(p["parents"][0]["message_refs"],["n1"])
        self.assertEqual(p["parents"][1]["conversation_id"],"b")
    def test_score(self):
        a={"pnf_factors":["f"],"gap_residues":["g"],"premises":["a"],"next_testable_step":"test"}
        b={"pnf_factors":["f"],"gap_residues":["g"],"premises":["b"]}
        self.assertEqual(score(a,b)["action"],"synthesize")
        self.assertEqual(score({}, {})["action"],"park")
    def test_cap_and_idempotent_work(self):
        for i in range(8):
            x=upsert_work(self.db,str(i),["p"],["node"],i)
            self.assertEqual(x,upsert_work(self.db,str(i),["p"],["node"],i))
        self.assertEqual(len(plan(self.db)),3)
        with self.assertRaises(ValueError): plan(self.db,8)
    def test_lifecycle_and_receipt(self):
        self.assertEqual(lifecycle()[0],"exact_conversation_refresh")
        key=upsert_work(self.db,"gap",["p"],["m"],1)
        attach_receipt(self.db,key,"formal","sha:abc")
        attach_receipt(self.db,key,"formal","sha:abc")
        self.assertEqual(len(__import__("json").loads(self.db.execute("SELECT receipt_refs FROM fleet_work_units").fetchone()[0])),1)
    def test_no_dom(self):
        validate_transport("async",False)
        for mode,dom in [("browser",False),("async",True)]:
            with self.assertRaises(ValueError): validate_transport(mode,dom)


    def test_exact_read_only_lifecycle_and_repeat(self):
        cid="123e4567-e89b-42d3-a456-426614174000"
        work=upsert_work(self.db,"gap",[cid],["node"],1)
        calls=[]
        def provider(exact):
            calls.append(exact)
            return dict(receipt_ref="receipt:1",source_ref="archive:node",
                source_digest="sha256:abc",archive_delta=2,pnf_ref="pnf:1",
                gap_ref="gap:1",gap_digest="sha256:def",gap_score=7,
                observed_at="2026-10-18T00:00:00Z")
        result=refresh_work_evidence(self.db,work,cid,provider)
        self.assertEqual(result["stage"],"rescored")
        self.assertEqual(result["stages"],["refreshed","ingested","reduced","rescored"])
        self.assertEqual(refresh_work_evidence(self.db,work,cid,provider)["replayed"],True)
        self.assertEqual(calls,[cid,cid])
        self.assertEqual(self.db.execute("SELECT count(*) FROM fleet_evidence_receipts").fetchone()[0],1)
        self.assertEqual(self.db.execute("SELECT priority FROM fleet_work_units").fetchone()[0],7)
        self.assertEqual(self.db.execute("SELECT state FROM fleet_work_units").fetchone()[0],"proposed")

    def test_deferred_and_failure_do_not_change_work_state(self):
        cid="123e4567-e89b-42d3-a456-426614174000"
        work=upsert_work(self.db,"gap",[cid],["node"],3)
        def deferred(_): raise EvidenceDeferred("not ready")
        def failed(_): raise RuntimeError("secret must not be stored")
        self.assertEqual(refresh_work_evidence(self.db,work,cid,deferred)["stage"],"deferred")
        self.assertEqual(refresh_work_evidence(self.db,work,cid,failed)["stage"],"failed")
        self.assertEqual(self.db.execute("SELECT state,priority FROM fleet_work_units").fetchone(),("proposed",3))
        rows=self.db.execute("SELECT error_class FROM fleet_evidence_receipts").fetchall()
        self.assertEqual(sorted(r[0] for r in rows),["EvidenceDeferred","RuntimeError"])
        self.assertEqual(self.db.execute("SELECT count(*) FROM fleet_evidence_receipts").fetchone()[0],2)

    def test_exact_id_guard_and_no_mutation_route(self):
        cid="123e4567-e89b-42d3-a456-426614174000"
        work=upsert_work(self.db,"gap",[cid],["node"],1)
        def forbidden(_): raise AssertionError("provider must not be invoked")
        for invalid in ("title", "123e4567-e89b-42d3-a456-426614174001"):
            with self.assertRaises(ValueError):
                refresh_work_evidence(self.db,work,invalid,forbidden)
        def forbidden_mutation(_):
            raise AssertionError("mutation route reached")
        # Provider is an exact-read-only injected callable; no mutation service
        # is imported or available to the controller.
        self.assertNotIn("MutationService",vars(__import__("scripts.evidence_fleet_controller",fromlist=["*"])))
        self.assertEqual(refresh_work_evidence(self.db,work,cid,forbidden_mutation)["stage"],"failed")

if __name__ == "__main__": unittest.main()
