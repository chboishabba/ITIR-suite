# M10 — Unified Workbench

Date: 2026-09-23  
Status: first bounded capstone source-written

## Purpose

M10 does not introduce a second semantic store and does not redesign the product
around a new UI ontology.

It projects the already-existing shared user/world runtime into a progressive
operator surface:

```text
Journal
  ↓
Timeline
  ↓
Handoff
  ↓
Matter / Proof
  ↓
Research
```

Every stage is a view over persisted/canonical state. A stage may be:

```text
available
blocked
unavailable
```

and those statuses are semantic UX signals, not truth values.

## First host

The existing fact-review route remains the first workbench host:

```text
itir-svelte/src/routes/graphs/fact-review/+page.svelte
```

The first read-model owner is:

```text
itir-svelte/src/lib/workbench/unifiedWorkbench.js
```

The first real regression fixture remains:

```text
itir-svelte/tests/fixtures/
  fact_review_wave5_real_professional_handoff_demo_bundle.json
```

## First projection contract

The read model emits:

```text
version
selected_fact_id

stages:
  journal
  timeline
  handoff
  matter_proof
  research

stage_by_key

invariant:
  shared_world_only = true
  derived_projection_only = true
  creates_semantic_authority = false
  creates_claim_truth = false
```

## Stage semantics

### Journal

Shows the selected persisted fact and its exact source/statement lineage.

### Timeline

Shows an existing chronology projection when present.

If the selected fact has no assembled event, the stage is `blocked`; the
workbench does not infer chronology to make the navigation look complete.

### Handoff

Shows the existing professional-handoff projection.

A fact that is not in the current handoff fibre is `blocked`, not silently
included.

### Matter / Proof

Shows the existing legal-follow/proof graph when one is attached.

If no legal proof graph exists, the stage is `unavailable`.

This is a critical firewall:

```text
personal/handoff material
!= legal applicability
!= proof payment
```

The UI must never synthesize a legal proof merely to complete the stage chain.

### Research

Shows existing persisted review/follow pressure:

- review queue;
- contested items;
- authority-follow queue.

It does not manufacture a new residual merely because the operator opened the
Research stage.

## Core invariants

```text
changing view depth
  != changing world state

hidden
  != discarded

blocked
  != false

unavailable
  != false

opening Matter/Proof
  != paying a legal atom

opening Research
  != creating a residual

rendering a projection
  != creating semantic authority
  != creating claim truth
```

## Formal owner

The projection invariants are mirrored in:

```text
chboishabba/dashi_agda

DASHI/Law/
  SensibLawUnifiedWorkbenchProjectionExact.agda
  SensibLawUnifiedWorkbenchProjectionRegression.agda
```

## First capstone behaviour

Using the real Wave-5 professional-handoff workbench:

```text
Journal       available
Timeline      blocked/unavailable where no event exists
Handoff       available only for handoff-selected rows
Matter/Proof  unavailable because Wave-5 has no legal proof graph
Research      available where persisted review pressure exists
```

This is a successful M10 result. The point is not to make every stage green;
the point is to preserve the real shape of the same world across the stage
sequence.

## M10 next tranche

The next implementation step should attach the same unified projection contract
to a workbench that actually has a legal-follow graph, then prove:

```text
selected source/fact
    ↓
same source/provenance coordinates
    ↓
Matter / Proof
    ↓
existing legal graph nodes/edges
    ↓
Research residual / follow pressure
```

without copying or reinterpreting semantic state.

The natural next fixture is an existing AU fact-review bundle with
`legal_follow_graph`, not a synthetic M10-only specimen.

## M10 closure gate

M10 should close when:

1. real personal/handoff workbench traverses the stage model without fabricated
   proof state;
2. real legal-follow workbench traverses the same stage model with proof state;
3. exact provenance coordinates remain reopenable across stages;
4. absent stages remain explicit;
5. navigation never changes authority/payment/truth;
6. route-level UI regressions and focused Agda owners pass.

The full product can later add richer Journal, Matter, Proof, Mission, Research,
Source and Comparative views, but those are expansions of this contract rather
than prerequisites for M10 correctness.
