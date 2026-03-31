# Wiki Timeline AAO-All Corpus Docs Panel

Date: 2026-03-31

## Change Class

Standard change.

## Problem

The `wiki-timeline-aoo-all` route still owned a large corpus-docs display block
and its small route-local helper logic inline in:

- `itir-svelte/src/routes/graphs/wiki-timeline-aoo-all/+page.svelte`

That made the route shell heavier than necessary even after Python-owned
timeline semantics were moved out.

## Requirement

Extract the corpus-docs display block into a route-local component while
keeping the route as a composition shell and preserving presentation-only
behavior.

## Component Boundary

Shared within the route family:

- `itir-svelte/src/routes/graphs/wiki-timeline-aoo-all/_components/CorpusDocsPanel.svelte`

Adopter:

- `itir-svelte/src/routes/graphs/wiki-timeline-aoo-all/+page.svelte`

Promoted slice:

- corpus-docs card rendering
- referenced/unreferenced badge shaping
- route-local follow-hint path matching
- human-readable file-size rendering

## Acceptance

- the route imports the route-local corpus-docs component
- the route no longer owns the corpus-docs panel block inline
- Svelte check and existing wiki timeline regression guards stay green

## Quality Gate

Run from `itir-svelte/`:

- `npm run check`
- `node --test tests/graph_ui_regressions.test.js tests/wiki_timeline_refactor_regressions.test.js`

## C4 / PlantUML

```plantuml
@startuml
title Wiki Timeline AAO-All Corpus Docs Panel

Component(route, "+page.svelte", "AAO-all composition shell")
Component(panel, "CorpusDocsPanel.svelte", "Route-local corpus docs presenter")

Rel(route, panel, "renders corpus-docs panel")

@enduml
```
