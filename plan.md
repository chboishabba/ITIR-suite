# Implementation Plan

## Milestone A: Shared state + page wiring (completed)
1. Create shared review-state helper.
2. Wire helper into thread/narrative/wiki pages.
3. Update route UI labels to expose state reason clearly.

## Milestone B: Narrative compare interaction model (completed)
1. Build selectable review-row model (shared/disputed/source-only/corroboration/abstention).
2. Add inspector tabs and explicit graph-open action.
3. Add bounded graph payload derived from selected row.

## Milestone C: Regression coverage alignment (completed)
1. Update graph UI regression assertions to new labels/flow.
2. Add checks for review-state helper wiring.
3. Add checks for narrative compare inspector + scoped graph sections.

## Milestone D: Selection bridge consolidation (completed)
1. Introduce shared selection-bridge helper.
2. Wire thread, narrative compare, and contested wiki to selection bridge.
3. Keep route-local behavior bounded while sharing event semantics.

## Milestone E: State telemetry + posture grammar (completed)
1. Emit `stateReason` from route server loaders for thread/narrative/wiki.
2. Consume server `stateReason` in route pages with local fallback only.
3. Add explicit posture chips in narrative compare rows and inspector.
4. Add regression guard ensuring no JSON/localStorage UI-state persistence in these pages.

## Milestone F: Docs/TODO/changelog sync (completed)
1. Update top-level TODO statuses for recent workbench followthrough.
2. Record behavior changes in `itir-svelte/CHANGELOG.md`.
3. Reconcile project-memory files with implemented state.

## Milestone G: P0 tokenizer + lexeme closeout refresh (completed)
1. Re-run deterministic tokenizer/lexeme migration tests in project venv.
2. Update tokenizer migration planning note with fresh verification evidence.
3. Mark `[P0]` tokenizer migration and lexeme-layer TODOs done.
4. Record verification refresh in `SensibLaw/CHANGELOG.md`.

## Milestone H: P1 SL engine/profile followthrough v1 (completed)
1. Ratify profile contracts/lint docs from draft to explicit allow/deny sets.
2. Implement profile admissibility+lints (`sl_profile`, `sb_profile`, `infra_profile`).
3. Add cross-profile safety tests and verify in project venv.
4. Mark TODO item done and record changelog entry.

## Milestone I: Next achievable sprint (completed)
1. Tool Use Summary hydration fixes:
   - DONE: diagnosed Shell/hour and Input/hour coupling in SB daily reducer.
   - DONE: implemented reducer-layer fix (agent `exec_command` and `request_user_input` hour bins).
   - DONE: added NotebookLM event-path coverage into the tool-use stream (`notebooklm_meta_event` family + hour bins).
2. DONE: add explicit regression tests for shell/input counter hydration.

## Milestone J: OpenRecall query/read-model interface (completed)
1. Update OpenRecall planning/TODO/context docs to define the neutral
   query/read-model seam over imported captures.
2. Add query-first helpers for:
   - latest import runs
   - capture counts by app/title/date
   - screenshot coverage
   - recent filtered capture rows
3. Add a bounded CLI around those helpers without introducing GUI-first
   coupling.
4. Add focused tests and record the shipped behavior in the changelog.
