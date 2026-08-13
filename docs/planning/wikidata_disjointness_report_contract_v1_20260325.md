# Wikidata Disjointness Report Contract `v1` (2026-03-25)

## Purpose
Freeze the first deterministic report contract for the standalone `P2738`
disjointness lane so implementation and review can proceed without reopening the
JSON shape.

## Scope
This contract applies to:

- `SensibLaw/src/ontology/wikidata_disjointness.py`
- `sensiblaw wikidata disjointness-report`

It does not yet imply:

- live-query execution
- hotspot-family promotion
- full parity with Ege/Peter's broader disjointness methodology

Related but distinct candidate-discovery surfaces now exist:

- `SensibLaw/scripts/run_wikidata_disjointness_candidate_scan.py`
  - supports `--backend wdqs`
  - supports `--backend zelph`
- `SensibLaw/data/ontology/wikidata_disjointness_pair_seed_v1.json`
  - current explicit seed surface for local `zelph` instance scans

## Promotion ladder policy
The disjointness lane now uses the same readiness language as the hotspot lane,
but only at the docs/governance layer.

Readiness states:

- `candidate`
- `anchored`
- `promotable`
- `promoted`

Hold reasons for non-promoted cases should use the same vocabulary as the
hotspot lane where applicable:

- `unclear_family`
- `unclear_conflict_surface`
- `page_only_not_fixture_backed`
- `good_neighborhood_bad_pathology_identity`
- `needs_predicate_narrowing`
- `insufficient_bounded_evidence`
- `not_reviewer_legible`

Important:

- `wikidata_disjointness_report/v1` remains observational
- promotion metadata does not belong in the report JSON itself
- readiness is now tracked in:
  - `docs/planning/wikidata_disjointness_case_index_v1.json`

## Input boundary
`v1` consumes one bounded Wikidata slice in the same broad `windows[]` /
`statement_bundles[]` style already used by the existing Wikidata projection
lane.

Current required semantics:

- exactly one window
- non-deprecated statements only
- supported properties:
  - `P2738`
  - `P11260`
  - `P279`
  - `P31`

This remains separate from candidate discovery:

- report input:
  - bounded pinned slice
- candidate scan input:
  - live WDQS rows, or
  - local `zelph` plus explicit disjoint-pair seeds

## Output schema
Top-level output:

```json
{
  "schema_version": "wikidata_disjointness_report/v1",
  "source_window_id": "t1",
  "bounded_slice": {
    "properties": ["P2738", "P11260", "P279", "P31"],
    "active_statement_count": 7
  },
  "disjoint_pairs": [],
  "subclass_violation_count": 0,
  "instance_violation_count": 0,
  "subclass_violations": [],
  "instance_violations": [],
  "culprit_classes": [],
  "culprit_items": [],
  "review_summary": {
    "disjoint_pair_count": 0,
    "subclass_violation_count": 0,
    "instance_violation_count": 0,
    "culprit_class_count": 0,
    "culprit_item_count": 0
  }
}
```

## Field meanings

### `disjoint_pairs[]`
One entry per extracted pairwise disjoint class pair.

Required fields:

- `pair_id`
- `holder_qid`
- `holder_label`
- `left_qid`
- `left_label`
- `right_qid`
- `right_label`
- `statement_value`
- `qualifier_pid`
- `property_pid`

### `subclass_violations[]`
One entry per violating class in the bounded local `P279` closure.

Required fields:

- `qid`
- `label`
- `pair_key`
- `left_qid`
- `left_label`
- `right_qid`
- `right_label`
- `holder_qid`
- `holder_label`
- `direct_parents`
- `ancestor_classes`

### `instance_violations[]`
One entry per violating item in the bounded local `P31` + `P279` closure.

Required fields:

- `qid`
- `label`
- `pair_key`
- `left_qid`
- `left_label`
- `right_qid`
- `right_label`
- `holder_qid`
- `holder_label`
- `direct_instance_of`
- `inferred_classes`

### `culprit_classes[]`
Subset of `subclass_violations[]`.

`v1` culprit rule:
- the class is itself a subclass violation
- none of its direct parents inside the bounded slice are also violations for
  the same disjoint pair
- emit downstream impact detail:
  - `downstream_subclass_violation_count`
  - `downstream_instance_violation_count`

### `culprit_items[]`
Subset of `instance_violations[]`.

`v1` culprit rule:
- the item is an instance violation
- none of its direct asserted `instance of` classes are already subclass
  violations for the same disjoint pair
- emit `explained_by_culprit_class_qid` on instance rows when a culprit class
  already explains the contradiction

## Example output
Example from the bounded synthetic pilot pack:

```json
{
  "schema_version": "wikidata_disjointness_report/v1",
  "source_window_id": "t1",
  "bounded_slice": {
    "properties": ["P2738", "P11260", "P279", "P31"],
    "active_statement_count": 7
  },
  "disjoint_pairs": [
    {
      "pair_id": "QTransportFamily:QLandMode:QWaterMode",
      "holder_qid": "QTransportFamily",
      "holder_label": "transport family",
      "left_qid": "QLandMode",
      "left_label": "land transport mode",
      "right_qid": "QWaterMode",
      "right_label": "water transport mode",
      "statement_value": "QTransportMode",
      "qualifier_pid": "P11260",
      "property_pid": "P2738"
    }
  ],
  "subclass_violation_count": 2,
  "instance_violation_count": 2,
  "subclass_violations": [
    {
      "qid": "QAmphibiousVehicle",
      "label": "amphibious vehicle",
      "pair_key": "QLandMode|QWaterMode",
      "left_qid": "QLandMode",
      "left_label": "land transport mode",
      "right_qid": "QWaterMode",
      "right_label": "water transport mode",
      "holder_qid": "QTransportFamily",
      "holder_label": "transport family",
      "direct_parents": ["QLandMode", "QWaterMode"],
      "ancestor_classes": ["QAmphibiousVehicle", "QLandMode", "QWaterMode"]
    }
  ],
  "instance_violations": [
    {
      "qid": "QJetSkiCar",
      "label": "jet ski car",
      "pair_key": "QLandMode|QWaterMode",
      "left_qid": "QLandMode",
      "left_label": "land transport mode",
      "right_qid": "QWaterMode",
      "right_label": "water transport mode",
      "holder_qid": "QTransportFamily",
      "holder_label": "transport family",
      "direct_instance_of": ["QLandMode", "QWaterMode"],
      "inferred_classes": ["QLandMode", "QWaterMode"]
    }
  ],
  "culprit_classes": [
    {
      "qid": "QAmphibiousVehicle",
      "label": "amphibious vehicle",
      "pair_key": "QLandMode|QWaterMode",
      "left_qid": "QLandMode",
      "left_label": "land transport mode",
      "right_qid": "QWaterMode",
      "right_label": "water transport mode",
      "holder_qid": "QTransportFamily",
      "holder_label": "transport family",
      "direct_parents": ["QLandMode", "QWaterMode"],
      "ancestor_classes": ["QAmphibiousVehicle", "QLandMode", "QWaterMode"]
    }
  ],
  "culprit_items": [
    {
      "qid": "QJetSkiCar",
      "label": "jet ski car",
      "pair_key": "QLandMode|QWaterMode",
      "left_qid": "QLandMode",
      "left_label": "land transport mode",
      "right_qid": "QWaterMode",
      "right_label": "water transport mode",
      "holder_qid": "QTransportFamily",
      "holder_label": "transport family",
      "direct_instance_of": ["QLandMode", "QWaterMode"],
      "inferred_classes": ["QLandMode", "QWaterMode"]
    }
  ],
  "review_summary": {
    "disjoint_pair_count": 1,
    "subclass_violation_count": 2,
    "instance_violation_count": 2,
    "culprit_class_count": 1,
    "culprit_item_count": 1
  }
}
```

## Lane decision
For now, disjointness remains a sibling lane, not a hotspot family.

Reason:

- `P2738` disjointness is now implemented, but only at bounded `v1` scope
- the hotspot lane is already a separate benchmark/evaluator surface
- premature merging would blur two different review questions:
  - "is this a structural hotspot worth cluster generation?"
  - "is this a disjointness contradiction worth direct ontology review?"

## Promotion gate for later hotspot integration
Only revisit hotspot integration after:

1. at least two real Wikidata-backed disjointness packs exist
2. the `wikidata_disjointness_report/v1` contract remains stable across them
3. we can define a non-hand-wavy hotspot-family contract for disjointness
4. reviewer usefulness is demonstrated beyond the synthetic pilot

Until then:

- keep disjointness report-first
- keep hotspot generation separate
- use disjointness findings as optional upstream candidate signals only

## Current scan backend boundary
The repo now has a real candidate-discovery backend split, but the local
`zelph` lane is still intentionally narrower than the WDQS lane:

- supported now:
  - `wdqs` backend for live subclass and instance scans
  - `zelph` backend for local instance scans from explicit pair seeds
- not yet claimed:
  - direct `P2738` qualifier mining from local `.bin` imports
  - local subclass-contradiction parity over `P279+`

That boundary should remain explicit until released zelph support catches up.

## Current case classifications
- synthetic pilot contradiction pack:
  - `promotable`
  - rationale: deterministic, fixture-backed, reviewer-legible, but not yet
    ratified as a promoted benchmark/report staple
- real nucleon baseline pack:
  - `anchored`
  - hold reason: `awaiting_additional_real_disjointness_packs`
- real fixed-construction contradiction pack:
  - `promotable`
  - hold reason: `awaiting_manifest_promotion`
- real working-fluid instance contradiction pack:
  - `promotable`
  - hold reason: `awaiting_manifest_promotion`
- broader disjointness ambitions beyond current packs:
  - `candidate`
  - hold reason: `insufficient_bounded_evidence`
