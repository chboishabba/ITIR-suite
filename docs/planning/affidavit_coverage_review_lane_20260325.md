# Affidavit Coverage Review Lane

Date: 2026-03-25
Status: initial bounded implementation exists
Scope: Mary-parity / AU next-step planning

## Purpose

Turn the current AU/Mary dense-substrate and fact-review surfaces into a
concrete corpus-to-affidavit review lane.

This lane is for the user story:
- `SL-US-31: Corpus-to-Affidavit Coverage Review`

It is not a claim that the repo already performs end-to-end affidavit
comparison on real client matters. It is the governance note for the first
bounded lane built on top of the substrate that now exists.

## Problem framing

Current repo strength:
- dense source-grounded extraction is now real for transcript-scale material
- persisted fact-review runs are queryable and operator-readable
- AU proves that transcript density can survive into a bounded operator queue
  without pretending reviewed event coverage is complete

Current gap:
- the repo does not yet have an explicit review surface answering:
  - what source-grounded material made it into the affidavit?
  - what is partially represented?
  - what appears omitted?
  - what remains too ambiguous or contested to treat as an omission?

## Current state

The current AU transcript lane proves:
- `1747` transcript units and `1747` dense substrate facts are visible
- the 24-row reviewed hearing projection is useful as operator triage, but not
  yet affidavit-grade reviewed coverage
- Mary parity is already in breadth/polish work, not architecture-missing work

This means the next useful move is not another abstract extraction layer.
It is a comparison/accounting lane over the substrate already produced.

## Contract shape

The lane should distinguish four layers clearly.

### 1. Source-grounded substrate

Examples:
- document rows
- transcript units
- statements
- observations
- dense fact rows

Contract:
- high recall
- provenance-safe
- may be messy
- not treated as affidavit-ready truth

### 2. Reviewed source candidates

Examples:
- reviewed or thresholded fact/event candidates
- contested and abstained review rows
- chronology-linked operator queue items

Contract:
- review status is explicit
- contestation is explicit
- still not the affidavit itself

### 3. Affidavit proposition layer

Examples:
- extracted affidavit propositions
- paragraph-level proposition groups
- paragraph-to-source linkage receipts

Contract:
- each proposition is source-linked, unsupported, or explicitly unresolved
- affidavit wording does not silently replace source structure

### 4. Coverage / omission review layer

Comparison statuses should include at least:
- `covered`
- `partial`
- `missing_review`
- `contested_source`
- `abstained_source`
- `unsupported_affidavit`

This layer is the operator-facing answer to corpus completeness.

## First bounded implementation slice

Input:
- one persisted AU dense-substrate artifact or fact-review run
- one affidavit-like text document or declaration draft

Output:
- one machine-readable coverage review bundle
- one human-readable omission/partial/support summary
- one queryable row surface linking:
  - affidavit proposition
  - source-grounded row(s)
  - status
  - provenance receipts
  - review reason

Recommended implementation posture:
- do not try to prove legal sufficiency
- do not promise exhaustive semantic deduping in v1
- prefer explicit review rows over hidden similarity merges

Current implementation surface:
- builder:
  `SensibLaw/scripts/build_affidavit_coverage_review.py`
- focused regression:
  `SensibLaw/tests/test_affidavit_coverage_review.py`
- current accepted source inputs:
  - `fact.review.bundle.v1`
  - bounded `au_public_handoff_v1`-style selected-fact slice

Current v1 output:
- machine-readable JSON artifact with:
  - affidavit proposition rows
  - source review rows
  - explicit statuses:
    - `covered`
    - `partial`
    - `missing_review`
    - `contested_source`
    - `abstained_source`
    - `unsupported_affidavit`
- human-readable markdown summary

Current limitation:
- matching is still lexical/provenance-first rather than deep semantic
  equivalence
- this is correct for the first bounded lane because it keeps review pressure
  explicit instead of hiding uncertain merges

## Acceptance criteria

### P1
- affidavit propositions can be listed and traced to source-grounded rows
- unsupported affidavit propositions remain explicit
- source rows above the configured review threshold can be surfaced as
  missing-review items when absent from the affidavit

### P2
- partial coverage is distinguishable from complete coverage
- contested and abstained source rows do not silently become omissions
- chronology and source class survive into the coverage bundle

### P3
- reviewers can reopen the same run and inspect coverage rows without rerunning
  the source extraction pipeline

## Governance

Promotable claims for this lane:
- the repo can compare affidavit propositions against a provenance-bearing
  source substrate
- omission review is explicit
- ambiguity and contestation survive comparison

Non-claims for this lane:
- the system has extracted every semantically possible fact from a corpus
- the affidavit is legally sufficient
- a missing-review row is automatically a filing omission

## Immediate repo followthrough

- add `SL-US-31` to the user-story source
- add acceptance-matrix coverage for affidavit comparison and omission review
- track an `affidavit_coverage_review` implementation lane in `TODO.md`
- use AU dense-substrate reality as the first planning anchor instead of
  inventing a fresh synthetic-only lane
