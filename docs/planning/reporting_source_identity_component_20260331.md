# Reporting Source Identity Component

Date: 2026-03-31

## Change Class

Standard change.

## Problem

After normalizing loader-side `TextUnit` shaping, the importer family still
duplicated source-identity and timestamp policy across multiple adopters:

- `SensibLaw/src/fact_intake/messenger_export_import.py`
- `SensibLaw/src/fact_intake/google_public_import.py`
- `SensibLaw/src/reporting/openrecall_import.py`

The duplicated logic covered:

- deterministic hashed source IDs
- Google public source-id formatting
- UTC timestamp rendering from millisecond exports
- local timestamp/date derivation for persisted capture rows
- OpenRecall capture-id construction

## Requirement

Create one shared Python owner for importer-side source identity and timestamp
policy so loader surfaces keep only extraction and source-specific filtering
behavior.

## Component Boundary

Shared owner:

- `SensibLaw/src/reporting/source_identity.py`

Adopters:

- `SensibLaw/src/fact_intake/messenger_export_import.py`
- `SensibLaw/src/fact_intake/google_public_import.py`
- `SensibLaw/src/reporting/openrecall_import.py`

## Acceptance

- Messenger import uses the shared hashed source-id and UTC timestamp helpers
- Google public import uses the shared source-id formatter
- OpenRecall import uses the shared capture-id and local timestamp/date helpers
- focused tests cover the shared owner and key adopters

## Quality Gate

Run from `SensibLaw/`:

- `../.venv/bin/python -m pytest -q tests/test_reporting_source_identity.py tests/test_personal_messenger_export_import.py tests/test_google_public_import.py tests/test_personal_openrecall_import.py`

## C4 / PlantUML

```plantuml
@startuml
title Reporting Source Identity Component

Component(messenger, "messenger_export_import.py", "Loader adopter")
Component(google, "google_public_import.py", "Loader adopter")
Component(openrecall, "openrecall_import.py", "Loader adopter")
Component(identity, "source_identity.py", "Shared source identity policy")

Rel(messenger, identity, "uses")
Rel(google, identity, "uses")
Rel(openrecall, identity, "uses")

@enduml
```
