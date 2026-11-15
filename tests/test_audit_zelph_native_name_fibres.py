"""Native exact EOF and true collision-fibre preservation across two name sections.

All physical receipts are fixture-only. The actual C++ upstream-schema decoder
is separately compiled/checked in tools/check_zelph_native_capnp_roundtrip.sh.
"""
from __future__ import annotations

from hashlib import sha256
import io
import json
from pathlib import Path
import sqlite3
import sys
from types import SimpleNamespace

import pytest

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))
from audit_zelph_native_name_fibres import (
    original_name_plan, run_native_name_audit, _strict,
)
from test_verify_zelph_hf_original_header import _fixture, REV
from verify_zelph_bin_shard_exact import _manifest_index, _ARTIFACT

_SHA = "a" * 64


def setup(tmp_path, *, missing=False, corrupt=False):
    manifest, index = _fixture()
    m, i = tmp_path / "manifest.json", tmp_path / "index.json"
    m.write_text(json.dumps(manifest, sort_keys=True))
    i.write_text(json.dumps(index, sort_keys=True))
    ms, ix = sha256(m.read_bytes()).hexdigest(), sha256(i.read_bytes()).hexdigest()
    source_index = _manifest_index(manifest, _ARTIFACT)
    originals = tmp_path / "physical"
    originals.mkdir()
    root = tmp_path / "shards"
    root.mkdir()
    for (section, n), item in source_index.items():
        if section not in ("nameOfNode", "nodeOfName"):
            continue
        raw = (b"n" if section == "nodeOfName" else b"m") * item["length"]
        path = root / item["relative"]
        path.parent.mkdir(parents=True, exist_ok=True)
        if not missing or section == "nodeOfName":
            path.write_bytes(raw)
        digest = sha256(raw).hexdigest()
        proof = {
            "version": "itir.zelph.direct_original_selected_chunk_equality.v1",
            "dataset_revision": REV,
            "original_manifest_raw_sha256": ms,
            "original_index_raw_sha256": ix,
            "source_bin_size_bytes": manifest["source"]["binSizeBytes"],
            "section": section, "chunk_index": n,
            "original_source_offset": item["offset"],
            "source_range_end_inclusive": item["offset"] + item["length"] - 1,
            "bytes_compared": item["length"],
            "published_object_uri": item["object_uri"],
            "original_binary_uri": f"hf://datasets/acrion/zelph/{_ARTIFACT}.bin",
            "original_source_http_status": 206, "published_shard_http_status": 200,
            "exact_original_packed_bytes_equal_published_shard": True,
            "full_index_manifest_offset_cover_checked": True,
            "original_qid_route_verified": False,
            "whole_name_domain_enumerated": False,
            "all_query_frontiers_closed": False,
            "native_p854_source_support_paid": False,
            "s29_persistence_paid": False, "edit_authority": False,
            "published_shard_raw_sha256": digest,
            "original_packed_range_raw_sha256": digest,
        }
        if corrupt and section == "nameOfNode":
            proof["original_source_offset"] += 1
        (originals / f"{section}-{n:06d}.json").write_text(json.dumps(proof))
    decoder = tmp_path / "native-decoder"
    decoder.write_bytes(b"fixture-native-identity")
    config = dict(manifest=m, original_index=i,
                  manifest_sha256=ms, original_index_sha256=ix,
                  revision=REV, physical_receipts_dirs=[originals], shard_root=root)
    return config, decoder


class FakeNative:
    def __init__(self, wire, rc=0):
        self.stdout = io.BytesIO(wire)
        self.rc = rc
        self.killed = False

    def wait(self, timeout=None):
        return self.rc

    def kill(self):
        self.killed = True


def simulated_native(*, mismatch=False, missing_terminal=False,
                     duplicate_terminal=False, incorrect_row_order=False,
                     exit_code=0):
    # The same two name/nameOfNode sections must preserve pair MULTIPLICITY.
    source = [("Q1", 11), ("Q1", 12), ("Q1", 12), ("Q2", 13)]
    inverse = list(reversed(source))
    if mismatch:
        inverse.pop()
    def start(cmd, **kwargs):
        section = cmd[cmd.index("--section")+1]
        n = int(cmd[cmd.index("--chunk-index")+1])
        rows = source if section == "nodeOfName" else inverse
        frames = [
            {"version": "itir.zelph.native_original_name_row.v1",
             "section": section, "chunk_index": n, "language": "wikidata",
             "row_index": index if not incorrect_row_order else index + 1,
             "name": name, "node_id": node}
            for index, (name, node) in enumerate(rows)
        ]
        end = {
            "version": "itir.zelph.native_original_name_rows_end.v1",
            "section": section, "chunk_index": n, "language": "wikidata",
            "rows_emitted": len(rows), "candidate_only": True, "authority": False,
        }
        if not missing_terminal:
            frames.append(end)
            if duplicate_terminal:
                frames.append(end)
        return FakeNative(
            b"".join(json.dumps(frame).encode()+b"\n" for frame in frames),
            rc=exit_code)
    return start


def test_complete_native_fibre_multisets_preserve_collisions_and_resume(tmp_path):
    cfg, decoder = setup(tmp_path)
    plan = original_name_plan(**cfg)
    assert plan["available_native_chunk_count"] == 2
    db = tmp_path / "native-fibres.sqlite"
    first = run_native_name_audit(
        plan=plan, decoder=decoder, sqlite_index=db,
        max_new_chunks=1, popen=simulated_native())
    assert not first["all_original_name_section_native_chunks_decoded"]
    assert first["both_source_name_sections_pair_multiplicities_equal"] is None
    last = run_native_name_audit(
        plan=plan, decoder=decoder, sqlite_index=db,
        max_new_chunks=1, popen=simulated_native())
    assert last["native_decoded_chunk_counts"] == {"nodeOfName": 1, "nameOfNode": 1}
    assert last["all_original_name_section_native_chunks_decoded"]
    assert last["both_source_name_sections_pair_multiplicities_equal"] is True
    assert last["all_original_name_key_fibres_verified"] is True
    assert last["original_name_keys_with_multiple_nodes_in_checked_rows"] == 1
    assert last["duplicate_original_name_node_pair_groups"] == 1
    assert last["a1_formal_kernel_instantiation_paid"] is False
    assert last["source_support_paid"] is False if "source_support_paid" in last else True
    with sqlite3.connect(db) as conn:
        assert conn.execute("SELECT COUNT(*) FROM native_rows").fetchone()[0] == 8
        assert conn.execute("SELECT COUNT(*) FROM completed_chunks").fetchone()[0] == 2
    repeat = run_native_name_audit(
        plan=plan, decoder=decoder, sqlite_index=db,
        max_new_chunks=5, popen=lambda **_kw: (_ for _ in ()).throw(
            AssertionError("must not re-run complete native chunk")))
    assert repeat["newly_completed_chunks"] == []


def test_missing_shard_is_unmaterialized_not_original_negative(tmp_path):
    cfg, decoder = setup(tmp_path, missing=True)
    plan = original_name_plan(**cfg)
    assert plan["available_native_chunk_count"] == 1
    result = run_native_name_audit(
        plan=plan, decoder=decoder, sqlite_index=tmp_path/"scratch.db",
        popen=simulated_native())
    assert not result["all_original_name_section_native_chunks_decoded"]
    assert not result["all_original_name_key_fibres_verified"]


def test_original_physical_offset_mutation_rejected(tmp_path):
    cfg, _ = setup(tmp_path, corrupt=True)
    with pytest.raises(ValueError, match="source_offset"):
        original_name_plan(**cfg)


def test_inverse_multiset_mismatch_fails_full_fibre_claim(tmp_path):
    cfg, decoder = setup(tmp_path)
    plan = original_name_plan(**cfg)
    result = run_native_name_audit(
        plan=plan, decoder=decoder, sqlite_index=tmp_path/"scratch.db",
        popen=simulated_native(mismatch=True))
    assert result["all_original_name_section_native_chunks_decoded"]
    assert result["both_source_name_sections_pair_multiplicities_equal"] is False
    assert result["all_original_name_key_fibres_verified"] is False


@pytest.mark.parametrize("invalid", [
    {"missing_terminal": True},
    {"duplicate_terminal": True},
    {"incorrect_row_order": True},
    {"exit_code": 2},
])
def test_bad_original_native_stream_has_no_committed_rows(tmp_path, invalid):
    cfg, decoder = setup(tmp_path)
    plan = original_name_plan(**cfg)
    db = tmp_path/"scratch.db"
    with pytest.raises(ValueError):
        run_native_name_audit(
            plan=plan, decoder=decoder, sqlite_index=db,
            popen=simulated_native(**invalid), max_new_chunks=1)
    with sqlite3.connect(db) as conn:
        assert conn.execute("SELECT COUNT(*) FROM completed_chunks").fetchone()[0] == 0
        assert conn.execute("SELECT COUNT(*) FROM native_rows").fetchone()[0] == 0


def test_native_source_revision_mixing_is_forbidden(tmp_path):
    cfg, decoder = setup(tmp_path)
    plan = original_name_plan(**cfg)
    db=tmp_path/"scratch.db"
    run_native_name_audit(plan=plan, decoder=decoder, sqlite_index=db,
                          popen=simulated_native(), max_new_chunks=1)
    mutated = dict(plan)
    mutated["dataset_revision"] = "b"*40
    with pytest.raises(ValueError, match="pins differ"):
        run_native_name_audit(plan=mutated, decoder=decoder,
                              sqlite_index=db, popen=simulated_native())


def test_duplicate_json_native_keys_fail_closed():
    with pytest.raises(ValueError, match="duplicate original-native"):
        _strict(b'{"name":"Q1","name":"Q2"}')
