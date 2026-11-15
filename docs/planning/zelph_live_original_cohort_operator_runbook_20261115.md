# Original Zelph → native Wikibase → SLR source review: physical operator runbook

**Owner:** existing ITIR [PR #14](https://github.com/chboishabba/ITIR-suite/pull/14). **Not a new PR, database, scheduler or alternative data source.** Original Zelph attribution: Stefan Zipproth / acrion (zelph.org); first-link research attribution: Ibrahim, Danforth and Dodds (2017). DASHI is mathematical gold, ITIR owns transport/native evidence, SLR owns production Rust/review, SensibLaw is historical/NORA reference.

## Zero-authority invariant and source gate

These commands generate *new observed bytes*, hashes and typed read-only candidate receipts. They do not independently certify that a URL is the original publisher, that a P854 document supports a property, that Wikipedia's first qualified hyperlink equals a Zelph/Wikidata graph edge, or that any record is suitable for Wikidata publication.

Operator-reported prior exact-head **PASS**: ITIR `fb61e629763b86c097f3f6a00a906575b02fe91d`, 165/165 Python and original Cap'n Proto mini-bin native, exit 0. **Everything added after that head in this runbook is SOURCE-WRITTEN / UNVERIFIED until rerun**. Use `bash tools/check_zelph_physical_maxcut_offline.sh` and log its exact HEAD and native compile exit status.

### 1. Obtain independently sourced byte pins *before* using the bytes

Record source/publisher, acquisition URL, immutable HF dataset revision, independent expected SHA256 and byte size. The reported HF revision is `0d4bd670959ebddae72f70d973410fdea8917ec1`; reported full-manifest raw SHA256 is `cedd5cf0e4951ae1aa7c2c5968614b0eb72a4c3b5c8b2dc4ab18c40be8c83f59`. These are previous operator-reported receipts, not fresh live checks in this branch. Reconfirm their provenance independently. Never create an "external expected hash" by simply hashing the untrusted file you are about to verify.

```bash
export REV=0d4bd670959ebddae72f70d973410fdea8917ec1
export MANIFEST_SHA=cedd5cf0e4951ae1aa7c2c5968614b0eb72a4c3b5c8b2dc4ab18c40be8c83f59
export RUN=/absolute/new/cohort-workspace
mkdir -p "$RUN"
python3 tools/acquire_pinned_source_bytes.py \
  --url "https://huggingface.co/datasets/acrion/zelph/resolve/$REV/wikidata-20260309-all/wikidata-20260309-all.hf-v2.json" \
  --source-kind zelph-manifest --dataset-revision "$REV" \
  --destination "$RUN/manifest.json" --max-mib 16 \
  --expected-sha256 "$MANIFEST_SHA" --execute \
  --receipt "$RUN/manifest-acquisition.json"
```

The **original full packed `.bin` is a different object from the split published shard files**. Its original upstream URL and independently trusted expected digest are not established by the source code or this runbook. Locate those externally before filling the following placeholders; don't invent an HF `.bin` path or assume that the split public shards reconstruct provenance automatically:

```bash
export BIN_URL='<authenticated-original-.bin-download-url>'
export BIN_SHA='<independently-authenticated-original-bin-sha256>'
python3 tools/acquire_pinned_source_bytes.py \
  --url "$BIN_URL" --source-kind zelph-original-bin \
  --dataset-revision "$REV" --destination "$RUN/original.bin" \
  --max-mib 100 --expected-sha256 "$BIN_SHA" --execute \
  --receipt "$RUN/bin-acquisition.json"
```

The client is network-off by default, bounded by `--max-mib`, and refuses overwrite, non-HTTPS/private hosts, bad lengths and bad supplied SHA digests. Its receipt explicitly keeps upstream-source authentication false: the operator must supply **independent original identity evidence**.

### 2. Build the actual native binaries (not the deleted offline-test temp files)

```bash
# Requires the same original generated Zelph capnp headers and libraries
# as tools/check_zelph_native_capnp_roundtrip.sh.
bash tools/build_zelph_native_live.sh "$RUN/native"
"$RUN/native/original-filtered-route" --bin "$RUN/original.bin" \
  --output "$RUN/initial-source-route.json" \
  --qid Q10403939 --qid Q10416948 --qid Q10422059 \
  --qid Q10651551 --qid Q56404383
```

`native-build-receipt.json` contains compiled executable hashes, not published upstream binary authenticity.

### 3. Fetch only manifest-declared selected shards; then prove range equality

```bash
python3 tools/plan_zelph_hf_selected_fetch.py \
  --manifest "$RUN/manifest.json" \
  --route "$RUN/initial-source-route.json" \
  --dataset-revision "$REV" --manifest-sha256 "$MANIFEST_SHA" \
  --shard-root "$RUN/shards" --max-selected-gib 16 \
  --execute --output "$RUN/selected-fetch-plan.json"
```

If the finite family has missing numeric frontiers, rerun the original producer and shard planner with explicitly enumerated `--node` values until the required original-source directions have been verified. Never reinterpret missing physical data as an empty adjacency.

### 4. Capture an actual full native Wikibase entity at an exact revision

Choose **actual** statement GUID and native entity revision from the original Wikibase source (no hard-coded fixture GUIDs). Special:EntityData's full JSON shape must be retained, including mainsnak, rank, qualifier, ordered reference and P854 values. Obtain an externally pinned raw response digest where possible.

```bash
export ENTITY_REV='<real-native-Wikibase-entity-revision-integer>'
export ENTITY_GUID='<real-QID-dollar-statement-GUID>'
export ENTITY_SHA='<independently-pinned-original-entity-raw-sha256>'
python3 tools/acquire_pinned_source_bytes.py \
  --url "https://www.wikidata.org/wiki/Special:EntityData/Q10403939.json?revision=$ENTITY_REV" \
  --source-kind wikibase-full-entity --destination "$RUN/wikibase-original.json" \
  --max-mib 64 --expected-sha256 "$ENTITY_SHA" --execute \
  --receipt "$RUN/wikibase-acquisition.json"
```

Do not confuse a Wikibase **entity revision** with a Wikipedia **article oldid**, or with the HF **dataset git SHA**.

### 5. One same-run P1/P2/P4 physical → native handoff

```bash
python3 tools/run_zelph_live_cohort.py \
  --source-bin "$RUN/original.bin" --manifest "$RUN/manifest.json" \
  --shard-root "$RUN/shards" \
  --producer "$RUN/native/original-filtered-route" \
  --decoder "$RUN/native/selected-decoder" \
  --output-dir "$RUN/verified-cohort" \
  --dataset-revision "$REV" --manifest-sha256 "$MANIFEST_SHA" \
  --expected-source-bin-sha256 "$BIN_SHA" \
  --qid Q10403939 --qid Q10416948 --qid Q10422059 \
  --qid Q10651551 --qid Q56404383 --target-qid Q10403939 \
  --entity-raw "$RUN/wikibase-original.json" \
  --expected-entity-sha256 "$ENTITY_SHA" \
  --statement-guid "$ENTITY_GUID" --property P14143 \
  --entity-revision "$ENTITY_REV" \
  --query-family docs/planning/zelph_five_qid_lr_query_family.example.json \
  --max-selected-gib 16 \
  > "$RUN/cohort-stdout.json"
```

**Exit 0**: the selected original physical one-hop and declared 20-word finite query family, plus native entity raw-byte evidence, satisfied *the input pins*. **Exit 2**: blocked / incomplete / mismatched; not a negative answer. The output path must be fresh and empty. Real physical evidence files are in `verified-cohort/`, including `source-bound-cohort-candidate.json`, `physical-acceptance.json` and the independently replayable selected receipts. A P854 claim or historical FLN identity is still not paid.

### 6. Bind each actual P854 document byte response without paying its semantics

For a URL **actually present** in `raw-native-observation.json`, capture the document with `tools/acquire_pinned_source_bytes.py --source-kind p854-document --execute --receipt ...`. If no independent digest exists, do not pass `--expected-sha256`; the receipt will explicitly say the pin was not supplied. Then:

```bash
python3 tools/verify_p854_document_bytes.py \
  --raw-native-observation "$RUN/verified-cohort/raw-native-observation.json" \
  --acquisition-receipt "$RUN/document-acquisition.json" \
  --document "$RUN/document-original.pdf" \
  --output "$RUN/p854-document-bytes.json"
```

A real person must separately review pages/sections/propositions and record source support. Actual downloaded PDF bytes alone do not establish that P14143 or its unit/qualifiers are supported.

### 7. SLR genuine PostgreSQL commit/reconnect (same existing database)

See [SLR #10 S29 bridge](https://github.com/chboishabba/slr/blob/agent/source-unit-wikimedia-handoff/docs/S29_REAL_SOURCE_REPLAY_20261115.md). Supply an existing database connection and run `scripts/s29_source_review_postgres.py` against the cohort candidate. It creates versioned tables inside that database only with explicit `--apply-schema`, commits the observation, reconnects, reads exact original coordinates, and logs exact-source dependency reopens on a changed revision. It never implies edit authority or automatically creates a human review decision.

### 8. DASHI first-link and NORA are independent consumers

For Wikipedia first-link claims, use DASHI #1505 `scripts/ibrahim_original_revision_audit.py` on original **revision-pinned wikitext** before comparing link semantics. For NORA, require an actually supplied source/standpoint/reviewer mapping and the SensibLaw #514 `plan_nora_source_bound_persisted_review` read-only crosswalk. Neither can infer equivalence merely from a matching QID.

## Hard boundary table

| Evidence | Script | Can prove | Cannot prove |
|---|---|---|---|
| Bounded HTTP raw bytes | `acquire_pinned_source_bytes.py` | exact observed SHA, length and supplied-pin equality | independent source authorship from self-declared hash |
| Original `.bin`/HF replay | `run_zelph_live_cohort.py` | same-run selected offsets, native decoding and declared finite query words | whole original graph name exhaustiveness/global negatives |
| Full Wikibase raw entity | existing native verifier | GUID/revision/property/mainsnak/qualifier/references | primary P854 document content or claim truth |
| P854 original response | `verify_p854_document_bytes.py` | original reference URL/bytes hash coordinates | substantive document endorsement |
| SLR Postgres readback | source review bridge | committed/reloaded candidate rows and exact sparse reopens | source authority or original document semantics |
| NORA/P3 | separate consumers | scoped revision-pinned evidence | cross-source equivalence without explicit identity proof |

**Known irreducible blockers:** authentic original bin location/identity, actual entity GUID and revision, actual P854 primary documents, human review and downstream legacy S29 schema mapping; no synthetic fixture can substitute.
