# Wikidata Structural Handoff V1 (2026-03-25)

## Purpose
Record the first checked wiki/Wikidata handoff artifact at the same legibility
level as the current GWB and AU checked handoffs.

This artifact is not a broad ontology-cleanup claim. It is a bounded reviewed
handoff over already-pinned repo fixtures that shows:

- what the repo can already recover and preserve from Wikidata structural review
- what is already strong enough to hand off as checked structure
- what remains explicitly held as review pressure rather than promoted truth

Related surfaces:
- `docs/planning/wikidata_zelph_single_handoff_20260325.md`
- `SensibLaw/docs/wikidata_working_group_status.md`
- `docs/planning/wikidata_hotspot_benchmark_lane_20260325.md`
- `docs/planning/wikidata_p2738_disjointness_lane_20260325.md`

## Scope
One checked structural handoff artifact now exists:

- output directory:
  `SensibLaw/tests/fixtures/zelph/wikidata_structural_handoff_v1/`
- files:
  - `wikidata_structural_handoff_v1.slice.json`
  - `wikidata_structural_handoff_v1.summary.md`
  - `wikidata_structural_handoff_v1.facts.zlp`
  - `wikidata_structural_handoff_v1.rules.zlp`
  - `wikidata_structural_handoff_v1.engine.json`
  - `wikidata_structural_handoff_v1.scorecard.json`

Validation:
- `cd /home/c/Documents/code/ITIR-suite/SensibLaw && ../.venv/bin/pytest -q tests/test_wikidata_structural_handoff.py`
- `cd /home/c/Documents/code/ITIR-suite && python SensibLaw/scripts/build_wikidata_structural_handoff.py`

## Bounded input set
The handoff should stay pinned to existing repo-owned artifacts only.

### Qualifier core
- importer-backed baseline:
  `SensibLaw/tests/fixtures/wikidata/real_qualifier_imported_slice_20260307.json`
- repo-pinned real drift case:
  `SensibLaw/tests/fixtures/wikidata/q100104196_p166_2277985537_2277985693/slice.json`
- paired report:
  `SensibLaw/tests/fixtures/wikidata/q100104196_p166_2277985537_2277985693/projection.json`

Reason:
- this is the most handoff-ready already-checked slice in the repo's
  wiki/Wikidata lane
- it gives both sides of the story in one bounded surface:
  importer-backed stable baseline and a pinned real anomaly with persisted
  projection output

### Hotspot exemplar packs
- `docs/planning/wikidata_hotspot_pilot_pack_v1.manifest.json`
- promoted packs to include:
  - `mixed_order_live_pack_v1`
  - `p279_scc_live_pack_v1`
  - `qualifier_drift_p166_live_pack_v1`
- one held/promotable review pack to include:
  - `software_entity_kind_collapse_pack_v0`

Reason:
- the first three are already manifest-promoted and legible
- the software pack is a clean held example that preserves review pressure
  instead of pretending every useful case is already promoted

### Disjointness exemplar cases
- baseline:
  `SensibLaw/tests/fixtures/wikidata/disjointness_p2738_nucleon_real_pack_v1/slice.json`
- subclass contradiction:
  `SensibLaw/tests/fixtures/wikidata/disjointness_p2738_fixed_construction_real_pack_v1/slice.json`
- instance contradiction:
  `SensibLaw/tests/fixtures/wikidata/disjointness_p2738_working_fluid_real_pack_v1/slice.json`

Reason:
- together they show zero-violation baseline, real subclass contradiction, and
  real instance contradiction without needing live query execution

## Intended artifact shape
The slice should expose three surfaces:

### 1. Qualifier baseline and real drift
- importer-backed stable baseline
- one pinned real anomaly with persisted projection
- bounded explanation of what changed and what did not

### 2. Checked structural exemplars
- promoted hotspot packs
- key cluster counts
- small sample query/question surfaces

### 3. Explicit review pressure
- held/promotable hotspot packs
- real contradiction cases
- contradiction counts and culprit counts

## Human-readable summary contract
The summary must be readable by:

- the Zelph developer
- the Wikidata Ontology Working Group
- a technically literate reader who does not want to read raw JSON first

It should explain, in plain language:

- what the checked slice proves
- what is still only a review surface
- why the software/GNU pack is held rather than promoted
- why the import baseline matters

## Zelph/query surface
The `.zlp` surface should support two fixed questions:

1. Which structural cases are already ready for checked handoff?
2. Which structural cases remain review-worthy because of governance hold or
   contradiction pressure?

The first fixed rule families should therefore derive:

- `structural_case_ready_for_handoff`
- `needs_review_due_to_structure`
- `needs_review_due_to_governance`
- `demonstrates_import_preservation`

## Scorecard contract
The scorecard should report at least:

- `destination = "checked_wikidata_structural_understanding"`
- `current_stage = "checked_structural_handoff_checkpoint"`
- promoted hotspot pack count
- held/promotable hotspot pack count
- contradiction-bearing disjointness case count
- zero-violation baseline case count
- import baseline statement count
- Zelph engine status

## Governance
- use pinned fixtures and reports only
- no live WDQS execution in the handoff build
- preserve the boundary between:
  - promoted structural exemplars
  - held/promotable review surfaces
  - importer-backed baseline evidence
- do not present the artifact as full Wikidata parity or ontology cleanup

## Non-goals
- no broad benchmark regeneration pass
- no new live candidate discovery
- no expansion into full pack `v1.7` yet
- no claim that this artifact replaces the more detailed working-group status
  note

## Success criteria
This slice is successful if:

- the repo now has one concrete checked wiki/Wikidata handoff directory
- the summary is human-legible without opening JSON first
- the scorecard and ZLP outputs match the checked-handoff shape used by GWB/AU
- the artifact strengthens collaboration readability without overstating parity

Current result:
- implemented with focused validation passing
- scorecard currently reports:
  - `promoted_hotspot_pack_count = 3`
  - `held_hotspot_pack_count = 1`
  - `hotspot_cluster_count = 19`
  - `disjointness_case_count = 3`
  - `contradiction_case_count = 2`
  - `zero_violation_baseline_case_count = 1`
  - `qualifier_baseline_statement_count = 8`
