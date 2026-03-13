# Compactified Context

- 2026-03-14 whitepaper context refresh:
  - resolved archived thread via `robust-context-fetch`
  - title: `Insights from Whitepaper`
  - online UUID: `69b41f22-a514-839f-946c-fa0e9f75cc46`
  - canonical thread ID: `eab13fe32136bc69aebdb9a21888b76215faab11`
  - source used: `db` (after pulling the online UUID into `~/chat_archive.sqlite`)
  - main topics / decisions pulled from the thread:
    - keep SL event-centric and observation-aware; do not flatten the core model
      into plain RDF triples
    - treat RDF/Wikidata compatibility as an adapter/export surface over SL's
      richer event / observation / provenance model
    - prioritize an explicit Observation layer that separates source statements
      from real-world events
    - prioritize case-construction primitives
      (`evidence -> fact -> norm -> claim`) ahead of broader ontology expansion
    - queue temporal law/versioning and jurisdiction as critical follow-on
      infrastructure after the observation/claim seam is explicit
    - avoid ontology explosion by preferring lean primitives plus typed
      relations/attributes over proliferating node classes
    - use p-adic / ultrametric structure as a candidate formalism for
      hierarchical case similarity and doctrinal clustering without defaulting
      to embedding-first search
    - treat legal reasoning as typed state transitions with guarded,
      provenance-auditable seams; "reversible" is a design direction for some
      transitions, not a blanket claim about all legal reasoning
    - prioritize Wikidata shapes that help with jurisdiction, court hierarchy,
      legislation/case relations, party/actor identity, temporal validity, and
      external-reference prepopulation rather than importing generic triples
- Completed slices:
  - workbench graph/review contract implementation in `itir-svelte`
  - P0 tokenizer/lexeme migration verification refresh with passing regression lane
  - P1 SL engine/profile followthrough v1 with concrete profile admissibility implementation and tests
  - NotebookLM metadata/review parity v1 started as a neutral read-model/source
    reuse slice rather than a fake activity-accounting upgrade
- New SL profile module:
  - `SensibLaw/src/text/profile_admissibility.py`
  - enforces profile allowlists and global span linting while preserving canonical tokens
- New tests:
  - `SensibLaw/tests/test_profile_admissibility.py` (passing)
- Documentation now aligned with implementation for:
  - `compression_engine.md`
  - `profile_contracts.md`
  - `profile_lint_rules.md`
  - `cross_profile_safety_tests.md`
- Progress on next priority sprint:
  - DONE: Tool Use Summary hydration fix for `Shell/hour` and `Input/hour` in
    SB reducer (`exec_command` + `request_user_input` hour bins).
  - DONE: regression coverage for these counters in
    `StatiBaker/tests/test_dashboard.py`.
  - DONE: NotebookLM notes-meta events now flow into tool-use stream as
    `notebooklm_meta_event` (family + hour bins).
- Additional hardening slice completed:
  - DONE: `A8` fail-closed CI stubs + waiver path for assumption controls
    (`docs/planning/assumption_controls_registry.json`).
  - DONE: `A1/Q1` axis hierarchy fixture coverage (collision detection +
    deterministic 2D fallback) in SensibLaw ribbon utilities/tests.
- NotebookLM current testing posture:
  - prefer a bounded live E2E smoke before broader network/generation runs
  - smoke should cover:
    - `auth check --test`
    - readonly notebook listing/get
    - one bounded chat ask
    - source listing on the same readonly notebook
  - first live attempt exposed an environment-only blocker:
    - repo `.venv` had valid NotebookLM auth storage
    - repo `.venv` was missing `pytest-asyncio` and `pytest-timeout`
    - async E2E fixtures therefore failed before the readonly smoke reached
      the API layer
  - resolved live-smoke path:
    - install the missing NotebookLM test deps into the repo-root `.venv`
    - keep using the repo-root `.venv` for live NotebookLM smoke runs
    - nested `notebooklm-py/.venv` was removed
    - live `auth check --test` succeeded
    - live bounded readonly smoke succeeded against notebook
      `2c63ab1a-08b9-4b6a-99e6-93469cc83c7f` (`SENSIBLAW`):
      - list notebooks
      - get notebook
      - one bounded chat ask
      - list sources
  - smoke runner should trust its explicit safe node list rather than the
    broader `readonly` pytest marker, because current marker coverage is
    incomplete for some live-read tests
  - treat token refresh and network permission as explicit prerequisites rather
    than assuming live NotebookLM access is always available
  - current NotebookLM suite posture:
    - enough for lifecycle/review/source reuse
    - not yet honest enough for waterfall/timeline activity parity
  - first standardization slice should add:
    - producer-owned NotebookLM observer report/query helpers
    - source-unit projection from source summaries/snippets
    - no reinterpretation of `notes_meta` as sessionized activity
  - DONE: separate additive NotebookLM interaction capture over conversation
    history + notes
    - raw families: `conversation_observed`, `note_observed`
    - normalized signal stays separate (`notebooklm_activity`)
    - query/read-model helpers and `TextUnit` preview projection now exist
    - still no dashboard session/waterfall claims from this lane alone
  - DONE: `A2/Q2` SB fold neutrality hardening via explicit fold-policy receipt,
    machine `mechanical_should_flags`, explicit fold `loss_profile`, and
    anti-nudge red-team tests.
  - DONE: `A3` causal claim-link provenance gates in
    `SensibLaw/src/reporting/narrative_compare.py`:
    - `supports`/`undermines` now emit required
      `link_type`, `confidence`, `counter_hypothesis_ref`
    - public artifact validator fails closed on missing causal provenance
    - regression coverage added in
      `SensibLaw/tests/test_narrative_compare.py`
    - host-wide pytest run for that file is currently blocked by missing
      `pdfminer` from shared `tests/conftest.py`; direct smoke run passed
