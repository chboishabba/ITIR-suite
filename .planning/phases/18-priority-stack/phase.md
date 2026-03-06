# Phase 18: Priority Stack Dependencies & Sequencing

**Owner:** Codex
**Date:** 2026-03-06
**Status:** Planned

## Goal
Produce an execution-ready plan that sequences the priority work:
lexeme layer, compression engine, Wikidata projection, and GWB/AAO pipelines,
with explicit dependencies and blocking decisions.

## Objectives
- Consolidate dependency map across P0–P3 priority items.
- Identify blocking decisions (canonical token stream choice, tokenizer replacement).
- Define minimal executable slices for Wikidata and Wiki pipeline work.

## Constraints
- Planning only; no implementation in this phase.
- Preserve existing doc contracts; do not invent new semantics.
- Keep plans small and executable (2–3 tasks per plan).

## Deliverables
- Phase plan files for execution (`18-01-PLAN.md`, `18-02-PLAN.md`).
- Dependency/sequence plan doc.
- Tokenizer migration plan doc (regex → deterministic).

## Acceptance Criteria
- Plan file exists with tasks, checkpoints, and success criteria.
- Dependencies and sequencing are explicit and referenced.

## Next Actions
1. Draft `18-01-PLAN.md`.
2. Draft `18-02-PLAN.md` (tokenizer migration planning).
3. Create a dependency/sequence plan doc.
