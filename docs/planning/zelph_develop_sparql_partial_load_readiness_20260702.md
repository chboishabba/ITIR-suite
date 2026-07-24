# Zelph Develop / SPARQL / Partial-Load Readiness

Date: 2026-07-02

## Current state

- Local Zelph working tree: `aur/zelph`
- Current branch: `acrion-develop-latest`
- Current commit: `df54f7740b78f011f41a86bf01b44713b8fb2132`
- `upstream/develop`: `df54f7740b78f011f41a86bf01b44713b8fb2132`
- `upstream/sparql`: `715e4326c8a62d896bb3d5285f10a79bad29c443`
- HF `acrion/zelph` observation on 2026-07-02:
  - `wikidata-20260309-all-shards` is visible
  - `wikidata-20260309-all-pruned-shards` is visible
  - the public sibling list did not expose manifest, route-sidecar, JSON index,
    or JSON manifest filenames

Updated HF observation on 2026-07-04:

- dataset API `lastModified`: `2026-07-01T03:10:52Z`
- public sibling count: `2323`
- root still exposes:
  - `wikidata-20260309-all.bin`
  - `wikidata-20260309-all-pruned.bin`
  - `wikidata-20260309-all-shards/`
  - `wikidata-20260309-all-pruned-shards/`
- full shard tree now exposes all four section directories with public objects:
  - `left`: `728` shard files
  - `right`: `984` shard files
  - `nameOfNode`: `204` shard files
  - `nodeOfName`: `204` shard files
- public dataset API still does **not** expose:
  - hosted manifest JSON
  - route-sidecar JSON
  - hosted index JSON
  - `.idx` sidecars

Bounded runtime probe on 2026-07-04 with local `aur/zelph/build-local/bin/zelph`
(`zelph 0.9.6-dev`):

- built a synthetic local `zelph-hf-layout/v2` manifest pointing at the public
  HF shard object URIs
- `meta-only` manifest load succeeded directly against the public shard layout
- bounded direct shard reads also succeeded for:
  - `nameOfNode=0`
  - `nodeOfName=0`
- `left=0` was deliberately not treated as a bounded acceptance case in this
  pass because public `left/chunk-000000` is multi-gigabyte

Practical reading:

- the public shard upload is now present enough to probe direct selected-chunk
  reads through a local manifest
- the hosted artifact contract is still incomplete for ITIR acceptance because
  the canonical manifest/index/route-sidecar objects are still missing

Conclusion:

- Local `aur/zelph` is already current with `upstream/develop`.
- The shard-compatible runtime line is therefore already present locally.
- The visible SPARQL work is still on a separate upstream branch from
  `develop`.
- Visible HF shard directories mean the data upload is present enough to watch,
  but not yet enough to treat ITIR acceptance as complete without a blessed
  binary plus manifest/route contract.
- As of 2026-07-04, the shard objects themselves are publicly readable enough
  for bounded direct probes through a local synthetic manifest, but canonical
  hosted-manifest acceptance is still blocked.

## 1. Audit: ITIR tools vs current Zelph `develop`

### What `develop` clearly supports now

From `aur/zelph/src/lib/command_executor.cpp` on `upstream/develop`:

- `.load-partial` supports:
  - explicit section selectors:
    - `left=...`
    - `right=...`
    - `nameOfNode=...`
    - `nodeOfName=...`
  - route selectors:
    - `route-node=...`
    - `route-name=...`
    - `route-lang=...`
  - manifest/runtime options:
    - `manifest=<path>`
    - `source-bin=<path>`
    - `shard-root=<path>`
    - `meta-only`
- `.index-file <file.bin> <json>` exists as a native surface.
- `.stat-file <file.bin>` exists as a native surface.

This means the core runtime surfaces that ITIR’s local tools expect are already
upstream on `develop`.

### What ITIR emits today

From `tools/build_zelph_hf_manifest.py`:

- ITIR still emits three manifest families:
  - `zelph-hf-layout/v1`
  - `zelph-hf-layout/v2`
  - `zelph-hf-layout/v3`
- `v1`:
  - `storageMode = single-file-offset-sidecar`
  - `transport.primary = http-range`
- `v2`:
  - `storageMode = multi-object-shards`
  - `transport.primary = hf-object-fetch`
- `v3`:
  - `storageMode = bucketed-query-shards`
  - planning/research layout, not the stable runtime target
- ITIR can advertise `nodeRouteIndex` sidecars through:
  - `hfObjects.nodeRouteIndex`
  - `layoutPlan.supportsNodeRouteIndex`
  - `capabilities.nodeRouteIndex`
  - `selectorModel.supportedOperations += node-route`

### What ITIR validates today

From `tools/run_zelph_partial_load_harness.py`:

- ITIR still validates both:
  - direct `.bin` chunk selection
  - manifest-backed selection
- The harness still treats several manifest chunk reads as:
  - `fallback_or_ok`

That is a stale acceptance posture for Stefan’s current stated target.

If the new WD shards are the real production path, the stronger target should
be:

- manifest-backed `v2` shard loads work directly
- no sequential fallback is required for normal shard-path cases

### Drift / stale assumptions discovered

The local planning docs still contain pre-fix assumptions that Stefan later
said changed:

- `docs/planning/zelph_hf_storage_contract_20260326.md` says:
  - `chunkIndex is file-local to the section/chunk family`
- Stefan later stated:
  - `chunkIndex` had to become section-global for the name sections so that
    manifest selection and sequential selection agree

Implication:

- local planning notes should no longer be treated as authoritative on
  name-section chunk identity
- actual runtime truth should be taken from the post-fix `develop` artifacts
  and emitted indexes/manifests

## 2. Checklist: when Stefan drops the WD HF artifacts

This is the concrete acceptance gate to run once Stefan provides the upload and
the blessed `develop` commit.

### Binary / branch

1. Confirm the exact Zelph commit or CI artifact he wants used.
2. Build or fetch that exact `develop` binary.
3. Record:
   - commit SHA
   - build provenance
   - whether it includes the post-fix name-section chunkIndex behavior

### Artifact contract

4. Fetch the HF manifest and route sidecar metadata.
5. Verify the manifest contains:
   - `manifestVersion`
   - `storageMode`
   - `transport.primary`
   - `source.headerLengthBytes`
   - `sections.*.chunkCount`
   - `hfObjects.nodeRouteIndex` if route selectors are expected
6. Reject if the production WD artifact arrives as:
   - `v1` only
   - no route sidecar
   - missing `capabilities.nodeRouteIndex` while routing is claimed

### Chunk identity sanity

7. Validate name-section chunk identity on the emitted index/manifest:
   - `nameOfNode` chunk indices are section-global
   - `nodeOfName` chunk indices are section-global
   - no per-language restart
8. Spot-check that `.index-file` output and manifest chunk selection agree on:
   - `left=0`
   - `right=0`
   - at least one `nameOfNode`
   - at least one `nodeOfName`

### Partial-load runtime

9. Run `tools/run_zelph_partial_load_harness.py` against the blessed binary and
   the blessed artifact.
10. Tighten interpretation of passing cases:
   - `manifest_v2_meta_only` must pass directly
   - `manifest_v2_left0` should pass directly
   - `manifest_v2_nameOfNode0` should pass directly
   - `manifest_v2_nodeOfName0` should pass directly
11. Treat sequential fallback on routine `v2` cases as a warning or failure,
    not a success path.

### Route-sidecar correctness

12. Validate:
   - `route-node=<id>` resolves chunk selectors deterministically
   - `route-name=<name> route-lang=<lang>` resolves deterministically
13. For at least one known QID and one known exact name:
   - compare route-selected chunks against explicit chunk selectors
   - ensure the loaded view is the same

### SPARQL + partial-loading combo

14. Only after the above is stable, run the SPARQL check:
   - import `sample_scripts/sparql.zph`
   - run one bounded SPARQL query over a partial-loaded artifact
15. Minimum acceptance target:
   - SPARQL dispatch works
   - no full-graph eager load occurs
   - route-selected chunk loading remains bounded and intentional
16. Stronger target:
   - exact-name and bounded subclass/path queries can run against routed
     partial loads without requiring the whole WD graph in RAM

### ITIR-side normalized connector acceptance

17. Materialize the manifest through the ITIR-side normalized transport
    adapter.
18. Verify the normalized transport artifact carries:
   - manifest version
   - transport mode
   - node-route capability
   - selected chunk/shard refs
   - sanitized backend capability flags
19. Verify it does not leak:
   - raw object URIs
   - raw route traces
   - bulky diagnostics

## 3. Merge-pressure map: SPARQL branch onto shard-compatible `develop`

Visible `upstream/sparql` diff against `upstream/develop` touches:

- `sample_scripts/sparql.zph`
- `src/lib/command_executor.cpp`
- `src/lib/interactive.cpp`
- `src/lib/network/zelph.cpp`
- `src/lib/network/zelph.hpp`
- `src/lib/network/zelph_impl.hpp`
- `src/lib/repl_state.hpp`
- `src/lib/script_engine.cpp`
- `src/lib/script_engine.hpp`
- test infrastructure:
  - `src/test/test_helpers.hpp`
  - `src/test/test_reasoning.cpp`
  - `src/test/test_sparql.cpp`

### Low merge risk

- `sample_scripts/sparql.zph`
  - additive script surface
- `src/test/test_sparql.cpp`
  - additive tests
- documentation additions
  - low semantic risk

### Medium merge risk

- `src/lib/command_executor.cpp`
  - SPARQL keyword/help wiring lands here
  - current visible `.load-partial` help text in `sparql` appears aligned with
    `develop`, so this should be manageable if no unrelated edits diverged
- `src/lib/interactive.cpp`
- `src/lib/repl_state.hpp`
  - SPARQL query accumulation and dispatch likely touch REPL control flow

### High merge risk

- `src/lib/script_engine.cpp`
- `src/lib/script_engine.hpp`
  - Janet bridge changes are central to Stefan’s SPARQL surface
- `src/lib/network/zelph.cpp`
- `src/lib/network/zelph.hpp`
- `src/lib/network/zelph_impl.hpp`
  - this is the main conflict zone
  - `develop` already carries:
    - manifest-backed partial loading
    - route-sidecar resolution
    - HF URI resolution
    - shard-root support
    - current predicate-index persistence work
  - `sparql` also changes core network/runtime behavior to support efficient
    closure evaluation and new native surfaces consumed by `sparql.zph`

### Specific concern

The visible SPARQL branch does not itself prove shard/manifest compatibility:

- `test_sparql.cpp` exercises SPARQL semantics
- it does not visibly exercise:
  - `.load-partial`
  - manifest-backed shard loading
  - route-sidecar routing under SPARQL execution

So even if `sparql` merges cleanly, the important combined acceptance target
remains unproven until someone explicitly tests:

- partial-loaded shard view
- routed selector path
- SPARQL evaluation over that bounded view

## Recommended next moves

1. Treat `upstream/develop` as the current runtime truth for shard-compatible
   loading.
2. Treat `upstream/sparql` as a separate feature line until Stefan explicitly
   says otherwise.
3. When the WD HF drop arrives, run the checklist above before treating the
   SPARQL + shard path as real.
4. Update any local planning note that still describes name-section chunkIndex
   as file-local/per-language rather than section-global.
