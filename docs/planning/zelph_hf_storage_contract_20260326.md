# Zelph HF Storage/Query Contract (2026-03-26)

## Goal
- Define concrete, actionable Hugging Face hosting/query contracts for Zelph artifacts.
- Keep one migration mode (`v1`) and one production-intended HF-native mode (`v2`).

## Design choice
- `zelph-hf-layout/v1` remains the migration contract:
  - one hosted `.bin` object
  - one hosted sidecar offset index object
  - one hosted manifest object
  - selector unit = section-local chunk index
  - transport = HTTP `Range` against the monolithic `.bin`
- `zelph-hf-layout/v2` is the implemented multi-object HF-native target:
  - one object per `(section, chunkIndex)`
  - one manifest that maps each selector to an object path
  - transport = object fetch on selected shard objects
  - optional shard materialization from local `.bin + sidecar` via
    `tools/build_zelph_hf_manifest.py --layout v2 --emit-shards`

## Manifest contract: `zelph-hf-layout/v1`
- `manifestVersion` = `zelph-hf-layout/v1`
- `storageMode` = `single-file-offset-sidecar`
- `transport.primary` = `http-range`
- `hfObjects` should include:
  - `bin`
  - `index`
  - `manifest`
- `sections` entries are chunk-offset views (`offset`, `length`, `range`).

## Manifest contract: `zelph-hf-layout/v2`
- `manifestVersion` = `zelph-hf-layout/v2`
- `storageMode` = `multi-object-shards`
- `transport.primary` = `hf-object-fetch`
- `hfObjects` should include:
  - `manifest`
  - `index`
  - `left`
  - `right`
  - `nameOfNode`
  - `nodeOfName`
  - each with section-level path prefixes under `shards/<section>/`
- `sections` entries are selector-to-object mappings (`objectPath`, `sourceOffset`,
  `sourceLength`, `sourceRange`) and remain usable for query planning.

## Chunk naming
- Shard object path pattern:
  - `shards/<section>/chunk-<chunkIndex>.capnp-packed`
- Historical note: this contract originally treated `chunkIndex` as file-local
  to the section/chunk family.
- Current post-fix expectation for WD name sections:
  - `nameOfNode` chunk indices are section-global
  - `nodeOfName` chunk indices are section-global
  - ITIR tooling must not assume a per-language restart for name-section chunk
    identity
- Adjacency sections (`left`, `right`) still use section-scoped chunk selectors
  for manifest selection. Regenerated artifacts may still change chunk
  identity, so manifests/indexes remain the runtime source of truth.

## Capabilities
- Both layouts expose:
  - `headerProbe`
  - `selectedChunkRead`
- Route-sidecar support now exists as an optional companion artifact:
  - `nodeRouteIndex`
  - format: `zelph-node-route/v1`
  - current manifest builder can advertise it when present
- Both layouts currently do **not** expose:
  - `smallNeighborhoodExpansion`
  - `fullReasoningSafe`

## Cache policy
- Recommended immutable cache semantics.
- Invalidation keys:
  - `manifestVersion`
  - object path and size
  - manifest identity fields (`createdAtUtc`, `path`, checksums when available)
- For `v1`, chunk-level cache keys should include `(offset,length)` in the local range fetch layer.

### Manifest revalidation note (2026-07-14)

Manifests and payload ranges must not share the same cache policy. A manifest
fetch with an open-ended length (`length=0`) can otherwise remain indefinitely
stale after an in-place manifest patch. This caused a consumer to continue
reading the superseded local `source.binPath` even though the Hub manifest had
already been changed to an `hf://` URI.

Required follow-up for the loader/cache implementation:

- revalidate manifest objects before reusing an open-ended manifest cache entry;
- include the Hub revision or ETag in the manifest cache identity;
- retain shard/header range caches as immutable only when bound to the same
  manifest/object revision;
- preserve explicit `source-bin` as an override for controlled offline or
  alternate-source loads.

Immediate operational recovery for a stale manifest cache is to remove the
generated manifest cache entry and refetch it; shard payload caches do not need
to be discarded solely because the manifest metadata changed.

## Limitations
- v1:
  - still monolithic `.bin`
  - patcher for direct seeks is still landing
  - historical file-local chunk identity assumptions are not authoritative for
    post-fix WD name sections
- v2:
  - hosted remote routed consumption now works against a real HF dataset repo
    after fixing:
    - remote manifest prefetch
    - raw-file URL mapping from `hf://...` to `resolve/main/...`
  - chunk completeness/semantic completeness remains read-only incomplete view until route
    and closure strategies are added
- direct selected-chunk reads now work on the current 2017 and 2026 local artifacts
  after fixing sidecar offset accounting
- remaining limitation is not chunk decode for these artifacts, but the absence of
  higher-level routing and cache contracts

## Tooling
- `tools/build_zelph_hf_manifest.py`
  - `--layout v1` (default): emit monolithic+sidecar contract.
  - `--layout v2`: emit shard-object contract.
  - `--emit-shards`: materialize shard files under `--shard-root` for local HF-upload
    rehearsal.
  - `--node-route`: advertise an exact route-sidecar artifact when one exists.
- `tools/run_zelph_partial_load_harness.py`
  - now emits per-case fetch plans in its JSON summary so `v1` range fetches and
    `v2` shard-object fetches are machine-visible against real artifacts.
- `tools/zelph_bin_route_builder.cpp`
  - emits an exact chunk-membership route sidecar from actual `.bin` chunk payloads.
- `tools/estimate_zelph_shard_fetch_budget.py`
  - estimates route-node and route-name remote fetch envelopes from an emitted
    shard tree.
- `tests/test_build_zelph_hf_manifest.py`
  - validates both v1 and v2 outputs.

## Next step
- current blocker is no longer basic hosted transport viability; it is shard
  granularity and route-sidecar density.
- measured 2026 shard envelope from
  `tools/estimate_zelph_shard_fetch_budget.py`:
  - route-node (`left + right`) median about `51.95 MiB`
  - route-node p95 about `60.63 MiB`
  - route-node max about `700.53 MiB`
  - route-name (`nodeOfName`) median about `21.70 MiB`
- next design move should be finer shard sizing and/or a second routing tier,
  not re-proving hosted fetch.
- concrete next-contract draft now lives in:
  - `docs/planning/zelph_hf_v3_shard_contract_20260326.md`

## 2026-07-02 addendum

Stefan's post-fix WD sharding changed name-section identity enough that older
file-local/per-language chunkIndex wording must be treated as superseded for
`nameOfNode` and `nodeOfName`. Current ITIR readiness is tracked in:

- `docs/planning/zelph_develop_sparql_partial_load_readiness_20260702.md`
- `docs/planning/itir_wd_zelph_sensiblaw_flatness_optimisation_roadmap_20260702.md`
