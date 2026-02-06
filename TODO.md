# TODO (ITIR-suite)

## Last assessed
- 2026-02-05

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
- Install `reverse-engineered-chatgpt` dependencies into root `ITIR-suite/.venv` (missing `websockets`, `curl_cffi==0.5.9`); current pip install fails without network or local wheels.
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
