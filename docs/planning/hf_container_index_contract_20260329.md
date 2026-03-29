# HF Container/Index Contract (2026-03-29)

## Goal

Define one small contract for batching logical shard payloads into HF-friendly
uploaded objects without collapsing:

- logical shard identity
- selector/routing semantics
- sink-neutral artifact meaning

This note exists because HF file-count/rate limits are now an explicit design
constraint, not just an operational annoyance.

## Scope

This contract is only for the HF batching/container layer.

It is **not**:

- the logical shard contract itself
- the selector/routing contract itself
- the spectral retrieval contract

Those remain separate layers.

## Core decision

Keep the logical artifact contract primary.

HF containerization is a projection layer that groups already-defined logical
shards into fewer uploaded objects.

So the correct ordering is:

`logical shards -> container membership -> uploaded HF objects -> published index`

Not:

`HF object layout defines the logical shards`

## Minimal staged model

Use this publication sequence:

`microshards -> sealed container -> uploaded object -> published manifest index`

Where:

- microshards
  - logical shard payloads from the shared artifact contract
- sealed container
  - one upload unit bundling many logical shard payloads
- uploaded object
  - one HF-hosted file
- published manifest index
  - metadata that maps logical shard ids to container membership and object refs

## Preferred physical layout

Current best-fit physical direction:

- outer format:
  `tar`
- payload members:
  `CBOR`
- control/meta:
  `JSON`
- compression:
  optional `zstd`

This is a batching choice, not a semantic identity choice.

## Required identity rule

Container membership must not redefine shard identity.

That means:

- logical shard id remains stable whether a shard is uploaded alone or inside a
  container
- `contentDigest` remains the identity anchor for the payload
- HF object path is only an attached location

## Required index fields

The HF container/index layer should add enough metadata to recover logical
shards from a containerized upload.

Minimum useful fields:

- `containerId`
- `containerRevision`
- `containerEncoding`
- `containerObjectRef`
- `members[]`

Each member entry should contain:

- `shardId`
- `contentDigest`
- `memberPath` or member name inside the container
- `sizeBytes`
- optional byte offset metadata if random access later becomes desirable

## Relationship to the shared artifact contract

The shared artifact contract still owns:

- `artifactId`
- `artifactRevision`
- `shards[]`
- `routingKeys`
- sink-neutral `objectRefs[]`

The HF container/index contract only adds:

- how multiple logical shards are grouped into one HF object
- how the consumer or puller finds the correct member payload inside that HF
  object

## Consumer rule

Selector/routing still resolves to logical shard ids first.

Then:

1. resolve selector -> logical shard ids
2. resolve logical shard ids -> container membership / HF object ref
3. fetch needed HF object(s)
4. extract needed member payload(s)
5. load/query in Zelph or another consumer

So the consumer model becomes:

`selector -> logical shard ids -> container index -> HF object -> member payload -> local load/query`

## Publisher rule

Publisher responsibilities at this layer:

- batch logical shard payloads into fewer upload objects
- publish the container object(s)
- publish the membership/index metadata
- preserve digest-anchored member identity

Publisher may not:

- redefine selector semantics
- redefine shard identity from HF path names
- smuggle ranking heuristics into the manifest as if they were truth/routing

## What this buys us

This layer exists to reduce:

- HF file-count pressure
- HF file-rate pressure
- upload overhead for many tiny shard objects

While preserving:

- logical shard identity
- selector-first retrieval
- multi-sink compatibility

## What remains open

This note does not yet decide:

- exact container size targets
- whether tar member offsets should be indexed for partial extraction
- whether one global index or partition-local indexes are better
- how IPFS mirrors should represent the same grouped upload
- how spectral ranking should annotate or prioritize candidate shards after
  selector resolution

## Promotion criteria

Treat this layer as promotable only if it can show all of:

- lower HF file pressure than one-object-per-microshard upload
- no change to logical shard ids or selector semantics
- deterministic rebuild from the same logical artifact
- clean recovery from container index to member payload
