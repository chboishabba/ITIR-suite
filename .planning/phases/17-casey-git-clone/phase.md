# Phase 17: Casey Git Clone

**Owner:** Codex
**Date:** 2026-02-07
**Status:** Implementing

## Goal
Create a standalone Casey prototype that proves superposition-style candidate
state, explicit workspace selection, explicit collapse, and frozen build views
through a local runtime + CLI testbed.

## Objectives
- Prove the core model and operation spine.
- Lock sqlite-first runtime/state posture for the local testbed.
- Expose a minimal human-usable CLI for the alice/bob divergence walkthrough.
- Freeze the next external boundaries:
  Casey -> fuzzymodo and Casey -> StatiBaker.

## Constraints
- Additive only; do not alter existing git workflows in ITIR-suite.
- Deterministic serialization for all core state objects.
- Human-controlled collapse of conflicts.

## Deliverables
- `casey-git-clone/` standalone package with model/ops/runtime/CLI.
- Planning docs under `docs/planning/casey-git-clone/` plus cross-project
  contract notes in `docs/planning/`.
- Passing model, operation, runtime, and CLI test coverage for the local
  superposition walkthrough.

## Acceptance Criteria
- Casey local runtime and CLI testbed execute in the root environment.
- The alice/bob divergent same-path walkthrough is test-covered.
- Cross-project contracts exist for the next two boundaries:
  Casey -> fuzzymodo and Casey -> StatiBaker.

## Open Questions
- Exact Casey -> fuzzymodo export adapter shape in code.
- Exact Casey -> StatiBaker receipt emission hooks in code.
- Whether `ChangeGroup` remains post-MVP after the boundary work lands.

## Next Actions
1. Implement Casey -> fuzzymodo `casey.facts.v1` export over runtime state.
2. Implement fuzzymodo advisory consumption for
   `fuzzymodo.casey.advisory.v1`.
3. Implement Casey -> StatiBaker receipt emission aligned to the observer-only
   seam.
