"""Deterministic offline max-cut tests for resumable complete name-section bytes."""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import audit_zelph_hf_name_section_bytes as audit

REV = "a" * 40
MAN = "b" * 64
IDX = "c" * 64
SIZE = 1000000


def setup(monkeypatch, tmp_path, count=3):
    m = tmp_path / "manifest.json"
    i = tmp_path / "index.json"
    m.write_text("{}")
    i.write_text("{}")
    rows = {
        ("nodeOfName", n): {
            "offset": 25 + n * 8, "length": 8,
            "object_uri": f"hf://datasets/acrion/zelph/original/shards/nodeOfName/chunk-{n:06d}-wikidata.capnp-packed"
        } for n in range(count)
    }
    def crosswalk(**kwargs):
        assert kwargs["manifest_sha256"] == MAN
        return {
            "original_index_raw_sha256_rechecked": IDX,
            "original_bin_size_bytes": SIZE,
            "section_chunk_counts": {"nodeOfNameChunkCount": count},
        }
    monkeypatch.setattr(audit, "verify_index_manifest_files", crosswalk)
    monkeypatch.setattr(audit, "_read_json", lambda *_args: {})
    monkeypatch.setattr(audit, "_manifest_index", lambda *_args: rows)
    fetched = []
    def verify(*, section, chunk_index, **kwargs):
        assert section == "nodeOfName"
        fetched.append(chunk_index)
        row = rows[(section, chunk_index)]
        digest = sha256(bytes([chunk_index]) * 8).hexdigest()
        return {
            "version": audit._VERSION, "dataset_revision": REV,
            "original_manifest_raw_sha256": MAN,
            "original_index_raw_sha256": IDX,
            "source_bin_size_bytes": SIZE,
            "section": section, "chunk_index": chunk_index,
            "original_source_offset": row["offset"],
            "source_range_end_inclusive": row["offset"] + row["length"] - 1,
            "bytes_compared": row["length"],
            "published_object_uri": row["object_uri"],
            "original_binary_uri": "hf://datasets/acrion/zelph/wikidata-20260309-all.bin",
            "published_shard_http_status": 200,
            "original_source_http_status": 206,
            "published_shard_raw_sha256": digest,
            "original_packed_range_raw_sha256": digest,
            "exact_original_packed_bytes_equal_published_shard": True,
            "full_index_manifest_offset_cover_checked": True,
            "original_qid_route_verified": False,
            "whole_name_domain_enumerated": False,
            "all_query_frontiers_closed": False,
            "native_p854_source_support_paid": False,
            "s29_persistence_paid": False, "edit_authority": False,
        }
    monkeypatch.setattr(audit, "verify_direct_original_chunk", verify)
    return {
        "manifest_path": m, "original_index_path": i,
        "manifest_sha256": MAN, "dataset_revision": REV,
        "original_index_sha256": IDX,
        "section": "nodeOfName", "receipts_dir": tmp_path / "receipts",
    }, fetched


def test_default_plan_is_offline_and_cannot_claim_full_a1(monkeypatch, tmp_path):
    params, fetched = setup(monkeypatch, tmp_path)
    result = audit.audit_name_section(**params)
    assert not fetched
    assert result["planned_chunk_indices"] == [0, 1, 2]
    assert result["all_name_section_packed_payload_bytes_verified"] is False
    assert result["full_A1_name_domain_theorem_instantiated"] is False
    assert result["all_native_name_rows_decoded"] is False
    assert not params["receipts_dir"].exists()


def test_two_bounded_runs_complete_only_byte_cover(monkeypatch, tmp_path):
    params, fetched = setup(monkeypatch, tmp_path)
    first = audit.audit_name_section(**params, execute=True, max_new_chunks=2)
    assert fetched == [0, 1]
    assert first["verified_chunk_count"] == 2
    assert first["all_name_section_packed_payload_bytes_verified"] is False
    second = audit.audit_name_section(**params, execute=True, max_new_chunks=2)
    assert fetched == [0, 1, 2]
    assert second["verified_chunk_count"] == 3
    assert second["all_name_section_packed_payload_bytes_verified"] is True
    assert second["full_A1_name_domain_theorem_instantiated"] is False
    assert second["collision_preserving_name_fibres_verified"] is False
    assert len(second["receipt_hashes"]) == 3


def test_exact_resume_does_not_request_old_source_range(monkeypatch, tmp_path):
    params, fetched = setup(monkeypatch, tmp_path)
    audit.audit_name_section(**params, execute=True, max_new_chunks=3)
    assert len(fetched) == 3
    again = audit.audit_name_section(**params, execute=True, max_new_chunks=3)
    assert len(fetched) == 3
    assert again["network_executed"] is False


@pytest.mark.parametrize("field,bad", [
    ("dataset_revision", "d"*40),
    ("original_manifest_raw_sha256", "f"*64),
    ("original_source_offset", 12345),
    ("bytes_compared", 7),
    ("exact_original_packed_bytes_equal_published_shard", False),
    ("original_qid_route_verified", True),
    ("published_shard_raw_sha256", "f"*64),
])
def test_tampered_retained_byte_receipt_blocks_resume(monkeypatch, tmp_path, field, bad):
    params, fetched = setup(monkeypatch, tmp_path)
    audit.audit_name_section(**params, execute=True, max_new_chunks=1)
    p = params["receipts_dir"] / "nodeOfName-000000.json"
    receipt = json.loads(p.read_text())
    receipt[field] = bad
    p.write_text(json.dumps(receipt))
    with pytest.raises(ValueError, match="receipt|digest"):
        audit.audit_name_section(**params, execute=True, max_new_chunks=2)
    assert fetched == [0]


def test_duplicate_json_fields_cannot_be_retained_evidence(monkeypatch, tmp_path):
    params, fetched = setup(monkeypatch, tmp_path)
    audit.audit_name_section(**params, execute=True, max_new_chunks=1)
    p = params["receipts_dir"] / "nodeOfName-000000.json"
    data = p.read_text()
    p.write_text(data[:-2] + ', "edit_authority": true}')
    with pytest.raises(ValueError, match="duplicate receipt JSON"):
        audit.audit_name_section(**params)


def test_symlinked_receipt_or_directory_rejected(monkeypatch, tmp_path):
    params, fetched = setup(monkeypatch, tmp_path)
    params["receipts_dir"].symlink_to(tmp_path, target_is_directory=True)
    with pytest.raises(ValueError, match="symlink"):
        audit.audit_name_section(**params, execute=True)


def test_explicit_network_budget_and_zero_chunk_cap(monkeypatch, tmp_path):
    params, fetched = setup(monkeypatch, tmp_path)
    plan = audit.audit_name_section(**params, max_new_chunks=0)
    assert plan["planned_chunk_indices"] == []
    assert plan["deferred_chunk_indices"] == [0, 1, 2]
    result = audit.audit_name_section(**params, execute=True, max_new_chunks=0)
    assert result["network_executed"] is False
    assert fetched == []


def test_wrong_name_section_and_invalid_revision_fail_closed(monkeypatch, tmp_path):
    params, fetched = setup(monkeypatch, tmp_path)
    with pytest.raises(ValueError, match="named sections"):
        audit.audit_name_section(**{**params, "section": "left"}, execute=True)
    with pytest.raises(ValueError, match="immutable"):
        audit.audit_name_section(**{**params, "dataset_revision": "main"}, execute=True)
    assert fetched == []
