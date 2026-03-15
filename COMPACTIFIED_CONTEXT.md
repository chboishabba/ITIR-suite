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
- 2026-03-15 whitepaper thread re-resolved after further posts:
  - title: `Insights from Whitepaper`
  - online UUID: `69b41f22-a514-839f-946c-fa0e9f75cc46`
  - canonical thread ID: `eab13fe32136bc69aebdb9a21888b76215faab11`
  - source used: `db`
  - archived message count at refresh: `122`
  - latest archived assistant timestamp: `2026-03-13T15:19:54+00:00`
  - Mary Technology / parity takeaway:
    - near-term product priority should be parity with Mary's practical
      fact-management / chronology / provenance / contestation workflow layer
    - current SL whitepaper priorities remain valid, but should be treated as
      layer-two legal-semantic followthrough over a Mary-equivalent fact
      substrate rather than the first user-facing milestone
    - ontology bridge / branch-set / external-ref work should be framed as
      support infrastructure for that parity target
    - typed transitions, burden policy, and p-adic retrieval remain strategic
      differentiators after the fact layer is credible
- 2026-03-15 Mary-parity fact-substrate interpretation update:
  - source: current working turn, aligned against
    `docs/planning/mary_parity_roadmap_20260315.md`
  - main decision:
    - the first Mary-parity fact substrate should not jump directly from
      `statement -> fact`
    - it should introduce a text-grounded `ObservationRecord` seam using a
      small stable predicate catalog for roughly 80-90% of factual statements
  - comparison with existing repo concepts:
    - existing `CaseObservation`, `ActionObservation`, `AlignmentObservation`,
      and `DecisionObservation` types are projection/aggregation shapes, not
      the canonical fact-intake observation lane
    - the new fact-intake observation layer should remain text-grounded and
      provenance-linked to statements/excerpts/sources
  - initial predicate families to scaffold:
    - actor identification
    - actions / events
    - object / target
    - temporal
    - harm / consequence
    - legal / procedural
  - design rule:
    - keep predicates few and stable, keep objects rich, and treat Wikidata as
      enrichment for objects rather than authority for predicate vocabulary
- 2026-03-15 event-candidate followthrough:
  - source: current working turn, aligned against the new fact-observation
    scaffold
  - main decision:
    - the next deterministic seam after observations is a derived
      `EventCandidate` layer
    - events should be reconstructable from observations and never become the
      primary source of truth
  - storage shape:
    - `event_candidates`
    - `event_attributes`
    - `event_evidence`
  - assembly stance:
    - rule-based and conservative
    - create events from event-trigger predicates plus actor/context anchors
    - merge only on stable explicit signatures
    - keep contestation observation-first, even when observations attach to the
      same event
- 2026-03-15 fact-substrate tightening pass:
  - reserve explicit distinction between:
    - structural/content-derived identity
    - run/execution metadata
  - make abstention explicit rather than inferring it from missing rows
  - keep event assembly language- and jurisdiction-neutral by consuming only
    normalized observation predicates; variation belongs in dictionaries,
    mappings, and parser-backed normalization packs instead
- 2026-03-15 Mary-parity role-pressure expansion:
  - expanded the new Mary-parity user stories in `docs/user_stories.md` for:
    - community legal centre intake
    - NGO litigation/campaign assembly
    - paralegal, solicitor, barrister, and judge/associate workflows
    - personal ITIR, investigative ITIR, trauma-survivor, and support-worker
      workflows
    - contested Wikipedia / Wikidata moderation and legality-assessment roles
    - adversarial public-figure and source-shopping / overstatement /
      sanitization pressures
    - family-law, child-sensitive, and cross-side handoff workflows
    - medical-negligence and professional-discipline overlap workflows
    - personal-to-professional handoff workflows
    - anti-AI-psychosis / false-coherence-resistance workflows
  - added the planning follow-ons:
    - `docs/planning/mary_parity_user_story_acceptance_matrix_20260315.md`
    - `docs/planning/mary_parity_gap_analysis_20260315.md`
  - story-informed near-term Mary-parity priority order:
    1. richer review queue reasons and contested/chronology triage
    2. source workflow run -> fact-review run reopen mapping
    3. widened legal/procedural observation visibility
- 2026-03-15 Mary-parity acceptance expansion status:
  - explicit passing gates now exist for:
    - `wave1_legal`
    - `wave2_balanced`
    - `wave3_trauma_advocacy`
    - `wave3_public_knowledge`
    - `wave4_family_law`
    - `wave4_medical_regulatory`
    - `wave5_handoff_false_coherence`
  - Wave 5 is no longer synthetic-only; it now includes repo-curated real
    transcript fixtures for professional handoff and contradiction-preserving
    false-coherence review
  - current Mary-parity limiting factor is no longer missing substrate
  - current limiting factors are:
    - real-fixture breadth in some newer waves
    - operator/workbench/export polish
  - planning baseline for the next loop:
    - `docs/planning/mary_parity_status_audit_20260315.md`
- 2026-03-15 Mary-parity Wave 1 legal gate:
  - added a canonical fixture manifest at
    `SensibLaw/data/fact_review/wave1_legal_fixture_manifest_v1.json`
  - added `SensibLaw/scripts/run_fact_review_acceptance_wave.py` to build the
    canonical transcript/AU + synthetic fixtures and emit a batch acceptance
    report for `wave1_legal`
  - tightened acceptance results with failed-check IDs and gap tags so the
    next implementation loop can be backlog-driven from real story failures
  - tightened the fact-review workbench with grouped issue filters,
    source-centric reopen links, approximate chronology visibility, and a
    clearer assertion/outcome/annotation distinction
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
- Ribbon ownership/context alignment:
  - archive thread resolved from local DB:
    - title: `Timeline Ribbon Overview`
    - online UUID: `69857c15-29ec-8398-ab2d-11f89180f79e`
    - canonical thread ID: `44e84563357cc580eb3f33faa72bf5658202364e`
    - source used: `db`
  - supporting historical concept thread also resolved from local DB:
    - title: `Feature timeline visualization`
    - online UUID: unknown / not stored
    - canonical thread ID: `f8170d36e0b2c28b2bb0366a7dc35a433e26ca00`
    - source used: `db`
  - current repo-facing decision:
    - `itir-ribbon/` remains the contract/spec source for ribbon invariants,
      lens DSL, and phase packs
    - `itir-svelte/` is the active UI/dev front where richer ribbon surfaces
      should live
    - when stream-oriented language appears in planning or pitches, treat it as
      the substrate feeding Ribbon rather than as a separate product surface
    - Ribbon remains general-purpose across conserved-allocation / timeline
      views; finance/social/legal streams are examples, not the boundary of the
      surface
    - existing `step-ribbon` wiki layout is a deterministic graph placement
      mode, not the full conserved-allocation ribbon surface
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
