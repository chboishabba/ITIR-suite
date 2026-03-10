# Compactified Context

- Current graph/review workbench state is implementation-first with shared contracts in place.
- Completed this run:
  - shared state helpers: `reviewState.ts`, `selectionBridge.ts`
  - selection bridge wired into arguments thread, narrative compare, contested wiki
  - route-server `stateReason` telemetry emitted and consumed by route pages
  - narrative compare posture chips added for shared/disputed/source-only/corroboration/abstention
  - regression guards updated for state telemetry + selection bridge + no JSON UI state persistence
- Explicit guarantee now covered by code + regression guard:
  - these workbench pages do not persist UI state using `localStorage` or `JSON.stringify`
- Remaining work:
  - runtime interaction tests (not just source-level assertions)
