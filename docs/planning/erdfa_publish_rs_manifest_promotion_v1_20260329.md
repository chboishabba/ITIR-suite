# `erdfa-publish-rs` Manifest Promotion `v1` (2026-03-29)

## Goal

Define the smallest richer manifest shape that would move
`erdfa-publish-rs` closer to the ITIR shared shard contract without forcing
Zelph runtime behavior into the publish crate.

## Why this is the next step

Current repo state already has:

- a bounded `zkperf`-on-`SL` contract and fixture
- a tiny HF container/index fixture
- a clear gap note showing what `erdfa-publish-rs` lacks relative to the ITIR
  shared contract

So the next smallest useful design step is to pin the minimal manifest
promotion shape rather than jumping straight into code.

## Core decision

Promote `erdfa-publish-rs` by adding a thin richer manifest layer, not by
replacing its current shard primitives.

The promoted shape should preserve:

- existing `Shard`
- existing content-addressed `cid`
- existing DA51/CBOR packaging discipline

While adding only the smallest missing metadata needed for cross-layer use.

## Minimal promoted fields

### Artifact-level additions on top of `ShardSet`

Add:

- `contractVersion`
- `artifactId`
- `artifactRevision`
- `artifactClass`
- `createdAtUtc`
- `buildProvenance`

These fields solve:

- immutable build/revision identity
- cross-sink rebuild identity
- builder/provenance clarity

### Per-shard additions on top of `ShardRef`

Add:

- `logicalKind`
- `encoding`
- `sizeBytes`
- optional `objectRefs[]`
- optional `routingKeys[]`

These fields solve:

- cross-consumer shard typing
- size-aware planning
- sink attachment as first-class data
- later Zelph-facing selector integration

## Explicit non-goals for v1

Do **not** require in this first promotion step:

- full routing index representation
- HF container membership metadata
- spectral ranking metadata
- any consumer-specific fetch policy

Those belong in adjacent layers, not the publish manifest core.

## Suggested shape

At the conceptual level:

- keep `Shard` payload object unchanged
- keep `cid` as the content identity
- promote only the manifest/catalog shape

So the promoted `ShardSet` conceptually becomes:

- artifact metadata
- enriched shard catalog
- optional sink refs

Not:

- a full consumer runtime contract

## Minimal example of promoted shard ref

Conceptually, each promoted shard ref should be able to say:

- this shard is `left-bucket-001`
- it is an `adjacency-bucket`
- it is encoded as `cbor`
- it is `2048` bytes
- it has digest `sha256:...`
- it may currently be attached to:
  - `ipfs://...`
  - `hf://...`

That is enough to support:

- publication
- sink projection
- later container/index layering
- later selector/routing layering

Without putting Zelph policy into the publisher.

## Promotion criteria

Treat this manifest promotion step as adequate if it can show:

- existing `erdfa-publish-rs` shard identity remains intact
- artifact revision/provenance becomes explicit
- per-shard type/encoding/size becomes explicit
- sink attachments move from helper-only to manifest-visible data
- routing remains optional metadata, not mandatory runtime behavior

## Immediate follow-up

Use:

- `docs/planning/jmd_fixtures/erdfa_manifest_promotion_v1.example.json`

as the first tiny concrete fixture for this promoted shape.

After that fixture, the next code-facing step can be:

- a concrete Rust struct sketch or JSON fixture for the promoted manifest shape

That would be the first implementation-ready artifact for the second ranked
step.
