# Zelph NLnet Grant Draft

Date: 2026-04-01

## Change Class

Standard change.

## Purpose

Freeze a bounded, grant-ready draft that Stefan can reuse without drifting past
the repo's actual Zelph doctrine.

This note is intentionally narrower than the general handoff docs. Its job is
to answer one question:

- what is the smallest credible artifact package we can honestly offer around
  the current `SensibLaw/ITIR -> Zelph` boundary?

## Thread Provenance

- title:
  `Strategic Contribution Advice`
- online UUID:
  `69cbf880-05ec-839a-8603-8532ca426638`
- canonical thread ID:
  `b0499d873b1a162931c96a0a8e016b9906da540a`
- source used:
  `web` pull into canonical archive, then `db` resolution

## One-Sentence Goal

Produce a reproducible fact-construction module and integration demo that lets
Zelph reason over unstructured-text-derived corpora through deterministic,
provenance-preserving graph facts.

## Primary Users

- developers working with semantic graph systems
- researchers building verifiable reasoning pipelines
- engineers who need reproducible `text -> graph facts -> inference` workflows

## Lower-Bound Deliverable

- deterministic `text -> reviewed facts` pipeline over one small corpus
- Zelph integration showing fact ingestion plus bounded reasoning
- one reproducible end-to-end demo:
  `text -> facts -> inference -> output`

## Existing Proof We Already Have

- working deterministic export surfaces from SensibLaw into Zelph
- successful bounded Zelph integration over real repo corpora
- reviewed handoff artifacts for GWB and AU (it added this, we can if you like - faster to ask me re these)
- fixture/test-backed bridge surfaces and operator-facing provenance discipline

Canonical proof surfaces:
- `docs/planning/zelph_external_handoff_20260320.md`
- `docs/planning/wikidata_zelph_single_handoff_20260325.md`
- `SensibLaw/sl_zelph_demo/compile_db.py`
- `SensibLaw/tests/test_sl_zelph_demo_tools.py`
- `SensibLaw/tests/fixtures/zelph/gwb_public_handoff_v1/`
- `SensibLaw/tests/fixtures/zelph/au_public_handoff_v1/`

## Non-Goals

- no claim that Zelph should ingest raw text directly inside its own runtime
- no claim of full ontology completion or broad autonomous fact extraction
- no claim that the current handoff pack is the final long-term collaboration
  contract
- no promise of personal/case-linked corpus sharing

## Current Honest Pitch

The grant-safe offer is:

- SensibLaw/ITIR handles deterministic extraction, review, and provenance
- Zelph consumes the exported structured facts for bounded downstream reasoning
- the grant funds the smallest reproducible bridge artifact that makes that
  boundary obvious and reusable

## ZKP Frame

### O

- Stefan as grant applicant / external downstream collaborator
- ITIR/SensibLaw as the upstream extraction and review surface
- Zelph as the downstream reasoning engine
- reviewers/funders who need a bounded, credible open-technology deliverable

### R

- define a deliverable small enough to finish and demonstrate quickly
- keep the claim aligned with what the repo already proves
- avoid phrasing that turns a bounded bridge into a vague platform promise

### C

- `docs/planning/zelph_external_handoff_20260320.md`
- `docs/planning/zelph_handoff_index_20260324.md`
- `docs/planning/wikidata_zelph_single_handoff_20260325.md`
- `SensibLaw/sl_zelph_demo/`
- `SensibLaw/tests/fixtures/zelph/`

### S

- the repo already supports a real `SL -> Zelph` bridge story
- current docs already say SensibLaw is upstream and Zelph is downstream
- the fetched thread sharpened the missing piece:
  grant framing should center the lower-bound deliverable rather than the full
  future collaboration surface
- the risky wording to avoid is "Zelph directly operates on raw text"
- the safe wording is:
  unstructured text is converted into deterministic provenance-preserving facts
  before Zelph reasoning begins

### L

1. one corpus selected
2. deterministic extraction path fixed
3. reviewed facts emitted
4. Zelph ingests the exported facts
5. demo shows bounded inference output
6. artifact is reproducible by others

### P

- keep the proposal centered on one reproducible bridge artifact
- reuse existing handoff/test surfaces as proof rather than promising new
  platform breadth
- describe the deliverable as a fact-construction module plus integration demo
- preserve explicit non-goals so reviewers see scope control

### G

- no repo wording may imply that Zelph replaces SensibLaw truth construction
- no repo wording may imply unreviewed raw-text ingest inside Zelph
- external claims must remain bounded to reproducible artifacts already close
  to current repo reality
- if the call requires broader promises than this, the draft must be narrowed
  or explicitly split into future work

### F

- the repo had handoff material but not one compact grant-ready note
- the grant wording still needed a cleaner lower-bound deliverable statement
- the remaining external gap is form-field mapping and budget text, not core
  technical framing

## ITIL Reading

- service:
  bounded reproducible bridge from reviewed text-derived facts into Zelph
- change type:
  standard documentation/governance clarification
- risk:
  low if the scope remains lower-bound and artifact-first
- backout:
  revert this note if future external positioning changes or if Stefan needs a
  different funder-specific framing

## ISO 9000 Reading

Quality objective:

- make the proposed deliverable testable, bounded, and consistent with current
  repo evidence

Quality controls:

- one-sentence goal names one artifact and one capability
- lower-bound deliverable is small and reproducible
- existing proof section cites concrete repo surfaces
- non-goals prevent scope inflation

## ISO 42001 Reading

Relevant AI-governance posture:

- deterministic and provenance-preserving construction is preferred over opaque
  automation claims
- operator review remains explicit before downstream reasoning
- the proposal does not hide uncertainty or promote raw text directly into
  reasoning authority

## ISO 27001 Reading

Information-security posture:

- use small reviewed corpora for the outward-facing demo
- avoid personal or case-linked material in the grant-facing artifact
- keep provenance and artifact boundaries explicit so shared outputs remain
  auditable

## Six Sigma Reading

Primary defect classes this framing is meant to reduce:

- vague grant promises that cannot be finished on time
- overclaiming deep integration beyond current repo evidence
- hidden scope creep from corpus expansion or ontology ambition
- ambiguity about where truth construction stops and reasoning begins

## C4 View

### Context

- unstructured source corpus is upstream evidence
- SensibLaw/ITIR extracts and reviews facts
- Zelph consumes the structured fact artifact
- funder/reviewer evaluates the bounded reproducible output

### Container

- corpus selection and ingest layer
- deterministic fact construction layer
- review/provenance layer
- Zelph bridge/demo layer
- reproducible output/report layer

## PlantUML

```plantuml
@startuml
title Zelph NLnet Lower-Bound Deliverable

Component(SOURCE, "Source Corpus", "Small reviewed text set")
Component(SL, "SensibLaw/ITIR", "Deterministic fact construction + provenance")
Component(REVIEW, "Review Gate", "Checked facts / abstentions")
Component(ZELPH, "Zelph", "Bounded downstream reasoning")
Component(DEMO, "Reproducible Demo", "text -> facts -> inference -> output")

Rel(SOURCE, SL, "ingest")
Rel(SL, REVIEW, "emit fact candidates + provenance")
Rel(REVIEW, ZELPH, "export reviewed facts")
Rel(ZELPH, DEMO, "bounded inference output")
Rel(SL, DEMO, "reproducible artifacts")
@enduml
```

## Current Honest Claim

Stefan can safely say:

- there is already a real deterministic bridge from reviewed structure into
  Zelph
- the proposed grant would package that bridge as a reproducible fact
  construction module plus demo
- this is a bounded first collaboration slice, not a claim of full raw-text
  reasoning or completeness
