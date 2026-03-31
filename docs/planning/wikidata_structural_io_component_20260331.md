# Wikidata Structural IO Component

Date: 2026-03-31

## Change Class

Standard change.

## Problem

The Wikidata structural handoff and review family still duplicated low-level IO
policy across multiple builders:

- `SensibLaw/scripts/build_wikidata_structural_handoff.py`
- `SensibLaw/scripts/build_wikidata_structural_review.py`
- `SensibLaw/scripts/build_wikidata_dense_structural_review.py`

The duplicated logic covered:

- repo-relative path rendering for source artifacts
- JSON payload loading from pinned fixture paths
- output artifact emission for JSON and markdown files

## Requirement

Create one shared Python owner for Wikidata structural IO policy so the
builders keep only structural review semantics and artifact content shaping.

## Component Boundary

Shared owner:

- `SensibLaw/src/policy/wikidata_structural_io.py`

Adopters:

- `SensibLaw/scripts/build_wikidata_structural_handoff.py`
- `SensibLaw/scripts/build_wikidata_structural_review.py`
- `SensibLaw/scripts/build_wikidata_dense_structural_review.py`

## Acceptance

- builders import the shared relative-path and JSON-loader helpers
- checked and dense review builders use the shared JSON+markdown artifact writer
- focused tests cover the shared owner and the three adopters

## Quality Gate

Run from `SensibLaw/`:

- `../.venv/bin/python -m pytest -q tests/test_wikidata_structural_io.py tests/test_wikidata_structural_handoff.py tests/test_wikidata_structural_review.py tests/test_wikidata_dense_structural_review.py`

## C4 / PlantUML

```plantuml
@startuml
title Wikidata Structural IO Component

Component(handoff, "build_wikidata_structural_handoff.py", "Handoff adopter")
Component(checked, "build_wikidata_structural_review.py", "Checked review adopter")
Component(dense, "build_wikidata_dense_structural_review.py", "Dense review adopter")
Component(io, "wikidata_structural_io.py", "Shared IO policy")

Rel(handoff, io, "uses")
Rel(checked, io, "uses")
Rel(dense, io, "uses")

@enduml
```
