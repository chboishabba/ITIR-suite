# Phase 17 Milestones: Casey Git Clone

## M1 - Docs Freeze
- Status: Complete
- Scope: model, workflow, and MVP backlog docs.
- Exit: docs reviewed and linked from root planning index.

## M2 - Model Scaffold
- Status: Complete
- Scope: core objects and deterministic ids.
- Exit: model tests for invariants pass.

## M3 - Ops Scaffold
- Status: Complete
- Scope: publish/sync/collapse/build-view operations.
- Exit: operation-level tests pass with fixtures.

## M4 - Storage Decision
- Status: Complete
- Scope: choose sqlite-first vs file-store-first and document rationale.
- Exit: decision recorded in
  `docs/planning/casey-git-clone/sqlite_runtime_decision_20260319.md`.

## M5 - External Boundaries
- Status: In progress
- Scope:
  - Casey -> fuzzymodo read-only export/advisory seam
  - Casey -> StatiBaker observer-only receipt/reference seam
- Exit:
  - Casey export adapter exists for `casey.facts.v1`
  - fuzzymodo advisory adapter exists for `fuzzymodo.casey.advisory.v1`
  - Casey receipt emission is wired for the sharpened SB seam
