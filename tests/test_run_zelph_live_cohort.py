"""Pure same-source crosswalk controls: zero invented entity/FLN authority."""
from copy import deepcopy
from pathlib import Path
import sys
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from run_zelph_live_cohort import build_source_bound_candidate


def example():
    physical = {
        "dataset_revision": "a" * 40, "manifest_sha256": "b" * 64,
        "source_bin_external_digest_matched_in_this_run": True,
        "original_packed_manifest_full_offset_cover_checked_in_this_run": True,
        "source_bin_ranges_reverified_in_same_native_audit": True,
        "selected_root_one_hop_equal_original_bin": True,
        "finite_words_complete": True,
        "source_support_paid": False, "p854_document_verified": False,
        "edit_authority": False,
        "route_raw_sha256": "1" * 64, "range_proof_raw_sha256": "2" * 64,
        "native_answer_raw_sha256": "3" * 64,
        "original_packed_partition_raw_sha256": "4" * 64,
    }
    route = {
        "routeVersion": "zelph-filtered-route/v1",
        "requestedQids": ["Q123"], "qidToZelphNodeIds": {"Q123": 42},
    }
    native = {
        "subject_qid": "Q123", "statement_guid": "Q123$abc",
        "property_id": "P14143", "source_kind": "full-wikibase-json-entity",
        "native_entity_revision_id": 1001, "raw_entity_sha256_checked": "a" * 64,
        "snapshot_bytes_match_pinned_digest": True,
        "same_source_native_statement_found": True,
        "p854_url_candidates": ["https://example.org/primary.pdf"],
        "native_quantity": {"amount": "+12", "unit": "1"},
        "references": [{"snaks": []}], "qualifiers": [],
        "edit_authority": False, "reviewed_source_support_paid": False,
    }
    return physical, route, native


def output(physical=None, route=None, native=None):
    p, r, n = example()
    return build_source_bound_candidate(
        physical=p if physical is None else physical,
        route=r if route is None else route,
        native=n if native is None else native,
        qid="Q123", source_bin_sha256="9" * 64,
    )


def test_valid_same_qid_remains_non_authoritative():
    result = output()
    assert result["zelph_internal_node_id"] == 42
    assert result["declared_lr_query_family_complete"]
    for flag in ("wikibase_entity_revision_equals_graph_dataset_revision_proved",
                 "wikipedia_oldid_first_qualified_link_same_as_zelph_edge_proved",
                 "upstream_http_origin_independently_authenticated_here",
                 "p854_primary_documents_independently_verified",
                 "persisted_s29_review_verified", "source_support_paid",
                 "creates_world_truth", "edit_authority"):
        assert result[flag] is False


@pytest.mark.parametrize("field", [
    "source_bin_external_digest_matched_in_this_run",
    "original_packed_manifest_full_offset_cover_checked_in_this_run",
    "source_bin_ranges_reverified_in_same_native_audit",
    "selected_root_one_hop_equal_original_bin", "finite_words_complete",
])
def test_missing_original_object_gate_refused(field):
    p, r, n = example()
    p[field] = False
    with pytest.raises(ValueError):
        output(physical=p)


@pytest.mark.parametrize("field", ["source_support_paid", "p854_document_verified", "edit_authority"])
def test_forged_physical_payment_refused(field):
    p, r, n = example()
    p[field] = True
    with pytest.raises(ValueError):
        output(physical=p)


@pytest.mark.parametrize("field,value", [
    ("subject_qid", "Q999"), ("snapshot_bytes_match_pinned_digest", False),
    ("same_source_native_statement_found", False),
    ("edit_authority", True), ("reviewed_source_support_paid", True),
])
def test_mismatched_or_promoted_wikibase_entity_refused(field, value):
    p, r, n = example()
    n[field] = value
    with pytest.raises(ValueError):
        output(native=n)


def test_route_node_and_qid_must_be_exact():
    p, r, n = example()
    r["qidToZelphNodeIds"] = {"Q123": True}
    with pytest.raises(ValueError):
        output(route=r)
    r["qidToZelphNodeIds"] = {"Q999": 42}
    with pytest.raises(ValueError):
        output(route=r)


def test_absent_finite_query_family_refused():
    p, r, n = example()
    p["finite_words_complete"] = None
    with pytest.raises(ValueError):
        output(physical=p)
