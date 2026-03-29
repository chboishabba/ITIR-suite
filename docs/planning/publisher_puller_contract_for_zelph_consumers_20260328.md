# Publisher/Puller Contract for Zelph Consumers (2026-03-28)

## Goal

Make the publish/pull split explicit without implying that `Zelph` itself owns
publication.

## Core clarification

`Zelph` is a consumer of logical shard artifacts.

It needs a publisher/puller contract to serve those artifacts, but it is not
itself the publish-layer authority.

So the correct reading is:

- publisher/puller side
  - emits logical artifacts, sink refs, and receipts
- consumer side
  - resolves selectors to logical shards, fetches payloads, and loads/querys
    them in `Zelph`

## Role split

- `Zelph`
  - read/query consumer
  - selector/routing-driven partial loader
  - downstream graph query surface
- publisher/puller
  - logical artifact emitter
  - sink attachment / retrieval surface
  - receipt and identity discipline
- sinks
  - `hf`, `ipfs`, `file`
  - storage/transport endpoints, not semantic authorities

## Practical flow

Publisher/puller flow:

`logical artifact -> shard ids -> sink refs -> receipt`

Zelph consumer flow:

`selector -> logical shard ids -> fetch -> Zelph load/query`

## Implications

This means:

- do not describe `Zelph` as the publish layer
- do not collapse sink layout into consumer semantics
- do not let publisher code define truth or reasoning semantics
- do let consumer/runtime code assume one stable logical artifact contract

## Current best-fit read

- Zelph-style sharding
  - best current fit for query-shaped reads
- Kant-style packaging
  - best current fit for publish/pull identity and content-addressed artifact
    packaging
- ZOS or a separate publisher crate
  - best current fit for orchestration around publication/retrieval, not for
    consumer-side reasoning

## ITIR-facing consequence

For `ITIR`, the useful abstraction is not "build a Zelph publisher".

It is:

- keep `SL` / truth / promotion upstream
- keep `Zelph` downstream as a query consumer
- keep publish/pull as a separate artifact-serving layer
- let one shared logical artifact contract connect them

That makes the missing work:

- consumer contract clarity, not consumer ownership of publication
- publisher/puller discipline, not publisher authority over semantics
