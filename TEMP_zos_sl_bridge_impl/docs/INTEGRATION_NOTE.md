# SL ↔ erdfa/Kant ↔ Zelph Prototype

This package implements a bounded prototype of:

1. Monster-hash surrogate → orbifold projection `(h % 71, h % 59, h % 47)`
2. Resonance test in the `o71-o59` plane using the generator offset from the uploaded SVG
3. `Φ` feature map combining:
   - SL fact features
   - shared lexical features for query/shard intersection
   - zkperf trace-window features
   - lattice resonance features
4. Query-sensitive domain assignment:
   - prefer explicit `domain_hint` values from trace windows when present
   - otherwise cluster trace windows with k-means and infer shard domains
   - assign query domain by nearest domain centroid in the same feature space
5. Manifold-aware spectral retrieval:
   - selector/candidate set assumed upstream
   - rank candidate shards by cosine similarity over `Φ`
   - add domain-match prior only (resonance is tiebreak-only)

## Important limitation

The exact `monster-hash(file)` algorithm was not available in the pasted artifact.  
This prototype uses a SHA-256-derived 64-bit integer as a deterministic stand-in, behind a replaceable function.

Resonance is now tiebreak-only and is not part of the core rank score.

An explicit post-ranking admissibility boundary is now implemented:

1. `manifold_aware_rank(...)` generates candidate rankings.
2. `admissibility_filter(...)` applies bounded gates:
   - `score >= min_score`
   - structured alignment (`domain_match == 1.0` or `spectral_score >= min_spectral`)
   - optional rejection of resonance-only signals
3. `manifold_aware_select(...)` returns accepted/rejected decisions with reasons.

## Test entry points

- Python:
  - `python -m zos_pipeline.cli --query "tenant mould complaint"`
- Rust:
  - `cargo run`

## Suggested next validation steps

- replace surrogate hash with real `monster-hash`
- feed real zkperf trace windows
- compare retrieval precision@k against SL-promoted facts
- keep resonance in proposal/tiebreak only
