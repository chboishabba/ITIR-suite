# Shared Evidence Bundle To Promoted Outcome Contract

Date: 2026-04-02

## Purpose

Define the smallest real cross-lane contract that AU, GWB, and Wikidata/Nat
can all adopt now without pretending they already share identical semantics.

This is the first implementation slice for the compiler-shaped moonshot frame:

- bounded evidence bundle in
- promoted outcomes out
- derived products after that

## Decision

Keep the shared contract deliberately small.

It should normalize only:

- what kind of evidence bundle a lane accepted
- what family of promoted outcomes it emitted
- what derived product classes it exposes downstream

It should not yet normalize:

- lane-specific predicate vocabularies
- doctrinal meaning
- detailed graph semantics
- promotion thresholds

## Shared Fields

The first contract surface is:

- `lane`
- `schema_version`
- `evidence_bundle`
  - `bundle_kind`
  - `source_family`
  - `source_count`
  - `item_count`
  - `item_label`
- `promoted_outcomes`
  - `outcome_family`
  - `promoted_count`
  - `review_count`
  - `abstained_count`
  - `outcome_labels`
- `derived_products[]`
  - `product_kind`
  - `role`
  - `default_surface`

## First Real Adopters

- AU public handoff
- GWB public handoff
- Wikidata migration pack

These are the right first adopters because they already expose bounded,
reviewable outputs that the repo treats as real products.

## Governance

- ITIL:
  - normalize accepted input and returned output first
- ISO 9000:
  - make the handoff contract explicit and testable
- ISO 42001 / NIST AI RMF:
  - keep evidence bundle, promoted outcome, and derived product distinct
- ISO 23894:
  - avoid hidden product drift or fake cross-lane sameness
- Six Sigma:
  - reduce product-shape variance before deeper semantic reuse
- C4:
  - promotion core emits stable lane products; graph/report stay derived

## Acceptance Gate

This slice is complete when:

- one shared contract module exists in code
- AU, GWB, and Wikidata/Nat each emit a real `compiler_contract` payload
- tests pin the lane-specific adapters without requiring fake semantic
  unification

## Landed Slice

This slice is now landed.

Code owner:

- [compiler_contract.py](/home/c/Documents/code/ITIR-suite/SensibLaw/src/policy/compiler_contract.py)

First adopters:

- [build_au_zelph_handoff.py](/home/c/Documents/code/ITIR-suite/SensibLaw/scripts/build_au_zelph_handoff.py)
- [build_gwb_zelph_handoff.py](/home/c/Documents/code/ITIR-suite/SensibLaw/scripts/build_gwb_zelph_handoff.py)
- [wikidata.py](/home/c/Documents/code/ITIR-suite/SensibLaw/src/ontology/wikidata.py)

Pinned tests:

- [test_compiler_contract.py](/home/c/Documents/code/ITIR-suite/SensibLaw/tests/test_compiler_contract.py)
- [test_au_zelph_handoff.py](/home/c/Documents/code/ITIR-suite/SensibLaw/tests/test_au_zelph_handoff.py)
- [test_gwb_zelph_handoff.py](/home/c/Documents/code/ITIR-suite/SensibLaw/tests/test_gwb_zelph_handoff.py)
- [test_materialize_wikidata_migration_pack.py](/home/c/Documents/code/ITIR-suite/SensibLaw/tests/test_materialize_wikidata_migration_pack.py)

## Not In Scope Yet

- reusable `promote | abstain | audit` gate
- AU/GWB full normalization onto the shared contract
- shared primitive/comparison layer
- graph hardening lane
