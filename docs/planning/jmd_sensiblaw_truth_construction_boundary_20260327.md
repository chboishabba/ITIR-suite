# JMD x SensibLaw Truth-Construction Boundary (2026-03-27)

## Purpose
Record the boundary clarified by the archived `Zero Trust Ontology` thread so
the repo does not drift into treating `SensibLaw` as a generic JMD runtime,
token layer, or execution fabric.

This is a planning note. It sharpens the existing JMD -> SL bridge doctrine and
does not add a new runtime contract.

## Source Context
- resolved via `robust-context-fetch`
- title: `Zero Trust Ontology`
- online UUID: `69c68637-ca2c-839e-826c-f5e8a034ed2e`
- canonical thread ID: `c2571b2b17183df38dd03704cf6e34f7bee44392`
- source used: `db` after direct UUID pull into `~/chat_archive.sqlite`

## Main Decision
Keep `SensibLaw` framed as the truth-construction layer between:

- messy input or corpus substrates
- downstream reasoning, optimisation, and agent layers

In this boundary:

- upstream sources may be JMD objects, legal corpora, Wikipedia, logs, or
  similar evidence-bearing substrates
- `SensibLaw` owns extraction, anchoring, reversible normalization, candidate
  assembly, promotion gates, and explicit abstention
- downstream systems such as `Zelph`, `DASHI`, or other agent/reasoning layers
  consume canonical or explicitly typed non-canonical outputs; they do not turn
  `SensibLaw` into the execution fabric itself

## Why This Matters
The thread sharpened a useful analogy:

- "law as meme" and "repeated motifs" can be read as the same abstraction only
  if the repo keeps the bridge disciplined
- that analogy is helpful as research framing, but not sufficient as a runtime
  contract
- the repo still needs source anchors, reversible transforms, candidate state,
  promotion basis, and abstention behavior expressed concretely

So the actionable reading is not "integrate SL into everything JMD is doing".
The actionable reading is:

> treat `SensibLaw` as the controlled boundary where messy evidence becomes
> anchored candidate structure and, only through promotion, truth-bearing
> canonical records

## Boundary Decomposition
### Upstream
- canonical source objects or revision-locked text
- external corpora and object graphs, including future JMD-facing substrates

### SensibLaw
- deterministic or governed extraction
- reversible normalization
- source-anchored annotations
- candidate fact / observation / event assembly
- explicit promotion and abstention control

### Downstream
- governed reasoning
- compression / invariance / DASHI-style collapse
- proof, audit, export, and agent-facing projections

## Contract Implications
- keep the near-term JMD lane as:
  read-only object graph -> SL corpus / candidate / promotion boundary
- do not describe `SensibLaw` as the JMD task executor, scheduler, or infra
  substrate
- graph usefulness claims must show more than graph richness:
  they should expose semantic drift, provenance conflicts, chronology tension,
  or repeated structure while preserving the promotion boundary
- motif/meme/cohomology language remains optional explanatory framing unless it
  cashes out into explicit source-anchored records, transforms, or proofs

## Non-Goals
- not a commitment to immediate JMD-side implementation work
- not a claim that JMD architectural enthusiasm equals readiness for upstream
  integration
- not a replacement for the existing authority split:
  JMD authoritative objects, SL truth-construction and promotion governance,
  Casey governed proposal handling, StatiBaker receipts

## Followthrough
- keep `docs/planning/jmd_sl_corpus_bridge_contract_20260319.md` as the
  bridge contract note
- keep `docs/planning/jmd_triage_roadmap_20260320.md` as the phase-order note
- use this note when updating TODOs or handoff language so "JMD integration"
  does not collapse ontology talk, runtime talk, and `SensibLaw` governance
  into one bucket
