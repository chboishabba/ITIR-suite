# TODO (ITIR-suite)

## Last assessed
- 2026-03-18

## Submodule TODO snapshot
- SensibLaw: S6 in progress with S6.5 external consumer contracts stubbed; near-term focus on schema freezes, sprint selection, Sprint 9 UI hardening, ingestion discipline tasks, and bounded citation-follow expansion; Sprint S7 checklist targets API/CLI projections, golden tests, and red-flag guards.
- SL-reasoner: no TODOs found.
- tircorder-JOBBIE: accessibility TODOs (extend ARIA roles/labels, add `aria-live`, automate audits, expand manual testing).
- WhisperX-WebUI: README TODO list appears complete; translation PRs requested.
- reverse-engineered-chatgpt: README TODOs remaining (better error handling, improve documentation); TODO.md items all completed.
- chat-export-structurer: no TODOs found.
- StatiBaker: pending work across intent/scope, temporal reduction rules (carryover/new/resolved), atom/handle definitions, integration adapters for TIRC/SL/ITIR refs, and guard tests that prevent content summarization.
- notebooklm-py:
  - keep a bounded live E2E smoke path healthy (`auth check --test` + readonly
    notebook/query smoke) before attempting broader network/generation runs
  - ensure the local test environment actually carries NotebookLM dev test deps
    (`pytest-asyncio`, `pytest-timeout`) in the repo-root `.venv` before
    treating E2E failures as API/auth issues
- NotebookLM suite standardization:
  - DONE: bounded live smoke in the repo-root `.venv`
  - DONE: first metadata/review parity slice via producer-owned observer
    read-model/query helpers and source-summary text-unit projection
  - DONE: define and implement the bounded NotebookLM interaction lane
    (`conversation_observed`, `note_observed`, separate normalized signal,
    query/read-model helpers, no dashboard session claims)
  - next: decide whether a later interaction-grade capture/session contract
    should be sourced from richer NotebookLM events or remain review-only
  - later: define a separate interaction-grade NotebookLM activity contract
    before treating NotebookLM as a first-class SB usage lane
- Chatistics: no TODOs found.
- pyThunderbird: no TODOs found.

## Active TODOs
## Priority legend
- [P0] Blocking / core platform correctness
- [P1] Near-term platform capability unlocks
- [P2] Important but deferrable
- [P3] Nice-to-have / polish

- [P1] Shared SL reducer adoption across products:
  - use `sensiblaw.interfaces.shared_reducer` as the supported cross-product
    lexer/reducer API
  - migrate first real runtime consumer paths in SB, TiRC, and ITIR-facing UI
    from doc-only boundary assumptions to adapter-backed canonical refs
  - keep any local tokenizer/indexing heuristics explicitly non-canonical
  - add cross-product guard tests so no product imports SL tokenizer internals
    directly for runtime integration
  - make adapter-produced tokenizer profile / canonical refs visible in
    receipts, overlays, or read models where cross-product preservation matters
- [P2] SensibLaw x Glasslane / Mirror packaging slice:
  - use chat thread `Aptos cryptocurrency overview`
    (`691ac8a3-4a30-8320-bd5f-f66efc3145e7`,
    canonical `dff5b29b89818300e7e352c0247c4cef3823bcfd`) as the current
    product-positioning source
  - package SensibLaw/TiRC for Mirror as the missing `human risk layer` rather
    than as a competing crypto research assistant
  - draft product-facing materials for:
    - `Crypto Consumer Harm Observatory (CCHO)`
    - `Risk & Behavioural Pattern Analytics` for exchanges/wallets
    - `High-Trust Explainability Layer` for boards/regulators
  - define the minimum reusable Ribbon stream-layer surface for this pitch:
    - Ribbon remains the named operator-facing surface / embed target
    - stream types for finance, conversation, obligation, and other
      timeline-aligned conserved/derived signals feed Ribbon
    - change-point / pattern-event outputs
    - provenance-safe API/export surfaces for partner embedding
  - keep crypto/regtech positioning focused on provenance, guardrails, and
    explainable pattern detection instead of generic market commentary
- [P1] Mary-parity fact-management roadmap (new top SL-facing priority):
  - use `docs/planning/mary_parity_roadmap_20260315.md` as the planning source
    for near-term SL execution
  - archived context inputs resolved on 2026-03-18:
    - `69b90f8b-3cf8-839c-bffe-b7da95565338` / `Zelph 0.9.5 Update`
      -> tiny deterministic SL -> Zelph bridge demo
    - `69b9f131-bb3c-839c-b2cd-233b4af8c72a` / `Branch · Zelph 0.9.5 Update`
      -> Stefan-facing upstream-positioning refinement
    - `69b75a97-6784-839b-bc2b-3824717279e0` / `ITIR SensibLaw Model`
      -> formalization plus file-search fallback for partial snippets
    - `69b7e167-53d8-839d-a9e6-56b239746525` / `Governance Model Mapping`
      -> explicit operator mapping for convergence/proof/ZK reasoning
    - `69b7e164-d0a8-839d-8418-41769163ba6d` / `Formal Model Application`
      -> state-compiler / prototype application over uploaded files
    - `69ba8956-35b8-839b-9707-f8c91c2b02dd` /
      `Ambiguity of "Community"`
      -> treat legal placeholders like `community` as unresolved
         normative-reference surfaces, not assumed KB entities
    - `69ba8c55-163c-839d-86b9-6c366a8dc29a` /
      `Formal Model to Engine`
      -> keep ingest/lexer/compression state/lattice/gap roles explicit
    - `69b7eb5b-0c78-839d-9012-a484905fdf0c` / `Model Mapping to Casey`
      -> keep Casey state/lattice/governance boundaries explicit
    - `69ba3af2-5df8-839b-bd8a-7c865be0b052` /
      `Casey Git Clone Differences`
      -> emphasize candidate lattice, explicit collapse, workspace selection,
         and immutable build projections in Casey-facing docs/adapters
  - treat Mary Technology as the benchmark for:
    - fact management
    - chronology / timeline handling
    - provenance and contestation of statements
    - litigation-workflow operator surfaces
  - position current ontology/bridge/branch-set work as support infrastructure
    for that parity target rather than as a standalone ontology milestone
  - define the minimum parity deliverable as:
    - source/excerpt/statement capture
    - a small explicit observation layer with a stable low-cardinality
      predicate catalog for the first factual substrate
    - chronology over captured facts/statements
    - contestable fact/claim handling
    - operator review / curation surfaces
    - external-reference/linkage support for the fact layer
  - immediate scaffold followthrough:
    - add canonical `ObservationRecord` storage/reporting between statements and
      facts
    - add deterministic `EventCandidate` assembly over observations with
      evidence/attribute tables
    - formalize structural IDs vs run IDs so execution context never rewrites
      content identity
    - make abstention explicit in fact/observation/event status handling rather
      than relying on row absence
    - keep the first predicate catalog small and stable rather than trying to
      encode the whole law at intake time
    - compare/align this lane against existing projection-style observation
      types (`CaseObservation`, `ActionObservation`, `DecisionObservation`)
    - keep events derived and reconstructable from observation evidence rather
      than treating them as a new canonical truth layer
    - keep language/jurisdiction variation in normalization packs and concept
      mappings rather than branching assembler logic
  - user-story-informed next slice:
    - expand Mary-parity operator pressure against
      `docs/user_stories.md`
    - use
      `docs/planning/mary_parity_user_story_acceptance_matrix_20260315.md`
      as the acceptance matrix for transcript/AU fact-review work
    - use
      `docs/planning/mary_parity_gap_analysis_20260315.md`
      to prioritize:
      1. richer review queue reasons and contested/chronology triage
      2. source workflow run -> fact-review run reopen mapping
      3. widened legal/procedural observation visibility
  - DONE in current loop:
    - add role-meaningful review queue reasons
      (`missing_date`, `missing_actor`, `contradictory_chronology`,
      `statement_only_fact`, `procedural_significance`, `source_conflict`)
    - add source-label-centric listing and latest reopen/query support for
      persisted fact-review runs
    - add bounded operator views (`intake_triage`, `chronology_prep`,
      `procedural_posture`, `contested_items`)
    - add story-driven acceptance reports over persisted runs
    - add a thin read-only fact-review workbench in `itir-svelte`
      (`/graphs/fact-review`) over the same persisted contract
  - next parity pressure:
    - DONE: add a canonical Wave 1 legal fixture manifest plus batch acceptance
      runner over transcript/AU persisted runs
    - DONE: tighten workbench/operator surfaces with grouped issue filters,
      source-centric reopen navigation, and dated/approximate/undated
      chronology separation
    - tighten role-specific pass/partial/fail gaps exposed by the new Wave 1
      batch report before moving to claim/theory layers
    - explicitly add fixture families for:
      - contested Wikipedia/Wikidata/public-figure moderation
      - lawyer/public-knowledge legality assessment (including GWB and Trump
        style lanes, with proven-illegal, legally dubious, and clearly
        authorized comparisons where possible)
      - family-law / child-sensitive / cross-side handoff
      - medical-negligence / professional-discipline overlap
      - personal-to-professional handoff and anti-AI-psychosis resistance
    - DONE: green the explicit acceptance-wave program through:
      - `wave1_legal`
      - `wave2_balanced`
      - `wave3_trauma_advocacy`
      - `wave3_public_knowledge`
      - `wave4_family_law`
      - `wave4_medical_regulatory`
      - `wave5_handoff_false_coherence`
    - next parity audit priority:
      - broaden real-fixture depth for waves that remain synthetic-heavy,
        especially:
        - `wave3_public_knowledge`
        - `wave4_family_law`
        - `wave4_medical_regulatory`
      - run an operator/workbench/export polish audit over the green waves
        before adding another major semantic family
  - after parity substrate is credible, fold back into:
    - explicit Observation / Claim contracts
    - deterministic `source/excerpt -> observation -> event/fact -> norm -> claim`
    - typed guarded state transitions
    - p-adic / ultrametric retrieval experiments
  - Dependencies:
    - archived thread `Insights from Whitepaper`
      (`69b41f22-a514-839f-946c-fa0e9f75cc46`)
    - `docs/planning/sl_whitepaper_followthrough_20260314.md`
    - current ontology bridge / external-ref / branch-set work in `SensibLaw`
- [P2] Wikidata ontology integration working (end-to-end):
  - align with `SensibLaw/docs/wikidata_queries.md` and `SensibLaw/docs/ONTOLOGY_EXTERNAL_REFS.md`
  - implement the deterministic projection/instability model in `docs/planning/time_series_transformations.md`
  - confirm ontology DB upsert flow + provenance contract for Wikidata refs
  - Dependencies:
    - operator spec: `SensibLaw/docs/wikidata_epistemic_projection_operator_spec_v0_1.md`
    - transition plan + slice decision: `SensibLaw/docs/planning/wikidata_transition_plan_20260306.md`
    - reproducible input slice (two dumps or two edit windows)
- [P1] SL observation + case-construction followthrough:
  - note: now explicitly phase-two after Mary-parity fact-layer work, not the
    first user-facing SL milestone
  - the 2026-03-18 archive pass sharpened the implementation boundary:
    - keep uploaded-file handling explicitly partial and file-search backed
    - keep the governance/proof operator explicit rather than implicit
    - frame the bridge work as a compact demo or state-compiler prototype,
      not a full Zelph integration
  - use `docs/planning/sl_whitepaper_followthrough_20260314.md` as the
    planning source for the next SL-facing architecture/spec pass
  - ratify explicit `Observation` and `Claim` contracts before adding more
    doctrinal node types
  - define the deterministic seam for
    `source/excerpt -> observation -> event/fact -> norm -> claim`
  - define RDF/Wikidata projection/export as an interoperability boundary, not
    the core SL authority model
  - queue legal versioning and jurisdiction as the next infrastructure slice
    after the observation seam is explicit
  - add a bounded typed-transition receipt design for
    `state + observation + norm -> updated state`
  - keep unresolved normative placeholders (for example `community`) as
    text-grounded observation/norm-reference surfaces until explicit legal
    context resolves them; do not force Wikidata/entity identity too early
  - define a narrow Wikidata prepopulation target
    (jurisdictions, courts, legislation, cases/citations, actor identity,
    temporal validity relations) instead of generic triple sync
  - decide whether to prototype p-adic / ultrametric case similarity as an
    explanation-first retrieval lane before any embedding-first default
  - Dependencies:
    - archived thread `Insights from Whitepaper`
      (`69b41f22-a514-839f-946c-fa0e9f75cc46`)
    - `docs/user_stories.md` claim-discipline requirements
    - current Wikidata planning docs and ontology external-ref contracts
- [P3] GWB seed pipeline completion (Wikipedia -> seed envelope -> ontology refs):
  - see `docs/planning/wiki_ingest_fact_tree_gwb_20260210.md` and `docs/planning/wiki_ingest_run_notes_20260210.md`
  - Dependencies:
    - revision-locked snapshots via pywikibot/MediaWiki (`SensibLaw/.cache_local/wiki_snapshots*`)
    - candidate extraction artifacts (`SensibLaw/scripts/wiki_candidates_extract.py`, `SensibLaw/.cache_local/wiki_candidates_gwb.json`)
    - ontology external-refs upsert path (`python -m cli ontology external-refs-upsert`)
    - optional: Graphviz `dot` for SVG rendering
- [P3] AAO timeline graph surface stabilization:
  - ensure `itir-svelte` AAO routes stay aligned with `docs/planning/wiki_timeline_extraction_gwb_20260211.md`
  - Dependencies:
    - base timeline artifact `SensibLaw/.cache_local/wiki_timeline_gwb.json`
    - AAO extractor `SensibLaw/scripts/wiki_timeline_aoo_extract.py`
    - extraction profile `SensibLaw/policies/wiki_timeline_aoo_profile_v1.json`
    - run with project venv for spaCy parser lane (see `docs/planning/wiki_timeline_extraction_gwb_20260211.md`)
    - admissibility gate: `docs/planning/oac_object_admissibility_contract_v1_20260211.md`
- [P2] Wikipedia revision harness followthrough:
  - DONE: define the first monitor pack and dedicated runner/state-store contract
  - DONE: define a second curated high-contestation monitor pack to complement
    the ontology-stress pack
  - DONE: land rolling current-vs-last-seen runner over live Wikipedia article packs
  - DONE: document the history-aware runner contract and suite interface
    posture for SB / SL-reasoner / fuzzymodo / casey-git-clone
  - DONE: implement bounded revision-history polling and candidate-pair
    scoring over recent article history windows
  - DONE: add section-aware diff targeting and pair-level report wrappers over
    the existing revision harness
  - DONE: attach bounded review-context joins from existing Wikidata
    diagnostics and bridge aliases to revision issue packets
  - DONE: add pack-level triage summaries and direct-consumer article severity
    surfaces
  - DONE: add contested-region graph artifacts/read models plus a dedicated
    `itir-svelte` page over the contested pack
  - DONE: expand the contested pack into `wiki_revision_contested_v2` with
    deeper bounded history defaults and graphing enabled
  - run repeated live passes over both curated packs so the lane accumulates
    real `changed` reports rather than mostly baseline/unchanged runs
  - compare volatility classes across packs (ontology-stress vs contested-live)
    before deciding what belongs in a default monitor set
  - decide whether `wiki_revision_contested_v2` should replace
    `wiki_revision_contested_v1` as the canonical contested live pack in docs
    and runbooks, or whether v1 should remain a smaller/lightweight sibling
  - add a bounded query/report contract for mining candidate contested titles
    without turning the lane into an open crawler
  - decide whether triage dashboards should later emit clearly-advisory edit
    suggestions or move directly to a workbench
  - Dependencies:
    - `SensibLaw/docs/wiki_revision_harness_contract_v0_1.md`
    - `SensibLaw/docs/wiki_revision_pack_runner_contract_v0_1.md`
    - `SensibLaw/docs/wiki_revision_pack_runner_contract_v0_2.md`
    - `SensibLaw/docs/planning/wiki_revision_harness_first_pass_20260309.md`
    - `SensibLaw/docs/planning/wiki_revision_contested_pack_20260309.md`
    - `SensibLaw/docs/planning/wiki_revision_history_runner_20260309.md`
    - `SensibLaw/docs/planning/wiki_revision_contested_region_graph_20260309.md`
    - `SensibLaw/scripts/wiki_revision_harness.py`
    - `SensibLaw/data/source_packs/wiki_revision_monitor_v1.json`
    - `SensibLaw/data/source_packs/wiki_revision_contested_v1.json`
    - `SensibLaw/data/source_packs/wiki_revision_contested_v2.json`
- [P1] Recent `itir-svelte` page audit followthrough:
  - DONE: add repeatable localhost audit runner `scripts/check_recent_pages.py`
  - DONE: record first audit findings in `docs/planning/recent_page_audit_20260309.md`
  - DONE: fix `/arguments/thread/69ac40e0-0cfc-839b-b2a8-0de3019379a9` returning HTTP `500`
  - DONE: fix the contested wiki graph lane so a graph-enabled `wiki_revision_contested_v2` run can hydrate `selected_graph` from DB or artifact-backed payloads rather than returning `null`
  - DONE: distinguish `producer run error` vs `changed run with missing graph payload` vs `valid populated graph` in `/graphs/wiki-revision-contested`
  - DONE: refresh contested wiki route default pack to graph-enabled `wiki_revision_contested_v2`
  - DONE: add explicit review-state + selection-bridge wiring for `/arguments/thread/[threadId]`, `/graphs/narrative-compare`, and `/graphs/wiki-revision-contested` with regression guards (including no `localStorage` / JSON UI-state persistence)
  - DONE: align UX/interaction work on `/arguments/thread/[threadId]`,
    `/graphs/narrative-compare`, and `/graphs/wiki-revision-contested` against
    `docs/planning/recent_workbench_page_user_stories_20260310.md`
  - keep `python scripts/check_recent_pages.py` in the manual verification loop whenever recent `itir-svelte` routes or upstream producer contracts change

- Come back to the Duncan/Emma response draft:
  - `docs/planning/response_to_duncan_emma_itir_hospital_advocacy_20260208.md` missed the intended mark (needs a better synthesis/voice and should be evaluated against the actual posting context).
- Tool Use Summary view follow-up:
  - DONE: Shell/hour and Input/hour now hydrate from tool-message bins (chat-archive `exec_command` + `request_user_input`) in the SB reducer layer.
  - DONE: Shell/hour and Input/hour share the same upstream time-binning path (SB reducer `frequency_by_hour`), with explicit regression coverage.
  - DONE: NotebookLM notes-meta interactions are now folded into the tool-use stream (`notebooklm_meta_event` family + hour bins) so tool-use counters and views hydrate from a shared reducer path.
- Grafana integration (do not reimplement Grafana):
  - ratify metrics/logs/traces scope and label/cardinality policy:
    `docs/planning/grafana_integration_metrics_scope_20260208.md`
  - implement Prometheus `/metrics` endpoints for orchestrator + key adapters
  - decide collector path (Prometheus vs Grafana Agent vs OTEL Collector) and hosting
  - add Grafana Alerting webhook ingest as an observer lane (link-first)
  - add a thin sitrep that reports alert state + links to Grafana, not charts
- SensibLaw Ontology DB migration hygiene:
  - DONE: Make SQLite ontology migrations idempotent by tracking applied migrations (do not re-run `001_normative_schema.sql` after `002_normalize_countries.sql` drops transitional columns).
  - DONE: Add guardrails so we don’t accidentally point ontology migrations at VersionedStore ingest DBs (different schema families).
  - DONE: Unblock DBpedia external ref upserts by making `ensure_database()` safe on repeated CLI calls.
  - DONE: DBpedia curation UX: emit a curated batch skeleton from Lookup API results (compatible with `ontology external-refs-upsert`) so we don’t copy/paste candidate URIs by hand.
- Execute assumption stress controls from
  `docs/planning/assumption_stress_test_20260208.md`:
  - DONE: add axis hierarchy policy fixtures and collision tests (`A1` / `Q1`)
  - DONE: implement SB fold-policy receipt + anti-nudge red-team tests (`A2` / `Q2`)
  - DONE: add claim-link provenance quality gates for receipts-backed artifacts (`A3`)
  - add plural-law non-reduction preservation fixtures (`A4` / `Q7`)
  - define encrypted-local performance budget benchmarks and degradation
    contracts (`A5`)
  - define contradiction action-branch protocol tests with uncertainty labels
    and no forced collapse (`A6`)
  - add deterministic lexical-noise guard fixtures:
    stopwords/number-heavy spans, cross-page artifacts, citation boilerplate
    flooding (`A7`)
  - DONE: add fail-closed CI stub tests for unresolved AIDs/Qx controls, with explicit
    waiver receipt path (`A8`)
  - add summary-lineage guards that block summary-of-summary canonical paths
    unless expanded to raw IDs first (`A9`)
  - define and enforce machine-readable `loss_profile` schema across fold/sitrep/
    receipts surfaces (`A10`)
- Run refactor execution from
  `docs/planning/refactor-master-coordination.md`:
  - keep `Q2`/`Q6`/`Q11` states updated (`OPEN` -> `RATIFIED` -> `IMPLEMENTED`
    -> `VERIFIED`)
  - enforce merge policy checks for all boundary-affecting PRs
  - update sprint gate checklist daily during Sprint 10 execution window
- Execute UI surface linking/integration followthrough from:
  - `docs/planning/ui_surface_registry_20260208.md`
  - `docs/planning/ui_integration_strategy_20260208.md`
  - `docs/planning/ui_surface_manifest.json`
  - add a minimal launcher page that reads the manifest and links native
    interfaces (include WhisperX Gradio + SB dashboard + SL Streamlit)
  - ratify `Q12` in
    `docs/planning/refactor-master-coordination.md` before any federated shell
    implementation
  - add a drift check ensuring registry docs and manifest entries stay aligned
    (no stale ports/commands)
- Add observer stubs + dashboards for:
  - iNaturalist biodiversity (insect trend phase: `upward_knee|peak|declining`)
  - mood self-report (explicit, non-inferential)
  - pet wearables / smart collars (smart-home telemetry, meta-only)
  - health data exports (meta-only by default):
    - FHIR export connector (Bundle/NDJSON) -> story events
    - scans folder connector (DICOM/exported images/PDFs) -> story events
    - doctor notes folder connector (txt/md/pdf refs) -> story events
    - OCR followthrough (handwritten/scanned docs):
      - local OCR pipeline (offline) for PDFs/images, emitting non-authoritative text artifacts linked by hash
      - optional frontier OCR path (explicit opt-in, redaction/cropping guidance, full provenance logging)
- CAM (Crisis-Advocacy Module) followthrough:
  - freeze an escalation envelope schema (machine-checkable): done (`docs/planning/schemas/escalation_envelope.schema.json`)
  - add envelope validation + red-team tests (no misrepresentation, no financial/legal binding, stop-on-success)
  - define CAM audit log artifact contract (after-action record)
- Prospective Sprint 10 (refactor thin slice) from
  `docs/planning/itir_prospective_sprint_10_refactor_20260208.md`:
  - ratify blocking decisions `Q2`, `Q6`, and `Q11` as ADRs before adapter
    freeze
  - freeze `itir.exchange.v1` with required replay/provenance fields including
    reducer version metadata
  - implement shared canonical reducer integration surface for TiRCorder/SB
    clients (Option C posture)
  - wire thin-slice adapters:
    TiRCorder->canonical IDs, SB->canonical ID refs, SB->Ribbon read-only map
  - add sprint gate tests:
    replay no-op/conflict, cross-path identity parity, projection safety, and
    expansion-invariant smoke
- Current execution pass scope (2026-02-07):
  - Convert live + archived Casey/Muratori conversation steps into explicit
    implementation artifacts for `fuzzymodo/` and `casey-git-clone/`.
  - Implement the mapped steps in code with project-local tests. (Done)
- Term sweep follow-ups from
  `__CONTEXT/last_sync/20260207T043655Z_term_sweep_sl_sensiblaw_itir_suite.md`:
  - Add a repeatable term-sweep runbook doc under `docs/planning/` covering
    scope, whole-word matching rules, and output artifact contract.
  - Add/refresh high-signal thread mappings in `__CONTEXT/convo_ids.md` for the
    top titled `SL`/`sensiblaw`/`itir`/`suite` conversations.
- Add a triage rule for overloaded term `suite` (flag likely false positives
  before context ratification).
- Execute chat artifact capture followthrough from
  `docs/planning/chat_artifact_capture_contract_20260208.md`:
  - add deterministic extractor for assistant-generated artifact classes
    (`download_link_artifact`, `inline_file_artifact`,
    `execution_claim_artifact`)
  - emit canonical artifact JSONL records with idempotency/provenance fields
  - add fixture tests for `sandbox:/mnt/data/*`, file-emission text patterns,
    and execution-claim co-occurrence
  - add replay and conflict tests (`same key+same hash` no-op; `same key+different hash` conflict)
- Execute followthrough plan from
  `docs/planning/sb_casey_jesuscrust_followthrough_20260207.md`:
  - implement SB observer/loss schema and refusal-path tests (`1.1`-`1.3`)
  - implement casey operation-contract tests (`2.1`-`2.5`)
  - formalize JesusCrust execution-boundary integration notes and ADR text
    (`3.1`-`3.5`)
- [P0] Execute tokenizer migration plan (regex → deterministic) with parity checks: DONE
  - `docs/planning/tokenizer_migration_plan_20260306.md`
  - GWB route payload parity:
    - `/graphs/wiki-timeline`
    - `/graphs/wiki-timeline-aoo`
    - `/graphs/wiki-timeline-aoo-all`
  - Existing SL ingest regression corpus:
    - `Mabo [No 2]`
    - `House v The King`
    - `Plaintiff S157`
    - `Native Title (NSW) Act 1994`
  - StatiBaker reducer and UI invariants:
    - shared canonical ID stability (same source text via SL/SB paths => same IDs)
    - no SB re-tokenization
    - compress -> expand invariant
    - no summary injection / no re-segmentation
    - context-bound rendering invariants
    - tool-use / chat-context metric stability
- [P1] Execute SL engine/profile followthrough from: DONE (v1 contract + tests)
  `docs/planning/sl_lce_profile_followthrough_20260208.md`:
  - draft domain-neutral engine spec (`docs/planning/compression_engine.md`)
  - define profile contracts (`docs/planning/profile_contracts.md`) for
    `sl_profile`, `sb_profile`, and `infra_profile` boundaries
  - define profile lint rules (`docs/planning/profile_lint_rules.md`) for
    forbidden axes/groups per profile
  - define cross-profile safety tests
    (`docs/planning/cross_profile_safety_tests.md`) that keep compression
    mechanics fixed while admissibility varies
  - Dependencies:
    - SL tokenizer contract: `SensibLaw/docs/tokenizer_contract.md`
    - lexeme layer baseline (see `[P0]` below)
    - decision: canonical token stream (lexeme-derived vs dedicated tokenizer)
    - deterministic multilingual tokenizer replacing regex (Layer‑1 only)
    - migration plan: `docs/planning/tokenizer_migration_plan_20260306.md`
- Apply refreshed SB boundary guidance from
  `docs/planning/sb_casey_jesuscrust_followthrough_20260207.md`:
  - codify "post-mortem forensic analyzers are observers, not memory
    authorities" in SB interop docs/contracts
  - add acceptance checks ensuring forensic imports cannot mutate canonical
    memory without explicit promotion receipts
- Apply Moltbook feedback intake from
  `docs/planning/moltbook_feedback_alignment_20260208.md`
  (`u/DexterAI`, `u/FiverrClawOfficial`, `u/TipJarBot`):
  - add idempotency and correlation IDs as first-class SB provenance fields
    in event/interface contracts
  - define explicit reversible SB transition contract and belief-time snapshot
    query semantics ("what did we believe at time T?")
  - add replay tests for duplicate retries and partial-write recovery
  - define external-settlement ownership signals (e.g., Base) as observer
    evidence by default, with explicit promotion receipts required for

- Audit-safe capability posture maintenance:
  - keep `docs/planning/itir_capability_posture_20260208.md` updated when new
    “courtroom-grade”/receipts/trauma-context language is added elsewhere
  - add a lint/checklist step to block docs that claim `TARGET` capabilities as
    `CURRENT` without an explicit label or implementation reference
    canonical-state impact
- Implement Fuzzymodo selector DSL parser over
  `docs/planning/fuzzymodo/selector_dsl.schema.json`.
- Implement canonical serialization + hash generation aligned with
  `docs/planning/fuzzymodo/canonical_hashing.md`.
- Add fixture-driven tests for selector and norm-constraint examples in
  `docs/planning/fuzzymodo/fixtures/`.
- Implement Fuzzymodo exchange channels defined in
  `fuzzymodo/docs/interfaces.md`: selector ingress, norm ingress, facts feed,
  decision egress, and replay artifact emission.
- Implement the DB-backed `fuzzymodo -> StatiBaker` seam from
  `docs/planning/fuzzymodo_statiBaker_interface_20260309.md`:
  - SB-owned overlay extension tables for `fuzzymodo_selector_v1`
  - separate decision-ledger persistence with SB reference-only joins
  - end-to-end adapter tests proving no selector/norm authority transfer
- DONE: Casey exchange channels defined in
  `casey-git-clone/docs/interfaces.md` now exist in the local testbed:
  publish ingress, sync command, collapse command, build snapshot egress,
  `casey.facts.v1` export, and `fuzzymodo.casey.advisory.v1` handling.
- DONE: Casey -> fuzzymodo contract from
  `docs/planning/casey_fuzzymodo_interface_contract_20260319.md` is now
  implemented in the local testbed with end-to-end tests over the minimal
  alice/bob flow.
- DONE: Casey -> StatiBaker observer seam from
  `docs/planning/casey_git_clone_statiBaker_interface_20260309.md` and
  `docs/planning/casey_statiBaker_receipt_schema_20260319.md` is now
  end-to-end in the Casey CLI/runtime lane:
  - Casey `publish` / `sync` / `collapse` / `build` emit receipts
    automatically
  - Casey operation/build ledgers persist locally by default
  - Casey observer bundles are emitted for replay/debug
  - `casey_workspace_v1` overlays can be ingested directly into SB dashboard DBs
  - tests cover Casey-ledger lookup and SB overlay ingestion
- Next Casey lane:
  - expose the same receipt/observer controls through any future non-CLI Casey
    entrypoints so the seam does not remain CLI-only
  - add broader cross-component interface-conformance checks so Casey/fuzzymodo/SB
    payload fields stay locked across future changes
- Keep the JMD/ERDFA shard-graph integration surface documented as future
  awareness only per `docs/planning/jmd_itir_intended_surface_20260319.md`:
  - do not treat it as an active Casey/fuzzymodo/SB contract yet
  - wait for a pinned shard schema / concrete adapter target before code work
- Implement cross-project channel adapters and validators per
  `docs/planning/project_interfaces.md` for:
  `SensibLaw/`, `SL-reasoner/`, `tircorder-JOBBIE/`, `StatiBaker/`,
  `WhisperX-WebUI/`, `reverse-engineered-chatgpt/`,
  `chat-export-structurer/`, `notebooklm-py/`, `Chatistics/`,
  `pyThunderbird/`, `SimulStreaming/`, `whisper_streaming/`, and
  `itir-ribbon/`.
- Implement ITIR orchestrator control-plane checks from
  `docs/planning/itir_orchestrator.md`:
  context/planning ingress, contract routing validation, execution sync hooks,
  and artifact egress bookkeeping.
- Add an orchestrator manifest mapping producer->consumer exchange channels
  across all component `docs/interfaces.md` contracts.
- Add interface-contract conformance tests that verify required ingress/egress
  payload fields and provenance metadata across component boundaries.
- Execute four-way intersection followthrough from
  `docs/planning/sl_tircorder_ribbon_sb_intersection_20260208.md`:
  - define shared exchange envelope schema (`itir.exchange.v1`) with
    `idempotency_key`, `correlation_id`, `causation_id`, and `payload_hash`
  - add adapter contract stubs for edge handoffs:
    TiRCorder->SL, SL->SB, SL->itir-ribbon, TiRCorder->SB, SB->itir-ribbon
  - add cross-component replay/conflict tests:
    same key+same hash no-op, same key+different hash conflict, belief-time
    replay reconstruction
  - add projection safety checks ensuring ribbon diagnostics cannot mutate SL/SB
    authoritative state without promotion receipts
- Resolve idempotency/dedupe cooperation decision queue from
  `docs/planning/itir_idempotency_dedupe_cooperation_20260208.md`
  before freezing `itir.exchange.v1`:
  - ratify `Q1` timeline axis policy for unified Streamline semantics
  - ratify `Q2` SB "mechanical should" storage contract (flags vs imperative text)
  - ratify `Q3` narrative frame storage model
  - ratify `Q4` dual-role subject/object schema policy
  - ratify `Q5` action kit ontology placement (template vs remedy class)
  - ratify `Q6` authority-crossing conflict domain boundaries
  - ratify `Q7` customary law precedence/reconciliation policy
  - ratify `Q8` expansion trace depth defaults (raw IDs only vs reducer trace)
  - ratify `Q9` evidence overlap cardinality (many-to-many canonical referencing)
  - ratify `Q10` clinic-mode offline inference requirement
  - ratify `Q11` canonical reducer runtime ownership model
    (shared runtime + SL-governed semantics)
- Enforce SL shared-reducer reuse policy from
  `docs/planning/itir_idempotency_dedupe_cooperation_20260208.md`:
  - define shared canonical reducer contract surface (service/package + versioning)
  - add TiRCorder adapter contract: transcription/text -> canonical shared IDs
  - add SB adapter contract: reduced records reference canonical shared IDs
  - add drift guard checks that forbid introducing independent canonical token/
    concept identity stores in TiRCorder/SB without explicit ADR override
  - add conformance tests that local heuristic tags are non-canonical unless
    promoted via receipts
- Execute reducer ownership contract from
  `docs/planning/reducer_ownership_contract_20260208.md`:
  - ratify Option C ownership model and capture as ADR
  - define canonical reducer integration surface (package/service API) and
    compatibility matrix
  - add envelope metadata fields for reducer provenance:
    `reducer_runtime_version` and `semantic_contract_version`
  - add canonical consistency tests across SL/TiRCorder/SB integration paths
  - add cross-product identity tests: same text via TiRCorder path vs SB path
    resolves to identical canonical IDs for same reducer/profile version
  - add SB boundary tests asserting SB reducer changes cannot alter canonical
    token/concept identity assignments
- Apply canonical consumption matrix from
  `docs/planning/itir_consumption_matrix_20260208.md`:
  - add adapter conformance checks for declared producer/consumer paths
  - add explicit tests for authority-write null paths (Ribbon->state, SB->capture)
  - ensure diagnostics-only outputs stay non-authoritative without receipts
  - add semantic-anchor conformance checks that SB/TiRCorder labeling paths use
    SL-issued canonical IDs and do not define parallel equivalence logic
- Execute Concept/RuleAtom + Expansion + Contradiction contract from
  `docs/planning/concept_ruleatom_expansion_contradiction_contract_20260208.md`:
  - add layer-boundary conformance checks: Concept identity layer vs RuleAtom
    logic layer references
  - add expansion-invariant checks over `C1`/`C2`/`C3`/`C4` reporting surfaces
    for SB SITREPs and receipts packs
  - add contradiction-finder fixtures for cross-system modality clashes and
    `needs_reconciliation` default outputs
  - ratify reconciliation policy linkage with `Q7` (precedence vs parallel
    authority policy)
- Execute TiRC->SL + Context Envelope + Promotion Receipt contract from
  `docs/planning/tirc_sl_context_envelope_promotion_receipts_contract_20260208.md`:
  - implement TiRCorder adapter path: transcript text -> shared canonical IDs
  - add conformance tests that TiRCorder heuristics remain non-canonical unless
    promoted via receipts
  - add context-envelope grounding tests that SB context is additive/read-only
    for SL interpretation flows
  - add authority-crossing receipt tests for required envelope linkage fields
    (`event_id`, `idempotency_key`, `payload_hash`, `correlation_id`,
    `causation_id`, authority classes)
- Execute Three Locks + Narrative Sovereignty contract from
  `docs/planning/three_locks_narrative_sovereignty_contract_20260208.md`:
  - implement Frame Compiler hard-fail checks for missing thesis/receipt/action
    locks
  - enforce claim->receipt anchor checks for all public artifact sentences
  - replace any exact "12-word only" gate with quality-gate policy
    (interpretable + receipt-backed + non-contradictory)
  - add anti-gaming tests:
    jargon-stuffed thesis, smooth unanchored thesis, jurisdiction-free action
- Re-run docTR timing on SensibLaw root PDFs using `/Whisper-WebUI/venv` (GPU if available) and record results in `doctr/PROFILE_RUNTIME_NOTES.md` on 2026-02-06.
- Implement timeline ribbon UI: conserved-quantity lens selector, conservation badge, lens inspector, segment tooltips, split/merge checks, and compare overlay (see `SensibLaw/docs/timeline_ribbon.md`).
- Wire ribbon UI to selector contract (`itir-ribbon/ui_contract.md`) and expose conservation metadata for Playwright tests.
- [P0] Implement SensibLaw lexeme layer tables + ingestion + tests (see `SensibLaw/docs/lexeme_layer.md`). DONE
  - Dependencies:
    - canonical text + span invariants (`SensibLaw/docs/tokenizer_contract.md`)
    - deterministic normalization (`SensibLaw/src/text/lexeme_normalizer.py`)
    - lexeme indexing (`SensibLaw/src/text/lexeme_index.py`)
    - storage tables in `SensibLaw/src/storage/versioned_store.py`
- Wire TiRCorder WhisperX-WebUI outputs to SB execution envelopes (adapter + tests + fixture). (Done)
- Fix missing TextSpan errors during PDF ingest for `Mabo [No 2]`, `House v The King`, `Native Title (NSW) Act 1994`, and `Plaintiff S157` (or add an explicit allow-missing-spans flag).
- Implement suite-level context safeguards: context-bound artifact view, epistemic state overlay, and context drift warnings (see `docs/user_stories.md`).
- Implement SL claim typing enforcement with inference-to-evidence graph requirements and denial pattern clustering (see `docs/user_stories.md`).
- Implement SB reputational exposure map and power asymmetry indicators (see `docs/user_stories.md`).
- Define Context Envelope JSON schema (see `docs/planning/adr_ctx_001.md`).
- Add UI invariant tests: no context-free rendering, no silent context loss, and
  irreversible compression (see `docs/planning/ui_context_components.md`).
- Wire Context Envelope validation into ingest and render paths (see
  `docs/planning/context_envelope_schema.md`).
- Implement UI invariant test harness entries for context drift, epistemic
  slider integrity, and interpretation-optional mode (see
  `docs/planning/ui_invariant_tests.md`).
- Draft database schema for context envelope storage (see
  `docs/planning/context_envelope_db_sketch.md`).
- Add minimal JSON fixtures for context envelope validation (see
  `docs/planning/context_envelope_fixtures.json`).
- Add UI invariant test runner template (see
  `docs/planning/ui_invariant_test_runner.md`).
- Choose a JSON Schema validator and wire fixture validation into CI (see
  `docs/planning/context_envelope_validate_stub.py`).

## Blockers / constraints
- No explicit blockers listed in submodule TODO files.
- reverse-engineered-chatgpt: send-message testing is stalled due to bot detection (noted in the ITIR-suite README), which may block any tasks that require message sending.
