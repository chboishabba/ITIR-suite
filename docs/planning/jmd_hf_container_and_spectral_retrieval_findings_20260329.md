# JMD HF Container and Spectral Retrieval Findings (2026-03-29)

## Goal

Record the latest materially useful additions from the refreshed JMD thread
`69c4a9b1-d014-83a0-8bb0-873e4eaa4098` without blurring them into existing SL,
shard, or transport contracts.

## Thread provenance

- title:
  `JMD FORMAL EXPLAIN - Meme System Explanation`
- online UUID:
  `69c4a9b1-d014-83a0-8bb0-873e4eaa4098`
- canonical thread ID:
  `c6e383233d0d7c4efde671be1432c825054cb222`
- source used:
  `db` after repeated direct UUID pulls into the canonical archive
- latest refreshed timestamp used in this pass:
  `2026-03-28T15:14:51+00:00`

## Current finding

The thread now sharpens three things beyond the earlier semantic/proof-first
read:

1. the logical artifact contract is more mature than "missing API"
2. HF file-count/rate pressure is a real container-design constraint
3. spectral ranking should be treated as a retrieval layer over the existing
   selector/shard contract, not as a replacement for it

## Matured contract read

The refreshed thread explicitly accepts the existing repo-facing logical
artifact shape as real:

- `artifactId`
- `artifactRevision`
- `shards[]`
- routing/selectors
- per-shard `contentDigest`
- multi-sink refs

So the gap is no longer:

- "is there any contract?"

It is now better described as:

- how stable the contract is
- how implemented it is across Zelph / `erdfa` / HF / IPFS
- how query-efficient it is under real transport constraints

## HF container/index finding

The thread now adds a concrete pressure model for HF publication:

- bandwidth is one bottleneck
- HF file-count / file-rate limits are another bottleneck

That implies a more containerized upload pipeline than simple one-object-per-
microshard publication.

The useful proposed staging model is:

`microshards -> sealed container -> uploaded object -> published manifest index`

Proposed concrete direction:

- outer format:
  `tar`
- payload members:
  `CBOR`
- control/meta:
  `JSON`
- compression:
  optional `zstd`

This should be read as a batching/container direction for HF-hosted push/pull,
not as a replacement for the logical shard contract itself.

## Spectral retrieval finding

The thread also adds a second-layer retrieval idea on top of the existing
selector/shard contract:

`selector resolution -> candidate shard set -> spectral ranking/compression -> fetch best few`

Important interpretation rule:

- selector/routing still comes first
- spectral ranking is an optimization/ranking layer over candidate shards
- it is not a substitute for logical shard identity or selector semantics

## Structured-feature constraint

The thread's later corrections make the feature-source rule explicit:

- acceptable feature basis:
  - SL facts
  - predicates / argument roles / qualifiers
  - zkperf trace structure
  - structured system outputs
- unacceptable feature basis:
  - raw tokens
  - naive co-occurrence
  - generic embeddings with no system-structural grounding

So any future "eigenvector / harmony" retrieval work should be constrained to
structured features, not free-floating embedding rhetoric.

## Manifold correction

The latest pasted navigator/manifold turns contribute one more useful
restriction:

- meaning/symmetry should be treated as valid only within a manifold/domain
- projection collapse is a real failure mode, not just philosophical language

For current planning this means:

- ranking/compression layers must preserve domain validity
- no assumption that all shards/traces/queries are comparable in one global
  space

## Practical ITIR reading

The clean current stack is:

- SL
  - truth / promotion / structured fact authority
- erdfa/Kant-style layer
  - logical shard packaging, identity, receipts, sink refs
- Zelph
  - selector-first read/query consumer
- optional spectral layer
  - ranks candidate shards after selector resolution using structured features
- HF container/index layer
  - batches upload artifacts to survive bandwidth + file-count constraints

## What this does not justify

This new thread state still does not justify:

- replacing selector routing with spectral retrieval
- using raw embeddings as the retrieval substrate
- treating HF containerization as the semantic artifact contract
- collapsing SL truth logic into ranking heuristics

## Practical follow-up

The next useful repo move is to keep these as separate but related notes:

- logical artifact contract
- HF container/index batching contract
- optional spectral post-selector retrieval layer

That keeps transport, artifact identity, and retrieval heuristics from
collapsing into one vague "API" idea.
