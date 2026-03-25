# Wikidata Hotspot Pack Contract (2026-03-25)

## Purpose
Define the first draft pack/schema/generator/evaluator contract for the
Wikidata hotspot benchmark lane.

This contract is planning-first. It exists to prevent benchmark-generation code
from drifting ahead of:

- hotspot taxonomy
- pack manifest shape
- provenance requirements
- evaluator/report boundaries

The benchmark lane should reuse the repo's existing deterministic Wikidata
surfaces instead of inventing a parallel ontology pipeline.

## Relationship to existing repo contracts
This contract extends, but does not replace:

- `SensibLaw/docs/wikidata_report_contract_v0_1.md`
- `SensibLaw/docs/planning/wikidata_transition_plan_20260306.md`
- `docs/planning/wikidata_hotspot_benchmark_lane_20260325.md`
- existing Wikidata fixture/report pairs under
  `SensibLaw/tests/fixtures/wikidata/`

The hotspot pack lane sits above the current projection/report lane:

- projection/report lane:
  turns bounded Wikidata slices into deterministic diagnostics
- hotspot pack lane:
  selects high-yield diagnostic regions and turns them into benchmark-ready
  test-cluster packs

## Core stance
- hotspot packs are reviewer-facing and benchmark-facing
- they remain bounded and deterministic
- they preserve why a hotspot was selected
- they do not flatten away structural pathology too early
- they do not prescribe ontology repair

## Hotspot taxonomy

### 1. `mixed_order`
Signal:
- same QID participates materially in both `P31` and `P279`

Primary evidence:
- `mixed_order_nodes[]` in the projected report

Typical benchmark families:
- `edge_yes`
- `edge_inv`
- `hierarchy`

### 2. `entity_kind_collapse`
Signal:
- one item is carrying incompatible roles at once:
  artifact, project, category, service, product, community, class

Primary evidence:
- explicit item-page statement pattern review
- later fixture-backed slice/report when local capture exists

Typical benchmark families:
- `edge_yes`
- `edge_inv`
- `kind_disambiguation`
- `property_inheritance`

### 3. `p279_scc`
Signal:
- reciprocal or cyclic `P279` structure

Primary evidence:
- `p279_sccs[]` in the projected report

Typical benchmark families:
- `edge_yes`
- `edge_inv`
- `hierarchy`
- `closure_conflict`

### 4. `property_constraint_pressure`
Signal:
- subject/value restrictions or neighboring property choices imply conflicting
  conceptualization

Primary evidence:
- property/constraint review note
- bounded slice and later projected diagnostics

Typical benchmark families:
- `property_inheritance`
- `constraint_scenario`

### 5. `qualifier_drift`
Signal:
- same `(subject, property)` slot changes qualifier signature or qualifier
  property set across windows/revisions

Primary evidence:
- `qualifier_drift[]` in the projected report

Typical benchmark families:
- `temporalized_statement`
- `revision_pair_agreement`
- `property_inheritance`

### 6. `typed_parthood_ambiguity`
Signal:
- parthood edges exist but endpoint typing leaves the semantic reading
  underdetermined

Primary evidence:
- `parthood_typing`

Typical benchmark families:
- `edge_yes`
- `inverse_validity`
- `type_sensitive_inheritance`

## Draft manifest schema
Use a simple deterministic JSON manifest.

Top-level required fields:
- `version`
- `date`
- `selection_policy`
- `entries[]`

### `selection_policy`
Required fields:
- `priority_order[]`
- `real_first`
- `allow_page_locked_candidates_without_local_slice`
- `require_provenance_receipts`

### `entries[]`
Each hotspot pack entry must include:
- `pack_id`
- `status`
- `promotion_status`
- `hotspot_family`
- `primary_story`
- `source_kind`
- `focus_qids[]`
- `focus_pids[]`
- `source_artifacts[]`
- `candidate_cluster_families[]`
- `selection_reason`
- `expected_value`
- `commands[]`

Optional fields:
- `hold_reason`
- `report_artifacts[]`
- `focus_revisions`
- `notes[]`

### Field guidance
- `pack_id`
  - stable, short, lower_snake_case
- `status`
  - provenance/backing state only
  - one of:
    - `fixture_backed`
    - `report_backed`
    - `page_locked_candidate`
    - `planned_only`
- `promotion_status`
  - readiness state only
  - one of:
    - `candidate`
    - `anchored`
    - `promotable`
    - `promoted`
- `hold_reason`
  - required when `promotion_status != promoted`
  - omitted when `promotion_status == promoted`
  - examples:
    - `unclear_family`
    - `unclear_conflict_surface`
    - `page_only_not_fixture_backed`
    - `good_neighborhood_bad_pathology_identity`
    - `needs_predicate_narrowing`
    - `insufficient_bounded_evidence`
    - `not_reviewer_legible`
- `hotspot_family`
  - one of the taxonomy keys above
- `primary_story`
  - short human reason the pack matters
- `source_kind`
  - one of:
    - `repo_fixture`
    - `repo_fixture_plus_report`
    - `page_review`
    - `revision_pair`
- `focus_qids[]`
  - principal item IDs
- `focus_pids[]`
  - principal properties relevant to the hotspot
- `source_artifacts[]`
  - repo-local inputs, slices, notes, or source pages
- `candidate_cluster_families[]`
  - benchmark cluster types this hotspot should generate
- `selection_reason`
  - one-sentence bounded justification
- `expected_value`
  - why this pack improves the benchmark lane
- `commands[]`
  - deterministic inspect/test/rebuild commands when available

## Ratified hotspot pack manifest
See:
- `docs/planning/wikidata_hotspot_pilot_pack_v1.manifest.json`

The pilot manifest is now ratified for `v1`. It intentionally keeps the
existing per-pack ids stable even where some ids still end in `_v0`; the
promotion happened at the manifest/contract level, not by forcing a pack-id
renaming pass.

Important:

- `status` and `promotion_status` are different axes
- `status` answers "what backing/provenance state is this pack in?"
- `promotion_status` answers "how ready is this pack for benchmark/report use?"

- `mixed_order_live_pack_v1`
- `p279_scc_live_pack_v1`
- `qualifier_drift_p166_live_pack_v1`
- `finance_entity_kind_collapse_pack_v0`
- `software_entity_kind_collapse_pack_v0`

## First emitted cluster-pack schema
The first generated output should be a deterministic JSON object with:

- `schema_version`
- `manifest_version`
- `selection_policy`
- `selected_pack_ids[]`
- `pack_count`
- `cluster_count`
- `packs[]`

### `packs[]`
Each emitted pack should include:

- `pack_id`
- `status`
- `promotion_status`
- `hold_reason`
- `hotspot_family`
- `primary_story`
- `focus_qids[]`
- `focus_pids[]`
- `source_artifacts[]`
- `candidate_cluster_families[]`
- `cluster_count`
- `clusters[]`

### `clusters[]`
Each emitted cluster should include:

- `cluster_id`
- `cluster_family`
- `expected_polarity`
- `supporting_hotspot_family`
- `subject_qid`
- `subject_label`
- `object_qid`
- `object_label`
- `relation_label`
- `relation_variant`
- `questions[]`
- `evidence`

### `questions[]`
Each emitted question should include:

- `question_id`
- `text`

Current emitted `cluster_family` values in the minimal generator:

- `edge_yes`
- `hierarchy`
- `closure_conflict`
- `temporalized_statement`
- `kind_disambiguation`
- `property_inheritance`

## First five candidate hotspot packs

### 1. `mixed_order_live_pack_v1`
- family: `mixed_order`
- focus QIDs:
  - `Q9779`
  - `Q8192`
  - `Q21169592`
  - `Q7187`
- current backing:
  - `SensibLaw/tests/fixtures/wikidata/live_p31_p279_slice_20260307.json`
- current signal:
  - repo fixture + report path already demonstrates mixed-order nodes

### 2. `p279_scc_live_pack_v1`
- family: `p279_scc`
- focus QIDs:
  - `Q22652`
  - `Q22698`
  - `Q52040`
  - `Q188`
- current backing:
  - `SensibLaw/tests/fixtures/wikidata/live_p31_p279_slice_20260307.json`
- current signal:
  - repo fixture + report path already demonstrates SCC neighborhoods

### 3. `qualifier_drift_p166_live_pack_v1`
- family: `qualifier_drift`
- focus QIDs:
  - `Q100104196`
- focus PIDs:
  - `P166`
- current backing:
  - `SensibLaw/tests/fixtures/wikidata/q100104196_p166_2277985537_2277985693/slice.json`
  - `SensibLaw/tests/fixtures/wikidata/q100104196_p166_2277985537_2277985693/projection.json`
- current signal:
  - repo-pinned revision-pair qualifier drift with medium severity

### 4. `finance_entity_kind_collapse_pack_v0`
- family: `entity_kind_collapse`
- focus QIDs:
  - `Q15809678`
  - `Q837171`
  - `Q2424752`
- focus PIDs:
  - `P31`
  - `P279`
- current backing:
  - `SensibLaw/tests/fixtures/wikidata/finance_entity_kind_collapse_pack_v0/slice.json`
- current signal:
  - product/service/category entanglement plus deprecated-rank governance clue

### 5. `software_entity_kind_collapse_pack_v0`
- family: `entity_kind_collapse`
- focus QIDs:
  - `Q44571`
  - `Q7598`
- focus PIDs:
  - `P31`
  - `P279`
  - `P527`
- current backing:
  - `SensibLaw/tests/fixtures/wikidata/software_entity_kind_collapse_pack_v0/slice.json`
- current signal:
  - artifact/project/community/class collapse in a domain that is easy to read

## Generator architecture sketch
Implemented first slice:

- `SensibLaw/src/ontology/wikidata_hotspot.py`
- `sensiblaw wikidata hotspot-generate-clusters`

### Inputs
- hotspot pack manifest entry
- source artifact(s):
  - repo slice JSON
  - projected report JSON

### Stages
1. `select_hotspot_pack`
   - choose manifest entry or entry subset
2. `load_hotspot_evidence`
   - load slices/reports/page metadata
3. `derive_cluster_candidates`
   - derive cluster rows based on hotspot family rules
4. `materialize_cluster_pack`
   - emit deterministic JSON pack
5. `emit_summary`
   - emit compact reviewer-facing summary

### Proposed module boundaries
- existing reuse target:
  - `SensibLaw/src/ontology/wikidata.py`
- first implementation module:
  - `SensibLaw/src/ontology/wikidata_hotspot.py`
- likely later split if the lane grows:
  - `SensibLaw/src/ontology/wikidata_hotspot_manifest.py`
  - `SensibLaw/src/ontology/wikidata_hotspot_clusters.py`
  - `SensibLaw/src/ontology/wikidata_hotspot_eval.py`
- current CLI shape:
  - `sensiblaw wikidata hotspot-generate-clusters`
- likely later CLI additions:
  - `sensiblaw wikidata hotspot-build-pack`
  - `sensiblaw wikidata hotspot-eval`

## Evaluator contract
The evaluator should stay separate from cluster generation.

### Inputs
- generated hotspot cluster pack
- normalized hotspot response bundle

Required response-bundle fields:

- `schema_version = "wikidata_hotspot_responses/v1"`
- `model_run_id`
- `model_id`
- `prompt_profile`
- `responses[]`

Each response row must include:

- `cluster_id`
- `question_id`
- `label`

Optional response-row field:

- `raw_text`

`label` must be one of:

- `yes`
- `no`
- `abstain`

### Outputs
Required top-level fields:
- `schema_version`
- `model_run_id`
- `model_id`
- `prompt_profile`
- `manifest_version`
- `selected_pack_ids[]`
- `cluster_results[]`
- `summary`

### `cluster_results[]`
Required fields:
- `cluster_id`
- `pack_id`
- `cluster_family`
- `expected_polarity`
- `question_results[]`
- `answer_distribution`
- `classification`
- `supporting_hotspot_family`

`classification` should be one of:
- `consistent`
- `inconsistent`
- `incomplete`
- `abstained`

### `summary`
Required fields:
- `cluster_counts`
- `inconsistency_rate`
- `incompleteness_rate`
- `abstention_rate`
- `by_hotspot_family`
- `by_cluster_family`

### Classification rule
- `abstained`
  - every response row for the cluster is `abstain`
- `consistent`
  - at least one non-`abstain` row exists and all non-`abstain` labels equal
    `expected_polarity`
- `incomplete`
  - at least one non-`abstain` row exists and all non-`abstain` labels equal
    the polarity opposite to `expected_polarity`
- `inconsistent`
  - the non-`abstain` labels contain both `yes` and `no`

### Validation rule
- every emitted `question_id` in the cluster pack must have exactly one matching
  response row
- duplicate response rows for the same `question_id` are invalid
- response rows may not reference unknown `cluster_id` or `question_id` values

## Evaluation stance
The evaluator should let us compare against IBM-style work on stronger terms:

- not only whether answers differ
- but whether the failures attach to visible structural pathologies
- and whether the same pathologies transfer across domains

## Current implemented boundary
- the evaluator is intentionally score-only for `v1`
- response normalization happens outside the evaluator
- live model execution is deferred to a later adapter-command extension
- the repo now has both:
  - `sensiblaw wikidata hotspot-generate-clusters`
  - `sensiblaw wikidata hotspot-eval`

## `v2` boundary decision
See:
- `docs/planning/wikidata_hotspot_eval_adapter_boundary_v2_20260325.md`

Current direction:
- keep live execution outside `SensibLaw` by default
- if `v2` is ever added, allow only a thin adapter-command wrapper
- keep provider logic, credentials, and normalization policy outside the
  hotspot evaluator

## Non-goals
- no direct model-running pipeline in `v1`
- no automatic prompt optimization
- no ontology repair suggestions
