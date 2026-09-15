# Adaptive Semantic Reader and Elucidatory Cone — 2026-09-16

## Purpose

Extend the existing Mabo Reading Workbench into a portable semantic reader without creating a second proof, parser, source, or world model.

The human primitive is:

```text
Explain(D, q, delta)
```

where `D` is the focused semantic detail, `q` is the user's question/intent, and `delta` is the disclosure/detail budget.

The reader is a projection over existing SensibLaw/SLR state. It does not own truth, authority, evidence payment, identity promotion, or source acquisition.

## Core recurrence

```text
focus detail
-> local PNF/semantic neighbourhood
-> adaptive elucidatory expansion
-> acquire only if a required coordinate is unpaid
-> compact semantic payload
-> human rendering
-> SLR/PNF parity + source/provenance check
-> repair or expose residual
```

Semantic expansion and source acquisition are distinct. Local material is tried first. SLR acquisition is invoked only for an explicit residual.

## Adaptive depth

Graph distance is only a base neighbourhood. A farther node may survive projection when its explanatory value for the current question is high.

```text
Keep(x) := distance(D,x) <= baseDepth
           OR elucidatoryValue(x | D,q,context) >= threshold
```

This is not a global importance score and does not mutate canonical graph state.

## Semantic targets

Targets are first-class identities with at least:

```text
spanRef
targetKind
surface
semanticRef
role?
entityRef?
sourceRef?
```

Nested and overlapping targets are required. A constituent and a composite target remain distinct even when their source spans overlap.

Example:

```text
They wove a panel from golden spider silk.
```

`They`, `wove`, `panel`, `golden spider silk`, `golden spider`, and `silk` may each be independent targets when supported by the current semantic projection.

## Portable semantic intents

The bounded UI vocabulary is:

```text
ExplainSpan
ExplainRole
WhyClaim
OpenSource
ExploreEntity
FollowReference
ExpandProofCone
Back
```

Frontend gesture != semantic intent != semantic mutation.

Each intent resolves to one of:

```text
Execute(action)
Defer(residual)
Reject(defect)
```

Local unavailability does not imply global failure.

## Progressive disclosure

Default order:

```text
readable proposition
subset explanation
subset source inspection
subset proof cone
subset wider world/context
```

Lay mode hides QIDs, hashes, all residual classes, source-role taxonomies, graph internals, and alternative paths by default.

The same semantic cone can drive plain explanation, simple-language explanation, legal explanation, grammar/PNF lesson, flashcard, question, comparison, or source inspection.

## Reading-comprehension cues

Human labels first:

```text
who / did what / to what / under what condition
```

Technical labels are optional:

```text
actor / predicate / patient / negation / modality / condition / temporal / coreference
```

Role overlays are navigation/learning aids only. They do not prove comprehension, belief, proposition truth, legal authority, or evidence payment.

## Wiki/Wikidata/source inspection

Context is explicitly stratified:

```text
canonical semantic object
<-> Wikidata identity
<-> revision-locked Wikipedia/context manifestation
-> cited/followable references
-> explicitly acquired source
-> provenance receipt
```

Firewalls:

```text
QID != applicability
Wikipedia != legal authority
context link != evidence payment
outbound reference != promoted fact
```

Perplexity/chat archives are another source-manifestation lane, not a semantic authority. Existing completeness/provenance diagnostics remain attached when such material is shown or followed.

## Renderer validation

The renderer is not an authority.

Given intended semantic payload `I_D` and rendered text `R`, reparsing produces `P(R)`. The relevant consumer must be able to factor its required observation through the reparsed rendering, and excess assertions must be checked against licensed payload/source coordinates.

High-stakes legal explanation additionally requires exact source/provenance checks for material propositions. PNF parity alone is not sufficient.

## Anti-panopticon boundary

The reader expands only what is required for the current focus/question/disclosure budget. It does not automatically join unrelated person/context data, publish browsing history, infer belief/comprehension, or widen disclosure merely because more world state exists.

`available world >> displayed world` is intentional.

## StatiBaker relation

`TimelineRibbonLite`, semantic trail, and proof cone are sibling consumers:

```text
TemporalRibbon != SemanticTrail != ProofCone
```

StatiBaker may retain explicitly permitted interaction/temporal receipts, but those receipts do not create semantic authority or comprehension claims.

## First implementation slice

1. Pure `semanticTrail.js` model for target identity, adaptive cone projection, outcome resolution, context firewalls, and portable intents.
2. Regression tests before production implementation.
3. Preserve existing Mabo `ReadingSurface` behaviour.
4. Add one reading-comprehension fixture using overlapping targets.
5. Wire generic semantic intents into existing guide/context affordances without replacing selectionBridge/JCUI.
6. Mirror target/outcome/disclosure/firewall semantics in a shallow DASHI owner.

## Acceptance

- Mabo still opens as a bounded human explanation rather than a graph.
- A role/entity click can reroot locally without loading the whole world.
- A high-elucidatory farther node can survive a bounded base-depth projection.
- Unpaid exact-source/context requirements defer to acquisition rather than inventing content.
- Overlapping composite/constituent targets remain independent.
- Wiki/Wikidata/source context stays visibly distinct from legal authority.
- No UI interaction mutates canonical proof/authority/payment state.
