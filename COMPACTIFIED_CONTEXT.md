# Compactified Context

- 2026-03-19 archived thread resolution pass:
  - resolved nine online UUIDs using `robust-context-fetch`
  - canonical source path: `~/chat_archive.sqlite`
  - write persistence for the newly supplied IDs was blocked during this pass by
    `sqlite3.OperationalError: database is locked`, so exact archive matches are
    marked `db` and the remaining titles/topics were captured via live read-only
    web fetches
  - summary:
    - `69b90f8b-3cf8-839c-bffe-b7da95565338`
      - title: `Zelph 0.9.5 Update`
      - canonical thread ID:
        `e45a889fa7d88547021c2a95ded89270b40fd6db`
      - source used: `db`
      - main topic: the full conversation moved from assessing Zelph as early
        stage-but-promising, to checking whether it overlaps with SL/ITIR, to
        defining a minimal negligence rule set and "irreducible disagreement,"
        and finally to a tiny deterministic SL -> Zelph bridge demo
      - demo takeaway: keep it tiny, deterministic, and legally meaningful
        enough to show a clean fact-graph handoff rather than a full
        integration
    - `69b9f131-bb3c-839c-b2cd-233b4af8c72a`
      - title: `Branch · Zelph 0.9.5 Update`
      - canonical thread ID:
        `e3d8bffb77f7df0337efe3684653c6bf441ca061`
      - source used: `db`
      - main topic: refine the Stefan-facing update so it sounds more precise,
        technically grounded, and clearly upstream rather than dependent on
        Zelph; Mary was explicitly treated as a competitor / external
        benchmark, not as evidence of the user’s own architecture
    - `69b75a97-6784-839b-bc2b-3824717279e0`
      - title: `ITIR SensibLaw Model`
      - canonical thread ID:
        `044540f8d6f0a880d507c1ce81341613b56d13b9`
      - source used: `db`
      - main topic: formalize ITIR/SL in a clean model, while treating uploaded
        content as partial snippets and forcing file-search / full-document
        lookup before answering from truncated excerpts
    - `69b7e167-53d8-839d-a9e6-56b239746525`
      - title: `Governance Model Mapping`
      - canonical thread ID:
        `49554563c68c31b87b5f28ff673355c0ff8b2a1b`
      - source used: `db`
      - main topic: map the printed O/R/C/S/L/P/G/F model onto the ITIR /
        SensibLaw governance machine and make the operator explicit for
        convergence, proofs, and ZK attestation reasoning
    - `69b7e164-d0a8-839d-8418-41769163ba6d`
      - title: `Formal Model Application`
      - canonical thread ID:
        `c1279d811ec67be9ebae1cab6c1ee865ca24299b`
      - source used: `db`
      - main topic: apply a state-compiler / prototype model to the problem
        using uploaded files, with the archive noting that the files were fully
        loaded and should be searched directly when needed
    - `69ba8956-35b8-839b-9707-f8c91c2b02dd`
      - title: `Ambiguity of "Community"`
      - online UUID only; canonical thread ID not persisted during this pass
      - source used: `web`
      - main topic: `"community"` in legal text is often a normative
        placeholder rather than a concrete entity, so SL should not expect
        Wikidata/entity linking to resolve it automatically
      - design takeaway: keep this lane text-grounded and support unresolved
        normative-reference handling instead of forcing entity resolution
    - `69bab27a-cb28-8398-b3ea-940d4fb47772`
      - title: `Branch · Ambiguity of "Community"`
      - online UUID only; canonical thread ID not persisted during this pass
      - source used: `web`
      - main topic: branch follow-up reinforcing the same ambiguity boundary
        and the need to preserve underdetermined legal placeholders
    - `69ba8c55-163c-839d-86b9-6c366a8dc29a`
      - title: `Formal Model to Engine`
      - online UUID only; canonical thread ID not persisted during this pass
      - source used: `web`
      - main topic: map the O/R/C/S/L/P/G/F-style formal model directly onto
        the ingest / lexer / compression engine so organization, demand, code,
        state, lattice, proposal, and gap remain explicit in that pipeline
    - `69b7eb5b-0c78-839d-9012-a484905fdf0c`
      - title: `Model Mapping to Casey`
      - online UUID only; canonical thread ID not persisted during this pass
      - source used: `web`
      - main topic: map the same formal model onto Casey with
        `TreeState + WorkspaceView` as state, the per-path candidate set as the
        lattice, collapse as explicit governance, and divergence as a first
        class measurable gap
    - `69b89b50-5554-839d-b9cf-f50f6eab3b8b`
      - title: `Debugging UX in Games`
      - online UUID only; canonical thread ID not persisted during this pass
      - source used: `web`
      - main topic: stream/debugging isolation discussion; recorded for
        completeness but not treated as a current repo-facing planning input
    - `69ba3af2-5df8-839b-bd8a-7c865be0b052`
      - title: `Casey Git Clone Differences`
      - online UUID only; canonical thread ID not persisted during this pass
      - source used: `web`
      - main topic: concise Casey differentiators: superposition instead of
        snapshots, conflicts as valid state, explicit collapse, workspace as
        selection over candidates, and immutable build projections
- 2026-03-19 ITIR surface-boundary followthrough:
  - source: current working turn
  - main decision:
    - `SL` owns representation/compression
    - `casey-git-clone` owns mutable possibility state and operational
      collapse/build authority
    - `fuzzymodo` owns read-only reasoning over exported Casey state
    - `StatiBaker` owns observer-only governance memory and alignment judgment
  - documentation artifacts added:
    - `docs/planning/casey_fuzzymodo_interface_contract_20260319.md`
    - `docs/planning/casey_statiBaker_receipt_schema_20260319.md`
  - immediate implementation priority:
    - implement Casey -> fuzzymodo as the next boundary
    - then implement the sharpened Casey -> StatiBaker receipt seam
- 2026-03-19 JMD/ERDFA intended-surface awareness:
  - resolved via `robust-context-fetch`
  - title: `Dependency-aware task scheduling`
  - online UUID: `69bb8ef6-e9d0-839c-a917-ae92116a02cd`
  - canonical thread ID: `2a13394ff8c932629d42aed76bb07f049eede036`
  - source used: `db` after pulling the online UUID into `~/chat_archive.sqlite`
  - main topic / decision:
    - treat JMD/ERDFA shard-graph scheduling as a future external surface only
    - draft mapping is JMD shard graph -> Casey runtime state -> fuzzymodo
      scoring -> StatiBaker receipts
    - do not promote it to an active Casey/fuzzymodo/SB contract yet
  - documentation artifact added:
    - `docs/planning/jmd_itir_intended_surface_20260319.md`

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
- 2026-03-19 Mary-parity next-step lock:
  - next SL-facing priority is operator-surface validation over the existing
    persisted fact-review contract, not more substrate expansion
  - the current Mary-parity pressure is:
    - `itir-svelte` `/graphs/fact-review` behavior against persisted
      `wave1_legal` runs
    - source-centric reopen behavior
    - canonical issue-filter switching
    - inspector classification rendering for `party_assertion`,
      `procedural_outcome`, and `later_annotation`
  - the fact-review route/server adapter has already been tightened to consume
    explicit workbench fields instead of ad hoc client derivation, so the next
    follow-through should prefer behavior-level UI validation and operator
    polish before another semantic-family expansion
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
    - host-wide pytest run and direct smoke run passed
  - DONE: additive fact-intake semantic normalization in `SensibLaw`
    - raw source/excerpt/statement/observation/fact/event tables remain the
      canonical observed layer
    - new sidecar semantic tables persist:
      - controlled classifications
      - inference results
      - cross-entity relations
      - policy outcomes
      - semantic refresh receipts
    - `persist_fact_intake_payload(...)` now dual-writes semantic
      materialization for new runs
    - `scripts/backfill_fact_semantics.py` rebuilds normalized semantics for
      existing runs without migration-time auto-backfill
    - review summary/workbench now prefer normalized semantic rows and only
      fall back to legacy derivation for non-materialized runs
    - lexical Zelph graphs remain derived/materialized, not OLTP-normalized
