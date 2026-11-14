"""Full original Zelph packed partition geometry tests (synthetic only)."""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from audit_zelph_original_packed_partition import verify_original_packed_partition

ART = "wikidata-20260309-all"


def _fixture():
    cursor = 12
    sections = {}
    for section, numbers in (("left", (0, 1)), ("right", (0,)),
                             ("nameOfNode", (0,)), ("nodeOfName", (0,))):
        chunks = []
        for number in numbers:
            name = (f"chunk-{number:06d}.capnp-packed" if section in ("left", "right")
                    else f"chunk-{number:06d}-wikidata.capnp-packed")
            row = {
                "chunkIndex": number, "offset": cursor, "length": number + 7,
                "objectPath": f"hf://datasets/acrion/zelph/{ART}/shards/{section}/{name}",
            }
            if section in ("left", "right"):
                row["which"] = section
            else:
                row["lang"] = "wikidata"
            chunks.append(row)
            cursor += number + 7
        sections[section] = {"chunks": chunks}
    manifest = {
        "manifestVersion": 2,
        "storageMode": "split-by-direction-and-section",
        "source": {"artifactName": ART, "binSizeBytes": cursor},
        "sections": sections,
    }
    route = {
        "routeVersion": "zelph-filtered-route/v1",
        "source": {
            "headerLengthBytes": 12, "binSizeBytes": cursor,
            "leftChunkCount": 2, "rightChunkCount": 1,
            "nameOfNodeChunkCount": 1, "nodeOfNameChunkCount": 1,
        },
    }
    return manifest, route


def _run(manifest=None, route=None, **kwargs):
    m, r = _fixture()
    return verify_original_packed_partition(manifest=manifest or m, route=route or r, **kwargs)


def test_exact_original_header_and_all_sections_form_one_partition():
    m, r = _fixture()
    result = _run(m, r, actual_source_size=m["source"]["binSizeBytes"])
    assert result["header_bytes"] == 12
    assert result["total_chunk_count"] == 5
    assert result["sections"]["left"]["chunk_count"] == 2
    assert result["sections"]["left"]["start_offset"] == 12
    assert result["sections"]["nodeOfName"]["end_offset_exclusive"] == m["source"]["binSizeBytes"]
    assert result["manifest_offset_cover_gap_free"]
    assert result["manifest_offset_cover_nonoverlapping"]
    assert result["manifest_section_order_matches_original_bin_header"]
    assert result["actual_original_bin_size_compared"]
    for authority in ("all_original_source_bytes_rehashed", "physical_chunk_bytes_verified_here",
                      "upstream_original_bin_authenticated", "complete_original_name_key_domain_verified",
                      "whole_graph_query_family_closed", "source_support_paid", "edit_authority"):
        assert result[authority] is False


@pytest.mark.parametrize("delta", [1, -1])
def test_forged_first_left_chunk_gap_or_overlap_rejected(delta):
    m, r = _fixture()
    m["sections"]["left"]["chunks"][0]["offset"] += delta
    with pytest.raises(ValueError, match="discontinuity/overlap"):
        _run(m, r)


def test_internal_second_left_chunk_gap_refused():
    m, r = _fixture()
    m["sections"]["left"]["chunks"][1]["offset"] += 1
    with pytest.raises(ValueError, match="left/1"):
        _run(m, r)


def test_cross_section_reordered_manifest_rejected():
    m, r = _fixture()
    left = m["sections"]["left"]["chunks"][0]
    right = m["sections"]["right"]["chunks"][0]
    left["offset"], right["offset"] = right["offset"], left["offset"]
    with pytest.raises(ValueError, match="discontinuity/overlap"):
        _run(m, r)


def test_final_trailing_original_bytes_not_covered_by_chunk_manifest():
    m, r = _fixture()
    m["source"]["binSizeBytes"] += 1
    r["source"]["binSizeBytes"] += 1
    with pytest.raises(ValueError, match="unaccounted final bytes"):
        _run(m, r)


def test_source_manifest_bin_size_mismatch_rejected():
    m, r = _fixture()
    r["source"]["binSizeBytes"] += 1
    with pytest.raises(ValueError, match="full-bin sizes"):
        _run(m, r)


def test_local_source_size_mismatch_rejected():
    m, r = _fixture()
    with pytest.raises(ValueError, match="local original binary size"):
        _run(m, r, actual_source_size=4)


def test_header_length_mismatch_detected():
    m, r = _fixture()
    r["source"]["headerLengthBytes"] = 11
    with pytest.raises(ValueError, match="discontinuity/overlap"):
        _run(m, r)


@pytest.mark.parametrize("bad", [None, 0, -1, "12", True])
def test_unverified_original_header_length_rejected(bad):
    m, r = _fixture()
    r["source"]["headerLengthBytes"] = bad
    with pytest.raises(ValueError, match="header length"):
        _run(m, r)


def test_header_section_count_mismatch_rejected():
    m, r = _fixture()
    r["source"]["leftChunkCount"] = 1
    with pytest.raises(ValueError, match="section count differs: left"):
        _run(m, r)


def test_replaced_chunk_identity_rejected_even_if_offset_geometry_looks_plausible():
    m, r = _fixture()
    m["sections"]["left"]["chunks"][0]["objectPath"] = "https://elsewhere.test/chunk"
    with pytest.raises(ValueError, match="not exact immutable artifact path"):
        _run(m, r)


def test_dense_global_indices_required_per_section():
    m, r = _fixture()
    m["sections"]["left"]["chunks"][1]["chunkIndex"] = 7
    with pytest.raises(ValueError, match="not exact immutable artifact path|not dense"):
        _run(m, r)


def test_negative_or_boolean_source_size_rejected():
    m, r = _fixture()
    r["source"]["binSizeBytes"] = True
    with pytest.raises(ValueError, match="full-bin sizes"):
        _run(m, r)
