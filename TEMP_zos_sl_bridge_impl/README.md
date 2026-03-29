# ZOS / SL bridge implementation bundle

This artifact contains:

- `python/zos_pipeline/`
- `python/tests/`
- `rust/zos_pipeline_rs/`
- `docs/INTEGRATION_NOTE.md`

Generated as a bounded reference implementation for:

- resonance pipeline
- Φ feature map
- query/shard lexical feature intersection
- query-sensitive domain classifier from traces
- manifold-aware spectral retrieval
- post-ranking admissibility filter

Current status:
- packaging/tests are runnable from `python/`
- resonance remains heuristic and is not yet separated into a pure proposal/tiebreak layer
- admissibility is now explicit as a second stage:
  `manifold_aware_rank -> admissibility_filter -> accepted/rejected decisions`
