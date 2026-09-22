# M9 — Personal World → Professional Consumer

Date: 2026-09-22  
Status: implementation handoff contract

## Purpose

M9 proves that the shared-user/world runtime is not merely a legal-world
runtime.

The first capstone is deliberately narrow:

```text
journal / notes / chats / documents / observer inputs
        ↓
provenance-bearing personal world
        ↓
reviewed selected coordinates
        ↓
consumer dependency + scope gate
        ├─ lawyer
        ├─ doctor
        ├─ advocate
        └─ regulator
```

The personal consumer remains first-class. Professional handoff is a projection
of the personal world, not promotion of the whole personal world.

## Existing real substrate

The existing Wave-5 professional-handoff fixture already demonstrates the
source-layer distinctions needed for this milestone:

- user-authored/client account;
- documentary/third-party record;
- later professional note/interpretation;
- uncertainty preservation;
- provenance drill-down;
- abstention/not-ready visibility;
- false-coherence resistance.

Canonical fixture:

```text
itir-svelte/tests/fixtures/
  fact_review_wave5_real_professional_handoff_demo_bundle.json
```

M9 should consume this lineage rather than create a second handoff corpus.

## Production runtime owner

The initial production semantics are in the Rust SensibLaw runtime:

```text
chboishabba/slr

crates/sl-legal-runtime/src/
  personal_world_handoff.rs

crates/sl-legal-runtime/examples/
  personal_world_professional_handoff.rs
```

Formal parity owner:

```text
chboishabba/dashi_agda

DASHI/Law/
  SensibLawPersonalWorldProfessionalHandoffExact.agda
  SensibLawPersonalWorldProfessionalHandoffRegression.agda
```

## First bounded coordinate classes

The initial runtime fixture separates:

```text
reviewed event
reviewed document
reviewed factual proposition
private hypothesis
explicitly-not-ready journal material
```

This is a semantic distinction, not a UI label.

## Admission rule

A coordinate enters a professional projection only when all required gates are
paid:

```text
coordinate exists in shared world
AND consumer dependency slice mentions it
AND coordinate is reviewed
AND role-specific share scope admits it
AND coordinate is not explicitly not-ready
```

A private personal hypothesis remains available to the personal consumer while
being excluded from professional consumers.

An explicitly-not-ready journal coordinate also remains visible to the personal
consumer and is withheld from professional projections.

## Projection receipt

Every professional projection must expose:

```text
consumer_ref
included_coordinate_refs
excluded_coordinate_refs
excluded_reason_refs
unresolved_coordinate_refs
candidate_only
creates_semantic_authority = false
creates_claim_truth = false
```

Important exclusion reasons include:

```text
personal-only-scope
explicitly-not-ready
unreviewed-personal-material
outside-consumer-dependency-slice
scope-not-admitted-for-role
```

The handoff must therefore explain absence rather than silently dropping
coordinates.

## First role slices

The first implementation intentionally makes the professional fibres distinct.

```text
lawyer
  reviewed event
  reviewed document
  reviewed fact

doctor
  reviewed event
  reviewed document
  reviewed fact

advocate
  reviewed event
  reviewed fact

regulator
  reviewed document
  reviewed fact
```

These are milestone fixtures, not universal claims about what every real
lawyer, doctor, advocate, or regulator should receive. Real dependency slices
remain matter/query specific.

## Recompute

M9 reuses the S19 affected-consumer index.

For example:

```text
reviewed fact changes
  → all current professional fixture consumers recompute

reviewed event changes
  → personal + lawyer + doctor + advocate recompute
  → regulator does not recompute
```

Recompute is driven by exact dependency, not professional-role proximity.

## Non-promotion boundaries

The first M9 slice must continue to enforce:

```text
personal availability
  != professional scope

professional scope
  != evidentiary authority

reviewed inclusion
  != claim truth

observer material
  != fact

private hypothesis
  != professional evidence

not-ready
  != missing-data pressure that the system may force closed
```

## Immediate next implementation

The next step is to adapt the existing real Wave-5 bundle into shared-world
coordinates while preserving its real source identifiers and source classes.

That adapter should produce:

```text
real source/fact/statement lineage
        ↓
personal-world coordinate candidates
        ↓
review gate
        ↓
scoped professional projections
        ↓
replayable M9 receipt
```

It must not fabricate review/payment for the currently unreviewed
`User journal account` or `Clinic letter` rows in that fixture.

## M9 closure gate

M9 should close only when:

1. the existing real professional-handoff fixture enters the shared-world path;
2. source provenance and source-class distinctions survive;
3. private/unready material remains available to the personal consumer;
4. selected reviewed coordinates can enter professional slices;
5. different roles receive different fibres;
6. exclusions are explicit and replayable;
7. one reviewed coordinate delta recomputes only exact dependent consumers;
8. no handoff creates semantic authority or claim truth.

That is the first demonstration that S19 is genuinely a Shared **User/World**
Runtime rather than a renamed shared legal world.

## 2026-09-22 implementation checkpoint — explicit scope receipts

The runtime now treats human/governance share scope as an explicit replayable
input rather than something inferred from review state or source class.

New production owners:

```text
chboishabba/slr

crates/sl-legal-runtime/src/
  personal_world_scope_receipt.rs
  wave5_professional_handoff_run.rs

crates/sl-legal-runtime/examples/
  wave5_professional_handoff_scope.rs
```

Formal owners:

```text
chboishabba/dashi_agda

DASHI/Law/
  SensibLawWave5ShareScopeReceiptExact.agda
  SensibLawWave5ShareScopeReceiptRegression.agda
```

The real Wave-5 scope executable deliberately runs with no fabricated human
decision. Its required result is therefore:

```text
therapist-note
  reviewed = true
  share-scope decision = absent
  professional inclusion = none
  unresolved_scope_coordinates contains therapist-note
```

The generic runtime can replay explicit Allow/Deny/NotReady/Withdrawn receipts,
and test-only fixtures prove that distinct professional fibres plus exact delta
recomputation work. Test-only scope receipts are explicitly labelled as not
human governance decisions.

Accordingly, the remaining M9 closure artifact is genuinely external to the
compiler:

```text
one or more explicit human/governance share-scope receipts
        ↓
real Wave-5 projection rerun
        ↓
reviewed scoped coordinate delta
        ↓
exact affected-professional-consumer recompute receipt
```

No review receipt, professional authorship, source class, or personal-world
availability is permitted to substitute for that decision.
