# Judgment Architecture Lane Split

Date: 2026-04-02

## Purpose

Record the current execution split after the substrate-first phase.

The repo is no longer mainly blocked on shared storage/runtime cleanup. The
next high-value work is reusable judgment architecture that can help both the
Wikidata moonshot and the broader legal / evidence-heavy lanes.

See also:

- `docs/planning/moonshot_compiler_normalization_reconsideration_20260402.md`

This note is deliberately plain:

- current safe operating rule is still bounded, review-first, fail-closed
- the long-term moonshot is stronger automated judgment
- these are not contradictory

## Current Read

The current operating rule remains:

- raw text is evidence input, not direct action authority
- graph surfaces must not overstate causality or certainty
- reviewer packets and workbenches are still operator aids

But the long-term direction is larger:

- the Nat lane still points toward blind migration automation
- the broader stack is clearly aiming at stronger judgment systems,
  including law-like decision support and decision-making surfaces
- those future decision layers must sit on grounded, typed, auditable
  interpretation rather than loose text inference

## Main Decision

The next reusable architecture push should be:

1. grounded text-to-observation comparison
2. typed doctrinal / semantic primitives
3. explicit uncertainty, conflict, and abstain handling
4. competing-interpretation / claim-boundary inspection
5. governance gates that keep stronger judgment fail-closed

This is the shared pattern:

- source-grounded text and records
- anchored observations
- typed domain primitives
- explicit uncertainty / conflict / abstain
- comparison against structured state
- stronger decision layers above that

That pattern is reusable across:

- Wikidata migration
- legal/doctrinal extraction
- later policy, climate, and similar evidence-heavy lanes

## Priority Read

Near-term priority order:

1. free-text to promoted-observation bridge work
2. legal / doctrinal primitive extraction and judgment scaffolding
3. domain-agnostic primitive/comparison architecture
4. Nat packet grounding depth on hard cases
5. disciplined claim-boundary / competing-interpretation graph work
6. stronger promotion and governance gates

Why this order:

- the text bridge is the nearest direct help to the Nat hard cases
- legal primitives are the strongest training ground for structured judgment
- domain-agnostic primitive architecture prevents one-off domain hacks
- grounding, graph discipline, and governance then harden and control the
  resulting system

## Worker Split

One bounded lane per worker:

- `Ramanujan`
  - first executable text bridge over representative temporal / multi-value
    climate rows
- `Erdos`
  - legal doctrinal primitive scaffold over bounded AU procedural-meaning
    cases
- `Euler`
  - domain-agnostic typed primitive and comparison pattern across the legal
    and Wikidata lanes
- `Lorentz`
  - Nat evidence-grounding depth on representative hard reviewer packets
- `Ohm`
  - disciplined competing-interpretation / claim-boundary graph surface
- `Huygens`
  - promotion, abstain, and audit gates for stronger judgment layers

## Returned Brief Read

The first worker briefs confirm the split and sharpen the first slice for each
lane.

- `Ramanujan`
  - strongest first promotion
  - the bridge is already partly real in
    `SensibLaw/src/ontology/wikidata.py`
  - first safe slice is one pinned climate pilot family only, additive bridge
    fields only, and explicit abstain outside the bounded temporal /
    multi-value pattern

- `Erdos`
  - legal lane should start as a doctrinal projection/review layer, not a base
    semantic rewrite
  - first primitive should be a bounded `Browne_v_Dunn` style
    cross-examination proposition over AU procedural-meaning cases
  - primary authority remains the promotion gate

- `Euler`
  - shared core should stay very small
  - one `TypedPrimitive` plus one `PrimitiveComparison`
  - no lane-specific action logic in the shared layer

- `Lorentz`
  - main gap is that grounding depth is still narrower than packet coverage
  - first safe slice is broader representative hard-packet grounding using the
    existing packet and evidence-report surfaces rather than widening packet
    shape

- `Ohm`
  - graph lane should stay explicit, read-only, and overlay-only
  - off by default
  - never allowed to drift into quasi-truth rendering

- `Huygens`
  - reusable governance surface should formalize:
    `promote | abstain | audit`
  - do not bake Nat-specific thresholds into the general abstraction

## Promotion Order

Under the higher-order compiler/product normalization read, this note no
longer controls the top-level lane order by itself.

The controlling near-term order is now:

1. `Ramanujan`
2. `Erdos`
3. `Lorentz`
4. `Euler`
5. `Ohm`
6. `Huygens`

Why this order:

- `Ramanujan` defines the shared evidence-bundle -> promoted-outcome contract
- `Erdos` turns that contract into a first real AU product family
- `Lorentz` then does the same for GWB so AU and GWB both normalize before
  we spend another round on shared semantic abstraction
- `Euler` follows after those concrete product adopters so the shared
  primitive/comparison layer is learned from real pressure instead of
  invented too early
- `Ohm` and `Huygens` remain real but are hardening layers after the product
  contract is clearer

## Immediate Execution Checkpoint

The next implementation promotion should now be:

- `Ramanujan`

The rest stay assigned and queued behind that promotion:

- `Erdos`
- `Lorentz`
- `Euler`
- `Ohm`
- `Huygens`

Do not reshuffle this order unless the first implementation slice reveals:

- hidden coupling
- a blocked contract seam
- or a stronger bounded promotion than the current text-bridge slice

## Reaffirmed Orchestration State

This checkpoint was rechecked after the returned worker briefs and aligned to
the compiler/product normalization note:

- one bounded lane per worker
- `Ramanujan` still first
- `Lorentz` now explicitly stays ahead of `Euler` in the controlling order
- no lane reassignment yet
- no promotion-order change yet

The next valid orchestrator action is implementation promotion, not another
selection round, unless new evidence changes the ordering logic above.

## Governance

Keep the following explicit:

- primary legal sources stay the truth anchor in legal lanes
- text does not bypass promotion
- graph work must not silently turn sequence into causality
- stronger judgment layers must remain replayable, auditable, and fail-closed

Do not drift into:

- open-ended generic semantics
- ad hoc domain-specific hacks with no reusable primitive layer
- prettier graph output without stronger challengeability

## Reconsideration

This split remains useful, but it is now subordinate to a clearer
compiler/product normalization read:

- bounded evidence group in
- promoted truth or abstention out
- derived review/product/graph surfaces after that

That broader read is now the higher-order orchestrator frame for AU, GWB, and
Wikidata/Nat, so this note should be read as the judgment-support layer rather
than the whole moonshot normalization story.

Current controlling companion:

- `docs/planning/moonshot_compiler_normalization_reconsideration_20260402.md`

That companion now controls the ordering whenever there is a conflict between
judgment-support sequencing and cross-lane product normalization.

## Completion Condition

This split is complete enough to hand over to the user-story/product phase when:

- at least one real text bridge lane is executable on representative hard rows
- at least one doctrinal primitive lane is executable on bounded legal cases
- the common primitive/comparison pattern is explicit enough to reuse
- governance gates are strong enough that promotion remains controlled
