# Workbench Architecture

## Shared contracts
- `reviewState` reason code model:
  - `loading`, `ready`, `unsupported`, `empty`, `load_error`, `producer_error`, `graph_not_enabled`, `missing_graph_payload`, `no_graph`
- Single active selection per page, with optional compare-set extensions.
- Bounded graph views are derived from local selection only.

## Modules
- `itir-svelte/src/lib/workbench/reviewState.ts`
  - central reason-code helpers per route family.
- Route-local UI state remains in Svelte pages.
- Graph payload builders remain route-local for now.

## Page responsibilities
- `arguments/thread`: transcript-first review and claim-family scoped graph.
- `narrative-compare`: row-first comparison review and scoped proposition graph.
- `wiki-revision-contested`: tuple/state-first triage with graph/non-graph diagnostic slot.

## Risks
- Overfitting scoped graphs to current fixture structures.
- Future drift between state helpers and page-specific messaging.
