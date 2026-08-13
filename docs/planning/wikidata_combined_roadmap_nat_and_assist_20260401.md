# Wikidata Combined Roadmap: Nat And Assist

Date: 2026-04-01

## Purpose

Record the current execution-order roadmap across:

- the Nat migration lane
- the broader Peter/Ege/Rosario assist lane

## Current Progress

### Nat

- bounded mainline: complete
- wider proof lane: complete
- wider online lane: held pending better reviewer-packet support
- non-company axis integration only, meaning the current company-focused
  tranche is a calibration step rather than a new expansion
- current moonshot gap is now explicit in:
  `SensibLaw/docs/planning/wikidata_nat_gap_to_moonshot_program_20260402.md`
- moonshot-closing lane artifacts now exist for:
  - grounding depth
  - Cohort B review bucket
  - Cohort C live-preview extension
  - Cohort D review lane
  - Cohort E diagnostics lane
  - automation graduation criteria
- the stronger reproducible operator surfaces now also exist for the same
  axis:
  - grounding-depth CLI plus batch report
  - Cohort B operator packet, queue, and report
  - Cohort C operator report and batch report
  - Cohort D operator review queue and operator report
  - Cohort E diagnostics CLI plus batch report
  - automation-graduation CLI plus batch evaluation
- the next broader measured-evidence layer now also exists:
  - grounding-depth evidence report
  - Cohort B operator batch report
  - Cohort C broader measured evidence sample
  - Cohort D operator report batch
  - Cohort E grouped diagnostics summary
  - automation-graduation repeated-run evidence report
- the next broader operator/governance layer now also exists:
  - grounding-depth comparison/index report
  - Cohort B operator evidence index
  - Cohort C operator index
  - Cohort D review-control index
  - Cohort E summary index
  - automation-graduation governance index
- adjacent Wikibase/Wikidata transport references have now been identified:
  - `https://github.com/Superraptor/Wikibase-Wikidata-Pipeline`
  - `https://github.com/Superraptor/wikiodk`
  These are not replacement runtimes for the Nat lane. Treat them as external
  adapter/reference surfaces for local Wikibase setup, local-Wikibase to
  Wikidata mapping, missing-statement/reference detection, and possible
  reviewed upload handoff.

### Assist Lane

- still partial and review-first
- continue only with materially broader bounded coverage
- the OCTF-facing assist framing should now mention the Claire/Superraptor
  repositories as adjacent references when explaining where transport/edit
  tooling ends and the ITIR/SensibLaw admissibility layer begins

## Recommended Order

1. treat the April 12 Family A-E routing table as the current action taxonomy:
   - Family A: `full_auto`
   - Family B: `split_auto`
   - Family C: repair plus migrate
   - Family D: review-only typed hold
   - Family E: manual reconstruction
2. build the generic Nat reviewer-packet layer:
   - deepen evidence grounding on representative hard packets
   - use the existing helper lanes as promotion evidence rather than as
     packet-shape expansion
3. use Cohorts B/C/D/E as the next structural breadth axis, with Cohort C as
   the highest-yield immediate branch
4. turn the report helpers into broader measured backlog evidence over real
   candidate slices
5. turn those repeated runs into higher-level operator/governance indexes
   before claiming stronger automation readiness
6. define explicit automation graduation criteria and exercise them with real
   proposal batches, repeated-run evidence, and governance indexes before any
   stronger moonshot-readiness claim
7. add a narrow adapter-spike for external Wikibase/Wikidata deltas:
   - input: mapped candidate delta from a local Wikibase or Wikidata sync tool
   - normalization: convert subject/predicate/object/reference diffs into the
     existing bounded candidate/change-review packet shape
   - output: review-only disposition report, not edit authority
   - optional handoff: only checked-safe/reviewed rows can be exported back to
     an uploader or OpenRefine-style staging surface
8. advance the assist lane only when broader bounded coverage or better
   culprit-oriented reporting is real

## Why This Order

Nat already proved:

- checked-safe handling
- wider direct-safe scarcity
- split-plan verification

So the highest-value next layer is closing the automation-readiness gap:
grounding, structural breadth, and promotion gates.

The key clarification is that source cohorts and action families are separate
axes. Nat Cohort A does not mean Family A. Family A means a row is clean enough
for `full_auto`; Family B means it is structured enough for `split_auto`; Family
C/D/E explain why a row needs repair, review-only hold, or manual
reconstruction.

The external-reference clarification adds a second boundary: transport is not
admissibility. `Wikibase-Wikidata-Pipeline` is useful because it can discover
and potentially upload mapped Wikibase/Wikidata statement/reference deltas.
`wikiodk` is useful because it shows a local Wikibase/ODK import sandbox path.
The ITIR/SensibLaw contribution remains the bounded review and governance
surface: candidate deltas become `ChangeReviewPacket`-style inputs, run through
structural/provenance checks, and emerge as checked, held, contradictory, or
insufficiently supported review artifacts before any staging/export path is
trusted.
