# Spectral Post-Selector Retrieval Contract (2026-03-29)

## Goal

Define one small contract for the optional ranking/compression layer that runs
after selector resolution and before remote fetch.

This note exists to keep spectral/eigenvector retrieval from blurring into:

- selector/routing semantics
- logical shard identity
- SL truth construction

## Scope

This contract is only for post-selector ranking of candidate shards.

It is **not**:

- the selector/routing contract
- the logical shard contract
- the HF container/index contract
- the SL promotion/truth contract

## Core decision

Spectral retrieval is optional and strictly downstream of selector resolution.

So the required ordering is:

`selector -> logical shard ids -> spectral ranking -> fetch subset`

Not:

`query -> spectral embedding -> infer shard identity`

## Required precondition

Spectral retrieval may only run on an already-resolved candidate set of logical
shard ids.

That means:

1. resolve query selectors normally
2. obtain candidate logical shard ids
3. compute structured features over query/candidate space
4. rank or compress the candidate set
5. fetch the chosen subset

## Feature-basis rule

The feature map must be built from structured system outputs.

Allowed feature sources:

- SL facts
- predicates
- argument roles
- qualifiers
- provenance-linked structured fields
- zkperf trace structure
- other explicitly modeled system state

Disallowed feature sources:

- raw token frequency
- bag-of-words co-occurrence
- generic embeddings with no system-structural grounding
- sink path strings as semantic proxies

## Output contract

The spectral layer should produce a bounded ranking artifact, not mutate the
underlying shard contract.

Minimum useful outputs:

- `queryId`
- `candidateShardIds[]`
- `rankedShardIds[]`
- optional per-shard score
- optional explanation/features summary
- ranking metadata:
  - feature basis version
  - ranking method id
  - timestamp or run id

## Consumer rule

Consumers may use the ranking layer to reduce fetch size, but they must not
treat ranking output as identity or truth.

So:

- ranked shards are still only candidate fetch priorities
- selector resolution remains the authoritative way shards enter the candidate
  set
- SL-promoted truth remains upstream and unaffected

## Manifold/domain rule

The ranking layer must preserve domain validity.

Practical rule:

- do not assume all queries, traces, and shards live in one globally
  comparable space
- ranking should be computed within an explicitly valid domain/manifold
- projection collapse or "no good neighbors" must be allowed as a real result

So acceptable outcomes include:

- good ranking
- weak ranking
- abstention / no stable neighborhood

## Abstention rule

The spectral layer must be allowed to abstain.

If the feature space is too sparse, too mixed, or outside a valid domain, the
layer should return:

- no compression
- low-confidence ranking
- or a pass-through fetch of the unranked candidate set

This avoids turning heuristic failure into false semantic certainty.

## Relationship to HF batching

If HF batching/containerization exists, spectral retrieval still acts on
logical shard ids first.

So the composed flow becomes:

`selector -> logical shard ids -> spectral ranking -> container index -> HF object -> member payload`

This preserves the layer order:

- routing first
- ranking second
- container resolution third
- transport fetch fourth

## What this buys us

This layer exists to improve:

- median fetch size
- tail fetch size
- query responsiveness
- prioritization of the most aligned shards first

Without changing:

- shard identity
- selector semantics
- truth authority

## What remains open

This note does not decide:

- exact feature schema
- exact linear algebra / ranking method
- whether "eigenvector" means PCA-like reduction, graph spectrum, or another
  structured ranking method
- how ranking explanations are surfaced to operators

## Promotion criteria

Treat this layer as promotable only if it shows all of:

- better fetch efficiency than unranked selector-only retrieval on the same
  workload
- no mutation of selector semantics
- no use of raw-token/generic-embedding shortcuts
- clean abstention when domain validity fails
