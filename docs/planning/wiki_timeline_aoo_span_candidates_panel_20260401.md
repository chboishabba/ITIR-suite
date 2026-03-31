# Wiki Timeline AAO Span Candidates Panel

Date: 2026-04-01

## Change Class

Standard change.

## Problem

After the selected event and context panel splits, the next safe
presentation-only block in
`itir-svelte/src/routes/graphs/wiki-timeline-aoo/+page.svelte` is the span
candidates panel. The route still rendered parser badge, toggle UI, and span
chips inline even though all ordering and selection state was already
precomputed.

## Requirement

- extract the span candidates panel into a route-local component
- keep `showAllSpans`, `spanShown`, and parser-derived display state in the route
- do not move span ranking or hygiene semantics into the component

## Promoted Slice

New route-local component:

- `itir-svelte/src/routes/graphs/wiki-timeline-aoo/_components/SpanCandidatesPanel.svelte`

Adopter:

- `itir-svelte/src/routes/graphs/wiki-timeline-aoo/+page.svelte`

## Acceptance

- the route becomes shorter again
- the component remains route-local
- span sorting and slice selection remain in the route
- regression and Svelte checks stay green

## Quality Gate

Run from `itir-svelte/`:

- `node --test tests/graph_ui_regressions.test.js tests/wiki_timeline_refactor_regressions.test.js`
- `npm run check`

## C4 / PlantUML

```plantuml
@startuml
title Wiki Timeline AAO Span Candidates Panel

Component(route, "wiki-timeline-aoo/+page.svelte", "Route shell")
Component(panel, "SpanCandidatesPanel.svelte", "Route-local presentation component")
Component(runtime, "Python wiki timeline runtime", "Canonical semantics owner")

Rel(route, panel, "passes precomputed span display props")
Rel(route, runtime, "consumes canonical payload")

@enduml
```
