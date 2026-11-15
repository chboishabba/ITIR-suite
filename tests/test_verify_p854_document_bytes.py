"""Actual document-byte receipt joining, no semantic/source authority inflation."""
from hashlib import sha256
from pathlib import Path
import sys
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from verify_p854_document_bytes import check_document


def fixtures(tmp_path):
    raw = b"%PDF-1.4 synthetic fixture, NOT a real primary report"
    path = tmp_path / "sample.pdf"
    path.write_bytes(raw)
    url = "https://example.org/primary.pdf"
    native = {
        "source_kind": "full-wikibase-json-entity",
        "same_source_native_statement_found": True,
        "snapshot_bytes_match_pinned_digest": True,
        "subject_qid": "Q123", "statement_guid": "Q123$guid",
        "native_entity_revision_id": 123,
        "raw_entity_sha256_checked": "a" * 64,
        "p854_url_candidates": [url],
    }
    acquisition = {
        "source_kind": "p854-document", "requested_url": url,
        "final_url": url, "download_performed": True,
        "observed_sha256": sha256(raw).hexdigest(), "bytes_written": len(raw),
        "expected_sha256": None,
    }
    return native, acquisition, path


def test_observed_document_keeps_review_and_source_payment_open(tmp_path):
    native, acquisition, path = fixtures(tmp_path)
    result = check_document(native=native, acquisition=acquisition, raw_document=path)
    assert result["actual_document_bytes_compared_with_acquisition"] is True
    assert result["independent_digest_pin_supplied"] is False
    for field in ("document_content_semantically_inspected",
                  "primary_document_support_for_claim_verified",
                  "reviewer_disposition_persisted",
                  "source_support_paid", "edit_authority"):
        assert result[field] is False


@pytest.mark.parametrize("field,value", [
    ("requested_url", "https://example.org/forged.pdf"),
    ("download_performed", False), ("source_kind", "wikibase-entity"),
    ("observed_sha256", "f" * 64), ("bytes_written", 1),
    ("expected_sha256", "1" * 64),
])
def test_tampered_acquisition_refused(tmp_path, field, value):
    native, acquisition, path = fixtures(tmp_path)
    acquisition[field] = value
    with pytest.raises(ValueError):
        check_document(native=native, acquisition=acquisition, raw_document=path)


def test_tampered_original_native_statement_refused(tmp_path):
    native, acquisition, path = fixtures(tmp_path)
    native["same_source_native_statement_found"] = False
    with pytest.raises(ValueError):
        check_document(native=native, acquisition=acquisition, raw_document=path)


def test_truncated_or_overbudget_document_refused(tmp_path):
    native, acquisition, path = fixtures(tmp_path)
    with pytest.raises(ValueError):
        check_document(native=native, acquisition=acquisition,
                       raw_document=path, max_bytes=2)
    path.unlink()
    with pytest.raises(ValueError):
        check_document(native=native, acquisition=acquisition, raw_document=path)
