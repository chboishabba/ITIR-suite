"""Strict exact-byte HF connector adversarial tests (never use public network)."""
from __future__ import annotations

from hashlib import sha256
import io

import pytest

from itir_mcp.shard_transport import (
    fetch_pinned_zelph_object, open_pinned_zelph_range,
    open_pinned_zelph_complete_object,
)

REV = "a" * 40
BASE = "hf://datasets/acrion/zelph/"
HEAD = BASE + "wikidata-20260309-all.bin"
METADATA = BASE + "wikidata-20260309-all/artifact.index.json"


class Response(io.BytesIO):
    def __init__(self, raw, *, status, headers, url="https://huggingface.co/any"):
        super().__init__(raw)
        self.status = status
        self.headers = headers
        self._url = url

    def geturl(self):
        return self._url


def _response_open(raw, *, status, headers, url="https://huggingface.co/any"):
    def opener(request, timeout):
        assert "/resolve/" + REV + "/" in request.full_url
        assert request.get_header("Accept-encoding") == "identity"
        assert 0 < timeout <= 600
        return Response(raw, status=status, headers=headers, url=url)
    return opener


def test_exact_native_source_range_http206():
    raw = b"packed source header"
    def open_range(request, timeout):
        assert request.get_header("Range") == f"bytes=0-{len(raw)-1}"
        return _response_open(raw, status=206, headers={
            "Content-Range": f"bytes 0-{len(raw)-1}/1000",
            "Content-Length": str(len(raw)), "Content-Encoding": "identity",
        })(request, timeout)
    with open_pinned_zelph_range(
        hf_uri=HEAD, revision=REV, start=0, length=len(raw),
        total_size=1000, opener=open_range,
    ) as response:
        assert response.read(len(raw)) == raw
        assert response.read(1) == b""


@pytest.mark.parametrize("bad", [
    BASE + "../escape", BASE + "file/../other", BASE + "file/%2e%2e",
    "hf://datasets/another/zelph/source.bin",
    "hf://models/acrion/zelph/source.bin",
])
def test_refuse_untrusted_identity_and_unsafe_path(bad):
    with pytest.raises(ValueError, match="original dataset|unsafe|unsupported"):
        with open_pinned_zelph_range(
            hf_uri=bad, revision=REV, start=0, length=3,
            total_size=20, opener=lambda *_a, **_k: None,
        ):
            raise AssertionError("network should not run")


@pytest.mark.parametrize("status", [200, 301, 416])
def test_never_promote_non206_or_http200_to_exact_physical_byte_evidence(status):
    opener = _response_open(b"abc", status=status, headers={
        "Content-Range": "bytes 0-2/10", "Content-Length": "3",
    })
    with pytest.raises(ValueError, match="exact HTTP 206"):
        with open_pinned_zelph_range(
            hf_uri=HEAD, revision=REV, start=0, length=3,
            total_size=10, opener=opener,
        ):
            pass


def test_wrong_remote_total_or_offset_is_refused():
    opener = _response_open(b"abc", status=206, headers={
        "Content-Range": "bytes 1-3/10", "Content-Length": "3",
    })
    with pytest.raises(ValueError, match="Content-Range mismatch"):
        with open_pinned_zelph_range(
            hf_uri=HEAD, revision=REV, start=0, length=3,
            total_size=10, opener=opener,
        ):
            pass


def test_tls_redirect_downgrade_refused():
    opener = _response_open(b"abc", status=206, headers={
        "Content-Range": "bytes 0-2/10",
    }, url="http://untrusted.invalid/range")
    with pytest.raises(ValueError, match="outside TLS"):
        with open_pinned_zelph_range(
            hf_uri=HEAD, revision=REV, start=0, length=3,
            total_size=10, opener=opener,
        ):
            pass


@pytest.mark.parametrize("bad", [-1, 0, True, 2**65])
def test_invalid_range_or_budget_never_reaches_network(bad):
    def refuse(*_args, **_kwargs):
        raise AssertionError("network should never run")
    with pytest.raises(ValueError, match="invalid exact"):
        with open_pinned_zelph_range(
            hf_uri=HEAD, revision=REV, start=bad, length=3,
            total_size=5, opener=refuse,
        ):
            pass


def test_full_bounded_metadata_http200_success():
    raw = b'{"manifestVersion":2}'
    proof = fetch_pinned_zelph_object(
        hf_uri=METADATA, revision=REV,
        opener=_response_open(raw, status=200, headers={
            "Content-Length": str(len(raw)), "Content-Encoding": "identity",
        }),
    )
    assert proof["bytes"] == raw
    assert proof["sha256"] == sha256(raw).hexdigest()
    assert proof["whole_object_observed"] is True
    assert proof["source_support_paid"] is False
    assert proof["edit_authority"] is False


def test_complete_http206_metadata_is_accepted_but_not_partial():
    raw = b"metadata"
    success = _response_open(raw, status=206, headers={
        "Content-Range": f"bytes 0-{len(raw)-1}/{len(raw)}",
        "Content-Length": str(len(raw)),
    })
    assert fetch_pinned_zelph_object(
        hf_uri=METADATA, revision=REV, opener=success,
    )["bytes"] == raw
    partial = _response_open(raw, status=206, headers={
        "Content-Range": f"bytes 0-{len(raw)-1}/{len(raw)+1}",
        "Content-Length": str(len(raw)),
    })
    with pytest.raises(ValueError, match="partial object"):
        fetch_pinned_zelph_object(
            hf_uri=METADATA, revision=REV, opener=partial,
        )


def test_metadata_prevents_hidden_truncation():
    opener = _response_open(b"123456789", status=200, headers={
        "Content-Length": "9",
    })
    with pytest.raises(ValueError, match="exceeds bound"):
        fetch_pinned_zelph_object(
            hf_uri=METADATA, revision=REV, max_bytes=8, opener=opener,
        )


def test_metadata_rejects_undetected_missing_bytes():
    opener = _response_open(b"foo", status=200, headers={
        "Content-Length": "4",
    })
    with pytest.raises(ValueError, match="Content-Length"):
        fetch_pinned_zelph_object(
            hf_uri=METADATA, revision=REV, opener=opener,
        )


def test_revision_must_be_immutable_before_any_request():
    def refuse(*_args, **_kwargs):
        raise AssertionError("network must not run")
    with pytest.raises(ValueError, match="immutable"):
        fetch_pinned_zelph_object(
            hf_uri=METADATA, revision="main", opener=refuse,
        )


def test_full_shard_http200_is_valid_but_original_range_http200_is_not():
    raw = b"full-shard"
    opener = _response_open(raw, status=200, headers={
        "Content-Length": str(len(raw)), "Content-Encoding": "identity",
    })
    with open_pinned_zelph_complete_object(
        hf_uri=METADATA, revision=REV, expected_size=len(raw),
        opener=opener,
    ) as response:
        assert response.read(len(raw)) == raw
        assert response.read(1) == b""
    with pytest.raises(ValueError, match="exact HTTP 206"):
        with open_pinned_zelph_range(
            hf_uri=HEAD, revision=REV, start=0, length=len(raw),
            total_size=100, opener=opener,
        ):
            pass


def test_complete_shard_http206_requires_total_equal_its_whole_object_length():
    raw = b"complete"
    good = _response_open(raw, status=206, headers={
        "Content-Length": str(len(raw)),
        "Content-Range": f"bytes 0-{len(raw)-1}/{len(raw)}",
    })
    with open_pinned_zelph_complete_object(
        hf_uri=METADATA, revision=REV, expected_size=len(raw),
        opener=good,
    ) as response:
        assert response.read(len(raw)) == raw
    partial = _response_open(raw, status=206, headers={
        "Content-Length": str(len(raw)),
        "Content-Range": f"bytes 0-{len(raw)-1}/{len(raw)+10}",
    })
    with pytest.raises(ValueError, match="partial shard"):
        with open_pinned_zelph_complete_object(
            hf_uri=METADATA, revision=REV, expected_size=len(raw),
            opener=partial,
        ):
            pass


def test_complete_shard_requires_exact_advertised_length_before_read():
    opener = _response_open(b"abc", status=200, headers={
        "Content-Length": "99",
    })
    with pytest.raises(ValueError, match="Content-Length"):
        with open_pinned_zelph_complete_object(
            hf_uri=METADATA, revision=REV, expected_size=3,
            opener=opener,
        ):
            pass


def test_selected_shard_compression_is_not_a_raw_byte_witness():
    opener = _response_open(b"abc", status=200, headers={
        "Content-Length": "3", "Content-Encoding": "gzip",
    })
    with pytest.raises(ValueError, match="identity encoding"):
        with open_pinned_zelph_complete_object(
            hf_uri=METADATA, revision=REV, expected_size=3,
            opener=opener,
        ):
            pass
