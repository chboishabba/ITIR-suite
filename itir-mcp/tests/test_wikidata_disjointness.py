"""Tests for itir.wikidata.disjointness_report MCP tool."""

from __future__ import annotations

from pathlib import Path
import unittest

from itir_mcp.contracts import ToolInputError
from itir_mcp.registry import build_default_registry
from itir_mcp.wikidata_disjointness_tool import wikidata_disjointness_report


class TestWikidataDisjointnessTool(unittest.TestCase):
    def setUp(self) -> None:
        self.repo_root = Path(__file__).resolve().parents[2]
        self.fixture_path = (
            self.repo_root
            / "SensibLaw"
            / "tests"
            / "fixtures"
            / "wikidata"
            / "disjointness_p2738_pilot_pack_v1"
            / "slice.json"
        )

    def test_disjointness_report_from_fixture_path(self) -> None:
        self.assertTrue(self.fixture_path.is_file(), f"Fixture missing: {self.fixture_path}")
        res = wikidata_disjointness_report({"slice_path": str(self.fixture_path)})

        self.assertEqual(res["version"], "itir.wikidata.disjointness_report.v1")
        self.assertTrue(res["authority_boundary"]["candidate_only"])
        self.assertTrue(res["authority_boundary"]["read_only"])
        self.assertFalse(res["authority_boundary"]["canonical_truth_mutated"])

        summary = res["summary"]
        self.assertGreater(summary["disjoint_pairs_count"], 0)
        self.assertGreater(summary["subclass_violations_count"], 0)
        self.assertGreater(summary["culprit_classes_count"], 0)

        report = res["report"]
        self.assertIn("disjoint_pairs", report)
        self.assertIn("subclass_violations", report)
        self.assertIn("culprit_classes", report)

    def test_disjointness_report_invalid_input(self) -> None:
        with self.assertRaises(ToolInputError):
            wikidata_disjointness_report({})

        with self.assertRaises(ToolInputError):
            wikidata_disjointness_report({"slice_path": "/nonexistent/path/slice.json"})

    def test_registry_registration(self) -> None:
        registry = build_default_registry()
        spec = registry.get_tool_spec("itir.wikidata.disjointness_report")
        self.assertIsNotNone(spec)
        self.assertTrue(spec.read_only)
        self.assertEqual(spec.name, "itir.wikidata.disjointness_report")


if __name__ == "__main__":
    unittest.main()
