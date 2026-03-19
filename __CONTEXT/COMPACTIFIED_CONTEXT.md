# Compactified Context (ITIR-suite)

## 2026-03-19
- Resolved nine online ChatGPT UUIDs using `robust-context-fetch`.
- Canonical archive path: `~/chat_archive.sqlite`.
- Exact DB matches were recorded from the archive; remaining supplied UUIDs were
  resolved via live read-only fetch because write persistence hit a locked DB.
- Recorded the resolved thread metadata for downstream context sync:
  - `69b90f8b-3cf8-839c-bffe-b7da95565338`
    - title: `Zelph 0.9.5 Update`
    - canonical thread ID: `e45a889fa7d88547021c2a95ded89270b40fd6db`
    - source: `db`
    - topic: full arc from Zelph capability assessment to a tiny deterministic
      SL -> Zelph bridge demo
  - `69b9f131-bb3c-839c-b2cd-233b4af8c72a`
    - title: `Branch · Zelph 0.9.5 Update`
    - canonical thread ID: `e3d8bffb77f7df0337efe3684653c6bf441ca061`
    - source: `db`
    - topic: Stefan-facing update refinement and upstream positioning, with
      Mary treated as a competitor benchmark
  - `69b75a97-6784-839b-bc2b-3824717279e0`
    - title: `ITIR SensibLaw Model`
    - canonical thread ID: `044540f8d6f0a880d507c1ce81341613b56d13b9`
    - source: `db`
    - topic: ITIR/SL formalization plus uploaded-file handling and
      file-search fallback for partial snippets
  - `69b7e167-53d8-839d-a9e6-56b239746525`
    - title: `Governance Model Mapping`
    - canonical thread ID: `49554563c68c31b87b5f28ff673355c0ff8b2a1b`
    - source: `db`
    - topic: operator-explicit mapping of the governance model into the
      ITIR/SensibLaw machine
  - `69b7e164-d0a8-839d-8418-41769163ba6d`
    - title: `Formal Model Application`
    - canonical thread ID: `c1279d811ec67be9ebae1cab6c1ee865ca24299b`
    - source: `db`
    - topic: state-compiler / prototype application over uploaded files
  - `69ba8956-35b8-839b-9707-f8c91c2b02dd`
    - title: `Ambiguity of "Community"`
    - canonical thread ID: unresolved during this pass
    - source: `web`
    - topic: `"community"` behaves like a legal normative placeholder; do not
      assume Wikidata/entity linking can resolve it
  - `69bab27a-cb28-8398-b3ea-940d4fb47772`
    - title: `Branch · Ambiguity of "Community"`
    - canonical thread ID: unresolved during this pass
    - source: `web`
    - topic: branch confirmation of the same unresolved normative-placeholder
      boundary
  - `69ba8c55-163c-839d-86b9-6c366a8dc29a`
    - title: `Formal Model to Engine`
    - canonical thread ID: unresolved during this pass
    - source: `web`
    - topic: explicit O/R/C/S/L/P/G/F mapping for ingest, lexer, and
      compression lanes
  - `69b7eb5b-0c78-839d-9012-a484905fdf0c`
    - title: `Model Mapping to Casey`
    - canonical thread ID: unresolved during this pass
    - source: `web`
    - topic: Casey state/lattice/governance mapping via
      `TreeState + WorkspaceView`, candidate lattice, and explicit collapse
  - `69b89b50-5554-839d-b9cf-f50f6eab3b8b`
    - title: `Debugging UX in Games`
    - canonical thread ID: unresolved during this pass
    - source: `web`
    - topic: debugging/stream isolation discussion; not promoted to active
      repo planning
  - `69ba3af2-5df8-839b-bd8a-7c865be0b052`
    - title: `Casey Git Clone Differences`
    - canonical thread ID: unresolved during this pass
    - source: `web`
    - topic: Casey differentiators centered on superposition, explicit
      collapse, workspace selection, and immutable build projections
- Surface-boundary followthrough for the ITIR stack:
  - `SL` = shared representation/compression substrate
  - `casey-git-clone` = mutable possibility / lattice surface
  - `fuzzymodo` = read-only reasoning / compression-gap surface
  - `StatiBaker` = observer-only governance-memory / alignment-gap surface
- Added planning artifacts to lock the next two boundaries:
  - `docs/planning/casey_fuzzymodo_interface_contract_20260319.md`
  - `docs/planning/casey_statiBaker_receipt_schema_20260319.md`
- Priority order sharpened:
  1. implement Casey -> fuzzymodo export/advisory contract
  2. implement Casey -> StatiBaker receipt/reference seam

## 2026-03-06
- Aligned priority execution sequencing for lexeme layer, tokenizer migration,
  compression engine followthrough, Wikidata projection, and GWB/AAO pipelines.
- Added planning docs:
  - `docs/planning/priority_execution_sequence_20260306.md`
  - `docs/planning/tokenizer_migration_plan_20260306.md`
- Updated `TODO.md` to reflect dependencies and tokenizer migration as a P0 item.
- Tightened tokenizer migration acceptance to two explicit backtest lanes:
  - GWB route payload parity
  - Existing SL ingest regression corpus (`Mabo [No 2]`, `House v The King`,
    `Plaintiff S157`, `Native Title (NSW) Act 1994`)
  - StatiBaker reducer and UI invariants (shared canonical IDs, no
    re-tokenization, compress->expand, no summary injection/re-segmentation,
    context-bound rendering, tool-use/chat-context metric stability)
- Added Phase 18 planning scaffolding:
  - `.planning/phases/18-priority-stack/phase.md`
  - `.planning/phases/18-priority-stack/18-01-PLAN.md`
  - `.planning/phases/18-priority-stack/18-02-PLAN.md`
- Robust context fetch attempt for thread
  `69aa6b40-6c0c-839a-a4a8-2d325db05451` failed:
  - local DB missing (`/home/c/.chat_archive.sqlite`)
  - web fallback failed due to DNS/network resolution for `chatgpt.com`
- Robust context fetch retried with outbound access:
  - web view succeeded (no local storage)
  - persist/download timed out (no export ingested)
- Pulled online thread `69aa6b40-6c0c-839a-a4a8-2d325db05451` into
  `/home/c/chat_archive.sqlite` via `reverse-engineered-chatgpt/scripts/pull_to_structurer.py`
  (38 messages). Canonical thread id:
  `fa3fda1d40351d824c9e886012ae6721a721cba5` (title: "Token Stream Decisions").

## 2026-02-06
- Documented suite-wide user stories and invariants for context preservation,
  claim typing, and pattern-only exposure across ITIR/SL/SB.
- Added "context is mandatory" invariant and knowledge-state overlay notes to
  `docs/itir_model.md`.
- Updated `TODO.md` with implementation tasks tied to the new user stories.
- Added ADR-CTX-001 and supporting UI and doctrine specs in `docs/planning/`.
- Added Context Envelope schema draft and UI invariant test checklist; added
  front-page context line to `README.md`.
- Added Context Envelope DB sketch, fixtures, and test runner template in
  `docs/planning/`.
- Added validation notes to context schema and a stub validator script in
  `docs/planning/`.
- Added `docs/planning/README.md` with validation stub guidance.

## 2026-02-07
- Synced live conversation `698686e2-6e48-839e-ad0f-91e6fa4697f8`
  (`OSS-Fuzz Bug Detection`) via `re_gpt.cli --view` with network approval.
- Confirmed latest assistant reply timestamp
  `2026-02-07T03:05:48.055634Z`.
- Captured selector-DSL direction as the current normative-graph focus for
  follow-on planning and implementation.
- Added phase/layout scaffolding for Fuzzymodo selector DSL across
  `.planning/phases/16-fuzzymodo-selector-dsl/`,
  `docs/planning/fuzzymodo/`, and `fuzzymodo/`.
- Added separate Casey Git Clone scaffold across
  `.planning/phases/17-casey-git-clone/`,
  `docs/planning/casey-git-clone/`, and `casey-git-clone/`.
- Defined intended intersections, interaction flow, and exchange channels
  inside `fuzzymodo/docs/interfaces.md` and
  `casey-git-clone/docs/interfaces.md`.
- Updated both project READMEs and `TODO.md` so implementation tasks map
  directly to the new channel contracts.
- Expanded the same interface-contract structure across all core ITIR component
  directories and added suite index `docs/planning/project_interfaces.md`.
- Documented ITIR-suite explicitly as orchestration control plane in
  `README.md` and added `docs/planning/itir_orchestrator.md` with channel-level
  orchestration contract.
- Moved detailed ITIR object model ownership to
  `SensibLaw/docs/itir_model.md` and reduced root `docs/itir_model.md` to a
  control-plane pointer.
- Refreshed live conversation `698686e2-6e48-839e-ad0f-91e6fa4697f8` and
  confirmed newer assistant state at `2026-02-07T03:05:48.055634Z`.
- Added conversation step mapping artifacts:
  - `docs/planning/fuzzymodo/conversation_step_map.md` (updated)
  - `docs/planning/fuzzymodo/speculation_policy.md` (new)
  - `docs/planning/casey-git-clone/conversation_step_map.md` (new)
- Implemented Fuzzymodo evaluator + speculation primitives and tests:
  - `fuzzymodo/src/selector_dsl/evaluator.py`
  - `fuzzymodo/src/selector_dsl/speculation.py`
  - `fuzzymodo/tests/test_evaluator.py`
  - `fuzzymodo/tests/test_speculation.py`
- Implemented Casey core model + non-blocking operations and tests:
  - `casey-git-clone/src/casey_git_clone/models.py`
  - `casey-git-clone/src/casey_git_clone/operations.py`
  - `casey-git-clone/tests/test_models.py`
  - `casey-git-clone/tests/test_operations.py`
- Added project changelogs:
  - `fuzzymodo/CHANGELOG.md`
  - `casey-git-clone/CHANGELOG.md`
- Added evidence-first ITIR definition source file from chat archive extracts:
  - `__CONTEXT/ITIR_DEFINITION_CONTEXT.md`
- Added ITIR definition ratification draft with explicit accepted/rejected/pending clauses:
  - `__CONTEXT/ITIR_DEFINITION_RATIFICATION.md`
- Applied user adjudication to six key definition snippets:
  - marked `investigative operating system` and `one system/modes` as qualified
    metaphors/doctrine, not canonical runtime identity.
  - affirmed `ITIR-suite` meta-repo/control-plane and SB product distinction.
  - re-scoped `re-segment time` as boundary guardrail, not default ITIR action.
- Added doctrine page clarifying separation of powers:
  - `docs/planning/why_itir_not_sl.md`
- Ran targeted archive sweep for `SL` (whole-word), `sensiblaw`, `itir`, and
  `suite` over `~/.chat_archive.sqlite` with
  `role IN ('user','assistant')`.
- Captured sweep artifacts:
  - `__CONTEXT/last_sync/20260207T043655Z_term_sweep_sl_sensiblaw_itir_suite.json`
  - `__CONTEXT/last_sync/20260207T043655Z_term_sweep_sl_sensiblaw_itir_suite.md`
- Synced follow-up planning into `TODO.md` for runbook formalization,
  high-signal thread index refresh, and `suite` false-positive triage.

## 2026-03-09
- Resolved archived fuzzymodo context from the canonical DB using
  `robust-context-fetch`:
  - online UUID `698686e2-6e48-839e-ad0f-91e6fa4697f8`
  - title `OSS-Fuzz Bug Detection`
  - canonical thread id `f007250c85c623e16ea46238451cdbb00c745743`
  - source used `db`
- Confirmed the archived fuzzymodo discussion treats selector/decision outputs
  as control-plane or observer-class artifacts, not as SB authority.
- Added suite planning note
  `docs/planning/fuzzymodo_statiBaker_interface_20260309.md` to freeze the
  minimal seam:
  - `fuzzymodo -> StatiBaker` is observer-only
  - DB-backed overlay rows or reference-heavy ledger refs only
  - selector DSL and norm constraints stay outside SB canonical state/policy
- Synced `fuzzymodo` and `StatiBaker` interface docs to that boundary and
  clarified that the full clause-rich `fuzzymodo` decision egress is still
  planned rather than fully implemented.
- Resolved archived Casey context from the canonical DB using
  `robust-context-fetch`:
  - title `Git Coordination Debate`
  - online UUID `697c4c95-e1cc-839e-ac27-c262a27574eb`
  - canonical thread id `b8800296148a7c14e0b84a152e0c67a2ba32acb0`
  - source used `db`
  - main topics: candidate-per-path superposition, explicit workspace
    selection, explicit collapse, immutable build views
  - title `Casey's Git idea summary`
  - canonical thread id `be7800224c818a1b8d029595c915727fffcdea04`
  - source used `db`
  - main topic: keep ambiguity visible until explicit collapse
- Added suite planning note
  `docs/planning/casey_git_clone_statiBaker_interface_20260309.md` to freeze
  the minimal Casey seam:
  - `casey-git-clone -> StatiBaker` is observer-only
  - DB-backed overlay rows or reference-heavy ledger refs only
  - Casey keeps workspace/candidate/build authority; SB stores receipts and refs

## 2026-02-07 (additional live context refresh)
- Synced conversation `6986c9f5-3988-839d-ad80-9338ea8a04eb`
  (`Conductor vs SB/ITIR`); latest assistant timestamp:
  `2026-02-07T06:10:06.463491Z`.
- Synced conversation `6986ccc6-a58c-83a1-9c72-76c671dd7af0`
  (`Codeex and Vibe Faster`); latest assistant timestamp:
  `2026-02-07T05:34:09.991600Z`.
- Synced JavaCrust-adjacent thread
  `6986c16d-e97c-839b-82b8-425b1e5a5e6d`
  (`GPU Methodology for CPU`); latest assistant timestamp:
  `2026-02-07T05:23:13.297950Z`.
- Note: user-provided JavaCrust ID
  `986c16d-e97c-839b-82b8-425b1e5a5e6d` was invalid; corrected leading segment
  (`6986c16d-...`) resolved.
- Updated tracked conversation list in `__CONTEXT/convo_ids.md` for future
  scripted sync runs.
- Added concrete followthrough artifact covering requested sections
  `1.1`-`1.5`, `2.1`-`2.5` (+ dev environment), and `3.1`-`3.5`:
  - `docs/planning/sb_casey_jesuscrust_followthrough_20260207.md`
- Linked followthrough doc from planning index and queued implementation items
  in root `TODO.md`.

## 2026-02-08
- Ran robust context refresh for
  `6986d38e-4b5c-839b-813a-608aa0de88d5` (`ADR language vs SensibLaw`).
- Live fetch confirmed latest assistant timestamp remains
  `2026-02-07T06:01:41.279462Z`.
- Added SL thread followthrough planning artifact:
  - `docs/planning/sl_lce_profile_followthrough_20260208.md`
- Saved refresh evidence artifact:
  - `__CONTEXT/last_sync/20260208T053748Z_context_refresh_6986d38e.md`
- Refreshed planning index and tracked conversation IDs:
  - `docs/planning/README.md`
  - `__CONTEXT/convo_ids.md`
- Queued implementation backlog for compression engine/profile contracts/lint
  and cross-profile safety tests in root `TODO.md`.
- Ran additional triplet context refresh for:
  - `6986c9f5-3988-839d-ad80-9338ea8a04eb` (`Conductor vs SB/ITIR`)
  - `6986ccc6-a58c-83a1-9c72-76c671dd7af0` (`Codeex and Vibe Faster`)
  - `6986c16d-e97c-839b-82b8-425b1e5a5e6d` (`GPU Methodology for CPU`)
- Saved triplet artifacts:
  - `__CONTEXT/last_sync/20260208T054446Z_context_refresh_triplet.md`
  - `__CONTEXT/last_sync/20260208T054446Z_latest_triplet_6986c9f5_6986ccc6_6986c16d.tsv`
- Updated planning docs with refreshed `Conductor vs SB/ITIR` timestamp
  (`2026-02-08T03:09:11.241219Z`) and explicit "forensics != memory authority"
  boundary framing.
- Corrected feedback source provenance from Reddit to Moltbook and replaced
  intake artifact with
  `docs/planning/moltbook_feedback_alignment_20260208.md`, expanding coverage
  to `u/DexterAI`, `u/FiverrClawOfficial`, `u/TipJarBot`, and `u/Tony-Ghost-Don`.
- Queued followthrough in `TODO.md` for idempotency/correlation provenance
  fields, reversible transition contracts, belief-time replay checks, and
  observer-only handling of external settlement ownership signals by default.
- Added focused four-way intersection contract artifact for
  `SensibLaw` x `tircorder-JOBBIE` x `itir-ribbon` x `StatiBaker`:
  `docs/planning/sl_tircorder_ribbon_sb_intersection_20260208.md`.
- Linked the artifact from planning indexes and queued followthrough in
  `TODO.md` for shared exchange envelope schema, edge adapter stubs, replay and
  conflict tests, and projection safety checks.
- Added idempotency/dedupe cooperation addendum:
  `docs/planning/itir_idempotency_dedupe_cooperation_20260208.md`
  capturing shared-vs-siloed boundary confirmations, authority-crossing
  handshake, anti-enshittification expansion invariant, and unresolved
  schema-freeze decision queue (`Q1`-`Q10`).
- Updated planning indexes and `TODO.md` to require ratification of `Q1`-`Q10`
  before freezing `itir.exchange.v1`.
- Expanded the same addendum with explicit non-dilution guidance:
  SL compression/reduction as shared reusable infrastructure, no competing
  canonical token/concept identity stores in TiRCorder/SB, and interim
  drift-control defaults to keep integration boundaries stable while ratification
  remains open.
- Added dedicated reducer ownership contract:
  `docs/planning/reducer_ownership_contract_20260208.md`
  clarifying which reducers are shared vs local, and recommending shared runtime
  distribution with SL semantic governance (Option C) to prevent duplicate
  canonical reducer implementations.
- Updated `TODO.md` and planning indexes to include reducer ownership ratification
  and conformance tests across SL/TiRCorder/SB.
- Expanded schema-freeze decision queue scope from `Q1`-`Q10` to `Q1`-`Q11`
  by adding canonical reducer runtime ownership ratification.
- Refined reducer contract with explicit mechanism-vs-semantics split, SB<->SL
  reducer handshake constraints, default Option C operating posture, and
  additional test/provenance requirements (`reducer_runtime_version`,
  `semantic_contract_version`, cross-product identity tests).
- Added canonical producer/consumer matrix artifact:
  `docs/planning/itir_consumption_matrix_20260208.md`
  and linked it from planning indexes, orchestration contract, and active TODOs
  as the primary anti-drift source for inter-component flow boundaries.
- Added focused contract artifact:
  `docs/planning/concept_ruleatom_expansion_contradiction_contract_20260208.md`
  to lock Concept-vs-RuleAtom boundaries, formalize the Expansion Invariant cost
  model (`C1`-`C4`), and define contradiction-finder output behavior with
  `needs_reconciliation` default for cross-system conflicts.
- Added implementation contract artifact:
  `docs/planning/tirc_sl_context_envelope_promotion_receipts_contract_20260208.md`
  to define TiRC->SL reducer wiring, context-envelope trauma grounding
  boundaries, and required promotion receipt linkage fields for authority-crossing
  writes.
- Added lock-enforcement artifact:
  `docs/planning/three_locks_narrative_sovereignty_contract_20260208.md`
  to codify thesis/receipt/action lock requirements with explicit anti-gaming
  caution: no hard exact 12-word correctness gate; quality/verifiability gates
  take precedence.
- Tightened core contracts to explicitly codify semantic anchors as the
  anti-dilution mechanism (SL-owned meaning spine) and to re-assert that
  temporal reducer logic remains SB-owned even when reducer runtime mechanisms
  are shared.
- Added prospective execution artifact:
  `docs/planning/itir_prospective_sprint_10_refactor_20260208.md`
  to convert the current contract set into a single 10-day thin-slice refactor
  plan with explicit blocking ratifications (`Q2`, `Q6`, `Q11`), envelope
  freeze, shared reducer integration, and contract-test gates.
- Linked the sprint artifact in `docs/planning/README.md` and queued active
  TODO execution items tied to that sprint.
- Added refactor coordination control-plane artifact:
  `docs/planning/refactor-master-coordination.md`
  to lock contract docs for the refactor window, define decision/merge gates,
  and centralize Sprint 10 execution tracking.
- Linked coordination artifact from planning index and interface index, and
  added active TODO items to enforce queue-state updates and gate checks.
- Added explicit architectural critique hardening artifact:
  `docs/planning/assumption_stress_test_20260208.md`
  capturing six high-risk assumptions (`A1`-`A6`) with failure modes, control
  policies, and test-gate requirements; wired into refactor master coordination
  and TODO execution backlog.
- Per chat-source phrase sweep, expanded stress controls with two previously
  under-specified items:
  - `A7` deterministic lexical-noise guardrails
    (stopwords/number-heavy spans, cross-page artifacts, citation boilerplate).
  - `A8` fail-closed CI gate discipline for unresolved controls (stub tests or
    explicit waiver receipts).
- Compression-specific hardening pass added:
  - `A9` summary-of-summary decay/review-inversion control via lineage guards
    requiring expansion to raw IDs before downstream summarization.
  - `A10` machine-readable `loss_profile` schema enforcement across fold/sitrep/
    receipts surfaces.
- Added cross-project UI coordination artifacts for multi-renderer discovery and
  integration planning:
  - `docs/planning/ui_surface_registry_20260208.md`
  - `docs/planning/ui_integration_strategy_20260208.md`
  - `docs/planning/ui_surface_manifest.json`
- Confirmed frontend direction from thread
  `69882c94-3094-839a-b539-15529d7e9c6c` as:
  - `SvelteKit + Tailwind` working target for SB migration
  - `React + Vite` explicit fallback posture
- Updated coordination/index artifacts so UI integration is now tracked in the
  same refactor control plane:
  - `docs/planning/project_interfaces.md`
  - `docs/planning/README.md`
  - `docs/planning/refactor-master-coordination.md` (`WS5`, `Q12`)
  - `TODO.md` (launcher + drift-check followthrough items)
