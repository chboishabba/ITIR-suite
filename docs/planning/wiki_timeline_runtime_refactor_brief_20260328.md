# `wikiTimelineAoo` Runtime Refactor Brief

## Current surface

[`itir-svelte/src/lib/server/wikiTimelineAoo.ts`](/home/c/Documents/code/ITIR-suite/itir-svelte/src/lib/server/wikiTimelineAoo.ts)
currently mixes:

- payload normalization
- python subprocess bridging
- repo/db path resolution
- HCA overlay policy
- AAO-shaped payload adaptation

The main seams are visible around:

- subprocess/runtime helpers from `itir-svelte/src/lib/server/wikiTimelineAoo.ts:223`
- payload normalization from `itir-svelte/src/lib/server/wikiTimelineAoo.ts:285`
- HCA overlay logic at `itir-svelte/src/lib/server/wikiTimelineAoo.ts:571`
- exported loader at `itir-svelte/src/lib/server/wikiTimelineAoo.ts:624`

## Reusable core to preserve or extract

- generic wiki timeline payload normalization
- loader/runtime plumbing for python-backed JSON extraction
- overlay hook contract for post-load augmentation
- event/action/negation normalization helpers

These are timeline-runtime concerns, not inherently AAO-only concerns.

## Specialized remainder that should stay explicit

- AAO-specific payload typing and adapter assumptions
- HCA-specific overlay policy
- legacy AAO db/env compatibility shims

Those should remain explicit adapters or overlays so the shared runtime does
not pretend every corpus looks like AAO.

## Proposed modules after split

- `itir-svelte/src/lib/server/wiki_timeline/runtime.ts`
  repo/db path resolution, subprocess execution, loader skeleton
- `itir-svelte/src/lib/server/wiki_timeline/normalize.ts`
  payload object normalization and typed helper functions
- `itir-svelte/src/lib/server/wiki_timeline/overlay.ts`
  generic overlay hook interface
- `itir-svelte/src/lib/server/wiki_timeline/hca_overlay.ts`
  HCA-specific overlay implementation
- `itir-svelte/src/lib/server/wiki_timeline/aoo_adapter.ts`
  AAO-specific payload shaping and exported compatibility adapter

## Acceptance checks

- current AAO route outputs are unchanged for the same corpus inputs
- HCA overlay still applies only where explicitly requested
- subprocess/runtime helpers can load a timeline without any AAO naming in the
  shared core
- AAO-specific types and assumptions live in adapter modules, not the runtime
  base
