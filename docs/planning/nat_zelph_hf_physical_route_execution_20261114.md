# Nat Zelph HF physical route execution — reported receipt and remaining verification

## 2026-11-15 operator source verification and stronger exact-head gate

**Operator's physical-tranche local readback:** original `bcbf7c3` source: 23/32 new Python tests pass, with 9 failures. Two one-line worktree repairs make 32/32 physical-shape tests pass; added to the prior 58 targets = **90/90 locally reported**. Both one-line fixes are now committed onto this same PR #14. The earlier failures must not be called 90/90 green **at original `bcbf7c3` without modifications**.

**C++ compile:** the original Cap'n Proto generated source and the selected decoder compile with `clang++ -fuse-ld=lld` (operator local linker `libcapnp.a` is LLVM-bitcode). The normal `g++` example cannot link on that toolchain. A separate **native packed-message writer/reader roundtrip** with all four original schema sections, exact section/direction/chunk index, and fail-closed appended garbage was added after the local report. It has NOT yet been executed.

**Current source additions after that local report:** strict source offset/size/SHA/URI + pinned HTTP206 original `.bin` URL validation in native audit; opt-in same-process `--source-bin` exact raw-byte re-verification; native rejection of valid packed messages with trailing bytes; synthetic negative controls; `tools/check_zelph_native_capnp_roundtrip.sh` and `tools/check_zelph_physical_maxcut_offline.sh` as clean-exact-head native/offline checkers. **The latest source head is untested in this chat.**

```bash
# One acceptance invocation on a clean ITIR PR #14 checkout:
bash tools/check_zelph_physical_maxcut_offline.sh
# Then execute actual immutable-shard physical P0/A1/A2 as documented below.
```

The source-level 90/90 local result does not prove source-bin↔HF identical bytes, full graph query closure or actual native Wikidata source support. The original physical request/route/receipt SHAs remain historical until independently recomputed on real files.




## Next accepted physical maximum-cut commands and source-state split

**Kernel (golden owner):** the operator's clean, source-only Agda 2.9 check at DASHI PR #1506 exact head `4c89edbe90ef0e29ea5c02b18bd5dfe090ab9e61` passed for seven imported modules. **ITIR local 58/58** Python tests were run at earlier head `a119add`, before the new physical tranche. Those results are credited but must not be described as validation of the latest C++ decoder or raw HF bytes.

**New combined execution doc:** [immutable full-source .bin ↔ selected HF byte-range + native Cap'n Proto A1/A2 pipeline](zelph_original_bin_hf_ranges_maxcut_20261114.md). This reuses the existing filtered route builder, exact Cap'n Proto schema, manifest v2, immutable HF revision, and local SLR/NORA authority firewall.

**New source and four test suites NOT YET RUN:** `verify_zelph_bin_shard_exact.py`, `verify_zelph_hf_remote_original_ranges.py`, `plan_zelph_hf_selected_fetch.py`, `audit_zelph_native_selected_physical.py`, `zelph_selected_packed_shard_decoder.cpp`. Each checks a distinct physical witness; the final audit requires the prior original-.bin source-range equality receipt. A successful fetch is not itself byte verification and one-hop selected-root equality is not all-word graph query completeness.

**No live HF access here:** Container DNS to `huggingface.co` failed; the pinned raw manifest and original source binary could not be acquired. **Physical P0/A1/A2 remains OPEN**, pending independent exact-head regression, native C++ compilation, actual immutable shard/range execution and preserved receipts.




## Later local regression receipt — ITIR PR #14 head `a119add` (14 November 2026)

Operator reports executing the **complete six-suite local Python 3.12 command** at head `a119add`: **58 passed in 3.54 s**. Per-suite: packager **6**, raw verifier **9**, HF probe **3**, byte/physical-name/adjacency closure **19**, strict QID routing **14**, manifest-v2 **7** (sum **58**). This **supersedes** the earlier 41-pass report only for these named tests. Reported results are local, not independent container execution here, and do not include a C++ physical rebuild, raw HF manifest/data rehash, physical selected-chunk readback, or full graph query closure. The later source on DASHI PR #1506 adds the three Agda 2.9 corrections plus [the previously authored core Set-sort changes from `0dc254eabe`](https://github.com/chboishabba/dashi_agda/commit/0dc254eabeb00c4fdf1dc6d6f1a0e013d05d9606).

**Physical next cut (not unit tests):** rerun the existing C++ filtered producer against the *actual pinned source .bin*, record source file SHA, emit new (different) route and receipt raw SHA256s, inspect real full-manifest `nodeOfName` coverage, acquire selected physical `left`/`right`/`nameOfNode` bytes, then run the source-bin versus HF root-neighbourhood equality audit and explicit query-family closure. Do not re-use the older digest after a producer-schema change. The same original source graph revision must be proven, not just copied into a field.

[Golden updated local Agda runner and exact gate roadmap](https://github.com/chboishabba/dashi_agda/blob/agent/nora-perspective-consumer-maxcut-20261114/Docs/ZelphTrieHyperfabricNatNoraMaximumCut20261114.md).



## New P0/A1/A2 implementation tranche (after the operator's 41-test run)

**Source changes on this same PR #14:** `package_zelph_filtered_route_receipt.py` now verifies that the interpreted route equals the JSON read back from the exact raw file hashed into the content address (previously separate objects could diverge). `tools/verify_zelph_filtered_route_replay.py` adds independent raw request/manifest/route/receipt replay; it checks the numeric-v2 manifest shape, request revision/digest binding, canonical receipt digest, original route raw SHA, QID/node/chunk mappings, and nonpromotion. This is a new verification tool, **not evidence the operator's prior raw files were replayed here**.

**A1 actual manifest cover:** `verify_manifest_name_cover` in `itir_mcp.zelph_query_closure` compares all numeric-v2 `nodeOfName` chunk index/language/length/physical URI tuples with independent SHA-checked name object receipts. It refuses omitted or additional chunks and duplicate identities. `declared_object_set_exhausted`/manifest-list completeness still does not imply the original graph's full name domain or a formally verified Cap'n Proto decoder.

**A2 actual source-bin oracle and selected-chunk check:** existing `tools/zelph_bin_filtered_route_builder.cpp` now collects adjacency lists for the *resolved five* (or any selected) node IDs in the same second pass of the original `.bin`; stores bounded `nodeAdjacency` and per-direction truncation flags; refuses same-QID cross-chunk collisions; checks each `AdjChunk.which` direction. `audit_selected_adjacency_against_bin` takes physically supplied `left/right` chunk bytes + a decoder, independently hashes every object, verifies exact planned node/chunk cover and compares each selected root's neighbourhood against the nontruncated source-bin oracle. A strict mismatch abstains. This is **root one-hop equality between two supplied carriers**, not all-word query-family completeness nor verified source-bin↔published HF identity.

**New code has not been locally rerun as part of this audit.** The earlier 41/41 result predates the added P0/A1/A2 tests and C++ changes. The raw manifest/dataset/route/digest four-tuple remains operator-reported. Preserve old digest receipts as historical; an updated C++ producer changes route JSON content and requires a new route and packaged digest.

Commands (in ITIR):
```bash
PYTHONPATH=itir-mcp/src python -m pytest -q \
  itir-mcp/tests/test_zelph_query_closure.py \
  tests/test_verify_zelph_filtered_route_replay.py \
  tests/test_package_zelph_filtered_route_receipt.py
# Build and execute the existing filtered route C++ producer with its pinned
# Cap'n Proto generated schema/toolchain; repackage the NEW emitted JSON.
# Then replay raw request/manifest/route/receipt with the new verifier.
```
[Golden maximum-cut ledger](https://github.com/chboishabba/dashi_agda/blob/agent/nora-perspective-consumer-maxcut-20261114/Docs/ZelphTrieHyperfabricNatNoraMaximumCut20261114.md).



**Date:** 2026-11-14. **Source of empirical values:** operator-supplied local execution report and command transcript summary; the raw local files are at `/home/c/Documents/code/ITIR-suite/build/receipts/` and were **not uploaded to GitHub or replayed by this audit**. This document is a handoff of reported measured data, not independent confirmation of the receipt bytes, HF content or local build/toolchain.

**Ownership:** DASHI/Agda **golden formal contracts**; SLR Rust/PostgreSQL **production state and reviewed evidence**; ITIR MCP **routing, graph-read interfaces and source receipt delivery**; SensibLaw Python **historical Nat reference**.

## 1. What the local run reportedly established

The operator reported:

- On `agent/nat-filtered-route-producer`, the combined exact-route, HF-probe and filtered-receipt suites: **21 targeted tests passed**. An earlier two-suite run showed **17 passed in 0.38s**. A separate broad suite had exit code 2; do **not** infer whole-repo green.
- The live [acrion/zelph dataset](https://huggingface.co/datasets/acrion/zelph) API resolved the immutable dataset SHA **`0d4bd670959ebddae72f70d973410fdea8917ec1`**.
- Full artifact `wikidata-20260309-all` manifest SHA-256: **`cedd5cf0e4951ae1aa7c2c5968614b0eb72a4c3b5c8b2dc4ab18c40be8c83f59`**.
- Pruned-small artifact manifest SHA-256: **`4f0696e81dd60c61c545f261b9bf3c5bb1bc22d181384381f147d7dd9dcc9cac`**.
- Live manifests did **not** advertise a `hfObjects.nodeRouteIndex`. The first metadata probe correctly returned **`manifest-route-index-not-advertised`**, `production_accepted=false`, rather than inferring missing QIDs.
- Local tools then read actual **pinned full-graph** `nodeOfName` section shards using Cap'n Proto C++ and performed exact string-key searches under `lang=wikidata`; this is a **separate producer path**, not a retroactive successful sidecar-based MCP `exact_wikidata_name_route` invocation.
- The operator reported a packaged `itir.zelph_filtered_route_receipt.v0_1`, with all five QIDs resolved and `full_route_materialization_performed=false`, `consumer_verification_performed=false`, `source_support_paid=false`, `edits_performed=false`.

## 2. Reported five-QID mapping — full artifact only

| External QID | Zelph internal node ID | `nodeOfName` shard index | Exact physical name-shard filename |
|---|---:|---:|---|
| `Q10403939` | `24721153` | 1 | `chunk-000001-wikidata.capnp-packed` |
| `Q10416948` | `874016` | 1 | `chunk-000001-wikidata.capnp-packed` |
| `Q10422059` | `63706277` | 1 | `chunk-000001-wikidata.capnp-packed` |
| `Q10651551` | `2475334` | 4 | `chunk-000004-wikidata.capnp-packed` |
| `Q56404383` | `741397` | 75 | `chunk-000075-wikidata.capnp-packed` |

The names refer to the *full graph at the recorded dataset revision*. They do not assert anything about pruned-small, the physical adjacency locations, or a future graph rebuild. Original QIDs are stable external names; internal node IDs/chunk indices are artifact-local.

Base for the reported physical files (substitute only the rows above):

```text
https://huggingface.co/datasets/acrion/zelph/resolve/0d4bd670959ebddae72f70d973410fdea8917ec1/wikidata-20260309-all/shards/nodeOfName/
```

**Important:** these are **reported** exact selected physical paths from the operator's run, not paths independently fetched or hash-verified here. A Cap'n Proto name chunk confirms a QID→internal-ID identity *in that graph*, not an adjacency or native statement claim.

## 3. Reported package identity and exact semantics

- Route artifact content address: **`sha256:fbc43156ae80b8e32f9cbd5b32dd30dcc2085ad9ead04e73e16ff8f376425233`**.
- Receipt JSON digest: **`d3970f969c4e9b030fdb75c2914318c20d9e20eb096cb0212ed3b6b421b6dd05`**.
- Route packager: [`tools/package_zelph_filtered_route_receipt.py`](https://github.com/chboishabba/ITIR-suite/blob/agent/nat-filtered-route-producer/tools/package_zelph_filtered_route_receipt.py).
- Reported actual producer lineage commit: `9386e6bd8974147339a186ef1d44c6acfa14dfce`; stated derived-from base route producer commit: `24f62fecbec11909bcdb32916801b2315a796513`.
- Local receipt path: `build/receipts/nat_zelph_filtered_route_receipt.json`. This `file://` local path is **not** a user-accessible GitHub artifact.
- The packager [implementation](https://github.com/chboishabba/ITIR-suite/blob/agent/nat-filtered-route-producer/tools/package_zelph_filtered_route_receipt.py) computes a SHA-256 of the **raw route file bytes**, then hashes a canonical receipt. `source_manifest_identity` is currently **copied from the caller's request**; the packager does not recompute a SHA-256 of the downloaded manifest or validate the route's raw source against its content. `complete_qid_resolution` checks matching QID lists, mapped node IDs, non-missing `nodeRoutes` keys and a producer flag; **not all of its graph relation assertions are independently decoded/validated**.
- `network_performed=false` is **packager-scope**, not an accurate description of the wider workflow: live HF shard bytes were reportedly downloaded in the upstream execution.
- `complete_qid_resolution=true` is **not** `complete_graph_query_coverage=true`, native `P14143` family coverage, or the full 57,989 statement migration.

## 4. Source-capability boundary that must survive SLR promotion

Per upstream [Zelph full Wikidata graph data description](https://huggingface.co/datasets/acrion/zelph), the principal full graph contains **entity-to-entity linked triples**, **not dates, quantities, identifier claims or full qualifier/reference statement bundles**. The disjointness-specialized variant separately carries selected list-item qualifiers. Consequently **neither a successful QID name route nor a positive adjacency hit can by itself verify Nat's quantitative P14143 values, methods, periods or P854 source propositions**. Those must come through native revision-pinned Wikidata exports and subsequently reviewed source evidence in SLR.

The original Nat 57,989 historical statements and the 57-slot five-QID test remain separate populations.

## 5. Gates after this execution (same owners)

| Gate | Readout after reported run | Exact remaining proof |
|---|---|---|
| Z4 — source identity | **Reported SHA and two manifests pinned** | Check raw receipt+manifest bytes independently; reconcile dataset SHA, sha256, run command and source identity; provenance guard on the route request |
| Z5 — name-section mapping | **Reported live Cap'n Proto exact five-QID name match** | Persist raw shard object-path/digest and exact selected chunk-to-manifest mapping in a reproducible execution receipt |
| Z6 — direct transport | **Reported direct `nodeOfName` shard decode** | Full no-fallback harness matrix for meta/left/right/nameOfNode/nodeOfName; corruption negative tests; do not call Z6 wholly closed |
| Z7 — budget | **No object-count/bytes tally provided** | Count downloaded physical objects/bytes/cache misses, including any scan across 204 name shards; compare targeted routing v2 and future v3 |
| Z8 — query coverage | **Name identity only** | Decode adjacency `left`/`right` and (where required) `nameOfNode`; determine scoped query-family completeness; preserve missing-route ≠ global absence |
| Z9 — SLR production | **Not performed** | Source-native SLR bundle, source/revision/GUID/proposition review, PG persisted S29 and selective reopen, Agda golden acceptance |
| Z10 — NORA | **Not performed** | Actual canonical NORA export/fixture and decision round trip via existing ITIR/SLR contracts |

## 2026-11-14 observed upstream manifest ABI correction

The same local operator reported the live manifest's `manifestVersion` as numeric **`2`** with `storageMode: split-by-direction-and-section`. Prior ITIR [`build_shared_shard_contract_from_zelph_manifest`](https://github.com/chboishabba/ITIR-suite/blob/agent/nat-filtered-route-producer/itir-mcp/src/itir_mcp/shard_transport.py) instead required string `zelph-hf-layout/v*`. This was a **concrete latent production mismatch** independent of the missing route sidecar.

[ITIR PR #14](https://github.com/chboishabba/ITIR-suite/pull/14) now source-implements compatibility for **only numeric 2 + exact published storage mode**, normalizing it to the internal `zelph-hf-layout/v2` contract; other numeric/layout combinations continue to fail closed. [Shape-specific regression tests](https://github.com/chboishabba/ITIR-suite/blob/agent/nat-filtered-route-producer/itir-mcp/tests/test_published_zelph_manifest_compat.py) are committed, but there is **no new native-run receipt for this patch**, and the fixture is based on the operator's live manifest field readback rather than a downloaded raw manifest in this audit. Raw live v2 interoperability still needs a network-enabled replay.

## Golden trie/ultrametric/hyperfabric maximum-cut owner

The transport is a *physical representation* of existing DASHI indexed prefix/fibre/adequacy semantics. The canonical [DASHI golden maximum-cut](https://github.com/chboishabba/dashi_agda/blob/agent/nora-perspective-consumer-maxcut-20261114/Docs/ZelphTrieHyperfabricNatNoraMaximumCut20261114.md) gives A1–A6 original mathematical obligations, B1–B6 runtime/Agda bridge obligations and C1–C6 physical/production acceptance. Exact prefix agreement and trie residuals are **already formalised**; a certified **key→physical shard cover**, query-specific completeness, and revision-coherent hyperfabric gluing are **not yet**.

The current 204-name-shard manifest and physical five-QID scan **are not assumed to be a balanced-ternary trie**. To exploit a trie/range index, demonstrate actual sort semantics and cross-chunk boundary coverage first. Otherwise use a correct section-global range map and keep the richer hyperfabric as the semantic overlay. `QID→nodeOfName` is not a native `P14143` statement. Do not build a second graph database or review store.

## 6. Minimum independent replay and promotion criteria

1. Obtain **the actual raw** `build/receipts/nat_zelph_filtered_route_receipt.json`, the byte-identical filtered-route JSON and the source request/manifest used by the operator (not screenshots). Rehash both at the named SHA; inspect and compare route `source`, `nodeRoutes` and `qidToNodeOfNameChunks` to the manifest+direct shard evidence.
2. Check that the route receipt's declared `node_to_left_chunks`, `node_to_right_chunks` and `node_to_name_of_node_chunks` were actually determined from their physical sections, **not copied or filled as empty placeholders**. Otherwise mark **name route verified, adjacency route pending**.
3. Record physical `remote_object_gets`, `bytes_fetched`, cache hits/misses, and timing for the name scan and subsequent per-node route; compare to v3 budgets.
4. Implement a strict provenance checker for route-request/manifest/shard/producer SHA consistency before SLR can admit these as executed transport evidence.
5. Under SLR production, use **native source family and actual P854 evidence** to pay source support; do not infer a quantitative/method/period claim from the entity-only Zelph adjacency graph.
6. Route this through ITIR's already-registered candidate-only MCP and **DASHI Agda golden** coverage/physical transport contracts. The next Agda gate is a pinned kernel receipt on the **actual same-source receipt**, not an unrelated finite data example.

The complete report cannot yet be independently reproduced from GitHub because the raw execution artifacts remain local. [Author-facing NORA entry point](https://github.com/chboishabba/SensibLaw/pull/514).


## 2026-11-14 source implementation delta — A1/A2/A6 consumer-side auditor

Added `itir-mcp/src/itir_mcp/zelph_query_closure.py` and `itir-mcp/tests/test_zelph_query_closure.py` on the **existing PR #14**. This supplements, rather than replaces, `itir.shard.exact_wikidata_name_route` and the C++ physical name scanner.

- `audit_declared_name_partition`: requires actual raw byte strings for **every caller-declared** section/global `nodeOfName` object, checks immutable graph identity presence, object SHA-256 and byte length, decodes each exactly once through an explicit callback, rejects undeclared/missing/duplicate physical objects and malformed decoded language/node IDs, preserves duplicate-name **collision fibres**.
- `lookup_audited_name`: returns a list of physical `(shard_id,node_id)` witnesses; an absent QID returns `unresolved-in-original-graph`, *not* global `novalue`. Decoder correctness remains an external refinement obligation.
- `evaluate_query_closure`: explicitly compares requested/inspected family dependencies and rejects mixed graph revisions. Full original-graph edge closure **remains false** without source-specific physical evidence, even if all supplied dependency labels were visited.
- Tests cover digest mutation, missing/extra chunks, chunk identity collisions, wrong language, invalid node, duplicate QID, scoped missing QID, mixed revisions and partial adjacency dependency closure.

**Do not claim that the input list of 'declared' objects is the full manifest population.** Binding manifest section enumeration, raw Cap'n Proto decoder identity and original-graph closure is still open. This utility intentionally does not infer native GUIDs, P14143 values, qualifiers or P854 support.

Run locally at exact PR head:
```bash
PYTHONPATH=itir-mcp/src python -m pytest -q \
  itir-mcp/tests/test_zelph_query_closure.py \
  itir-mcp/tests/test_exact_wikidata_name_route.py \
  itir-mcp/tests/test_published_zelph_manifest_compat.py
```

**Next physical maximum cut:** materialise original manifest/source request/route JSON and all selected real Cap'n Proto objects, run the callback against the repository's pinned decoder, then check manifest-level enumeration and decode `left/right/nameOfNode`. Record network object count + byte totals + cache state and no sequential fallback, with the actual dataset SHA. The historical five-QID values above remain *operator-reported*, not independently re-hashed here.

[Golden A1–A6 proof source and P0–P5 gate ledger](https://github.com/chboishabba/dashi_agda/blob/agent/nora-perspective-consumer-maxcut-20261114/Docs/ZelphTrieHyperfabricNatNoraMaximumCut20261114.md).
