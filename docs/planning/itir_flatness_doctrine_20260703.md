# ITIR Flatness Doctrine

Date: 2026-07-03

## Core Definition

Flatness is not "low node count" or "simple graph shape".

Flatness is failure to preserve inspectable typed linkage depth between
source-local evidence and higher-order semantic, legal, ontology, or governance
anchors.

Depth means a reviewer can walk typed, inspectable, multi-hop paths from local
anchors to review/authority anchors without losing the intermediate layers that
justify the move.

Non-flat means enough intermediate structure survives that a reviewer can see
how a local token, span, sentence, provision, claim, or candidate becomes a
reviewable global assertion.

## Two Failure Classes

### Projection Flatness

The data graph itself is shallow.

Expected typed intermediate layers are absent, merged, deduplicated away, or
never emitted.

Examples:

- `token -> sentence`
- `mention -> item`
- `sentence -> obligation`

when the expected ladder required additional typed steps.

### Render Flatness

The data graph contains depth, but the UI collapses or hides it.

Examples:

- the graph contains `token -> sentence -> PNF -> review packet -> tranche`
  but the web UI only presents `token -> sentence`
- typed layers exist but are hidden by default, unnavigable, over-coalesced, or
  visually too dense to inspect

## Shared Invariant

No local evidence anchor may promote directly to a global claim.

Every promotion must preserve an inspectable typed path through the relevant
intermediate layers, including source, parse, domain, authority, residual, and
review/tranche boundaries.

No renderer may hide the path by which promotion was claimed.

## Domain-Agnostic Ladder

Generic shape:

```text
local evidence
-> source-local structure
-> parsed/normalised structure
-> domain ontology node
-> external ontology / authority node
-> review packet
-> tranche/global governance anchor
```

The exact ontology varies by domain. The invariant does not.

Lanes inherit the linkage-depth control-plane, not Wikidata geometry. The
shared audit/receipt contract may be reused across WD, GWB/Brexit, AU, and
affidavit families, while each lane keeps its own typed ladder at the lane
boundary.

## Expected Ladders

### SensibLaw / PNF

```text
token
-> sentence:document
-> sentence:PNF
-> document:PNF
-> claim / norm / obligation / exception / constraint candidate
-> review packet
-> authority surface
-> tranche/global
```

Flat failure examples:

- `token -> sentence`
- `sentence -> claim`

because those erase the PNF/document/authority middle.

### Predicate-Role Depth

Flatness is often role erasure, not just missing hops.

For a sentence such as:

```text
[...] walked the [...] to the [...]
```

the important carrier is not a named frame class like `WalkFrame`. The real
system stays generic for memory and comparability reasons.

The role-preserving ladder is:

```text
word/mention
-> token
-> lexical WD candidate (soft)
-> span within sentence/document
-> sentence:PNF
-> role/filler in generic PNF carrier
-> document:PNF
-> entity/topic candidate
-> WD semantic/authority candidate
-> corpus query result
-> review packet / tranche
```

That means:

- a lexical mention is not yet a fact
- a sentence is not yet a claim
- a Wikidata item match is not yet a promotion
- PNF is the typed middle layer that preserves how the mention functions

`token -> WD` may exist early as a soft lexical stitch, but it stays candidate
only until the PNF/document/review path explains the role of the mention.

### Wikidata

```text
mention/text anchor
-> token/span
-> candidate entity/property
-> Wikidata item/property
-> statement
-> qualifier/reference context
-> class/property lattice
-> constraint / project-rule pressure
-> review packet
-> tranche/global
```

Flat failure:

```text
mention -> item
```

because it skips candidate state, statement context, qualifiers, references,
class lattice, constraint pressure, and review status.

### Legislation

```text
token/span
-> sentence
-> subsection
-> section
-> part/division
-> instrument/Act/regulation
-> jurisdiction
-> legal concept / obligation / permission / prohibition
-> doctrine / case-law pressure
-> review packet
-> tranche/global
```

Flat failure:

```text
sentence -> obligation
```

without section, instrument, jurisdiction, version, exception context, and
authority boundary.

### Case Law

```text
quote/span
-> paragraph
-> issue
-> holding / ratio / obiter candidate
-> doctrine node
-> jurisdiction/court hierarchy
-> subsequent treatment
-> report packet
-> authority tranche
```

Flat failure:

```text
quote -> legal rule
```

without ratio/obiter/treatment status.

### Medical / Scientific Ontology

```text
text span
-> sentence
-> claim
-> study / evidence object
-> population/intervention/comparator/outcome
-> measure/effect size
-> ontology term
-> guideline / external authority
-> review packet
-> tranche/global
```

Flat failure:

```text
paper says X -> medical fact X
```

without study type, population, endpoint, ontology mapping, guideline status,
and residual uncertainty.

### Cross-Ontology Bridge

```text
source span
-> local ontology node
-> candidate Wikidata item/property
-> mapped external ontology concept
-> equivalence/subclass/relatedness relation
-> domain-specific pressure
-> residual
-> review decision
-> tranche/global
```

Flat failure:

```text
local concept = Wikidata item
```

when the honest relation may only be `closeMatch`, `broadMatch`,
`candidateEquivalent`, or a jurisdiction-specific analogue.

## Diagnostics

The current shallow graph-shape audit should be treated as only one component.

The fuller doctrine needs diagnostics such as:

- `layer_coverage`
- `typed_path_depth`
- `bridge_completeness`
- `anchor_to_tranche_reachability`
- `path_multiplicity`
- `collapse_points`
- `authority_boundary_visibility`
- `residual_visibility`
- `candidate_vs_promoted_visibility`
- `render_inspectability`

Useful status fields:

- `linkage_depth_status`:
  `absent | shallow | partial | complete | overcollapsed | overexpanded`
- `render_depth_status`:
  `not_applicable | faithful | visually_collapsed | hidden_by_default | unnavigable | too_dense`
- `collapse_origin`:
  `projection | normalisation | deduplication | id_collision | summarisation | renderer | unknown`

## Next Highest-Alpha Step

The next highest-alpha step is not renderer work.

It is the first machine-facing bridge contract where:

- PNF remains the spine
- Zelph/WD is the first external bridge
- the audit proves the bridge does not erase the spine

Canonical next-tranche note:

- `docs/planning/pnf_zelph_wd_linkage_depth_contract_20260703.md`

## Known Example

The current `hotspot_eval` latent-slice defect is a projection-side collapse,
not a webui collapse:

```text
duplicate latent-slice node ids
-> node collapse before rendering
-> collapse_origin: id_collision
```

## Renderer Obligations

When linkage depth exists in the data:

- the UI must preserve inspectability of the ladder
- typed boundaries must remain navigable
- candidate vs promoted state must stay visible
- authority/review boundaries must not be visually erased
- default summarisation must not imply promotion

If the renderer hides the path, the review surface is still flat even when the
data graph is not.
