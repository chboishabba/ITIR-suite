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

## Phase H: WD/Zelph-to-ITIR/SL Execution Tranche (2026-07-15)

The HF transport/cache acceptance work is now sufficient to begin the next
ITIR/SL/WD implementation round. The current Zelph cache PR is
[acrion/zelph#30](https://github.com/acrion/zelph/pull/30), with the local
implementation based on the refactored `develop` tree. It provides:

- remote manifest consumption with revision/ETag-aware cache identity;
- versioned manifest, shard, and binary-range cache entries;
- bounded remote partial loading without downloading the full WD binary;
- explicit metadata-only loading;
- offline cache-policy tests and a live stale-manifest regression.

The next work must remain generic-first. WD is the first external bridge and
Zelph is the first external graph consumer; neither owns the ITIR/SL world
model, completeness semantics, linkage audit, or receipt contract.

### Prioritised implementation order

#### 1. Consume the published WD manifests remotely

Create one normalized ITIR transport adapter over the blessed manifest and
cache contract. Record:

- manifest URI and revision/ETag;
- artifact and manifest versions;
- source header metadata;
- section/chunk counts and object paths;
- route-sidecar capability;
- cache and transport diagnostics.

This adapter must not expose raw Zelph-specific paths as the product API. It
should produce a generic bounded graph-slice request/result carrier.

#### 2. Load bounded Zelph slices without downloading the full graph

Start with the pruned artifact and a deliberately small fixture plan. Verify
metadata-only, one-section, and four-section loads. A slice result must carry
selected sections, selected chunks, selected bytes, and the source revision.

The current published chunk-0 test envelope is approximately 778 MB across
all four sections; that is expected payload cost, not a full-binary download.
The adapter must make this distinction visible to callers.

#### 3. Test incomplete versus completeness-certified graph views

Partial loading is not semantic completeness. Add a generic graph-view state:

```text
incomplete:
  selected coverage only
  unresolved shard coverage
  results are progressive/candidate-only

complete:
  required coverage declared
  all required shards examined
  no pending coverage
  completeness receipt attached
```

No lane or WD adapter may promote a partial result as exhaustive merely because
Zelph loaded successfully. Completeness must be tied to the query, manifest
revision, selected chunks, and coverage policy.

#### 4. Integrate the states into ITIR/SL world-model and receipt surfaces

The generic carrier/projection boundary should expose:

- `WorldModelRef` for the local target;
- external graph/slice provenance;
- coverage state and unresolved residuals;
- bridge proposals and decisions;
- pressure diagnostics;
- source and manifest receipts;
- final completeness receipt where justified.

The core should audit and project these values. Adapters emit them. Profiles
configure them. Lanes prefill source/profile data. Wrappers attach receipts.
Do not add WD fields directly to lane-owned entities or claims.

#### 5. Test WD entity/event linking

Use one reviewed entity attachment and one reviewed event attachment as the
first functional bridge cases. Preserve:

```text
local source span
→ local entity/event candidate
→ external bridge proposal
→ WD evidence/revision
→ review decision
→ ITIR/SL linkage case
→ receipt
```

WD identity must not replace the local candidate, inherit a formal role, or
inherit legal/evidentiary authority. Rejected, conflicted, and stale links must
remain reconstructable.

#### 6. Run domain-specific type/pressure checks

Only after the bridge and coverage surfaces are stable, run bounded WD pressure
profiles such as superclass, disjointness, qualifier, cohort, and expected
shape checks. Pressure results remain diagnostics or review candidates; they do
not overwrite lane-local PNF, legal authority, or source-grounded truth.

### First bounded tranche

The first implementation tranche should be deliberately small:

```text
remote pruned manifest
→ costed selected graph chunks
→ explicit incomplete receipt
→ one reviewed entity/event attachment
→ one domain-pressure result
→ generic ITIR/SL review surface
```

Then replay the same generic path through GWB, AU, Brexit, and Affidavit
fixtures. Their current siloing is a legacy implementation artifact; the
end-state tests the same carrier, bridge, coverage, projection, and receipt
contracts at different readiness levels.

### 2026-07-15 implementation checkpoint

The first provider-neutral carrier is now implemented across ITIR-MCP and
SensibLaw:

- ITIR-MCP fetches a remote manifest and derives a bounded graph-slice plan
  without fetching shard payloads; the plan records sections, logical chunks,
  declared bytes, unresolved shard coverage, and candidate-only status.
- SensibLaw validates graph-view coverage, carries external bridge proposals,
  decisions, and pressure diagnostics in the shared world model, and exposes
  them in generic review/linkage/receipt projections.
- The checked fixture contains one entity attachment, one event attachment,
  one reviewed decision, and one expected-shape diagnostic. It proves that
  incomplete coverage is not complete closure and that none of these records
  inherits role, legal, evidentiary, or promotion authority.

Live validation against the published pruned artifact resolved revision
`aee8527468167147da8e3170562870dfc4ade664`. Its 111,981-byte manifest supports
metadata-only graph planning with no shard fetch. A remote four-section
selection subsequently loaded chunks `left=74`, `right=74`, `nameOfNode=13`,
and `nodeOfName=13`: 60,731,574 bytes (about 57.9 MiB) of payload, not the full
graph. Zelph 0.9.9 explicitly marked the resulting graph view incomplete.

Status against the first six implementation steps is now:

| Step | Status | Boundary reached |
| --- | --- | --- |
| Consume published WD manifests remotely | done | ITIR-MCP resolves the revision-bound remote manifest. |
| Load bounded Zelph slices without the full graph | done for explicit bounded selection | `itir.shard.bounded_graph_slice_plan` reports selectors/chunks and declared byte cost before a fetch. Zelph remotely loaded a four-section 60,731,574-byte (57.9 MiB) selection; chunks are still coarse and `nodeRouteIndex: false` prevents efficient QID-targeted selection. |
| Distinguish incomplete from completeness-certified views | done | Coverage validation makes incomplete views candidate-only and fails closed for unsupported completion claims. |
| Carry graph state into ITIR/SL world-model and receipts | done | Graph coverage, bridge candidates/decisions, pressure, provenance, and review/linkage/receipt projections share the provider-neutral carrier. |
| Test WD entity/event linking | first revision-pinned entity-export slice done | The generic Wikibase adapter validates supplied QID/revision and emits label/alias/property/statement observations. `Q1785637@2443793937` attaches to a generic local entity with an explicit decision and to a local review event as review-required `related_concept`; shared review/linkage/receipt projections preserve both without authority inheritance. |
| Run domain-specific type/pressure checks | first bounded direct-type/closure slice done | The generic evaluator still abstains with a coverage residual for the incomplete absence fixture. The validated `Q1785637@2443793937` export positively observes `P31`; revision-pinned entity exports for its direct types observe `Q4830453 -> Q43229` through `P279`, yielding a compatible, explicitly bounded organisation-superclass diagnostic. No global closure is claimed. |

The immediate implementation sequence is therefore: select one local
GWB/AU/Brexit entity and event candidate; derive logical name/node/property
selectors; emit a query-shaped slice plan that reports selected sections,
logical chunks, and declared payload bytes before any shard fetch; then load
only the accepted coverage; emit reviewed bridge attachments; run one bounded
expected-shape or class/property diagnostic; then replay that generic context
through the GWB, AU, Brexit, and Affidavit wrappers. The wrappers may add only
source anchors and profile defaults, not lane-owned bridge semantics.

The first concrete adopter is Nat Cohort D row `Q1785637`. Its historical
synthetic incomplete fixture records a missing-`P31` typing deficit and remains
an abstention regression. The current revision-pinned `Q1785637@2443793937`
entity export instead positively observes `P31` and supports bounded
organisation-compatible pressure through supplied `P279` evidence. Neither
case defines a pharmacy-chain structural signature, global closure, or an
automatic type/migration action. Both use the same generic local
entity/graph-view/bridge/pressure carrier and are reusable for later
organisation, city, and cohort-derived expected-shape profiles.

The historical four-section section-0 selection remains an acceptance smoke
test only. The current remote bounded acceptance selection is
`left=74/right=74/nameOfNode=13/nodeOfName=13` at 60,731,574 bytes (57.9 MiB).
Both prove that a partial graph can resolve graph relations (`left`/`right`) and
node/name mappings (`nameOfNode`/`nodeOfName`), but neither is the required
shape of every query. Until route indexes and smaller shards exist, a logical
query-shaped plan can still select a physically large shard; the plan must
surface that cost rather than conceal it.

### SensibLaw H9 transport consequence

The first SensibLaw H9 transport integration now uses the Zelph CLI through a
provider-neutral snapshot backend. HF is the primary source; a local `.bin`
artifact is an interchangeable offline source, and live Wikidata is disabled
unless a caller explicitly supplies that tier.

The current public March 2026 pruned v2 HF manifest is useful for proving the
transport boundary, but it has no `nodeRouteIndex`. Its legacy chunks are too
coarse to make one subprocess per label acceptable. The backend therefore
loads only the `nodeOfName` section for v2 discovery and batches the complete
label workload through one Zelph process. Property queries keep name sections
out of the load. This is a measured fallback, not the target economics.

The shard optimization remains the v3 query-shaped bucket plan: deterministic
name and adjacency buckets plus a route sidecar. Existing estimates put v2
route-name at 21.70 MiB median / 41.57 MiB p95 and two-sided route-node at
51.95 MiB median / 60.63 MiB p95. A newer full HF rip should publish a
route-aware v3 manifest before it is treated as the production H9 source.

### Compiler-convergence control note

The governing next programme is
`docs/planning/generic_world_model_compiler_convergence_20260716.md`.
It treats Nat, Peter/Ege/Rosario, GWB, AU, Brexit, and Affidavit as proving
tranches of one generic compiler, sequences generic replay before closure and
cohort-derived DSP, and separates runtime graph algorithms from DASHI's formal
non-authority boundary.

### Context provenance and later pressure/federation work

The architecture refresh for this tranche was reviewed against the archived
ChatGPT thread `WD Bridge Architecture` (online UUID
`6a54b21f-ba30-83ec-b08e-0e62cb9d0933`, canonical archive thread
`71e63a13e10f7370ace24a676750577ca63e3317`, DB snapshot
`pull_20260714T035959Z`). A 2026-07-15 live refresh attempt returned zero
messages, so the current reading is archive-backed rather than freshly
web-verified. Its hidden Project/NotebookLM file-context messages are not
treated as authored design evidence.

The resulting clarifications are:

- bridge capability is suite-wide while traversal remains candidate-conditional;
- a WD identity attachment, external type pressure, local role, and authority
  result are distinct records;
- later expected-shape pressure should combine bounded graph, article,
  simplification, translation, and domain-cohort views through the same generic
  diagnostic carrier, without copying peer values or asserting global truth;
- bridge receipts should later become inputs to a forkable, versioned basis
  manifest. Channel/publication projections consume selected bases and
  attestations under local policy; popularity, hosting, or token weight must
  not become a truth oracle.

### Implementation notes for later large-query execution

The eventual large-join executor should be asynchronous and progressive:

```text
query
→ logical join tree
→ selectivity/cost estimates
→ bounded async shard requests
→ streaming/semi-joins
→ spill-to-disk intermediates
→ adaptive reprioritisation
→ progressive results
```

Priority should favour expected join-space reduction per fetch cost. The
planner must use bounded concurrency, cancellation, cache reuse, and explicit
coverage watermarks. It should not claim a globally optimal static join tree:
observed shard selectivity may change the plan.

This is a follow-on to the first six steps, not a prerequisite for the initial
WD/ITIR/SL integration. Smaller or query-oriented shards, route indexes, cache
metrics, and cold/hot performance benchmarks should be selected from measured
workloads rather than assumed globally optimal shard sizes.
