# Wiki Revision Pack Storage Component

Date: 2026-03-31

## Change Class

Standard change.

## Problem

The Wikipedia revision-pack runner still owned low-level artifact naming and
JSON storage policy inline. That made the runner responsible for both
orchestration and storage mechanics in:

- `SensibLaw/src/wiki_timeline/revision_pack_runner.py`

## Requirement

Create one shared Python owner for revision-pack artifact naming and JSON IO,
while leaving SQLite persistence and run orchestration in the runner.

## Component Boundary

Shared owner:

- `SensibLaw/src/wiki_timeline/revision_pack_storage.py`

First adopter:

- `SensibLaw/src/wiki_timeline/revision_pack_runner.py`

Promoted slice:

- stable JSON serialization for manifest hashing
- artifact slugging
- revision artifact path shaping
- pair artifact path shaping
- contested graph artifact path shaping
- JSON read/write helpers
- default output directory shaping

## Acceptance

- `revision_pack_runner.py` imports the shared storage owner
- storage helper tests pin artifact-path and JSON behavior
- existing revision-pack runner regressions stay green
- SQLite schema and run-state behavior remain in the runner

## Quality Gate

Run from `SensibLaw/`:

- `../.venv/bin/python -m pytest -q tests/test_revision_pack_storage.py tests/test_wiki_revision_pack_runner.py`

## C4 / PlantUML

```plantuml
@startuml
title Wiki Revision Pack Storage Component

Component(runner, "revision_pack_runner.py", "Revision-pack orchestration")
Component(storage, "revision_pack_storage.py", "Artifact naming and JSON IO")

Rel(runner, storage, "uses artifact-path and JSON helpers")

@enduml
```
