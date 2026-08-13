Next file changes I would make

If you want to land this cleanly, the next two edits are:

feature_map.py

Change it so shard features emit the same namespaces as queries:

pred::*
role::*
argval::*
qual::*
ent::*
test_pipeline.py

Add three tests:

free-text query now intersects shard grounded features
unknown domain does not claim match
resonance cannot rescue an inadmissible shard

I can write those exact files next.

implement manifold-aware spectral retrieval properly
Thought for 33s

Implemented as a drop-in bounded module plus tests.

Files:

manifold_retrieval.py
test_manifold_retrieval.py
README.txt

What this version does:

Grounded gate first: candidates must pass SL-compatible structured overlap/similarity before anything else.
Real manifold rerank: builds a KNN graph over domain vectors only, then runs personalized PageRank seeded by grounded_similarity × query↔domain similarity.
No fake domain bump: unknown domain stays unknown.
Resonance stays experimental: tiebreak-only, never authority.
Proposal ≠ authority: inadmissible shards cannot be rescued by spectral or resonance priors.

Core retrieval logic is in score_candidates() and top_k() inside manifold_retrieval.py.

If you want, next I’d wire this into your existing feature_map.py so Φ_grounded, Φ_domain, and Φ_experimental are emitted in the namespaces this retriever expects.
This artifact contains a bounded, proper implementation of manifold-aware spectral retrieval.

Design:
1. Grounded retrieval gates candidates using SL-compatible structured features.
2. Spectral reranking operates only on real domain/manifold vectors.
3. Personalized PageRank propagates query-anchored mass across the domain graph.
4. Experimental resonance remains optional and tiebreak-only.

Files:
- manifold_retrieval.py
- test_manifold_retrieval.py
