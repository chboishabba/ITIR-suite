"""Offline negative controls for the read-only ITIR formal gap-join CLI."""
import importlib.util
import pathlib
import unittest

PATH = pathlib.Path(__file__).resolve().parents[1] / "scripts" / "formal_gap_join.py"
SPEC = importlib.util.spec_from_file_location("formal_gap_join", PATH)
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


class GapJoinTests(unittest.TestCase):
    def setUp(self):
        self.item = {
            "obligation_ref": "DASHI.Obligation.Hecke",
            "query": "Hecke prime-power recurrence",
            "target_prover": "lean",
            "statement_digest": "a"*64,
        }

    @staticmethod
    def good(kind):
        return {"candidate_only": True, "establishes_proof": False,
                "authority_kind": kind, "summary": {"results": []}}

    def test_candidate_only_with_exact_statement_digest(self):
        seen = []
        def inspect(payload):
            seen.append(("inspect", payload))
            return self.good("similarity")
        def route(payload):
            seen.append(("route", payload))
            return self.good("obligation_routing")
        output = mod.join_one(self.item, inspect, route)
        self.assertTrue(output["candidate_only"])
        self.assertFalse(output["discharges_obligation"])
        self.assertEqual(seen[1][1]["statement_digest"], "a"*64)
        self.assertEqual(seen[1][1]["target_prover"], "lean")

    def test_refuse_actor_supplied_promotion(self):
        def fake(_):
            return {"candidate_only": False, "establishes_proof": True}
        with self.assertRaisesRegex(ValueError, "non-candidate"):
            mod.join_one(self.item, fake, fake)

    def test_no_duplicate_obligations(self):
        def fake(_):
            return self.good("similarity")
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            mod.run([self.item, self.item], fake, fake)

    def test_reject_invalid_digest_and_prover(self):
        def fake(_):
            return self.good("similarity")
        for override in ({"statement_digest": "incorrect"},
                         {"target_prover": "ai"}):
            with self.subTest(override=override):
                with self.assertRaises(ValueError):
                    mod.join_one({**self.item, **override}, fake, fake)

    def test_bounded_batch(self):
        def fake(_):
            raise AssertionError("must not invoke provider")
        with self.assertRaisesRegex(ValueError, "bounded batch"):
            mod.run([self.item] * 501, fake, fake)

    def test_deterministic_and_no_proof_promotion(self):
        def fake(_):
            return self.good("similarity")
        b = {**self.item, "obligation_ref": "second"}
        result = mod.run([b, self.item], fake, fake)
        self.assertEqual([x["obligation_ref"] for x in result],
                         ["DASHI.Obligation.Hecke", "second"])
        self.assertTrue(all(x["establishes_proof"] is False for x in result))


if __name__ == "__main__":
    unittest.main()
