# ITIR WD/Zelph, SensibLaw Flatness, And Optimisation Roadmap

Date: 2026-07-02

## Summary

This note turns Stefan's WD/HF update into the next executable ITIR roadmap.
It keeps three workstreams separate:

- WD/Zelph readiness: prove the new HF shards, manifest path, route sidecar,
  and blessed `develop` binary before treating full WD linking as available.
- SensibLaw graph flatness: measure where structure is lost before changing
  graph rendering.
- optimisation: baseline reconciliation and graph-linking costs before trying
  to compress DB size or move storage back to HF.

Current external observation on 2026-07-02:

- `acrion/zelph` on Hugging Face is public and currently exposes:
  - `wikidata-20260309-all-shards`
  - `wikidata-20260309-all-pruned-shards`
- The public dataset API lists section shard directories and shard objects, but
  no manifest, route-sidecar, JSON index, or JSON manifest filenames were found
  in the sibling list.

Treat that as "shards are visible", not "ITIR acceptance-ready". The acceptance
gate still waits on Stefan's explicit go-ahead for both the final `develop`
commit and the usable HF artifact contract.

## WD/Zelph Acceptance

Use `docs/planning/zelph_develop_sparql_partial_load_readiness_20260702.md` as
the detailed checklist. This roadmap adds the immediate order of operations:

1. Confirm Stefan's blessed Zelph commit or GitHub CI artifact.
2. Confirm whether the HF drop will include a hosted manifest and route sidecar,
   or whether ITIR must generate a local manifest/index projection from a
   supplied `.bin`/index pair.
3. Verify manifest fields before runtime testing:
   - `manifestVersion`
   - `storageMode`
   - `transport.primary`
   - `source.headerLengthBytes`
   - `sections.*.chunkCount`
   - route-sidecar capability when route selectors are expected
4. Verify post-fix name-section chunk identity:
   - `nameOfNode` chunk indices are section-global
   - `nodeOfName` chunk indices are section-global
   - no per-language restart assumption survives in ITIR docs or tools
5. Run `tools/run_zelph_partial_load_harness.py` with v2 cases requiring direct
   success. Routine v2 fallback is now a warning/failure condition, not a
   production-ready success path.
6. Only after partial loading and route selection are stable, test SPARQL over a
   bounded partial-loaded view.

SPARQL readiness remains a combined capability claim. Passing SPARQL semantics
alone does not prove SPARQL + `.load-partial` + manifest + route-sidecar.

## SensibLaw Flatness Audit

The "too flat" concern should be handled as a diagnostic pass before renderer
work. In this roadmap, `flatness` is not defined as "the graph looks visually
simple." It is defined as loss of meaningful intermediate linkage layers
between local evidence and higher-order semantic/governance anchors.

Cross-domain doctrine:

- `linkage flatness`: the emitted graph omits or collapses expected typed
  intermediate layers
- `render flatness`: those layers exist in the graph, but the UI collapses or
  hides them
- canonical doctrine note:
  `docs/planning/itir_flatness_doctrine_20260703.md`

This definition is not Wikidata-specific. It is intended to hold across:

- SensibLaw / PNF lanes
- legal/source ontologies
- Wikidata lanes
- cross-ontology bridges
- other ITIR graph-bearing surfaces

Representative linkage ladders:

- SensibLaw / PNF:
  `token -> sentence:document -> sentence:PNF -> document:PNF -> claim/constraint -> review packet -> tranche/global`
- legal/source ontology:
  `token -> sentence -> provision -> section -> instrument -> doctrine/obligation -> jurisdiction -> tranche`
- Wikidata:
  `mention/text anchor -> candidate entity/property -> statement/qualifier context -> class/property lattice -> report/review tranche`
- cross-ontology bridge:
  `text anchor -> local ontology node -> external WD candidate -> mapped concept -> review decision -> tranche/global`

The current codebase has multiple possible flattening points:

- parser/extraction may under-emit typed relationships
- derived graph projection may collapse relation kinds
- Graphviz rendering may hide structure with a simple left-to-right layout
- embedding/PCA display may collapse high-dimensional structure into a weak 2D
  projection

The original ITIR/SensibLaw concern is specifically about missing linkage depth,
for example collapsing a richer chain such as:

- `word/mention -> token -> lexical WD candidate -> span:sentence:document -> sentence:PNF -> role/filler in generic PNF carrier -> document:PNF -> WD semantic/authority candidate -> PNF:Global/tranche`

down to something much flatter such as:

- `token -> sentence`

Important correction:

- PNF should be described with generic typed role/filler carriers, not named
  lexical frame classes such as `WalkFrame`
- those named frame labels may be useful as human hints, but they are not the
  system's canonical memory/comparison structure
- flatness often shows up as role erasure, not only missing hop count

First measure the source graph and derived graph payloads using existing
diagnostics:

- node count
- edge count
- component count
- giant-component ratio
- branching factor
- cone width by depth
- selectivity and leakage
- node-kind and edge-kind distributions

Then extend those metrics with linkage-depth diagnostics:

- layer coverage
- typed path depth
- bridge completeness
- path multiplicity
- anchor-to-tranche reachability
- collapse point

So the decision order is:

1. determine whether linkage depth is missing in the emitted graph
2. only if depth is present, investigate visual/rendering collapse in
   `itir-svelte`

Do not start with a renderer rewrite. If source graph diagnostics show low
branching and low edge-kind diversity, the issue is extraction/projection. If
diagnostics show rich structure but the display looks flat, then the issue is
layout/rendering.

Hard boundary: SensibLaw graph surfaces stay derived, optional, reviewable,
non-authoritative, and challengeable by source and receipt. WD labels, parser
output, embeddings, and graph visual density are not truth authority.

## Optimisation Baseline

The optimisation lane should extend
`docs/planning/itir_pnf_optimisation_campaign_20260605.md`, not create a
separate performance doctrine.

Initial WD/reconciliation rows should record:

- manifest version and HF commit SHA
- selected section count
- selected shard count
- selected bytes
- route-sidecar presence
- direct vs fallback status
- cache hits and misses
- DB rows written
- DB bytes written
- wall time
- RSS peak where available
- semantic/review drift status

Use HF as the likely distribution and reconciliation storage path only after the
bounded local acceptance loop proves artifact shape, routing, and capability
flags. Optimising DB size before direct partial-load and graph diagnostics are
measured would hide the real bottleneck.

## Near-Term Implementation Queue

1. Align stale planning docs around section-global name-section chunk identity
   and direct-success v2 manifest expectations.
2. Tighten `tools/run_zelph_partial_load_harness.py` so `manifest_v2_*` cases
   default to direct success rather than `fallback_or_ok`.
3. Add an ITIR-side fixture test that feeds a real sample manifest produced by
   `tools/build_zelph_hf_manifest.py` into the normalized HF transport adapter.
4. Add a small graph-flatness diagnostic report or fixture over one
   representative SensibLaw graph payload before changing Streamlit or Graphviz
   rendering.
5. When Stefan gives the go-ahead, run the WD acceptance gate and record the
   exact commit, HF SHA, manifest/route shape, and harness output.

As of 2026-07-03, item 4 is now executable via:

- `cd SensibLaw && ../.venv/bin/python -m cli.__main__ wikidata lane-flatness`

Current result:

- all current lane graphs remain `projection_flat`
- renderer follow-up stays deferred to the `itir-svelte` priority list
- `hotspot_eval` shows a real pre-render projection-loss issue: duplicate latent
  slice node ids collapse 20 emitted nodes down to 13 unique nodes
- current executable audit is still only a first-order structural screen; it
  does not yet prove the richer cross-ontology linkage ladder above

As of 2026-07-04, the linkage-depth follow-on has also moved beyond the first
GWB proof:

- `SensibLaw/src/policy/linkage_adapters.py` now exposes generic
  projection/collection fragments that accept lane-local layer names rather
  than freezing a narrow helper ontology
- `SensibLaw/src/ontology/wikidata_superclass_linkage.py` uses that kit for the
  `Q43229` superclass-pressure lane
- `SensibLaw/src/policy/brexit_linkage.py` uses the same kit for the bounded
  Brexit archive/policy-intent lane
- both adopters keep their underlying report builders receipt-free and attach
  receipts only at the lane wrapper boundary
- no new shared audit concept was added for either lane; the same
  `policy/linkage_depth.py` core continues to audit all lane families

## Next Highest-Alpha Step

The next tranche after the shared doctrine note is:

- `docs/planning/pnf_zelph_wd_linkage_depth_contract_20260703.md`

Order:

1. define `ExpectedLayerContract`
2. add `sensiblaw_pnf_wd_linkage`
3. add one tiny dog fixture plus one real SensibLaw fixture
4. add a non-visual linkage-depth audit
5. make the Zelph/WD bridge retain contract-compatible edges

As of 2026-07-03, items 1-4 are now executable via:

- `cd SensibLaw && ../.venv/bin/python -m cli.__main__ wikidata linkage-depth`

Current result:

- `dog_soft_stitch` passes as a synthetic control
- `climate_review_demonstrator` passes as the first bounded real-text
  PNF x Zelph/WD linkage case
- both cases preserve token/span -> sentence:document -> sentence:PNF ->
  document:PNF -> entity/topic candidate -> WD candidate ->
  Zelph/WD review surface -> review packet/tranche
- early token -> WD soft stitches are present but remain `promotion = blocked`
6. only then revisit renderer obligations

As of 2026-07-04, item 5 is now live for the first bounded real-text bridge:

- `SensibLaw/src/ontology/wikidata.py` remains the normalized generic climate
  demonstrator surface
- `SensibLaw/src/policy/linkage_depth.py` is now the shared control-plane
  engine rather than a WD-owned runtime
- `SensibLaw/src/policy/gwb_linkage_depth.py` proves the first non-WD bounded
  legal-follow adopter
- `SensibLaw/src/policy/au_linkage_depth.py` is now the first richer legal
  authority adopter, proving source -> legal context -> claim candidate ->
  authority -> review bundle -> tranche depth without requiring a WD bridge
- `SensibLaw/src/policy/linkage_adapters.py` now adds the first generic
  emission/composition layer so lanes can become arbitrarily deep without new
  audit-core work
- `SensibLaw/src/policy/gwb_narrative_linkage.py` is now the first
  adapter-composition proof, preserving multi-source
  source -> document -> parse -> candidate -> narrative coalescence ->
  authority -> tranche depth while keeping `build_gwb_semantic_report(...)`
  receipt-free
- `SensibLaw/src/ontology/wikidata_lane_receipts.py` now emits the
  contract-bearing `linkage_depth_receipt` for the climate lane as a lane-level
  enrichment surface
- `SensibLaw/src/ontology/wikidata_linkage_depth.py` now prefers the emitted
  bridge artifact over later audit reconstruction for that lane
- emitted receipt edges now carry contract-compatible bridge metadata including
  layer transitions, promotion boundaries, authority surfaces, and source
  anchors

Current result:

- `climate_review_demonstrator` is no longer only a reconstructed proof case
- the climate lane receipt surface now carries its own PNF x Zelph/WD linkage
  spine without teaching the generic WD adapter climate geometry
- audit reconstruction remains available as fallback, but the climate lane now
  defaults to `case_source = emitted_bridge_artifact`

As of 2026-07-04, the same lane-level emitted receipt pattern also now covers
the next WD pressure lane:

- `SensibLaw/src/ontology/wikidata_disjointness.py` remains a normalized
  bounded disjointness projector with no lane-receipt construction inside it
- `SensibLaw/src/ontology/wikidata_lane_receipts.py` now emits a disjointness
  `linkage_depth_receipt` as a lane-level enrichment surface
- `SensibLaw/src/ontology/wikidata_linkage_depth.py` now audits mixed lane
  contracts, so the climate PNF bridge and the structural disjointness bridge
  can both be consumed as emitted artifacts
- the disjointness receipt preserves:
  `source_window -> statement_bundle -> disjoint_pair ->
  violation_candidate -> WD review candidate -> Zelph/WD review surface ->
  review packet/tranche`

Current result:

- `disjointness_report` is now an emitted receipt case rather than only a
  later reconstruction
- the generic WD adapter boundary remains intact
- the next WD pressure lane can be extended by adding another lane-level
  receipt builder rather than teaching a generic adapter a new ladder

## Phase G.0

As of 2026-07-04, the next tranche is Phase G.0: extract the shared
linkage-depth control-plane into `SensibLaw/src/policy/linkage_depth.py`, keep
lane geometry outside the core, and prove inheritance with the first non-WD
adopter, `gwb_broader_review`.

Implementation order:

1. move the generic contract/case/receipt/audit machinery out of the
   Wikidata-named module and keep the public WD CLI as a compatibility wrapper
2. leave WD lane geometry in `src/ontology/wikidata_linkage_depth.py` and
   `src/ontology/wikidata_lane_receipts.py`
3. add a shallow but honest GWB legal-follow contract that does not require a
   WD bridge
4. freeze the next richer AU legal spine and the separate affidavit
   reconciliation/coverage contract family in docs before implementing them

Family order after extraction:

- GWB/Brexit: bounded public-source / legal-follow proving grounds
- AU: richer legal authority spine
- affidavit: reconciliation / coverage spine with `claim_root` /
  `incident_root` style reconciliation anchors
