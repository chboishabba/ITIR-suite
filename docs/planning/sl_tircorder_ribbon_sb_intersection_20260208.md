# SL x TiRCorder x ITIR-Ribbon x StatiBaker Intersection Contract (2026-02-08)

## Purpose
Define the concrete intersection between:
- `SensibLaw` (SL) as structural/provenance authority.
- `tircorder-JOBBIE` as capture/transcript event producer.
- `itir-ribbon` as timeline/lens projection contract.
- `StatiBaker` (SB) as append-only state compiler.

This document translates existing intent into an explicit cross-component
handoff contract and identifies remaining gaps.

## Scope
- Orchestration context: `docs/planning/itir_orchestrator.md`.
- Component contracts:
  - `SensibLaw/docs/interfaces.md`
  - `tircorder-JOBBIE/docs/interfaces.md`
  - `itir-ribbon/docs/interfaces.md`
  - `StatiBaker/docs/interfaces.md`
- This is a contract/planning artifact only (no runtime behavior change in this pass).

## Current declared alignment
- SL is treated as deterministic substrate with span/provenance outputs.
- TiRCorder is treated as upstream capture/transcript and event emitter.
- SB is treated as append-only reduction layer over multi-source signals.
- ITIR-ribbon is treated as a projection/lens contract, not authority memory.
- ITIR-suite control plane is declared as coordinator, not semantic owner.

## Four-way edge map

### Edge E1: TiRCorder -> SL
- Producer:
  - TiRCorder `Channel C` transcript egress
  - TiRCorder `Channel D` timeline/event egress
- Consumer:
  - SL `Channel A` source ingress
- Required invariant:
  - Ingested records must remain provenance-linked to capture source and timing.

### Edge E2: SL -> SB
- Producer:
  - SL `Channel B` structural egress
  - SL `Channel C` graph/API egress
- Consumer:
  - SB `Channel A` state ingress
- Required invariant:
  - SB reductions must not rewrite SL substrate facts; they reference/compile.

### Edge E3: SL -> ITIR-ribbon
- Producer:
  - SL spans, rule/logic structures, and conservation-relevant metadata
- Consumer:
  - Ribbon `Channel B` context envelope ingress
- Required invariant:
  - Ribbon rendering remains context-bound and non-authoritative.

### Edge E4: TiRCorder -> SB
- Producer:
  - TiRCorder timeline/event egress
- Consumer:
  - SB state ingress
- Required invariant:
  - Audio/transcript event history remains replayable under retries/reimports.

### Edge E5: SB -> ITIR-ribbon
- Producer:
  - SB distilled brief/action-state egress (`Channel C/D`)
- Consumer:
  - Ribbon lens/segment model inputs (`Channel B/C`)
- Required invariant:
  - Ribbon projects SB reductions as lens views; no mutation of SB canonical history.

### Edge E6: ITIR-ribbon -> SL/SB QA loop
- Producer:
  - Ribbon validation egress (`Channel D`)
- Consumer:
  - SL/SB test and QA workflows
- Required invariant:
  - Validation outputs are diagnostics only unless explicitly promoted via receipts.

## Gap assessment (documented vs executable)

### G1: Shared handoff envelope missing
Current docs declare channels but not one shared payload contract across all four
components.

### G2: Cross-component idempotency/correlation not explicitly frozen
Per-component docs mention deterministic behavior, but suite-level handoff keys
(`idempotency_key`, `correlation_id`, `causation_id`) are not yet standardized.

### G3: Authority/promotion boundary needs explicit receipt rule at edges
Observer outputs and projections need explicit promotion-receipt gates before
they can alter canonical state surfaces.

### G4: End-to-end contract tests across all four are not yet defined
Existing tests are mostly component-local, not full chain replay tests.

### G5: SB-to-ribbon semantic mapping is under-specified
How SB reductions map to ribbon segments/lenses is implied but not schema-frozen.

## Recommended improvements

### R1: Define a shared cross-component envelope (`itir.exchange.v1`)
- Minimum fields:
  - `event_id`
  - `source_component`
  - `source_entity_id`
  - `idempotency_key`
  - `correlation_id`
  - `causation_id`
  - `occurred_at`
  - `ingested_at`
  - `span_refs` (when text-backed)
  - `provenance`
  - `payload_hash`

### R2: Freeze authority classes at exchange boundary
- `authoritative_substrate` (SL)
- `observer_capture` (TiRCorder)
- `compiled_state` (SB)
- `projection_only` (ITIR-ribbon)

### R3: Add promotion-receipt gate for cross-class transitions
Any transition from observer/projection into canonical/compiled authority must
emit promotion receipts and preserve source provenance.

### R4: Add cross-component contract tests
- Duplicate replay test: same idempotency key and payload hash => no-op.
- Conflict test: same idempotency key with different payload hash => conflict.
- Belief-time replay test: reconstruct state at time `T` using recorded receipts.
- Projection safety test: ribbon diagnostics cannot mutate SL/SB state.

### R5: Add SB-to-ribbon mapping contract
Define exact mapping from SB `carryover/new/resolved` reductions to ribbon
segment semantics and conservation metadata.

## Immediate followthrough
- Add TODO items for schema, adapters, and contract tests.
- Keep per-component interface docs as source-of-truth per component, while this
  document remains the four-way intersection map.
- Use `docs/planning/itir_idempotency_dedupe_cooperation_20260208.md` for
  shared-vs-siloed idempotency semantics, authority-crossing handshake details,
  and unresolved schema-freeze decisions (`Q1`-`Q11`).
