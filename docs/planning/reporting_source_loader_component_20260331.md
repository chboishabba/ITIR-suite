# Reporting Source Loader Component

Date: 2026-03-31

## Change Class

Standard change.

## Problem

After normalizing importer-side source identity, the importer family still kept
duplicated loader-entry policy across multiple adopters:

- `SensibLaw/src/fact_intake/messenger_export_import.py`
- `SensibLaw/src/fact_intake/google_public_import.py`
- `SensibLaw/src/reporting/openrecall_import.py`

The duplicated logic covered:

- loader path expansion and canonical resolution
- Messenger export file discovery
- HTTP request-backed text fetch for Google public exports
- timestamped screenshot artifact discovery for OpenRecall imports

## Requirement

Create one shared Python owner for importer-side source loader policy so
adopters keep only source-specific extraction, filtering, and projection.

## Component Boundary

Shared owner:

- `SensibLaw/src/reporting/source_loaders.py`

Adopters:

- `SensibLaw/src/fact_intake/messenger_export_import.py`
- `SensibLaw/src/fact_intake/google_public_import.py`
- `SensibLaw/src/reporting/openrecall_import.py`

## Acceptance

- Messenger import uses the shared path-resolution and export-file discovery
  helpers
- Google public import uses the shared text-fetch helper
- OpenRecall import uses the shared path-resolution and timestamped-artifact
  lookup helpers
- focused tests cover the shared owner and key adopters

## Quality Gate

Run from `SensibLaw/`:

- `../.venv/bin/python -m pytest -q tests/test_reporting_source_loaders.py tests/test_personal_messenger_export_import.py tests/test_google_public_import.py tests/test_personal_openrecall_import.py tests/test_openrecall_integration.py tests/test_google_docs_contested_narrative_review.py`

## C4 / PlantUML

```plantuml
@startuml
title Reporting Source Loader Component

Component(messenger, "messenger_export_import.py", "Loader adopter")
Component(google, "google_public_import.py", "Loader adopter")
Component(openrecall, "openrecall_import.py", "Loader adopter")
Component(loaders, "source_loaders.py", "Shared loader policy")

Rel(messenger, loaders, "uses")
Rel(google, loaders, "uses")
Rel(openrecall, loaders, "uses")

@enduml
```
