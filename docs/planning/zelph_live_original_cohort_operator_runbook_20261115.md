# Original Zelph → native Wikibase → SLR source review: physical operator runbook

## 15 November 2026: P0 existing itir-mcp HF connector is the sole physical transport owner

**Supersedes prior P0 metadata/shard acquisition via separate HF CLI or duplicated HTTP in tools.** Strict pinned physical API owner: itir-mcp/src/itir_mcp/shard_transport.py, functions fetch_pinned_zelph_object and open_pinned_zelph_range. The existing bounded preview APIs remain backward compatible and DO NOT prove complete source byte equality.

New consumer paths: tools/probe_zelph_hf_original_metadata.py (exact two pinned source metadata objects + raw native header), tools/verify_zelph_hf_original_header.py (strict original tiny HTTP206), tools/plan_zelph_hf_selected_fetch.py (exact selected shard object streaming, not subprocess), tools/verify_zelph_hf_remote_original_ranges.py (byte-for-byte comparison against original source HTTP206), and tools/run_zelph_hf_connector_maxcut.py (one-command dry-run / actual P0 physical receipt). All changes remain in existing ITIR PR #14; there is no new graph index or database owner.

**Real upstream wire compatibility:** Zelph's emitter uses manifestVersion=zelph-hf-layout/v2, storageMode=multi-object-shards, sourceOffset/sourceRange and nested object.path/object.sizeBytes. Earlier ITIR synthetic receipts used manifestVersion=2, storageMode=split-by-direction-and-section and offset. The same strict physical index parser now accepts both exact original-v2 dialects while checking source.binPath, source offsets, section indices/counts/byte sums, object paths, declared ranges and original header partition. It rejects unexpected annotations/fifth sections until separately formalised; there is no silent downgrade or fabricated completeness. Regression fixtures exercise the upstream emitter's real field layout.

**Exact-head source acceptance to run:**

    bash tools/check_zelph_physical_maxcut_offline.sh

Run it on the latest PR #14 head and record actual Python test count and native C++ result. The historical clean user receipt 198/198 Python plus native C++ at c73ad1ee641866f273113f3e12a4a3340db7cf40 PREDATES these new connector changes and is not a new-head PASS.

**Single command P0 header-only: build upstream native probe in separate new binary directory, then dry-run or explicit execution.** Use verified independently pinned manifest digest/revision:

    REV=0d4bd670959ebddae72f70d973410fdea8917ec1
    MANIFEST_SHA=cedd5cf0e4951ae1aa7c2c5968614b0eb72a4c3b5c8b2dc4ab18c40be8c83f59
    NATIVE=/absolute/NEW-native-bin-directory
    RUN=/absolute/NEW-evidence-workspace
    bash tools/build_zelph_native_live.sh "$NATIVE"
    python3 tools/run_zelph_hf_connector_maxcut.py --dataset-revision "$REV" --manifest-sha256 "$MANIFEST_SHA" --workspace "$RUN"
    python3 tools/run_zelph_hf_connector_maxcut.py --execute --dataset-revision "$REV" --manifest-sha256 "$MANIFEST_SHA" --workspace "$RUN" --header-decoder "$NATIVE/original-header-probe"

The second command is the only network operation; do not run it in an existing workspace. It requests exactly the pinned full manifest and original artifact.index.json via the HF connector plus a *tiny original .bin header* HTTP206 range. It never requests the full 82 GiB .bin. Outputs include metadata raw objects, original-header/original-header.capnp-packed, original-header/original-header-proof.json and physical-p0-disposition.json.

**Conditional selected-source bytes, only if a real source-backed route has been independently acquired:**

    ROUTE=/absolute/independently-authenticated-original-filtered-route.json
    RUN=/absolute/DIFFERENT-new-selected-evidence-workspace
    python3 tools/run_zelph_hf_connector_maxcut.py --execute --dataset-revision "$REV" --manifest-sha256 "$MANIFEST_SHA" --workspace "$RUN" --header-decoder "$NATIVE/original-header-probe" --source-backed-route "$ROUTE" --max-selected-gib 8

The existing connector streams complete published shard objects using exact whole-object HTTP 200 (with declared Content-Length) or complete-object HTTP 206 (with exact Content-Range), plus byte caps, per-object raw SHA256 and exclusive file creation. **The separate original .bin source-range comparator REQUIRES HTTP 206** and proves byte-for-byte equality only for selected source ranges. No arbitrary or absent route is silently completed: the manifest byte-offset index is NOT a node/QID-to-adjacency chunk index, so it does not prove a full name domain or all query words. An invalid or unavailable hosted manifest/index/header is BLOCKED, never synthetically replaced or claimed as PASS.

**Evidence firewall:** header/index agreement != payload equality; selected payload equality != route completeness; route completeness != native Wikibase statement/P854 support; valid source coordinates != human review or persisted S29; no output grants edit authority. Old 100 MiB limit for downloading an approximately 82 GiB original is impossible and is NOT used by this connector path.


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

### 1A. First physical maximum cut: HTTP206 original *header* without 82 GiB

The complete original `.bin` is **not** required for the first P0 witness. Before any large transfer, acquire the exact HF-v2 manifest and original `artifact.index.json` at the immutable revision, then request **only the initial packed header range** of the original binary. The native upstream-schema parser checks its four section counts against the complete index/manifest offset partition. This works only if the pinned remote `.bin` endpoint actually exists and honors exact HTTP 206. The source publisher, revision and raw manifest digest must remain pinned; an independently supplied `artifact.index.json` SHA is preferable.

```bash
# Compile the native header parser with the SAME generated original schema
# used by the existing check_zelph_native_capnp_roundtrip.sh.
CAPNP_ROOT=aur/zelph/build-local/src/lib/io
clang++ -fuse-ld=lld -std=c++17 -O2 -I "$CAPNP_ROOT" \
  tools/zelph_original_packed_header_probe.cpp \
  "$CAPNP_ROOT/zelph.capnp.c++" -lcapnp -lkj \
  -o "$RUN/original-header-probe"

# Dry-run (default) uses zero network and requests no source payload.
python3 tools/probe_zelph_hf_original_metadata.py \
  --dataset-revision "$REV" --manifest-sha256 "$MANIFEST_SHA" \
  --local-dir "$RUN/header-metadata" --receipt-dir "$RUN/p0-header"

# Explicit network cut: two metadata objects and the exact tiny packed
# header HTTP206 range, NOT the 82 GiB original .bin.
python3 tools/probe_zelph_hf_original_metadata.py --execute \
  --dataset-revision "$REV" --manifest-sha256 "$MANIFEST_SHA" \
  --local-dir "$RUN/header-metadata" --receipt-dir "$RUN/p0-header" \
  --header-decoder "$RUN/original-header-probe"
```

On success the physically retained `p0-header/original-header.capnp-packed` and `original-header-proof.json` bind the header's raw SHA, index/manifest offset geometry, four counts, exact TLS/HTTP 206 and immutable source revision. **This does not certify original payload bytes, the complete name-key domain or QID→adjacency-chunk routing.** If DNS, the original source object, or HTTP byte ranges are unavailable, mark the physical gate **BLOCKED**, not passed.

### 1B. No-full-bin selected payload path, *conditional on an independently sourced route*

Existing `tools/verify_zelph_hf_remote_original_ranges.py` can compare **selected** published shard files to exact HTTP206 byte ranges in the pinned original `.bin`, without downloading or storing its full 82 GiB. It requires a previously source-backed `route.json` and the selected shard files; the comparator cannot generate node routes by itself:

```bash
python3 tools/plan_zelph_hf_selected_fetch.py \
  --manifest "$RUN/header-metadata/wikidata-20260309-all/wikidata-20260309-all.hf-v2.json" \
  --route "$RUN/source-backed-route.json" \
  --dataset-revision "$REV" --manifest-sha256 "$MANIFEST_SHA" \
  --shard-root "$RUN/shards" --max-selected-gib 16 --execute \
  --output "$RUN/selected-fetch-plan.json"

python3 tools/verify_zelph_hf_remote_original_ranges.py \
  --manifest "$RUN/header-metadata/wikidata-20260309-all/wikidata-20260309-all.hf-v2.json" \
  --route "$RUN/source-backed-route.json" \
  --shard-root "$RUN/shards" \
  --dataset-revision "$REV" --manifest-sha256 "$MANIFEST_SHA" \
  --max-selected-gib 16 --output "$RUN/selected-original-ranges.json"
```

The name sections are sorted on different keys, but `left` and `right` chunks are **not sorted by node ID**. The original `.index-file` records *chunk byte offsets*, not a QID/node→adjacency-chunk index. Consequently, a correct original source-backed route cannot be manufactured just from the header plus `artifact.index.json`. It must come from an independently audited original `.bin` scan, an upstream published node-route index with authenticated provenance, or a separately justified complete streamed scan of the relevant chunks. Without that evidence, selected range equality is a **conditional physical payload witness**, not proof of all original node neighbours or negative answers.

### 1C. Full-original fallback ONLY when truly required and explicitly budgeted

The original full packed `.bin` is a distinct object from the split published shards. Its genuine upstream URL and independently trusted whole-bin SHA256 are not supplied by this runbook; do not invent either. The earlier example `--max-mib 100` for an approximately **82 GiB** full binary was impossible: a 100 MiB cap cannot fetch it. If an operator deliberately chooses a full local original scan, the cap must exceed the verified original byte size, and adequate storage, time and transfer budget must be provided. This is **not** the header-only pathway and should not be executed as part of the small P0 probe.

```bash
# OPTIONAL full-original fallback only, after source URL and independently
# authenticated digest/size are known and the huge transfer is approved:
# python3 tools/acquire_pinned_source_bytes.py \
#   --url "$BIN_URL" --source-kind zelph-original-bin \
#   --dataset-revision "$REV" --destination "$RUN/original.bin" \
#   --max-mib <budget-at-least-original-bin-size-in-MiB> \
#   --expected-sha256 "$BIN_SHA" --expected-bytes <known-full-byte-length> \
#   --execute --receipt "$RUN/bin-acquisition.json"
```

Even an exact received SHA against a *caller-provided* pin is not independently authenticated authorship. Once a real full original is independently established, the downstream original two-pass route/selected same-source native audit below is available. Until then, its steps 2–5 are **conditional and must not be described as executed**.

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
