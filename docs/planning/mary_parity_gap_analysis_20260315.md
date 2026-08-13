# Mary-Parity Gap Analysis

Date: 2026-03-15
Purpose: identify what the expanded user stories say is still missing after the
current transcript/AU fact-review implementation.

Status note:
- This document captured the gap picture before the later acceptance waves were
  implemented.
- Current parity status and remaining priorities are now better summarized in
  `docs/planning/mary_parity_status_audit_20260315.md`.

## Current strengths

### 1. Shared substrate now exists
- transcript and AU both land in the same fact-review contract
- observations are canonical
- events are derived and evidence-backed
- stored runs are queryable later

### 2. Operator summaries are now real
- review queue exists
- contested summary exists
- chronology summary exists
- run list / summary / chronology / full report are queryable by CLI

### 3. Provenance-first posture is intact
- source -> excerpt -> statement -> observation -> event/fact links are
  preserved
- no reasoning-first or verdict-first drift has been introduced

## Primary gaps by story pressure

### Gap A: legal/procedural observation richness is still thin
Impacts:
- `SL-US-12`
- `SL-US-13`
- `SL-US-14`
- `SL-US-15`
- `SL-US-16`
- `SL-US-18`

Current state:
- predicate catalog supports legal/procedural rows
- actual extraction/pipeline coverage is still narrow outside current AU lane

Needed:
- stronger real extraction/population for
  `claimed`, `denied`, `admitted`, `ordered`, `ruled`
- clearer display of party assertion vs procedural outcome in reports

### Gap F: contested wiki / Wikidata moderation surfaces are not yet explicit
Impacts:
- `SL-US-15`
- `SL-US-16`
- `SL-US-18`

Current state:
- GWB is the main public-figure and contested-public-material proving lane
- wiki/Wikidata infrastructure exists, but not yet as a Mary-parity
  fact-review acceptance family for moderation-sensitive claims

Needed:
- curated highly contested public-figure fixture families
- explicit allegation/denial/finding/unsupported splits
- moderation-safe and defamation-sensitive review posture over those runs

### Gap G: mereology / institutional-boundary inspection is still weak
Impacts:
- `SL-US-16`
- `SL-US-17`
- `SL-US-18`

Current state:
- actor/organization/jurisdiction distinctions exist in pieces
- review bundles do not yet strongly foreground office-holder vs institution vs
  campaign/government/body boundaries

Needed:
- stronger inspection of person/office/organization/jurisdiction structure
- curated fixtures where responsibility boundaries are contested
- no silent merge of personal and institutional actors

### Gap H: public-figure legality assessment fixtures are not yet curated
Impacts:
- `SL-US-18`
- `SL-US-19`
- `SL-US-20`
- `SL-US-21`
- `SL-US-22`
- `SL-US-23`
- `SL-US-24`

Current state:
- GWB is the current parity proving lane
- there is no explicit curated family for:
  - clearly unlawful/proven-illegal circumstances
  - plausibly unlawful / legally dubious circumstances
  - clearly lawful / authorized comparison cases

Needed:
- a bounded public-figure legality fixture set, likely including GWB and Trump
- side-by-side provenance-first review over proven, alleged, and dubious cases
- no legal conclusion emitted by default

### Gap I: family-law / cross-side provenance handoff is not yet a parity lane
Impacts:
- `SL-US-25`
- `SL-US-26`
- `SL-US-27`
- `SL-US-28`

Current state:
- chronology and contested review infrastructure exists
- but family-law and child-sensitive cross-side review is not yet an explicit
  fixture or acceptance family

Needed:
- bounded family-law and cross-side fixture sets
- stronger side distinction, child-sensitive context, and handoff-safe posture
- explicit acceptance around provenance-preserving transfer between recipients

Status update:
- closed as an acceptance-lane gap
- now a real-fixture-depth and operator-polish gap rather than a missing lane

### Gap J: medical / professional-discipline overlap fixtures are not yet curated
Impacts:
- `SL-US-29`
- `SL-US-30`

Current state:
- observation/event substrate is capable of supporting these matters
- but there is no explicit fixture family for treatment chronology,
  professional complaint, investigation, finding, and sanction staging

Needed:
- bounded medical-negligence and professional-discipline fixture sets
- explicit review surfaces for record vs allegation vs later interpretation
- stronger stage distinction for complaint/investigation/finding/sanction

Status update:
- closed as an acceptance-lane gap
- remains thin on real-fixture depth

### Gap B: review queue semantics are present but still generic
Impacts:
- `SL-US-09`
- `SL-US-11`
- `ITIR-US-12`
- `ITIR-US-14`

Current state:
- queue reasons exist
- contested summary exists

Needed:
- more role-meaningful reasons:
  - missing date
  - missing actor
  - contradictory chronology
  - uncorroborated statement-only fact
- queue grouping or filtering by issue type

### Gap C: chronology ergonomics are backend-good but not yet role-shaped
Impacts:
- `SL-US-13`
- `SL-US-14`
- `ITIR-US-11`
- `ITIR-US-13`

Current state:
- chronology report exists
- dated vs undated counts exist

Needed:
- better chronology views over:
  - sparse dates
  - approximate dates
  - procedural vs substantive events
  - contradiction clusters tied to chronology

### Gap D: support/advocacy-safe reporting posture is not yet explicit enough
Impacts:
- `ITIR-US-13`
- `ITIR-US-14`
- `ITIR-US-15`
- `ITIR-US-16`
- `SL-US-09`
- `SL-US-10`

Current state:
- backend posture is provenance-first and non-reasoning

Needed:
- explicit support-safe / read-only export posture
- clearer distinction between direct statement, later annotation, and review
  note
- stronger “follow-up need” framing rather than institutionalized certainty

### Gap K: anti-false-coherence / anti-AI-psychosis pressure is not yet explicit
Impacts:
- `ITIR-US-16`
- `ITIR-US-13`

Current state:
- uncertainty, abstention, and provenance are present
- but the system does not yet explicitly test whether review surfaces resist
  false coherence escalation on sparse, high-conflict material

Needed:
- acceptance checks for contradiction preservation and abstention visibility
- explicit “not enough evidence” posture in high-conflict review outputs
- fixture families that stress narrative hardening risk

Status update:
- closed as an acceptance-lane gap
- now represented in `wave5_handoff_false_coherence`

### Gap E: persisted-run navigation still relies on copied run IDs
Impacts:
- `SL-US-11`
- `SL-US-13`
- `ITIR-US-12`

Current state:
- runs are listable/queryable once you have or can discover the fact run

Needed:
- stable mapping from source workflow run IDs to fact-review run IDs
- easier reopening from transcript/AU semantic runs into the fact-review layer

## Priority order informed by stories

### Next implementation priority
1. richer review queue reasons and contested/chronology triage
2. workflow-run -> fact-run mapping / reopen ergonomics
3. legal/procedural observation visibility and extraction widening
4. contested wiki/Wikidata/public-figure fixture families for moderation and
   legality-assessment pressure
5. stronger person/office/organization/jurisdiction boundary visibility
6. family-law and cross-side provenance-preserving fixture families
7. medical / professional-discipline overlap fixture families

### Hold for later
1. role-specific UI polish
2. broader doctrinal reasoning
3. Mary-beyond parity semantic layers

## Recommendation for the resumed loop

Resume the Mary-parity loop with this order:

1. tighten review queue semantics
2. add run-mapping / reopen ergonomics
3. widen procedural/legal observation visibility
4. curate contested public-figure fixture families
5. add moderation / mereology / legality-assessment acceptance passes

This order best serves the newly expanded operator stories while keeping the
current substrate stable.
