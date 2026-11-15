#!/usr/bin/env python3
"""Read-only original P854 document-byte receipt bound to native Wikibase reference.

A matching URL plus pinned downloaded bytes proves a transport observation,
NOT that the document's text supports the statement, nor edit authority.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import sys
from typing import Any

from verify_zelph_bin_shard_exact import _read_json

_SHA = re.compile(r"[0-9a-f]{64}\Z")


def check_document(*, native: dict[str, Any],
                   acquisition: dict[str, Any], raw_document: Path,
                   max_bytes: int = 128 * 1024 * 1024) -> dict[str, Any]:
    if (native.get("source_kind") != "full-wikibase-json-entity"
            or native.get("same_source_native_statement_found") is not True
            or native.get("snapshot_bytes_match_pinned_digest") is not True):
        raise ValueError("actual exact-native Wikibase statement receipt required")
    urls = native.get("p854_url_candidates")
    url = acquisition.get("requested_url")
    if (type(urls) is not list or not urls or type(url) is not str
            or urls.count(url) < 1):
        raise ValueError("document acquisition URL not in original native P854 references")
    if (acquisition.get("source_kind") != "p854-document"
            or acquisition.get("download_performed") is not True):
        raise ValueError("no actual original P854 acquisition receipt")
    if (type(max_bytes) is not int or max_bytes <= 0
            or not raw_document.is_file()
            or not 0 < raw_document.stat().st_size <= max_bytes):
        raise ValueError("P854 source document missing/over byte budget")
    observed = acquisition.get("observed_sha256")
    if type(observed) is not str or not _SHA.fullmatch(observed):
        raise ValueError("acquisition receipt lacks full observed SHA256")
    digest = sha256()
    length = 0
    with raw_document.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            length += len(block)
            if length > max_bytes:
                raise ValueError("P854 document exceeded byte budget")
            digest.update(block)
    if digest.hexdigest() != observed or acquisition.get("bytes_written") != length:
        raise ValueError("original downloaded P854 bytes disagree with acquisition receipt")
    externally_pinned = acquisition.get("expected_sha256")
    if externally_pinned is not None and (not _SHA.fullmatch(externally_pinned)
                                          or externally_pinned != observed):
        raise ValueError("P854 document differs from externally supplied expected SHA256")
    return {
        "version": "itir.wikidata.p854_actual_document_bytes.v1",
        "subject_qid": native["subject_qid"],
        "statement_guid": native["statement_guid"],
        "native_entity_revision_id": native["native_entity_revision_id"],
        "native_raw_sha256": native["raw_entity_sha256_checked"],
        "source_p854_url": url,
        "download_final_url": acquisition.get("final_url"),
        "document_sha256": observed,
        "document_bytes": length,
        "actual_document_bytes_compared_with_acquisition": True,
        "independent_digest_pin_supplied": externally_pinned is not None,
        "document_content_semantically_inspected": False,
        "primary_document_support_for_claim_verified": False,
        "reviewer_disposition_persisted": False,
        "source_support_paid": False,
        "edit_authority": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-native-observation", type=Path, required=True)
    parser.add_argument("--acquisition-receipt", type=Path, required=True)
    parser.add_argument("--document", type=Path, required=True)
    parser.add_argument("--max-mib", type=int, default=128)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        native = _read_json(args.raw_native_observation, 64 * 1024 * 1024)
        acquisition = _read_json(args.acquisition_receipt, 1024 * 1024)
        doc = check_document(native=native, acquisition=acquisition,
                             raw_document=args.document, max_bytes=args.max_mib * 1024**2)
        body = json.dumps(doc, sort_keys=True, indent=2) + "\n"
        if args.output:
            with args.output.open("x", encoding="utf-8") as f:
                f.write(body)
        else:
            print(body, end="")
        return 0
    except (ValueError, TypeError, KeyError, OSError, OverflowError) as exc:
        print(json.dumps({"status": "blocked", "reason": str(exc),
                          "edit_authority": False}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
