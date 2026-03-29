# `wiki-timeline-aoo-all` Route Refactor Brief

## Current surface

[`itir-svelte/src/routes/graphs/wiki-timeline-aoo-all/+page.svelte`](/home/c/Documents/code/ITIR-suite/itir-svelte/src/routes/graphs/wiki-timeline-aoo-all/+page.svelte)
is a large route component that currently owns:

- route-local filters and viewport state
- graph node/edge assembly helpers
- evidence/source/lens toggles
- context-table and corpus-doc linkage logic
- AAO-all presentation policy

This makes the route behave like a mini-application runtime instead of a thin
composition shell.

## Reusable core to preserve or extract

- timeline graph builder functions
- graph selection/viewport state helpers
- evidence/source/lens visibility logic
- reusable timeline context panels

These are route-support concerns and should be reusable across related timeline
surfaces.

## Specialized remainder that should stay explicit

- AAO-all route defaults and copy
- route-specific dataset limits
- any presentation choices tied specifically to the AAO-all view

Those belong in the route shell or an explicit AAO-all adapter layer.

## Proposed modules after split

- `itir-svelte/src/lib/wiki_timeline/graph.ts`
  node/edge assembly and lane construction
- `itir-svelte/src/lib/wiki_timeline/selection.ts`
  selected-node / context synchronization helpers
- `itir-svelte/src/lib/wiki_timeline/filters.ts`
  graph-control defaults and visibility toggles
- `itir-svelte/src/lib/wiki_timeline/components/WikiTimelineGraphControls.svelte`
- `itir-svelte/src/lib/wiki_timeline/components/WikiTimelineContextPanel.svelte`
- `itir-svelte/src/lib/wiki_timeline/components/WikiTimelineEvidencePanel.svelte`
- route file remains as the AAO-all composition shell

## Acceptance checks

- rendered graph structure is unchanged for the same payload and filter set
- selection and scroll behavior remain stable after component extraction
- generic graph/control logic becomes reusable without carrying `aoo-all`
  naming
- route file becomes mostly composition plus AAO-all defaults
