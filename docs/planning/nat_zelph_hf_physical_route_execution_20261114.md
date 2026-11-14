# Nat Zelph HF physical route execution — reported receipt and remaining verification

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
