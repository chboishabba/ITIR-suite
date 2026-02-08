# ITIR Prospective Sprint 10 (Refactor Slice) (2026-02-08)

## Why this sprint exists
Current docs now agree on authority boundaries and reducer ownership, but the
implementation path is still fragmented across many TODO lines.

This sprint defines one executable slice that reduces uncertainty without
attempting a full-suite rewrite.

## Current position (where this leaves us)
- Contract direction is aligned:
  - shared primitives
  - siloed semantics
  - SL semantic authority
  - SB temporal authority
  - TiRCorder capture authority
- Main remaining risk is execution drift, not missing theory.
- Most uncertainty comes from not having one gated delivery plan for:
  - shared exchange envelope
  - shared canonical reducer runtime consumption
  - cross-component idempotency/replay tests

## Sprint objective
Freeze and implement the minimum cross-component contract needed to prove:
- idempotent/replay-safe cooperation across SL/TiRCorder/SB/Ribbon
- SL-governed canonical reducer reuse without semantic dilution
- SB temporal reducer independence under shared reducer runtime consumption

## Duration
- 10 working days (single sprint).

## Scope
### In scope
- Ratify blocking decisions for implementation (`Q2`, `Q6`, `Q11`).
- Freeze `itir.exchange.v1` schema and envelope fields.
- Implement shared canonical reducer integration surface (Option C posture).
- Wire thin-slice adapters:
  - TiRCorder -> SL canonical IDs
  - SB -> canonical ID references (no local canonical store)
  - SB -> Ribbon projection payload mapping (read-only)
- Add cross-component contract tests for replay/conflict/authority boundaries.

### Out of scope
- Full ontology expansion (`Q1`, `Q3`, `Q4`, `Q5`, `Q7`, `Q8`, `Q9`, `Q10`).
- Full UI redesign or complete Ribbon interaction overhaul.
- New legal inference features.
- Any mutation path from Ribbon diagnostics into canonical SL/SB state.

## Work packages
## WP1 — Ratification pack (Days 1-2)
- Produce short ADR for:
  - `Q11` Option C ratification (shared runtime, SL semantic governance)
  - `Q6` collision-domain rule
  - `Q2` SB mechanical-should storage contract
- Output: ratified decision text referenced by schema/tests.

## WP2 — Envelope freeze (Days 2-4)
- Define `itir.exchange.v1` schema with required fields:
  - `event_id`
  - `idempotency_key`
  - `payload_hash`
  - `correlation_id`
  - `causation_id`
  - `authority_class`
  - `reducer_runtime_version`
  - `semantic_contract_version`
- Add validation fixtures and adapter-level schema checks.

## WP3 — Shared reducer integration (Days 3-6)
- Expose one supported canonical reducer client surface (package/service).
- Pin reducer/profile versions across SL/TiRCorder/SB adapters.
- Mark all non-canonical fallback outputs explicitly as non-authoritative.

## WP4 — Adapter thin slice (Days 5-8)
- TiRCorder ingestion path emits canonical IDs from shared reducer outputs.
- SB reducers consume canonical IDs but preserve SB-local temporal fold logic.
- Ribbon consumes mapped SB/SL projection payloads read-only.

## WP5 — Contract test gate (Days 7-10)
- Add and require:
  - same key + same hash => no-op replay
  - same key + different hash => hard conflict
  - cross-path identity parity (same text via TiRCorder/SB paths => same IDs)
  - projection safety (Ribbon diagnostics cannot mutate SL/SB canonical state)
  - expansion invariant smoke (summary expands to raw IDs/provenance directly)

## Definition of done
- `itir.exchange.v1` schema is frozen and referenced by adapters/tests.
- Blocking decisions (`Q2`, `Q6`, `Q11`) are ratified and linked to code/tests.
- TiRCorder + SB paths consume shared canonical reducer outputs.
- No independent canonical token/concept identity store is introduced in SB or
  TiRCorder.
- Contract test suite passes for replay/conflict/authority/projection safety.
- Sprint note and TODO list are consistent with implemented artifacts.

## Risks and controls
- Risk: hidden semantic drift via local heuristics.
  - Control: drift guard tests + explicit non-canonical tagging.
- Risk: adapter version skew.
  - Control: pinned reducer/profile compatibility matrix checks.
- Risk: oversized sprint.
  - Control: strict thin-slice scope; defer non-blocking ontology decisions.

## Deliverables
- ADR(s) for `Q2`, `Q6`, `Q11`.
- `itir.exchange.v1` schema + fixtures.
- Shared reducer client contract doc + compatibility matrix.
- Adapter updates for TiRCorder/SB/Ribbon boundaries.
- Contract test suite + CI hook.

## Exit outcome
After this sprint, the team should be able to build further features without
re-arguing reducer ownership or idempotency semantics each time.
