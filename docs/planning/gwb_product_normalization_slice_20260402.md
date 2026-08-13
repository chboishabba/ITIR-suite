# GWB Product Normalization Slice

Date: 2026-04-02

## Purpose

Promote the third compiler-shaped moonshot lane:

- GWB product normalization on the shared contract

The first contract slice already landed in:

- AU public handoff
- GWB public handoff
- Wikidata migration pack

The AU followthrough then normalized a second AU product surface:

- AU fact-review bundle

GWB needs the equivalent move:

- normalize the GWB review artifact family, not just the public handoff

## Decision

Make the GWB review artifacts emit the same shared `compiler_contract`
summary.

First bounded adopters:

- GWB public review
- GWB broader review

This keeps the slice honest:

- no semantic-pipeline rewrite
- no new relation-promotion thresholds
- no graph redesign
- no UI reshaping

It only normalizes product shape across real GWB outputs.

## Acceptance Gate

This slice is complete when:

- GWB public review emits `compiler_contract`
- GWB broader review emits `compiler_contract`
- the contract reflects public-source evidence in plus action/relation/review
  outcomes out
- current GWB review tests still pass

## Landed Slice

This slice is now landed.

Updated code:

- [compiler_contract.py](/home/c/Documents/code/ITIR-suite/SensibLaw/src/policy/compiler_contract.py)
- [build_gwb_public_review.py](/home/c/Documents/code/ITIR-suite/SensibLaw/scripts/build_gwb_public_review.py)
- [build_gwb_broader_review.py](/home/c/Documents/code/ITIR-suite/SensibLaw/scripts/build_gwb_broader_review.py)

Pinned tests:

- [test_compiler_contract.py](/home/c/Documents/code/ITIR-suite/SensibLaw/tests/test_compiler_contract.py)
- [test_gwb_public_review.py](/home/c/Documents/code/ITIR-suite/SensibLaw/tests/test_gwb_public_review.py)
- [test_gwb_broader_review.py](/home/c/Documents/code/ITIR-suite/SensibLaw/tests/test_gwb_broader_review.py)
- [test_gwb_zelph_handoff.py](/home/c/Documents/code/ITIR-suite/SensibLaw/tests/test_gwb_zelph_handoff.py)

Result:

- GWB public handoff, GWB public review, and GWB broader review now all emit
  the shared compiler-shaped summary
- GWB therefore has a normalized product family under the same contract
  without rewriting the semantic pipeline
