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
- proving-slice read model:
  `build_contested_affidavit_proving_slice(...)`
- proving-slice query surface:
  `SensibLaw/scripts/query_fact_review.py contested-proving-slice`
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
- persisted SQLite review run plus a bounded grouped read model exposing:
  - supported
  - disputed
  - missing
  - needs clarification
  - minimal derived next steps

Current limitation:
- matching is still lexical/provenance-first rather than deep semantic
  equivalence
- this is correct for the first bounded lane because it keeps review pressure
  explicit instead of hiding uncertain merges
- however, this should now be treated as a transitional `v0` matching posture,
  not the intended final reconciliation model
- cross-side duplicate and same-incident sibling handling is still weak:
  a composite response paragraph can support one proposition directly while a
  nearby sibling proposition is incorrectly chosen as the best match

## Johl fixture reading

The live Johl affidavit / response pair should now be treated as the primary
Mary-parity fixture for the next quality step.

Why this fixture matters:
- it pressures family-law and cross-side operator stories directly
- it contains same-incident sibling claims stated on both sides
- it contains shared-root claims with later contextual additions
- it exposes duplicate-root, authority, and contradiction-handling failures
  more clearly than the narrower AU-only fixtures

## Next quality boundary

The next improvement should be a bounded `claim reconciliation` layer rather
than a broader ontology rewrite.

This means the lane should move toward:
- normalized affidavit propositions
- normalized response units
- typed proposition-response relation classification
- dominant relation resolution before final bucket assignment

The target relation set is now:
- `exact_support`
- `equivalent_support`
- `explicit_dispute`
- `implicit_dispute`
- `partial_overlap`
- `adjacent_event`
- `substitution`
- `procedural_nonanswer`
- `unrelated`

The next bounded extension should also add:
- shared `claim_root` / `incident_root` clustering for materially duplicate or
  near-duplicate cross-side claims
- side-local leaf claims beneath that root
- typed authority reading for the matched material:
  source-local assertion, shared-text duplicate, procedural record, or later
  contextual addition

This relation layer should eventually drive the operator-facing bucket surface
more directly than raw similarity scores.

Target bucket reading:
- `supported`:
  exact/equivalent support
- `disputed`:
  explicit/implicit dispute
- `needs_clarification`:
  partial overlap, adjacent event, substitution
- `non_substantive_response`:
  procedural nonanswer
- `missing`:
  unrelated / no viable candidate

Current grouped read model remains valid as a proving-slice surface, but it
should now be interpreted as a bounded bridge toward this richer
relation-driven resolver rather than the final quality model.

Current implementation status:
- the persisted lane now stores relation-led comparison fields directly:
  - `relation_root`
  - `relation_leaf`
  - `primary_target_component`
  - `explanation`
  - `missing_dimensions`
- the proving-slice read model now derives and emits:
  - `relation_root`
  - `relation_leaf`
  - `explanation`
  - `missing_dimensions`
- the proving-slice section layout now includes explicit non-resolving
  subclasses and treats `needs_clarification` as a derived rollup rather than
  the only explanatory class
- a first bounded duplicate-root followthrough now exists in the builder:
  - duplicate or near-duplicate support clauses can now be promoted ahead of a
    nearby contextual clause
  - builder output now emits:
    - `claim_root_id`
    - `claim_root_text`
    - `claim_root_basis`
    - `alternate_context_excerpt`
- the persisted lane still does not fully cluster duplicate roots or
  same-incident sibling leaves before final best-match selection

Current live Johl reading after that first pass:
- `p2-s38` and `p2-s39` now promote to support via duplicate-root handling
- `p2-s5` and `p2-s6` remain unresolved as same-incident sibling-leaf
  cross-swap failures
- `p2-s21` still looks closer to adjacent event or substitution than true
  support

Forward interpretation rule:
- treat `weakly_addressed` as a transitional proving-slice output only
- do not preserve it as a stable target bucket in the next classifier pass
- the next quality step should redistribute those rows into:
  - `partial_support`
  - `adjacent_event`
  - `substitution`
  - `non_substantive_response`

Immediate next implementation priority:
- continue the duplicate-root / incident-cluster pass for cross-side and
  same-incident sibling leaves
- stop the Johl keyboard/audio pair from cross-swapping into the wrong support
  or dispute rows
- keep support, qualification, contradiction, adjacent-event, and procedural
  readings at the leaf level under a shared root

The operator-facing question is no longer just:
- was this proposition touched?

It is now:
- was it supported?
- was it disputed?
- was it only partially answered?
- was the response about a nearby but different event?
- was it a substitution or procedural nonanswer?

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

### P4
- top-line grouped output does not rely on `weakly_addressed` as a mixed
  catch-all bucket
- explicit denials are surfaced as `disputed`
- operator-facing rows include a short explanation:
  classification, matched response, reason, missing dimension

### P5
- materially duplicate or near-duplicate cross-side claims can be grouped
  under one shared root without flattening side-local wording
- same-incident sibling leaves do not cross-swap into the wrong support row
- authority is typed locally to the relation being shown rather than treated
  as one global winner for the whole cluster

## Governance

Promotable claims for this lane:
- the repo can compare affidavit propositions against a provenance-bearing
  source substrate
- omission review is explicit
- ambiguity and contestation survive comparison
- the repo can now articulate the next honest quality boundary as
  duplicate-root and side-local leaf reconciliation, not just stronger
  similarity

Non-claims for this lane:
- the system has extracted every semantically possible fact from a corpus
- the affidavit is legally sufficient
- a missing-review row is automatically a filing omission
- the lane already resolves duplicate-root clustering or cross-side authority
  selection robustly

## Immediate repo followthrough

- add `SL-US-31` to the user-story source
- add acceptance-matrix coverage for affidavit comparison and omission review
- track an `affidavit_coverage_review` implementation lane in `TODO.md`
- use AU dense-substrate reality as the first planning anchor instead of
  inventing a fresh synthetic-only lane
- use `docs/planning/affidavit_claim_reconciliation_contract_20260329.md` as
  the next quality contract for moving beyond similarity-led bucketing
- use the Johl affidavit / response pair as the next Mary-parity fixture for:
  duplicate-root clustering, side-local leaf support/contradiction, and typed
  authority reading
