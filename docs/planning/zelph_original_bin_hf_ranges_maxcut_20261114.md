# Same-original Zelph `.bin` ↔ selected HF shards — physical maximum-cut receipt (2026-11-14)

## Exact-head offline gate CLOSED — 15 November 2026

**Operator-reported clean execution:** ITIR PR #14 commit `e64c04f32f791502f6feccd3d918ece9a426c122`, command `bash tools/check_zelph_physical_maxcut_offline.sh`, clean tracked worktree, exit 0. **95/95 Python regression tests passed** across ten modules. Both C++ files compiled with `clang++ -fuse-ld=lld -std=c++17 -O2`; the generated upstream-schema packed fixture decoded **four** original Zelph section types correctly and rejected **five** wrong-direction/index/lang/trailer/empty-candidate controls. This supersedes the earlier 90/90 patched-worktree status as the latest offline source-level acceptance.

**What has NOT been checked:** no actual `acrion/zelph` immutable raw manifest fetched/rehashed in this latest run, no original real `.bin` against published shard offset equality, no real original-five-QID `nodeAdjacency` comparison, no full A1 manifest-vs-source name-domain exhaustion, no A2 arbitrary query-family closure, no actual network request/byte budgets, no independent native P854 evidence, no SLR PostgreSQL S29 persistence and no authentic Éder Porto NORA export. The `--source-bin` audit rechecks bytes but still does not recompute the oracle from the original binary or authenticate that binary's upstream origin; its result exposes those false flags. Such proof requires a separately verified source provenance and original producer execution.

### Exact next physical acceptance outputs

| Artifact | Producer | Acceptance criterion |
|---|---|---|
| `original-source.json` | Original binary metadata / independent upstream identity | Same `wikidata-20260309-all` source revision, actual binary SHA/size and provenance; a local arbitrary `.bin` path is insufficient |
| `manifest-raw.json`, SHA256 | HF immutable revision `0d4bd670959ebddae72f70d973410fdea8917ec1` | Real raw digest equals `cedd5cf0e4951ae1aa7c2c5968614b0eb72a4c3b5c8b2dc4ab18c40be8c83f59` or halt and explain |
| `route-new.json` | Original-bin `zelph_bin_filtered_route_builder.cpp` | Five exact QIDs, section-global name/adjacency routes, bounded `nodeAdjacency`, producer/schema digest; **new** hash, not historic `fbc43156...` |
| `selected-shards/` | `plan_zelph_hf_selected_fetch.py --execute` | Only requested pinned objects, no unbounded transfer; real GET/bytes/cache counts separately |
| `selected-range-proof.json` | Local `.bin` exact ranges or immutable HTTP206 original range | **Real original bytes** equal each shard byte range including offset, length, SHA and physical object URI; no source provenance overclaim |
| `native-selected-physical-answer.json` | C++ decoder + `audit_zelph_native_selected_physical.py` | Original-bin name↔node and selected left/right neighbour/value-count equality for five QIDs; no truncation, collision ambiguity or synthetic fixture |
| `query-family-closure.json` | Subsequent query evaluator / proof witness | Exact query grammar, real original answers, selected-view answers and boundary closure for all required steps; one-hop result **not** enough |

**Next run:** use the commands below for P0 real bytes. If local original `.bin` exists, invoke the final native audit with `--source-bin "$BIN"`; if it does not, use immutable remote `206` with the range receipt and mark original-range replay as previously witnessed, not same-run. The current high-information wall is **physical-source access and query-family proof**, not parser/fixture compiler readiness.


## 2026-11-15 local diagnostic receipt and follow-up acceptance

The operator ran four new physical Python suites at **ITIR `bcbf7c3` with local corrections**: initial **23/32**; after fixing the native range argument and the negative test's immutable object path, **32/32** passed. With the previously checked 58 regressions, the operator reports **90/90 passing locally**. The native C++ decoder compiled and ran under **`clang++ -fuse-ld=lld`**, because the system's `libcapnp.a` contains LLVM bitcode that the default GNU linker could not read. These tests used synthetic data and the operator's fixed worktree; they were **not a clean exact-head acceptance of the original `bcbf7c3` commit**.

The exact two fixes are now committed to ITIR #14: `manifest_sha=manifest_sha256` in `audit_zelph_native_selected_physical.py`, and a matching `chunk-000007-wikidata.capnp-packed` URI in the density negative-control fixture. The subsequent source now also pins the original range's **source offset**, remote source URL, and exact HTTP 206 status before native decoding; permits `--source-bin` to **re-verify original .bin byte equality within the same process** rather than trusting a JSON claim; and rejects trailing bytes in native Cap'n Proto shard messages. These newer assertions have **not yet been run**.

### Required new native schema round-trip gate

```bash
# Builds TWO binaries from upstream-generated original Zelph schema:
# a genuine packed fixture writer and the selected-shard decoder;
# runs four real Cap'n Proto sections plus fail-closed negative controls.
bash tools/check_zelph_native_capnp_roundtrip.sh

# Source audit on local original .bin: strengthens a prior receipt by
# repeating exact raw-byte comparisons before native output is accepted.
python tools/audit_zelph_native_selected_physical.py \
  --manifest "$MANIFEST" --route "$ROUTE" --range-receipt "$RANGE" \
  --source-bin "$BIN" --shard-root "$ROOT" \
  --decoder tools/zelph_selected_packed_shard_decoder \
  --dataset-revision "$REV" --manifest-sha256 "$MANIFEST_SHA" \
  --max-selected-gib "$MAX_GIB" \
  --source-bin "$BIN" \
  --output /path/to/native-selected-physical-answer.json
```

The native decoder's successful **compilation alone** is weaker than actual packed-schema round-trip execution. A receipt-only native audit (without `--source-bin`) explicitly returns `source_bin_range_equality_reverified_in_this_run=false`; it remains dependent on the independent previously recorded range receipt. A real five-QID full acceptance must still present the actual immutable HF object bytes, original source `.bin` or remote 206 range, compiled schema adapter, and closed query-family premises.


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
clang++ -fuse-ld=lld -std=c++17 -O2 -I aur/zelph/build-local/src/lib/io \
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
clang++ -fuse-ld=lld -std=c++17 -O2 -I aur/zelph/build-local/src/lib/io \
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
