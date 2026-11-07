"""Fail-closed candidate-only biology source ingestion tests."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "itir-mcp" / "src"
sys.path.insert(0, str(ROOT))

from itir_mcp.biological_source_candidate_adapter import (
    project_biological_sources,
)


def source():
    return {
        "status": "unpromoted-source-intake",
        "pnf_mutation_performed": False,
        "biological_calibration_proven": False,
        "gocam": {
            "model_id": "gomodel:synthetic",
            "sha256": "a"*64,
            "schema_validated": False,
            "activities": [
                {"id":"g:A","causal_associations":[
                    {"predicate":"RO:0002629",
                     "downstream_activity":"g:B",
                     "evidence":[{"reference":"PMID:123"}]}]},
                {"id":"g:B","causal_associations":[]},
            ],
        },
        "sbml": {
            "model_id": "synthetic", "sha256":"b"*64,
            "schema_validated":False,
            "reactions":[{"id":"R1"}],
        },
        "candidate_joins": [{
            "gocam_activity":"g:A","sbml_reaction":"R1",
            "evidence_reference":"PMID:123","trusted":False,
        }],
    }


def spatial():
    return {
        "status": "source-matched-spatial-observation-not-kinetic-mechanism",
        "pnf_mutation_performed": False,
        "original_source_digest_verified_by_independent_fetch": False,
        "transport_mode_claim_independently_validated": False,
        "source_id": "spatial:synthetic",
        "original_source": "spatial:synthetic",
        "source_sha256": "d"*64,
        "original_csv_sha256": "d"*64,
        "original_source_sha256_declared": "e"*64,
        "original_measurement_rows": 2,
        "context_measurements": [
            {
                "specimen":"s1", "time_s":"0", "region":"blood",
                "compartment":"plasma", "bh4_amount_mol":"0.000002",
                "bh2_amount_mol":"0.000001",
                "connection_id":"a", "transport_mode":"vascular_perfusion",
                "transport_source_reference":"source-only:test",
                "experiment":"exp1", "split":"test",
            },
            {
                "specimen":"s1", "time_s":"0", "region":"endothelium",
                "compartment":"cytosol", "bh4_amount_mol":"0.000001",
                "bh2_amount_mol":"0.000002",
                "connection_id":"a", "transport_mode":"plasma_membrane",
                "transport_source_reference":"source-only:test",
                "experiment":"exp1", "split":"test",
            },
        ],
    }


class BiologyWorldModelTests(unittest.TestCase):
    def test_canonical_candidate_identity_and_no_promotion(self):
        a=project_biological_sources(source())
        b=project_biological_sources(source())
        self.assertEqual(a,b)
        self.assertEqual(a["bundle_id"],b["bundle_id"])
        self.assertFalse(a["pnf_promotion"])
        self.assertFalse(a["postgres_mutation"])
        self.assertFalse(a["source_statement_parser_invoked"])
        self.assertTrue(a["candidate_statements"][0]["candidate_only"])
        self.assertFalse(a["candidate_joins"][0]["identity_established"])
        self.assertEqual(a["candidate_joins"][0]["original_evidence_reference"],
                         "PMID:123")

    def test_missing_evidence_rejected(self):
        r=source()
        r["gocam"]["activities"][0]["causal_associations"][0]["evidence"]=[]
        with self.assertRaises(ValueError):
            project_biological_sources(r)

    def test_untrusted_and_join_endpoint_required(self):
        r=source()
        r["candidate_joins"][0]["trusted"]=True
        with self.assertRaises(ValueError):
            project_biological_sources(r)
        r=source()
        r["candidate_joins"][0]["sbml_reaction"]="MISSING"
        with self.assertRaises(ValueError):
            project_biological_sources(r)

    def test_join_evidence_requires_selected_original_activity(self):
        r=source()
        r["candidate_joins"][0]["evidence_reference"]="PMID:UNSUPPORTED"
        with self.assertRaises(ValueError):
            project_biological_sources(r)
        # Even a reference present on a *different* original activity
        # cannot be used to assert this selected activity/reaction join.
        r=source()
        r["gocam"]["activities"][1]["molecular_function_evidence"]=[
            {"reference":"PMID:OTHER"}
        ]
        r["candidate_joins"][0]["evidence_reference"]="PMID:OTHER"
        with self.assertRaises(ValueError):
            project_biological_sources(r)

    def test_reject_mutation_and_corrupt_source(self):
        r=source()
        r["pnf_mutation_performed"]=True
        with self.assertRaises(ValueError):
            project_biological_sources(r)
        r=source()
        r["gocam"]["sha256"]="not-a-hash"
        with self.assertRaises(ValueError):
            project_biological_sources(r)

    def test_spatial_assay_preserves_compartment_and_transport_candidate(self):
        bundle = project_biological_sources(source(), spatial_measurement=spatial())
        candidate = bundle["spatial_observation_candidates"]
        self.assertTrue(candidate["candidate_only"])
        self.assertEqual(candidate["measured_csv_sha256"], "d"*64)
        self.assertEqual(len(candidate["same_specimen_context_rows"]), 2)
        self.assertEqual(candidate["same_specimen_context_rows"][0]["region"], "blood")
        self.assertEqual(candidate["same_specimen_context_rows"][1]["compartment"], "cytosol")
        self.assertFalse(candidate["same_physical_model_established"])
        self.assertFalse(candidate["transport_law_validated"])
        self.assertFalse(bundle["pnf_promotion"])

    def test_spatial_assay_rejects_unanchored_or_false_source_identity(self):
        r = spatial()
        r["source_sha256"] = "f"*64
        with self.assertRaises(ValueError):
            project_biological_sources(source(), spatial_measurement=r)
        r = spatial()
        r["context_measurements"][0]["transport_source_reference"] = ""
        with self.assertRaises(ValueError):
            project_biological_sources(source(), spatial_measurement=r)
        r = spatial()
        r["context_measurements"][0]["transport_mode"] = "teleport"
        with self.assertRaises(ValueError):
            project_biological_sources(source(), spatial_measurement=r)
        r = spatial()
        r["context_measurements"][1] = r["context_measurements"][0].copy()
        with self.assertRaises(ValueError):
            project_biological_sources(source(), spatial_measurement=r)
        r = spatial()
        r["transport_mode_claim_independently_validated"] = True
        with self.assertRaises(ValueError):
            project_biological_sources(source(), spatial_measurement=r)
        r = spatial()
        r["context_measurements"][0]["bh4_amount_mol"] = "-1"
        with self.assertRaises(ValueError):
            project_biological_sources(source(), spatial_measurement=r)

    def test_assay_remains_separate_evidence(self):
        kin={
            "source_id":"assay:1","source_sha256":"c"*64,
            "status":"model-fit-only-not-mechanism-validated",
            "pnf_mutation_performed":False,
        }
        case=project_biological_sources(source(),kinetic_calibration=kin)
        self.assertEqual(len(case["assay_evidence"]),1)
        self.assertFalse(case["assay_evidence"][0]["bio_model_identity_established"])


if __name__=="__main__":
    unittest.main()
