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
"$CXX" "${COMMON[@]}" tools/zelph_original_packed_header_probe.cpp \
  "$CAPNP_GENERATED" -lcapnp -lkj -o "$TMP/original-header-probe"

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

# Directly decode the real original Cap'n Proto packed-header fixture, not
# JSON-declared counts. Probe supports tiny standalone original HTTP206 ranges.
"$TMP/original-header-probe" --header-file "$TMP/packed/header.capnp-packed" \
  > "$TMP/original-header-probe.json"
python3 - "$TMP/original-header-probe.json" <<'PY'
import json
import sys
from pathlib import Path
value = json.loads(Path(sys.argv[1]).read_text())
assert value["version"] == "itir.zelph.native_original_packed_header_probe.v1"
assert {key: value[key] for key in (
    "leftChunkCount", "rightChunkCount",
    "nameOfNodeChunkCount", "nodeOfNameChunkCount",
)} == {key: 1 for key in (
    "leftChunkCount", "rightChunkCount",
    "nameOfNodeChunkCount", "nodeOfNameChunkCount",
)}
assert value["header_size_bytes"] > 0
assert value["source_upstream_authenticity_proved"] is False
assert value["edit_authority"] is False
print("PASS: original packed Zelph header native decoder counts 4 sections")
PY

# A trailing extra byte cannot silently be accepted as part of the
# exact original source packed header interval.
cp "$TMP/packed/header.capnp-packed" "$TMP/header-with-trailer.bin"
printf 'x' >> "$TMP/header-with-trailer.bin"
if "$TMP/original-header-probe" --header-file "$TMP/header-with-trailer.bin" \
  >"$TMP/header-with-trailer.stdout" 2>"$TMP/header-with-trailer.stderr"; then
  echo "BLOCKED: original header parser silently accepted appended trailer" >&2
  exit 3
fi

# Original header decoder refuses non-Cap'n Proto bytes.
printf '\x00\x01\x02' > "$TMP/corrupted-original-header.bin"
if "$TMP/original-header-probe" --header-file "$TMP/corrupted-original-header.bin" \
  > "$TMP/invalid-header.stdout" 2>"$TMP/invalid-header.stderr"; then
  echo "BLOCKED: original header native parser accepted corrupted packed bytes" >&2
  exit 3
fi

# Actually execute the SAME original-bin two-pass producer on a full
# miniature source (not just its CLI parsing) with a named QID root and an
# unnamed numeric node reached through the named root's left adjacency.
"$TMP/original-filtered-route" --bin "$TMP/packed/original-small.bin" \
  --output "$TMP/mini-original-route.json" --qid Q1 --node 8
python3 - "$TMP/mini-original-route.json" <<'PY'
import json
import sys
from pathlib import Path

route = json.loads(Path(sys.argv[1]).read_text())
assert route["routeVersion"] == "zelph-filtered-route/v1"
assert route["requestedQids"] == ["Q1"]
assert route["qidToZelphNodeIds"] == {"Q1": 7}
assert route["qidToNodeOfNameChunks"] == {"Q1": 0}
assert route["additionalNumericNodes"] == [8]
assert route["nodeRoutes"]["7"] == {"left": [0], "right": [0], "nameOfNode": [0]}
assert route["nodeRoutes"]["8"] == {"left": [0], "right": [0], "nameOfNode": []}
assert route["nodeAdjacency"]["7"]["left"] == [8, 9]
assert route["nodeAdjacency"]["7"]["right"] == [10]
assert route["nodeAdjacency"]["8"]["left"] == [11]
assert route["nodeAdjacency"]["8"]["right"] == [12]
for node_id in ("7", "8"):
    row = route["nodeAdjacency"][node_id]
    for direction in ("left", "right"):
        assert row[direction + "Truncated"] is False
assert route["completeQidResolution"] is True
assert route["sourceBinToPublishedHfDatasetIdentityVerified"] is False
print("PASS: native two-pass original mini-bin QID+numeric frontier route")
PY

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

# A numeric source frontier (node 8) has valid physical adjacency
# without inventing any QID or nameOfNode entry for that node.
assert json.loads(run("left", "--node", "8").stdout)["rows"] == [
    {"node_id": 8, "neighbors": [11], "values_seen": 1, "truncated": False}
]
assert json.loads(run("right", "--node", "8").stdout)["rows"] == [
    {"node_id": 8, "neighbors": [12], "values_seen": 1, "truncated": False}
]
assert json.loads(run("nameOfNode", "--node", "8").stdout)["rows"] == []

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



# The upstream original whole-.bin route builder unions repeated same-node
# native AdjPair rows within a single packed shard. The selected decoder must
# have identical semantics, including duplicate occurrence count and scoped
# truncation controls; an unrelated node must never appear as an own result.
python3 - "$TMP/decoder" "$TMP/packed" <<'PY'
import json
from pathlib import Path
import subprocess
import sys
decoder, root = sys.argv[1], Path(sys.argv[2])
path = root / "left-duplicate-node.capnp-packed"
def run(*extra):
    proc = subprocess.run([
        decoder, "--file", str(path), "--section", "left",
        "--chunk-index", "0", "--node", "7", *extra],
        capture_output=True, text=True, timeout=60, check=False)
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    payload = json.loads(proc.stdout)
    assert payload["authority"] is False
    assert payload["candidate_only"] is True
    return payload
assert run()["rows"] == [{
    "node_id": 7, "neighbors": [8, 9, 15],
    "values_seen": 4, "truncated": False,
}]
assert run("--max-neighbors", "2")["rows"] == [{
    "node_id": 7, "neighbors": [8, 9],
    "values_seen": 4, "truncated": True,
}]
print("PASS: native duplicate-node original adjacency union and bounded truncation")
PY


# Exhaustive native name-row mode is separate from the QID selection mode:
# demand one complete footer after reading the packed message through EOF.
# Preserve ambiguous repeated keys as a multi-valued fibre, not a dict.
python3 - "$TMP/decoder" "$TMP/packed" <<'PY'
import json
from pathlib import Path
import subprocess
import sys
exe, root = sys.argv[1], Path(sys.argv[2])

def run(section, filename, *flags):
    return subprocess.run([
        exe, "--file", str(root / filename), "--section", section,
        "--chunk-index", "0", "--lang", "wikidata",
        "--stream-name-rows", *flags
    ], capture_output=True, text=True, timeout=60, check=False)

def checked_rows(section, filename, expected):
    proc = run(section, filename)
    assert proc.returncode == 0, (proc.stderr, proc.stdout)
    docs = [json.loads(line) for line in proc.stdout.splitlines()]
    assert len(docs) == len(expected) + 1
    footer = docs.pop()
    assert footer == {
        "version": "itir.zelph.native_original_name_rows_end.v1",
        "section": section, "chunk_index": 0,
        "language": "wikidata", "rows_emitted": len(expected),
        "candidate_only": True, "authority": False,
    }
    for idx, (row, (name, node_id)) in enumerate(zip(docs, expected)):
        assert row == {
            "version": "itir.zelph.native_original_name_row.v1",
            "section": section, "chunk_index": 0, "language": "wikidata",
            "row_index": idx, "name": name, "node_id": node_id,
        }
    return docs

checked_rows("nameOfNode", "nameOfNode.capnp-packed", [("Q1", 7)])
checked_rows("nodeOfName", "nodeOfName.capnp-packed", [("Q1", 7)])
rows = checked_rows("nodeOfName", "nodeOfName-multifibre.capnp-packed",
                    [("Q1", 7), ("Q1", 8), ("Q2", 9)])
assert [row["node_id"] for row in rows if row["name"] == "Q1"] == [7, 8]

# A deliberately insufficient row cap must return a nonzero exit and never
# emit the required terminal marker; partial stdout cannot be promoted.
limited = run("nodeOfName", "nodeOfName-multifibre.capnp-packed",
              "--max-name-rows", "1")
assert limited.returncode != 0
assert "name-row count exceeds explicit bound" in limited.stderr
assert "native_original_name_rows_end.v1" not in limited.stdout

bad_lang = subprocess.run([
    exe, "--file", str(root / "nodeOfName.capnp-packed"),
    "--section", "nodeOfName", "--chunk-index", "0", "--lang", "en",
    "--stream-name-rows"
], capture_output=True, text=True, timeout=60)
assert bad_lang.returncode != 0

for section, filename in [("left", "left.capnp-packed"),
                          ("right", "right.capnp-packed")]:
    assert run(section, filename).returncode != 0

trailing = root / "nodeOfName-with-trailer.capnp-packed"
trailing.write_bytes((root / "nodeOfName.capnp-packed").read_bytes() + b"attack")
bad_tail = run("nodeOfName", trailing.name)
assert bad_tail.returncode != 0
assert "native_original_name_rows_end.v1" not in bad_tail.stdout
print("PASS: exhaustive native name-row NDJSON + duplicate fibres, "
      "row caps, wrong type/language, and fail-closed trailer")
PY

echo "PASS: native Cap'n Proto fixture + selected decoder compile and replay"
echo "NOT COVERED: actual immutable HF objects, original 82 GiB binary provenance,"
echo "whole graph name or query completeness, Wikidata native P854, S29, NORA."
