# Fact Intake Payload Mutations Component

Date: 2026-03-31

## Change Class

Standard change.

## Problem

Fact-intake payload mutation logic still existed as local helper blocks in more
than one adopter:

- `SensibLaw/src/fact_intake/personal_handoff_bundle.py`
- `SensibLaw/src/fact_intake/acceptance_fixtures.py`

The duplicated logic covered:

- observation row append/mutation
- review row append/mutation
- contestation row append/mutation
- deterministic mutation-row identifiers

## Requirement

Create one shared Python owner for fact-intake payload mutations so adopters
reuse the same append semantics instead of rebuilding them inline.

## Component Boundary

Shared owner:

- `SensibLaw/src/fact_intake/payload_mutations.py`

Adopters:

- `SensibLaw/src/fact_intake/personal_handoff_bundle.py`
- `SensibLaw/src/fact_intake/acceptance_fixtures.py`

## Acceptance

- both adopters import the shared payload-mutation helpers
- deterministic IDs remain stable
- focused tests cover the shared owner and both adopters

## Quality Gate

Run from `SensibLaw/`:

- `../.venv/bin/python -m pytest -q tests/test_fact_intake_payload_mutations.py tests/test_personal_handoff_bundle.py tests/test_fact_review_acceptance_wave.py`

## C4 / PlantUML

```plantuml
@startuml
title Fact Intake Payload Mutations Component

Component(handoff, "personal_handoff_bundle.py", "Fact-intake adopter")
Component(fixtures, "acceptance_fixtures.py", "Fact-intake adopter")
Component(mutations, "payload_mutations.py", "Shared payload mutation owner")

Rel(handoff, mutations, "uses")
Rel(fixtures, mutations, "uses")

@enduml
```
