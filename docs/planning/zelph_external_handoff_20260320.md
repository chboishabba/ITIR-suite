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

## Current Status Snapshot (2026-03-23)
What is already real in the repo:
- small Zelph-facing demos exist and are still the cleanest shareable proof
  points
- benchmark/calibration artifacts exist for multiple corpora, but not all of
  them are appropriate to hand externally without review
- deterministic Zelph-facing export slices (DB/rule-atom, ontology bridge,
  sanitized fact-semantic bench examples) now exist and can be stitched together
  into a contrasted pack that tells the ingest->provenance->Zelph story
- the current intended claim remains behavior-level:
  bounded downstream reasoning over exported fact structure, not raw-text
  ingestion inside Zelph

What is still uncertain:
- whether probability/uncertainty handling should remain entirely upstream for
  the first collaboration slice
- whether the cleanest first export is:
  graph facts, predicate-as-node exports, or a Janet-facing bridge
- which benchmark/result fragments are safe enough to externalize without
  leaking personal or case-linked material

## Zelph Dev Contact Surfaces
These are the repo surfaces a Zelph developer can be pointed at first.

Primary shareable entrypoints:
- `SensibLaw/sl_zelph_demo/run.sh`
- `SensibLaw/sl_zelph_demo/db_run.sh`
- `SensibLaw/sl_zelph_demo/wikidata_run.sh`
- `SensibLaw/tests/test_sl_zelph_demo_tools.py`
- this note

Primary code surfaces:
- `SensibLaw/sl_zelph_demo/compile_db.py`
- `SensibLaw/sl_zelph_demo/lex_to_zelph.py`
- `SensibLaw/scripts/zelph_runner.py`
- `SensibLaw/src/zelph_bridge.py`

Primary rule/demo packs:
- `SensibLaw/sl_zelph_demo/db_rules.zlp`
- `SensibLaw/sl_zelph_demo/wiki_lex_rules.zlp`
- `SensibLaw/sl_zelph_demo/ontology_rules.zlp`
- `SensibLaw/src/fact_intake/zelph_invariants.zlp`
- `SensibLaw/src/fact_intake/zelph_workbench_rules.zlp`

Primary caution surfaces:
- benchmark result JSONs under
  `SensibLaw/tests/fixtures/fact_semantic_bench/results/`
- any chat-derived or transcript-derived corpora
- any local analysis or export artifacts not explicitly reviewed for sharing

Clarification:
- this note names repo-facing technical contact surfaces only
- it does not record private personal contact details

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
- the demo identifies narrow downstream behavior over revision-history
- patterns (reversion detection, volatility-style edit signals) that feed a
- bounded review signal

Clarification:
- this is a deliberately small demo of downstream reasoning over structured
  lexical facts
- it should not be read as establishing a stable formal ontology role for wiki
  editors
- the externally relevant claim is the behavior-level one: Zelph can consume a
  compact exported fact slice and infer bounded review-relevant signals from it
  (the old wiki/revert lane is now a minor review signal example, not the
  headline story)

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

## Stefan-facing Zelph pack
- demo scripts/tests (e.g., `SensibLaw/sl_zelph_demo/run.sh`, `SensibLaw/tests/test_sl_zelph_demo_tools.py`) plus several sanitized graph-export examples now back the handoff story
- lead slice: deterministic DB/rule-atom export (`SensibLaw/sl_zelph_demo/compile_db.py`, `db_rules.zlp`, `db_run.sh`, `tests/test_sl_zelph_demo_tools.py`) proves Zelph-dev technical credibility and downstream reasoning value
- ingester-derived structured graph example: sanitized fact-semantic bench outputs under `SensibLaw/tests/fixtures/fact_semantic_bench/results/` (legal, chat, transcript slices) show how the reviewed, provenance-backed graph can be handed to Zelph without surfing the old wiki/revert story
- ontology/predicate-as-node example: `SensibLaw/sl_zelph_demo/ontology_demo.zph`, `ontology_rules.zlp`, `SensibLaw/sl_zelph_demo/lex_to_zelph.py` demonstrate richer predicate bridging in a sanitized surface
- optional review signal example: keep the wiki/review run drawn from `SensibLaw/sl_zelph_demo/wiki_demo_full.zph`, `wiki_lex_rules.zlp`, `wiki_inferred.txt`, framed as a historical/diagnostic case rather than the main positioning

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

## Open Collaboration Questions
- Which sanitized benchmark slice from `SensibLaw/tests/fixtures/fact_semantic_bench/results/` (legal, chat, transcript) should we prime as the ingester-derived structured graph example in the Zelph pack?
- Are there additional log/metadata artifacts from the DB/rule-atom export path (`SensibLaw/sl_zelph_demo/compile_db.py`, `db_rules.zlp`, `db_run.sh`) that Zelph devs will need to believe the deterministic handoff story?
- Should we keep the wiki lane as the optional bounded review signal example described above, or do we need a second review-focused slice before handing the pack externally?

## Suggested Questions / Next Discussion Points
- Which sanitized ontology/predicate-as-node exports under `SensibLaw/sl_zelph_demo/ontology_*` should be documented to showcase richer predicate bridging?
- Do we want to annotate the sanitized fact-semantic bench outputs that power the ingester-derived slice so recipients understand how to regenerate them?

## Intended Next Tests
- keep the outward-facing handoff note aligned with tests that already exist for:
  volatility signals, reversion detection, and reversion-without-context risk
- add one small bridge-level regression that verifies the handoff claims remain
  true for the current demo outputs
- prefer behavior assertions over role-label assertions in any future
  Stefan-facing Zelph pack

## One-sentence Summary
SensibLaw is trying to make text-derived facts stable, reviewable, and
provenance-preserving before handing a compact graph slice to Zelph for
downstream reasoning.
