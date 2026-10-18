import sqlite3
import unittest
from scripts.evidence_fleet_controller import (migrate,lineage,packet,score,upsert_work,plan,lifecycle,validate_transport,attach_receipt,refresh_work_evidence,EvidenceDeferred,exact_async_archive_provider,attach_gap_to_archive)

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


    def test_existing_async_puller_exact_once_and_gap(self):
        import json, tempfile
        from pathlib import Path
        from types import SimpleNamespace
        cid="123e4567-e89b-42d3-a456-426614174000"
        with tempfile.TemporaryDirectory() as td:
            puller=Path(td)/"pull_to_structurer.py"; puller.touch()
            archive=Path(td)/"archive.sqlite"; archive.touch()
            formal=Path(td)/"formal.agda"; formal.touch()
            world=Path(td)/"world.slrw"; world.touch()
            calls=[]
            def run(cmd, **kwargs):
                calls.append(cmd)
                return SimpleNamespace(returncode=0,stdout=json.dumps({
                    "requested_targets":1,"selected_id_filters":1,
                    "async":{"total":1,"ok":1,"failures":0,"messages":4},
                    "source_id":"pull_receipt_1","ingest":{"inserted":2,"duplicates":1,"parsed_messages":4,"artifacts":{"indexed":1}}}))
            def gap(*args):
                self.assertEqual(args,(cid,str(formal),str(world)))
                return SimpleNamespace(unmatched_informal_factors=2,
                    unmatched_formal_factors=1,matched_semantic_factors=5)
            provider=exact_async_archive_provider(str(puller),str(archive),"main",
                formal_file=str(formal),slrw_path=str(world),runner=run,gap_compare=gap)
            with self.assertRaises(ValueError): provider("not-a-uuid")
            self.assertEqual(len(calls),0)
            work=upsert_work(self.db,"gap",[cid],["node"],1)
            result=refresh_work_evidence(self.db,work,cid,provider)
            self.assertEqual(result["stage"],"rescored")
            self.assertEqual(len(calls),1)
            self.assertEqual(calls[0][calls[0].index("--ids")+1],cid)
            self.assertEqual(calls[0][calls[0].index("--engine")+1],"async")
            self.assertNotIn("--titles",calls[0])
            self.assertNotIn("--dry-run",calls[0])
            self.assertEqual(self.db.execute("SELECT priority FROM fleet_work_units").fetchone()[0],3)
            receipt=self.db.execute("""SELECT archive_delta,duplicates,parsed_messages,
              fetched_messages FROM fleet_archive_receipts""").fetchone()
            self.assertEqual(receipt,(2,1,4,4))
            self.assertEqual(self.db.execute("SELECT count(*) FROM fleet_gap_receipts").fetchone()[0],1)
            self.assertEqual(refresh_work_evidence(self.db,work,cid,provider)["archive_replayed"],True)
            self.assertEqual(self.db.execute("SELECT count(*) FROM fleet_archive_receipts").fetchone()[0],1)
            self.assertEqual(self.db.execute("SELECT count(*) FROM fleet_gap_receipts").fetchone()[0],1)

    def test_async_rejection_and_missing_gap_are_deferred(self):
        import json,tempfile
        from pathlib import Path
        from types import SimpleNamespace
        cid="123e4567-e89b-42d3-a456-426614174000"
        with tempfile.TemporaryDirectory() as td:
            puller=Path(td)/"pull.py";puller.touch()
            archive=Path(td)/"archive.db";archive.touch()
            work=upsert_work(self.db,"gap",[cid],["node"],1)
            count=[]
            def reject(cmd,**kwargs):
                count.append(1)
                return SimpleNamespace(returncode=0,stdout=json.dumps({
                    "requested_targets":1,"selected_id_filters":1,
                    "async":{"total":1,"ok":0,"failures":1},"source_id":"x","ingest":{"inserted":0,"duplicates":0,"parsed_messages":0,"artifacts":{}}}))
            p=exact_async_archive_provider(str(puller),str(archive),"main",runner=reject)
            self.assertEqual(refresh_work_evidence(self.db,work,cid,p)["stage"],"deferred")
            self.assertEqual(len(count),1)
            def accepted(cmd,**kwargs):
                return SimpleNamespace(returncode=0,stdout=json.dumps({
                    "requested_targets":1,"selected_id_filters":1,
                    "async":{"total":1,"ok":1,"failures":0,"messages":2},
                    "source_id":"x","ingest":{"inserted":1,"duplicates":1,"parsed_messages":2,"artifacts":{}}}))
            p=exact_async_archive_provider(str(puller),str(archive),"main",runner=accepted)
            result=refresh_work_evidence(self.db,work,cid,p)
            self.assertEqual(result["stage"],"deferred")
            self.assertEqual(result["archive_stage"],"ingested")
            self.assertEqual(self.db.execute("SELECT archive_delta FROM fleet_archive_receipts").fetchone()[0],1)
            self.assertEqual(self.db.execute("SELECT count(*) FROM fleet_gap_receipts").fetchone()[0],0)
            formal=Path(td)/"f.agda";formal.touch()
            world=Path(td)/"w.slrw";world.touch()
            def gap(*args):
                return SimpleNamespace(unmatched_informal_factors=2,
                    unmatched_formal_factors=0,matched_semantic_factors=1)
            receipt=result["archive_receipt_digest"]
            attached=attach_gap_to_archive(self.db,work,cid,receipt,str(formal),str(world),gap)
            self.assertEqual(attached["stage"],"rescored")
            self.assertTrue(attach_gap_to_archive(self.db,work,cid,receipt,
                str(formal),str(world),gap)["replayed"])
            self.assertEqual(self.db.execute("SELECT count(*) FROM fleet_archive_receipts").fetchone()[0],1)
            self.assertEqual(self.db.execute("SELECT count(*) FROM fleet_gap_receipts").fetchone()[0],1)

if __name__ == "__main__": unittest.main()
