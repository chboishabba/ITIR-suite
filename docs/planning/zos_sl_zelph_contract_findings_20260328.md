# ZOS / SL / Zelph Contract Findings (2026-03-28)

## Goal

Freeze the current thread-backed reading of the `ZOS -> SL -> Zelph` stack so
the repo does not blur conceptual state, promoted truth, and downstream graph
reasoning.

## Thread provenance

- title:
  `JMD FORMAL EXPLAIN - Meme System Explanation`
- online UUID:
  `69c4a9b1-d014-83a0-8bb0-873e4eaa4098`
- canonical thread ID:
  `c6e383233d0d7c4efde671be1432c825054cb222`
- source used:
  `db` after direct UUID pull into the canonical archive

## Current finding

The fetched thread sharpens the stack into three different roles:

- ZOS
  - dynamic candidate-state / evolving ontology layer
- SL
  - deterministic extraction and promotion layer
- Zelph
  - downstream fact-graph / query / reasoning layer

The key thread-backed reading is:

- ZOS handles candidate or dynamically estimated structure
- SL turns extracted material into promoted facts under governed criteria
- Zelph consumes that fact graph as a downstream reasoning surface

So the intended next-step order is:

1. define the `ZOS <-> SL` contract formally
2. build a minimal ZOS engine in Python
3. map ZOS outputs into a Zelph input layer

## Updated clarification from the refreshed thread

The later turns make the disambiguation stricter than the earlier read.

The refreshed thread explicitly supports:

- ZOS should **not** replace or supplant SL's canonical truth construction
- ZOS should supplement SL by operating over structured SL facts
- ZOS must not work from naive token frequency or raw text co-occurrence
- if ZOS proposes candidate facts or semantic structures, they must re-enter SL
  through an explicit candidate/promotion boundary

The clean practical reading is:

- SL remains the truth / promotion authority
- ZOS remains the semantic overlay / clustering / hypothesis layer
- Zelph remains downstream reasoning over already-formed fact/overlay inputs

## Stronger disambiguation rule

To avoid the repo drifting into "ZOS replaces SL" language, keep this rule
explicit:

- if ZOS modifies or overrides SL truth state, that is competition and a
  design error
- if ZOS references SL promoted facts, organizes them, and submits proposals
  back through SL, that is supplementation/layering

Short form:

- SL constructs truth
- ZOS organizes and proposes
- Zelph reasons

## Input discipline

The refreshed thread also sharpens the substrate rule:

- bad ZOS:
  raw token frequency, bag-of-words co-occurrence, or word-pair counting
- acceptable ZOS:
  structured predicates, argument roles, qualifiers, and fact-level patterns

So any first ZOS engine prototype should consume structures shaped like:

- predicate
- arguments
- qualifiers
- refs back to SL promoted facts and source anchors

## What this rules out

This thread does not justify:

- collapsing ZOS and SL into one runtime surface
- treating Zelph as the place where truth promotion happens
- treating the publish layer as the first or only unresolved abstraction
- treating ZOS as a replacement system for SL

Instead it supports a stricter split:

- conceptual/dynamic state first
- promoted truth second
- graph reasoning third
- publication/transport after those boundaries are clear

## Practical contract read

For current repo planning, the cleanest contract shape is:

- `ZOS -> SL`
  - candidate structures, provisional state, or dynamic ontology material
- `SL -> Zelph`
  - promoted facts and bounded derived graph atoms only
- `SL -> ZOS`
  - structured promoted facts and their qualifiers/anchors, not raw strings
- publish layer
  - packages already-formed logical artifacts; it does not define truth or
    reasoning semantics

## Immediate planning consequence

The publish-layer note remains valid, but it is downstream of this stack
ordering.

So the near-term sequence should be:

1. keep `ZOS -> SL -> Zelph` role separation explicit
2. define the `ZOS <-> SL` contract before widening Rust-facing publisher work
3. keep the first ZOS engine prototype minimal and Python-first
4. treat any Zelph mapping as an input-layer bridge, not as promotion logic
5. add an explicit disambiguation / conflict rule so "ZOS supplements SL"
   stays enforceable in docs and code planning
