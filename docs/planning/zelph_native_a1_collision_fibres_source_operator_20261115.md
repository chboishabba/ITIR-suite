# Zelph A1 — original source-byte equality → full native name-row/duplicate fibre audit

**15 November 2026 — ITIR PR #14.** This is an executable operator handoff. No real
run of these NEW A1 files has yet been reported. The previous source heads and
receipts remain immutable evidence, but are not acceptance for the new code.

## Confirmed prerequisites (operator receipts, not freshly fetched in this document)

At immutable HF dataset revision
`0d4bd670959ebddae72f70d973410fdea8917ec1`:

- ITIR #14 `adba4f0dbc385cdcd8f23601eaa6a6b9be6c7c98` had **347/347 Python
  tests and original-schema native C++ PASS**.
- Verified `nodeOfName` chunks **0, 1, 4, 75**: chunk 0 SHA
  `0bbfc205a26caeb8a0daf5e1b265cc10a0895d43e5c7828c0c4ad8109efc8508`;
  chunk 1 `26176322617b93c4233d4c7c5fba67381fc53f133dfa3dae8f74df49ac07c6af`;
  chunk 4 `b5329bacb0d1150f60b1b782a22ef9885820b584cf7a3dfa2ff846da54435377`;
  chunk 75 `b60b21862463ef7abe17760f15cb3dca9ead1288f61171ca7bf36817adced1a3`.
  Physical bytes are equal to published pinned original HTTP206 ranges, not
  to an independently SHA-audited whole .bin.
- All 5 QID roots were **positive original-schema decoded native rows**:
  `Q10403939 → 24721153`, `Q10416948 → 874016`,
  `Q10422059 → 63706277`, `Q10651551 → 2475334`,
  `Q56404383 → 741397`. None of this proves all-name completeness.

There are **204** `nodeOfName` and **204** `nameOfNode` original name
chunks, according to the already audited original 25-byte header/index geometry.
Selected-byte equality ≠ exhaustive native row decoding ≠ formal Agda A1 weld.

## New source: three complementary evidence layers

1. `tools/audit_zelph_native_name_rows.py` (pre-existing concurrent source):
   one original physical receipt + exact packed shard + pinned C++ decoder ->
   complete NDJSON per-chunk row stream and terminal EOF/count receipt, retaining
   duplicate names without forcing a single-node map.
2. `tools/audit_zelph_native_name_section.py` (pre-existing concurrent source):
   joins all physical, native-row and original saved row-stream receipts for a
   single named section, with optional `--require-complete` and QID fibre
   projection; never pays missing chunks as negatives.
3. `tools/audit_zelph_native_name_fibres.py` (**new complementary SQLite
   aggregate**): directly streams original C++ rows into a *local scratch
   database* with transaction rollback unless native terminal frame and process
   exit 0. Preserves all duplicate `(name,node)` multiplicities. Only when
   **both name sections** are completely original-byte covered AND native
   streamed does it compare inverse name/node **multisets with counts**. It
   can additionally replay all five native QID roots against the original
   `nodeOfName` rows. This is not an alternative PostgreSQL S29 database,
   not a general proof of the native decoder's adequacy, and not all Wikidata.

`tools/materialize_original_equal_name_shards.py` fills missing saved Cap'n
Proto files for *previously source-equality-receipted* chunks by fetching
**only the pinned complete HF shard** and checking its SHA against the earlier
exact original HTTP206 receipt. It never re-downloads the 87.95 GB source bin.
The existing resumable `audit_zelph_hf_name_section_bytes.py` now accepts
`--import-physical-receipts-dir` to reconcile matrix chunks 1/4/75 into its
section ledger *without re-fetching* them, and `--save-published-root` to keep
newly compared packed shard bytes for native decoding.

## Local operator commands (use already retained exact files)

```bash
# From the ITIR #14 clean current-head worktree:
git rev-parse HEAD
bash tools/check_zelph_physical_maxcut_offline.sh

REV=0d4bd670959ebddae72f70d973410fdea8917ec1
MANIFEST_SHA=cedd5cf0e4951ae1aa7c2c5968614b0eb72a4c3b5c8b2dc4ab18c40be8c83f59
INDEX_SHA=89f7ccac888e9e7db09b349cef246e725d969f07d4280142c325e96e12a30d77
META=/tmp/zelph-new-p0-evidence/metadata/wikidata-20260309-all
MANIFEST="$META/wikidata-20260309-all.hf-v2.json"
INDEX="$META/artifact.index.json"
RUN=/tmp/zelph-new-original-name-evidence
OLD=/tmp/zelph-new-p0-evidence/nodeOfName-receipts
MATRIX="$RUN/positive-name-matrix"
SHARDS="$RUN/source-equal-shards"

# REQUIRED NEW COMPILE: prior adba4f0 decoder hash need not include latest
# upstream-schema native --stream-name-rows implementation.
bash tools/build_zelph_native_live.sh "$RUN/native-a1"
DECODER="$RUN/native-a1/selected-decoder"
sha256sum "$DECODER"
```

### Import existing physically verified chunks into one name-section ledger

```bash
python3 tools/audit_zelph_hf_name_section_bytes.py \
  --manifest "$MANIFEST" --original-index "$INDEX" \
  --dataset-revision "$REV" --manifest-sha256 "$MANIFEST_SHA" \
  --original-index-sha256 "$INDEX_SHA" --section nodeOfName \
  --receipts-dir "$OLD" --import-physical-receipts-dir "$MATRIX" \
  --save-published-root "$SHARDS" \
  --max-new-chunks 0 --execute
```

**Expected after import, if original receipts are intact:** distinct verified
indices `0,1,4,75` in the unified name-section receipt directory, no new
source HTTP206 transfer. Any inconsistent physical bytes/identity fails closed.

### Restore saved chunk 0 if missing (single-sided HF read, not full .bin)

```bash
python3 tools/materialize_original_equal_name_shards.py \
  --manifest "$MANIFEST" --original-index "$INDEX" \
  --dataset-revision "$REV" --manifest-sha256 "$MANIFEST_SHA" \
  --original-index-sha256 "$INDEX_SHA" \
  --physical-receipts-dir "$OLD" --physical-receipts-dir "$MATRIX" \
  --save-published-root "$SHARDS" --max-new-chunks 4 \
  --max-transfer-mib 256 --execute \
  --output "$RUN/a1-old-shard-rematerialization.json"
```

This should fetch only old physically witnessed packed files missing from
`$SHARDS`, typically chunk 0. No new original HTTP206 proof is claimed.

### First real SQLite A1 row-enumeration cut (four named chunks)

```bash
python3 tools/audit_zelph_native_name_fibres.py \
  --manifest "$MANIFEST" --original-index "$INDEX" \
  --dataset-revision "$REV" --manifest-sha256 "$MANIFEST_SHA" \
  --original-index-sha256 "$INDEX_SHA" \
  --physical-receipts-dir "$OLD" --physical-receipts-dir "$MATRIX" \
  --shard-root "$SHARDS" --decoder "$DECODER" \
  --positive-roots-receipt "$RUN/five-original-positive-qid-roots.json" \
  --sqlite-index "$RUN/a1-original-native-fibres.sqlite" \
  --max-new-chunks 4 --max-chunk-mib 256 --max-rows-per-chunk 10000000 \
  --decoder-timeout-seconds 900 --execute \
  --output "$RUN/a1-first-four-chunks.json"
```

**Expected:** nonzero exact original `nodeOfName` row counts, four positive
root replays (three chunks covering five QIDs), collision-preserving
`(name,node)` rows in SQLite; **`all_original_name_key_fibres_verified=false`**
and `both_source_name_sections_pair_multiplicities_equal=null` because
only one name section is partially covered. Actual row counts are UNKNOWN
until execution; do not invent them.

### Continue original name sections with bounded physical transfers

```bash
# Repeat with a bounded number of NEW chunks per invocation. The --import
# argument means existing matrix chunk 4/75 is not redundantly redownloaded.
python3 tools/audit_zelph_hf_name_section_bytes.py \
  --manifest "$MANIFEST" --original-index "$INDEX" \
  --dataset-revision "$REV" --manifest-sha256 "$MANIFEST_SHA" \
  --original-index-sha256 "$INDEX_SHA" --section nodeOfName \
  --receipts-dir "$OLD" --import-physical-receipts-dir "$MATRIX" \
  --save-published-root "$SHARDS" \
  --max-new-chunks 8 --max-chunk-mib 256 --max-transfer-mib 1024 \
  --execute

# The inverse section is independently named and has no verified chunks yet.
python3 tools/audit_zelph_hf_name_section_bytes.py \
  --manifest "$MANIFEST" --original-index "$INDEX" \
  --dataset-revision "$REV" --manifest-sha256 "$MANIFEST_SHA" \
  --original-index-sha256 "$INDEX_SHA" --section nameOfNode \
  --receipts-dir "$RUN/nameOfNode-receipts" \
  --save-published-root "$SHARDS" \
  --max-new-chunks 8 --max-chunk-mib 256 --max-transfer-mib 1024 \
  --execute
```

After each fresh set of packed shards, rerun the SQLite native audit with both
receipt directories and a **new** `--output` filename, reusing the same
`--sqlite-index`. All saved original provenance pins, native decoder binary
hash and processed-chunk digests must remain unchanged. The result only
claims two-section exact inverse multiplicity after every source name chunk
has complete physical/NDJSON evidence; otherwise reports incomplete.

## Acceptance / exact remaining gates

| Gate | Closing condition | Position |
|---|---|---|
| P0-S selected chunk | original HTTP206 bytes == published immutable packed shard | **operator PASS**: 0,1,4,75 of nodeOfName |
| P1 five-QID positive | exact original-equal shard + original C++ nodeOfName positive row | **operator PASS**: all 5 |
| A1a source name chunks | all 204 `nodeOfName` + all 204 `nameOfNode` physical witnesses | **OPEN** |
| A1b native row enumeration | native stream, exact terminal/exit, all 408 chunks, original multiplicity retained | **OPEN; executable implementation added** |
| A1c inverse collision fibres | complete sections; exact `(name,node,count)` multiset equality or explicit counterexample | **OPEN; executable join added** |
| A1d Agda full-source theorem weld | source-key universe ↔ indexed full-cover `CompleteNameShardFibre` / formal decoder refinement | **OPEN** |
| A2 | numeric node→left/right exact source ranges, original adjacency and full 20-word finite frontier closure | **OPEN** |
| P4/P5 | real Wikibase GUID/P14143/P854 primary semantics, PostgreSQL review/reopen and NORA export | **OPEN** |

**The 408 native name chunks only close their named sections.** They are
not evidence of A2 adjacency across 984+984 `left/right` shards, original
Wikipedia first-links, historical Ibrahim corpus, or publication authority.
