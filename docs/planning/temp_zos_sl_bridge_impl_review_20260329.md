# TEMP ZOS/SL bridge review - 2026-03-29

scope
- reviewed bundle:
  `/home/c/Documents/code/ITIR-suite/TEMP_zos_sl_bridge_impl`
- review mode:
  correctness, boundary discipline, and testability before any continuation of current bridge work

main findings
- The prototype originally over-claimed manifold-aware retrieval.
- The initial review found four concrete problems:
  - packaging/tests were not runnable from a clean checkout
  - query and shard features did not intersect enough for cosine similarity to mean what the prototype claimed
  - the domain model was effectively inactive because query domain was always unset
  - the ranking path mixed structured `SL` fact features with a surrogate hash-derived resonance prior that is not query-grounded and is not derived from `SL` facts or zkperf invariants

current status after patch
- Fixed:
  - packaging/tests now run in `python/`
  - query/shard vectors now share lexical `lex::*` features derived from structured fact content and query projection
  - domain scoring is now query-sensitive, using explicit `domain_hint` values when present and centroid assignment otherwise
  - an explicit admissibility / acceptance boundary now exists after ranking:
    - `manifold_aware_rank(...)` remains candidate generation
    - `admissibility_filter(...)` now emits accepted/rejected decisions with reasons
    - `manifold_aware_select(...)` composes the two stages
  - resonance is now demoted to proposal/tiebreak only:
    it no longer contributes to the core correctness score
- Still open:
  - policy tuning remains heuristic:
    thresholds and acceptance rules are now explicit, but still provisional

governance reading
- Keep `SL` as truth authority.
- Keep `ZOS` in the proposal layer only.
- Resonance may exist only as proposal/tiebreak signal, never as correctness or truth authority.
- Domain/manifold logic must be real and query-sensitive, not a constant score prior.
- Structural reading:
  - `ZOS` stands to `SL` as `CLOCK` stands to `DASHI`
  - proposal/microphase space is upstream of admissible/promoted state
  - projection alone is not enough; admissibility still has to be enforced

recommended direction
- Do not treat this bundle as final integration material yet.
- Salvage path:
  - keep the packaging/tests fix
  - keep the query/shard structured lexical intersection
  - keep the query-sensitive domain/manifold scoring
  - keep the explicit admissibility / acceptance boundary between ranking and accepted outputs
  - keep resonance only as a proposal/tiebreak layer, not as a core correctness score
- Preferred operator shape:
  - `manifold_aware_rank -> candidate set`
  - `admissibility filter -> accepted set`
  - `promotion/output boundary -> promoted outputs`

priority reading
- This bridge is no longer the first implementation priority while the
  affidavit local-first proving slice still has a coarse mixed classifier.
- Near-term priority order:
  1. affidavit root/incident clustering and operator-facing lineage quality
  2. threshold calibration in this temporary bridge
- Even with the new admissibility stage, keep this bundle bounded as
  proposal/retrieval infrastructure rather than promoted truth machinery.

validation
- reviewed:
  `python/zos_pipeline/retrieval.py`
  `python/zos_pipeline/feature_map.py`
  `python/zos_pipeline/monster_lattice.py`
  `python/tests/test_pipeline.py`
  `docs/INTEGRATION_NOTE.md`
- executed:
  `pytest -q` in `TEMP_zos_sl_bridge_impl/python`
  `python -m zos_pipeline.cli --query "tenant mould complaint" --admit`
- result:
  passing after the packaging/tests patch and admissibility-stage addition
