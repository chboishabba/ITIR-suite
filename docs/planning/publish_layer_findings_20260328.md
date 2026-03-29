# Publish Layer Findings (2026-03-28)

## Goal

Freeze the current read on the "publish layer" question before more Rust-facing
work or template exploration turns into an accidental contract.

## Current finding

The repo is not uncertain about whether publication exists. It is uncertain
about where to freeze the publication boundary and which crate should own it.

Current evidence supports this split:

- `kant-zk-pastebin`
  - strongest current retrieval / shard-manifest / IPFS-adjacent reference
    surface
- `erdfa-publish-rs`
  - strongest current ERDFA shard production / serialization surface
- ZOS
  - best current role fit for publish/pull orchestration
- Zelph
  - read/query consumer, not the publish/pull contract owner

So the unresolved hinge is:

- the shared artifact contract
- sink abstraction
- publish/pull role ownership

It is not:

- basic transport reachability
- whether HF or IPFS can be used at all
- whether Rust is allowed in the stack

## Practical boundary

For current planning, the publish layer should mean:

- input:
  normalized artifact or logical shard-set description
- responsibilities:
  package payloads, attach digests, emit sink refs, produce publication
  receipts
- non-responsibilities:
  JMD bridge semantics, truth promotion, Casey governance, or Zelph query
  routing

This keeps the layer aligned with the shared-shard contract's
"logical artifact first, sinks attached later" model.

## How to treat `rust-nix-template`

`../rust-nix-template` is useful as a host for the programmable transform /
publisher seam, but it must not be treated as proof that the contract is
settled.

What the template usefully contributes right now:

- a Rust + Nix workspace shell
- config-driven publish endpoint placeholders
- DA51 / CBOR packaging direction
- an explicit dependency path toward `erdfa-publish`

What it does not justify:

- freezing the publish-layer trait boundary yet
- promoting one sink layout as canonical
- claiming a finished ZOS/JMD publish contract

Important current caveat:

- the template `src/main.rs` is scaffold-quality and currently malformed /
  duplicated, so it is not a clean baseline implementation

## Recommended next move

Before implementation, keep the repo aligned to this sequence:

1. freeze the publish-layer findings and role split
2. keep Rust-facing work at the programmable transform layer boundary
3. only then choose whether to:
   - extract a minimal publish crate, or
   - write the trait/interface contract first

## Immediate acceptance criteria

Any first publish-layer prototype should satisfy all of:

- accepts a logical artifact or shard-set input
- emits sink-neutral identity plus sink-specific refs
- records a receipt surface
- keeps query routing out of the publisher
- does not silently redefine the JMD/SL bridge contract
