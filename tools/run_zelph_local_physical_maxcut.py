#!/usr/bin/env python3
"""One local, fail-closed P0→P1→P2 Zelph source-bin/shard native witness.

No download or invented dataset identity. Uses an existing ORIGINAL .bin, a
pinned raw manifest and already-present selected HF shard objects. Runs the
original Cap'n Proto two-pass filtered producer, independently replays selected
raw packed source offsets in the same process, then executes the native
four-section selected decoder + bounded root adjacency equality. Optionally
checks finite left/right query words and reports exact missing frontiers.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any

from verify_zelph_bin_shard_exact import verify_selected_source_ranges
from audit_zelph_native_selected_physical import verify_native_selected_shard_answer
from audit_zelph_finite_query_family import finite_relation_word_closure, _strict_json

_REV = re.compile(r'[0-9a-f]{40}\Z')
_SHA = re.compile(r'[0-9a-f]{64}\Z')
_QID = re.compile(r'Q[1-9][0-9]*\Z')


def _raw_sha(path: Path) -> str:
    digest = sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(4 * 1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, sort_keys=True, indent=2) + '\n', encoding='utf-8')


def run_local_physical_maxcut(*, source_bin: Path, manifest: Path, shard_root: Path,
                              producer: Path, decoder: Path, output_dir: Path,
                              dataset_revision: str, manifest_sha256: str,
                              qids: list[str], extra_nodes: list[int] | None = None,
                              family_path: Path | None = None,
                              expected_source_bin_sha256: str | None = None,
                              max_selected_gib: int = 16,
                              producer_timeout_seconds: int = 7200) -> dict[str, Any]:
    if not _REV.fullmatch(dataset_revision) or not _SHA.fullmatch(manifest_sha256):
        raise ValueError('immutable dataset revision and manifest SHA256 required')
    if not qids or len(qids) > 10000 or len(set(qids)) != len(qids) or any(not _QID.fullmatch(qid) for qid in qids):
        raise ValueError('nonempty distinct canonical QID roots required')
    nodes = extra_nodes or []
    if (len(nodes) > 100000 or nodes != sorted(set(nodes))
            or any(type(node) is not int or not 0 <= node <= 2**64 - 1 for node in nodes)):
        raise ValueError('numeric source frontier must be sorted distinct uint64 values')
    if type(max_selected_gib) is not int or max_selected_gib <= 0:
        raise ValueError('positive selected physical GiB budget required')
    if type(producer_timeout_seconds) is not int or producer_timeout_seconds <= 0:
        raise ValueError('positive bounded original-producer timeout required')
    for required in (source_bin, manifest, producer, decoder):
        if not required.is_file():
            raise ValueError(f'missing required actual file: {required}')
    if not shard_root.is_dir():
        raise ValueError('selected immutable shard root is unavailable')
    # Optional explicit external hash; a local filesystem path does not prove
    # provenance. Even a matching SHA requires independent trusted sourcing.
    source_matched = expected_source_bin_sha256 is not None
    if source_matched:
        if not _SHA.fullmatch(expected_source_bin_sha256):
            raise ValueError('expected original .bin digest must be lowercase SHA256')
        if _raw_sha(source_bin) != expected_source_bin_sha256:
            raise ValueError('original .bin bytes disagree with externally pinned digest')
    if _raw_sha(manifest) != manifest_sha256:
        raise ValueError('published raw manifest SHA256 mismatch')
    output_dir.mkdir(parents=True, exist_ok=True)
    if not output_dir.is_dir():
        raise ValueError('physical evidence output path is not a directory')
    for filename in ('route-new.json', 'selected-range-proof.json',
                     'native-selected-physical-answer.json',
                     'finite-lr-query-closure.json', 'physical-acceptance.json'):
        if (output_dir / filename).exists():
            raise ValueError('output directory already contains physical evidence; refuse overwrite')
    route = output_dir / 'route-new.json'
    range_path = output_dir / 'selected-range-proof.json'
    native_path = output_dir / 'native-selected-physical-answer.json'
    summary_path = output_dir / 'physical-acceptance.json'
    cmd = [str(producer), '--bin', str(source_bin), '--output', str(route)]
    for qid in qids:
        cmd.extend(['--qid', qid])
    for node in nodes:
        cmd.extend(['--node', str(node)])
    proc = subprocess.run(cmd, capture_output=True, text=True,
                          timeout=producer_timeout_seconds, check=False)
    if proc.returncode != 0:
        raise ValueError(f'original .bin two-pass source route producer failed: {proc.stderr[:500]}')
    if not route.is_file() or not 0 < route.stat().st_size <= 64 * 1024 * 1024:
        raise ValueError('producer did not emit bounded source-origin route JSON')
    verified = verify_selected_source_ranges(
        manifest_path=manifest, route_path=route, source_bin=source_bin,
        shard_root=shard_root, dataset_revision=dataset_revision,
        manifest_sha256=manifest_sha256, max_selected_gib=max_selected_gib,
    )
    _write(range_path, verified)
    native = verify_native_selected_shard_answer(
        manifest_path=manifest, route_path=route, range_receipt_path=range_path,
        shard_root=shard_root, decoder_executable=decoder,
        dataset_revision=dataset_revision, manifest_sha256=manifest_sha256,
        max_selected_gib=max_selected_gib, source_bin=source_bin,
    )
    _write(native_path, native)
    closure = None
    if family_path is not None:
        family, _ = _strict_json(family_path)
        closure = finite_relation_word_closure(
            query_family=family, audits=[(native, _raw_sha(native_path))],
        )
        _write(output_dir / 'finite-lr-query-closure.json', closure)
    summary = {
        'version': 'itir.zelph.same_run_local_original_bin_maxcut.v1',
        'dataset_revision': dataset_revision,
        'manifest_sha256': manifest_sha256,
        'source_bin_external_digest_matched_in_this_run': source_matched,
        'upstream_source_origin_independently_authenticated_here': False,
        'original_source_bin_route_producer_executed': True,
        'source_bin_ranges_reverified_in_same_native_audit':
            native['source_bin_range_equality_reverified_in_this_run'],
        'selected_root_one_hop_equal_original_bin':
            native['selected_root_one_hop_bidirectional_adjacency_equal_original_bin'],
        'selected_object_count': native['selected_object_count'],
        'route_raw_sha256': _raw_sha(route),
        'range_proof_raw_sha256': _raw_sha(range_path),
        'native_answer_raw_sha256': _raw_sha(native_path),
        'finite_family_supplied': family_path is not None,
        'finite_words_complete': closure['all_declared_words_closed'] if closure else None,
        'missing_numeric_source_boundaries': closure['missing_boundaries'] if closure else None,
        'source_support_paid': False,
        'p854_document_verified': False,
        'creates_world_truth': False,
        'edit_authority': False,
    }
    _write(summary_path, summary)
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('source-bin','manifest','shard-root','producer','decoder','output-dir'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--dataset-revision', required=True)
    parser.add_argument('--manifest-sha256', required=True)
    parser.add_argument('--qid', action='append', required=True)
    parser.add_argument('--node', type=int, action='append', default=[])
    parser.add_argument('--query-family', type=Path)
    parser.add_argument('--expected-source-bin-sha256')
    parser.add_argument('--max-selected-gib', type=int, default=16)
    parser.add_argument('--producer-timeout-seconds', type=int, default=7200)
    args = parser.parse_args()
    try:
        result = run_local_physical_maxcut(
            source_bin=args.source_bin, manifest=args.manifest,
            shard_root=args.shard_root, producer=args.producer, decoder=args.decoder,
            output_dir=args.output_dir, dataset_revision=args.dataset_revision,
            manifest_sha256=args.manifest_sha256, qids=args.qid,
            extra_nodes=args.node, family_path=args.query_family,
            expected_source_bin_sha256=args.expected_source_bin_sha256,
            max_selected_gib=args.max_selected_gib,
            producer_timeout_seconds=args.producer_timeout_seconds,
        )
        print(json.dumps(result, sort_keys=True, indent=2))
        return 0 if result['finite_words_complete'] is not False else 3
    except (ValueError, OSError, TypeError, subprocess.TimeoutExpired) as exc:
        print(json.dumps({'status': 'blocked', 'reason': str(exc), 'edit_authority': False}), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
