# Portable Semantic Reading Trail Design — 2026-09-15

## Purpose

Define the shared human-interaction layer for ITIR/SensibLaw reading, proof exploration, PNF-assisted comprehension, source inspection, and bounded rabbit-hole navigation without turning UI components into semantic owners.

This design sits above canonical SensibLaw/SLR world/proof state and below the first concrete frontend interpreter, ITIR/Svelte.

It complements, rather than replaces:

- the Mabo Reading Workbench v0 planning surface;
- the progressive proof explanation workbench;
- JCUI semantic interaction intent;
- StatiBaker temporal continuity;
- WikimediaWorldWalk local world buckets;
- canonical SensibLaw/SLR proof/source machinery.

## Architectural law

The primary split is:

```text
semantic interaction intent
!= frontend widget
!= DOM selector
!= physical gesture
!= semantic mutation
```

A click, Enter key, tap, voice command, native control activation, or fake-driver step may all implement the same semantic intent.

Correctness is consumer-indexed. A frontend interpreter need only preserve the observation promised by the interaction:

```text
Q_C(interpret_frontend(intent)) = Q_C(meaning(intent))
```

This does not imply identical pixels, syntax, scheduling, implementation language, or performance.

## Shared semantic intents

The first bounded vocabulary is:

- `ExplainSpan(spanRef)`
- `ExplainRole(spanRef)`
- `WhyClaim(claimRef)`
- `OpenSource(sourceRef)`
- `ExploreEntity(entityRef)`
- `FollowReference(referenceRef)`
- `ExpandProofCone(claimRef)`
- `Back(trailRef)`

These are semantic operations. ITIR/Svelte is the first interpreter. JCUI may encode/replay them, but browser selectors are not the canonical language.

## Admissibility

An intent executes only when the current world/projection can support the requested query and policy allows disclosure:

```text
Admissible(I)
iff
CapabilitySupports(I)
and ReferencesResolve(I,W)
and DisclosurePermits(I,P)
and Q_I FactorsThrough AvailableProjection(W)
```

Interpretation yields one of:

- `Execute(action, receipt)`
- `Defer(residual)`
- `Reject(defect)`

A local failure does not imply global failure.

Example:

```text
OpenSource(exactJudgmentSpan)
-> ExactQuotation does not factor through Skeleton
-> defer with reacquisition/materialisation residual
-> verify source identity/digest
-> retry OpenSource
```

The UI must not invent source text or silently widen authority when a local projection is insufficient.

## Progressive disclosure

The reader starts with readable prose. Deeper structure appears only on demand:

```text
readable proposition
subset explanation
subset source inspection
subset proof cone
subset wider world/context
```

The default interaction grammar is:

```text
Orient -> Project -> Why? -> Source -> Meaning -> Follow -> Back / Next unresolved
```

Dense information is compressed by grouping and progressive disclosure, not by rendering every identifier, proof edge, QID, PNF tuple, residual, and citation simultaneously.

## Sibling projections

The product keeps three sibling projections separate:

```text
TemporalRibbon : when / temporal mass / life-event projection
SemanticTrail  : what this expression/object connects to while reading
ProofCone      : why this proposition follows, fails, or remains unresolved here
```

`TimelineRibbonLite` remains a StatiBaker temporal/accounting consumer. It is not the parent abstraction for semantic/proof navigation.

## PNF reading-comprehension mode

PNF is reused as a reading-comprehension overlay, not replaced by a second parser.

The first disclosure should be human language:

```text
who / did what / to what / under what condition
```

and only later, when useful:

```text
actor / predicate / patient / modifier / antecedent / dependency
```

Legal reading additionally benefits from emphasising modal and structural operators such as `must`, `may`, `cannot`, `unless`, `subject to`, negation, conditions, exceptions, attribution wrappers, and actor/patient changes.

A role overlay does not create proposition truth, legal authority, comprehension, or evidence payment.

## Constituent and composite semantic targets

A multi-token expression may expose both a composite referent and independently meaningful constituent targets.

Example:

```text
They wove a panel from golden spider silk.
```

Possible semantic targets include:

- `They` — actor/antecedent-resolution target;
- `wove` — action/predicate target;
- `panel` — patient/product target;
- `golden spider silk` — composite material/referent target;
- `silk` — independently meaningful constituent/material target;
- potentially `golden spider` — independently meaningful constituent/entity target when the producer has a supported weld.

The important rule is:

```text
constituent target != composite target
```

and neither target automatically inherits every property, identity, source, or authority relation of the other.

A composite target may be a joint product or phrase-level referent while a constituent such as `silk` remains a first-class semantic object with its own source, ontology, and follow trail.

The UI should therefore support nested/overlapping semantic spans without forcing one canonical clickable tokenisation.

## Mabo flagship

The first flagship remains reader-like first.

Landing question:

> Why was Mabo such a big deal?

The default page is short prose with understated semantic affordances. The bounded five-ish-node chain appears on `Why?`, not by default:

```text
prior proposition
-> challenged premise
-> Mabo proposition
-> legal consequence
-> qualification / downstream application
```

Each node/phrase can invoke the same portable intents:

- Explain
- Meaning
- Why
- Source
- Explore context
- Follow
- Back

The proof graph is something the user enters, not the screen they start inside.

## Wiki/Wikidata/source context

Wiki/Wikidata remain context/navigation coordinates, never authority merely by inclusion.

A context trail may expose:

```text
canonical object
<-> Wikidata identity
<-> revision-locked Wikipedia/context page
-> cited references
-> explicitly followed source
-> source/provenance receipt
```

Firewalls:

```text
QID != applicability
Wikipedia != legal authority
context link != evidence payment
outbound link != promoted fact
```

## Relation to world buckets

The Reading Trail projects from a potentially much larger local world bucket:

```text
available world >> displayed world
```

The user may rabbit-hole and re-root locally without publishing the whole bucket or their navigation history.

Publishing a selected world remains distinct from publishing a Reading Trail:

```text
publish selected world != publish browsing history
```

StatiBaker may optionally receive temporal interaction receipts only under explicit policy. Such receipts do not imply belief, comprehension, preference, or semantic truth.

## Formal boundaries to mirror in DASHI

The intended formal firewalls are:

```text
UIIntent !=> SemanticMutation
FollowEntity !=> IdentityPromotion
WikiContext !=> LegalAuthority
OpenProofCone !=> ClaimTruth
HiddenFromView !=> AbsentFromWorld
UnavailableLocally !=> GloballyUnavailable
RejectedIntent !=> GlobalFailure
RoleOverlay !=> Comprehension
CompositeTarget != ConstituentTarget
```

The existing query-factorisation and reopenability machinery should own the adequacy/reopening proofs. No new confidence calculus is introduced.

## First implementation slice

The first frontend interpreter is ITIR/Svelte and should reuse existing selection/source/graph primitives rather than create a parallel semantic state.

The first slice needs only enough vocabulary to demonstrate two consumers over the same machinery:

1. Mabo legal reading: `WhyClaim -> OpenSource -> ExploreEntity -> ExpandProofCone -> Back`.
2. Reading comprehension: `ExplainRole -> ExploreEntity -> FollowReference -> Back`.

JCUI can replay the same semantic intents against fake state and ITIR application state. Browser selectors remain a later physical rendering/accessibility check.

## Non-goals

This design does not:

- replace the existing proof graph;
- make Streamlit the product UI;
- merge StatiBaker with SensibLaw;
- infer comprehension or belief from interaction;
- make Wikipedia/Wikidata authoritative;
- require global graph loading for a local question;
- require pixel-identical frontend implementations;
- treat compound phrases as indivisible semantic atoms.

## Acceptance criteria

The design is successful when:

- a lay reader can understand the first Mabo proposition without seeing a graph;
- clicking `Why?` reveals only a bounded local proof cone;
- clicking `Source` reopens exact source material or returns an explicit materialisation residual;
- PNF/grammar overlays remain optional and literal text remains primary;
- a composite phrase and its meaningful constituents can each be explored independently;
- Wiki/Wikidata/source-follow context remains visibly distinct from legal authority;
- Back restores the previous semantic locus;
- JCUI can express the same semantic journey without CSS/DOM selectors;
- no interaction receipt is interpreted as belief, comprehension, truth, or authority.
