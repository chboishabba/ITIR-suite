"""Route-free physical source chunk verification, no real HF requests."""
from __future__ import annotations

from hashlib import sha256
import io
import json
from pathlib import Path
import sys

import pytest

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from verify_zelph_hf_direct_original_chunk import verify_direct_original_chunk
from test_verify_zelph_hf_original_header import _fixture, HEADER, REV


class Response(io.BytesIO):
    def __init__(self, raw: bytes, status: int, headers: dict):
        super().__init__(raw)
        self.status = status
        self.headers = headers

    def geturl(self):
        return "https://huggingface.co/pinned-original-source"


def _inputs(tmp_path):
    manifest, index = _fixture()
    m = tmp_path / "published-manifest.json"
    i = tmp_path / "published-original.index.json"
    m.write_text(json.dumps(manifest, sort_keys=True))
    i.write_text(json.dumps(index, sort_keys=True))
    return m, i, sha256(m.read_bytes()).hexdigest(), sha256(i.read_bytes()).hexdigest()


def _call(tmp_path, *, section="nodeOfName", chunk_index=0, body=b"abcde",
          wrong_source=False, bad_status=False, **kwargs):
    m, i, md, idx = _inputs(tmp_path)
    ranges = []

    def opener(req, timeout):
        ranged = req.get_header("Range")
        ranges.append((req.full_url, ranged))
        assert req.get_header("Accept-encoding") == "identity"
        assert "/resolve/" + REV + "/" in req.full_url
        if req.full_url.endswith(".bin"):
            expected = next(x for x in _fixture()[1][section]
                            if x["chunkIndex"] == chunk_index)
            assert ranged == (
                f"bytes={expected['offset']}-"
                f"{expected['offset'] + len(body) - 1}"
            )
            return Response(
                b"abXde" if wrong_source else body,
                200 if bad_status else 206, {
                    "Content-Range": (
                        f"bytes {expected['offset']}-"
                        f"{expected['offset'] + len(body) - 1}/"
                        f"{_fixture()[0]['source']['binSizeBytes']}"
                    ),
                    "Content-Length": str(len(body)),
                },
            )
        assert ranged == f"bytes=0-{len(body)-1}"
        return Response(body, 200, {"Content-Length": str(len(body))})

    result = verify_direct_original_chunk(
        manifest_path=m, original_index_path=i,
        dataset_revision=REV, manifest_sha256=md,
        original_index_sha256=idx,
        section=section, chunk_index=chunk_index,
        max_chunk_mib=1, opener=opener, **kwargs,
    )
    return result, ranges


@pytest.mark.parametrize("section", ["left", "right", "nameOfNode", "nodeOfName"])
def test_direct_selected_original_chunk_equality_for_each_real_section(tmp_path, section):
    proof, requests = _call(tmp_path, section=section)
    assert proof["section"] == section
    assert proof["bytes_compared"] == 5
    assert proof["exact_original_packed_bytes_equal_published_shard"] is True
    assert proof["published_shard_raw_sha256"] == sha256(b"abcde").hexdigest()
    assert proof["original_packed_range_raw_sha256"] == sha256(b"abcde").hexdigest()
    assert proof["published_shard_http_status"] == 200
    assert proof["original_source_http_status"] == 206
    assert proof["original_qid_route_verified"] is False
    assert proof["whole_name_domain_enumerated"] is False
    assert proof["all_query_frontiers_closed"] is False
    assert proof["edit_authority"] is False
    assert len(requests) == 2


def test_direct_chunk_mismatch_fails_before_receipt(tmp_path):
    with pytest.raises(ValueError, match="packed bytes differ"):
        _call(tmp_path, wrong_source=True)


def test_direct_chunk_does_not_accept_original_source_http200(tmp_path):
    with pytest.raises(ValueError, match="exact HTTP 206"):
        _call(tmp_path, bad_status=True)


def test_missing_source_chunk_preflight_without_network(tmp_path):
    m, i, md, idx = _inputs(tmp_path)
    def forbid(*_args, **_kwargs):
        raise AssertionError("must not contact network")
    with pytest.raises(ValueError, match="absent"):
        verify_direct_original_chunk(
            manifest_path=m, original_index_path=i,
            dataset_revision=REV, manifest_sha256=md,
            section="left", chunk_index=999,
            opener=forbid,
        )


def test_corrupt_original_manifest_digest_preflight_without_network(tmp_path):
    m, i, md, idx = _inputs(tmp_path)
    def forbid(*_args, **_kwargs):
        raise AssertionError("must not contact network")
    with pytest.raises(ValueError, match="manifest digest mismatch"):
        verify_direct_original_chunk(
            manifest_path=m, original_index_path=i,
            dataset_revision=REV, manifest_sha256="f"*64,
            section="nameOfNode", chunk_index=0,
            opener=forbid,
        )


@pytest.mark.parametrize("bad_section,index", [
    ("annotations", 0), ("left", -1), ("nodeOfName", True),
])
def test_invalid_section_and_chunk_indices_cannot_trigger_network(
    tmp_path, bad_section, index
):
    m, i, md, idx = _inputs(tmp_path)
    def forbid(*_args, **_kwargs):
        raise AssertionError("must not contact network")
    with pytest.raises(ValueError, match="explicit original section"):
        verify_direct_original_chunk(
            manifest_path=m, original_index_path=i,
            dataset_revision=REV, manifest_sha256=md,
            section=bad_section, chunk_index=index, opener=forbid,
        )


def test_real_zero_byte_source_offset_not_assumed_to_mean_first_chunk(tmp_path):
    proof, _ = _call(tmp_path, section="left")
    assert proof["original_source_offset"] == len(HEADER)
    assert proof["source_range_end_inclusive"] == len(HEADER) + 4
