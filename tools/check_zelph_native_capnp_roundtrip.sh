#!/usr/bin/env bash
# Native P0/A1/A2 kernel-adjacent acceptance; no HF downloads.
# Uses real generated Zelph Cap'n Proto, exact packed writers/readers.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

CXX="${ZELPH_CXX:-clang++}"
CAPNP_ROOT="${ZELPH_CAPNP_INCLUDE:-aur/zelph/build-local/src/lib/io}"
CAPNP_GENERATED="${ZELPH_CAPNP_CPP:-$CAPNP_ROOT/zelph.capnp.c++}"
if ! command -v "$CXX" >/dev/null 2>&1; then
  echo "BLOCKED: C++ compiler not found: $CXX" >&2
  exit 2
fi
if [ ! -r "$CAPNP_ROOT/zelph/zelph.capnp.h" ] && [ ! -r "$CAPNP_ROOT/zelph.capnp.h" ]; then
  echo "BLOCKED: generated original Zelph capnp header not found under $CAPNP_ROOT" >&2
  exit 2
fi
if [ ! -r "$CAPNP_GENERATED" ]; then
  echo "BLOCKED: generated original Zelph Cap'n Proto .c++ absent: $CAPNP_GENERATED" >&2
  exit 2
fi

TMP="$(mktemp -d -t zelph-native-roundtrip.XXXXXX)"
trap 'rm -rf "$TMP"' EXIT

# Local Cap'n Proto static archives may contain LLVM IR bitcode, requiring
# clang + lld rather than the distro g++/ld.bfd. Override ZELPH_LD_FLAG if
# your pinned build uses another compatible linker.
LINKER_FLAG="${ZELPH_LD_FLAG:--fuse-ld=lld}"
COMMON=("$LINKER_FLAG" -std=c++17 -O2 -I "$CAPNP_ROOT")
"$CXX" "${COMMON[@]}" tools/zelph_native_capnp_fixture.cpp \
  "$CAPNP_GENERATED" -lcapnp -lkj -o "$TMP/fixture"
"$CXX" "${COMMON[@]}" tools/zelph_selected_packed_shard_decoder.cpp \
  "$CAPNP_GENERATED" -lcapnp -lkj -o "$TMP/decoder"
"$CXX" "${COMMON[@]}" tools/zelph_bin_filtered_route_builder.cpp \
  "$CAPNP_GENERATED" -lcapnp -lkj -o "$TMP/original-filtered-route"

# The new --node frontier flag is explicit; reject nondecimal, signed IDs.
# A valid numeric ID should reach the (intentionally absent) source bin,
# not be rejected as an unknown argument.
if "$TMP/original-filtered-route" --bin "$TMP/absent.bin" \
  --output "$TMP/absent-route.json" --qid Q1 --node -1 \
  >"$TMP/invalid.stdout" 2>"$TMP/invalid.stderr"; then
  echo "BLOCKED: accepted negative numeric node ID" >&2
  exit 3
fi
grep -q "nondecimal numeric frontier ID" "$TMP/invalid.stderr" || {
  cat "$TMP/invalid.stderr" >&2
  echo "BLOCKED: did not reject invalid numeric frontier at the parser" >&2
  exit 3
}
if "$TMP/original-filtered-route" --bin "$TMP/absent.bin" \
  --output "$TMP/absent-route.json" --qid Q1 --node 42 \
  >"$TMP/valid.stdout" 2>"$TMP/valid.stderr"; then
  echo "BLOCKED: unexpectedly found source .bin fixture" >&2
  exit 3
fi
grep -q "failed to open source bin" "$TMP/valid.stderr" || {
  cat "$TMP/valid.stderr" >&2
  echo "BLOCKED: valid numeric source root did not reach source opening" >&2
  exit 3
}

mkdir -p "$TMP/packed"
"$TMP/fixture" "$TMP/packed"

python3 - "$TMP/decoder" "$TMP/packed" <<'PY'
import json
from pathlib import Path
import subprocess
import sys

exe, root = sys.argv[1], Path(sys.argv[2])


def run(section, *extra, file=None):
    path = file or root / (section + ".capnp-packed")
    return subprocess.run([
        exe, "--file", str(path), "--section", section,
        "--chunk-index", "0", *extra,
    ], text=True, capture_output=True, timeout=60, check=False)


expected = {
    "left": ([ "--node", "7"], [{"node_id": 7, "neighbors": [8, 9],
                                 "values_seen": 2, "truncated": False}]),
    "right": (["--node", "7"], [{"node_id": 7, "neighbors": [10],
                                "values_seen": 1, "truncated": False}]),
    "nameOfNode": (["--lang", "wikidata", "--node", "7"],
                   [{"node_id": 7, "name": "Q1"}]),
    "nodeOfName": (["--lang", "wikidata", "--qid", "Q1"],
                   [{"name": "Q1", "node_id": 7}]),
}
for section, (args, rows) in expected.items():
    proc = run(section, *args)
    assert proc.returncode == 0, (section, proc.stderr, proc.stdout)
    payload = json.loads(proc.stdout)
    assert payload["version"] == "itir.zelph.selected_native_capnp_decode.v1"
    assert payload["section"] == section and payload["chunk_index"] == 0
    assert payload["rows"] == rows, (section, payload["rows"])
    assert payload["candidate_only"] is True
    assert payload["authority"] is False

# Direction and chunk-index are not interchangeable.
assert run("right", "--node", "7",
           file=root / "left.capnp-packed").returncode != 0
assert subprocess.run([
    exe, "--file", str(root / "left.capnp-packed"),
    "--section", "left", "--chunk-index", "1", "--node", "7",
], capture_output=True).returncode != 0
# Name language mismatch must fail.
assert run("nameOfNode", "--lang", "en", "--node", "7").returncode != 0
# Preserve selection-only semantics: missing QID returns no candidate rows.
assert json.loads(run("nodeOfName", "--qid", "Q99999").stdout)["rows"] == []
# An otherwise valid packed message with a trailer must not decode as one
# exact message with silent ignored bytes.
tampered = root / "left-trailing.capnp-packed"
tampered.write_bytes((root / "left.capnp-packed").read_bytes() + b"trailing")
assert run("left", "--node", "7", file=tampered).returncode != 0

print("PASS: 4 native packed Zelph section roundtrips and 5 fail-closed controls")
PY

echo "PASS: native Cap'n Proto fixture + selected decoder compile and replay"
echo "NOT COVERED: actual immutable HF objects, original 82 GiB binary provenance,"
echo "whole graph name or query completeness, Wikidata native P854, S29, NORA."
