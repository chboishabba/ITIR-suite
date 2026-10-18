import sqlite3
import unittest
from scripts.evidence_fleet_controller import (migrate,lineage,packet,score,upsert_work,plan,lifecycle,validate_transport,attach_receipt)

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

if __name__ == "__main__": unittest.main()
