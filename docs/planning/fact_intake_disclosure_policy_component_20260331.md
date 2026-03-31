# Fact Intake Disclosure Policy Component

Date: 2026-03-31

## Change Class

Standard change.

## Problem

The fact-intake disclosure/export layer still duplicated recipient and protected-
disclosure policy across two adopters:

- `SensibLaw/src/fact_intake/personal_handoff_bundle.py`
- `SensibLaw/src/fact_intake/protected_disclosure_envelope.py`

The duplicated logic included:

- recipient profile normalization
- stable payload hashing
- UTC creation timestamps
- allowed-recipient normalization
- protected-disclosure settings normalization
- share-with normalization

That duplication is no longer acceptable now that the transcript/AU fact-intake
bundle family has been normalized behind shared Python owners.

## Requirement

Create one shared Python owner for fact-intake disclosure policy so personal
handoff and protected-disclosure envelopes consume the same normalization rules
instead of carrying their own local copies.

## Component Boundary

Shared owner:

- `SensibLaw/src/fact_intake/disclosure_policy.py`

Adopters:

- `SensibLaw/src/fact_intake/personal_handoff_bundle.py`
- `SensibLaw/src/fact_intake/protected_disclosure_envelope.py`
- `SensibLaw/src/fact_intake/personal_chat_import.py`

## Acceptance

- both adopters import the shared disclosure-policy helpers
- recipient profile and protected-disclosure settings stay behaviorally stable
- focused tests cover the shared owner and both adopters

## Quality Gate

Run from `SensibLaw/`:

- `../.venv/bin/python -m pytest -q tests/test_fact_intake_disclosure_policy.py tests/test_personal_handoff_bundle.py tests/test_protected_disclosure_envelope.py`

## C4 / PlantUML

```plantuml
@startuml
title Fact Intake Disclosure Policy Component

Component(personal_handoff, "personal_handoff_bundle.py", "Fact-intake adopter")
Component(protected_env, "protected_disclosure_envelope.py", "Fact-intake adopter")
Component(policy, "disclosure_policy.py", "Shared disclosure normalization")

Rel(personal_handoff, policy, "uses")
Rel(protected_env, policy, "uses")

@enduml
```
