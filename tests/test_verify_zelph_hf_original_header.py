"""P0 exact original offset-index/manifest crosswalk and remote native header tests.

No live network or 82 GiB source bytes; tests mock only the pinned HTTP
response and native decoder subprocess interface, which is separately checked
with the real generated Cap'n Proto in check_zelph_native_capnp_roundtrip.sh.
"""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import io
import json
from pathlib import Path
import sys

import pytest

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))
from verify_zelph_index_manifest_original import (
    crosscheck_original_index, verify_index_manifest_files,
)
from verify_zelph_hf_original_header import verify_pinned_original_header

ART = "wikidata-20260309-all"
REV = "a" * 40
HEADER = b"synthetic-upstream-header"


def _fixture():
    cursor = len(HEADER)
    sections = {}
    index = {"file": "/old-producer-path/original.bin",
             "header": {"offset": 0, "length": len(HEADER)}}
    for section, numbers in (
        ("left", (0, 1)), ("right", (0,)),
        ("nameOfNode", (0,)), ("nodeOfName", (0,)),
    ):
        chunks = []
        originals = []
        for number in numbers:
            name = (f"chunk-{number:06d}.capnp-packed" if section in ("left", "right")
                    else f"chunk-{number:06d}-wikidata.capnp-packed")
            record = {"chunkIndex": number, "offset": cursor, "length": 5 + number}
            if section in ("left", "right"):
                record["which"] = section
            else:
                record["lang"] = "wikidata"
            originals.append(dict(record))
            chunks.append({
                **record,
                "objectPath": f"hf://datasets/acrion/zelph/{ART}/shards/{section}/{name}",
            })
            cursor += record["length"]
        sections[section] = {"chunks": chunks}
        index[section] = originals
    manifest = {
        "manifestVersion": 2, "storageMode": "split-by-direction-and-section",
        "source": {
            "artifactName": ART,
            "headerLengthBytes": len(HEADER),
            "binSizeBytes": cursor,
        },
        "sections": sections,
    }
    return manifest, index


def _paths(tmp_path):
    manifest, index = _fixture()
    mpath = tmp_path / "pinned.hf-v2.json"
    ipath = tmp_path / "artifact.index.json"
    mpath.write_text(json.dumps(manifest, sort_keys=True))
    ipath.write_text(json.dumps(index, sort_keys=True))
    return mpath, ipath, sha256(mpath.read_bytes()).hexdigest(), sha256(ipath.read_bytes()).hexdigest()


def _check(manifest=None, index=None):
    m, i = _fixture()
    return crosscheck_original_index(
        manifest=manifest if manifest is not None else m,
        original_index=index if index is not None else i,
    )


def test_original_index_and_manifest_entire_5_chunk_partition():
    result = _check()
    assert result["section_chunk_counts"] == {
        "leftChunkCount": 2, "rightChunkCount": 1,
        "nameOfNodeChunkCount": 1, "nodeOfNameChunkCount": 1,
    }
    assert result["all_manifest_chunk_offsets_equal_original_index"]
    assert result["entire_index_partition_gap_free"]
    assert result["entire_index_partition_nonoverlapping"]
    assert result["original_bin_header_raw_bytes_fetched"] is False
    assert result["original_source_upstream_authenticity_proved"] is False
    assert result["all_chunk_payload_bytes_checked"] is False
    assert result["entire_name_domain_byte_checked"] is False


@pytest.mark.parametrize("section,attribute", [
    ("left", "offset"), ("left", "length"), ("right", "offset"),
    ("nameOfNode", "offset"), ("nodeOfName", "length"),
])
def test_forged_source_index_chunk_drift_rejected(section, attribute):
    m, i = _fixture()
    i[section][0][attribute] += 1
    with pytest.raises(ValueError, match="byte offset identity mismatch"):
        _check(m, i)


@pytest.mark.parametrize("section", ["left", "right", "nameOfNode", "nodeOfName"])
def test_omitted_original_index_section_rejected(section):
    m, i = _fixture()
    i.pop(section)
    with pytest.raises(ValueError, match="section fields"):
        _check(m, i)


def test_native_source_header_size_drift_refused():
    m, i = _fixture()
    m["source"]["headerLengthBytes"] += 1
    with pytest.raises(ValueError, match="header lengths"):
        _check(m, i)


def test_name_language_disagrees_across_original_index():
    m, i = _fixture()
    i["nodeOfName"][0]["lang"] = "en"
    with pytest.raises(ValueError, match="name language"):
        _check(m, i)


def test_forged_global_chunk_index_rejected():
    m, i = _fixture()
    i["left"][1]["chunkIndex"] = 0
    with pytest.raises(ValueError, match="byte offset identity mismatch"):
        _check(m, i)


def test_manifest_and_index_source_sha_independently_checked(tmp_path):
    mp, ip, ms, i_sha = _paths(tmp_path)
    result = verify_index_manifest_files(
        manifest_path=mp, index_path=ip,
        manifest_sha256=ms, index_sha256=i_sha,
    )
    assert result["original_index_raw_sha256_rechecked"] == i_sha
    assert result["original_index_expected_digest_independently_supplied"]


def test_tampered_original_index_sha_refused(tmp_path):
    mp, ip, ms, i_sha = _paths(tmp_path)
    with pytest.raises(ValueError, match="raw offset index digest mismatch"):
        verify_index_manifest_files(
            manifest_path=mp, index_path=ip,
            manifest_sha256=ms, index_sha256="f" * 64,
        )


class Response(io.BytesIO):
    def __init__(self, payload, status, range_header, encoding="identity", length=None):
        super().__init__(payload)
        self.status = status
        self.headers = {
            "Content-Range": range_header, "Content-Encoding": encoding,
            "Content-Length": str(len(payload) if length is None else length),
        }


def _source_opener(original_size, *, http_status=206, bad_range=False,
                   bad_bytes=False, encoding="identity", extra=False,
                   content_length=None):
    def open_request(request, timeout):
        assert request.get_header("Range") == f"bytes=0-{len(HEADER)-1}"
        assert request.get_header("Accept-encoding") == "identity"
        assert request.full_url.endswith(f"/{ART}.bin")
        assert "/resolve/" + REV + "/" in request.full_url
        assert timeout == 60
        payload = HEADER + (b"!" if extra else b"")
        if bad_bytes:
            payload = HEADER[:-1]
        range_text = f"bytes 0-{len(HEADER)-1}/{original_size}"
        if bad_range:
            range_text = f"bytes 1-{len(HEADER)-1}/{original_size}"
        return Response(payload, http_status, range_text, encoding, content_length)
    return open_request


def _decoder(*, header):
    assert header == HEADER
    return {
        "version": "itir.zelph.native_original_packed_header_probe.v1",
        "header_size_bytes": len(header),
        "leftChunkCount": 2, "rightChunkCount": 1,
        "nameOfNodeChunkCount": 1, "nodeOfNameChunkCount": 1,
        "source_upstream_authenticity_proved": False,
        "edit_authority": False,
    }


def _remote(tmp_path, **k):
    mp, ip, ms, idxsha = _paths(tmp_path)
    manifest, _ = _fixture()
    kwargs = dict(
        manifest_path=mp, index_path=ip,
        manifest_sha256=ms, original_index_sha256=idxsha,
        dataset_revision=REV,
        header_decoder_executable=tmp_path / "real-schema-probe",
        opener=_source_opener(manifest["source"]["binSizeBytes"]),
        decode_header=_decoder,
    )
    kwargs.update(k)
    return verify_pinned_original_header(**kwargs)


def test_tiny_original_remote_header_206_matches_all_four_sections(tmp_path):
    result = _remote(tmp_path)
    assert result["original_source_http_status"] == 206
    assert result["header_bytes_received"] == len(HEADER)
    assert result["header_raw_sha256"] == sha256(HEADER).hexdigest()
    assert result["full_original_index_manifest_geometry_checked"]
    assert result["native_original_header_matches_all_four_section_counts"]
    for field in ("full_original_bin_sha256_verified", "all_name_shards_verified",
                  "original_bin_selected_shard_bytes_equal", "name_domain_exhausted",
                  "all_query_words_closed", "native_p854_source_verified",
                  "source_support_paid", "edit_authority"):
        assert result[field] is False


@pytest.mark.parametrize("flag", ["bad_range", "bad_bytes", "extra"])
def test_remote_header_corrupted_range_rejected(tmp_path, flag):
    m, _ = _fixture()
    with pytest.raises(ValueError, match="Content-Range|Content-Length|truncated|oversized"):
        _remote(tmp_path, opener=_source_opener(m["source"]["binSizeBytes"], **{flag: True}))


def test_remote_header_http200_fallback_rejected(tmp_path):
    m, _ = _fixture()
    with pytest.raises(ValueError, match="HTTP 206"):
        _remote(tmp_path, opener=_source_opener(m["source"]["binSizeBytes"], http_status=200))


def test_remote_header_nonidentity_compression_rejected(tmp_path):
    m, _ = _fixture()
    with pytest.raises(ValueError, match="non-identity"):
        _remote(tmp_path, opener=_source_opener(m["source"]["binSizeBytes"], encoding="gzip"))


def test_native_header_incorrect_section_count_rejected(tmp_path):
    def wrong_decode(*, header):
        x = _decoder(header=header)
        x["rightChunkCount"] = 999
        return x
    with pytest.raises(ValueError, match="native original header disagrees"):
        _remote(tmp_path, decode_header=wrong_decode)


def test_unpinned_revision_cannot_trigger_network(tmp_path):
    def forbid_network(*args, **kwargs):
        raise AssertionError("must not fetch wrong revision")
    with pytest.raises(ValueError, match="immutable Hugging Face"):
        _remote(tmp_path, dataset_revision="main", opener=forbid_network)


def test_raw_manifest_preflight_fails_before_network(tmp_path):
    mp, ip, ms, idxsha = _paths(tmp_path)
    mp.write_text('{"forged":true}')
    def forbid_network(*args, **kwargs):
        raise AssertionError("must not fetch under wrong digest")
    with pytest.raises(ValueError, match="raw pinned manifest digest mismatch"):
        verify_pinned_original_header(
            manifest_path=mp, index_path=ip, manifest_sha256=ms,
            original_index_sha256=idxsha, dataset_revision=REV,
            header_decoder_executable=tmp_path / "probe",
            opener=forbid_network, decode_header=_decoder,
        )


def test_exact_remote_original_header_byte_evidence_retained_without_overwrite(tmp_path):
    output = tmp_path / "raw-original-header.capnp-packed"
    result = _remote(tmp_path, raw_header_output=output)
    assert output.read_bytes() == HEADER
    assert sha256(output.read_bytes()).hexdigest() == result["header_raw_sha256"]
    assert result["raw_header_byte_copy_written"] is True
    # No subsequent request or run may silently replace physical bytes.
    with pytest.raises(ValueError, match="refuse overwrite"):
        _remote(tmp_path, raw_header_output=output)


def test_bad_final_redirect_not_accepted_as_original_tls_source(tmp_path):
    manifest, _ = _fixture()
    size = manifest["source"]["binSizeBytes"]
    class Insecure(Response):
        def geturl(self):
            return "http://untrusted.invalid/downgrade"
    def opener(request, timeout):
        return Insecure(HEADER, 206, f"bytes 0-{len(HEADER)-1}/{size}")
    with pytest.raises(ValueError, match="outside TLS"):
        _remote(tmp_path, opener=opener)
