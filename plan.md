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

## Milestone F: Remaining
1. Add true route interaction tests (select -> inspect -> graph -> return) beyond static source assertions.
