# Wiki Timeline AAO Object Resolver Hints Panel

Date: 2026-04-01

## Change Class

Standard change.

## Problem

After the selected-event, selected-context, and span-candidates extractions,
the next safe presentation-only block in
`itir-svelte/src/routes/graphs/wiki-timeline-aoo/+page.svelte` is the object
resolver hints panel. The route still renders the hint cards inline even though
all hint-row shaping already happens in route state.

## Requirement

- extract the object resolver hints panel into a route-local component
- keep `objectHintRows` derivation in the route
- do not move resolver policy or scoring semantics into the component

## Promoted Slice

New route-local component:

- `itir-svelte/src/routes/graphs/wiki-timeline-aoo/_components/ObjectResolverHintsPanel.svelte`

Adopter:

- `itir-svelte/src/routes/graphs/wiki-timeline-aoo/+page.svelte`

## Acceptance

- the route becomes shorter again
- the component remains route-local
- hint-row derivation and ordering remain in the route
- regression and Svelte checks stay green

## Quality Gate

Run from `itir-svelte/`:

- `node --test tests/graph_ui_regressions.test.js tests/wiki_timeline_refactor_regressions.test.js`
- `npm run check`

## C4 / PlantUML

```plantuml
@startuml
title Wiki Timeline AAO Object Resolver Hints Panel

Component(route, "wiki-timeline-aoo/+page.svelte", "Route shell")
Component(panel, "ObjectResolverHintsPanel.svelte", "Route-local presentation component")
Component(runtime, "Python wiki timeline runtime", "Canonical semantics owner")

Rel(route, panel, "passes precomputed object hint rows")
Rel(route, runtime, "consumes canonical payload")

@enduml
```
