# Devlog

## 2026-03-15
- Re-ran `robust-context-fetch` for whitepaper thread
  `69b41f22-a514-839f-946c-fa0e9f75cc46` after the earlier fetch process was
  interrupted:
  - title: `Insights from Whitepaper`
  - canonical thread id:
    `eab13fe32136bc69aebdb9a21888b76215faab11`
  - source used for final resolution: `db`
  - archived thread now resolves with `122` messages
  - latest archived assistant timestamp:
    `2026-03-13T15:19:54+00:00`
- Extracted the thread's Mary-comparison takeaway into a new planning note
  `docs/planning/mary_parity_roadmap_20260315.md`:
  - Mary Technology should be treated as the near-term benchmark for fact
    management, chronology, provenance, contestation, and operator-facing
    litigation workflow
  - current SL ontology / branch-set / external-ref work is now explicitly
    support infrastructure for that parity target
  - SL's richer Observation / Claim / typed-transition agenda remains valid but
    moves to phase-two followthrough after the fact layer is credible
- Updated `COMPACTIFIED_CONTEXT.md`, `TODO.md`, `plan.md`, and `status.json`
  so Mary parity is the top SL-facing roadmap priority.
- Interpreted the next Mary-parity seam more concretely:
  - the first fact substrate should include a text-grounded
    `statement -> observation -> fact` path rather than jumping directly from
    statements to facts
  - the initial observation layer should use a small stable predicate catalog
    aimed at broad factual coverage instead of a large doctrinal ontology
  - existing `CaseObservation` / `ActionObservation` /
    `AlignmentObservation` / `DecisionObservation` shapes remain adjacent
    projection or aggregation surfaces rather than the canonical intake lane
- Defined the immediate follow-on seam after observations:
  - add a deterministic `ObservationRecord -> EventCandidate` assembler
  - keep event candidates derived and reconstructable from observation
    evidence, with separate event-attribute and event-evidence tables
  - keep contestation observation-first rather than duplicating base events
- Tightened the Mary-parity fact substrate contracts further:
  - separate structural/content identity from run/execution metadata
  - make abstention explicit in status semantics instead of silent omission
  - keep event assembly portable by consuming normalized observation predicates
    only, with language/jurisdiction variation pushed into dictionaries,
    mappings, and parser-backed normalization layers
- Expanded the new Mary-parity user-story set in `docs/user_stories.md` to
  make the role pressure more concrete for:
  - community legal centre intake
  - NGO litigation/campaign assembly
  - paralegal, solicitor, barrister, and judge/associate workflows
  - personal ITIR, investigative ITIR, trauma-survivor, and support-worker
    workflows
- Added two planning follow-ons to turn those stories into implementation
  pressure:
  - `docs/planning/mary_parity_user_story_acceptance_matrix_20260315.md`
  - `docs/planning/mary_parity_gap_analysis_20260315.md`
- Updated TODO/plan to make the next Mary-parity loop explicitly story-driven:
  - richer review queue reasons and contested/chronology triage first
  - workflow run -> fact-review run reopen mapping second
  - legal/procedural observation visibility widening third
- Added the next Mary-parity operator/workbench slice:
  - role-meaningful review queue reasons
  - source-label-centric fact-run listing and reopen support
  - bounded operator views for intake, chronology, procedure, and contested work
  - story-driven acceptance reports over persisted fact-review runs
  - a thin read-only `itir-svelte` fact-review workbench at
    `/graphs/fact-review`
- Expanded the role/acceptance pressure again after implementation so the next
  fixture families are explicit:
  - contested Wikipedia/Wikidata moderation and defamation-sensitive review
  - public-figure legality assessment and lawyer-vs-maintainer conflict lanes
  - family-law / child-sensitive / cross-side handoff lanes
  - medical-negligence / professional-discipline overlap lanes
  - personal-to-professional handoff and anti-AI-psychosis / anti-false-
    coherence lanes
- Added the Wave 1 legal parity gate itself:
  - canonical transcript/AU + synthetic fixture manifest
  - batch acceptance runner over persisted fact-review runs
  - stricter story results with failed-check IDs and gap tags
  - workbench grouping/navigation updates around those same issue classes
  - additive AU legal/procedural signal widening for `claimed`, `denied`,
    `ordered`, and `ruled`
- Continued the Mary-parity acceptance program through later waves:
  - greened `wave2_balanced`
  - greened `wave3_trauma_advocacy`
  - greened `wave3_public_knowledge`
  - greened `wave4_family_law`
  - greened `wave4_medical_regulatory`
  - greened `wave5_handoff_false_coherence`
- Broadened Wave 5 beyond synthetic-only coverage by adding repo-curated real
  transcript fixtures for:
  - professional handoff
  - contradiction-preserving false-coherence review
- Added additive workbench/operator views for:
  - `trauma_handoff`
  - `professional_handoff`
  - `false_coherence_review`
  - `public_claim_review`
  - `wiki_fidelity`
  - `claim_alignment`
- Added a parity status audit and synced the Mary-planning files:
  - `docs/planning/mary_parity_status_audit_20260315.md`
  - roadmap/gap-analysis updates
  - TODO/plan/compactified-context sync

## 2026-03-18
- Resolved and analyzed the full transcripts for the five online ChatGPT UUIDs
  pulled into `~/chat_archive.sqlite` on 2026-03-18:
  - `69b90f8b-3cf8-839c-bffe-b7da95565338` / `Zelph 0.9.5 Update`
    - full arc: Zelph capability assessment, SL/ITIR overlap check, negligence
      rule minimization, irreducible-disagreement framing, and a tiny
      deterministic SL -> Zelph bridge demo
  - `69b9f131-bb3c-839c-b2cd-233b4af8c72a` / `Branch · Zelph 0.9.5 Update`
    - full arc: Stefan-facing draft refinement, upstream positioning, and Mary
      treated as a competitor benchmark rather than evidence of the user’s
      architecture
  - `69b75a97-6784-839b-bc2b-3824717279e0` / `ITIR SensibLaw Model`
    - full arc: formalizing ITIR/SL terms while insisting truncated uploaded
      content be treated as partial and answered via file-search / full-doc
      lookup
  - `69b7e167-53d8-839d-a9e6-56b239746525` / `Governance Model Mapping`
    - full arc: mapping the O/R/C/S/L/P/G/F model into the ITIR/SensibLaw
      governance machine and making the operator explicit for convergence,
      proofs, and ZK attestation reasoning
  - `69b7e164-d0a8-839d-8418-41769163ba6d` / `Formal Model Application`
    - full arc: applying a state-compiler / prototype model to uploaded files,
      with the loaded-file/searchable-file behavior treated as operational
      ground truth
- Updated `COMPACTIFIED_CONTEXT.md`, `__CONTEXT/COMPACTIFIED_CONTEXT.md`, and
  `__CONTEXT/convo_ids.md` so the resolved thread metadata is recorded at the
  repo context layer as well as the sync helper layer.
- Updated `TODO.md` to reflect the full-conversation archive pass and the
  sharpened SL boundary notes.
- Added a “Test → Ingest → Zelph bridge path” section to
  `docs/planning/mary_parity_roadmap_20260315.md` so Mary-parity execution keeps
  the Wave acceptance suites, deterministic ingest, and the tiny SL -> Zelph
  demo aligned.
- No code changes were needed for this turn; the work was docs/context only.

## 2026-03-14
- Used `robust-context-fetch` to pull online thread
  `69b41f22-a514-839f-946c-fa0e9f75cc46` into the canonical archive and resolve
  it locally:
  - title: `Insights from Whitepaper`
  - canonical thread id:
    `eab13fe32136bc69aebdb9a21888b76215faab11`
  - source used for final resolution: `db`
- Re-ran the same online pull after additional posts were added to the thread:
  - parsed messages increased from `93` to `110`
  - latest assistant timestamp now
    `2026-03-13T14:58:51+00:00`
- Captured the thread's main repo-facing decisions into
  `COMPACTIFIED_CONTEXT.md` and new planning note
  `docs/planning/sl_whitepaper_followthrough_20260314.md`:
  - preserve SL's richer event-centric model rather than flattening it into
    plain RDF triples
  - introduce an explicit Observation layer between source statements and
    events
  - prioritize the provenance-first
    `evidence -> fact -> norm -> claim` seam ahead of broader ontology growth
  - treat RDF/Wikidata as an adapter/export boundary
  - queue temporal law/versioning and jurisdiction as the next hidden
    infrastructure slice after observation is explicit
  - add typed transition / guarded-seam framing for legal state updates
  - add a bounded p-adic / ultrametric similarity direction as an exploratory,
    explanation-first alternative to embedding-default retrieval
  - narrow Wikidata relevance to jurisdiction/court/legislation/case/actor/time
    shapes for prepopulation and external-reference support
- Updated `TODO.md` and `plan.md` to add the next planned SL milestone.

## 2026-03-10
- Bootstrapped canonical project-memory files for autonomous orchestration.
- Prioritized implementation backlog into milestone order.
- Implemented shared review-state helper and route state chips.
- Reworked narrative-compare into row-select + inspector + bounded graph flow.
- Implemented shared selection bridge helper (`selectionBridge.ts`).
- Wired selection bridge into thread, narrative compare, and wiki contested pages.
- Added route-server `stateReason` telemetry for:
  - `arguments/thread/[threadId]`
  - `graphs/narrative-compare`
  - `graphs/wiki-revision-contested`
- Updated narrative compare visual grammar with explicit posture chips.
- Added regression guard asserting no `localStorage` / `JSON.stringify` UI-state persistence in these workbench pages.
- Ran `node --test itir-svelte/tests/graph_ui_regressions.test.js` (all passing).
- Synced top-level TODO and `itir-svelte/CHANGELOG.md` to implemented behavior.
- Ran P0 tokenizer/lexeme migration regression lane in venv:
  - `tests/test_deterministic_legal_tokenizer.py`
  - `tests/test_lexeme_layer.py`
  - `tests/test_tokenizer_migration_sl_regression.py`
  Result: `30 passed`.
- Updated tokenizer migration planning note and marked `[P0]` tokenizer + lexeme TODOs done.
- Recorded verification refresh in `SensibLaw/CHANGELOG.md`.
- Completed P1 SL engine/profile followthrough v1:
  - ratified contract/lint/safety docs from draft
  - implemented `src/text/profile_admissibility.py`
  - added `tests/test_profile_admissibility.py`
  - test result: `4 passed`
  - marked TODO entry done and logged behavior in changelog

## 2026-03-11
- Started Milestone J: OpenRecall query/read-model interface.
- Updated the OpenRecall planning note, TODO, external-ingestion docs, and
  compactified context so the next slice is explicitly query-first rather than
  GUI-first.
- Implemented neutral OpenRecall query/read-model helpers:
  - latest import runs
  - capture summary by app/title/date
  - screenshot coverage
  - recent filtered capture rows
- Added `SensibLaw/scripts/query_openrecall_import.py` as the bounded CLI over
  those helpers.
- Verified with focused OpenRecall tests (`22 passed`) and direct CLI smoke
  runs against a local ITIR DB.
- Started Milestone K: NotebookLM bounded live smoke.
- Updated NotebookLM development docs plus root TODO/context so the intended
  live path is explicit: auth check with network, then a narrow readonly
  notebook/chat/source smoke instead of the whole generation-heavy E2E suite.
- Added `notebooklm-py/scripts/run_e2e_smoke.py` and unit coverage for the
  bounded smoke runner.
- First live attempt exposed a local env blocker only:
  - repo `.venv` had valid NotebookLM auth
  - repo `.venv` was missing `pytest-asyncio` and `pytest-timeout`
- Installed the missing NotebookLM pytest plugins into the repo-root `.venv`
  and removed the nested `notebooklm-py/.venv`.
- Live NotebookLM smoke then passed from the repo-root `.venv` against the
  `SENSIBLAW` notebook:
  - `auth check --test`
  - notebook list
  - get notebook
  - one bounded readonly chat ask
  - source list
- Continued priority Milestone I (Tool Use Summary hydration):
  - patched `StatiBaker/sb/dashboard.py` so agent `exec_command` tool messages
    contribute hourly bins to `frequency_by_hour.shell`
  - patched `StatiBaker/sb/dashboard.py` so `request_user_input` tool messages
    contribute hourly bins to `frequency_by_hour.input`
  - added tool-use payload fields:
    `exec_command_hour_bins`, `request_user_input_count`,
    `request_user_input_hour_bins`
  - updated summary counters to expose host vs agent-request input split
    (`input_events_host`, `input_events_agent_request_user_input`)
  - added/updated regression tests in `StatiBaker/tests/test_dashboard.py`
    for shell/input hydration from chat-archive tool messages
  - folded NotebookLM notes-meta into the same tool-use stream via synthetic
    `notebooklm_meta_event` family plus `notebooklm_meta_hour_bins`
  - test slice result: `7 passed` for focused tool-use + NotebookLM coverage
- Completed next priority assumption-stress slice:
  - added machine-readable control registry:
    `docs/planning/assumption_controls_registry.json`
  - added explicit waiver receipt path:
    `docs/planning/waivers/assumption_controls_waiver_20260311.md`
  - added fail-closed CI stub tests:
    `SensibLaw/tests/test_assumption_controls_fail_closed.py`
  - added `A1/Q1` axis policy fixtures:
    `SensibLaw/src/sensiblaw/ribbon/axis_policy.py`
    `SensibLaw/tests/test_ribbon_axis_policy.py`
  - verification run:
    `pytest -q tests/test_assumption_controls_fail_closed.py tests/test_ribbon_axis_policy.py`
    result: `5 passed`
- Completed next priority assumption-stress control `A2/Q2`:
  - hardened `StatiBaker/sb/fold.py` with explicit `fold_policy` output:
    `policy_receipt`, boolean `mechanical_should_flags`, and explicit
    `loss_profile` declaration
  - added anti-nudge red-team coverage:
    `StatiBaker/tests/test_fold_policy_redteam.py`
  - expanded fold tests for receipt/flag behavior:
    `StatiBaker/tests/test_fold.py`
  - verification run:
    `pytest -q tests/test_fold.py tests/test_fold_policy_redteam.py`
    result: `6 passed`
- Completed next priority assumption-stress control `A3`:
  - hardened `SensibLaw/src/reporting/narrative_compare.py` so all public
    causal links (`supports`/`undermines`) carry explicit provenance fields:
    `link_type`, `confidence`, `counter_hypothesis_ref`
  - added fail-closed validator
    `ensure_claim_link_provenance_for_public_artifact(...)` and invoked it in
    both validation and comparison report builders
  - expanded causal-link receipts to require:
    `link_type`, `confidence`, `counter_hypothesis_ref`
  - added regression coverage in
    `SensibLaw/tests/test_narrative_compare.py` for field presence + fail-closed
    behavior
  - full `pytest` lane and direct smoke execution against
    `demo/narrative/friendlyjordies_chat_arguments.json` resulted in successful
    validation/comparison artifact builds
- Started Milestone O: NotebookLM metadata/review parity.
  - updated docs/TODO/context/changelog posture so NotebookLM is explicitly
    metadata-first for now, with review/source parity ahead of activity parity
  - added a neutral NotebookLM observer read-model/report module over
    `StatiBaker/runs/<date>/logs/notes/<date>.jsonl`
  - added a bounded JSON query CLI for NotebookLM observer dates/summary/events
  - added source-summary `TextUnit` projection for downstream structure and
    semantic reuse
  - added focused tests around NotebookLM observer summaries, event queries,
    and source-unit projection
- Planned Milestone P: bounded NotebookLM interaction capture.
  - documented a separate additive contract over conversation history and notes
  - decided not to reinterpret `notes_meta` as activity/session data
  - next implementation target is a separate `notebooklm_activity` lane with
    raw capture, normalized preview rows, and query/read-model helpers
- Completed Milestone P: bounded NotebookLM interaction capture.
  - added `StatiBaker/scripts/capture_notebooklm_activity.py` for bounded
    conversation-history and note observation
  - added `StatiBaker/adapters/notebooklm_activity.py` with separate
    `signal: notebooklm_activity`
  - extended `scripts/run_day_notebooklm_auto.sh` to emit raw/normalized
    interaction outputs without feeding them into `run_day.sh`
  - added `SensibLaw/src/reporting/notebooklm_activity.py` and
    `scripts/query_notebooklm_activity.py`
  - added preview `TextUnit` projection and focused tests
  - kept the lane explicitly out of dashboard/session accounting
