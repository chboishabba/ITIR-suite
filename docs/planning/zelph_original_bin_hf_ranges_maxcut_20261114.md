# Same-original Zelph `.bin` ↔ selected HF shards — physical maximum-cut receipt (2026-11-14)

## New native original-bin two-pass mini-fixture gate (new head not yet rerun)

The existing `tools/check_zelph_native_capnp_roundtrip.sh` now builds **three** C++ binaries with original upstream-generated Cap'n Proto: native writer, selected shard decoder and `zelph_bin_filtered_route_builder.cpp`. It generates all four packed shard types PLUS an original packed header, concatenates an internally consistent full mini source `.bin`, and runs the **actual original two-pass filtered route producer** on `--qid Q1 --node 8`. The fixture has `Q1 ↔ 7`, left `7→{8,9}`, right `7→{10}`, and unnamed numeric node `8` with left `8→{11}` and right `8→{12}`. It checks routes, source-local oracle arrays, value count, nontruncation, exact chunk indices, nameless node 8 decode, wrong-section/index/language/trailer controls and read-only flags. This is a genuine source-format **synthetic binary** contract, not an original Wikidata/HF provenance witness.

Run **new exact committed head**:

```bash
bash tools/check_zelph_physical_maxcut_offline.sh
# Also use the golden pinned Agda 2.9 9-target acceptance in DASHI #1506:
bash scripts/check_zelph_trie_hyperfabric_maxcut.sh
# And SLR B5 new native structural comparison:
cargo test -p sensiblaw-source-handoff native_statement_evidence
```

Only the **previous** ITIR `e64c04f` head is operator-verified at 95 Python + native 4/5. The new A1/A2 Agda, added Python finite-word/unnamed numeric route controls, original two-pass mini-bin and SLR native Rust source have **no new exact-head acceptance receipt yet**. The local agent created/tested a standalone Python prototype with 16/16 synthetic tests, which is not a check of the final committed source and must not be presented as one.


## New A2 finite relation-word closure — explicit numeric frontier loop

**New implementation at latest ITIR #14 source (NOT included in prior exact-head 95/95 receipt):** original C++ filtered producer accepts extra `--node <u64>` root IDs in addition to unchanged five QID seeds, preserving sorted/distinct numeric identity and using the **same two scans** of the original `.bin`. This does not create a graph index or fabricate a QID for an unnamed numeric node. The original range verifier, immutable HF selected fetch and native decoder now select and audit the exact union of five named roots and extra numeric nodes. `audit_zelph_native_selected_physical.py` exports the source-bin-equal `root_adjacency` for each checked numeric node/direction, along with QID names and extra roots.

`audit_zelph_finite_query_family.py` composes those finite one-hop equalities for explicit numeric `left`/`right` relation words. Every intermediate `(node, direction)` must have a source- and selected-equal native root observation from the same graph revision and manifest. Missing boundaries are emitted as concrete next scanner targets; they do **not** give scoped absence. This is a finite path construction, not a property-filtered P31/P279/P14143/SPARQL query.

The five QID/node numeric pairs in the example below are **operator-reported historical mapping values**, not current accepted live bytes. The example exercises 20 one- and two-hop queries and should initially produce missing boundaries for most two-hop words until the original source frontier is traversed.

```bash
# First: the separate immutable byte / source route / native decoder steps below
# must already have produced an ACTUAL native-selected-physical-answer.json.
FAMILY=docs/planning/zelph_five_qid_lr_query_family.example.json
AUDIT=/path/to/native-selected-physical-answer.json
python tools/audit_zelph_finite_query_family.py \
  --query-family "$FAMILY" --native-audit "$AUDIT" \
  --output /path/to/finite-lr-query-closure.json
# Exit 3 is an expected FAIL-CLOSED 'missing intermediate physical rows',
# not a source-negative answer. Read missing_boundaries in the JSON.

# Rerun the original source-bin producer with ALL five real seed QIDs,
# plus EACH distinct numeric node_id from missing_boundaries. Do not use
# fake QID strings; explicit --node is the new bounded source-frontier path.
tools/zelph_bin_filtered_route_builder --bin "$BIN" \
  --output /path/to/expanded-original-bin-route.json \
  --qid Q10403939 --qid Q10416948 --qid Q10422059 \
  --qid Q10651551 --qid Q56404383 \
  --node <exact-node-from-missing-boundaries>
# Repeat selected-only HF fetch, exact original-bin byte-range proof,
# native schema replay with the expanded route, and finite closure until
# ALL declared finite words close or the explicit cap/truncation stops it.

# Local exact-head source verification; includes original 95-suite tests
# plus newly added finite-word and numeric frontier checks:
bash tools/check_zelph_physical_maxcut_offline.sh
```

**Important:** The example `--node <...>` is a placeholder, not a runnable numeric argument. Fill it from the actual missing-boundary JSON. The original binary must be authenticated independently and the native source-bin route oracle is not recomputed inside the final finite-word checker. A report with `all_declared_words_closed=true` is therefore **conditional on the attached native source audits**, not a standalone proof of original HF authenticity. It does not supply source support, write rights, or native Wikibase P854/P14143 statements.

**New proof partner:** [DASHI/Interop/ZelphFiniteQueryWordClosureExact.agda](https://github.com/chboishabba/dashi_agda/blob/agent/nora-perspective-consumer-maxcut-20261114/DASHI/Interop/ZelphFiniteQueryWordClosureExact.agda) proves source-reachable one-step equality implies equality of the entire declared finite relation word. New Agda head **not yet typechecked**; existing exact seven-module earlier Agda PASS remains valid at its source commit.



## 15 November FLN ↔ original Zelph HF source and reviewer gate

The separate [DASHI Ibrahim exact-lemma acceptance matrix](https://github.com/chboishabba/dashi_agda/blob/feat/ibrahim-fln-ternary-revision-maxcut-20261114/Docs/IbrahimFLNMaximumCutAcceptanceAndExactLemmas20261115.md) now lists the original-wikitext first-link edge, the selected Hyperfabric physical incidence and reviewed ITIR consumer as **three distinct original objects until a physical/source crosswalk is produced**. The native Zelph `nodeOfName`/QID/name graph does not, by itself, prove that a Wikipedia article's first qualifying hyperlink points to the same node, nor that its cross-language meaning was reviewed. Retain original page `oldid`, `pageid`, wikitext hash/selected span, original `.bin` offsets/digest and source→target adjacency in the joined receipt.

**Current ITIR acceptance boundary:** the operator reported **58/58 earlier Python tests** and **32/32 new tests after two local corrections** at `bcbf7c3` (initial 23/32). The corrected worktree total is **90/90 locally**, and `clang++ -fuse-ld=lld` successfully compiled the native decoder. The subsequent physical hardening and real Cap'n Proto generator/decoder roundtrip are **source written but not yet clean-head executed**. ITIR #14 current source head when this crosswalk was written: `e64c04f`. No same-run original-source `.bin` ↔ selected shard comparison, published complete-name partition, A2 original/selected query-family closure, original P14143/P854/GUID, S29 persisted-review receipt or authentic Éder Porto NORA export was supplied to this assistant.

**Next ordered deliverables:**
1. Clean-head `bash tools/check_zelph_physical_maxcut_offline.sh`: 90 Python, native packed writer→reader roundtrip for all four sections and negative controls.
2. Repeated original-range audit with `--source-bin` (only once), correct immutable chunk index/object filename, source offset/length, actual SHA, URI and HTTP 206 original-byte provenance; fail closed when unavailable.
3. Complete original-name partition and actual decoded first-hop and query-family source/selected adjacency equality on a single dataset revision and physical manifest. No inferred global absence from an unvisited source graph.
4. An independently retrieved original Wikipedia revision/selector span packet and explicit crosswalk if integrating FLN; source identity must be verified, not inferred from QID/name.
5. Pass approved reviewer/consumer-specific result to existing SLR/S29 and SensibLaw NORA owners; retain original source views and recheck after persisted reload. No external edit is authorised by the tests.

**Original attribution:** Zelph upstream data/shards are external; Ibrahim/Danforth/Dodds are original FLN method authors (DOI 10.1016/j.jocs.2016.12.001); the original sheaf-hypergraph model is due to Duta et al.; Éder Porto owns external NORA work. The crosswalk constraints are DASHI/ITIR integration governance and not a source data receipt.

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
