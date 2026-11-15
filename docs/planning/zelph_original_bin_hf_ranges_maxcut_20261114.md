# Same-original Zelph `.bin` ↔ selected HF shards — physical maximum-cut receipt (2026-11-14)

## 15 November 2026 P0 real-source shortcut: original header + entire offset index (NO 82 GiB local binary)

**Last exact-head accepted by operator:** ITIR #14 at `fb61e629763b86c097f3f6a00a906575b02fe91d`: **165/165 Python tests and native Cap'n Proto C++ original mini-source** passed. DASHI #1506 at `9512b316` 9/9 Agda; SLR #10 `06bda03d` 24/24 Rust; SensibLaw #514 `f77b28f` 17/17 Python. All refer only to their checked source. New original-header metadata integration commits in this section are NOT YET locally accepted.

**High-value original artifact observation:** Zelph upstream publishes (i) full HF-v2 sharded manifest, (ii) `artifact.index.json` (original packed header and **every** chunk offset), (iii) original `.bin`, and (iv) actual shard objects. `.index-file` writes a byte-offset record for the packed original header and each of four section-global chunk groups. Source: https://acrion.github.io/zelph/sharding/ . Thus a pinned immutable `GET Range: bytes=0-(headerLengthBytes-1)` to the ORIGINAL `.bin` and direct native Cap'n Proto parse of its header can authenticate its **four actual source chunk counts** without materialising the full 82 GiB file.

**New committed P0 implementation (not yet new-head verified):** `verify_zelph_index_manifest_original.py` compares *all* index/manifest source chunks (section-global ID, direction/language, exact offset, exact length, size, contiguous header-plus-four-section cover). `zelph_original_packed_header_probe.cpp` parses only the actual standalone packed original header with upstream-generated Cap'n Proto and rejects unconsumed/trailing bytes. `verify_zelph_hf_original_header.py` uses HTTPS revision-pinned original `.bin` URL with exact HTTP206, Content-Range, Content-Length, identity encoding, bounded 1 MiB header, TLS-only final endpoint, and all four native count matches; it can retain the exact raw original header bytes under an exclusive-create path. `probe_zelph_hf_original_metadata.py` combines a DRY-RUN or explicit two-file Hugging Face CLI fetch (`manifest` and `artifact.index.json` ONLY) with the original HTTP206/native header check. It independently hashes the saved packed header before writing its final receipt, and refuses extra download arguments, a stale revision or overwriting evidence.

**Operator commands, after obtaining generated original schema headers:**

```bash
REV=0d4bd670959ebddae72f70d973410fdea8917ec1
# Supply a separately pinned full raw manifest SHA256; do not replace it
# with the hash of a different manifest revision.
MANIFEST_SHA=<expected-original-manifest-sha256>
CAPNP_ROOT=aur/zelph/build-local/src/lib/io
clang++ -fuse-ld=lld -std=c++17 -O2 -I "$CAPNP_ROOT" \
  tools/zelph_original_packed_header_probe.cpp \
  "$CAPNP_ROOT/zelph.capnp.c++" -lcapnp -lkj \
  -o /tmp/zelph-original-header-probe

# No network by default. Prints EXACTLY TWO immutable metadata filenames.
python tools/probe_zelph_hf_original_metadata.py \
  --dataset-revision "$REV" --manifest-sha256 "$MANIFEST_SHA" \
  --local-dir /path/to/p0-hf-metadata \
  --receipt-dir /path/to/new-empty-p0-header-receipts

# Opt-in: fetch ONLY those two metadata files and the exact tiny
# original .bin header HTTP206 range, then native-decode/count-crosscheck.
python tools/probe_zelph_hf_original_metadata.py --execute \
  --dataset-revision "$REV" --manifest-sha256 "$MANIFEST_SHA" \
  --local-dir /path/to/p0-hf-metadata \
  --receipt-dir /path/to/new-empty-p0-header-receipts \
  --header-decoder /tmp/zelph-original-header-probe
# Optional: --original-index-sha256 <separately-pinned-index-raw-sha256>
# Outputs include original-header.capnp-packed (exact raw source bytes)
# and original-header-proof.json (counts, full offset geometry, raw SHA).

# This is NEW source. Run local clean exact-head acceptance first:
bash tools/check_zelph_physical_maxcut_offline.sh
```

**Critical logical boundary:** A complete manifest/index crosswalk and a genuine native-decoded original source header only prove a header/offset-geometry fact at the fixed HF revision. They do **not** prove that every published chunk payload byte matches the original `.bin`, that 204 name chunks' decoded rows exhaust its name-key domain, that every QID gets all names/collisions, or that selected original graph relation words/joins preserve answers. Those still require immutable *selected* raw HTTP206 range comparisons, original source-backed route witnesses and A1/A2 physical premise instantiation. The main source HTTP original `.bin` remained inaccessible via DNS in this chat's execution environment; NO real physical P0 proof is claimed.


## Exact B5 discriminator acceptance and new P0 packed-partition audit (15 November 2026)

The operator's clean-worktree exact-head check of [ITIR PR #14 at `712011a91231295250ce196e77d0015e04635492`](https://github.com/chboishabba/ITIR-suite/commit/712011a91231295250ce196e77d0015e04635492) ran `bash tools/check_zelph_physical_maxcut_offline.sh` with **145/145 Python tests** and genuine native original-schema C++ packed Cap'n Proto roundtrips/negative controls, exit 0. This supersedes the previously documented 120/120 checked-head offline tranche. The additional 25 are 19 `test_verify_wikidata_native_entity_snapshot.py` and 6 `test_run_zelph_local_physical_maxcut.py`. It does not mean any 82 GiB upstream source bytes were physically replayed.

Companion local acceptance: [SLR #10 `fc819e652be4e78dcfaa3bcc0c1dafad8d6f3840`](https://github.com/chboishabba/slr/commit/fc819e652be4e78dcfaa3bcc0c1dafad8d6f3840) **24/24 Rust**, including five strict `native_raw_receipt_join` tests; [DASHI #1506 `20ef376c832568992baab3db5e657a8dc76e76e6`](https://github.com/chboishabba/dashi_agda/commit/20ef376c832568992baab3db5e657a8dc76e76e6) **9/9 Agda 2.9.0** (source unchanged from `cf3ba8d`); [SensibLaw #514 `f77b28f20ad4b15a2f873a223c2650fcc71461f8`](https://github.com/chboishabba/SensibLaw/commit/f77b28f20ad4b15a2f873a223c2650fcc71461f8) **17/17 pytest** (source unchanged from `a5715ea7`). These are operator-reported exact-head local results.

**Newer ITIR source requires a new acceptance:** branch subsequently reached [`11b5ea3f96d2d0ebb54121f84d03973a2a1ba9e0`](https://github.com/chboishabba/ITIR-suite/commit/11b5ea3f96d2d0ebb54121f84d03973a2a1ba9e0), **six commits after the 145-test accepted source**. The new `tools/audit_zelph_original_packed_partition.py` checks `headerLengthBytes`, whole-bin length, section header counts, dense section-global chunk numbers, actual declared offsets, nonoverlap, gaps, and final byte coverage for `left`, `right`, `nameOfNode`, and `nodeOfName`. It is integrated into `run_zelph_local_physical_maxcut.py` and its synthetic test module is included in the offline checker. **SOURCE WRITTEN / EXACT-HEAD CHECK OPEN** at `11b5ea3`; do not count the new tests as accepted until rerun.

**Original-object P0/P1/P2 still OPEN:** execute the real driver with independently acquired upstream source `.bin`, pinned original source digest, signed/independently audited dataset revision and manifest, and real immutable HF shard bytes. Check packed partition geometry, same-run selected original ranges/shard equality, four-section native decoder and finite declared query words. A successful synthetic mini-bin cannot pay any of these. Full name-key coverage, semantic P14143/P854 source confirmation and actual S29 persist/reload are also separate gates. The candidate-only raw entity join never grants source support or edit authority.

Exact-head acceptance:
```bash
git rev-parse HEAD
bash tools/check_zelph_physical_maxcut_offline.sh
```

---

## 15 November 2026 operator exact-head acceptance and next original-packed partition gate

**New operator verification RECEIVED:** ITIR #14 at `712011a91231295250ce196e77d0015e04635492` passed **145/145 Python tests plus all native C++ roundtrips including the two-pass original mini `.bin` producer**, under clean tracked-worktree conditions. SLR #10 at `fc819e652be4e78dcfaa3bcc0c1dafad8d6f3840` passed **24/24 Rust tests**. DASHI #1506 at `20ef376c832568992baab3db5e657a8dc76e76e6` retained **9/9 Agda 2.9.0** kernel targets; SensibLaw #514 at `f77b28f20ad4b15a2f873a223c2650fcc71461f8` retained **17/17 Python** tests. Exact-head source-level gates CLOSED at *these recorded source heads only*. P0 actual HF original bytes, real P854 source and S29 persistence OPEN.

**New independently formulated P0 structural cut (subsequent ITIR code; NOT part of 145/145 PASS):** `tools/audit_zelph_original_packed_partition.py` checks that the entire published manifest tiles the original packed `.bin` with one header and the correct four ordered sections: `left`, `right`, `nameOfNode`, `nodeOfName`. It demands source header length, bin size agreement, all section-global dense chunk numbers, identical section counts, exact `offset(cursor)`, full final byte coverage, and refuses overlaps, gaps, reordered sections, trailing bytes and boolean/invalid metadata. It is metadata/offset geometry only, **not** raw remote byte equality, whole-source rehash, downstream name-key enumeration, or original upstream authenticity. The one-shot physical runner now requires it *before* selected original/shard byte comparison and writes `original-packed-partition.json` with its raw SHA recorded in `physical-acceptance.json`.

**New source acceptance:** `bash tools/check_zelph_physical_maxcut_offline.sh` includes `tests/test_audit_zelph_original_packed_partition.py` and two newly added same-run driver partition tests; this latest commit has **not** been verified on a clean local head. Run it at the new SHA rather than assuming the old 145/145 receipt covers modified tests. No original 82 GiB `.bin` or real HF selected objects were downloaded in this chat environment: HTTPS requests to pinned Hugging Face dataset endpoints failed at the runtime network layer.

**Independent structural verification if an original route/manifest is available:**

```bash
python tools/audit_zelph_original_packed_partition.py \
  --manifest /path/to/pinned-raw-full-manifest.json \
  --route /path/to/fresh-source-bin-route.json \
  --source-bin /path/to/original-wikidata-20260309-all.bin \
  --expected-manifest-sha256 <independently-pinned-manifest-digest> \
  --output /path/to/new-original-packed-partition.json
# Omitting --source-bin checks the header/manifest supplied size agreement
# without verifying an actual local binary's byte size.
```

**A1 mathematical interpretation:** if (i) a trusted complete original source header gives exact section counts, (ii) all source packed sections form this gap-free partition, (iii) every original `nodeOfName` chunk has an independently checked same-original byte-equivalent published shard, and (iv) the decoder faithfully enumerates name rows, then every original source `nodeOfName` row is included in that published name-section cover. Those premises do **not** establish key uniqueness, QID name-range indexes, native Wikidata P14143/P854 source semantics or full graph query closure. The A1 collision-preserving list-fibre proof and the remaining global index completeness are distinct.


## 2026-11-15 next physical and native-source maximum cut (source committed; new head unverified)

**Operator acceptance checkpoint:** On clean checked heads, DASHI #1506 `cf3ba8d` Agda 2.9 **9/9**; ITIR #14 `7385872` Python **120/120** plus full upstream-schema packed original-mini-bin C++ builder/decoder; SLR #10 `4e0f150` Rust **19/19**; SensibLaw #514 `a5715ea7` Python **17/17**. These close their precise *offline* gate only. Subsequent ITIR/SLR commits below require fresh source-head checks.

**One-shot P0→P2 original local replay:** `tools/run_zelph_local_physical_maxcut.py` invokes the existing two-pass original `.bin` filtered producer, selected-offset byte comparator and actual C++ native schema decoder *in the same local execution*. Optionally feeds source-equal node/direction rows into `audit_zelph_finite_query_family.py`, reporting required additional numeric node boundaries without turning them into negative answers. The run produces `route-new.json`, `selected-range-proof.json`, `native-selected-physical-answer.json`, optional `finite-lr-query-closure.json` and `physical-acceptance.json`. Each output SHA is reported and prior files cannot be silently overwritten. Offline isolated orchestrator negatives: **6/6 passed locally**; new GH exact-head has not been rerun.

```bash
# On the pinned new ITIR #14 branch, only AFTER obtaining the actual
# original source bin and fetching selected immutable HF shard files.
python tools/run_zelph_local_physical_maxcut.py \
  --source-bin "$BIN" --manifest "$MANIFEST" \
  --shard-root "$ROOT" \
  --producer tools/zelph_bin_filtered_route_builder \
  --decoder tools/zelph_selected_packed_shard_decoder \
  --output-dir /path/to/new-empty-physical-acceptance \
  --dataset-revision "$REV" --manifest-sha256 "$MANIFEST_SHA" \
  --qid Q10403939 --qid Q10416948 --qid Q10422059 \
  --qid Q10651551 --qid Q56404383 \
  --query-family docs/planning/zelph_five_qid_lr_query_family.example.json \
  --max-selected-gib 16
# Optional (only if independently sourced):
#   --expected-source-bin-sha256 <full-raw-source-bin-sha256>
# Exit 0: real selected one-hop and requested finite words complete;
# Exit 3: real one-hop success but missing numeric node/direction boundaries;
# Exit 2: fail-closed source/provenance/decoder/error budget.
# For exit 3, read finite-lr-query-closure.json and rerun in a fresh
# empty output directory with each independently validated --node value.
```

**Read-only native Wikibase P4 source-byte lane:** New `tools/verify_wikidata_native_entity_snapshot.py` accepts *full* Wikibase JSON (Special:EntityData or wbgetentities) for one exact `(QID, statement GUID, property, lastrevid)` and an externally pinned raw SHA256. It preserves exact quantity amount/unit/bounds, qualifier snaks, ordered reference records, P854 URLs, and fails closed on malformed/duplicate/truncated JSON. Isolated 19/19 adversarial cases passed locally; the new repo head is not yet verified. This is NOT the structurally different Wikibase REST statement representation. The output retains `upstream_http_provenance_independently_verified=false` and `p854_documents_independently_verified=false`. The downstream SLR `native_raw_receipt_join` binds the raw receipt's QID/GUID/property/revision/digest/P854/quantity to the existing native candidate, with no source payment or edit authority.

```bash
# Obtain/pin an ORIGINAL full entity snapshot at a known revision
# independently. Revision-specific URLs are documented by Wikidata:
# https://www.wikidata.org/wiki/Special:EntityData/Q10403939.json?revision=<REVISION>
python tools/verify_wikidata_native_entity_snapshot.py \
  --raw-entity /path/to/native-full-entity.json \
  --expected-sha256 <independently-pinned-raw-entity-sha256> \
  --qid Q10403939 --statement-guid '<actual-QID-dollar-GUID>' \
  --property P14143 --entity-revision <actual-integer-revision> \
  --output /path/to/raw-native-observation.json
# Actual statement GUID and entity revision must come from the native source.
# A hash freshly computed from the same untrusted local bytes is not
# independent network/source-origin authentication.
```

**Latest source acceptance, NOT YET RUN:** `bash tools/check_zelph_physical_maxcut_offline.sh` now includes two new suites (19 raw-native and 6 local-physical driver tests) in addition to the operator-verified 120, i.e. 145 selected Python cases if the previous 120 remain unchanged. The C++ original-mini-bin roundtrip and previously verified checks remain in the runner. SLR adds 4 focused native-raw-receipt tests; cargo exact-head check pending.

**Still OPEN:** real original/source HF-byte origin, whole graph name-domain A1, property-labelled source/selected query A2, actual native entity bytes & P854 document inspection, S29 durable review/restart, genuine Éder Porto NORA export and current exhausted Nat GUID cursor. No graph candidate or self-reported receipt grants source review, semantic truth or external edits.


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



## 15 November exact-head native offline acceptance — PASS at a22995e4

**Verified source commit:** GitHub confirms `a22995e4d52d167686aaa2130e2fdfbcdf4b3dca` exists in this PR's history. The operator's local exact-head run of `bash tools/check_zelph_physical_maxcut_offline.sh` reports **120/120 Python PASS**, a successfully compiled upstream-schema Cap'n Proto writer/decoder, genuine packed-message roundtrip of **four sections** (`left`, `right`, `nameOfNode`, `nodeOfName`), **five fail-closed negative controls** (direction swapping, wrong chunk index, language mismatch, unknown-QID candidate-only, trailing-byte tampering) and **exit 0**.

**Offline native gate CLOSED at checked head.** This is stronger than the old **90/90 corrected-local Python** and decoder-compilation-only report. Later branch commits are not necessarily independently tested by that receipt. The original publication's immutable source `.bin` range-by-range SHA, selected HF shards, native first-hop query equality on one physical graph and full original partition are **NOT** paid by synthetic packed fixtures. These require the actual original `--source-bin` audit with a pinned manifest/original data source and independent bytes, followed by A1/A2 query closure. GUID/P14143/P854, S29 persistence/restart, authentic NORA export and reviewed Wikipedia cross-language repair remain separate.

**Next decisive physical execution:** `python tools/audit_zelph_native_selected_physical.py ... --source-bin "$BIN" ...` against the actual verified original `.bin`, immutable chunk paths with matching offsets, lengths, HTTP 206 status, selected shard SHA, all four native sections and same-object query-family responses. A missing raw original or unsupported range request is **BLOCKED**, never a synthetic success.

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
