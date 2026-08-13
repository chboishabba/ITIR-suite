# Promote Abstain Audit Gate Slice

Date: 2026-04-02

## Purpose

Land the first reusable `promote | abstain | audit` gate above the normalized
compiler-shaped products.

The shared contract is already real.
AU and GWB product normalization are already real.

The next bounded step is not new semantics. It is a shared decision record
that says:

- what the gate decided
- why it decided that
- what product evidence it used

## Decision

Keep the first gate extremely small.

Inputs:

- lane id
- product ref
- compiler-contract summary

Outputs:

- `decision`
  - `promote`
  - `abstain`
  - `audit`
- `reason`
- `evidence`
  - promoted count
  - review count
  - abstained count
  - product roles used

## First Rule

The first reusable rule is:

- `promote`
  - promoted outcomes exist and neither review nor abstention pressure exists
- `abstain`
  - no promoted outcomes exist
- `audit`
  - promoted outcomes exist but review or abstention pressure also exists

This is intentionally simple.

It does not replace lane-local promotion logic.
It wraps normalized products in one common downstream decision surface.

## First Adopters

- AU public handoff
- AU fact-review bundle
- GWB public handoff
- GWB public review
- GWB broader review
- Wikidata migration pack

## Acceptance Gate

This slice is complete when:

- one shared gate module exists
- all currently normalized products emit the same gate record
- tests pin the rule and the first adopter payloads

## Outcome

Landed.

Implemented:

- shared gate module:
  - `SensibLaw/src/policy/product_gate.py`
- first adopters:
  - AU public handoff
  - AU fact-review bundle
  - GWB public handoff
  - GWB public review
  - GWB broader review
  - Wikidata migration pack

Rule now emitted:

- `promote`
  - promoted outcomes exist and no open review/abstain pressure exists
- `abstain`
  - no promoted outcomes exist
- `audit`
  - promoted outcomes exist but review or abstain pressure also exists

Validation:

- focused gate:
  - `28 passed`
- touched modules:
  - `py_compile` passed

## Next Lane

The next pinned lane is the first operator-grade workflow layer over the
normalized outputs.
