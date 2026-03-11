# Devlog

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
