# JMD Push/Pull Surfaces and Blockers (2026-03-29)

## Goal

Separate three different inputs that were getting conflated in the push/pull
 discussion:

- semantic boundary clarification from the refreshed JMD thread
- local implementation scaffolding from `../rust-nix-template`
- still-missing external JMD infra contract needed to move beyond the current
  `kant-zk-pastebin` / `erdfa-publish-rs` reference model

## What the refreshed JMD thread did clarify

The refreshed thread
`69c4a9b1-d014-83a0-8bb0-873e4eaa4098`
(`c6e383233d0d7c4efde671be1432c825054cb222`) clarified semantic boundaries:

- `ZOS` should supplement `SL`, not replace it
- `ZOS` should consume structured `SL` facts, not raw token-frequency or
  bag-of-words inputs
- `ZOS` proposals must re-enter `SL` through the candidate/promotion boundary
- `Zelph` remains downstream reasoning over already-formed inputs

That thread is therefore relevant to governance and role separation.

It also now adds a stronger execution-proof thesis:

- JMD explicitly frames the service proof around:
  Nix flake, git history, perf profile, and resource use
- JMD explicitly says:
  `zkperf + erdfa` is "the API"

That means the thread is now relevant to both:

- governance / role separation
- trust / receipt framing for service execution

It is still not, by itself, a stable declaration of JMD host/runtime push/pull
surfaces.

## What can now be inferred, but not yet promoted to declared contract

The refreshed thread is now strong enough to support one small provisional
contract inference, provided it is marked as inference rather than declared
spec.

Provisional inferred contract:

- artifact
  - the result payload or logical shard/output being exchanged
- `erdfa` payload
  - the structured semantic/proof encoding attached to that artifact
- `zkperf` receipt
  - the execution receipt proving environment, code lineage, runtime behavior,
    and resource use

Short form:

`artifact + erdfa payload + zkperf receipt`

This is useful because it gives `ITIR` a cleaner temporary mental model for
what a JMD-aligned push/pull object may eventually look like.

But it remains inference only until there is a sharper declaration of:

- transport/endpoints
- cache/replay behavior
- acknowledgement/receipt schema
- capability/auth rules

## What `../rust-nix-template` did clarify

`../rust-nix-template` clarified that there is a plausible local home for a
Rust-facing transform/publisher seam:

- Nix + Rust workspace shell
- publish endpoint placeholders in config
- packaging direction aligned with DA51 / CBOR
- dependency path toward `erdfa-publish`

So it helps answer:

- where a first publisher/puller crate could live
- how a sink-neutral packaging seam could be prototyped locally

It does not answer:

- what the authoritative JMD-side push/pull contract is
- which remote endpoints are actually stable
- what replay/cache guarantees the live host makes
- whether JMD wants the same artifact/receipt layout as the local scaffold

## What is still missing

The blocker for moving beyond the current reference surfaces remains external
infra certainty.

The repo still lacks a stable enough JMD-side contract for:

- declared `/browse` behavior
- declared `/raw/{id}` behavior
- any stronger `/ipfs/{cid}` or equivalent retrieval guarantee
- latest-index or latest-post replay semantics
- publication acknowledgement / receipt semantics
- cache/replay expectations when live host surfaces drift or disappear

So the missing information is operational contract shape, not conceptual
permission to implement push/pull.

More specifically, the repo now has a better provisional answer to:

- what kind of object JMD may want exchanged

But it still lacks the stable operational answer to:

- where that object is pushed/pulled
- how it is requested
- how replay and caching work
- how acknowledgement is represented on the wire

## Current ITIR posture

Until the external contract is clearer, `ITIR` should treat:

- `kant-zk-pastebin`
  - as the strongest current retrieval / manifest reference surface
- `erdfa-publish-rs`
  - as the strongest current shard-production / publish reference surface
- `itir_jmd_bridge`
  - as pull-first and plugin-shaped rather than hard-coded to a speculative JMD
    host contract
- `../rust-nix-template`
  - as local scaffolding for a publisher/puller seam, not evidence that JMD
    infra is already pinned

## Practical consequence

This leaves the next push/pull work in a constrained position:

- semantic/governance boundaries are clearer than they were
- proof/receipt framing is clearer than it was
- consumer/publisher role split is clearer than it was
- local Rust/Nix implementation posture is clearer than it was
- external JMD infra is still the unresolved blocker for going beyond the
  current `kant` / `erdfa` reference pair

## Resume criteria

Treat real JMD push/pull expansion as unblocked only if at least one of these
becomes true:

1. JMD host surfaces are declared stable enough to treat as an external
   contract
2. `ITIR` adopts local cache/replay surfaces as the practical contract for
   pull-side work
3. an explicit JMD infra note pins endpoint, receipt, and replay semantics well
   enough to target implementation without guessing
