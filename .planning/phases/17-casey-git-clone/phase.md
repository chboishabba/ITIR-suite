# Phase 17: Casey Git Clone

**Owner:** Codex
**Date:** 2026-02-07
**Status:** Planned -> Implementing

## Goal
Create a standalone project scaffold for a superposition-style VCS prototype so
implementation can start without reshaping docs or directory layout.

## Objectives
- Define MVP data model and operations.
- Define deterministic storage and hashing expectations.
- Scaffold Python package and tests for model invariants.
- Keep this project isolated in its own folder.

## Constraints
- Additive only; do not alter existing git workflows in ITIR-suite.
- Deterministic serialization for all core state objects.
- Human-controlled collapse of conflicts.

## Deliverables
- `casey-git-clone/` standalone folder with package scaffold.
- Planning docs under `docs/planning/casey-git-clone/`.
- Initial model/test stubs for core object invariants.

## Acceptance Criteria
- Project appears as top-level component in `README.md`.
- Data model docs cover required object set and operations.
- Test scaffold executes in root `.venv`.

## Open Questions
- Whether to persist object store as sqlite first or filesystem blobs first.
- How to interop with Git pointers in early iterations.
- Whether `ChangeGroup` lands in MVP or post-MVP.

## Next Actions
1. Implement dataclass models and canonical hashing helpers.
2. Add operations: publish, sync, collapse, build-view snapshot.
3. Add fixture-based tests for candidate-set behavior.
