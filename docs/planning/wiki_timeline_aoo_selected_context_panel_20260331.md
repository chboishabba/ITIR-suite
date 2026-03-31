# Wiki Timeline AAO Selected Context Panel

Date: 2026-03-31

## Change Class

Standard change.

## Problem

After the runtime normalization work, the next safe TS-side slice in the AAO
route family is presentation-only shell slimming. The context panel inside
`itir-svelte/src/routes/graphs/wiki-timeline-aoo/+page.svelte` is large but
already consumes route-shaped props rather than defining timeline semantics.

## Requirement

- extract the selected-event context panel into a route-local component
- keep all event/context derivation in the route
- do not move graph, numeric, or source semantics into the component

## Promoted Slice

New route-local component:

- `itir-svelte/src/routes/graphs/wiki-timeline-aoo/_components/SelectedContextPanel.svelte`

Adopter:

- `itir-svelte/src/routes/graphs/wiki-timeline-aoo/+page.svelte`

Inputs stay presentation-only:

- selected event
- selected node id
- selected context summary
- selected context details
- expand/collapse flag
- display-only callbacks/helpers

## Acceptance

- the route becomes materially shorter
- the new component is route-local only
- context derivation remains in the route
- regression and Svelte checks stay green

## Quality Gate

Run from `itir-svelte/`:

- `node --test tests/graph_ui_regressions.test.js tests/wiki_timeline_refactor_regressions.test.js`
- `npm run check`

## C4 / PlantUML

```plantuml
@startuml
title Wiki Timeline AAO Selected Context Panel

Component(route, "wiki-timeline-aoo/+page.svelte", "Route shell")
Component(panel, "SelectedContextPanel.svelte", "Route-local presentation component")
Component(runtime, "Python wiki timeline runtime", "Canonical semantics owner")

Rel(route, panel, "passes precomputed display props")
Rel(route, runtime, "consumes canonical payloads")

@enduml
```
