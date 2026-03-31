# Fact Intake Handoff Artifact Writer Component

Date: 2026-03-31

## Change Class

Standard change.

## Problem

The fact-intake handoff script family still duplicated artifact emission logic
across multiple entrypoints:

- `SensibLaw/scripts/build_personal_handoff_from_chat_json.py`
- `SensibLaw/scripts/build_personal_handoff_from_messenger_export.py`
- `SensibLaw/scripts/build_personal_handoff_from_google_public.py`
- `SensibLaw/scripts/build_personal_handoff_from_message_db.py`

The duplicated logic covered:

- mode-to-version routing
- summary renderer selection
- normalized/report/summary file emission
- common return payload fields

## Requirement

Create one shared Python owner for handoff artifact writing so the script
entrypoints keep only source-loading and metadata-specific concerns.

## Component Boundary

Shared owner:

- `SensibLaw/src/fact_intake/handoff_artifacts.py`

Adopters:

- `SensibLaw/scripts/build_personal_handoff_from_chat_json.py`
- `SensibLaw/scripts/build_personal_handoff_from_messenger_export.py`
- `SensibLaw/scripts/build_personal_handoff_from_google_public.py`
- `SensibLaw/scripts/build_personal_handoff_from_message_db.py`
- `SensibLaw/scripts/build_personal_handoff_from_openrecall.py`

## Acceptance

- all four scripts import the shared artifact writer
- version selection and summary rendering stay behaviorally stable
- focused tests cover the shared writer and script adopters

## Quality Gate

Run from `SensibLaw/`:

- `../.venv/bin/python -m pytest -q tests/test_fact_intake_handoff_artifacts.py tests/test_personal_chat_import.py tests/test_personal_messenger_export_import.py tests/test_google_public_import.py tests/test_personal_message_db_import.py`

## C4 / PlantUML

```plantuml
@startuml
title Fact Intake Handoff Artifact Writer Component

Component(chat_json, "build_personal_handoff_from_chat_json.py", "Script adopter")
Component(messenger, "build_personal_handoff_from_messenger_export.py", "Script adopter")
Component(google_public, "build_personal_handoff_from_google_public.py", "Script adopter")
Component(message_db, "build_personal_handoff_from_message_db.py", "Script adopter")
Component(writer, "handoff_artifacts.py", "Shared handoff artifact writer")

Rel(chat_json, writer, "uses")
Rel(messenger, writer, "uses")
Rel(google_public, writer, "uses")
Rel(message_db, writer, "uses")

@enduml
```
