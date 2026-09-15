# Mabo Reading Workbench v0 — design addendum

Date: 2026-09-15

## Status

This document refines `docs/planning/progressive_proof_explanation_workbench_20260915.md` into the first concrete vertical slice. It does not replace that roadmap.

The v0 flagship is deliberately bounded to one Mabo proposition chain. It is not a generic legal dashboard, not a full proof-graph explorer, and not a browser-automation project.

## Goal

Give a lay reader a compact answer to “why was Mabo such a big deal?” and let them progressively reopen the exact proposition, source, context, bounded proof cone and provenance without changing semantic state.

The same interaction contract must also be executable as JCUI semantic actions, so tests describe user intent rather than selectors or gestures.

## Ownership

- SensibLaw owns legal proposition identity, authority/application semantics, support/defeater/comparator role, residuals and proof state.
- SLR/PNF owns linguistic candidate structure and token/role annotations supplied to the read model.
- ITIR/Svelte owns the display/read interaction surface only.
- JCUI owns typed interaction intent and observations; DOM selectors and physical gestures are adapters.
- StatiBaker may optionally record an explicitly opted-in navigation trail, but interaction receipts do not imply belief, understanding or legal truth.

## UX invariant

```text
available information != information initially visible
```

The default route shows only one bounded explanatory chain. Richer information appears only after user action.

```text
proof graph available != proof graph initially visible
```

## Route

Create a dedicated workbench route:

```text
/reading/mabo
```

The route is a reusable Reading Workbench instance backed by a Mabo specimen read model; do not encode legal semantics directly in the Svelte page.

## Initial visible state

The first screen contains:

1. title/question: “Why was Mabo such a big deal?”;
2. one plain-language explanation block;
3. five bounded explanatory nodes:
   - Before;
   - Challenged premise;
   - What the Court changed;
   - Immediate native-title consequence;
   - Important limitation / later application;
4. quiet actions: `Why?`, `Source`, `Meaning`, `Follow`, `Show reasoning`;
5. no full graph, QID, digest, paragraph IDs, residual table or raw PNF by default.

The page must make the qualification visible in ordinary language: a doctrinal change does not mean every traditional claim automatically succeeds.

## Canonical read model

Create a producer-shaped UI contract under `itir-svelte/src/lib/reading/`.

```ts
export type ReadingNodeKind =
  | 'explanation'
  | 'proposition'
  | 'authority'
  | 'consequence'
  | 'qualification'
  | 'concept'
  | 'source';

export type ReadingSemanticRef = {
  id: string;
  kind: ReadingNodeKind;
  label: string;
};

export type ReadingSourceRef = {
  id: string;
  title: string;
  sourceRole: 'primary_authority' | 'legislation' | 'secondary_context' | 'identity_context';
  citation?: string;
  revision?: string;
  charStart?: number;
  charEnd?: number;
  sourceArtifactId?: string;
  href?: string;
};

export type ReadingPnfToken = {
  text: string;
  role: 'actor' | 'predicate' | 'patient' | 'modifier' | 'negation' | 'modality' | 'condition' | 'other';
  semanticRef?: string;
};

export type ReadingEdge = {
  id: string;
  from: string;
  to: string;
  kind: 'sequence' | 'support' | 'defeater' | 'comparator' | 'context' | 'source';
  label?: string;
};

export type ReadingWorkbenchModel = {
  schema: 'itir.reading_workbench.v0_1';
  question: string;
  summary: string;
  initialNodeIds: string[];
  nodes: ReadingSemanticRef[];
  edges: ReadingEdge[];
  sources: ReadingSourceRef[];
  pnfByNode: Record<string, ReadingPnfToken[]>;
  wikiContext: Record<string, { qid?: string; wikipediaTitle?: string; href?: string }>;
  semanticPromotion: false;
};
```

The model is a display/read projection. It must not become the authoritative Mabo proof store.

## Selection bridge

Reuse `createSelectionBridge` from `itir-svelte/src/lib/workbench/selectionBridge.ts`.

The active semantic ref is shared across:

- explanation cards;
- PNF/token affordances;
- Semantic Inspector;
- Source Drawer;
- bounded proof cone.

No component keeps a second independent notion of “selected proposition.”

## Reading Surface

Create a shallow component that renders the summary and initial five nodes.

Each node exposes semantic buttons rather than encoded selectors:

```text
Meaning
Why?
Source
Follow
```

PNF highlighting is opt-in. When enabled, highlight roles such as actor/predicate/patient and high-value legal operators such as negation, modality and conditions. PNF annotations are explanatory aids, not legal conclusions.

## Semantic Inspector

The inspector is selection-driven and closed/compact by default.

For a selected proposition or concept, show only:

- plain label;
- type/kind;
- one short explanation;
- source count;
- context identity if available;
- explicit actions to reveal PNF, source, proof cone or context.

## Source Drawer

Reuse `DocumentViewer.svelte` and its char-span highlight contract.

The compact header shows:

```text
Source
Role
Citation / version
Used here for
```

Then actions:

```text
Open exact passage
Open full source
Provenance
```

The exact passage uses `DocumentHighlight` with source-owned character offsets. If source text is unavailable, say so explicitly; never synthesize a fake passage from the explanation text.

## Wiki/Wikidata context

Wiki/Wikidata are context/navigation only.

```text
QID -> cross-source identity candidate != proposition truth
Wikipedia -> context/discovery != legal authority
```

Show these only after `Meaning` / `Explore context`.

The first card may show a resolved title and QID. Deeper provenance/revision information stays behind an explicit expansion.

## Bounded proof cone

Reuse `LayeredGraph.svelte` only after `Show reasoning`.

For v0 the graph is bounded to the current locus and one declared neighborhood. It may render:

```text
challenged premise
-> authority/applicability
-> Mabo proposition
-> support / defeater / comparator
-> immediate consequence / residual
```

The graph is selection-synchronized with the reading surface through the existing selection bridge.

Graph node `scale` remains a truth-neutral display emphasis only.

## Reading Trail

Maintain an in-memory navigation stack for v0:

```ts
export type ReadingTrailEntry = {
  semanticId: string;
  action: 'activate' | 'follow' | 'open_source' | 'expand_reasoning' | 'back';
};
```

Default persistence is ephemeral. No inferred comprehension/belief score is permitted.

Later StatiBaker integration may persist the trail only through explicit opt-in modes (`local trail`, `durable/bookmarked`, `learning history`).

## JCUI contract

The Mabo workbench must expose stable semantic target ids, not CSS selectors.

Minimum fixture flow:

```text
Activate semantic:mabo:proposition:terra-nullius
Expand semantic:mabo:proposition:terra-nullius
Expect Expanded semantic:mabo:proposition:terra-nullius
OpenSource source:mabo:1992:hca:23
Expect Visible source:mabo:1992:hca:23
Zoom semantic:mabo:proof-cone Fit
```

A later Svelte JCUI adapter resolves these semantic ids to application state/actions. Physical input and DOM selectors remain implementation detail.

## Accessibility

All semantic actions must be keyboard reachable.

- buttons use native `<button>` semantics;
- focus state is visible;
- graph nodes remain Enter/Space activatable;
- opening a source drawer moves focus intentionally and closing returns it;
- PNF role information is conveyed in text/ARIA as well as color;
- progressive disclosure does not depend on hover.

## v0 non-goals

Do not implement:

- generic dashboarding;
- full unbounded authority graph;
- browser/Puppeteer selector flows;
- persistent personalization;
- hidden learner model;
- automatic Wiki/Wikidata authority transfer;
- graph-layout GPU work before profiling;
- authoring/editing proof state from the reading page.

## Acceptance criteria

1. Initial load shows a comprehensible Mabo explanation without a graph.
2. A reader can enable PNF affordances for the selected sentence/node without changing proof state.
3. `Source` opens the exact source passage where source bytes/span are available.
4. `Explore context` exposes Wiki/Wikidata identity separately from legal authority.
5. `Show reasoning` reveals only a bounded proof cone.
6. The same semantic selection synchronizes reading, inspector, source and graph.
7. Back/Follow produce an explicit Reading Trail, ephemeral by default.
8. A JCUI fixture can describe the main flow without CSS selectors or physical gestures.
9. Every displayed legal assertion remains reopenable to source/proof coordinates.
10. Changing view depth never changes semantic promotion/payment state.
