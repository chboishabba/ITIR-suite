# Wikidata Combined Assist Handoff

Date: 2026-04-01

## Purpose

This is the current outward-facing first-link handoff for the Wikidata-facing
work in the repo.

It is the shortest repo-backed explanation of:

1. what is now real in the Nat migration-review lane
2. what is now real in the Peter / Ege / Rosario assist lane
3. what we are still not claiming
4. what the next collaboration decisions actually are

## One-line summary

The repo now has two bounded Wikidata-facing lanes:

- a normalized Nat `P5991 -> P14143` migration-review lane
- a bounded Peter / Ege / Rosario assist lane over benchmark shape,
  disjointness, and checked structural handoff

Both are real, review-first, and still explicitly incomplete.

## Current State

### 1. Nat lane

Current repo-pinned progress:

- `7 / 8`
- `87.5%`

What is now pinned:

- revision-locked sandbox proposal capture
- normalized five-cohort mapping
- explicit cohort manifests
- first bounded business-family tranche materialization
- qualifier/reference shape scan over that tranche
- first explicit classification checkpoint over that tranche
- review-only export artifacts for that tranche
- first live Cohort A expansion pass pinned as a bounded tranche

Current bounded Cohort A truth:

- entities:
  `Q10403939` (`Akademiska Hus`)
  `Q10422059` (`Atrium Ljungberg`)
- candidate rows:
  `53`
- classification:
  - `split_required`: `53`
- checked-safe subset:
  none

Plain-language reading:

- the lane is no longer just a sandbox discussion
- it is now a governed review workflow
- the current result is structured split pressure, not safe rewrite
- the first live expansion pass also returned zero checked-safe rows

### 2. Peter / Ege / Rosario assist lane

Current repo-pinned progress:

- `4 / 7`
- `57.142857%`

What is now pinned:

- prior-work/originality boundary
- Rosario benchmark/scorer-shape comparison note
- bounded `P2738` disjointness lane
- checked wiki/Wikidata structural handoff
- explicit assist-lane completion model

Plain-language reading:

- Rosario parity is meaningful but partial on benchmark/scorer shape
- Ege/Peter parity is no longer only adjacent because a real bounded
  disjointness lane exists
- the remaining parity gap is still broader coverage and better culprit
  sophistication

## What This Means

The Wikidata-facing work is now strong enough to hand over in two honest
sentences:

- Nat lane:
  the repo can normalize community migration discussion into bounded review
  cohorts and preserve fail-closed classification state
- assist lane:
  the repo can already provide bounded structural handoff, bounded
  disjointness reporting, and benchmark-shape comparison surfaces without
  claiming full method parity

## What We Are Not Claiming

- We are not claiming full migration readiness for the Nat lane.
- We are not claiming full parity with Rosario.
- We are not claiming full parity with Ege/Peter.
- We are not claiming broad Wikidata ontology cleanup.
- We are not claiming that any current handoff replaces working-group review.

## Next Decisions

### Nat lane

Next branch:

- expand Cohort A beyond the current business-family tranche
- or branch to Cohort C, the higher-risk non-GHG / missing-`P459` lane

The stronger immediate move is still:

- run a targeted checked-safe hunt inside Cohort A first

Reason:

- blind business-family expansion is now less informative because the first
  live tranche also came back entirely `split_required`

### Assist lane

Next branch:

- deepen the `P2738` lane so coverage is no longer the dominant gap
- improve culprit-oriented reporting

The stronger immediate move is:

- push the disjointness lane further before rewriting the outward parity story

Reason:

- the main documented gap is still method maturity, not framing

## Why This Is Useful To Collaborators

### Value to the Wikidata Ontology Working Group

- the repo now exposes bounded, reproducible, review-first migration and
  diagnostic surfaces
- it separates diagnosis from execution
- it preserves provenance and explicit hold states

### Value to Peter / Ege / Rosario-style collaboration

- the repo now has a clearer division between:
  - migration-review work
  - benchmark/scorer-shape comparison
  - disjointness comparison
  - checked downstream handoff
- that makes collaboration easier because each comparison surface is explicit
  rather than collapsed into one novelty claim

## Best Reading Order After This Note

If the reader wants:

- Nat detail:
  `SensibLaw/docs/planning/wikidata_ontology_group_handoff_nat_lane_20260401.md`
- broader lane sequencing:
  `docs/planning/wikidata_combined_roadmap_nat_and_assist_20260401.md`
- assist-lane completion model:
  `docs/planning/wikidata_assist_lane_completion_model_20260401.md`
- checked structural handoff detail:
  `docs/planning/wikidata_structural_handoff_v1_20260325.md`

## ZKP Frame

### O

- ontology working group
- Nat migration reviewers
- Rosario benchmark comparison audience
- Ege/Peter disjointness comparison audience
- repo maintainers and downstream collaborators

### R

- provide one current outward-facing handoff that is honest about both lanes

### C

- this handoff note plus the current Nat and assist completion notes

### S

- Nat is at `7 / 8`
- assist lane is at `4 / 7`
- both lanes are bounded and incomplete

### L

- pinned lane state
- current outward-facing handoff
- later broader external packet

### P

- use this note as the current first-link handoff

### G

- do not overclaim readiness or parity

### F

- both lanes still need more work before a broader completion claim is honest

## ITIL Reading

- service:
  Wikidata collaboration handoff surface
- change class:
  standard change
- goal:
  one coherent current external handoff instead of multiple disconnected notes

## ISO 9000 Reading

- quality objective:
  one authoritative, current, evidence-backed handoff for collaborators
- quality result:
  current progress and current gaps are now stated in one place

## Six Sigma Reading

Observed defect mode:

- collaboration story drift across multiple partial notes

Control response:

- make one note the current first-link handoff and route readers outward from
  there

## C4 / PlantUML

```plantuml
@startuml
title Wikidata Combined Assist Handoff

Component(nat, "Nat Lane", "Migration-review state")
Component(assist, "Assist Lane", "Parity and handoff state")
Component(handoff, "Combined Assist Handoff", "Current first-link note")
Component(group, "Collaborators", "Ontology group / parity audience")

Rel(nat, handoff, "summarized in")
Rel(assist, handoff, "summarized in")
Rel(handoff, group, "shared with")

@enduml
```
