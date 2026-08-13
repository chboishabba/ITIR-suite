# Mary-Parity User Story Acceptance Matrix

Date: 2026-03-15
Purpose: map the expanded Mary-parity user stories onto concrete substrate and
operator capabilities so implementation order stays role-driven.

## Scope

Stories covered:
- `SL-US-09` through `SL-US-14`
- `SL-US-15` through `SL-US-18`
- `SL-US-19` through `SL-US-28`
- `SL-US-29` through `SL-US-31`
- `ITIR-US-11` through `ITIR-US-14`
- `ITIR-US-15` through `ITIR-US-16`

Current substrate assumptions:
- canonical seam:
  `source -> excerpt -> statement -> observation -> event/fact -> review bundle`
- transcript and AU both land in `fact.review.bundle.v1`
- persisted runs are queryable with run summaries, review queue, contested
  summary, and chronology reporting

## Capability matrix

### Source/provenance drill-down
- Required by:
  - `SL-US-09`
  - `SL-US-11`
  - `SL-US-12`
  - `SL-US-13`
  - `SL-US-15`
  - `SL-US-18`
  - `SL-US-19`
  - `SL-US-20`
  - `SL-US-21`
  - `SL-US-22`
  - `SL-US-23`
  - `SL-US-24`
  - `SL-US-25`
  - `SL-US-26`
  - `SL-US-27`
  - `SL-US-28`
  - `ITIR-US-11`
  - `ITIR-US-15`
  - `ITIR-US-14`
- Current coverage:
  - covered in stored fact-intake report and review bundles
- Acceptance checks:
  - every fact links to statement/excerpt/source IDs
  - every event links to evidence observations
  - operator can inspect stored runs without rerunning extraction

### Explicit uncertainty / abstention / contestation
- Required by:
  - `SL-US-09`
  - `SL-US-10`
  - `SL-US-12`
  - `SL-US-14`
  - `SL-US-15`
  - `SL-US-18`
  - `SL-US-19`
  - `SL-US-20`
  - `SL-US-21`
  - `SL-US-22`
  - `SL-US-23`
  - `SL-US-24`
  - `SL-US-25`
  - `SL-US-26`
  - `SL-US-27`
  - `SL-US-28`
  - `ITIR-US-11`
  - `ITIR-US-13`
  - `ITIR-US-14`
  - `ITIR-US-15`
  - `ITIR-US-16`
- Current coverage:
  - covered at observation/fact/event status level
  - covered by contested summary and review queue reasons
- Acceptance checks:
  - abstained rows remain visible
  - contradictory facts can coexist
  - contested items are summarized separately from chronology

### Chronology-first review
- Required by:
  - `SL-US-09`
  - `SL-US-11`
  - `SL-US-13`
  - `SL-US-14`
  - `SL-US-15`
  - `SL-US-18`
  - `SL-US-19`
  - `SL-US-21`
  - `SL-US-22`
  - `SL-US-23`
  - `SL-US-25`
  - `SL-US-26`
  - `SL-US-27`
  - `SL-US-28`
  - `ITIR-US-11`
  - `ITIR-US-12`
  - `ITIR-US-13`
  - `ITIR-US-14`
  - `ITIR-US-15`
  - `ITIR-US-16`
- Current coverage:
  - event chronology and fact chronology both available
  - chronology summaries now report dated vs undated density
- Acceptance checks:
  - event chronology remains reconstructable from observation evidence
  - dated vs undated material is explicit
  - chronology does not silently imply certainty when dates are sparse

### Review queue / operator follow-up
- Required by:
  - `SL-US-09`
  - `SL-US-11`
  - `SL-US-12`
  - `SL-US-15`
  - `SL-US-18`
  - `SL-US-19`
  - `SL-US-20`
  - `SL-US-21`
  - `SL-US-22`
  - `SL-US-23`
  - `SL-US-24`
  - `SL-US-25`
  - `SL-US-26`
  - `SL-US-27`
  - `SL-US-28`
  - `ITIR-US-12`
  - `ITIR-US-14`
  - `ITIR-US-15`
- Current coverage:
  - persisted run summary and bundles include review queue
- Acceptance checks:
  - queue reasons include unreviewed / contested / uncertain / abstained
  - queue rows are linked to provenance-bearing facts
  - operator can reopen queue from a stored run

### Corpus-to-affidavit coverage accounting
- Required by:
  - `SL-US-31`
- Current coverage:
  - partial; the source side is now real through transcript/AU dense-substrate
    and fact-review artifacts, but affidavit comparison is not yet a first-class
    persisted review lane
- Acceptance checks:
  - affidavit propositions can be linked to source-grounded rows or marked
    unsupported explicitly
  - source rows above a configured review threshold can surface as omission
    review items when absent from the affidavit
  - contested or abstained source rows remain distinct from clear omissions
  - comparison rows keep provenance-bearing source and affidavit handles
  - cross-side duplicate or near-duplicate claims can be grouped under one
    shared claim root without flattening side-local wording
  - same-incident sibling leaves do not cross-swap into the wrong support row
  - support, qualification, contradiction, and adjacent-event relations are
    resolved at the leaf level within a shared root

### Legal/procedural observation visibility
- Required by:
  - `SL-US-12`
  - `SL-US-13`
  - `SL-US-14`
  - `SL-US-15`
  - `SL-US-16`
  - `SL-US-18`
- Current coverage:
  - scaffold only; predicate catalog exists, but legal/procedural extraction is
    still narrow in real pipelines
- Acceptance checks:
  - procedural/legal predicates are visible as observations or event
    attributes
  - party assertions vs procedural outcomes stay distinguishable

### Moderation / defamation-risk posture
- Required by:
  - `SL-US-15`
  - `SL-US-16`
  - `SL-US-18`
- Current coverage:
  - partial; provenance-first and non-reasoning posture exists, but
    moderation-sensitive public-figure handling is not yet an explicit review
    lane
- Acceptance checks:
  - allegation, denial, finding, and unsupported assertion remain separable
  - the system does not emit guilt/defamation conclusions
  - high-conflict public-figure material keeps source-local wording and contestation

### Structural / mereological boundary visibility
- Required by:
  - `SL-US-16`
  - `SL-US-17`
  - `SL-US-18`
- Current coverage:
  - partial; actor/organization/jurisdiction signals exist, but institutional
    and office-capacity boundaries are still weak in the current fact-review
    surface
- Acceptance checks:
  - person, office, organization, and jurisdiction remain distinguishable
  - office-holder and institution are not silently merged
  - structural ambiguity remains inspectable

### Family-law / cross-side affidavit reconciliation
- Required by:
  - `SL-US-25`
  - `SL-US-26`
  - `SL-US-28`
  - `SL-US-31`
- Current coverage:
  - partial; provenance-first coexistence is real, but duplicate-root
    clustering and side-local leaf reconciliation are still weak in the
    affidavit lane
- Acceptance checks:
  - John-side and Johl-side wording remain side-local
  - materially duplicate claims can share one root cluster
  - later context or qualification does not silently erase the shared root
  - contradiction is asserted at the leaf level, not by flattening the whole
    cluster into one side's wording

### Public-figure legality assessment posture
- Required by:
  - `SL-US-18`
- Current coverage:
  - partial; chronology/provenance/review bundle exists, but there is not yet a
    curated public-figure legality fixture family
- Acceptance checks:
  - proven unlawful, alleged, and legally dubious cases remain distinguishable
  - procedural posture and legal observations remain visible enough for
    theory-testing
  - public narrative volume does not become hidden authority

### Read-only / non-reasoning posture
- Required by:
  - `SL-US-14`
  - `ITIR-US-13`
  - `ITIR-US-14`
  - `ITIR-US-16`
- Current coverage:
  - backend surfaces are descriptive only
- Acceptance checks:
  - no recommendation or legal conclusion is emitted by review/query surfaces
  - reports remain provenance-first and inspection-only

### Anti-false-coherence / anti-AI-psychosis posture
- Required by:
  - `ITIR-US-13`
  - `ITIR-US-16`
- Current coverage:
  - partial; explicit uncertainty and abstention exist, but this posture is not
    yet treated as its own acceptance family
- Acceptance checks:
  - sparse contradictory material does not silently collapse into one story
  - abstention and unresolved state remain explicit
  - the system does not default to psychologizing or conspiracy-style coherence

## Priority implications

### P1
- strengthen review queue semantics and operator summaries
- strengthen chronology ergonomics and dated/undated clarity
- keep source drill-down stable across transcript and AU

### P2
- widen real legal/procedural observation coverage beyond current AU relation
  mapping
- add support/advocacy-safe export/report shapes
- add a first bounded affidavit-coverage review lane over the existing AU/Mary
  dense substrate and persisted fact-review machinery
- add contested Wikipedia/Wikidata/public-figure fixture families for
  moderation and legality-assessment pressure
- add stronger mereology and institutional-boundary inspection over those runs
- add family-law and cross-side fixture families with child-sensitive,
  provenance-preserving handoff pressure

### P3
- role-specific presentation tuning after the core substrate is stable

## Immediate test pressure

Before resuming the Mary-parity loop, the next implementation passes should be
judged against these questions:

1. Does this reduce ambiguity for `SL-US-09` / `SL-US-11` / `SL-US-13`?
2. Does this preserve explicit uncertainty for `ITIR-US-11` / `ITIR-US-13` /
   `ITIR-US-14`?
3. Does it improve stored-run reopen/query behavior for `ITIR-US-12`?
