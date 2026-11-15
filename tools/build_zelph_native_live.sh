#!/usr/bin/env bash
# Compile the EXISTING original Zelph Cap'n Proto reader/producer for real P1/P2.
# Deliberately separate from the offline checker, which deletes its temp binaries.
# Usage: bash tools/build_zelph_native_live.sh /path/to/new-empty-native-bin-dir
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
OUT="${1:?Pass an explicit NEW empty output directory}"
if [ -L "$OUT" ] || [ -e "$OUT" ] && [ -n "$(ls -A "$OUT")" ]; then
  echo "BLOCKED: destination symlink or non-empty build directory: $OUT" >&2
  exit 2
fi
mkdir -p "$OUT"
OUT="$(cd "$OUT" && pwd -P)"
CXX="${ZELPH_CXX:-clang++}"
CAPNP_ROOT="${ZELPH_CAPNP_INCLUDE:-aur/zelph/build-local/src/lib/io}"
CAPNP_GENERATED="${ZELPH_CAPNP_CPP:-$CAPNP_ROOT/zelph.capnp.c++}"
LINKER_FLAG="${ZELPH_LD_FLAG:--fuse-ld=lld}"
command -v "$CXX" >/dev/null || { echo "BLOCKED: missing C++ compiler" >&2; exit 2; }
test -r "$CAPNP_GENERATED" || { echo "BLOCKED: original generated Capnp .c++ unavailable" >&2; exit 2; }
test -r "$CAPNP_ROOT/zelph/zelph.capnp.h" || test -r "$CAPNP_ROOT/zelph.capnp.h" || {
  echo "BLOCKED: original generated Capnp header unavailable" >&2
  exit 2
}
COMMON=("$LINKER_FLAG" -std=c++17 -O2 -I "$CAPNP_ROOT")
"$CXX" "${COMMON[@]}" tools/zelph_bin_filtered_route_builder.cpp "$CAPNP_GENERATED" \
  -lcapnp -lkj -o "$OUT/original-filtered-route"
"$CXX" "${COMMON[@]}" tools/zelph_selected_packed_shard_decoder.cpp "$CAPNP_GENERATED" \
  -lcapnp -lkj -o "$OUT/selected-decoder"
"$CXX" "${COMMON[@]}" tools/zelph_original_packed_header_probe.cpp "$CAPNP_GENERATED" \
  -lcapnp -lkj -o "$OUT/original-header-probe"
python3 - "$OUT" "$CXX" "$LINKER_FLAG" <<'PY'
import hashlib
import json
from pathlib import Path
import subprocess
import sys
root, compiler, linker = Path(sys.argv[1]), sys.argv[2], sys.argv[3]
binaries = {}
for name in ("original-filtered-route", "selected-decoder", "original-header-probe"):
    binary = root / name
    if not binary.is_file() or binary.stat().st_size == 0:
        raise SystemExit("BLOCKED: missing compiled original native executable " + name)
    h = hashlib.sha256()
    with binary.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    binaries[name] = {"path": str(binary), "sha256": h.hexdigest()}
out = {
    "version": "itir.zelph.native_live_original_build.v1",
    "compiler": compiler, "linker_flag": linker,
    "binary_digests": binaries,
    "compiled_locally": True,
    "validated_against_actual_original_hf_bytes": False,
    "upstream_source_authenticated": False,
    "edit_authority": False,
}
(root / "native-build-receipt.json").write_text(json.dumps(out, sort_keys=True, indent=2) + "\n")
print(json.dumps(out, sort_keys=True, indent=2))
PY
