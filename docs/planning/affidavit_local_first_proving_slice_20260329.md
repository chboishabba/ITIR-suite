# Affidavit Local-First Proving Slice (2026-03-29)

## Purpose
Pin the first bounded proving slice decision for the current ITIR/SensibLaw
production path.

This note answers a narrower question than the general service architecture:
what should be implemented first if the goal is to prove that the suite can
turn fragmented narrative/evidence into a reviewable, trustworthy local-first
artifact?

## Decision
Use the existing affidavit coverage/review lane as the first
SQLite/local-first proving slice for narrative-integrity work.

This is a proving slice for:
- story -> structure
- provenance anchoring
- supported / disputed / missing / unresolved comparison
- reviewable local-first artifact persistence

It is not the first slice for:
- obligation/SLA execution
- actor/fallback escalation workflows
- broad ordinary-user guidance

Those remain better served by a tenancy/actionability slice later.

## Why affidavit, not tenancy, first

### What affidavit proves best
- fragmented lived narrative can be compared against source-grounded material
- omission pressure can stay explicit rather than being silently flattened
- contested and abstained material can survive comparison
- the review artifact can remain non-moralizing and provenance-first
- SQLite/local-first persistence already exists in the repo for this lane

### What tenancy would prove better
- obligation creation
- deadlines / SLA handling
- actor/fallback assignment
- escalation paths

So the lane split is:
- affidavit first for narrative integrity and evidence structure
- tenancy later for obligation execution

## Existing repo substrate to reuse
Do not invent a parallel affidavit runtime.

The current proving slice must build on:
- builder:
  `SensibLaw/scripts/build_affidavit_coverage_review.py`
- Google Docs wrapper:
  `SensibLaw/scripts/build_google_docs_contested_narrative_review.py`
- persisted SQLite receiver:
  `persist_contested_affidavit_review(...)`
- contested review read model:
  `SensibLaw/src/fact_intake/read_model.py`
- query surface:
  `SensibLaw/scripts/query_fact_review.py`

This means the immediate next implementation move should be a bounded local
read-model/workbench refinement over the existing lane rather than a new
architecture.

## Proving slice runtime target
- runtime target:
  SQLite local-first
- fixture posture:
  one fixture-backed affidavit flow
- persisted store:
  local `itir.sqlite`

## Required proving-slice outputs
The first affidavit proving slice should expose:
- one persisted review run
- one summary surface over that run
- one read model grouped into:
  - supported
  - disputed
  - weakly addressed
  - missing
  - needs clarification
- one short next-step list derived from explicit counts/statuses

To improve real affidavit runs, the proving slice may also tighten
proposition decomposition before matching:
- split long affidavit sentences into bounded clause-level propositions when
  there is clear punctuation-level evidence such as semicolons
- do not invent semantic clause boundaries beyond those explicit textual cues
- prefer smaller reviewable propositions over one large proposition that mixes
  multiple events, motives, and consequences

These outputs should be enough to answer:
- what affidavit propositions are source-backed?
- what is disputed or unsupported?
- what source-side material is still missing review or clarification?

## Scope guardrails
- do not widen this slice into a general case-management product
- do not force obligation modeling into affidavit review where it does not fit
- do not replace the current provenance-first matching posture with hidden
  semantic collapse
- do not claim legal sufficiency from the proving slice

## Immediate implementation target
Add one bounded proving-slice read model and query surface over persisted
contested affidavit review runs.

That means:
- keep SQLite/local-first
- reuse the existing persisted review tables
- expose grouped statuses plus minimal next steps
- let explicit response-role / support-state signals improve proving-slice
  grouping without inflating `covered`
- expose opt-in progress reporting for long-running live builders so fetch,
  proposition matching, artifact writing, and persistence do not look hung
- expose opt-in trace reporting for proposition-level review work so operators
  can stream:
  sentence -> proposition -> tokens -> candidate selection -> classification
  -> semantic basis -> promotion result
- add focused regression tests over the new surface

## Relationship to existing notes
This note narrows the production path described in:
- `docs/planning/itir_sensiblaw_postgres_schema_and_deployment_bundle_20260328.md`
- `docs/planning/itir_sensiblaw_production_schema_dashboard_deployment_pack_20260328.md`
- `docs/planning/affidavit_coverage_review_lane_20260325.md`

The practical reading is now:
- first proving slice for evidence/narrative integrity:
  affidavit + SQLite local-first
- later proving slice for obligation/action execution:
  tenancy
