# Reporting Text Unit Builder Component

Date: 2026-03-31

## Change Class

Standard change.

## Problem

The handoff-import loader family still duplicated low-level `TextUnit` shaping
across multiple loaders:

- `SensibLaw/src/fact_intake/messenger_export_import.py`
- `SensibLaw/src/fact_intake/google_public_import.py`
- `SensibLaw/src/reporting/structure_report.py`
- `SensibLaw/src/reporting/openrecall_import.py`

The duplicated logic covered:

- indexed `TextUnit` construction
- timestamped speaker line rendering
- header/body text composition

## Requirement

Create one shared Python owner for reusable `TextUnit` builders so loader
surfaces keep only source-specific extraction and filtering policy.

## Component Boundary

Shared owner:

- `SensibLaw/src/reporting/text_unit_builders.py`

Adopters:

- `SensibLaw/src/fact_intake/messenger_export_import.py`
- `SensibLaw/src/fact_intake/google_public_import.py`
- `SensibLaw/src/reporting/structure_report.py`
- `SensibLaw/src/reporting/openrecall_import.py`

## Acceptance

- loader surfaces import the shared text-unit builders
- timestamped speaker text stays stable
- OpenRecall header/body shaping stays stable
- focused tests cover the shared owner and key adopters

## Quality Gate

Run from `SensibLaw/`:

- `../.venv/bin/python -m pytest -q tests/test_reporting_text_unit_builders.py tests/test_personal_messenger_export_import.py tests/test_google_public_import.py tests/test_personal_openrecall_import.py tests/test_structure_report.py`

## C4 / PlantUML

```plantuml
@startuml
title Reporting Text Unit Builder Component

Component(messenger, "messenger_export_import.py", "Loader adopter")
Component(google, "google_public_import.py", "Loader adopter")
Component(structure, "structure_report.py", "Loader adopter")
Component(openrecall, "openrecall_import.py", "Loader adopter")
Component(builders, "text_unit_builders.py", "Shared TextUnit builder")

Rel(messenger, builders, "uses")
Rel(google, builders, "uses")
Rel(structure, builders, "uses")
Rel(openrecall, builders, "uses")

@enduml
```
