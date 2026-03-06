# TODO (ITIR-suite)

## Last assessed
- 2026-02-08

## Submodule TODO snapshot
- SensibLaw: S6 in progress with S6.5 external consumer contracts stubbed; near-term focus on schema freezes, sprint selection, Sprint 9 UI hardening, ingestion discipline tasks, and bounded citation-follow expansion; Sprint S7 checklist targets API/CLI projections, golden tests, and red-flag guards.
- SL-reasoner: no TODOs found.
- tircorder-JOBBIE: accessibility TODOs (extend ARIA roles/labels, add `aria-live`, automate audits, expand manual testing).
- WhisperX-WebUI: README TODO list appears complete; translation PRs requested.
- reverse-engineered-chatgpt: README TODOs remaining (better error handling, improve documentation); TODO.md items all completed.
- chat-export-structurer: no TODOs found.
- StatiBaker: pending work across intent/scope, temporal reduction rules (carryover/new/resolved), atom/handle definitions, integration adapters for TIRC/SL/ITIR refs, and guard tests that prevent content summarization.
- notebooklm-py: no TODOs found.
- Chatistics: no TODOs found.
- pyThunderbird: no TODOs found.

## Active TODOs
- Come back to the Duncan/Emma response draft:
  - `docs/planning/response_to_duncan_emma_itir_hospital_advocacy_20260208.md` missed the intended mark (needs a better synthesis/voice and should be evaluated against the actual posting context).
- Tool Use Summary view follow-up:
  - Shell/hour is not hydrating from available sources (incl. chats); also verify Input/hour hydration.
  - Determine whether Shell/hour and Input/hour share the same upstream event/time-binning pipeline (likely coupled) and fix at the right layer (ingest vs reducer vs projection).
  - NotebookLM: ensure NotebookLM interactions (via `notebooklm-py` / any export/adapter) are ingested into the same tool-use event stream so Shell/hour/Input/hour and related counters can hydrate consistently.
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
  - add axis hierarchy policy fixtures and collision tests (`A1` / `Q1`)
  - implement SB fold-policy receipt + anti-nudge red-team tests (`A2` / `Q2`)
  - add claim-link provenance quality gates for receipts-backed artifacts (`A3`)
  - add plural-law non-reduction preservation fixtures (`A4` / `Q7`)
  - define encrypted-local performance budget benchmarks and degradation
    contracts (`A5`)
  - define contradiction action-branch protocol tests with uncertainty labels
    and no forced collapse (`A6`)
  - add deterministic lexical-noise guard fixtures:
    stopwords/number-heavy spans, cross-page artifacts, citation boilerplate
    flooding (`A7`)
  - add fail-closed CI stub tests for unresolved AIDs/Qx controls, with explicit
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
- Execute SL engine/profile followthrough from
  `docs/planning/sl_lce_profile_followthrough_20260208.md`:
  - draft domain-neutral engine spec (`docs/planning/compression_engine.md`)
  - define profile contracts (`docs/planning/profile_contracts.md`) for
    `sl_profile`, `sb_profile`, and `infra_profile` boundaries
  - define profile lint rules (`docs/planning/profile_lint_rules.md`) for
    forbidden axes/groups per profile
  - define cross-profile safety tests
    (`docs/planning/cross_profile_safety_tests.md`) that keep compression
    mechanics fixed while admissibility varies
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
- Implement Casey exchange channels defined in
  `casey-git-clone/docs/interfaces.md`: publish ingress, sync command, collapse
  command, build snapshot egress, and fuzzymodo facts export adapter.
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
- Implement SensibLaw lexeme layer tables + ingestion + tests (see `SensibLaw/docs/lexeme_layer.md`).
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
