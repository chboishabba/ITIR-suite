# Zelph original A2-B maximum cut: authentic Bloom candidate routing without a full original .bin

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
