"""Offline original complete section physical/native A1 join: exact rows, no false proof."""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import audit_zelph_native_name_section as native
from verify_zelph_bin_shard_exact import _ARTIFACT, _manifest_index
from test_verify_zelph_hf_original_header import _fixture, REV

DECODE = "d" * 64
SECTION = "nodeOfName"


def _frames(n, names):
    body = []
    for i, (name, node) in enumerate(names):
        body.append({
            "version": "itir.zelph.native_original_name_row.v1",
            "section": SECTION, "chunk_index": n, "language": "wikidata",
            "row_index": i, "name": name, "node_id": node,
        })
    body.append({
        "version": "itir.zelph.native_original_name_rows_end.v1",
        "section": SECTION, "chunk_index": n, "language": "wikidata",
        "rows_emitted": len(names), "candidate_only": True, "authority": False,
    })
    return b"".join((json.dumps(x, sort_keys=True) + "\n").encode()
                    for x in body)


def setup(tmp_path):
    manifest, original_index = _fixture()
    # NameOfNode is the last original section, so a second name chunk extends
    # the full source image without changing earlier physical offsets.
    old = manifest["source"]["binSizeBytes"]
    previous = original_index["nodeOfName"][0]
    extra = {
        "chunkIndex": 1, "offset": old, "length": 6, "lang": "wikidata",
    }
    original_index["nodeOfName"].append(extra.copy())
    manifest["sections"]["nodeOfName"]["chunks"].append({
        **extra,
        "objectPath": "hf://datasets/acrion/zelph/wikidata-20260309-all/shards/nodeOfName/chunk-000001-wikidata.capnp-packed",
    })
    manifest["source"]["binSizeBytes"] += 6
    m, i = tmp_path / "full.hf-v2.json", tmp_path / "original.index.json"
    m.write_text(json.dumps(manifest, sort_keys=True))
    i.write_text(json.dumps(original_index, sort_keys=True))
    md, idx = sha256(m.read_bytes()).hexdigest(), sha256(i.read_bytes()).hexdigest()
    pr = tmp_path / "physical"
    nr = tmp_path / "native"
    pr.mkdir()
    nr.mkdir()
    rows = _manifest_index(manifest, _ARTIFACT)
    names = [[("Q1", 7), ("Q1", 8)], [("Q1", 9), ("Q2", 11)]]
    for n in [0, 1]:
        item = rows[(SECTION, n)]
        physical = {
            "version": "itir.zelph.direct_original_selected_chunk_equality.v1",
            "dataset_revision": REV,
            "original_manifest_raw_sha256": md,
            "original_index_raw_sha256": idx,
            "source_bin_size_bytes": manifest["source"]["binSizeBytes"],
            "section": SECTION, "chunk_index": n,
            "original_source_offset": item["offset"],
            "source_range_end_inclusive": item["offset"] + item["length"] - 1,
            "bytes_compared": item["length"],
            "published_object_uri": item["object_uri"],
            "original_binary_uri": "hf://datasets/acrion/zelph/wikidata-20260309-all.bin",
            "published_shard_http_status": 200,
            "original_source_http_status": 206,
            "published_shard_raw_sha256": sha256(bytes([n]) * item["length"]).hexdigest(),
            "original_packed_range_raw_sha256": sha256(bytes([n]) * item["length"]).hexdigest(),
            "exact_original_packed_bytes_equal_published_shard": True,
            "full_index_manifest_offset_cover_checked": True,
            "original_qid_route_verified": False,
            "whole_name_domain_enumerated": False,
            "all_query_frontiers_closed": False,
            "native_p854_source_support_paid": False,
            "s29_persistence_paid": False,
            "edit_authority": False,
        }
        physical_path = pr / f"{SECTION}-{n:06d}.json"
        physical_path.write_text(json.dumps(physical))
        row_path = nr / f"{SECTION}-{n:06d}.native.ndjson"
        row_path.write_bytes(_frames(n, names[n]))
        native_receipt = {
            "version": "itir.zelph.native_original_name_chunk_enumeration.v1",
            "dataset_revision": REV, "section": SECTION,
            "chunk_index": n, "language": "wikidata",
            "manifest_raw_sha256": md,
            "original_index_raw_sha256": idx,
            "physical_original_name_chunk_receipt_sha256": sha256(physical_path.read_bytes()).hexdigest(),
            "original_packed_chunk_raw_sha256": physical["published_shard_raw_sha256"],
            "native_decoder_executable_sha256": DECODE,
            "native_packed_chunk_rows_enumerated": len(names[n]),
            "native_name_rows_stdout_sha256": sha256(row_path.read_bytes()).hexdigest(),
            "native_stdout_bytes": row_path.stat().st_size,
            "native_name_rows_file": str(row_path),
            "target_name_fibres": {"Q1": [node for name, node in names[n] if name == "Q1"]},
            "complete_native_row_stream_for_this_chunk": True,
            "name_duplicates_discarded": False,
            "all_original_name_chunks_verified": False,
            "full_name_domain_A1_instantiated": False,
            "global_name_absence_proved": False,
            "edit_authority": False,
        }
        (nr / f"{SECTION}-{n:06d}.native.json").write_text(
            json.dumps(native_receipt),
        )
    return {
        "manifest_path": m, "original_index_path": i,
        "dataset_revision": REV, "manifest_sha256": md,
        "original_index_sha256": idx, "decoder_sha256": DECODE,
        "section": SECTION, "physical_receipts_dir": pr,
        "native_receipts_dir": nr, "target_qids": ("Q1", "Q2", "Q999"),
    }


def test_entire_section_exact_original_packed_and_all_native_rows_join(tmp_path):
    args = setup(tmp_path)
    result = native.audit_original_name_section_domain(**args, require_complete=True)
    assert result["source_original_name_chunk_count"] == 2
    assert result["verified_physical_chunks"] == [0, 1]
    assert result["verified_native_name_row_chunks"] == [0, 1]
    assert result["native_rows_verified"] == 4
    assert result["target_name_fibres_preserving_repeated_values"] == {
        "Q1": [7, 8, 9], "Q2": [11], "Q999": [],
    }
    assert result["target_name_scope_is_full_original_name_section"] is True
    assert result["original_packed_byte_and_native_row_section_cover"] is True
    assert result["global_name_fibre_A1_proved"] is False
    assert result["decoder_adequacy_formal_theorem_instantiated"] is False


def test_missing_native_second_chunk_is_not_full_domain(tmp_path):
    args = setup(tmp_path)
    (args["native_receipts_dir"] / "nodeOfName-000001.native.json").unlink()
    (args["native_receipts_dir"] / "nodeOfName-000001.native.ndjson").unlink()
    result = native.audit_original_name_section_domain(**args)
    assert result["verified_native_name_row_chunks"] == [0]
    assert result["missing_native_row_chunk_indices"] == [1]
    assert result["target_name_scope_is_full_original_name_section"] is False
    with pytest.raises(ValueError, match="incomplete"):
        native.audit_original_name_section_domain(**args, require_complete=True)


def test_missing_physical_source_receipt_cannot_leave_native_orphan(tmp_path):
    args = setup(tmp_path)
    (args["physical_receipts_dir"] / "nodeOfName-000001.json").unlink()
    with pytest.raises(ValueError, match="orphan"):
        native.audit_original_name_section_domain(**args)


@pytest.mark.parametrize("field,bad", [
    ("native_decoder_executable_sha256", "0"*64),
    ("physical_original_name_chunk_receipt_sha256", "0"*64),
    ("complete_native_row_stream_for_this_chunk", False),
    ("name_duplicates_discarded", True),
    ("native_name_rows_file", "/tmp/wrong.ndjson"),
    ("native_packed_chunk_rows_enumerated", -1),
])
def test_changed_native_receipt_cannot_be_promoted(tmp_path, field, bad):
    args = setup(tmp_path)
    p = args["native_receipts_dir"] / "nodeOfName-000000.native.json"
    value = json.loads(p.read_text())
    value[field] = bad
    p.write_text(json.dumps(value))
    with pytest.raises(ValueError, match="mismatch|changed"):
        native.audit_original_name_section_domain(**args)


@pytest.mark.parametrize("attack", ["wrong_index", "missing_footer", "after_footer", "wrong_count", "duplicate_json"])
def test_untrusted_native_name_stream_cannot_claim_original_domain(tmp_path, attack):
    args = setup(tmp_path)
    rows_file = args["native_receipts_dir"] / "nodeOfName-000000.native.ndjson"
    frames = _frames(0, [("Q1", 7), ("Q1", 8)]).decode().splitlines()
    if attack == "wrong_index":
        row = json.loads(frames[1])
        row["row_index"] = 0
        frames[1] = json.dumps(row)
    elif attack == "missing_footer":
        frames.pop()
    elif attack == "after_footer":
        frames.append('{"version":"attack"}')
    elif attack == "wrong_count":
        row = json.loads(frames[-1])
        row["rows_emitted"] = 9999
        frames[-1] = json.dumps(row)
    elif attack == "duplicate_json":
        frames[0] = frames[0][:-1] + ', "name": "Q2"}'
    rows_file.write_text("\n".join(frames) + "\n")
    native_path = args["native_receipts_dir"] / "nodeOfName-000000.native.json"
    receipt = json.loads(native_path.read_text())
    receipt["native_stdout_bytes"] = rows_file.stat().st_size
    receipt["native_name_rows_stdout_sha256"] = sha256(rows_file.read_bytes()).hexdigest()
    native_path.write_text(json.dumps(receipt))
    with pytest.raises(ValueError, match="schema|terminal|duplicate|footer|count"):
        native.audit_original_name_section_domain(**args)


def test_no_absolute_wikidata_absence_claim_even_complete_name_section(tmp_path):
    args = setup(tmp_path)
    result = native.audit_original_name_section_domain(**args, require_complete=True)
    assert result["target_name_fibres_preserving_repeated_values"]["Q999"] == []
    assert result["all_wikibase_entities_or_statements_verified"] is False
    assert result["original_qid_adjacency_routes_proved"] is False
    assert result["global_name_fibre_A1_proved"] is False
