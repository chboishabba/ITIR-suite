# Wikidata Combined Roadmap: Nat And Assist Lanes

Date: 2026-04-01

## Change Class

Standard change.

## Purpose

Record one combined roadmap for:

- completing the Nat `P5991 -> P14143` migration-review lane
- completing the Peter / Ege / Rosario Wikidata assist lane

This note is intentionally about execution ordering and honest progress
reporting. It does not widen any lane's authority.

## Inputs

- `SensibLaw/docs/planning/wikidata_ontology_group_handoff_nat_lane_20260401.md`
- `SensibLaw/docs/wikidata_working_group_status.md`
- `docs/planning/wikidata_parity_gap_note_rosario_ege_20260325.md`
- `docs/planning/wikidata_p2738_disjointness_lane_20260325.md`
- `docs/planning/wikidata_structural_handoff_v1_20260325.md`

## ZKP Frame

### O

Actors and surfaces:

- Nat (WDU) migration proposal and ontology working group
- Ege Doğan / Peter Patel-Schneider disjointness comparison surface
- Rosario benchmark / scorer comparison surface
- SensibLaw Wikidata diagnostics, migration, review, and handoff artifacts
- repo maintainers deciding sequencing and promotion

### R

Required outcome:

- complete the Nat lane through verified migration-review readiness
- complete the Peter/Ege/Rosario assist lane through a stronger,
  reviewer-legible parity/assist packet
- keep both lanes bounded, provenance-aware, and honest about remaining gaps

### C

Primary code and artifact surfaces:

- Nat lane:
  - `SensibLaw/docs/planning/wikidata_nat_lane_cohort_manifests_20260401.md`
  - `SensibLaw/docs/planning/wikidata_nat_cohort_a_seed_slice_20260401.md`
  - `SensibLaw/docs/planning/wikidata_nat_cohort_a_shape_scan_20260401.md`
- assist lane:
  - `docs/planning/wikidata_parity_gap_note_rosario_ege_20260325.md`
  - `docs/planning/wikidata_p2738_disjointness_lane_20260325.md`
  - `docs/planning/wikidata_structural_handoff_v1_20260325.md`
  - `SensibLaw/src/ontology/wikidata_disjointness.py`

### S

Current state is asymmetric:

- Nat lane already has a repo-pinned completion model
- assist lane now also has a repo-pinned completion model; it is narrower and
  lower-confidence on method parity than Nat, but no longer only inferred

That means the roadmap must distinguish:

- repo-owned progress count
- derived progress count

### L

Combined ordering:

1. complete the Nat lane to verified bounded migration-review readiness
2. complete the assist lane to stronger parity/assist maturity
3. only then collapse them into one broader outward-facing Wikidata assist
   packet

### P

Proposal:

- finish Nat first because it is already normalized into explicit milestones
- use that completion to strengthen the ontology-group-facing migration story
- then deepen the assist lane where the remaining gaps are still primarily
  coverage, culprit sophistication, and combined handoff coherence

### G

Governance:

- Nat progress numbers must stay tied to the pinned completion model
- assist-lane progress numbers must stay tied to the pinned completion model
- no lane should claim parity or execution readiness just because it has one
  readable handoff artifact

### F

Main current gap:

- Nat is structurally ahead but not yet execution-complete
- assist lane has meaningful bounded substance but still needs broader coverage
  and better culprit sophistication before it is execution-complete

## Lane 1: Nat

### Current progress

Repo-pinned progress:

- `7 / 8`
- `87.5%`

Source:

- `SensibLaw/docs/planning/wikidata_ontology_group_handoff_nat_lane_20260401.md`

### Completed

1. proposal captured
2. task buckets mapped into cohorts
3. review cohort manifests pinned
4. first bounded Cohort A tranche materialized
5. Cohort A shape scan completed
6. Cohort A classification checkpoint completed
7. review-only export artifacts produced

### Remaining

8. post-edit verification

### Completion roadmap

Phase 1:
- run a targeted checked-safe hunt inside Cohort A rather than continue blind
  business-family expansion

Phase 2:
- if no promoted subset appears, branch to Cohort C, the non-GHG /
  missing-`P459` lane

Phase 3:
- DONE: emit explicit review-only outputs for the classified subset

Phase 4:
- run post-edit verification on any promoted subset

### Exit condition

Nat is complete only when:

- at least one bounded promoted subset has both export and after-state
  verification
- the remaining unresolved cohorts are explicit held or review-only states,
  not silent unfinished work

## Lane 2: Peter / Ege / Rosario Assist

### Current progress

This lane now has a repo-pinned completion model.

- `4 / 7`
- `57.142857%`

Source:

- `docs/planning/wikidata_assist_lane_completion_model_20260401.md`

Completed:

1. prior-work/originality governance pinned
2. Rosario-adjacent benchmark/scorer shape achieved in bounded form
3. Ege/Peter-adjacent bounded `P2738` disjointness lane implemented
4. checked structural handoff artifact exists

### Current documented posture

The local docs still say:

- Rosario parity is meaningful but partial
- Ege/Peter parity is improved from purely adjacent, but still below method
  parity on coverage and culprit sophistication

That remains the correct reading.

### Remaining

5. broader `P2738` coverage beyond the current bounded slice family
6. stronger culprit sophistication and closer disjointness-method parity
7. one combined reviewer-facing assist packet instead of scattered parity,
   handoff, and originality notes

### Completion roadmap

Phase 1:
- deepen the disjointness lane so coverage is no longer the dominant parity gap

Phase 2:
- strengthen culprit-oriented reporting and working-group usefulness

Phase 3:
- convert the current partial-parity state into one explicit Peter/Ege/Rosario
  assist packet with:
  - prior-work positioning
  - disjointness capability summary
  - benchmark/scorer-shape summary
  - checked structural handoff summary

### Exit condition

The assist lane is complete only when:

- broader disjointness coverage exists
- culprit sophistication is no longer the main documented gap
- one combined outward-facing assist packet can be handed over without
  requiring a reader to reconstruct state from multiple planning notes

## Recommended Sequence

1. Finish Nat first.
2. Then finish the assist lane.
3. Then produce one combined outward-facing Wikidata assist handoff.

Reason:

- Nat already has a crisp finish line and explicit milestones.
- The assist lane still needs its own finish line made first-class.
- Completing Nat first reduces ambiguity in the ontology-group migration story.

## ITIL Reading

- service portfolio:
  Nat migration-review lane plus Wikidata parity/assist lane
- change class:
  standard change
- sequencing rule:
  finish the lane with the clearer service milestones first

## ISO 9000 Reading

- quality objective:
  standardized, auditable completion criteria across both Wikidata-facing lanes
- current quality gap:
  Nat has explicit completion accounting; assist lane now has it too, but the
  finish lines are different in scope and maturity

## Six Sigma Reading

Current variation source:

- inconsistent progress accounting between lanes

Control response:

- preserve the distinction between repo-pinned progress and derived progress
- do not flatten “partial parity” into “done”

## C4 / PlantUML

```plantuml
@startuml
title Combined Wikidata Roadmap

Component(nat, "Nat Lane", "Migration-review workflow")
Component(assist, "Peter/Ege/Rosario Assist Lane", "Parity / assist workflow")
Component(group, "Ontology Working Group", "Reviewer / collaborator surface")
Component(outward, "Combined Assist Handoff", "Future external packet")

Rel(nat, group, "migration-review handoff")
Rel(assist, group, "parity / assist handoff")
Rel(nat, outward, "must complete before")
Rel(assist, outward, "must complete before")

@enduml
```
