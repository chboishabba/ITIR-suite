# Shard Stack Layer Order (2026-03-29)

## Goal

Give one one-page end-to-end stack ordering for the current shard/retrieval
design without introducing any new theory.

## Layer order

The current intended order is:

1. `SL`
   - truth/promotion authority
   - emits structured facts and provenance-bearing outputs
2. logical shard/artifact contract
   - defines `artifactId`, `artifactRevision`, `shards[]`, routing/selectors,
     per-shard `contentDigest`, and sink refs
3. optional spectral post-selector ranking
   - ranks already-resolved candidate shard ids using structured features
4. optional HF container/index layer
   - groups logical shard payloads into fewer uploaded HF objects
5. sink fetch
   - HF / IPFS / local file object retrieval
6. `Zelph`
   - local load/query/reasoning over fetched payloads

## Canonical flow

The clean composed flow is:

`SL outputs -> logical artifact/shards -> selector -> logical shard ids -> optional spectral ranking -> optional container index -> sink object -> payload -> Zelph load/query`

## Layer responsibilities

- `SL`
  - decides structured truth/promotion
  - does not do sink routing or ranking heuristics
- logical shard/artifact contract
  - decides shard identity, selector space, and sink-neutral meaning
- spectral layer
  - only ranks candidate shards after selector resolution
  - does not define shard identity or truth
- HF container/index layer
  - only batches uploads and maps shard ids to container membership
  - does not define shard identity or selector semantics
- sink layer
  - only stores/fetches objects
- `Zelph`
  - consumes fetched payloads for local query/reasoning

## Ordering constraints

Keep these ordering rules explicit:

- selector resolution must happen before spectral ranking
- spectral ranking must happen before HF container resolution if both exist
- HF object layout must not define logical shard identity
- sink location must not define selector semantics
- SL truth/promotion must remain upstream of all retrieval heuristics

## Short form

If you need the compressed version, use:

`truth -> shards -> rank -> batch -> fetch -> reason`

Where:

- `truth` = `SL`
- `shards` = logical artifact contract
- `rank` = optional spectral post-selector layer
- `batch` = optional HF container/index layer
- `fetch` = HF/IPFS/file object retrieval
- `reason` = `Zelph`
