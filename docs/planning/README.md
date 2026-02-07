# Planning Docs

This folder contains ADRs, UI component specs, doctrine notes, and validation
artifacts for the context invariant.

## ITIR Orchestrator Contract

ITIR-suite orchestration role and boundaries:
- `docs/planning/itir_orchestrator.md`

## Validation (Stub)

The context envelope validation stub lives at:
- `docs/planning/context_envelope_validate_stub.py`

To wire validation:
1. Choose a JSON Schema validator (draft 2020-12 compatible).
2. Implement the TODOs in the stub.
3. Add the script to CI or a pre-commit hook.

## Fuzzymodo Selector DSL Pack

Fuzzymodo planning artifacts live under:
- `docs/planning/fuzzymodo/`

This pack defines selector DSL contracts, norm-constraint schemas, canonical
hashing rules, and fixture samples for implementation scaffolding.

## Casey Git Clone Pack

Casey-derived superposition VCS planning artifacts live under:
- `docs/planning/casey-git-clone/`

## Project Interface Contracts

Suite-wide interface contract index:
- `docs/planning/project_interfaces.md`
