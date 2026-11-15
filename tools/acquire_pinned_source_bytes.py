#!/usr/bin/env python3
"""Acquire EXACT bytes for a caller-identified source, without silently paying authority.

The source identity, URL, revision and expected SHA must come from an independent
operator/primary-source investigation. A locally matching user-supplied digest
is not a proof of upstream authorship. Default is an offline plan; --execute
performs one bounded HTTPS download to a *new* destination only.

This is a transport adapter, not a substitute for run_zelph_local_physical_maxcut.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import ipaddress
import json
import os
from pathlib import Path
import re
import socket
import sys
import tempfile
from urllib.parse import urlsplit
from urllib.request import Request, build_opener, HTTPRedirectHandler

_HEX64 = re.compile(r"[0-9a-f]{64}\Z")
_HEX40 = re.compile(r"[0-9a-f]{40}\Z")
_ALLOWED = {"zelph-original-bin", "zelph-manifest", "zelph-shard",
            "wikibase-full-entity", "p854-document"}
_CHUNK = 1024 * 1024


def require_public_https(url: str, *, resolve: bool = False) -> str:
    """Disallow local/credential-bearing URLs; recheck final redirect target."""
    if not isinstance(url, str) or len(url) > 8192:
        raise ValueError("bounded source URL required")
    parsed = urlsplit(url)
    if (parsed.scheme != "https" or not parsed.hostname
            or parsed.username is not None or parsed.password is not None
            or parsed.port not in (None, 443) or parsed.fragment):
        raise ValueError("only credential-free public HTTPS URLs are allowed")
    hostname = parsed.hostname.rstrip(".").lower()
    if (hostname in {"localhost", "localhost.localdomain"}
            or hostname.endswith((".localhost", ".local", ".internal"))
            or "." not in hostname):
        raise ValueError("local/internal source hosts refused")
    try:
        addr = ipaddress.ip_address(hostname)
    except ValueError:
        addr = None
    if addr is not None and not addr.is_global:
        raise ValueError("non-public source IP refused")
    if resolve:
        # DNS preflight is a safety gate, not resistance to DNS rebinding;
        # run only with trusted source URLs in a controlled environment.
        for item in socket.getaddrinfo(hostname, 443, type=socket.SOCK_STREAM):
            if not ipaddress.ip_address(item[4][0]).is_global:
                raise ValueError("source hostname resolves to private or reserved IP")
    return hostname


def acquisition_plan(*, url: str, kind: str, destination: Path,
                     max_bytes: int, expected_sha256: str | None = None,
                     expected_length: int | None = None,
                     dataset_revision: str | None = None) -> dict:
    require_public_https(url)
    if kind not in _ALLOWED:
        raise ValueError("unknown source-kind")
    if type(max_bytes) is not int or not 0 < max_bytes <= 128 * 1024**3:
        raise ValueError("positive explicit <=128 GiB byte budget required")
    if expected_sha256 is not None and not _HEX64.fullmatch(expected_sha256):
        raise ValueError("expected SHA256 must be 64 lowercase hex digits")
    if expected_length is not None and (type(expected_length) is not int
                                        or not 0 < expected_length <= max_bytes):
        raise ValueError("expected length outside byte budget")
    if kind.startswith("zelph-") and (
        dataset_revision is None or not _HEX40.fullmatch(dataset_revision)
    ):
        raise ValueError("Zelph transfer requires immutable 40-hex dataset revision")
    if kind.startswith("zelph-") and "huggingface.co" in (urlsplit(url).hostname or ""):
        # For HF URLs, prohibit moving references such as main/latest.
        if "/resolve/" in url and ("/resolve/" + dataset_revision + "/") not in url:
            raise ValueError("HF resolve path must use the exact pinned dataset SHA")
    if destination.exists() or destination.is_symlink():
        raise ValueError("refuse overwrite or symlink destination")
    if not destination.parent.is_dir() or destination.parent.is_symlink():
        raise ValueError("destination parent must exist and not be a symlink")
    return {
        "version": "itir.source_acquisition.pinned_transport.v1",
        "source_kind": kind, "requested_url": url,
        "requested_revision": dataset_revision,
        "expected_sha256": expected_sha256,
        "expected_bytes": expected_length,
        "byte_budget": max_bytes,
        "destination": str(destination),
        "download_performed": False,
        "digest_matches_supplied_pin": False,
        "upstream_source_origin_independently_authenticated": False,
        "primary_document_semantics_verified": False,
        "creates_world_truth": False,
        "edit_authority": False,
    }


class PublicHTTPSRedirects(HTTPRedirectHandler):
    """Reject redirects before urllib makes an HTTP request to the new host."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        require_public_https(newurl, resolve=True)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def acquire(*, plan: dict, destination: Path, timeout_seconds: int = 45) -> dict:
    if type(timeout_seconds) is not int or timeout_seconds <= 0:
        raise ValueError("positive timeout required")
    require_public_https(plan["requested_url"], resolve=True)
    digest = sha256()
    length = 0
    temp_name = None
    try:
        req = Request(plan["requested_url"], headers={
            "Accept-Encoding": "identity",
            "User-Agent": "ITIR-source-acquisition-v1 (read-only)",
        })
        with build_opener(PublicHTTPSRedirects()).open(req, timeout=timeout_seconds) as response:
            final_url = response.geturl()
            require_public_https(final_url, resolve=True)
            if response.status != 200:
                raise ValueError("whole-object HTTP 200 required (no ranges/partial content)")
            advertised = response.headers.get("Content-Length")
            advertised_length = None
            if advertised is not None:
                if not advertised.isdecimal() or int(advertised) > plan["byte_budget"]:
                    raise ValueError("HTTP content exceeds byte budget")
                if plan["expected_bytes"] is not None and int(advertised) != plan["expected_bytes"]:
                    raise ValueError("HTTP length differs from externally supplied length")
                advertised_length = int(advertised)
            with tempfile.NamedTemporaryFile(mode="wb", dir=destination.parent,
                                             prefix=".itir-source-", delete=False) as f:
                temp_name = f.name
                while True:
                    block = response.read(min(_CHUNK, plan["byte_budget"] - length + 1))
                    if not block:
                        break
                    length += len(block)
                    if length > plan["byte_budget"]:
                        raise ValueError("stream exceeds explicit byte budget")
                    digest.update(block)
                    f.write(block)
                f.flush()
                os.fsync(f.fileno())
        if (length == 0 or
                (advertised_length is not None and length != advertised_length) or
                (plan["expected_bytes"] is not None and length != plan["expected_bytes"])):
            raise ValueError("truncated/empty source")
        value = digest.hexdigest()
        if plan["expected_sha256"] is not None and value != plan["expected_sha256"]:
            raise ValueError("source bytes differ from supplied SHA256 pin")
        # os.link is atomic and refuses destination overwrite, even on a race.
        os.link(temp_name, destination, follow_symlinks=False)
        return {**plan, "download_performed": True,
                "final_url": final_url, "bytes_written": length,
                "observed_sha256": value,
                "digest_matches_supplied_pin": plan["expected_sha256"] is not None}
    finally:
        if temp_name is not None:
            Path(temp_name).unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True)
    parser.add_argument("--source-kind", choices=sorted(_ALLOWED), required=True)
    parser.add_argument("--destination", type=Path, required=True)
    parser.add_argument("--max-mib", type=int, required=True)
    parser.add_argument("--expected-sha256")
    parser.add_argument("--expected-bytes", type=int)
    parser.add_argument("--dataset-revision")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    try:
        plan = acquisition_plan(url=args.url, kind=args.source_kind,
            destination=args.destination, max_bytes=args.max_mib * 1024**2,
            expected_sha256=args.expected_sha256, expected_length=args.expected_bytes,
            dataset_revision=args.dataset_revision)
        if args.execute:
            plan = acquire(plan=plan, destination=args.destination)
        output = json.dumps(plan, sort_keys=True, indent=2) + "\n"
        if args.receipt:
            with args.receipt.open("x", encoding="utf-8") as receipt:
                receipt.write(output)
        else:
            print(output, end="")
        return 0
    except (OSError, ValueError, OverflowError) as exc:
        print(json.dumps({"status": "blocked", "reason": str(exc),
                          "edit_authority": False}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
