# Wikidata Structural Geometry Component

Date: 2026-03-31

## Change Class

Standard change.

## Problem

After normalizing Wikidata queue policy and low-level IO policy, the checked and
dense structural review builders still duplicated source-row and cue-building
geometry. The clearest overlaps are qualifier-drift, hotspot, and disjointness
slices in:

- `SensibLaw/scripts/build_wikidata_structural_review.py`
- `SensibLaw/scripts/build_wikidata_dense_structural_review.py`

## Requirement

Create one shared Python owner for Wikidata structural row and cue geometry,
starting with qualifier-drift, then hotspot, then disjointness overlap.

## Component Boundary

Shared owner:

- `SensibLaw/src/policy/wikidata_structural_geometry.py`

First adopters:

- `SensibLaw/scripts/build_wikidata_structural_review.py`
- `SensibLaw/scripts/build_wikidata_dense_structural_review.py`

Promoted slices:

- checked qualifier-drift source row
- checked qualifier-drift cue fanout
- dense qualifier-drift source row
- dense qualifier-drift cue fanout
- checked hotspot summary/question rows and cue fanout
- dense hotspot summary/focus/family rows and cue fanout
- checked disjointness rows and cue fanout
- dense disjointness rows and cue fanout

## Acceptance

- checked and dense builders import the shared qualifier-drift, hotspot, and
  disjointness helpers
- row shape and cue shape stay stable
- focused shared-geometry tests cover both variants
- existing checked and dense review regressions stay green

## Quality Gate

Run from `SensibLaw/`:

- `../.venv/bin/python -m pytest -q tests/test_wikidata_structural_geometry.py tests/test_wikidata_structural_review.py tests/test_wikidata_dense_structural_review.py`

## C4 / PlantUML

```plantuml
@startuml
title Wikidata Structural Geometry Component

Component(checked, "build_wikidata_structural_review.py", "Checked review adopter")
Component(dense, "build_wikidata_dense_structural_review.py", "Dense review adopter")
Component(geometry, "wikidata_structural_geometry.py", "Shared row and cue geometry")

Rel(checked, geometry, "uses qualifier-drift, hotspot, and disjointness helpers")
Rel(dense, geometry, "uses qualifier-drift, hotspot, and disjointness helpers")

@enduml
```
