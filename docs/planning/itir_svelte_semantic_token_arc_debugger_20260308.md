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
- social / kinship / friendship: teal
- state / affect: violet
- fallback / unknown: slate

Confidence opacity:
- `high`: strongest
- `medium`: medium
- `low`: faint but visible
- `abstain`: not rendered in the first UI pass

### 3. Anchor sourcing
Anchor payloads should be emitted by the report producer, not re-derived in the
Svelte server loader.

Producer-side anchor derivation should use existing event-local report artifacts
in this order:
1. resolved mentions already attached to the event
2. receipt surfaces such as `verb`, `cue_surface`, or similar lexical evidence
3. bounded label-text fallback for subject/object/predicate when explicit
   mention anchoring is absent

This remains display/debug anchoring only. It must not write spans back into
canonical semantic storage.

Anchor provenance should be visible in the UI:
- `mention`
- `receipt`
- `label_fallback`

This provenance is important because users need to know whether an arc is
grounded in event-local mention evidence or only in a weaker producer fallback.
The side panel should also expose a compact provenance-strength summary per
relation so reviewers can quickly distinguish mention-backed anchors from
receipt-anchored or fallback-heavy ones.
The event/source viewers should reflect that distinction too, so mention-backed
highlights read as firmer than receipt-anchored highlights, and fallback spans
stay visibly weaker/debuggier.

### 4. Pin / freeze behavior
Hover remains the fast discovery mode, but the workbench should also support a
pin/freeze interaction.

Chosen first-pass interaction:
- hover a token to preview arcs
- click a token to pin the current relation set
- click a relation or anchor chip in the side panel to pin that specific
  relation without depending on token hover
- while pinned, moving the mouse should not clear the visible arcs
- provide an explicit clear action

Pinned state is still view-local. It does not persist outside the page.

### 4a. Same-type echo highlights
When a token/anchor is active, the workbench should lightly echo other anchors
of the same type within the selected event text.

Chosen v1 interpretation of "same type":
- same anchor role (`subject`, `predicate`, or `object`)
- same relation family as the active relation

Chosen rendering:
- use the active relation family color
- keep echoes light and secondary to the selected token/arc set
- scale echo opacity by the source relation strength for each echoed anchor
- do not override the primary active token styling

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
  - `charStart`
  - `charEnd`
  - `tokenStart`
  - `tokenEnd`
  - `sourceArtifactId`

The inspector should be domain-agnostic:
- no legal-only type names in the component contract
- no requirement that a producer be a semantic-report route
- relation family/color mapping may be producer-specific, but the view contract
  stays stable

Chosen ownership boundary:
- Python/report producers own tokenization, anchor derivation, relation-family
  mapping, and confidence-to-opacity shaping for this contract
- `itir-svelte` consumes the contract and renders it
- Svelte server code may still provide a fallback `unavailableReason`, but it
  should not be the semantic authority for anchor selection

Current span contract:
- `charStart` / `charEnd` are the producer-owned display/debug span boundary
- `tokenStart` / `tokenEnd` remain derived render helpers for the current arc UI
- `sourceArtifactId` records the originating evidence surface:
  - mention-backed anchors: mention cluster id
  - receipt-backed anchors: candidate/receipt locator
  - fallback anchors: bounded fallback id
- these spans remain non-canonical review artifacts, not persisted semantic
  provenance

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
- same-type echo highlights for anchors sharing the active role/family
- compact legend explaining color and opacity semantics
- side panel listing the hovered/pinned relation(s), anchor labels, and anchor
  provenance
- compact review summary panel showing predicate counts, top cue surfaces, and
  `text_debug` coverage/exclusion counts from the producer-owned report summary
- event-local text viewer using the selected event text plus producer-owned
  `charStart` / `charEnd` anchor spans for cross-highlighting
- source-document viewer slot that stays explicit about missing source text
  instead of faking a full document from event text

## Viewer Coupling
The semantic report workbench should own one shared selection bridge across:
- token-arc inspector
- event-local text viewer
- source-document viewer slot

Chosen v1 behavior:
- the event-local viewer always renders the selected `text_debug` event text
- the selected active anchor is highlighted strongly in that viewer
- other anchors in the active relation are highlighted at medium strength
- same-role/same-family echoes are highlighted lightly using the existing
  family-color + opacity-strength rules
- the source-document viewer is shown but may be unavailable

Chosen source-document fallback:
- transcript/freeform should emit grouped source-document text and source-level
  char spans so the source-document slot can render real source text
- GWB/AU should emit grouped timeline-source documents built from the
  normalized timeline payload's full event text, rather than staying blocked on
  unavailable source documents
- if no real source document text is available, show an explicit unavailable
  panel

## Review Feedback Seam
The semantic report workbench now also acts as a bounded review-submission
surface.

Current v1 behavior:
- reviewers can submit append-only correction records from the active semantic
  selection
- corrections are keyed by source/run/event/relation/anchor refs
- evidence refs come from the current viewer selection state
- submissions persist locally as JSONL review artifacts rather than rewriting
  semantic tables in place
- recent correction records are visible in the workbench for the active
  corpus/run

Boundary:
- this is a review lane, not an in-place semantic editor
- correction submissions are proposals/receipts, not canonical truth changes

## Mission Observer Surface
When a semantic producer emits a bounded mission/follow-up observer artifact,
the workbench may surface it beside the semantic review UI.

Current v1:
- transcript/freeform emits `mission_observer`
- the workbench shows compact mission/follow-up counts plus a downloadable JSON
  export
- the intended downstream consumer is SB's read-only/additive overlay seam

Boundary:
- this observer payload remains reference-heavy
- it does not justify dumping threads, events, or raw semantic reports into SB
- do not reuse event text as a fake source document

## Follow-ups
1. Extend the current producer-owned `text_debug` contract with char spans and
   source artifact ids so graph/document cross-highlighting can be built on a
   real shared span surface instead of token-only render helpers.
2. Extend pin mode so individual relations, not just token-triggered arc sets,
   can be frozen directly from the side panel.
3. Keep the inspector contract generic and prove it across at least one legal
   and one non-legal producer before treating the abstraction as settled.
