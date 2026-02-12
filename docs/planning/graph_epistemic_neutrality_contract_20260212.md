# Graph Epistemic Neutrality Contract (2026-02-12)

## Purpose
Ensure graph rendering does not visually overstate certainty or collapse assertion/evidence structure into a single endorsed narrative.

## Scope
Applies to wiki/HCA timeline graph views, including:
- `wiki-timeline`
- `wiki-timeline-aoo`
- `wiki-timeline-aoo-all`
- timeline ribbon variants

## Rendering principles
1. **Deterministic layout first**
   - stable coordinates by lane/order; avoid force-layout drift for core role edges
2. **Truth vs view separation**
   - resolved entity lane is distinct from modifier/span lane
3. **Edge typing is explicit**
   - role, sequence, evidence/context edges are visually distinct
4. **No implied endorsement**
   - avoid central visual treatment that suggests one final "true storyline"

## Node classes
1. `entity` (resolved identity)
   - solid border/fill
2. `modifier` or `span_candidate`
   - dashed border, lighter styling
3. `action` (lemma-first)
   - pill style; optional surface in tooltip
4. `evidence`
   - separate lane or overlay region

## Edge classes
1. `ROLE_SUBJECT`, `ROLE_OBJECT`
   - solid
2. `NEXT_STEP`
   - thin solid or arrow
3. `ATTRIBUTED_TO`, `SUPPORTS`, `CITES_SAME_RECORD`
   - dotted/dashed overlay; lower opacity; not layout-driving

## Interaction contract
1. Default view
   - show role + sequence edges
2. Toggle: modifiers/spans
3. Toggle: evidence/context overlays
4. Context panel
   - must expose source sentence and references for selected node/edge

## Anti-chaos sizing rule
If node sizing is enabled:
- use bounded, monotonic transforms only (e.g., `tanh`/log scaling)
- cap min/max width
- no layout-force effects from size changes

## Required badges
Header should include:
- extraction profile id/hash
- projection scope (entity/time/filter)
- source artifact path

## Non-goals
- no causal inference from sequence edges
- no hidden confidence rewriting in truth layer
- no suppression of source-grounded structure without user-visible toggle
