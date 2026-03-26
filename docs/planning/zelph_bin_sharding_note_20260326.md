# Zelph `.bin` Sharding/Partial-Load Note (2026-03-26)

## Observed format (from `src/lib/io/zelph.capnp`, `zelph_impl.hpp`)
- Main message: `ZelphImpl` (Cap’n Proto) stores counts:
  `leftChunkCount`, `rightChunkCount`, `nameOfNodeChunkCount`,
  `nodeOfNameChunkCount`, plus bookkeeping and graph/probability payloads.
- Chunks are:
  - `AdjChunk` (`which` = `"left"`/`"right"`, `chunkIndex`, list of `AdjPair { node, adj[] }`)
  - `NameChunk` (`lang`, `chunkIndex`, list of `NamePair { key(Text), value(Text) }`)
  - `NodeNameChunk` (`lang`, `chunkIndex`, list of `NodeNamePair { key(Text), value(Node) }`)
- Save writes packed messages in this order:
  1) header
  2) all left chunks
  3) all right chunks
  4) all nameOfNode chunks
  5) all nodeOfName chunks
- Load currently reads header + every packed chunk sequentially and materializes full maps.

## Sidecar index
- `tools/zelph_bin_indexer.cpp` emits `header/left/right/nameOfNode/nodeOfName`
  ranges as `(chunkIndex, offset, length[, which/lang])`.
- The indexer is sufficient to map chunk selectors to byte ranges for range fetch
  or local seek.

## Production direction
- `zelph-hf-layout/v1`:
  - keep monolithic `.bin` + sidecar, remote via HTTP `Range`, useful migration baseline.
- `zelph-hf-layout/v2`:
  - explicit object-per-chunk manifests
  - optional local shard emission using:
    `tools/build_zelph_hf_manifest.py --layout v2 --emit-shards --shard-root ...`
- This is now a concrete, concrete file-and-manifest split path, not only a paper design.

## Safe partial-load scope
- Keep partial load read-only:
  - header stats
  - selected chunk inspection (left/right adjacency)
  - selected name/object chunk reads
- Blocked operations remain:
  - inference
  - pruning
  - cleanup
  - edit/save/import

## Loader implications
- Chunk selectors are still section-local and file-derived.
- v1 still helps for backward compatibility and small transition; v2 should be treated
  as the target shape for HF-native querying.
- Practical next move in Zelph:
  - consume sidecar offsets directly (no full sequential scan)
  - fetch only selected chunks
  - switch transport from local range-only to object path + local cache for v2

## Open questions
1) Chunk-to-shard routing policy for higher-level reads: only selector-level now, or route cache for `QID -> candidate chunks`?
2) What route table granularity is acceptable (exact QID hash, language bucket, or node-range)?
3) What metadata is mandatory in object entries (`checksum`, `etag`, `expires`, `lastModified`) for cache correctness?

## Quality Snapshot (2026-03-26)
- Bins available:
  - `/home/c/Documents/code/ITIR-suite/wikidata-20171227-pruned.bin` (1.4 GB)
  - `/home/c/Documents/code/ITIR-suite/wikidata-20260309-all-pruned.bin` (~5.6 GB)
- Verified local commands:
  - `.stat-file` on both bins reads chunk counts and file size.
  - `.index-file` on 2017 bin writes index entries and offsets.
  - `.load-partial` on `.bin` inputs supports explicit selectors plus `-`/`none` for section skips.
  - `.load-partial ... meta-only` is fast and stable.
- Current regression boundary:
  - direct `.bin` partial reads of adjacency chunks are functional (e.g.
    `left=0 right=none nameOfNode=none nodeOfName=none`).
  - manifest-driven `.load-partial` with selected sections is now functional on both local bins.
  - explicit section skip (`left=none`, etc.) works and confirms loader wiring.
- Interpretation:
  - `.bin` partial path is currently production-adjacent for targeted local inspection.
  - manifest chunk transport is now locally viable for the bounded selector cases we tested.

## Root Cause Closed
- Earlier manifest failures were caused by sidecar offset drift, not by an inherent
  Cap'n Proto message-size limitation on the tested bins.
- The bug source:
  - offset/length accounting in the indexers counted bytes through
    `kj::BufferedInputStreamWrapper`, which can read ahead beyond the current
    message boundary.
- Fix:
  - use a counting buffered stream that tracks bytes actually consumed by the
    reader, so `offset` and `length` line up with true packed-message boundaries.
- Effect:
  - `manifest_v1_left0`
  - `manifest_v2_left0`
  - `manifest_v1_nameOfNode0`
  - `manifest_v2_nameOfNode0`
  all now load directly on both the 2017 and 2026 artifacts without fallback.

## Concrete next local steps
- DONE:
  - sidecar index generator exists: `tools/zelph_bin_indexer.cpp`
  - exact prototype route-sidecar generator exists: `tools/zelph_bin_route_builder.cpp`
  - v1 + v2 manifest generation in `tools/build_zelph_hf_manifest.py`
  - v2 shard materialization option in `build_zelph_hf_manifest.py`
  - manifest coverage in `tests/test_build_zelph_hf_manifest.py`
- Next:
  - wire route-sidecar consumption into patched Zelph loader transport layer
  - move route-sidecar output beyond large prototype JSON if this lane stays active
  - wire v2 manifest consumption into patched Zelph loader transport layer
  - add one real remote-object smoke for selected-chunk fetch

## Shared Artifact Run (smallest local bin): 2017-pruned
- Inputs:
  - `wikidata-20171227-pruned.bin` (1.4 GB)
  - derived index: `/tmp/wikidata-20171227-pruned.bin.index.json` (4.1 KB)
- Commands:
  - `tools/zelph_bin_indexer /home/.../wikidata-20171227-pruned.bin > /tmp/wikidata-20171227-pruned.bin.index.json`
  - `clang++ -fuse-ld=lld -std=c++17 -O2 -I aur/zelph/build-local/src/lib/io tools/zelph_bin_route_builder.cpp aur/zelph/build-local/src/lib/io/zelph.capnp.c++ -lcapnp -lkj -pthread -o tools/zelph_bin_route_builder`
  - `tools/zelph_bin_route_builder /home/.../wikidata-20171227-pruned.bin /tmp/wikidata-20171227-pruned.route.json`
  - `python tools/build_zelph_hf_manifest.py --bin ... --index ... --output /tmp/wikidata-20171227-pruned.hf-v1.json --layout v1`
  - `python tools/build_zelph_hf_manifest.py --bin ... --index ... --output /tmp/wikidata-20171227-pruned.hf-v2.json --layout v2 --emit-shards --shard-root /tmp/wikidata-20171227-pruned-shards`
  - `python tools/build_zelph_hf_manifest.py --bin ... --index ... --output /tmp/wikidata-20171227-pruned.hf-v2.with-route.json --layout v2 --node-route /tmp/wikidata-20171227-pruned.route.json`
- Resulting checksums:
  - bin: `4323de237969702e77b0a05b37a4ac898b56c9da5aca7526e25ffabccf9515c7`
  - manifest v1: `acf8ec436cdff5ec8960e8524ee2a94deccc49b8c6b646ab7d099e1673cc9d55`
  - manifest v2: `0d0a61af63446c5379b8f0443a63d0289e66b8554583acbb629bd0b870ae4c2d`
- Layout summary:
  - shard sections: left 18, right 18, nameOfNode 8, nodeOfName 8
  - emitted shards: 52 files, ~1.4 GiB total
  - route sidecar prototype: `/tmp/wikidata-20171227-pruned.route.json` (~735 MiB)
  - naming now includes language in shard filenames for multilingual sections:
    `chunk-000000-en.capnp-packed` and `chunk-000000-wikidata.capnp-packed` coexist safely.
