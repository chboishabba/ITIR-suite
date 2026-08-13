# Zelph / ERDFA / HF / IPFS Example Flow (2026-03-29)

## Goal

Give one concrete end-to-end example of how the current shared-contract read is
supposed to work:

- `erdfa`/Kant-style packaging emits logical shards
- `HF` and `IPFS` attach sink refs to the same logical shards
- `Zelph` resolves selectors to logical shard ids first
- `Zelph` then fetches those shard payloads from an available sink

This is an example flow, not a claim that every runtime detail is already
implemented in one repo.

## The object being exchanged

The shared-contract object is logical-first.

At minimum it contains:

- `artifactId`
- `artifactRevision`
- `shards[]`
- per-shard `shardId`
- per-shard `routingKeys`
- per-shard `contentDigest`
- per-shard `objectRefs[]`

Each `objectRef` is a sink attachment such as:

- `hf://datasets/...`
- `ipfs://<cid>`
- local `file` path for rehearsal

Important rule:

- sink refs attach to a logical shard
- sink refs do not define the shard's meaning

## Example publication flow

Assume we build one artifact:

- `artifactId = wikidata-2026-demo`
- `artifactRevision = rev-20260329-a`

The publisher emits logical shards like:

- `left-bucket-001`
- `right-bucket-441`
- `nodeOfName-en-017`
- `summary-000`

For `nodeOfName-en-017`, the publisher records:

- `shardId = nodeOfName-en-017`
- `logicalKind = name-bucket`
- `contentDigest = sha256:abc123...`
- `routingKeys = [route-name=tenant, route-lang=en]`

Then it attaches sink refs for the same payload:

- HF object ref:
  `hf://datasets/acrion/zelph-demo/shards/nodeOfName/en/bucket-017.capnp-packed`
- IPFS object ref:
  `ipfs://bafy...`

The publisher may also emit:

- JSON manifest for Zelph/HF-style consumption
- CBOR manifest for ERDFA/Kant/IPFS-style publication

Those two projections must still describe the same:

- `artifactId`
- `artifactRevision`
- `shardId`
- `contentDigest`

## Example query flow: exact name lookup

Assume the user/runtime asks for:

- `route-name=tenant`
- `route-lang=en`

The flow is:

1. Zelph loads the manifest and routing index.
2. Zelph resolves the selector to logical shard ids.
3. The routing index returns:
   - `nodeOfName-en-017`
4. Zelph looks up `objectRefs[]` for that logical shard.
5. Zelph chooses one available sink:
   - HF first for hosted querying, or
   - IPFS/local file if configured
6. Zelph fetches the payload for `nodeOfName-en-017`.
7. Zelph loads that shard and continues the query locally.

Important constraint:

- Zelph does **not** route by inspecting HF path names or IPFS CIDs directly.
- It routes by logical selector -> logical shard id -> chosen sink ref.

## Example query flow: node adjacency lookup

Assume the user/runtime asks for:

- `route-left-node=Q123`

The flow is:

1. Zelph resolves `route-left-node=Q123` through the routing index.
2. The routing index returns logical shard ids such as:
   - `left-bucket-001`
   - `left-bucket-019`
3. Zelph checks those shards' `objectRefs[]`.
4. Zelph fetches the needed payloads from HF or IPFS.
5. Zelph loads only those adjacency shards, not the whole artifact.

This is why the current repo position says:

- Zelph-style sharding is best fit for query-shaped reads
- HF is best fit for practical hosted querying
- IPFS is best fit for immutable publication

## Where `erdfa` fits

`erdfa-publish-rs` is the current best publish-side reference in the repo.

In this flow it is responsible for:

- packaging shard payloads
- assigning stable logical shard identities
- attaching digests
- projecting sink refs
- emitting receipts/manifests

It is not responsible for:

- Zelph query semantics
- selector resolution inside the consumer
- truth construction

## What HF and IPFS each contribute

- HF
  - object hosting convenient for remote partial query
  - easier operational workflow for testing and hosted reads
- IPFS
  - immutable content-addressed publication
  - integrity-first distribution and mirroring

The same logical shard may legitimately exist in both places at once.

## What remains unresolved

This example flow assumes the shared artifact contract, but it does not settle:

- whether Zelph `v2` or `v3` bucket layout is the long-term best query layout
- the final comparison between Zelph-style and Kant-style shard generation
- JMD-side remote host semantics beyond the current reference surfaces

So the right current reading is:

- the logical flow is clear
- the role split is clear
- the long-term optimal shard family is still a comparison question
