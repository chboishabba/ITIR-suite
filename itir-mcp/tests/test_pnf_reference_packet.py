"""Token-free, database-free reference packet boundary tests."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from itir_mcp.pnf_reference_packet import reference_work_packet
from itir_mcp.registry import build_default_registry
from itir_mcp.contracts import ToolInputError

BASE={"pg_dsn":"dbname=fixture","source_ref":"thread-1",
      "work_ref":"work-1","world_ref":"world-1"}

class Cursor:
    def __init__(self):
        self.calls=[]
        self.rows=[]
    def __enter__(self): return self
    def __exit__(self,*a): return False
    def execute(self,sql,args):
        self.calls.append((sql,args))
        if "FROM corpus.chat_archive_message" in sql:
            self.rows=[("msg-1","node-1",None,"active","user","2026","thread-1",
                "sqlite:archive#node-1","a"*64,"rev-1","[]")]
        elif "FROM corpus.source_statement" in sql:
            self.rows=[("rev-1","role","dep",0,4,"batch")]
        else:
            self.rows=[("cmp","rev-1","rev-2","consumer","sha256:abc")]
    def fetchall(self):return self.rows

class Conn:
    def __init__(self):self.cursor_obj=Cursor()
    def __enter__(self):return self
    def __exit__(self,*a):return False
    def cursor(self):return self.cursor_obj

class Tests(unittest.TestCase):
    def test_registry_and_packet_cap(self):
        spec=build_default_registry().get_tool_spec("itir.pnf.reference_work_packet")
        self.assertTrue(spec.read_only)
        self.assertFalse(spec.input_schema["additionalProperties"])
        conn=Conn()
        out=reference_work_packet({**BASE,"limit":1},connect=lambda _:conn)
        self.assertEqual(len(out["source_refs"]),1)
        self.assertEqual(len(out["factor_signatures"]),1)
        self.assertEqual(len(out["comparison_receipts"]),1)
        self.assertIsNone(out["raw_text"])
        self.assertEqual(out["authority"],"evidence_only")
        self.assertEqual(conn.cursor_obj.calls[0][1],("thread-1",1))
    def test_guard_drill_down_no_database_or_raw(self):
        with self.assertRaises(ToolInputError):
            reference_work_packet({**BASE,"drill_down":True},connect=lambda _:None)
        out=reference_work_packet({**BASE,"drill_down":True,"max_chars":64},
            connect=lambda _:self.fail("DB access"))
        self.assertIsNone(out["raw_text"])
        self.assertIn("canonical_archive_verified_drill_down_not_materialised",
                      out["missing_evidence"])
    def test_invalid_cap_and_extra_fields(self):
        for args in ({"limit":25},{"limit":0},{"surprise":"x"}):
            with self.assertRaises(ToolInputError):
                reference_work_packet({**BASE,**args},connect=lambda _:self.fail("DB"))
    def test_no_promotion_and_safe_envelope(self):
        r=build_default_registry().safe_invoke("itir.pnf.reference_work_packet",
            {**BASE,"drill_down":True,"max_chars":32})
        self.assertTrue(r["ok"],r)
        out=r["result"]["result"]
        self.assertTrue(out["candidate_only"])
        self.assertNotIn("promoted",out)
        self.assertIsNone(out["raw_text"])

if __name__=="__main__":unittest.main()
