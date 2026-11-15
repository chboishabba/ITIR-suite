# Zelph A2 original HTTP206 → native left/right → declared 20-word maximum cut

## 15 November source-original A2-B key-filter / candidate replay follow-up

The older full 984+984 section-native scanner below remains an exact but
expensive reference implementation. The [new source-original A2-B operator
maximum cut](https://github.com/chboishabba/ITIR-suite/blob/agent/nat-filtered-route-producer/docs/planning/zelph_original_lr_bloom_sparse_a2_maxcut_20261115.md)
adds genuine upstream Cap'n Proto key-only Bloom membership extraction,
original HTTP206/decoder/bitmap-pinned complete-shard receipts,
candidate-only native adjacency replay and direct 20-word closure support.
It is safe with the operator's currently physically accepted
`left:5`, `right:1`, `right:983`, but will report UNKNOWN outside
these three source-equal chunks. No numeric node-ID range is inferred
because upstream adjacency serialization iterates an unordered segmented
map. Full 984+984 source membership cover or a separately certified
same-original route index remains mandatory to close selected original
one-hop adjacency. The new source and Agda edge-equivalence weld
need fresh exact-head tests.

---

## 15 Nov — reuse audit: Agda golden + upstream Zelph routed HF / historical logs BEFORE 1,968 original adjacency scans

**Why this matters:** The source-first A2 full-scan fallback is *valid as a physical witness but not the architecture's cheapest/default query plan*. Before burning 984+984 original HTTP206 adjacency chunk comparisons, reuse the prior authoring and its historical acceptance logs. The original graph has UNSORTED left/right chunk node keys: neither chunk number nor node ID range gives routes. A genuine same-artifact complete node-route index can select exact candidate original chunks and justify a much cheaper declared finite query family. A previous v3 artifact's route sidecar is not proof about a different full `.bin`.

### Recovered concrete existing owners and primary logs

| Owner | Actual existing code/receipt | Prior physical/review evidence |
|---|---|---|
| DASHI mathematical | `DASHI/Interop/ZelphBoundedGraphCoverageExact.agda`, `ZelphPhysicalShardQueryMaxCutExact.agda`, `ZelphMultiNameShardFibreExact.agda`, `ZelphFiniteQueryWordClosureExact.agda`; existing prefix-ultrametric, typed hyperfabric, query-indexed adequacy | Agda #822 coverage firewall; #1506 9/9 kernel on last operator head; *conditional* coverage/finite-word theorems, no physical HF premises minted |
| Zelph upstream runtime | `.stat-file`, `.index-file`, `.load-partial`, `route-node`, `route-name`/`route-lang`, manifest + original packed Capnp chunk loader, immutable HF cache | `acrion/zelph#25` routed hosted `chbwa/zelph-sharded` v3 smoke 5.476s remote, 7.948s explicit, 21s sequential fallback; `#26` load-all fix; `#30` cache revision/ETag revalidation, 156/156 tests + live 778,058,079 bytes |
| ITIR producer | `tools/zelph_bin_indexer.cpp`, `zelph_bin_route_builder.cpp`, `zelph_bin_v3_bucket_builder.cpp`, `build_zelph_hf_manifest.py`, `build_shared_shard_artifact_contract.py`, `build_ipfs_shard_ref_map.py` | `docs/planning/zelph_bin_sharding_note_20260326.md`: 2017 pruned real route sidecar ~735 MiB, routed `.load-partial` and HF; `zelph_hf_v3_shard_contract_20260326.md`: 1536-shard design/proof, not equivalent by declaration to 2026 full original |
| ITIR runtime | `itir-mcp/src/itir_mcp/shard_transport.py`, `tools/run_zelph_partial_load_harness.py`, exact HF manifest/route selectors, new P0-H/P0-S original HTTP206 provenance tools | `docs/planning/itir_wd_zelph_sensiblaw_flatness_optimisation_roadmap_20260702.md`: live hosted 60,731,574-byte four-section partial load; `zelph_develop_sparql_partial_load_readiness_20260702.md`: July dataset at that date lacked public route/index manifests |
| SLR | `chboishabba/slr#28` route-aware snapshot-first HF, nodeRouteIndex, `P31/P279` slices, 5-wide distinct cold-object dedupe, immutable revision-aware cache/replay, PostgreSQL recurrent acquisition | Sprint 1 PR acceptance was recorded; source/query economics and native physical-object receipt/replay NOT to be reimplemented as another transport controller |
| New ITIR A2-B | `build_zelph_original_lr_bloom.py` and `query_zelph_original_lr_blooms.py` (already in PR #14) | Original-verified source-equal per-chunk native Bloom is a reusable candidate router; negatives only within completely verified chunks, positive candidates still need original native decoder; a complete 984+984 Bloom cover is not obtained from incomplete original source |

### Physical discriminator before proceeding with A2-P/N/F

1. Inspect the **retained pinned** 2026 full original manifest `wikidata-20260309-all.hf-v2.json` (revision `0d4bd670959ebddae72f70d973410fdea8917ec1`, raw manifest SHA `cedd5cf0e4951ae1aa7c2c5968614b0eb72a4c3b5c8b2dc4ab18c40be8c83f59`) for actual `hfObjects.nodeRouteIndex`, `selectorModel.supportedOperations`, `capabilities.nodeRouteIndex`, sidecar SHA and source original `.bin` correspondence. A feature in code or a sidecar from another revision is NOT evidence of its presence here. Earlier July public observations did not find a route sidecar. Importantly, the existing 14 November operator receipt `docs/planning/nat_zelph_hf_physical_route_execution_20261114.md` reports the pinned November full manifest ALSO lacked `hfObjects.nodeRouteIndex`: exact metadata result `manifest-route-index-not-advertised`, `production_accepted=false`. That is a recorded operator observation, not an independent re-fetch of its raw manifest in this source write. The old exact five-QID route content SHA is `fbc43156ae80b8e32f9cbd5b32dd30dcc2085ad9ead04e73e16ff8f376425233`, local receipt `build/receipts/nat_zelph_filtered_route_receipt.json`; this was a name-route success, NOT an adjacency membership proof. A newly published same-revision route sidecar must be separately evidenced before use.
2. Search retained **local** transport/harness/cache/log artifacts for a same-original route: `artifact.route.json`, `artifact-v3.route.json`, `*.index.json`, `*.pidx*`, `zelph-hf-cache/v2`, `build/receipts/nat_zelph_filtered_route_receipt.json` and `/tmp/zelph-new-p0-evidence`. The source-index `.index.json` maps chunk→byte range; **it does not map arbitrary node IDs→left/right chunks**. Machine-local `.pidx` is a transitive predicate-cache, not a node-to-chunk route index. A route sidecar generated for the 2017 pruned or separately rebucketed v3 artifact cannot be used as original 2026 source membership.
3. If authentic **complete original-node-route membership** is independently evidenced for the SAME original packed image and chunk partition, route each of the five positive QID node IDs to the minimum original left/right chunk set and route each next numeric frontier with that certified index. Preserve source-byte equality on selected relevant original ranges, compare actual native left/right selected-node rows, and prove a **query-scoped one-hop completeness** certificate (not global `984+984` coverage). Agda `ZelphFiniteQueryWordClosureExact.SourceReachableBoundary` already gives the inductive finite-word theorem once real source-reachable step equalities are supplied. The current full-section LR Python runner does NOT YET accept this alternative route certificate: implement as an option only after a real same-source index is produced and audited.
4. If the only source is a v3 rebucketed sidecar, require a separate original source→bucket **semantic adjacency and name multi-fibre refinement** (not just manifest/source file name equality), with precise revision/consumer certificate. Until then continue original source routing only.
5. If no correct complete same-original route exists, use current resumable full original LR byte audit as an expensive fallback, reusing source-equal shard copies. Reuse the NEW original per-chunk Bloom constructor to index each native `AdjPair.node` during this single initial physical pass; query with the existing Bloom reader to prune future native replay candidates. A partial Bloom cover cannot certify global negatives, so do not call it exact sparse routing before 984+984 complete.

**Important distinction:** Positive original-QID evidence already from four `nodeOfName` physical chunks (0,1,4,75) and 4 million native rows is enough to select concrete root IDs; it does NOT certify that the QID has only one name fibre or that a partial adjacency chunk is its entire original neighbour set. To close original A2's *declared finite words*, a same-original complete node-route index plus original-byte/native equality at every reached boundary could be much smaller than full left/right scans, but the index itself needs real coverage evidence.

### Existing cached/live log anchors (not new implementation prerequisites)

- Upstream Zelph PR #30 actually exercised `ctest --test-dir build-hf-cache --output-on-failure -R zelph_tests`: 156/156, focused 3/3 HF-cache policy; tampered/stale ETag manifest correctly refetched; meta-only 111,981 bytes + 31-byte header at cold 2.34s/hot 0.93s; full selected four-section pruned chunk-0 payload 778,058,079 bytes (~742MiB), with 232,194,888-byte left=0 alone. This demonstrates previous manifest caching and source identity guards; it does NOT prove original full-graph node routes.
- Upstream Zelph PR #25 records actual remote HF `chbwa/zelph-sharded` v3 route smoke 5.476s versus 7.948s explicit and ~21s sequential fallback. That route belongs to the v3 PROOF artifact, not the immutable full original `wikidata-20260309-all.bin` absent matching source equivalence.
- ITIR November 14 physical operator route receipt: `docs/planning/nat_zelph_hf_physical_route_execution_20261114.md` (raw local artifact `build/receipts/nat_zelph_filtered_route_receipt.json`); five positive original QIDs but `full_route_materialization_performed=false`, `consumer_verification_performed=false` and `source_support_paid=false`. The last does not mean the underlying shard reads did not happen; the package does not itself grant the stronger authority.
### Source links

- Upstream code/docs: https://github.com/acrion/zelph/blob/main/mkdocs/docs/sharding.md ; https://github.com/acrion/zelph/pull/25 ; https://github.com/acrion/zelph/pull/30
- Existing ITIR March/July logs: `docs/planning/zelph_bin_sharding_note_20260326.md`, `docs/planning/zelph_hf_v3_shard_contract_20260326.md`, `docs/planning/zelph_develop_sparql_partial_load_readiness_20260702.md`, `docs/planning/itir_wd_zelph_sensiblaw_flatness_optimisation_roadmap_20260702.md`
- SLR physical acquisition: https://github.com/chboishabba/slr/pull/28
- DASHI Agda: https://github.com/chboishabba/dashi_agda/pull/822 and https://github.com/chboishabba/dashi_agda/pull/1506


## 15 Nov 2026 — integrated large-bite A2 source HTTP206 / native / 20 distinct words

**Latest local diagnostic by operator:** ITIR #14 at `a3a32d74e1cb7865e9c85437d3bec47e502d2b19` ran 442/448 Python and native Cap'n Proto C++ PASS. Six test errors were all due to the original `tests/test_audit_zelph_native_original_lr_roots.py` fixture using `dest.parent.mkdir(parents=True)` for multiple chunks under one left/right directory. The one-line fix `dest.parent.mkdir(parents=True, exist_ok=True)` was separately verified by the operator as **6/6 PASS** and committed directly to existing PR #14. That does **not** yet establish a new exact-head 448/448 run. SLR 24/24 + 4/4, SensibLaw 25/25 and DASHI 9/9 stay at the operator's independently checked heads.

**New, materially larger code cut committed in the SAME ITIR PR, awaiting operator acceptance:** `tools/run_zelph_original_a2_finite_round_maxcut.py` composes the existing original HTTP206-vs-published full packed `left/right` section validators, authenticated single-object restoration, full original-schema native selected-adjacency scan and declared relation-word closure. It independently pins immutable revision, manifest/index raw SHA, native executable SHA, actual positive QID receipt, and the exact 20-query JSON SHA. Both original `left` and `right` physical comparisons are PRE-FLIGHTED under one **combined** two-sided network cap before any source request; the source-equal shard rematerialiser now also supports `left/right` and uses only remaining one-sided budget. The actual native scan is bounded by original chunk, node, row, neighbour and timeout caps, with one transactionally pinned SQLite scratch DB per exact numeric-node cohort.

**Successive finite graph frontiers are handled without hand editing:** the new A2 runner reads immutable, complete prior native scan receipts; verifies original source/decoder/root identity and SHA256 of the completed native SQLite snapshot; feeds their exact rows to the existing finite-word evaluator; and schedules only the next numeric frontier nodes under the declared count cap. A new node cohort receives its OWN deterministic SQLite filename and immutable complete scan JSON receipt. An incomplete 984+984 source scan NEVER emits a complete source-frontier receipt and NEVER pays absence/negative adjacency. The future run repeats without rewriting past receipts, source SHA or native cache. This is not an Agda theorem, property filter or general graph index.

**Mathematical soundness improvement:** A2's `all_twenty_original_lr_words_closed` now requires 20 distinct `(QID, direction-word)` contracts, not 20 differently labelled repetitions of 4 words. The canonical `docs/planning/zelph_five_qid_lr_query_family.example.json` actually contains 5 QIDs × 4 distinct words = **20 distinct contracts**. New tests cover forged duplicates, first/second native numeric frontier progression, cross-phase aggregate transfer budget, wrong decoder/family SHA, malformed words, corrupted SQLite snapshot and partial 984+984 sections.

### One-command operator plan and bounded live round

```bash
REV=0d4bd670959ebddae72f70d973410fdea8917ec1
MANIFEST_SHA=cedd5cf0e4951ae1aa7c2c5968614b0eb72a4c3b5c8b2dc4ab18c40be8c83f59
INDEX_SHA=89f7ccac888e9e7db09b349cef246e725d969f07d4280142c325e96e12a30d77
META=/tmp/zelph-new-p0-evidence/metadata/wikidata-20260309-all
RUN=/tmp/zelph-new-original-name-evidence
mkdir -p "$RUN"
# Build with `bash tools/build_zelph_native_live.sh "$RUN/native-a2"`
# into a NEW empty directory if the current original-schema decoder is absent.
DECODER="$RUN/native-a2/selected-decoder"
ROOTS="$RUN/five-original-positive-qid-roots.json"
FAMILY=docs/planning/zelph_five_qid_lr_query_family.example.json
DECODER_SHA=$(sha256sum "$DECODER" | awk '{print $1}')
FAMILY_SHA=$(sha256sum "$FAMILY" | awk '{print $1}')
ARGS=(
  --manifest "$META/wikidata-20260309-all.hf-v2.json"
  --original-index "$META/artifact.index.json"
  --dataset-revision "$REV"
  --manifest-sha256 "$MANIFEST_SHA"
  --original-index-sha256 "$INDEX_SHA"
  --decoder "$DECODER" --decoder-sha256 "$DECODER_SHA"
  --positive-roots-receipt "$ROOTS"
  --query-family "$FAMILY" --query-family-sha256 "$FAMILY_SHA"
  --left-receipts-dir "$RUN/left-original-receipts"
  --right-receipts-dir "$RUN/right-original-receipts"
  --shard-root "$RUN/source-equal-shards"
  --native-audit-dir "$RUN/a2-native-numeric-frontiers"
  --max-network-mib 1024 --max-physical-per-section 8
  --max-restore 8 --max-native-chunks 16
  --max-numeric-frontier 64 --max-chunk-mib 256
)
# If prior physical matrix receipts exist, add:
# ARGS+=(--import-physical-receipts-dir "$RUN/positive-name-matrix")
bash tools/check_zelph_physical_maxcut_offline.sh
python3 tools/run_zelph_original_a2_finite_round_maxcut.py "${ARGS[@]}"
python3 tools/run_zelph_original_a2_finite_round_maxcut.py "${ARGS[@]}" --execute
```

The first call is an **offline/zero-network plan**; the second executes a bounded actual original source batch. Repeat the same execute invocation only while acceptable given measured network/disk costs, retaining immutable original HTTP206 receipts and native SQLite cohorts. The final closure flag is permitted only when the source original 984+984 adjacency physical chunks are verified, relevant native full-section scans complete, and **all 20 distinct declared finite LR words** have no unobserved numeric frontier. This never establishes 20 arbitrary property-filtered Wikidata statements, original source P854, global A1 unique QID names, full original .bin SHA, S29 PG persistence, or NORA authority.

**Current material frontier:** all 984+984 production adjacency HTTP206 parity, complete original native selected LR scans and real 20-word closure remain OPEN. The latest newly written A2 coordinator/anti-duplicate tests are not covered by the earlier 442/448 diagnostic nor by the isolated fixture 6/6; a clean new-head exact acceptance is required.


**15 November 2026. SOURCE-WRITTEN; new-head verification required.**

The original P0-S/P1/A1 operator has supplied real physical and native receipts:
ITIR PR #14 exact checked head `f7d1bff7a87c24ed2fd7f9603176efd022c8b1fd`
passed **410/410 Python + original-schema C++ Cap'n Proto**. Four
`nodeOfName` original sections chunks **0,1,4,75** were verified exact
HTTP206-versus-published packed bytes; all four were natively enumerated,
**4,000,000 original name/node rows (1,000,000 per chunk)** were reported
in a local 608 MB SQLite audit scratch DB, and the exact source-native QID
root IDs replayed in those rows:

| QID | original source-native node ID |
|---|---:|
| Q10403939 | 24721153 |
| Q10416948 | 874016 |
| Q10422059 | 63706277 |
| Q10651551 | 2475334 |
| Q56404383 | 741397 |

These are user-operator observations; the raw local SQLite file and its
receipts were not rehashed by this repo documentation write. **Source code
uses SQLite table `native_rows`**, whereas one operator summary called it
`name_node_rows`; check `sqlite_master` if the discrepancy persists.

## Why A2 is separate

The complete original packed `wikidata-20260309-all.bin` is
**87,954,185,510 bytes**, immutable published HF dataset
`acrion/zelph` revision
`0d4bd670959ebddae72f70d973410fdea8917ec1`.
The original header/index declares **984 `left` and 984 `right` packed
adjacency chunks**, plus 204+204 name chunks. A positively decoded QID name
→ node ID does **not** prove which adjacency chunks contain that node.
The existing exact local original source-bin route builder derives chunk
membership only by scanning those sections. A guessed modulo chunk,
fixed-offset shard, or missing row in a partial section is **not evidence of
zero adjacency or completeness**.

The new A2 cut therefore supports resource-bounded full-section verification
and replay. This is a potentially **large transfer**: both the original
HTTP206 ranges and the independently published packed objects are requested
for each new source chunk. Across all 1,968 adjacency chunks, the aggregate
two-sided bytes can be comparable to or greater than downloading the entire
source once. Review dry-run advertised source bytes and disk/network budgets
before electing to execute full-section coverage. Reuse precise original
node→chunk routing if subsequently independently verified to avoid that cost.

## New actual source under ITIR PR #14

- `tools/audit_zelph_hf_original_adjacency_sections.py`:
  original immutable manifest/index geometry; for `left` or `right`,
  exact source-bin HTTP206 vs published-shard byte parity per original chunk,
  receipt import, resume, bounded two-sided byte budget, and optional exact
  saved Cap'n Proto packed copy. A physical section is marked complete ONLY
  when every 984 source chunk has its individual valid original-equality
  receipt. No traversal authority from byte hashes alone.
- `tools/audit_zelph_native_original_lr_roots.py`:
  accepts the actual five positive QID root receipt and physically verified
  original left/right shards. Runs original-schema native C++ selected-node
  decoder on each shard, hashes native output, persists bounded per-chunk
  observations and an exact set of target nodes in a pinned **SQLite scratch
  DB**. A node direction is `complete_one_hop_adjacency=true` only when
  **all original chunks for that direction** are matched and decoded. A
  partial section's empty rows are `UNKNOWN`, never negative. A different
  target set must use a new SQLite file.
- `tools/close_original_http206_lr_finite_words.py`:
  reads complete-source native per-root sweeps, checks the *same*
  dataset/manifest/index/root receipt/decoder and each canonical node
  direction. It executes only the explicitly declared 20 finite words in
  `docs/planning/zelph_five_qid_lr_query_family.example.json`. If a
  two-step word lacks a numeric frontier direction, it emits exact
  `next_numeric_nodes_to_native_scan`, never guesses an end-node result.
  Independent root and later numeric-frontier native scans can then be joined.
  `all_twenty_original_lr_words_closed=true` requires all **20** queries
  to have complete valid source-equal evidence at every step, not merely
  a complete root scan.
- Tests integrated into `bash tools/check_zelph_physical_maxcut_offline.sh`
  include source-byte equality, section/import/resume, actual native
  direction-row validation, source-scope vs incomplete unknown, content drift,
  target-set isolation, first/second layer and exactly-20-word controls.

All newly added code is **UNVERIFIED at its own changed head** until operator
acceptance. No live physical adjacency or 20-word closure receipt is claimed.

## Operator execution — bounded, old source files reused

```bash
# From ITIR PR #14 checkout at its current head:
git rev-parse HEAD
bash tools/check_zelph_physical_maxcut_offline.sh

REV=0d4bd670959ebddae72f70d973410fdea8917ec1
MANIFEST_SHA=cedd5cf0e4951ae1aa7c2c5968614b0eb72a4c3b5c8b2dc4ab18c40be8c83f59
INDEX_SHA=89f7ccac888e9e7db09b349cef246e725d969f07d4280142c325e96e12a30d77
META=/tmp/zelph-new-p0-evidence/metadata/wikidata-20260309-all
MANIFEST="$META/wikidata-20260309-all.hf-v2.json"
INDEX="$META/artifact.index.json"
RUN=/tmp/zelph-new-original-name-evidence
SHARDS="$RUN/source-equal-shards"
ROOTS="$RUN/five-original-positive-qid-roots.json"
# Freshly compile the original-schema decoder from THIS exact A2 head:
# previous native-a1 executable predates duplicate-node union semantics.
bash tools/build_zelph_native_live.sh "$RUN/native-a2"
DECODER="$RUN/native-a2/selected-decoder"
LEFT="$RUN/left-original-receipts"
RIGHT="$RUN/right-original-receipts"
FAMILY=docs/planning/zelph_five_qid_lr_query_family.example.json

# Bind every A2 source/native receipt to this newly compiled decoder.
sha256sum "$DECODER" "$ROOTS"
```

### A2-P first: dry-run original left/right physical budgets

```bash
for SIDE in left right; do
  python3 tools/audit_zelph_hf_original_adjacency_sections.py \
    --manifest "$MANIFEST" --original-index "$INDEX" \
    --dataset-revision "$REV" --manifest-sha256 "$MANIFEST_SHA" \
    --original-index-sha256 "$INDEX_SHA" \
    --section "$SIDE" --receipts-dir "$RUN/$SIDE-original-receipts" \
    --save-published-root "$SHARDS" \
    --max-new-chunks 8 --max-transfer-mib 1024 --max-chunk-mib 256
done
```

The dry-run shows exactly which immutable source chunks would be
streamed, their aggregate two-sided byte budget, and what remains OPEN.
The default is **no network**, and no fake adjacency receipt.

### A2-P next: opt-in one bounded real HTTP206 batch per direction

```bash
for SIDE in left right; do
  python3 tools/audit_zelph_hf_original_adjacency_sections.py \
    --manifest "$MANIFEST" --original-index "$INDEX" \
    --dataset-revision "$REV" --manifest-sha256 "$MANIFEST_SHA" \
    --original-index-sha256 "$INDEX_SHA" \
    --section "$SIDE" --receipts-dir "$RUN/$SIDE-original-receipts" \
    --save-published-root "$SHARDS" \
    --max-new-chunks 8 --max-transfer-mib 1024 --max-chunk-mib 256 \
    --execute
done
```

Re-running is incremental: previously receipted chunks are audited and
not re-requested, unless the current saved file does not match its
previous source hash (fail closed). To close full section coverage,
repeat only with sufficient explicit total network/storage budget and
retain completed per-chunk receipts. Do not infer full A2 from this first
bounded batch.

### A2-N first native selected-QID observation sweep

```bash
python3 tools/audit_zelph_native_original_lr_roots.py \
  --manifest "$MANIFEST" --original-index "$INDEX" \
  --dataset-revision "$REV" --manifest-sha256 "$MANIFEST_SHA" \
  --original-index-sha256 "$INDEX_SHA" \
  --physical-receipts-dir "$LEFT" --physical-receipts-dir "$RIGHT" \
  --shard-root "$SHARDS" --positive-roots-receipt "$ROOTS" \
  --decoder "$DECODER" \
  --sqlite-index "$RUN/a2-original-five-root-scan.sqlite" \
  --max-new-chunks 8 --max-neighbors 200000 \
  --max-stdout-mib 64 --timeout-seconds 900 --execute \
  --output "$RUN/a2-original-five-root-batch01.json"
```

Use a **new output filename** on each run and the **same SQLite index**:
completed native shard observations are reused; a changed decoder,
dataset, QID set or original physical digest is rejected. Until all
`984+984` original adjacency source chunks are physically verified
and natively scanned, no selected-root direction is marked complete.

### A2-F finite query closure, once root source sweep is complete

After root sweep completion, save its receipt as a NEW output, e.g.
`$RUN/a2-five-roots-source-complete.json`. Then:

```bash
python3 tools/close_original_http206_lr_finite_words.py \
  --query-family "$FAMILY" \
  --native-audit "$RUN/a2-five-roots-source-complete.json" \
  --output "$RUN/a2-20-words-first-pass.json"
# Exit 3 is EXPECTED while second-hop numeric boundaries remain unobserved.
```

The JSON emits `next_numeric_nodes_to_native_scan`. For bounded
frontier batches of at most **251 additional IDs** (the five QID roots
are automatically included in every scan), create a **NEW SQLite file
per target set**, adding a separate `--extra-node N` for each requested
node, then run the original native source scan over retained packed
sections again. Its same-source complete receipt can be passed as an
additional `--native-audit` argument to the finite query closure tool.
Repeat until the JSON has no missing source numeric boundaries, or
report the explicit budget/source blocker. The result is accepted only
for the 20 declared finite words, not all possible graphs/queries.

**No full-source route can be claimed with only selected adjacency shards
unless an independent source-original node→chunk index establishes
coverage for EVERY queried node direction.** Treat the huge full-section
path as a correct but expensive fallback; a verified sparse routing
index is a separate optimization/evidence gate.

## Gate table

| Gate | Exact next acceptance | Current |
|---|---|---|
| P0-S name | direct HTTP206 equality chunks 0/1/4/75 | Operator PASS (selected only) |
| P1 name | five exact source-native QIDs and 4M native rows | Operator PASS (selected only) |
| A1 name | all 204+204 physical+native chunks and collision-fibre inverse + Agda decoder weld | OPEN |
| A2-P | actual original HTTP206 bytes == published `left/right` shards | OPEN; executor committed |
| A2-N | all chunk directions natively scanned for selected numeric nodes | OPEN; executor committed |
| A2-F | all 20 finite query words closed with complete intermediate frontiers | OPEN; evaluator committed |
| P4/P5 | Wikibase original GUID/P14143/P854 source, S29 real PG review/reopen, NORA | OPEN |

Run with the same physically pinned source, not newly discovered
unrelated "latest" revisions. Failed/partially observed runs do not
confer graph negatives, source authority or editing rights.
