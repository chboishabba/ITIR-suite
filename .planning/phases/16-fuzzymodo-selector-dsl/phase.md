# Phase 16: Fuzzymodo Selector DSL

**Owner:** Codex
**Date:** 2026-02-07
**Status:** Planned -> Implementing

## Goal
Ship an implementation-ready selector and norm-constraint foundation for
Fuzzymodo so quirk/vulnerability decisions are scoped, reproducible, and
human-governed.

## Objectives
- Freeze a minimal DSL syntax and semantics.
- Define schema contracts for selectors and norm constraints.
- Define canonical hashing and invalidation rules.
- Scaffold parser/canonicalizer/evaluator modules and fixture-based tests.

## Constraints
- No semantic invention: selectors only match existing graph facts.
- No implicit OR or fuzzy predicates.
- Human approval remains mandatory for normative effects.

## Deliverables
- Planning docs under `docs/planning/fuzzymodo/`.
- JSON schema drafts for selector and norm-constraint payloads.
- `fuzzymodo/` module layout with stubs for parser, canonicalizer, evaluator.
- Fixture samples and initial smoke tests.

## Acceptance Criteria
- Schemas parse and validate structurally with documented required fields.
- Canonical hashing rules are documented and testable.
- Module/test layout is ready for implementation without reshuffling paths.
- TODO and context docs point to the new phase and artifacts.

## Open Questions
- Whether graph field catalogs should be centralized in one registry module.
- How strict first-pass type validation should be for operator/value pairs.
- Which JSON schema draft version to enforce in CI.

## Next Actions
1. Implement parser and canonicalizer against schema-backed fixtures.
2. Add evaluator with `all_of`/`any_of`/`not` semantics and graph scoping.
3. Wire norm-constraint invalidation checks against changed graph facts.
