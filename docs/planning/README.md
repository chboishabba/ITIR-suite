# Planning Docs

This folder contains ADRs, UI component specs, doctrine notes, and validation
artifacts for the context invariant.

## ITIR Orchestrator Contract

ITIR-suite orchestration role and boundaries:
- `docs/planning/itir_orchestrator.md`
- `docs/planning/why_itir_not_sl.md` (separation of powers: ITIR vs SL)

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

## Cross-Thread Followthrough (2026-02-07)

Concrete outputs for:
- SB/fuzzer invariants and acceptance checks
- casey-git model/operation contracts
- JesusCrust integration and ADR-ready principles

Document:
- `docs/planning/sb_casey_jesuscrust_followthrough_20260207.md`

## SL LCE/Profile Followthrough (2026-02-08)

Concrete outputs from thread `6986d38e-4b5c-839b-813a-608aa0de88d5`
(`ADR language vs SensibLaw`) covering:
- engine/profile separation
- ingest-safe invariant language
- profile contract and safety-test backlog

Document:
- `docs/planning/sl_lce_profile_followthrough_20260208.md`
