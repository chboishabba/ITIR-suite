# Zelph Node-Route Sidecar (2026-03-26)

## ZKP Frame

O:
- Local owners:
  - patched `aur/zelph` loader and harness
  - local manifest/index builders
- External owner:
  - Stefan/upstream Zelph

R:
- Now that direct selected-chunk reads work, the next missing capability is routing:
  - given a node or exact name lookup, decide which chunk(s) to load without probing the whole section
- The route layer must not assume sorted node ranges unless that property is explicitly emitted.

C:
- Current artifact surfaces:
  - `.bin`
  - sidecar offset index
  - HF `v1` / `v2` manifests
- Proposed new artifact:
  - node-route sidecar emitted from actual chunk payloads

S:
- Current selected-chunk transport works for bounded selector cases.
- Current manifests still require the caller to already know chunk indexes.
- Important constraint from code:
  - adjacency storage uses `ankerl::unordered_dense::segmented_map`
  - save iterates current container order
  - therefore chunk order should not be treated as a stable node-range partition without explicit proof

L:
- direct chunk transport
- exact route sidecar
- small neighborhood expansion
- higher-level remote query contract

P:
- Route sidecar `v1` should be explicit and exact, not inferred:
  - `nodeToLeftChunks`
  - `nodeToRightChunks`
  - `nodeToNameOfNodeChunks` by language
  - `nameToNodeOfNameChunks` by language and exact normalized string hash
- Emit it by scanning real chunk payloads after index/manifest generation.
- Use compact records:
  - for node-routed sections:
    - `node`
    - `section`
    - `chunkIndexes`
  - for reverse-name sections:
    - `lang`
    - `nameHash64`
    - `chunkIndexes`

G:
- Promotion criteria:
  - no assumption of monotonic node ranges unless a separate invariant is introduced and tested
  - route sidecar can be regenerated from existing artifacts
  - harness can validate routed chunk lookups against direct scan truth

F:
- Missing implementation:
  - builder for the route sidecar
  - exact-name normalization/hash contract
  - routed harness cases

Synthesis:
- The right next route layer is an emitted exact sidecar, not a guessed node-range partition.

Adequacy:
- Adequate for implementation planning.

Next action:
- Build a route-sidecar generator that scans chunks and emits exact node/name -> chunk mappings.

## Proposed artifact

- `manifestVersion`:
  - `zelph-node-route/v1`
- companion files:
  - `artifact.route.json` for debugging/prototyping
  - later optional binary/Cap'n Proto projection for scale

## Proposed layout

- top-level:
  - `source.manifestPath`
  - `source.binPath`
  - `source.indexPath`
  - `routing.nodeExact`
  - `routing.nameExact`
- `routing.nodeExact`:
  - keyed by node id string
  - values:
    - `left`
    - `right`
    - `nameOfNode`
      - keyed by language
- `routing.nameExact`:
  - keyed by language then normalized exact-name hash
  - values:
    - `nodeOfName` chunk list

## Why not node ranges

- Current serialization iterates:
  - `_left.begin()`
  - `_right.begin()`
- Those maps are `ankerl::unordered_dense::segmented_map`, not ordered maps.
- So a range contract would be speculative unless Zelph explicitly changes save-time chunking to emit ordered chunks and records the ranges.

## Suggested build path

1. Reuse the fixed sidecar offsets.
2. Read each chunk once.
3. Emit exact route memberships.
4. Add routed harness probes:
   - resolve node -> chunk(s)
   - load only those chunk(s)
   - compare with bounded direct selector truth

## Progress impact

- Direct transport layer:
  - now working
- Route layer:
  - exact prototype builder now exists:
    - `tools/zelph_bin_route_builder.cpp`
  - current emitted artifact:
    - `zelph-node-route/v1`
    - chunk-centric exact memberships from real payloads:
      - `left`: `chunkIndex -> nodes[]`
      - `right`: `chunkIndex -> nodes[]`
      - `nameOfNode`: `lang + chunkIndex -> nodes[]`
      - `nodeOfName`: `lang + chunkIndex -> names[]`
- current consumer status:
    - manifest can advertise the route sidecar
    - patched Zelph now consumes it for opt-in routed partial loads:
      - `route-node=<id,...>` resolves `left` / `right` / `nameOfNode`
      - `route-name=<exact>` + `route-lang=<lang>` resolves `nodeOfName`
    - routed loads reuse the existing explicit chunk loader after sidecar resolution
- Higher-level remote query UX:
  - blocked on route layer, not on manifest chunk transport

## First implemented result

- Build command:
  - `clang++ -fuse-ld=lld -std=c++17 -O2 -I aur/zelph/build-local/src/lib/io tools/zelph_bin_route_builder.cpp aur/zelph/build-local/src/lib/io/zelph.capnp.c++ -lcapnp -lkj -pthread -o tools/zelph_bin_route_builder`
- Real run:
  - `./tools/zelph_bin_route_builder /home/c/Documents/code/ITIR-suite/wikidata-20171227-pruned.bin /tmp/wikidata-20171227-pruned.route.json`
- Observed output:
  - route file size: about `735 MiB`
  - source chunk counts:
    - left `18`
    - right `18`
    - nameOfNode `8`
    - nodeOfName `8`
- Interpretation:
  - exact route generation is feasible from existing `.bin` payloads
  - JSON is acceptable as a prototype/debug artifact
  - a denser binary or sqlite projection is still likely preferable before treating route sidecars as the long-term hosted format

## First consumer result

- Build:
  - `cd /home/c/Documents/code/ITIR-suite/aur/zelph && cmake --build build-local -j4`
- Real routed node load:
  - `.load-partial /tmp/wikidata-20171227-pruned.hf-v2.with-route.local.json route-node=1 shard-root=/tmp/zelph-partial-load-harness/wikidata-20171227-pruned/wikidata-20171227-pruned-shards`
  - observed:
    - `left chunks=1/18`
    - `right chunks=1/18`
    - `route_requested=true`
    - subsequent `.out 1` succeeded
- Real routed exact-name load:
  - `.load-partial /tmp/wikidata-20171227-pruned.hf-v2.with-route.local.json route-name=A route-lang=wikidata shard-root=/tmp/zelph-partial-load-harness/wikidata-20171227-pruned/wikidata-20171227-pruned-shards`
  - observed:
    - `nodeOfName chunks=1/8`
    - subsequent `.lang wikidata` then `.node A` resolved through the routed `nodeOfName` slice
- Remaining limitation:
  - unauthenticated direct HF object fetch still returns `401` on the current hosted shard URLs
  - routing is now implemented; hosted transport/auth remains the next operational gap
