# itir-svelte Semantic Token Arc Debugger (2026-03-08)

## Purpose
Add a view-layer semantic debugging surface in `itir-svelte` that feels closer
to token embedding / attention / relation visualizers:
- text rendered as hoverable tokens
- arcs drawn between token anchors for semantic relations
- color driven by relation family/type
- opacity driven by confidence tier

This is explicitly a visualization and debugging aid. It does not change the
underlying semantic extraction or promotion logic.

## Chosen Placement
Add the first version to the existing semantic report route:
- `/graphs/semantic-report`

Reason:
- the route already has semantic-report payloads
- it already serves a review/debug posture
- it avoids inventing a disconnected UI surface for the same data

## Intended Behavior

### 1. Hoverable token text
For a selected semantic event, render the event text as discrete hoverable
tokens.

On token hover:
- detect whether the token participates in one or more semantic anchors
- draw arcs from that token's anchor to the other anchors in the same relation
- keep arcs transient and debug-oriented; this is not a canonical graph editor

### 2. Arc semantics
Arcs should be:
- colored by semantic relation family/type
- opacity-weighted by confidence tier
- visually stronger for promoted rows than for candidate-only rows

Initial bounded mapping:
- review / adjudication: blue
- authority / precedent invocation: green
- executive / governance action: amber
- conversational: rose
- state / affect: violet
- fallback / unknown: slate

Confidence opacity:
- `high`: strongest
- `medium`: medium
- `low`: faint but visible
- `abstain`: not rendered in the first UI pass

### 3. Anchor sourcing
Anchors should be derived from existing event-local report artifacts in this
order:
1. resolved mentions already attached to the event
2. receipt surfaces such as `verb`, `cue_surface`, or similar lexical evidence
3. bounded label-text fallback for subject/object/predicate when explicit
   mention anchoring is absent

This remains display-layer anchoring only. It must not write spans back into
canonical semantic storage.

Anchor provenance should be visible in the UI:
- `mention`
- `receipt`
- `label_fallback`

This provenance is important because users need to know whether an arc is
grounded in event-local mention evidence or only in a weaker display fallback.

### 4. Pin / freeze behavior
Hover remains the fast discovery mode, but the workbench should also support a
pin/freeze interaction.

Chosen first-pass interaction:
- hover a token to preview arcs
- click a token to pin the current relation set
- while pinned, moving the mouse should not clear the visible arcs
- provide an explicit clear action

Pinned state is still view-local. It does not persist outside the page.

### 5. Fallback posture
Some corpora/events may not expose enough event text or anchorable surfaces.

The view should:
- show the arc inspector only for events with usable text
- display a clear fallback/debug note when the selected corpus lacks text-rich
  event payloads
- avoid inventing synthetic token spans when no defensible anchor exists

## Boundaries
- No new semantic promotion logic.
- No change to canonical relation storage.
- No claim that token anchors are authoritative provenance spans.
- No hidden re-tokenization contract for SensibLaw.

This is a debug/view layer over already-produced event text + receipts.

## Generality Constraint
The anchor/provenance model should stay reusable for non-legal text-rich
semantic/debug lanes.

That means:
- avoid hardcoding legal-only anchor source names or UI copy
- let relation family coloring vary by predicate family, not by one legal
  ontology only
- keep the component usable for transcript/freeform/event-debug surfaces later
  if they provide the same event-text + relation-anchor payload shape

## Shared Text-Debug Contract
The token-arc workbench should stop depending on a semantic-report-specific
payload type and instead consume a small shared text-debug contract.

Chosen generic shape:
- `events[]`
- per event:
  - `eventId`
  - `text`
  - `tokens[]`
  - `relations[]`
  - counts/summary fields useful for workbench controls
- per relation:
  - `relationId`
  - `displayLabel`
  - `family`
  - `confidenceTier`
  - `promotionStatus`
  - `anchors[]`
- per anchor:
  - `role`
  - `label`
  - `source`
  - `tokenStart`
  - `tokenEnd`

The inspector should be domain-agnostic:
- no legal-only type names in the component contract
- no requirement that a producer be a semantic-report route
- relation family/color mapping may be producer-specific, but the view contract
  stays stable

## Producer Strategy
This workbench should be proven against at least two producers.

Chosen first two producers:
1. legal semantic report payloads (`gwb`, `hca`)
2. transcript/freeform semantic report payloads over `TextUnit` input

The second producer matters because it proves the workbench is not merely
legal-flavored naming wrapped around one route. Transcript/freeform text is the
first real pressure-test for a reusable event-text + relation-anchor debug
surface.

## First-pass UI Shape
- event picker/list from semantic-report per-event rows
- token ribbon / wrapped token field for the selected event
- hover arcs rendered in an SVG overlay
- click-to-pin / clear-pin controls
- compact legend explaining color and opacity semantics
- side panel listing the hovered/pinned relation(s), anchor labels, and anchor
  provenance

## Follow-ups
1. Move from heuristic token anchoring toward a shared span contract once
   semantic/viewer span boundaries are settled more formally.
2. Extend pin mode so individual relations, not just token-triggered arc sets,
   can be frozen directly from the side panel.
3. Keep the inspector contract generic and add at least one non-legal producer
   before treating the abstraction as settled; transcript/freeform is the
   chosen first proof lane.
