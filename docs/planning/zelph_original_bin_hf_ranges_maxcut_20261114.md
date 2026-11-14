# Same-original Zelph `.bin` ↔ selected HF shards — physical maximum-cut receipt (2026-11-14)

**State:** Source and tests committed in ITIR PR #14; NO actual HF source-range or native Cap’n Proto execution receipt yet in this chat. The operator's 58/58 earlier Python tests preceded these additions. The 7/7 exact-head Agda 2.9 check at DASHI commit `4c89edbe90ef0e29ea5c02b18bd5dfe090ab9e61` passed separately.

## What was actually added

| Gate | Existing-owner implementation | What its successful physical run proves |
|---|---|---|
| P0a | `tools/plan_zelph_hf_selected_fetch.py` | Deterministic selected-only immutable HF file list and explicit GiB cap (network off by default; `--execute` invokes HF CLI) |
| P0b | `tools/verify_zelph_bin_shard_exact.py` | Each selected published packed shard is byte-for-byte the corresponding `offset`/`length` range from the *local* original `.bin` |
| P0c | `tools/verify_zelph_hf_remote_original_ranges.py` | Optional same-source comparison without local 82 GiB original: exact immutable remote original-bin HTTP `206 Content-Range` equals selected local shard bytes; rejects server fallback to `200` |
| A1/A2 decoder | `tools/zelph_selected_packed_shard_decoder.cpp` | Native schema-specified `AdjChunk`, `NameChunk`, and `NodeNameChunk` rows for selected nodes and names; checked section-global chunk index, language, and truncation |
| A1/A2 witness | `tools/audit_zelph_native_selected_physical.py` | Requires a prior P0 local/remote range equality receipt, rehashes every selected shard, checks actual QID→node and inverse name rows and compares decoded left/right neighbour sets and value counts to the *original-bin* route oracle |

## Exact operator execution (requires external original `.bin` and/or functioning HF range requests)

```bash
REV=0d4bd670959ebddae72f70d973410fdea8917ec1
MANIFEST_SHA=cedd5cf0e4951ae1aa7c2c5968614b0eb72a4c3b5c8b2dc4ab18c40be8c83f59
ART=wikidata-20260309-all
ROOT=/path/to/hf-root
BIN=/path/to/wikidata-20260309-all.bin
MANIFEST="$ROOT/$ART/$ART.hf-v2.json"
ROUTE=/path/to/new-source-bin-filtered-route.json
RANGE=/path/to/selected-range-proof.json
MAX_GIB=16

# 1. Acquire the actual manifest at immutable revision and independently hash.
hf download acrion/zelph "$ART/$ART.hf-v2.json" --repo-type dataset --revision "$REV" --local-dir "$ROOT"
sha256sum "$MANIFEST" # MUST equal MANIFEST_SHA

# 2. Compile and run existing filtered route builder against original source .bin
# (same generated upstream capnp schema as existing builder).
g++ -std=c++17 -O2 -I aur/zelph/build-local/src/lib/io \
  tools/zelph_bin_filtered_route_builder.cpp \
  aur/zelph/build-local/src/lib/io/zelph.capnp.c++ \
  -lcapnp -lkj -o tools/zelph_bin_filtered_route_builder
tools/zelph_bin_filtered_route_builder --bin "$BIN" --output "$ROUTE" \
  --qid Q10403939 --qid Q10416948 --qid Q10422059 \
  --qid Q10651551 --qid Q56404383

# 3. Plan first, then explicitly download ONLY selected HF physical chunks.
python tools/plan_zelph_hf_selected_fetch.py \
  --manifest "$MANIFEST" --route "$ROUTE" \
  --dataset-revision "$REV" --manifest-sha256 "$MANIFEST_SHA" \
  --shard-root "$ROOT" --max-selected-gib "$MAX_GIB"
python tools/plan_zelph_hf_selected_fetch.py \
  --manifest "$MANIFEST" --route "$ROUTE" \
  --dataset-revision "$REV" --manifest-sha256 "$MANIFEST_SHA" \
  --shard-root "$ROOT" --max-selected-gib "$MAX_GIB" --execute

# 4A. Local same-original.bin packed-range identity, if original file present.
python tools/verify_zelph_bin_shard_exact.py \
  --manifest "$MANIFEST" --route "$ROUTE" --source-bin "$BIN" \
  --shard-root "$ROOT" --dataset-revision "$REV" \
  --manifest-sha256 "$MANIFEST_SHA" --max-selected-gib "$MAX_GIB" \
  --output "$RANGE"

# 4B. ALTERNATIVE (not additional requirement): immutable HF HTTP 206
# source-bin byte ranges, with no local 82 GiB binary:
# python tools/verify_zelph_hf_remote_original_ranges.py \
#   --manifest "$MANIFEST" --route "$ROUTE" --shard-root "$ROOT" \
#   --dataset-revision "$REV" --manifest-sha256 "$MANIFEST_SHA" \
#   --max-selected-gib "$MAX_GIB" --output "$RANGE"

# 5. Build native schema decoder and check selected physical one-hop answer.
g++ -std=c++17 -O2 -I aur/zelph/build-local/src/lib/io \
  tools/zelph_selected_packed_shard_decoder.cpp \
  aur/zelph/build-local/src/lib/io/zelph.capnp.c++ \
  -lcapnp -lkj -o tools/zelph_selected_packed_shard_decoder
python tools/audit_zelph_native_selected_physical.py \
  --manifest "$MANIFEST" --route "$ROUTE" --range-receipt "$RANGE" \
  --shard-root "$ROOT" --decoder tools/zelph_selected_packed_shard_decoder \
  --dataset-revision "$REV" --manifest-sha256 "$MANIFEST_SHA" \
  --max-selected-gib "$MAX_GIB" \
  --output /path/to/native-selected-physical-answer.json

# 6. New regressions (NOT part of prior 58/58 pass):
python -m pytest -q \
  tests/test_verify_zelph_bin_shard_exact.py \
  tests/test_verify_zelph_hf_remote_original_ranges.py \
  tests/test_plan_zelph_hf_selected_fetch.py \
  tests/test_audit_zelph_native_selected_physical.py
```

**Footprint:** The full public original source is approximately 82 GiB, structured into 984 left, 984 right, 204 nameOfNode and 204 nodeOfName chunks. The new tools select only source-routed chunks and enforce a declared maximum selected byte budget. Public background: https://zelph.org/sharding/ and https://zelph.org/binaries/ .

**Important blocker:** Source URLs were verified from Zelph's public documentation, but direct DNS to huggingface.co is unavailable in this assistant's container. No remote manifest or shard was fetched or rehashed here. The HTTP-206 alternative must be run on an environment that can access the immutable Hub endpoint; some CDNs may refuse byte ranges, which must be treated as a blocked gate rather than as a successful fallback.

**Do not conflate:** Physical same-original byte-range equality is a real material advance, but it proves neither completeness of the original graph's name domain nor arbitrary relation words. The native QID↔node and left/right decoder join covers selected roots only. No query-negative/global absence, native P14143 quantity, GUID, qualifier, P854 primary source, SLR S29 persistence, NORA original export or edit authority follows. Old route and receipt digests must be preserved as historical: the new C++ root-adjacency route has a DIFFERENT content address.

**Ownership:** DASHI/Agda golden contracts; existing ITIR Python/C++ Zelph physical integration; SLR Rust/PostgreSQL authoritative native source/review state; SensibLaw Python historical handoff; external NORA author Éder Porto.
