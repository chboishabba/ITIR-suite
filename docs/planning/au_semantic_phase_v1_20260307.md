# Australian Semantic Phase v1 (2026-03-07)

## Purpose
Bring the Australian proving lane up to the same semantic maturity and
auditability standard as the current GWB lane without changing the frozen
semantic v1.1 storage shape.

## Chosen Defaults
- non-famous people default to document-local canonical actors
- judges may resolve globally when title/surname cues are strong
- the first Australian deliverable is reviewed seed import + report parity
- the frozen v1.1 shape remains:
  - unified entity spine
  - mention resolution
  - event_role -> relation_candidate -> semantic_relation
- no Australian-specific schema fork unless pressure-testing proves a concrete
  failure

## Initial Australian proving set
- `Mabo [No 2]`
- `Plaintiff S157/2002 v Commonwealth`
- `House v The King`
- `Native Title (New South Wales) Act 1994`

## Current v1 seed/report lane
- reviewed seed import tables:
  - `au_semantic_linkage_imports`
  - `au_semantic_linkage_seeds`
  - `au_semantic_linkage_seed_authorities`
  - `au_semantic_linkage_seed_refs`
  - `au_semantic_linkage_seed_cues`
  - `au_semantic_linkage_matches`
  - `au_semantic_linkage_match_receipts`
- report sections:
  - per-seed
  - per-event
  - ambiguous events
  - unmatched seeds

## Initial actor policy
- non-famous participants are document-local canonical actors by default
- current supported participant patterns:
  - appellant
  - respondent
  - plaintiff
  - defendant
  - accused
  - applicant
- titled individuals may resolve to document-local actors
- legal representatives now have first deterministic coverage:
  - `counsel for the appellant/respondent`
  - `senior counsel for the appellant/respondent`
  - titled representative surfaces ending in `SC` / `KC` / `QC`
- explicit office surfaces now have first deterministic coverage:
  - `Attorney-General`
  - `Registrar`
- weak discourse/forum labels such as `the Court` abstain unless stronger
  evidence exists

## Initial relation policy
Wave 1 predicates:
- `appealed`
- `challenged`
- `heard_by`
- `decided_by`

Wave 2 predicates enabled for candidate/promoted coverage where supported:
- `applied`
- `followed`
- `distinguished`
- `held_that`
- low-confidence `decided_by` candidates are now also retained when `held`
  surfaces support the decision lane but stronger promotion evidence is still
  missing

Promotion remains conservative and receipt-derived. Candidate-only rows are
preferred over weak promotion.
