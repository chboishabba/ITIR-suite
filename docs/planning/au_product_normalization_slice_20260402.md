# AU Product Normalization Slice

Date: 2026-04-02

## Purpose

Promote the second compiler-shaped moonshot lane:

- AU product normalization on the shared contract

The first contract slice already landed in AU public handoff, GWB public
handoff, and Wikidata migration pack. AU still has another important product
surface that should stop looking bespoke:

- the AU fact-review bundle

## Decision

Make the AU fact-review bundle emit the same shared `compiler_contract`
summary inside its semantic context.

This keeps the slice bounded:

- no doctrinal rewrite
- no new promotion thresholds
- no graph changes
- no operator-view redesign

It only normalizes AU product shape across its own real outputs.

## Scope

In scope:

- shared AU bundle adapter in code
- AU fact-review bundle emission
- test coverage for the normalized bundle surface

Out of scope:

- GWB normalization
- reusable `promote | abstain | audit` gate
- broader workflow/UI changes

## Acceptance Gate

This slice is complete when:

- the AU fact-review bundle emits `semantic_context.compiler_contract`
- the contract reflects legal/hearing evidence in plus procedural/review
  outcomes out
- existing AU bundle tests still pass

## Landed Slice

This slice is now landed.

Updated code:

- [compiler_contract.py](/home/c/Documents/code/ITIR-suite/SensibLaw/src/policy/compiler_contract.py)
- [au_review_bundle.py](/home/c/Documents/code/ITIR-suite/SensibLaw/src/fact_intake/au_review_bundle.py)

Pinned tests:

- [test_compiler_contract.py](/home/c/Documents/code/ITIR-suite/SensibLaw/tests/test_compiler_contract.py)
- [test_au_fact_review_bundle.py](/home/c/Documents/code/ITIR-suite/SensibLaw/tests/test_au_fact_review_bundle.py)
- [test_au_zelph_handoff.py](/home/c/Documents/code/ITIR-suite/SensibLaw/tests/test_au_zelph_handoff.py)

Result:

- AU public handoff and AU fact-review bundle now both emit the shared
  compiler-shaped summary
- AU therefore has two normalized product surfaces under the same contract
  without widening doctrine or operator workflow scope
