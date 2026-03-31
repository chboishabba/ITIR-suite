# Wikidata Assist Lane Completion Model

Date: 2026-04-01

## Purpose

Pin a local completion model for the Peter / Ege / Rosario Wikidata assist
lane so the repo stops relying on an inferred progress estimate.

This note is the bounded finish-line document for the assist lane. It does not
claim parity or reproduction. It defines what "done enough for now" means in
repo-backed terms.

## Scope

The assist lane covers three linked comparison surfaces:

- Rosario benchmark/scorer adjacency
- Ege / Peter `P2738` disjointness adjacency
- checked wiki/Wikidata handoff parity

## ZKP Frame

### O

Actors and surfaces:

- Wikidata Ontology Working Group
- Rosario benchmark comparison surface
- Ege / Peter disjointness comparison surface
- checked wiki/Wikidata handoff surface
- repo maintainers

### R

Required outcome:

- turn the assist lane from inferred progress into a formally pinned completion
  model
- keep prior-work boundaries explicit
- make the lane finishable by milestones rather than by vibe

### C

Primary artifact surfaces:

- `docs/planning/wikidata_parity_gap_note_rosario_ege_20260325.md`
- `docs/planning/wikidata_p2738_disjointness_lane_20260325.md`
- `docs/planning/wikidata_structural_handoff_v1_20260325.md`
- `SensibLaw/docs/wikidata_working_group_status.md`

### S

Current repo-backed state:

- Rosario parity is meaningful but partial
- Ege/Peter parity is improved but still below method parity on coverage and
  culprit sophistication
- one checked wiki/Wikidata handoff artifact already exists
- one bounded `P2738` disjointness lane already exists
- there was no repo-pinned completion model for the assist lane before this
  note

### L

Assist-lane ordering now becomes:

1. pinned prior-work boundary note
2. bounded disjointness lane
3. checked structural handoff artifact
4. formal assist completion model
5. broader coverage / culprit sophistication improvements
6. combined outward-facing assist packet

### P

Proposal:

- define the assist lane as complete enough when the repo has:
  - explicit prior-work boundaries
  - a bounded disjointness lane
  - a checked structural handoff artifact
  - one combined outward-facing assist packet
- keep the model narrow enough to be usable as a status document

### G

Governance:

- no parity claim beyond what the docs explicitly support
- progress counts are only valid if they can be explained against pinned
  milestones
- inferred progress may still be used as a derived state, but the milestone
  model is now the source of truth

### F

Gap closed by this note:

- the assist lane now has a formal local completion model

Remaining gap:

- the assist lane still needs broader disjointness coverage and better culprit
  sophistication before it is actually complete

## Completion Model

The assist lane is measured against seven bounded milestones:

1. prior-work / originality boundary pinned
2. Rosario parity gap note pinned
3. bounded `P2738` disjointness lane exists
4. checked wiki/Wikidata structural handoff exists
5. disjointness coverage expands beyond the initial bounded lane
6. culprit sophistication improves beyond the current bounded method
7. one combined outward-facing assist packet exists

Current repo state:

- completed: `1`, `2`, `3`, `4`
- remaining: `5`, `6`, `7`

Pinned progress baseline:

- `4 / 7`
- `57.142857%`

Interpretation:

- this is now a formal model, not just an inferred estimate
- the model is intentionally conservative because it counts only artifacts that
  are directly pinned in the repo

## Exit Conditions

The assist lane is complete enough when:

- the remaining gaps are explicitly documented as partial rather than hidden
- the combined outward-facing assist packet can be assembled without inventing
  new parity claims

## ITIL Reading

- service:
  Wikidata assist / comparison workflow
- change class:
  standard change
- success measure:
  the lane has an explicit service-level completion model instead of an
  informal estimate

## ISO 9000 Reading

- quality objective:
  traceable completion criteria with explicit evidence for each milestone
- quality result:
  the assist lane can now be reported with the same discipline as the Nat
  lane, even though its finish line is narrower

## Six Sigma Reading

Observed defect mode:

- progress drift from implied status

Control response:

- make milestones explicit and count only pinned milestones

## C4 / PlantUML

```plantuml
@startuml
title Wikidata Assist Lane Completion Model

Component(parity, "Rosario / Ege-Peter Parity Notes", "Boundary and comparison surfaces")
Component(disjointness, "P2738 Disjointness Lane", "Bounded method slice")
Component(handoff, "Checked Structural Handoff", "Reviewed artifact")
Component(model, "Assist Completion Model", "Pinned milestones")
Component(packet, "Combined Assist Packet", "Future outward-facing output")

Rel(parity, model, "defines boundaries")
Rel(disjointness, model, "contributes coverage")
Rel(handoff, model, "contributes checked handoff evidence")
Rel(model, packet, "leads to")

@enduml
```
