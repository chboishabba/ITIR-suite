# Zelph original A2-B maximum cut: authentic Bloom candidate routing without a full original .bin

## Five-shard physical batch and first positive source edge — 15 November 2026

**Current operator-reported actual evidence is FIVE original-equal adjacency shards (L:5,7; R:1,2,983), not the older three.** The operator retained `/tmp/zelph-new-original-name-evidence/a2b-build-batch01.json`, `a2b-build-batch02.json`, `a2b-five-roots-source-route-partial-5shards.json`, `a2b-original-five-root-batch02.json`, and the source-native scratch SQLite. Raw local files have not been independently re-read from this remote GitHub documentation update.

| Direction/chunk | Original-shard byte length | Reported HTTP206 original-equal SHA256 | Native Bloom wire SHA256 when fully supplied |
|---|---:|---|---|
| `left:5` | 62,972,326 | `d4ae3f77c9b6a48d3380ceeb8499d26783dc8db3d85b21949ff0cb1b9431df95` | consult batch01 raw receipt |
| `left:7` | 56,979,303 | `a1fa1b06150d9aec84381337aa252222b477838e7aa28a28c4c8c57635e146b7` | `46e0112cfb86bbf9c2745fad0c6bf56a86a31b693d07f58df054dd5d62a5cd96` |
| `right:1` | 34,976,558 | `58a1ee68b69da3fb8d2038741aa2a944208a0005a7fa8331fa55e8c14d9b626d` **(disputed by subsequent table)** | consult batch01 raw receipt |
| `right:2` | 45,807,066 | `12ca8cd3bbdf9eb5f343d04612638542922d631eadf2432157b1622dcd60d10d` | `4873d586261f337d622a839072a3ab7aff424da2055861a4bcf43be1252ad75e` |
| `right:983` | 29,849,869 | `6e0b7596ff503ee82424b94f6f3630f9d9e79e605d33682ef1764ebc3b6dcf88` **(disputed by subsequent table)** | consult batch01 raw receipt |

**Totals from operator’s bounded source run:** 230,585,122 physical original-equal adjacency bytes, **5/1968 chunks** indexed, **4,424,620 native source key rows**, and **10,485,920 Bloom wire bytes** (5 × 2,097,184, including headers/footers; an earlier operator table stated 10,485,760, which is exactly five bitmaps *without* the 32-byte wire overhead each). All 1,963 remaining source chunks are UNKNOWN.

**Per-chunk discrepancy requiring original receipt adjudication:** A previous ledger reported `right:1` 741,648 rows and SHA `58a1...`; `right:983` 682,972 rows and SHA `6e0...`. The later five-shard table instead says `right:1` 1,000,000 rows and SHA beginning `4d14...`; `right:983` 424,620 rows and SHA beginning `999b...`. Both pairings sum to 1,424,620 rows. They **cannot both certify the same per-chunk original byte identity**. Do not overwrite the full digests above from abbreviated later values or assert the conflict resolved by a matching aggregate. The operator must inspect the actual `right-000001.json`/`right-000983.json` physical receipts and native Bloom receipts and rehash the retained packed files before signing an unambiguous canonical per-chunk evidence ledger.

**First original-native positive replay:** Bloom query finds node `741397` (`Q56404383`) possible in `right:2`. Direct original-schema selected-native `--node 741397` on that original-equal shard returns `values_seen=7`, `truncated=false`, and **7 sorted unique neighbours**:

```json
[4750078302585009999, 5722258421574666509,
 7048854505916013243, 8266125300765673293,
 8422695159416374426, 8884238291781291067,
 9111393206167045379]
```

This is a **chunk-scoped source-positive adjacency witness** only. Do not promote it to complete `right` adjacency of node 741397: the current partial route records 981 unverified right chunks, and the left direction has 982 unknown chunks. The five-root partial route must continue reporting `all_original_adjacency_blooms_completed=false`.

### New logical certificate bridge — source-written, exact-head acceptance OPEN

Implemented in this same ITIR PR #14:

- `tools/certify_zelph_original_finite_word_boundary.py`: re-runs the existing `original_http206_finite_words` evaluator against exact raw audit JSON digests and independently rechecks each **source-reachable** frontier step; emits per-node/direction source receipt dependencies, multiplicity counters, the next frontier, and explicit missing boundaries. It rejects a changed finite result, source identity drift through the upstream evaluator, contradictory multiplicity over repeated exact rows, and forged/relabelled completion.
- `tests/test_certify_zelph_original_finite_word_boundary.py`: adversarial partial-positive, two-step induction, tampered trace/certificate, multiplicity conflict and mixed-source regression tests.
- `tools/check_zelph_physical_maxcut_offline.sh` includes the new test. **Only local syntax compilation and an isolated stubbed smoke test were performed during the source-write; a new exact-branch full pytest+native check is still required.** The earlier **506/506** and **10/10 Agda** acceptance receipts remain bound to their earlier exact tested heads, not the new code commit.

Illustrative issuance, **only once actual complete source native audit receipts are available**:

```bash
python3 tools/close_original_http206_lr_finite_words.py \
  --query-family docs/planning/zelph_five_qid_lr_query_family.example.json \
  --native-audit /path/to/complete-exact-audit.json \
  --output /tmp/original-20-finite-words.json

python3 tools/certify_zelph_original_finite_word_boundary.py \
  --query-family docs/planning/zelph_five_qid_lr_query_family.example.json \
  --native-audit /path/to/complete-exact-audit.json \
  --finite-result /tmp/original-20-finite-words.json \
  --output /tmp/source-reachable-boundary-certificate.json
# Recheck a previously emitted certificate with the same raw inputs:
python3 tools/certify_zelph_original_finite_word_boundary.py \
  --query-family docs/planning/zelph_five_qid_lr_query_family.example.json \
  --native-audit /path/to/complete-exact-audit.json \
  --finite-result /tmp/original-20-finite-words.json \
  --certificate /tmp/source-reachable-boundary-certificate.json
```

These commands are a **conditional step-certificate projection**, not a universal source-verification oracle. The certificate does not discharge concrete original HTTP206 byte verification, arbitrary C++ semantics, `OriginalRow ↔ NativeRow` in Agda, the construction of an Agda `SourceReachableBoundary` proof term, full first-link Wikipedia equivalence, P854 source support, S29 durability or NORA authority. The source-logical and physical evidence layers stay separate until independently replayed and stitched by the actual external witness contract.

**Next coordinated cut:** physically index the remaining 1,963 chunks (or find complete independent same-original routing), while replay-testing the new boundary certificate and mapping its per-step dependencies into SLR S29 without treating incomplete local positives as scoped global negatives. A second-operator exact-head local test remains required for new source.

---


## A2-B1 physical-filter evidence crosswalk — three original shards DONE, full A2-B2 still OPEN

**Additional already-produced local operator receipts, recovered from the contemporaneous A2-B execution rather than re-executed by this documentation commit.** The previous A2-B0 acceptance block immediately below mentions generating the first three Bloom files as a next step; this paragraph **supersedes that particular stale instruction.**

Native A2-B decoder: `/tmp/zelph-new-original-name-evidence/native-a2b/selected-decoder`, SHA-256 `debaca4bd4fe08a16c446e65751fe999a0f8d82e49dce2a5f3619b452678eef7`. Actual retained operator build receipt: `/tmp/zelph-new-original-name-evidence/a2b-build-batch01.json`.

| Directional original chunk | Bloom wire bytes | Actual native source key rows | Physical original-equal source chunk SHA-256 |
|---|---:|---:|---|
| `left:5` | 2,097,184 | 1,000,000 | `d4ae3f77c9b6a48d3380ceeb8499d26783dc8db3d85b21949ff0cb1b9431df95` |
| `right:1` | 2,097,184 | 741,648 | `58a1ee68b69da3fb8d2038741aa2a944208a0005a7fa8331fa55e8c14d9b626d` |
| `right:983` | 2,097,184 | 682,972 | `6e0b7596ff503ee82424b94f6f3630f9d9e79e605d33682ef1764ebc3b6dcf88` |

**Aggregate: 3 physical source-bound Bloom filters, 6,291,552 output bytes, 2,424,620 actual native key rows.** The five original-positive QID roots `Q10403939`, `Q10416948`, `Q10422059`, `Q10651551`, `Q56404383` produced empty **candidate chunk index lists among those three verified filter chunks only**. The query receipt correctly reported `all_original_adjacency_blooms_completed=false`. It does **not** assert no original neighbours, no source row in the remaining chunks, or full 20-word closure.

This establishes **A2-B1's three-chunk live pilot** with actual native filter files and evidence, not just synthetic ABI roundtrip. The next high-alpha physical gate is **A2-B2: verify/index the other 1,965 original left/right chunks (or authenticate a complete alternative same-original source route certificate)**; then A2-B3 selects and natively decodes Bloom-positive frontier chunks to instantiate the conditional Agda theorem. A2-B0 and pilot B1 do not waive the global coverage or decoder/refinement premises.

The individual per-filter Bloom digests were supplied only in abbreviated form in the contemporaneous operator summary; do not invent full digests in repository documentation. The receipt path above is local operator evidence, not a versioned file committed in this repository. Independently rerunning the physical gate requires access to those retained local files and source receipt bytes.

---


## Operator exact-head acceptance — A2-B0 CLOSED (15 November 2026)

**Newly reported clean-worktree acceptance, recorded as operator evidence, not independently reproduced by this documentation commit:**

- **ITIR PR #14:** exact checked commit `d858c01477932460897f46540e5a05ab734b0084`, `bash tools/check_zelph_physical_maxcut_offline.sh` **exit 0**, **506/506 Python tests across 36 modules PASS**, **native C++ Cap'n Proto fixture/selected decoder/filtered route/header probe roundtrip PASS**, including the real native Bloom binary ABI, duplicate-key union and name-fibre fail-closed tests. This closes the previous post-fix *offline code/test* acceptance requirement.
- **Golden DASHI Agda PR #1506:** merged exact commit `2f18e7efa03a2d6be9b73614fbf7d047bc2d1aaf`, `scripts/check_zelph_trie_hyperfabric_maxcut.sh` **exit 0**, **10/10 Agda 2.9.0 targets PASS** in the operator's clean worktree, including `DASHI/Interop/ZelphOriginalBloomPrunedSourceRouteExact.agda`. This closes the *kernel-check* component of A2-B0; the theorem remains conditional on actual physical source coverage and native decoder adequacy.
- **SLR PR #10:** reported checked `e11d0d9`, **24/24 Rust + 4/4 S29 Python PASS**, with **one live PostgreSQL test skipped**: this does *not* close real persisted/restarted database acceptance.
- **SensibLaw PR #514:** reported checked `345b6f12`, **25/25 Python review handoff tests PASS**. This is not an original NORA export or external review decision.

**Source/physics ledger untouched:** published full .bin reported size 87,954,185,510 bytes and 25-byte original header SHA `2599c689cd2da7dfaeeacab5dc4f68003d3e8e02ec854313e5f083d5c3fd2998`; original-equal `nodeOfName:0` and `nodeOfName:1` source bytes additionally reported (45.47 MiB total). Prior receipts support original-equal `nodeOfName:4,75` and original-equal adjacency `left:5`, `right:1,983`, **but no full name/adjacency source partition**. Do not confuse the original header's four section *chunk counts* with 1,968 physically decoded adjacency chunks.

**Current gate state:** A2-B0 **CLOSED** for reproducible code/test and conditional Agda source-kernel acceptance. A2-B1/B2/B3 and complete A1 remain **OPEN**. In particular, three source-equal adjacency chunks do not yet prove native Bloom key filters were physically generated; no 984+984 negative coverage or 20-word physical closure follows from offline tests.

**Next A2-B1 cut:** using retained operator original-equal `left:5`, `right:1`, `right:983` and the new-head native decoder, execute the *existing* generator and query commands below. Report a source-bound artifact per chunk with source length, exact original HTTP206 SHA, source-equal packed SHA, decoder SHA, key row count, Bloom wire SHA, end-of-message check and explicit original section coverage counters. Expect **3/1968** or less; absence in uninspected chunks remains unknown. Then resume A2-B2's full-section coverage (or independently proved same-original node-route certificate), followed by candidate replay and the finite 20-word frontier induction.

**Acceptance provenance:** the Agda and ITIR successful exit codes were supplied by the local operator; the committed documentation update does not independently replay the local Nix/compiler environment or retrieve the /tmp physical receipts. Earlier “new head unverified” warnings below are historical and superseded only for the two exact heads named here.

---


## 15 November follow-up — exact source patch, acceptance still separated

**Live ITIR PR #14 head before this documentation update:** `bb69f6556503798bf704cd68a713d4114ffedbb4`. The reported operator clean-worktree baseline `2f407629417ad7dfd63d4c04c85309812831ba7d` had 505/506 Python checks passing; a locally tested one-line assertion correction brought that to 506/506, and a separate local native C++ Cap'n Proto roundtrip passed after restoring inherited Python import paths. Those local corrected runs are **not** independent exact-head checks of the new committed files.

Two changes now committed on the **same** ITIR branch:

1. `4e41a5065f3405e16994a84f2a6501e0fb801e75` — Bloom replay test accepts the earlier fail-closed physical/source mismatch as well as the downstream unverified-Bloom refusal. It must continue to **reject** altered candidate routes.
2. `bb69f6556503798bf704cd68a713d4114ffedbb4` — the native original-schema Bloom roundtrip invokes Python with `PYTHONPATH="tools:itir-mcp/src:${PYTHONPATH:-}"`, preserving any caller-provided `re_gpt` or other import locations.

**Next exact-head commands, against the checked-out current branch (not an uncommitted test overlay):**

```bash
git rev-parse HEAD
git status --porcelain --untracked-files=no
bash tools/check_zelph_physical_maxcut_offline.sh
```

**Golden alignment:** DASHI Agda PR #1506 is now **merged** (15 November 2026). Its last publicly inspected Zelph runner enumerates **10** Agda targets, including `DASHI/Interop/ZelphOriginalBloomPrunedSourceRouteExact.agda`. Earlier 9/9 local operator acceptance applies to the earlier mathematical spine, **not** a separately witnessed 10/10 kernel run. Run `bash scripts/check_zelph_trie_hyperfabric_maxcut.sh` at the exact merged Agda tree before marking A2-B0 wholly accepted.

**Physical/semantic gate ledger (do not promote source-written or synthetic fixtures):**

| Gate | Supported current receipt | Exact unresolved obligation |
|---|---|---|
| ITIR A2-B0 offline | Reported local 506/506 corrected overlay plus native C++ pass; both corrections now committed | Clean source-head Python + C++ acceptance, with pinned HEAD and exit zero |
| Agda A2-B0 golden | Earlier 9/9 locally accepted; tenth Bloom-specific module source-written and merged | Exact-head pinned 10/10 kernel validation and concrete decoder/refinement assumptions |
| A2-B1 first filters | `left:5`, `right:1`, `right:983` HTTP206-vs-published matching bytes reported (127,798,753 bytes) | Build and validate actual native Bloom files and hash-bound receipts for these three retained original-equal chunks |
| A2-B2 source completeness | 3 original adjacency chunks physically checked out of 984+984 | Verify the other **1,965** chunks or provide an independently authenticated complete same-original node-key route index; do not infer from unsorted chunk ordinal |
| A2-B3 twenty words | Five original-positive QID roots and the 20 distinct finite QID/relation-word declarations | Bloom-complete native candidate replay for every *reachable node/direction*, then instantiate `SourceReachableBoundary` and close all twenty results |
| A1 / native evidence / S29 / NORA | Original source-backed `nodeOfName` chunks 0/1/4/75, four million row observations; separate offline S29/NORA tests | Full source name-fibre/inverse evidence, source primary P854 semantics, real PG restart/readback, actual NORA export and scoped reviewer acceptance |

**Critical negative boundary:** A native Bloom-negative is an exact chunk exclusion **only** after original HTTP206 byte equality, full native key enumeration, exact packed EOF and hash-ABI agreement are independently checked. With 3/1968 filters, no absence claim about an entire original adjacency direction is justified. A positive Bloom result never proves a graph edge until the candidate chunk is decoded. The existing 2017/v3 route sidecars cannot substitute for this pinned 2026 source.

The next physical operator step reuses the already retained three original-equal packed files (no new large download), compiles the current `--adjacency-bloom` decoder, executes the three-filter generator and five-root query commands below, and stores per-filter exact SHA/row counts; then resume remaining chunk acquisition by bounded source-equal HTTP206 ranges. Do not claim 20-word closure from three partial filters.

---


**15 November 2026. Source-written in existing ITIR PR #14, not yet accepted at changed head.**

## New high-alpha producer finding

The real [upstream Zelph serialization](https://github.com/acrion/zelph/blob/2ebe7d4e1d428d34f02a2565cf4f138b050ee71d/src/lib/network/zelph_persistence.cpp)
writes original `left/right` sections by iterating `_left.begin()` and
`_right.begin()` in fixed entry-count chunks. The underlying type is
[an unordered segmented map](https://github.com/acrion/zelph/blob/2ebe7d4e1d428d34f02a2565cf4f138b050ee71d/src/lib/network/network.hpp)
(`ankerl::unordered_dense::segmented_map<Node,adjacency_set>`).
The original [Cap'n Proto schema](https://github.com/acrion/zelph/blob/2ebe7d4e1d428d34f02a2565cf4f138b050ee71d/src/lib/io/zelph.capnp)
records each `AdjPair.node`, but it has NO numeric min/max range or
node→chunk key in the chunk header. Hence numeric modulo, sorted node-range
or ordinal `node_id → chunk_index` inference is unjustified.

The original full `wikidata-20260309-all.bin` is 87,954,185,510
bytes at dataset revision
`0d4bd670959ebddae72f70d973410fdea8917ec1`. Physically accepted
operator P0-S original name chunks 0,1,4,75 contain 4,000,000
native source-name rows, and five QID positive native roots replay.
New A2-P independent original HTTP206 equality receipts (all from the
**same source revision**):

| Exact original chunk | Source packed bytes | Original/published SHA256 |
|---|---:|---|
| `left:5` | 62,972,326 | `d4ae3f77c9b6a48d3380ceeb8499d26783dc8db3d85b21949ff0cb1b9431df95` |
| `right:1` | 34,976,558 | `58a1ee68b69da3fb8d2038741aa2a944208a0005a7fa8331fa55e8c14d9b626d` |
| `right:983` | 29,849,869 | `6e0b7596ff503ee82424b94f6f3630f9d9e79e605d33682ef1764ebc3b6dcf88` |

**127,798,753 original selected adjacency bytes**, 3/1968 directional
chunks; A2-N operator's selected root scan correctly returned
`unknown_outside_scanned_source_chunks=true`. No original adjacency
complete direction or 20-word closure is yet accepted. DASHI #1505
15/15 Agda 2.8.0.2 and 57/57 Python checks were accepted by the
operator, but do not pay A2 source bytes.

## Exact new architecture: one original full scan, many sparse frontier lookups

```text
Pinned original .bin HTTP206 === immutable published packed Capnp shard
                 |    (each chunk once; P0-S / A2-P)
                 v
Actual upstream Capnp decoder --adjacency-bloom
   every AdjPair.node -> deterministic source key filter
   exact packed EOF -> emit binary Bloom (2 MiB/chunk)
                 |
   physical original SHA + native decoder SHA
   + binary filter SHA + original chunk identity
                 v
   A2-B: local compact filters (about 3.9 GiB for 1968 chunks)
                 |
        selected QID/numeric frontier node ids
                 |
     +-----------+-----------+
     |                       |
 source chunk Bloom      Bloom candidate
 says absent             key may be present
     |                       |
 exact exclusion         actual original-schema
 ONLY that chunk         Capnp selected native replay
     |                       |
     +-----------+-----------+
                 |
 all 984+984 original chunks Bloom-indexed?
       NO -> UNKNOWN missing source boundaries
       YES -> exact complete original selected one-hop
                 |
     finite 20 original left/right relation words
       (missing frontier nodes => separate native replay batch)
```

A per-chunk Bloom is **not** a proof of adjacency existence. Its **negative**
is exact ONLY for a chunk whose source bytes matched original HTTP206 and
whose complete original native keys passed exact Capnp EOF. A positive may
be a false positive, so no edge exists without native replay. Even if every
**observed** filter says absent, missing original chunks remain unknown
until whole-section coverage exists. No global unique QID name fibre is
claimed from selected five source-positive QIDs.

The native executable uses the fixed `ZLBLOOM1` ABI: 16-byte header,
2^21 byte bitmap, 16-byte `ZLBEND01` EOF/row-count footer. Exactly
7 deterministic splitmix64 double-hash probes per source `uint64` node
key. C++ emits the Bloom **only after** the same actual packed-message
reader proves one complete message with zero trailing bytes. The Python
indexer verifies binary length, chunk/direction, hash parameters,
native row count, original HTTP206 receipt SHA, saved packed SHA, decoder
SHA and immutable original manifest/index.

The original `AdjChunk` writer's unordered map means these filters are
an **alternative explicit key-coverage index**: they do not rely on numeric
ordering. All 1,968 chunks still need an initial source-byte check and
native membership extraction. This is a **rescan optimization**, not
an invented shortcut to avoid full source coverage.

## Source delivered / ownership

| Owner | Exact source | Acceptance |
|---|---|---|
| ITIR original Capnp | `tools/zelph_selected_packed_shard_decoder.cpp` | New native `--adjacency-bloom`; no selector, complete original packed EOF |
| ITIR original per-chunk witness | `tools/build_zelph_original_lr_bloom.py` | Native binary filter + original source HTTP206/packed/decoder digest; resumable |
| ITIR exact key routing | `tools/query_zelph_original_lr_blooms.py` | Per requested node `possible_native_source_chunk_indices`, exclusions and missing chunks |
| ITIR candidate replay | `tools/replay_zelph_original_lr_bloom_candidates.py` | Complete original Bloom source required before selected native replay can close exact one-hop |
| ITIR finite query | `tools/close_original_http206_lr_finite_words.py` | Accepts full-source native adjacency sweep OR complete original Bloom + all candidate native replays |
| DASHI/Agda | [Zelph trie/hyperfabric/Nat/NORA golden maxcut](https://github.com/chboishabba/dashi_agda/blob/agent/nora-perspective-consumer-maxcut-20261114/Docs/ZelphTrieHyperfabricNatNoraMaximumCut20261114.md) | Decoder-model soundness, full name fibres, A2 logical/finite closure theorem remain separate |
| SLR S29 / SensibLaw NORA | downstream handoffs | Persistent review, primary P854 and export authority still OPEN |

## Operator commands — THREE existing physical adjacency chunks, no fresh HTTP206

```bash
# Checkout current ITIR PR #14 exact head and run all Python + real C++:
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
LEFT="$RUN/left-original-receipts"
RIGHT="$RUN/right-original-receipts"
BLOOMS="$RUN/native-original-lr-blooms"

# A2-B requires new native executable; old native-a2 hash is obsolete
# because it predates the --adjacency-bloom source ABI.
bash tools/build_zelph_native_live.sh "$RUN/native-a2b"
DECODER="$RUN/native-a2b/selected-decoder"
DECODER_SHA="$(sha256sum "$DECODER" | cut -d' ' -f1)"
```

New native membership filters for already matched `left:5`,
`right:1`, `right:983`:

```bash
python3 tools/build_zelph_original_lr_bloom.py \
  --manifest "$MANIFEST" --original-index "$INDEX" \
  --dataset-revision "$REV" --manifest-sha256 "$MANIFEST_SHA" \
  --original-index-sha256 "$INDEX_SHA" \
  --physical-receipts-dir "$LEFT" --physical-receipts-dir "$RIGHT" \
  --shard-root "$SHARDS" --positive-roots-receipt "$ROOTS" \
  --decoder "$DECODER" --bloom-root "$BLOOMS" \
  --max-new-chunks 3 --max-key-rows 2000000 --execute \
  --output "$RUN/a2b-first-three-source-chunk-blooms.json"
```

This does NOT fetch original HTTP206 again. The source-equal packed
bytes must still be locally available at `$SHARDS`, with matching
physical receipts. Expect three fixed-size binary filters (about
6.0 MiB total) and three JSON receipts, provided the native decoder
and source evidence pass. Actual counts/hashes remain unknown until
execution.

Query all five original-positive QID node IDs without any new HTTP
transfer, with every other shard explicitly UNKNOWN:

```bash
python3 tools/query_zelph_original_lr_blooms.py \
  --manifest "$MANIFEST" --original-index "$INDEX" \
  --dataset-revision "$REV" --manifest-sha256 "$MANIFEST_SHA" \
  --original-index-sha256 "$INDEX_SHA" \
  --physical-receipts-dir "$LEFT" --physical-receipts-dir "$RIGHT" \
  --positive-roots-receipt "$ROOTS" \
  --decoder-sha256 "$DECODER_SHA" \
  --bloom-root "$BLOOMS" \
  --output "$RUN/a2b-five-roots-source-route-partial.json"
```

With three filters, `all_original_adjacency_blooms_completed` MUST
be `false`; `complete_original_bloom_section_cover` MUST be false for
both directions. `possible_native_source_chunk_indices` indicate
**possible** node membership within 3 individually verified chunks
only; all absent filter chunks are UNKNOWN. If the new indexer or
native binary differs from actual source, fail closed and report
the exact mismatch.

## After full original section coverage, sparse numerical frontier scans

1. Continue the resource-bounded
   `audit_zelph_hf_original_adjacency_sections.py` per direction
   until all 984+984 source chunks have physical HTTP206 equality.
   Build A2-B filters for the new verified packed chunks in batches.
   Keep filters and physical receipts permanently; the much larger
   locally cached packed shards can be removed *after* verifying these
   proofs, if disk budget requires.
2. Rerun `query_zelph_original_lr_blooms.py` with the same pins.
   **Only if 984+984 filters exist** is a Bloom-negative a
   whole-source original direction exclusion.
3. Run `replay_zelph_original_lr_bloom_candidates.py`
   in dry-run, then with `--execute --hydrate` under explicit
   `--max-hydrate-mib`. It rehydrates missing **candidate only**
   source-equal standalone shards from immutable HF, hashes to
   their earlier exact original HTTP206 bytes, then uses actual
   original Capnp selected `--node` decoder. The returned exact
   one-hop witness uses version
   `itir.zelph.original_lr_bloom_pruned_exact_native_onehop.v1`.
4. Feed root and subsequently frontier replay receipts into the
   existing `close_original_http206_lr_finite_words.py`
   `--native-audit <receipt>` arguments. It accepts only same
   original dataset, manifest, original index, positive-QID receipt
   and native decoder. Any missed candidate or duplicate
   QID/relation-word contract is rejected. The 20-word ledger
   closes only after all actual numeric frontier directions are
   native-resolved. If a source portion remains uncovered, the
   evaluator returns exact missing boundaries or blocks rather than
   fabricate absence.

**Example dry-run candidate replay after full original Bloom cover**:

```bash
python3 tools/replay_zelph_original_lr_bloom_candidates.py \
  --manifest "$MANIFEST" --original-index "$INDEX" \
  --dataset-revision "$REV" --manifest-sha256 "$MANIFEST_SHA" \
  --original-index-sha256 "$INDEX_SHA" \
  --physical-receipts-dir "$LEFT" --physical-receipts-dir "$RIGHT" \
  --positive-roots-receipt "$ROOTS" --bloom-root "$BLOOMS" \
  --decoder "$DECODER" --shard-root "$SHARDS" \
  --max-hydrate-mib 512
# If within the operator budget, add --execute --hydrate and --output
# with an unused new receipt path. This only works after all filters exist.
```

This is **not** a new GitHub PR, new route oracle, external index service
or PostgreSQL S29 implementation. The saved index is local digest-bound
original source evidence and can be replayed by the original native
decoder. The physical initial scan cost cannot be removed by this technique:
the benefit is exact candidate routing and avoidance of repeatedly scanning
the entire original graph for each finite-query frontier.

## Exact stage status (as of this source commit)

| Gate | Status |
|---|---|
| P0-S selected original name 0,1,4,75 | Operator PASS |
| P1 five native QID root positives | Operator PASS |
| A1 4M original native rows for 4/204 chunks | Operator PASS; full A1 OPEN |
| A2-P original `left:5`, `right:1`, `right:983` physical bytes | Operator PASS; full 984+984 OPEN |
| A2-N selected-root scan over these 3 shards | Operator PASS; incomplete directions UNKNOWN |
| A2-B indexed source key filters (new code) | SOURCE WRITTEN; local native/test acceptance OPEN |
| A2-N(Bloom) exact candidate-only native one-hop (new code) | SOURCE WRITTEN; full-Bloom source prerequisite OPEN |
| A2-F all 20 original finite words | OPEN |
| Source P854 / real S29/Postgres reopen / NORA | OPEN |
