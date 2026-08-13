# Zelph HF `v3` Shard Contract (2026-03-26)

ZKP Frame

O:
- Local owners:
  - patched `aur/zelph` loader
  - local `.bin` index/route/manifest tooling
- External owner:
  - Stefan/upstream Zelph if this moves beyond local proof
- Runtime surfaces:
  - local `.bin`
  - HF-hosted object store
  - route sidecar
  - Zelph partial loader

R:
- Current `v2` proves hosted remote querying is feasible.
- The next requirement is not mere correctness; it is fetch-budget viability for
  large Wikidata artifacts.
- Acceptance target for a promotable remote layout:
  - exact-name lookup usually below `10 MiB`
  - routed node lookup usually below `10-20 MiB`
  - no normal query path whose median cost sits around `50+ MiB`
  - rare tails should be bounded far below the current `700+ MiB`

C:
- Current artifact/code surfaces:
  - `tools/build_zelph_hf_manifest.py`
  - `tools/zelph_bin_indexer.cpp`
  - `tools/zelph_bin_route_builder.cpp`
  - `tools/estimate_zelph_shard_fetch_budget.py`
  - `aur/zelph/src/lib/network/zelph_impl.hpp`
- Proposed new artifact family:
  - `zelph-hf-layout/v3`
  - `zelph-node-route/v2`

S:
- Current `v2` reuses original Zelph chunk boundaries.
- This gave a cheap migration and a successful hosted proof.
- Measured 2026 remote envelope:
  - route-node median about `51.95 MiB`
  - route-node p95 about `60.63 MiB`
  - route-node max about `700.53 MiB`
  - route-name median about `21.70 MiB`
- Therefore:
  - transport is solved
  - route lookup is solved
  - shard granularity is not solved
- Remaining uncertainty:
  - which bucket key gives the best fetch reduction without creating an
    unmanageable route index or too many tiny objects

L:
- `v2` proof -> explicit fetch-budget targets -> `v3` bucket contract ->
  local estimator -> hosted proof -> promotable remote format

P:
- Proposal A:
  - define `v3` adjacency shards by deterministic node-id buckets, not original
    file chunk boundaries
  - likely first cut:
    - `left` keyed by subject node bucket
    - `right` keyed by object/target node bucket
- Proposal B:
  - split route policy from payload policy:
    - compact route index maps selector -> bucket ids
    - payload shards contain only bucket-local records
- Proposal C:
  - make node-route one-sided by default:
    - `route-left-node`
    - `route-right-node`
    - symmetric fetch is opt-in
- Proposal D:
  - keep current `v2` as migration/compat proof and treat `v3` as the first
    query-shaped hosted layout

G:
- Promote `v3` only if:
  - estimator on a regenerated sample shows route-node median materially below
    the current `~52 MiB`
  - hosted proof confirms that measured fetch cost tracks the estimate
  - route sidecar remains deterministic and rebuildable from existing bins
  - loader complexity stays additive rather than replacing the whole partial
    loader path

F:
- Missing:
  - a formal `v3` bucket identity contract
  - a shard generator for `v3`
  - a smaller route-sidecar representation aligned to buckets instead of legacy
    chunk ids
  - empirical estimator output for candidate bucket sizes

Synthesis:
- `v3` should stop inheriting original `.bin` chunk boundaries and instead shard
  by query-shaped buckets with a compact route sidecar.

Adequacy:
- Adequate for implementation planning.

Next action:
- implement the smallest `v3` builder slice that can regenerate a sampled shard
  tree and compare its estimated fetch budget against `v2`.

## Why `v2` Is Not Enough

`v2` was the right first proof because it avoided inventing a new physical
layout before transport, routing, and HF object fetch were all proven.

But it inherits the original serialization unit:
- one object per legacy packed chunk
- route resolution returns legacy chunk ids
- remote query cost is therefore dominated by legacy chunk size, not by the
  actual lookup cardinality

That is acceptable for:
- migration
- compatibility
- proof of hosted feasibility

It is not acceptable as the likely end-state for full Wikidata remote querying.

## Proposed `v3` Contract

### Layout identity

- `manifestVersion`: `zelph-hf-layout/v3`
- `storageMode`: `bucketed-query-shards`
- `transport.primary`: `hf-object-fetch`

### Core idea

Replace legacy chunk ids with deterministic bucket ids.

- adjacency payloads:
  - `left` bucketed by subject node
  - `right` bucketed by target/object node
- name payloads:
  - `nameOfNode` bucketed by node
  - `nodeOfName` bucketed by `(lang, normalized_name_hash)`

### Bucket ids

Use stable bucket ids independent of legacy chunk order.

Candidate first cut:
- `bucket = node_id % bucket_count` for node-keyed sections
- `bucket = hash64(normalized_name) % bucket_count` for reverse-name sections

This is intentionally simple for the first slice because:
- deterministic
- easy to regenerate
- easy to estimate
- avoids assuming sorted node ranges

### Object paths

- `shards/left/bucket-000123.capnp-packed`
- `shards/right/bucket-000123.capnp-packed`
- `shards/nameOfNode/<lang>/bucket-000045.capnp-packed`
- `shards/nodeOfName/<lang>/bucket-000045.capnp-packed`

### Selector model

`v3` selectors should be bucket-based, but user-facing routed queries should not
need to know bucket ids.

User surfaces:
- `route-node=<id>`
- `route-left-node=<id>`
- `route-right-node=<id>`
- `route-name=<exact> route-lang=<lang>`

Route sidecar resolves those selectors into one or more bucket ids.

## Proposed `zelph-node-route/v2`

The current route sidecar is a large chunk-centric JSON prototype. `v3` should
move to a bucket-centric route sidecar.

### Desired semantics

- node route:
  - `node -> leftBuckets[]`
  - `node -> rightBuckets[]`
  - `node -> nameOfNodeBuckets[lang][]`
- exact name route:
  - `(lang, normalized_name_hash) -> nodeOfNameBuckets[]`

### Preferred representation

First promotable target should be denser than JSON:
- sqlite or binary table projection
- keyed lookup, not full linear scan

JSON may remain acceptable for tiny hosted proofs only.

## Default Query Policy

Current route-node assumes both adjacency directions are useful and fetches both.

For `v3`, default policy should be one-sided by intent:
- use `route-left-node=<id>` when inspecting outgoing facts
- use `route-right-node=<id>` when inspecting incoming/source-side facts
- use `route-node=<id>` only when symmetric adjacency is specifically needed

Reason:
- this alone can halve typical first-hop fetch cost in many workflows
- it keeps policy visible instead of silently overfetching

## Candidate Budget Targets

These are planning targets, not yet proven:

- route-left-node median:
  - `< 10 MiB`
- route-right-node median:
  - `< 10 MiB`
- route-node median:
  - `< 20 MiB`
- route-name median:
  - `< 10 MiB`
- route-node p95:
  - `< 30 MiB`

If a candidate `v3` scheme cannot approach these on the 2026 artifact, it is
not yet a good remote layout.

## Implementation Plan

### Phase 1: Budgeted design

1. Add a `v3` estimator mode that simulates bucket counts without rewriting the
   whole artifact.
2. Compare candidate bucket counts:
   - adjacency:
     - `256`
     - `512`
     - `1024`
   - names:
     - `128`
     - `256`
3. Pick the cheapest candidate that materially reduces median and p95 fetch cost.

### Phase 2: Minimal builder

1. Build a `v3` shard emitter from existing `.bin` + index input.
2. Emit a compact route sidecar aligned to buckets.
3. Generate a local `v3` manifest and run the fetch-budget estimator.

### Phase 3: Hosted proof

1. Upload a small `v3` proof artifact to HF.
2. Patch Zelph loader to consume `v3` manifests and bucket routes.
3. Repeat hosted route-node and route-name tests.

## First Recommended Collapse

The best first concrete move is:
- simulate `v3` bucketing on the 2026 artifact without changing Zelph runtime yet

Why:
- cheapest new evidence
- directly tests whether bucketing actually fixes the cost problem
- avoids premature loader complexity until the budget win is real

## First Lower-Bound Simulation

Using:
- `tools/estimate_zelph_shard_fetch_budget.py`
- `tools/simulate_zelph_v3_bucket_budget.py`
- source:
  - `/tmp/wikidata-20260309-fetch-budget.json`

Observed `v2` baseline:
- route-node median: `51.95 MiB`
- route-name median: `21.70 MiB`

Lower-bound `v3` candidates under balanced bucket redistribution:

- adjacency buckets `256`:
  - route-left average: `8.68 MiB`
  - route-right average: `9.26 MiB`
  - route-node two-sided average: `17.94 MiB`
  - route-node one-sided average: `9.26 MiB`
- adjacency buckets `512`:
  - route-left average: `4.34 MiB`
  - route-right average: `4.63 MiB`
  - route-node two-sided average: `8.97 MiB`
  - route-node one-sided average: `4.63 MiB`
- adjacency buckets `1024`:
  - route-node two-sided average: `4.48 MiB`

- name buckets `128`:
  - route-name average: `4.40 MiB`
- name buckets `256`:
  - route-name average: `2.20 MiB`
- name buckets `512`:
  - route-name average: `1.10 MiB`

Interpretation:
- even a conservative first cut at `256` adjacency buckets would likely beat the
  current `v2` route-node median by a large margin if rebucketing is reasonably
  balanced
- `512` adjacency buckets plus `128-256` name buckets looks like the most
  credible first target:
  - large expected reduction
  - still avoids exploding object count too aggressively

Important caveat:
- this is a lower-bound simulation, not promoted evidence
- it does not yet account for skew, hotspot buckets, or route fanout > 1
- it is sufficient to justify building a real `v3` emitter slice
