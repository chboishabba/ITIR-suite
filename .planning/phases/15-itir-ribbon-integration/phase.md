# Phase 15: ITIR Ribbon Integration

**Owner:** Codex
**Date:** 2026-02-06
**Status:** Planned → Implementing

## Goal
Ship a ribbon demo surface with conserved allocation semantics, lens DSL wiring,
selector contract, and a Playwright conservation test harness.

## Objectives
- Add a Streamlit ribbon demo tab that exposes the selector contract.
- Wire lens DSL evaluation into demo data generation.
- Provide phase-regime and lens-pack scaffolding for ITIR/SB/SL/LES/DASHI.
- Gate Playwright tests on `RIBBON_DEMO_URL`.

## Constraints
- No narrative labels or inferred meaning in demo output.
- Selector contract must remain stable for tests.
- All changes must be additive and non-destructive.

## Deliverables
- `itir-ribbon/` module with DSL + phase packs.
- Streamlit ribbon demo tab with `data-testid`/`data-*` attributes.
- Playwright conservation spec (gated by `RIBBON_DEMO_URL`).
- Lens DSL evaluator + unit tests.

## Acceptance Criteria
- Segment widths sum to 100% under each lens.
- Lens switch preserves segment order and anchors.
- Demo emits `data-width-norm` for conservation checks.
- Playwright spec runs when `RIBBON_DEMO_URL` is set.

## Open Questions
- Final route/URL for demo tab in production UI.
- Whether to mount ribbon demo as a standalone module.

## Next Actions
1. Implement ribbon demo tab with selectors.
2. Wire lens DSL evaluation to demo data.
3. Add tests and update changelog.
