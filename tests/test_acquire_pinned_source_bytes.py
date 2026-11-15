"""Offline adversarial checks for exact-byte acquisition; never hits the network."""
from __future__ import annotations
import io
from hashlib import sha256
from pathlib import Path
import sys
from unittest.mock import patch
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from acquire_pinned_source_bytes import acquisition_plan, acquire, require_public_https


def plan(tmp_path, **changes):
    args = dict(url="https://huggingface.co/datasets/acrion/zelph/resolve/" + "a" * 40 + "/graph.bin",
                kind="zelph-original-bin", destination=tmp_path / "source.bin",
                max_bytes=128, dataset_revision="a" * 40)
    args.update(changes)
    return acquisition_plan(**args)


@pytest.mark.parametrize("bad", [
    "http://example.com/a", "https://localhost/a",
    "https://127.0.0.1/a", "https://[::1]/a",
    "https://user:secret@example.org/a", "file:///tmp/a",
    "https://host.local/x", "https://192.168.0.1/x",
    "https://example.org:8443/x", "https://example.org/x#fragment",
])
def test_unsafe_url_rejected(bad):
    with pytest.raises(ValueError):
        require_public_https(bad)


def test_hf_immutable_revision_required(tmp_path):
    with pytest.raises(ValueError):
        plan(tmp_path, url="https://huggingface.co/datasets/acrion/zelph/resolve/main/graph.bin")
    with pytest.raises(ValueError):
        plan(tmp_path, dataset_revision=None)


def test_length_budget_and_sha_pin_validation(tmp_path):
    with pytest.raises(ValueError):
        plan(tmp_path, expected_length=129)
    with pytest.raises(ValueError):
        plan(tmp_path, expected_sha256="a" * 63)
    with pytest.raises(ValueError):
        plan(tmp_path, max_bytes=True)


def test_refuse_overwrite_and_symlink(tmp_path):
    dst = tmp_path / "source.bin"
    dst.write_bytes(b"present")
    with pytest.raises(ValueError):
        plan(tmp_path)
    dst.unlink()
    dst.symlink_to(tmp_path / "somewhere")
    with pytest.raises(ValueError):
        plan(tmp_path)


class FakeResponse:
    def __init__(self, data, url, status=200):
        self.buffer = io.BytesIO(data)
        self.url = url
        self.status = status
        self.headers = {"Content-Length": str(len(data))}

    def geturl(self):
        return self.url

    def read(self, count):
        return self.buffer.read(count)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return None


def test_actual_stream_digest_match_and_atomic_commit(tmp_path):
    raw = b"original-byte-evidence-123"
    url = "https://huggingface.co/datasets/acrion/zelph/resolve/" + "a" * 40 + "/graph.bin"
    p = plan(tmp_path, expected_length=len(raw), expected_sha256=sha256(raw).hexdigest())
    with patch("acquire_pinned_source_bytes.require_public_https", return_value="huggingface.co"), \
         patch("acquire_pinned_source_bytes.urlopen",
               return_value=FakeResponse(raw, url)):
        receipt = acquire(plan=p, destination=tmp_path / "source.bin")
    assert receipt["digest_matches_supplied_pin"] is True
    assert receipt["upstream_source_origin_independently_authenticated"] is False
    assert receipt["primary_document_semantics_verified"] is False
    assert (tmp_path / "source.bin").read_bytes() == raw


def test_bad_digest_fails_closed_and_leaves_no_target(tmp_path):
    url = "https://huggingface.co/datasets/acrion/zelph/resolve/" + "a" * 40 + "/graph.bin"
    p = plan(tmp_path, expected_sha256="0" * 64)
    with patch("acquire_pinned_source_bytes.require_public_https", return_value="huggingface.co"), \
         patch("acquire_pinned_source_bytes.urlopen",
               return_value=FakeResponse(b"wrong", url)):
        with pytest.raises(ValueError, match="SHA256"):
            acquire(plan=p, destination=tmp_path / "source.bin")
    assert not (tmp_path / "source.bin").exists()
    assert not list(tmp_path.glob(".itir-source-*"))
