# Zelph `.bin` Sharding/Partial-Load Note (2026-03-26)

## Observed format (from `src/lib/io/zelph.capnp`, `zelph_impl.hpp`)
- Main message: `ZelphImpl` (Cap’n Proto) stores counts: `leftChunkCount`, `rightChunkCount`, `nameOfNodeChunkCount`, `nodeOfNameChunkCount`, plus prob list and bookkeeping.
- Chunks: `AdjChunk` (`which` = `"left"`/`"right"`, `chunkIndex`, list of `AdjPair { node, adj[] }`), `NameChunk` (`lang`, `chunkIndex`, list of `NamePair { key(Node), value(Text) }`), `NodeNameChunk` (`lang`, `chunkIndex`, list of `NodeNamePair { key(Text), value(Node) }`).
- Save path writes:
  1) packed main message
  2) left chunks (packed, sequential)
  3) right chunks
  4) name_of_node chunks
  5) node_of_name chunks
- Chunk size at save: `chunkSize = 1 << 21` elements (see `saveToFile`).
- Load path reads header, then streams all packed chunks in order; no offset table; always full materialization to adjacency/name maps.

## Sidecar offset index (proposed)
- One JSON (or binary) index alongside `.bin`:
  - `main`: `{offset, length}`
  - `left`: list of `{chunkIndex, offset, length}`
  - `right`: list …
  - `nameOfNode`: list …
  - `nodeOfName`: list …
- Indexer algorithm (single pass):
  - open file; `pos=0`
  - read packed message (header); record `offset=0`, `length=pos_after - offset`
  - for each section in order (left, right, nameOfNode, nodeOfName):
    - for `count` from header, read packed message, record `chunkIndex` from payload, plus `offset`, `length`
    - advance `pos` by bytes consumed
- This yields byte ranges usable for local random access or HTTP `Range` reads.

## Partial-load loader sketch
- Add loader entry that takes a chunk selector:
  - adjacency: list of left/right chunk indexes
  - names: optional lang filter + chunk indexes
  - if selector empty, load header only (for stats) or bail
- Use sidecar index to seek to needed ranges; otherwise scan to build offsets on the fly.
- For remote: fetch ranges via HTTP; decode each packed message as today; build partial maps.
- Caveats:
  - adjacency chunks are range-partitioned over node IDs (sorted by map iteration at save); need to confirm monotonic iteration to avoid missing nodes when partial.
  - name chunks are per-language, but chunk order is per-language section, sorted by node or key; partial loads must tolerate missing chunks (maps will be incomplete).
  - current algorithms expect full maps; partial mode should be opt-in and clearly documented as “incomplete graph.”

## Questions for upstream
1) OK to add a sidecar offset index and a loader that accepts a chunk selector?
2) Are there invariants (e.g., cross-chunk assumptions) that would break if only a subset of chunks is loaded?
3) Should chunking key change (e.g., explicit node ranges) to make selective loads meaningful?
4) Would you accept emitting the offset table inside the main message (extra list of offsets) versus a sidecar file?

## Next local steps
- Write a small indexer that emits the sidecar for existing `.bin` files (header + ranges).
- Add a “stats-only”/“header-only” mode to report counts without full load.
- Prototype a selector-based loader path to prove partial adjacency/name loads work for read-only inspection.***
