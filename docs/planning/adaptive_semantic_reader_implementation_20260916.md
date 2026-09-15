# Adaptive Semantic Reader implementation plan — 2026-09-16

## Goal

Extend the existing `agent/mabo-reading-workbench-v1` implementation rather than creating a new app. Keep `itir-svelte` as the sole frontend, `ReadingSurface` as the current Mabo consumer, and add a reusable semantic-trail projection beneath it.

## Task 1 — RED: semantic-trail contracts

Create `itir-svelte/tests/semantic_trail_regressions.test.js` before production code. Require:

- overlapping constituent/composite targets retain independent identities;
- adaptive cone includes all nodes within base depth and only high-elucidatory nodes beyond it;
- local adequate projection executes immediately;
- missing materialisation/source coordinate defers with the exact residual rather than becoming global failure;
- malformed/unresolvable target rejects explicitly;
- portable semantic intents compile for `ExplainRole`, `ExploreEntity`, `FollowReference`, and `Back`;
- Wiki/Wikidata context candidates carry explicit non-authority/non-payment firewalls;
- default disclosure hides expert identifiers/graph/provenance internals.

Expected RED cause: `semanticTrail.js` does not yet exist.

## Task 2 — GREEN: minimal pure semantic-trail model

Create `itir-svelte/src/lib/workbench/semanticTrail.js` with only the API demanded by Task 1:

- `createSemanticTarget`
- `buildElucidatoryCone`
- `resolveExplainOutcome`
- `compileSemanticIntent`
- `createContextCandidate`
- `defaultSemanticDisclosure`

No network, persistence, source acquisition, renderer LLM, or canonical-state mutation belongs here.

## Task 3 — reading-comprehension fixture

Test first, then add a tiny fixture around:

```text
They wove a panel from golden spider silk.
```

Expose `They`, `wove`, `panel`, `golden spider silk`, and `silk` as separate semantic targets. Assert composite/constituent distinction and human-first PNF cue labels.

The fixture is a presentation/regression specimen only; it does not claim real-world identity or provenance.

## Task 4 — preserve and adapt the Mabo reader

Add regression tests proving existing Mabo five-stage behaviour remains unchanged while guide/context affordances can compile portable semantic intents.

Prefer adapting the existing `ReadingSurface.svelte` and `readingSurface.js` through the generic model rather than duplicating UI state.

## Task 5 — source/context inspection projection

Add a pure projection contract that separates:

```text
semantic object
Wikidata/QID identity candidate
Wikipedia/context manifestation
followable reference
acquired source/provenance
legal authority/application
```

Do not fetch anything in the UI module. Missing exact source text should yield `Defer(materialisation/source residual)` for the outer SLR recurrence.

Existing Perplexity resolver/archive machinery is source-lane/reference material only. Its partial/completeness provenance must survive projection; it is not a production semantic ABI.

## Task 6 — shallow DASHI parity owner

Add a focused owner such as:

`DASHI/Interop/SemanticReaderElucidatoryConeExact.agda`

Mirror only the stable interface:

- semantic target kinds;
- Execute/Defer/Reject outcomes;
- base-depth OR high-elucidatory inclusion rule;
- disclosure is projection, not world deletion;
- composite target != constituent target;
- UI intent != semantic mutation;
- Wiki context != legal authority;
- QID != applicability;
- role overlay != comprehension;
- local unavailable != globally unavailable;
- acquired/source display != evidence payment/claim truth.

Keep the owner shallow and independently type-checkable; do not import broken broad aggregates merely to export it.

## Task 7 — verification

ITIR focused commands:

```bash
cd itir-svelte
node --test tests/semantic_trail_regressions.test.js
node --test tests/reading_surface_regressions.test.js
npm run check
```

DASHI:

```bash
agda -i . DASHI/Interop/SemanticReaderElucidatoryConeExact.agda
```

Only after focused green receipts should we wire a live SensibLaw Mabo proof projection or the SLR acquisition recurrence into the UI.

## Deferred

- renderer model selection / local LLM integration;
- automatic prose repair loop;
- live Perplexity query UI;
- whole-world graph loading;
- StatiBaker whole-life/temporal UI integration;
- learning progress/skill inference;
- user-comprehension scoring.

Those are downstream consumers of the semantic-trail contract, not prerequisites for this tranche.
