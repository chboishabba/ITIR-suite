# M10 — Unified Workbench

Date: 2026-09-23  
Status: Dioxus/wgpu production host active; first bounded capstone source-written

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

## Canonical production host

The production Unified Workbench host is now:

```text
chboishabba/itir-dioxus
```

with Dioxus owning ordinary shell UI and wgpu owning charts, proof topology and
interaction-heavy visualisation through a framework-neutral Visualisation IR.

The prior Svelte implementation:

```text
itir-svelte/src/routes/graphs/fact-review/+page.svelte
itir-svelte/src/lib/workbench/unifiedWorkbench.js
```

is **not** the production M10 host. It remains only a useful read-model /
regression reference for the already-checked Wave-5 projection semantics. New
M10 UI work must not extend that surface.

The first real regression fixture remains owned by ITIR-suite:

```text
itir-svelte/tests/fixtures/
  fact_review_wave5_real_professional_handoff_demo_bundle.json
```

The fixture remains a data/acceptance input even though the production UI has
moved to `itir-dioxus`.

## Dioxus/wgpu projection contract

The production architecture is:

```text
canonical ITIR/SensibLaw world
        ↓
framework-neutral workbench read model / Visualisation IR
        ↓
        ├── Dioxus shell projection
        └── wgpu visual projection

Dioxus event ──┐
               ├──> same admitted DomainCommand ──> canonical reducer
GPU pick ──────┘
```

Permanent boundaries:

```text
DioxusEvent != SemanticMutation
GpuPick     != SemanticMutation

VisualisationIR != canonical graph store

hidden from visual
!= absent from world

projection change
!= authority change
!= truth change
!= payment
```

No production semantic command ABI should depend on JSON/regex decoding.

## Current Rust owner

The first production implementation now lives in:

```text
chboishabba/itir-dioxus

src/workbench/mod.rs
src/visual/command.rs
src/visual/selection.rs
src/visual/ir.rs
src/visual/gpu.rs
src/app.rs
```

It already models:

- fixed Journal → Timeline → Handoff → Matter/Proof → Research ordering;
- available / blocked / unavailable states;
- Wave-5 personal/handoff calibration without fabricated chronology/proof;
- an AU legal-bearing constructor that makes Matter/Proof available only when
  persisted legal graph nodes actually exist;
- shell selection and GPU picking decoding to the same `DomainCommand`;
- a shared selection reducer;
- framework-neutral Graph/Chart visual IR;
- a feature-gated wgpu projection boundary.

## Stage semantics

### Journal

Shows persisted facts/sources/statement lineage.

### Timeline

Shows an existing chronology projection when present.

If no assembled event exists, the stage is blocked/unavailable. The workbench
must not infer chronology merely to make the navigation look complete.

### Handoff

Shows existing scoped professional-handoff state.

A coordinate not in the admitted handoff fibre remains blocked/excluded rather
than silently included.

### Matter / Proof

Shows an existing legal-follow/proof graph when attached.

If no legal proof graph exists, the stage is `unavailable`.

This is a critical firewall:

```text
personal/handoff material
!= legal applicability
!= proof payment
```

The UI must never synthesize a legal proof merely to complete the stage chain.

### Research

Shows existing persisted review/follow pressure and residuals. Opening the view
does not manufacture new research work.

## Formal owner

Projection invariants remain mirrored in:

```text
chboishabba/dashi_agda

DASHI/Law/
  SensibLawUnifiedWorkbenchProjectionExact.agda
  SensibLawUnifiedWorkbenchProjectionRegression.agda

DASHI/Core/
  PortableInteractiveViewExact.agda
```

and the Dioxus/wgpu bridge must continue to refine those formal boundaries
rather than inventing frontend authority.

## First capstone behaviour

Using the real Wave-5 professional-handoff material:

```text
Journal       available
Timeline      unavailable where no event exists
Handoff       blocked while real share scope is unresolved
Matter/Proof  unavailable because Wave-5 has no legal proof graph
Research      available where real review/follow pressure exists
```

This is a successful M10 result. The point is not to make every stage green;
the point is to preserve the real shape of the same world.

## M10 current next tranche

The next empirical weld is the complementary legal-bearing run:

```text
real AU persisted legal_follow_graph
        ↓
itir-dioxus UnifiedWorkbenchReadModel
        ↓
Journal / source
        ↓
Timeline if persisted event exists
        ↓
Matter / Proof = available
        ↓
exact persisted legal graph nodes/edges
        ↓
Research/follow pressure
```

Do not edit an old fixture to invent missing legal graph state.

The first GPU-backed specimen should then render those persisted legal/proof
refs through `VisualisationIr`, with Dioxus selection and GPU picking producing
the same admitted semantic command.

## M10 closure gate

M10 closes when:

1. the Dioxus host runs the real personal/handoff workbench without fabricated
   chronology/proof;
2. a real legal-bearing AU workbench traverses the same read model with exact
   persisted proof nodes/edges;
3. source/provenance coordinates remain reopenable across stages;
4. unavailable/blocked stages remain explicit;
5. Dioxus and GPU selection paths decode to the same domain command/reducer;
6. one bounded wgpu proof/source graph renders from framework-neutral IR;
7. navigation/rendering never changes semantic authority, truth or payment;
8. focused Rust/Dioxus and Agda receipts pass.

Richer Journal, Matter, Proof, Mission, Research, Source and Comparative views
are later expansions of this contract rather than prerequisites for M10
correctness.
