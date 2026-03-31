# Wiki Timeline AAO Selected Event Panel

Date: 2026-04-01

## Change Class

Standard change.

## Problem

After the selected-context extraction, the next safe presentation-only block in
`itir-svelte/src/routes/graphs/wiki-timeline-aoo/+page.svelte` is the selected
event header and layout/time controls. The route still carried that rendering
inline even though the block already consumed route-shaped props.

## Requirement

- extract the selected event header and layout/time controls into a route-local
  component
- keep route state and navigation semantics in the route
- do not move graph derivation or timeline semantics into the component

## Promoted Slice

New route-local component:

- `itir-svelte/src/routes/graphs/wiki-timeline-aoo/_components/SelectedEventPanel.svelte`

Adopter:

- `itir-svelte/src/routes/graphs/wiki-timeline-aoo/+page.svelte`

## Acceptance

- the route becomes shorter again
- the new component stays route-local
- layout/time state still lives in the route and is only passed through
- regression and Svelte checks stay green

## Quality Gate

Run from `itir-svelte/`:

- `node --test tests/graph_ui_regressions.test.js tests/wiki_timeline_refactor_regressions.test.js`
- `npm run check`

## C4 / PlantUML

```plantuml
@startuml
title Wiki Timeline AAO Selected Event Panel

Component(route, "wiki-timeline-aoo/+page.svelte", "Route shell")
Component(panel, "SelectedEventPanel.svelte", "Route-local presentation component")
Component(runtime, "Python wiki timeline runtime", "Canonical semantics owner")

Rel(route, panel, "passes selected event and UI state")
Rel(route, runtime, "consumes canonical payload")

@enduml
```
