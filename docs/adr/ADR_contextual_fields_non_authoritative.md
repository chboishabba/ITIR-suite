# ADR-00XX: Contextual Fields Are Non-Authoritative

Status: Accepted  
Date: 2026-02-06  
Applies to: ITIR, SB, SensibLaw renderers and exports  
Owner: Architecture

## Context

SB/ITIR ingest “context fields” such as weather, market indices, astronomical
events, and symbolic overlays (e.g., astrology). These signals are
environmental and socially powerful, but they are **not facts about the user**
and **not evidence of intent or causality**. Without guardrails they can
colonise meaning (e.g., “bad market → stress → cause”), which violates the
Right to Context and Right to Opacity doctrines.

## Decision

Context fields SHALL be treated as **read-only, non-authoritative overlays**
that align on time (and optionally place) but NEVER participate in inference,
summaries, prioritisation, alerts, or promotion. They remain outside the
authoritative SB core (events/artifacts/activity).

## Invariants

- Context fields align by time/space only; **no causal or behavioural meaning**.
- Summaries MUST declare whether context is included or excluded; no silent
  blending.
- Context fields can NOT trigger alerts, reorder importance, or modify logic
  outputs.
- Symbolic overlays (e.g., astrology) are **opt-in, explicitly labeled
  symbolic**, and never attach automatically to events.
- Exports that drop context MUST log the loss; exports that keep context must
  retain provenance (“this data did not come from you”).

## Data Model (normative sketch)

```json
{
  "type": "context_field.weather",           // market | astronomy | ...
  "source": "bom.gov.au",
  "location": "lat,lon",
  "time_range": "...",
  "values": { "temp_c": 34.2, "wind_kmh": 42 },
  "provenance": { "retrieved_at": "...", "license": "CC-BY" }
}
```

Symbolic overlays live as `symbolic_overlay.*` with mandatory disclaimer:
“Symbolic framework; non-causal”.

## Consequences

Positive: prevents coercive interpretation; preserves situated memory; keeps
external signals from overwhelming user evidence.  
Negative: adds toggles and friction; limits “insight” style features. These are
accepted tradeoffs.

## Rejected Alternatives

- Treating context fields as features for recommendation/alerting.
- Auto-attaching symbolic overlays to events.
- Summarising weather/market into behavioural claims.

## Compliance / Tests

- Rendering tests: context fields never appear in summaries without a “context
  included/excluded” badge.
- Export tests: dropping context emits a loss log entry.
- Language lint: forbid causal terms (“caused, influenced, impacted”) in
  context panels.
