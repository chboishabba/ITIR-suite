# ZOS vs fuzzymodo / Casey / StatiBaker (2026-03-28)

## Goal

Pin the practical role comparison between `ZOS` and the existing
`fuzzymodo` / `casey-git-clone` / `StatiBaker` surfaces so the repo does not
accidentally assign the same job to multiple systems.

## Current finding

`ZOS` is not best compared to all three equally.

It is closest to `fuzzymodo`, and much less similar to `casey-git-clone` or
`StatiBaker`.

## Existing repo-backed roles

- `casey-git-clone`
  - mutable possibility state
  - explicit workspace / collapse / build authority
- `fuzzymodo`
  - advisory selector/query/ranking reasoning over exported state
- `StatiBaker`
  - observer-only memory, receipts, and alignment/timeline compilation
- `SL`
  - truth construction and promotion authority

## Practical comparison

### ZOS vs `casey-git-clone`

Not the same role.

- `casey-git-clone` owns operational candidate/workspace state
- `ZOS` should not own mutable operational possibility state

If `ZOS` starts holding live candidate realities, explicit collapse state, or
build authority, it is drifting into Casey territory.

### ZOS vs `StatiBaker`

Not the same role.

- `StatiBaker` stores observer memory, receipts, and references
- `ZOS` should not become the canonical history/governance ledger

If `ZOS` starts storing long-lived observer truth, execution receipts, or daily
timeline authority, it is drifting into StatiBaker territory.

### ZOS vs `fuzzymodo`

This is the real overlap.

Both look like supplemental reasoning/organization layers over already-exposed
state rather than primary truth or execution authorities.

Current practical difference:

- `fuzzymodo`
  - path-local selector/ranking/advisory layer
  - explicit exported-state consumer
- `ZOS`
  - broader semantic clustering / overlay / hypothesis layer over SL-backed
    facts

So the risk is not "ZOS replaces Casey" or "ZOS replaces StatiBaker".

The risk is:

- `ZOS` re-describes a broader, fuzzier version of work that may already fit
  inside `fuzzymodo`
- or `ZOS` sprawls upward into SL truth or downward into SB memory

## Recommended reading

For current planning, treat `ZOS` as:

- nearest to `fuzzymodo`
- downstream of `SL`
- separate from Casey operational state
- separate from StatiBaker observer memory

Short form:

- `SL` constructs truth
- `ZOS` supplements with semantic hypotheses/overlays
- `fuzzymodo` ranks/advises over explicit exported state
- `casey-git-clone` manages live possibility state
- `StatiBaker` records observer memory and receipts

## Recommended next move

If `ZOS` becomes concrete, force one of two outcomes early:

1. narrow `ZOS` until it is clearly just a semantic sub-lane within
   `fuzzymodo`, or
2. keep `ZOS` separate but explicitly forbid it from:
   - owning truth
   - owning mutable workspace/candidate state
   - owning observer/timeline memory

## Disambiguation test

Use this quick test for future proposals:

- if the proposal changes canonical truth or promotion:
  it belongs to `SL`
- if the proposal changes live candidate/workspace/build state:
  it belongs to `casey-git-clone`
- if the proposal records append-only receipts or observer memory:
  it belongs to `StatiBaker`
- if the proposal ranks or filters explicit exported state:
  it likely belongs to `fuzzymodo`
- if the proposal clusters, overlays, or hypothesizes over structured SL facts:
  it may belong to `ZOS`, but only as a supplemental layer
