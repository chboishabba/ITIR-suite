# Devlog

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
  - full `pytest` lane for that file is blocked locally by missing `pdfminer`
    via shared `tests/conftest.py`; ran direct smoke execution against
    `demo/narrative/friendlyjordies_chat_arguments.json` with successful
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
