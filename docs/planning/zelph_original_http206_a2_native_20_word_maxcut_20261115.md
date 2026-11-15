# Zelph A2 original HTTP206 → native left/right → declared 20-word maximum cut

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
