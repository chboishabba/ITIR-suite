# Wiki Revision Pack Summary Component

Date: 2026-03-31

## Change Class

Standard change.

## Problem

The revision-pack runner still owned pack-level triage ranking, run-summary
assembly, and human-readable summary rendering inline in:

- `SensibLaw/src/wiki_timeline/revision_pack_runner.py`

That mixed execution orchestration with producer-owned reporting/read-model
geometry.

## Requirement

Create one shared Python owner for revision-pack triage ranking and summary
assembly while leaving fetch, scoring, and SQLite writes in the runner.

## Component Boundary

Shared owner:

- `SensibLaw/src/wiki_timeline/revision_pack_summary.py`

Adopter:

- `SensibLaw/src/wiki_timeline/revision_pack_runner.py`

Promoted slice:

- severity ranking for pack triage
- top changed article ranking
- top pair and section ranking
- contested-graph triage ranking
- run summary payload assembly
- human-readable summary rendering

## Acceptance

- the runner imports the shared summary owner
- focused summary tests cover pack triage and human summary output
- existing revision-pack runner regressions stay green

## Quality Gate

Run from `SensibLaw/`:

- `../.venv/bin/python -m pytest -q tests/test_revision_pack_summary.py tests/test_wiki_revision_pack_runner.py`

## C4 / PlantUML

```plantuml
@startuml
title Wiki Revision Pack Summary Component

Component(runner, "revision_pack_runner.py", "Revision-pack orchestration")
Component(summary, "revision_pack_summary.py", "Pack triage and summary owner")

Rel(runner, summary, "uses triage and summary assembly")

@enduml
```
