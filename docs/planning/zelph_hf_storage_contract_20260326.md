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
- `chunkIndex` is file-local to the section/chunk family.

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

## Limitations
- v1:
  - still monolithic `.bin`
  - patcher for direct seeks is still landing
  - file-local chunk identity
- v2:
  - route-sidecar generation and local routed consumption now exist, but hosted
    object fetch still needs auth/transport validation on real HF URLs
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
- `tests/test_build_zelph_hf_manifest.py`
  - validates both v1 and v2 outputs.

## Next step
- harden hosted HF object fetch/auth for routed v2 manifests, then decide whether
  the prototype JSON route sidecar should be replaced by a denser binary/sqlite
  representation.
