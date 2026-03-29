# `erdfa-publish-rs` vs Shared Shard Contract `v1` (2026-03-29)

## Goal

Compare the actual local `/home/c/Documents/code/erdfa-publish-rs` data model
to `docs/planning/shared_shard_artifact_contract_v1_20260327.md` so the repo
can distinguish:

- what `erdfa-publish-rs` already gives us
- what ITIR still needs before it can serve Zelph-style consumers cleanly

## What `erdfa-publish-rs` already provides

From `/home/c/Documents/code/erdfa-publish-rs/src/lib.rs`:

- `Shard`
  - `id`
  - `cid`
  - `component`
  - `tags`
- `ShardSet`
  - `name`
  - `shards: Vec<ShardRef>`
- `ShardRef`
  - `id`
  - `cid`
  - `tags`
- DA51-tagged CBOR serialization for both shard and manifest
- tar emission of `*.cbor` plus `manifest.cbor`
- helper projection methods:
  - `ipfs_url()`
  - `paste_url(base)`

This means `erdfa-publish-rs` is already strong on:

- content-addressed shard identity
- CBOR shard encoding
- simple manifest emission
- IPFS/pastebin-facing publication helpers

## Where it already aligns with the shared contract

The local crate already supports several important pieces of the shared ITIR
contract:

- stable logical shard identity
  - `Shard.id`
- immutable content identity
  - `Shard.cid`
- manifest-level shard catalog
  - `ShardSet.shards`
- serialization-neutral direction in principle
  - CBOR exists now; JSON could be added later without changing the concept of
    shard identity
- sink attachment direction in embryo
  - helper methods already point at IPFS and paste/raw publication surfaces

So it is a legitimate publish-side reference.

## What is missing relative to ITIR's shared contract

The shared contract wants a richer logical artifact model than the current
`erdfa-publish-rs` `ShardSet`.

### Artifact-level gaps

Missing artifact fields:

- `contractVersion`
- `artifactId`
- `artifactRevision`
- `artifactClass`
- `createdAtUtc`
- `buildProvenance`

Current nearest local field:

- `ShardSet.name`

That is not enough to model immutable artifact revision, builder provenance, or
cross-sink rebuild identity.

### Per-shard catalog gaps

Missing per-shard fields:

- `section`
- `logicalKind`
- `encoding`
- `sizeBytes`
- `routingKeys`
- `objectRefs[]`

Current local shard refs only expose:

- `id`
- `cid`
- `tags`

That is enough for simple publication, but not enough for Zelph-style selector
resolution or sink-pluggable consumer fetch.

### Sink-model gaps

The shared contract requires explicit multi-sink attachments such as:

- `sink`
- `uri`
- `sizeBytes`
- `contentDigest`
- optional `transportHints`

`erdfa-publish-rs` currently exposes sink helpers as computed URLs, but does
not store sink attachments in the manifest as first-class data.

So today it can suggest:

- "here is how to derive an IPFS or paste/raw URL"

But it cannot yet say:

- "this logical shard is mirrored to HF and IPFS with these exact attached
  object refs"

### Routing-model gaps

The shared contract requires selector/routing semantics such as:

- `route-node=<id>`
- `route-left-node=<id>`
- `route-right-node=<id>`
- `route-name=<exact>`
- `route-lang=<lang>`

`erdfa-publish-rs` has no first-class selector model or routing index in the
manifest.

This is the biggest reason it cannot by itself serve as the full Zelph-facing
contract.

## Practical conclusion

Current best read:

- `erdfa-publish-rs`
  - already works as a real publish/package primitive
  - already proves DA51 CBOR shard + manifest discipline
  - already proves content-addressed shard identity
- ITIR shared contract `v1`
  - is still needed as the bridge layer for:
    - artifact revision/provenance
    - routing keys
    - explicit multi-sink object refs
    - Zelph consumer fetch semantics

So the right move is not to replace the shared contract with
`erdfa-publish-rs`.

It is to treat `erdfa-publish-rs` as the publish-side substrate that needs a
thin richer manifest/contract layer on top.

## Minimal promotion path

If ITIR wanted to promote `erdfa-publish-rs` toward the shared contract, the
smallest useful additions would be:

1. artifact-level identity/provenance fields on `ShardSet`
2. per-shard `encoding`, `sizeBytes`, and `logicalKind`
3. first-class `objectRefs[]` instead of sink helper methods alone
4. optional `routingKeys` for Zelph-facing selector resolution

That would materially reduce the gap without forcing Zelph runtime behavior
into the publish crate.
