# Python Domain Ownership Policy

Date: 2026-03-30

## Purpose

Make one suite-level architecture rule explicit:

- TypeScript/JavaScript must not own business logic.
- Python-owned producer/runtime layers must own domain semantics,
  normalization, projection policy, and cross-lane reusable rules.

This is a correction to current repo state, not a description of fully-fixed
reality.

## Problem

`ITIR-suite` currently has real domain logic duplicated across:

- Python producer/runtime layers in `SensibLaw` and related adapters
- `itir-svelte` server helpers and route shells

That duplication is not just a stylistic issue. It creates:

- conflicting semantics across lanes
- repeated normalization logic
- harder parity checking
- hidden regressions when a route changes without the producer changing
- increased pressure to invent lane-local JS/TS policy instead of reusing the
  canonical runtime

## Required rule

### Python owns

- domain/business rules
- canonical normalization
- coalescing and reconciliation logic
- resolver and loader policy
- projection semantics shared across lanes
- canonical graph/timeline/fact ordering rules
- reusable cross-lane adapters

### TS/JS may own

- presentation
- interaction state
- route composition
- transport-safe request/response handling
- view-only formatting
- local UI affordances that do not change canonical meaning

### TS/JS must not own

- canonical fact/proposition synthesis
- canonical timeline ordering policy
- cross-lane numeric semantics
- domain reconciliation/coalescing rules
- source resolution rules that should match producer/runtime behavior
- any other logic that would create a second authority surface

## Current violating surfaces

The current high-signal violating surfaces include:

- `itir-svelte/src/lib/server/wikiTimeline.ts`
- `itir-svelte/src/routes/graphs/wiki-fact-timeline/projection.ts`
- `itir-svelte/src/lib/wiki_timeline/numeric.ts`
- `itir-svelte/src/lib/wiki_timeline/graph.ts`
- `itir-svelte/src/routes/graphs/timeline-ribbon/+page.server.ts`

These files should be treated as migration surfaces, not stable architecture.

## Migration rule

When a TS/JS surface contains business logic:

1. define the Python-owned replacement boundary first
2. move canonical semantics into Python
3. reduce TS/JS to a shell, adapter, or display layer
4. add parity tests so the JS/TS layer cannot silently diverge

Do not widen TS/JS helper modules as a substitute for migration.

## Lane-specific interpretation

### Wiki / timeline / GWB

- shared timeline and fact semantics belong in Python-owned runtime or producer
  modules
- `itir-svelte` route/server files should consume already-shaped payloads
  rather than deciding canonical graph/fact semantics

### Affidavit

- affidavit review already mostly lives in Python and must stay there
- do not invent a parallel JS/TS affidavit runtime or semantic layer

### Adapters

- bounded adapter contracts such as `itir-mcp` may validate envelopes and
  transport behavior
- adapters must not redefine producer semantics

## Governance

Promotion criteria for future work in this area:

- no new business logic is introduced into TS/JS
- any remaining TS/JS business-logic surface is explicitly marked as temporary
  migration debt
- new cross-lane semantics land in Python first
- route and adapter layers only consume or display canonical semantics

## Immediate execution consequence

This should be treated as a P0 architecture correction in `TODO.md`, not as a
mere large-file cleanup preference.
