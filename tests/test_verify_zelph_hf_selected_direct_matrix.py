"""P0-S exact full-domain selection, cumulative budget, and fail-closed receipts.

The individual network-backed parity verifier has separate four-section mocked
HTTP tests. These exercise the selector and aggregate receipt *without network*.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import sys

import pytest

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))
from verify_zelph_hf_selected_direct_matrix import (
    parse_keys, plan_matrix, execute_matrix,
)
from test_verify_zelph_hf_original_header import _fixture, REV

KEYS = ["left:0", "right:0", "nameOfNode:0", "nodeOfName:0"]


def pinned(tmp_path):
    manifest, index = _fixture()
    a, b = tmp_path / "manifest.json", tmp_path / "index.json"
    a.write_text(json.dumps(manifest, sort_keys=True))
    b.write_text(json.dumps(index, sort_keys=True))
    return dict(
        manifest_path=a, original_index_path=b,
        dataset_revision=REV,
        manifest_sha256=sha256(a.read_bytes()).hexdigest(),
        original_index_sha256=sha256(b.read_bytes()).hexdigest(),
    )


def selected(tmp_path, chosen=KEYS, **changes):
    kwargs = dict(**pinned(tmp_path), keys=parse_keys(list(chosen)))
    kwargs.update(changes)
    return plan_matrix(**kwargs)


@pytest.mark.parametrize("bad", [
    [], ["left:-1"], ["left:1.0"], ["nameOfNode:foo"],
    ["other:0"], ["left:0", "left:00"], ["left:4294967296"],
    ["left:0", "left:0"], [True],
])
def test_invalid_chunk_selector_fails_before_any_network(bad):
    with pytest.raises(ValueError):
        parse_keys(bad)


def test_exact_full_index_geometry_preflight_and_two_sided_budget(tmp_path):
    plan = selected(tmp_path)
    assert plan["complete_original_index_geometry_checked"] is True
    assert plan["selected_chunk_count"] == 4
    assert [r["section"] for r in plan["entries"]] == [
        "left", "right", "nameOfNode", "nodeOfName"]
    assert plan["total_two_sided_payload_bytes"] == (
        2 * plan["selected_bytes_each_source"]
    )
    assert plan["network_executed"] is False
    assert plan["qid_routes_verified"] is False


def test_invalid_or_tampered_pinned_metadata_rejected(tmp_path):
    kwargs = pinned(tmp_path)
    kwargs["manifest_sha256"] = "0" * 64
    with pytest.raises(ValueError):
        plan_matrix(**kwargs, keys=parse_keys(KEYS))
    kwargs = pinned(tmp_path)
    kwargs["original_index_sha256"] = "0" * 64
    with pytest.raises(ValueError):
        plan_matrix(**kwargs, keys=parse_keys(KEYS))


def test_off_manifest_selector_and_budget_fail_before_http(tmp_path):
    with pytest.raises(ValueError, match="missing"):
        selected(tmp_path, ["left:999"])
    with pytest.raises(ValueError, match="budget"):
        selected(tmp_path, max_total_mib=0)
    with pytest.raises(ValueError, match="budget"):
        selected(tmp_path, max_chunk_mib=0)
    with pytest.raises(ValueError):
        selected(tmp_path, max_total_mib=True)


def mock_witness(plan, *, tamper_key=None, fail_key=None):
    index = {(row["section"], row["chunk_index"]): row for row in plan["entries"]}
    def verify_one(**kwargs):
        key = (kwargs["section"], kwargs["chunk_index"])
        if key == fail_key:
            raise ValueError("original HTTP206 byte mismatch")
        row = index[key]
        digest = sha256(f"{key}".encode()).hexdigest()
        return {
            "version": "itir.zelph.direct_original_selected_chunk_equality.v1",
            "dataset_revision": plan["revision"],
            "original_manifest_raw_sha256": plan["manifest_sha256"],
            "original_index_raw_sha256": plan["index_sha256"],
            "section": row["section"], "chunk_index": row["chunk_index"],
            "original_source_offset": row["source_offset"],
            "source_range_end_inclusive": row["source_end_inclusive"],
            "bytes_compared": row["bytes"],
            "published_object_uri": row["published_object_uri"],
            "original_source_http_status": 206,
            "exact_original_packed_bytes_equal_published_shard": key != tamper_key,
            "full_index_manifest_offset_cover_checked": True,
            "original_packed_range_raw_sha256": digest,
            "published_shard_raw_sha256": digest,
            "original_bin_full_digest_verified": False,
            "original_qid_route_verified": False,
            "all_query_frontiers_closed": False,
            "native_p854_source_support_paid": False,
            "s29_persistence_paid": False, "edit_authority": False,
        }
    return verify_one


def test_complete_selected_four_section_matrix_writes_exact_receipts(tmp_path):
    inputs = pinned(tmp_path)
    plan = plan_matrix(**inputs, keys=parse_keys(KEYS))
    outdir = tmp_path / "verified"
    outcome = execute_matrix(plan=plan, evidence_dir=outdir,
                             verify_one=mock_witness(plan), **{
        "manifest_path": inputs["manifest_path"],
        "original_index_path": inputs["original_index_path"],
    })
    assert outcome["selected_chunk_count"] == 4
    assert outcome["all_explicitly_selected_chunks_byte_equal"] is True
    assert outcome["all_original_chunks_byte_checked"] is False
    assert outcome["qid_routes_verified"] is False
    assert outcome["full_original_bin_sha256_verified"] is False
    assert len(list(outdir.glob("*.json"))) == 5
    for entry in outcome["selected_receipts"]:
        assert sha256((outdir / entry["receipt_file"]).read_bytes()).hexdigest() == (
            entry["receipt_sha256"]
        )
    assert json.loads((outdir / "selected-matrix-complete.json").read_text()) == outcome
    with pytest.raises(ValueError, match="exists"):
        execute_matrix(plan=plan, evidence_dir=outdir,
                       verify_one=mock_witness(plan), **{
            "manifest_path": inputs["manifest_path"],
            "original_index_path": inputs["original_index_path"],
        })


def test_mid_matrix_remote_mismatch_preserves_prior_witness_but_no_final(tmp_path):
    inputs = pinned(tmp_path)
    plan = plan_matrix(**inputs, keys=parse_keys(KEYS))
    outdir = tmp_path / "partial"
    with pytest.raises(ValueError, match="HTTP206 byte mismatch"):
        execute_matrix(plan=plan, evidence_dir=outdir,
                       verify_one=mock_witness(plan, fail_key=("nameOfNode", 0)),
                       manifest_path=inputs["manifest_path"],
                       original_index_path=inputs["original_index_path"])
    assert (outdir / "left-000000.json").is_file()
    assert (outdir / "right-000000.json").is_file()
    assert not (outdir / "selected-matrix-complete.json").exists()


def test_caller_supplied_equality_boolean_cannot_override_wrong_witness(tmp_path):
    inputs = pinned(tmp_path)
    plan = plan_matrix(**inputs, keys=parse_keys(KEYS))
    outdir = tmp_path / "tamper"
    with pytest.raises(ValueError, match="identity, equality, or authority"):
        execute_matrix(plan=plan, evidence_dir=outdir,
                       verify_one=mock_witness(plan, tamper_key=("right", 0)),
                       manifest_path=inputs["manifest_path"],
                       original_index_path=inputs["original_index_path"])
    assert not (outdir / "selected-matrix-complete.json").exists()


def test_plan_drift_denied_without_any_evidence_directory(tmp_path):
    inputs = pinned(tmp_path)
    plan = plan_matrix(**inputs, keys=parse_keys(KEYS))
    plan["selected_bytes_each_source"] = 1
    evidence = tmp_path / "no-unsafe-start"
    with pytest.raises(ValueError, match="drifted"):
        execute_matrix(plan=plan, evidence_dir=evidence,
                       verify_one=mock_witness(plan),
                       manifest_path=inputs["manifest_path"],
                       original_index_path=inputs["original_index_path"])
    assert not evidence.exists()
