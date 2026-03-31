# NotebookLM Run Loader Component

Date: 2026-03-31

## Change Class

Standard change.

## Problem

NotebookLM reporting surfaces still duplicated runs-root resolution and dated
artifact lookup policy in:

- `SensibLaw/src/reporting/notebooklm_observer.py`
- `SensibLaw/src/reporting/notebooklm_activity.py`

## Requirement

Create one shared Python owner for NotebookLM run-root resolution and dated
artifact discovery, while leaving row parsing and reporting logic in each
surface.

## Component Boundary

Shared owner:

- `SensibLaw/src/reporting/notebooklm_run_loader.py`

First adopters:

- `SensibLaw/src/reporting/notebooklm_observer.py`
- `SensibLaw/src/reporting/notebooklm_activity.py`

Promoted slice:

- runs-root resolution
- date-directory validation
- dated artifact discovery for observer logs
- dated artifact discovery for activity outputs

## Acceptance

- observer and activity import the shared run loader
- dated artifact filtering remains stable
- focused shared-loader tests cover both path shapes

## Quality Gate

Run from `SensibLaw/`:

- `../.venv/bin/python -m pytest -q tests/test_notebooklm_run_loader.py tests/test_notebooklm_observer.py tests/test_notebooklm_activity.py`

## C4 / PlantUML

```plantuml
@startuml
title NotebookLM Run Loader Component

Component(observer, "notebooklm_observer.py", "Observer report adopter")
Component(activity, "notebooklm_activity.py", "Activity report adopter")
Component(loader, "notebooklm_run_loader.py", "Shared runs-root and date-file loader")

Rel(observer, loader, "uses observer file lookup")
Rel(activity, loader, "uses activity file lookup")

@enduml
```
