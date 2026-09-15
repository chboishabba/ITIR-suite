# ITIR/Svelte roadmap: progressive proof explanation workbench

Date: 2026-09-15

## Purpose

Define the UI contract for legal/public-interest proof explanation without making the interface graph-first or leaking internal information density into every view.

The working frontend remains `itir-svelte` (SvelteKit + Tailwind). Legacy SensibLaw Streamlit surfaces remain useful as feature-regression references only.

The product seam is not a separate Mabo app. It is a reusable proof-explanation mode over a canonical SensibLaw proof specimen.

## Core UX law

```text
argument-first
-> graph-second
-> provenance-on-demand
```

The same canonical object must drive both lay explanation and expert inspection.

```text
Explain <-> Inspect
```

No separate simplified truth model is permitted.

## Projection stack

### Explain

Default public/lay view.

Show:

```text
human question
one bounded proposition chain
plain-language consequence
what still needs checking / what is not being claimed
small provenance affordances
```

Do not show by default:

```text
QIDs
hashes
paragraph IDs
all residual classes
all source-role tags
full proof graph
all alternative paths
```

### Why / contingent arguments

Expand the selected proposition only.

```text
claim
-> authority
-> applicability
-> support
-> qualifier / defeater / comparator
-> residual
```

This view answers `why does this step follow here?` rather than rendering every graph edge.

### Source inspector

Open the exact supporting source in context.

Required coordinates:

```text
source identity
document/court/instrument identity
source role
paragraph/section/span
revision/version
surrounding context
full-source action
```

Exact-source expansion should be cheaper than accepting a generated summary.

### Research/context drawer

Wiki/Wikidata/public ontology surfaces are context/navigation aids.

Show progressively:

```text
resolved entity/concept
related cases/people/statutes/concepts
cited references
outbound links/follow candidates
acquired-source trail
unresolved follow failures
```

Discovery surfaces never inherit authority into followed sources.

### Proof graph

Optional expert/power view.

Expose:

```text
typed nodes/edges
support/defeater/comparator roles
alternative readings
conflicts
source genealogy
residual/payment history
review/promotion state
```

## Legal-term interaction

A legal term such as `estoppel` should be progressive rather than overloaded.

First interaction may be a compact hover/card:

```text
term
short lexical definition
optional pronunciation
Wikipedia lead/image when useful
```

Then explicit actions:

```text
See Australian legal construction
Show contingent arguments
Open sources
Explore context
```

The richer legal view may compose:

```text
selected corpus
+ applicable legislation
+ binding/persuasive authorities
+ factual predicates
+ exceptions/defeaters
+ temporal/jurisdiction coordinates
```

but should not appear merely because the user hovered the word.

Firewalls:

```text
Wiktionary != legal authority
Wikipedia != legal authority
QID identity != applicability
context link != evidence payment
```

## Public-interest / CLC interaction

The same interaction model should support a concerned citizen or activist preparing an argument for a CLC, representative, journalist, regulator, or self-represented filing.

Default surface should help transform:

```text
concern / prose / AI-written submission
```

into an inspectable object with:

```text
literal formulation
possible intended issue
source anchors
predicate events
potential authority/rules
supporting material
contrary/limiting material
unresolved questions
```

The UI must preserve the literal text and inferred interpretation separately.

A professional reviewer can therefore distinguish:

```text
what the person actually wrote
what the system inferred they might mean
what authority applies if that interpretation is correct
what further fact/source would decide the difference
```

## Mabo flagship mode

The first flagship explanation should answer:

```text
Why was Mabo such a big deal?
```

using one concrete proposition chain rather than a giant graph.

Visible skeleton:

```text
Before
-> proposition challenged
-> what the Court did
-> why this changed the legal argument space
-> important qualification/limitation
-> what remains unresolved/not claimed
```

Primary actions:

```text
See the judgment
Explore context
Show contingent arguments
Show proof graph
```

Each action refines the current view without mutating proof state.

## Query-indexed information density

The UI should be treated as query-indexed projection.

```text
Q_layExplanation may factor through Explain
Q_primaryAuthorityAudit does not factor through Explain
Q_contextNavigation may factor through Context
Q_fullChallenge requires richer proof/source state
```

Therefore:

```text
hidden from current view
!= discarded
!= unavailable
!= unsupported
```

Every explanation-bearing assertion must remain reopenable to its canonical proof/source coordinates.

## Frontend direction

Stay with the current `itir-svelte` line rather than extending Streamlit.

Prefer:

- shallow component hierarchy;
- semantic HTML where appropriate;
- native browser primitives before large client-side widget frameworks;
- derived views over typed data instead of DOM-encoded state;
- graph visualisation isolated behind an explicit power view;
- WebAssembly/WebGPU only where they materially improve local graph/layout/search/compute, not as architecture theatre;
- progressive loading of source/context panes rather than pre-rendering all evidence.

Avoid:

- deeply nested component state as semantic storage;
- graph-first landing pages;
- duplicating canonical proof state into UI-only models;
- making every ontology/source edge visible simultaneously;
- automatic authority transfer from discovery/context panes.

## Feature-regression mining from legacy UIs

Legacy Streamlit remains useful to identify feature expectations such as:

```text
document preview
knowledge graph navigation
obligations/residuals
case comparison
audit/history
collections/workflow state
```

Reimplement only the features demanded by the new projection model; do not preserve old screen structure for compatibility.

## High-alpha order

1. canonical proof specimen read model;
2. Explain projection;
3. exact-source inspector;
4. legal-term/context card with Wiki/Wikidata distinction;
5. contingent-argument expansion;
6. Inspect/proof graph power view;
7. local WASM/WebGPU acceleration only after profiling shows an actual need.

## Acceptance criterion

A lay user can understand the selected argument without seeing the graph.

A professional can reopen every displayed claim into exact source/proof coordinates.

Changing view depth never changes semantic state, authority, or payment.