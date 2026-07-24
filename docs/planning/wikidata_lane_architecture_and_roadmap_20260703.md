# Wikidata Lane Architecture And Roadmap

Date: 2026-07-03

## Purpose

This is the clean architecture/roadmap note for the current Wikidata lane
surface in ITIR/SensibLaw after Zelph `0.9.6`.

It is intentionally narrower than the older broad roadmap notes and more
architectural than the tactical shard-readiness notes. Use it as the top
planning link for:

- current lane inventory
- lane normalization direction
- Zelph integration order
- graph flatness handling
- cross-lane reuse into legal/journal work

## Current Architecture

The current repo now has three executable Wikidata architecture surfaces:

```bash
cd SensibLaw
../.venv/bin/python -m cli.__main__ wikidata lane-status
../.venv/bin/python -m cli.__main__ wikidata lane-bundle --lane disjointness_report
../.venv/bin/python -m cli.__main__ wikidata lane-graph --lane disjointness_report
../.venv/bin/python -m cli.__main__ wikidata lane-flatness
../.venv/bin/python -m cli.__main__ wikidata lane-plan --lane climate_review_demonstrator
../.venv/bin/python -m cli.__main__ wikidata lane-proof --lane disjointness_report
```

Those commands expose:

1. lane inventory and dependency class
2. a shared review bundle for one lane
3. a graph-side latent slice / flatness diagnostic view for one lane
4. a cross-lane flatness audit that decides whether rendering should stay deferred
5. a bounded adjacent-Zelph discovery plan for the parallel live-adjacent lanes
6. a bounded direct-Zelph proof surface for the first shard-native lane

The current runnable lanes are:

- `climate_review_demonstrator`
- `change_review_packet`
- `disjointness_report`
- `hotspot_eval`
- `nat_live_follow_preflight`

## Control Plane

Treat each Wikidata lane as a bounded review surface that may keep its own
native report, but must also project into one shared normalized shape:

- `sl.wikidata_signal_review_bundle.v0_1`

That bundle is the current carrier for:

- `surface_signal`
- `signal_kind`
- `authority_surface`
- `soft_type_strength`
- `candidate_entities`
- `candidate_properties`
- `residuals`
- `receipts`
- `dependency_cone`
- `promotion_status`

The important invariant remains:

- a Wikidata/entity/property match creates only a candidate projection
- promotion remains bounded and review-first
- no lane gains edit authority from normalization

## Lane Classes

The repo now classifies the current lanes into three dependency classes:

### `direct_zelph`

- `disjointness_report`

This is the first direct Zelph `0.9.6` beneficiary because the lane matches
the new qualifier + SPARQL + shard story most directly.

### `adjacent_live`

- `climate_review_demonstrator`
- `nat_live_follow_preflight`

These lanes can benefit from Zelph-backed discovery or confirmation pressure,
but do not require Zelph to remain executable today.

### `review_geometry`

- `change_review_packet`
- `hotspot_eval`

These are deterministic reviewer-geometry lanes. They matter, but they are not
the first Zelph integration pressure point.

## Graph / Flatness Plane

Flatness should be handled as a data/projection diagnostic question before it
is treated as a renderer problem.

In this note, `flatness` is not merely "low visual density." The broader ITIR
meaning is failure to preserve meaningful intermediate linkage layers between
local evidence and higher-order semantic/review anchors.

Use two distinct categories:

- `linkage flatness`: the emitted graph omits or collapses expected typed
  intermediate layers
- `render flatness`: those layers exist, but the display collapses them

This matters because the same doctrine is intended to carry across Wikidata,
SensibLaw/PNF, legal ontologies, journal/research lanes, and cross-ontology
bridges.

Canonical doctrine note:

- `docs/planning/itir_flatness_doctrine_20260703.md`

The first graph-side owner is:

- `sl.wikidata_latent_slice_graph.v0_1`

It derives a small typed graph from the normalized lane bundle and then emits:

- graph metrics
- node/edge kind distributions
- cone diagnostics
- flatness posture

Current meaning of the flatness posture:

- `projection_flat`: the lane graph is still structurally shallow in its
  current projection
- this is a measured property, not a visual complaint
- renderer work should only come after the diagnostics say the structure is
  present but presentation collapses it

The current `lane-flatness` audit is therefore only a first-order structural
screen. It does not yet prove richer linkage-depth ladders such as:

- Wikidata:
  `mention/text anchor -> candidate entity/property -> statement/qualifier context -> class/property lattice -> report/review tranche`
- SensibLaw / PNF:
  `word/mention -> token -> lexical WD candidate -> span:sentence:document -> sentence:PNF -> role/filler in generic PNF carrier -> document:PNF -> claim/constraint -> review packet -> tranche/global`
- legal/source ontology:
  `token -> sentence -> provision -> section -> instrument -> doctrine/obligation -> jurisdiction -> tranche`

Important boundary for those examples:

- the PNF layer should be described generically in terms of typed role/filler
  carriers
- human labels like `WalkFrame` may be explanatory shorthand, but they are not
  the canonical system object

The current executable audit surface for that decision is:

- `wikidata lane-flatness`
- it currently keeps renderer follow-up deferred to the `itir-svelte` priority
  list because all current lane graphs remain projection-flat and
  `hotspot_eval` also shows node-identity collapse before display

This matters because the same graph-side discipline is intended to carry over
into legal/journal lanes rather than producing a separate visualization
doctrine for each domain.

## Zelph / WD Order Of Work

Near-term order:

1. keep `lane-status` as the quick inventory surface
2. treat `disjointness_report` as the first shard-native Zelph lane
3. keep climate/live-follow progressing in parallel
4. use the latent slice graph to measure flatness before touching rendering

That second item is now partially implemented as a bounded local proof surface:

- `wikidata lane-proof --lane disjointness_report`
- proves the direct Zelph contract locally at the architecture/control-plane
  level
- keeps full hosted WD acceptance explicitly pending on manifest/index
  publication and byte alignment

Hosted WD shard acceptance still depends on the published manifest/index
surface being stable and byte-aligned with the uploaded shard objects. Until
that closes, local bounded proofs remain real, but they are not yet the final
full-WD acceptance signal.

That fourth item is now also executable as a non-visual audit surface:

- `wikidata lane-flatness`
- confirms whether the problem is still projection-side rather than visual
- keeps webui rendering deferred until a lane reaches a structured posture

The next highest-alpha tranche after that is:

- `docs/planning/pnf_zelph_wd_linkage_depth_contract_20260703.md`
- starts with Zelph/WD as the first external bridge
- does not let Zelph/WD redefine flatness
- keeps PNF as the spine and requires the bridge to preserve it

That third item is now also executable as a bounded adjacent plan surface:

- `wikidata lane-plan --lane climate_review_demonstrator`
- `wikidata lane-plan --lane nat_live_follow_preflight`
- keeps climate/live-follow machine-runnable as Zelph-adjacent discovery lanes
- makes it explicit that hosted WD publication is not a blocker for this tranche

## Cross-Lane Reuse

Do not treat this as a Wikidata-only architecture.

The intended reuse direction is:

- Wikidata lane proves the normalized review bundle
- Wikidata lane proves the latent slice graph / flatness diagnostics
- legal/journal lanes later reuse those same bounded carrier surfaces

So the architectural move is not “make Wikidata special”; it is:

- prove the shared bounded carrier on the best available typed public graph
- then reuse that carrier across other ITIR lanes

## Current Recommended Reading Order

1. this note:
   `docs/planning/wikidata_lane_architecture_and_roadmap_20260703.md`
2. current runnable lane snapshot:
   `docs/planning/wikidata_lanes_zelph_096_status_20260703.md`
3. tactical WD/Zelph acceptance and shard-readiness note:
   `docs/planning/zelph_develop_sparql_partial_load_readiness_20260702.md`
4. flatness/optimisation side note:
   `docs/planning/itir_wd_zelph_sensiblaw_flatness_optimisation_roadmap_20260702.md`
