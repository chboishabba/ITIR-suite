#!/usr/bin/env bash
# Exact-head OFFLINE contract acceptance for ITIR PR #14.
# All Python route/receipt/physical-shape regressions plus genuine Cap'n Proto
# packed-message writer/decoder roundtrip. Does NOT fetch live HF bytes.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
HEAD="$(git rev-parse HEAD)"
printf 'ITIR Zelph physical-contract offline acceptance\nHEAD=%s\n' "$HEAD"
if [ -n "$(git status --porcelain --untracked-files=no)" ]; then
  echo "BLOCKED: tracked files differ from HEAD, not an exact-head receipt." >&2
  exit 3
fi
PYTHONPATH=itir-mcp/src python3 -m pytest -q \
  itir-mcp/tests/test_zelph_query_closure.py \
  itir-mcp/tests/test_exact_wikidata_name_route.py \
  itir-mcp/tests/test_published_zelph_manifest_compat.py \
  tests/test_package_zelph_filtered_route_receipt.py \
  tests/test_verify_zelph_filtered_route_replay.py \
  tests/test_probe_zelph_hf_nat_routes.py \
  tests/test_verify_zelph_bin_shard_exact.py \
  tests/test_verify_zelph_hf_remote_original_ranges.py \
  tests/test_plan_zelph_hf_selected_fetch.py \
  tests/test_audit_zelph_native_selected_physical.py \
  tests/test_audit_zelph_finite_query_family.py \
  tests/test_verify_wikidata_native_entity_snapshot.py

bash tools/check_zelph_native_capnp_roundtrip.sh

if [ -n "$(git status --porcelain --untracked-files=no)" ]; then
  echo "BLOCKED: acceptance wrote changes to tracked source." >&2
  exit 3
fi

printf 'PASS: exact-head offline Python and native Capnp source acceptance: %s\n' "$HEAD"
printf '%s\n' \
  'NOT VERIFIED: physical HF source and manifest bytes, original .bin identity,' \
  'real QID adjacency equality, all-word query closure, native Wikidata' \
  'GUID/P854/P14143, S29 persistence, NORA export or edit authority.'
