# Zelph External Handoff Note (2026-03-20)

## Purpose
This note is the short, technically grounded document we can point a Zelph
developer at so they understand what SensibLaw/ITIR is doing, what has already
been demonstrated locally, and where we think a clean collaboration boundary
could exist.

It is intentionally upstream-facing and should not be read as a claim that
SensibLaw depends on Zelph or that a deep integration contract already exists.

## Current Positioning
SensibLaw is working primarily at the text-to-structure boundary:

- deterministic ingest from messy source corpora into explicit facts,
  observations, claims, events, and review states
- provenance-preserving storage so downstream reasoning can always be traced
  back to source material
- operator-facing review surfaces to prevent silent fact inflation
- semantic materialization and benchmark loops to test stability before any
  stronger reasoning/export claims

The intended relationship to Zelph is:

- SensibLaw upstream:
  extract, normalize, review, and preserve provenance over facts from text
- Zelph downstream:
  reason over already-structured graph facts, constraints, and rules

This is a bridge/demo posture, not a dependency posture.

## What Has Already Been Demonstrated
### 1. Database atom ingest into Zelph
Repo evidence:
- `SensibLaw/sl_zelph_demo/compile_db.py`
- `SensibLaw/sl_zelph_demo/db_rules.zlp`
- `SensibLaw/tests/test_sl_zelph_demo_tools.py`

Current demonstrated behavior:
- `compile_db.py` exports `rule_atoms` from SQLite into Zelph facts/rules
- modality atoms like `modality.must` and `modality.may` are projected into
  Zelph
- Zelph rules classify obligations and permissions over the exported atoms

### 2. Lexical graph projection into Zelph
Repo evidence:
- `SensibLaw/sl_zelph_demo/lex_to_zelph.py`
- `SensibLaw/sl_zelph_demo/wiki_lex_rules.zlp`
- `SensibLaw/sl_zelph_demo/wiki_inferred.txt`

Current demonstrated behavior:
- Wikipedia revision comments are tokenized into ordered lexical node sequences
- recursive Zelph rules match those lexical graphs
- the demo identifies reversion edits and infers a `wiki sentinel` role from a
  revision-history pattern

### 3. Fact-semantic benchmark calibration
Repo evidence:
- `SensibLaw/scripts/benchmark_fact_semantics.py`
- `SensibLaw/scripts/run_fact_semantic_benchmark_matrix.py`
- `SensibLaw/tests/fixtures/fact_semantic_bench/README.md`
- `SensibLaw/tests/fixtures/fact_semantic_bench/results/`

Current demonstrated behavior:
- benchmark runs exist for:
  - `wiki_revision`
  - `chat_archive`
  - `transcript_handoff`
  - `au_legal`
- the benchmark records `refresh_status`, stage, fact counts, and elapsed time
- recent checked-in result fixtures show `refresh_status == "ok"` on the
  benchmark paths we are using as the current baseline

## What We Are Actually Trying To Prove
The near-term claim is not "Zelph solves our ingest problem."

The near-term claim is:

1. SensibLaw can deterministically convert unstructured corpora into explicit,
   provenance-preserving fact structures.
2. A compact, meaningful subset of those facts can be projected into Zelph
   without losing the upstream provenance story.
3. Zelph can then reason over the exported structure in a way that is useful,
   testable, and clearly downstream of the ingest/review layer.

That is why the current bridge is intentionally tiny and deterministic.

## What We Think Is Interesting About Zelph
Based on Stefan's description and our own demo work, the most interesting
collaboration surfaces are:

- graph-native predicates as first-class nodes
- constraint/negation-oriented reasoning over already-structured facts
- probability-aware fact treatment, if that capability becomes script/runtime
  visible in a practical way
- Janet-enabled ingest/transform/runtime surfaces, where appropriate

The interesting overlap is not raw text parsing inside Zelph by default; it is
what Zelph can do once SensibLaw has already produced stable, provenance-backed
graph structure.

## Boundary We Want To Keep Clean
- SensibLaw should remain the authority for ingest, extraction, review, and
  source traceability.
- Zelph should be treated as a reasoning engine over exported graph structure.
- We should avoid describing the current work as a full runtime integration.
- We should avoid shipping personal or sensitive benchmark/result JSONs to third
  parties until they are reviewed and sanitized.

## What We Can Safely Point To
Likely safe to share after one final review:
- `SensibLaw/sl_zelph_demo/`
- `SensibLaw/tests/test_sl_zelph_demo_tools.py`
- this note

Needs review/sanitization before external sharing:
- benchmark result JSONs under
  `SensibLaw/tests/fixtures/fact_semantic_bench/results/`
- any chat-derived or transcript-derived corpora
- any local analysis artifacts that may contain personal or case-linked content

## Suggested Questions / Next Discussion Points
- What is the cleanest stable export shape from SensibLaw into Zelph:
  direct graph facts, richer predicate-as-node exports, or a small Janet-facing
  ingest bridge?
- Should probabilities/uncertainty stay purely upstream at first, or is there a
  concrete Zelph-side use case worth shaping now?
- Which tiny benchmark slice would best demonstrate downstream reasoning value
  without forcing premature architectural coupling?

## One-sentence Summary
SensibLaw is trying to make text-derived facts stable, reviewable, and
provenance-preserving before handing a compact graph slice to Zelph for
downstream reasoning.
