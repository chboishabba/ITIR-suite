# Affidavit Reconciliation Text Normalization (2026-03-30)

## Purpose
Record the first bounded normalization slice for duplicated affidavit
reconciliation text helpers inside Python-owned lanes.

This note does not claim the broader affidavit reconciliation problem is solved.
It only fixes one concrete duplication seam that should not remain stranded
inside a Google Docs wrapper script.

## Problem

The affidavit lane is already Python-owned, but some reconciliation-adjacent
text handling still lives inline inside:

- `SensibLaw/scripts/build_google_docs_contested_narrative_review.py`

That wrapper currently owns its own:

- enumeration-prefix stripping
- duplicate-filter tokenization
- overlap similarity scoring
- duplicate affidavit-unit detection
- contested response block grouping

This is the wrong long-term shape.

Those helpers are not Google-Docs-specific product glue. They are a bounded
piece of affidavit reconciliation text policy.

## Required boundary

Keep the affidavit lane Python-owned, but also keep it normalized inside
Python.

For this slice:

- wrapper scripts may orchestrate fetch / parse / persist flow
- shared reconciliation-text helpers should live in a reusable Python module
- future affidavit or contested-response builders should import the shared
  helper instead of cloning duplicate tokenization/grouping logic

## First bounded extraction

Extract the Google Docs duplicate-heading grouping helpers into a shared module
that exposes:

- duplicate-filter tokenization
- enumeration-prefix stripping
- token-overlap similarity
- duplicate affidavit-unit detection
- contested response unit grouping

The first adopter remains:

- `SensibLaw/scripts/build_google_docs_contested_narrative_review.py`

## Non-goals

This slice does not yet:

- replace the broader reconciliation heuristics in
  `SensibLaw/scripts/build_affidavit_coverage_review.py`
- unify every tokenizer or lexical heuristic in the affidavit lane
- solve duplicate-root / sibling-leaf clustering fully
- claim a final proposition/relation normalization core

## Acceptance

This slice is complete when:

- the Google Docs contested narrative wrapper no longer owns those helpers
- the helpers live behind one Python-owned reusable module
- focused tests pin duplicate-heading grouping behavior
- docs, TODO, implementation, and changelog all describe the same slice
