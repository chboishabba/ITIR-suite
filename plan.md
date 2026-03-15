# Implementation Plan

## Milestone A: Shared state + page wiring (completed)
1. Create shared review-state helper.
2. Wire helper into thread/narrative/wiki pages.
3. Update route UI labels to expose state reason clearly.

## Milestone B: Narrative compare interaction model (completed)
1. Build selectable review-row model (shared/disputed/source-only/corroboration/abstention).
2. Add inspector tabs and explicit graph-open action.
3. Add bounded graph payload derived from selected row.

## Milestone C: Regression coverage alignment (completed)
1. Update graph UI regression assertions to new labels/flow.
2. Add checks for review-state helper wiring.
3. Add checks for narrative compare inspector + scoped graph sections.

## Milestone D: Selection bridge consolidation (completed)
1. Introduce shared selection-bridge helper.
2. Wire thread, narrative compare, and contested wiki to selection bridge.
3. Keep route-local behavior bounded while sharing event semantics.

## Milestone E: State telemetry + posture grammar (completed)
1. Emit `stateReason` from route server loaders for thread/narrative/wiki.
2. Consume server `stateReason` in route pages with local fallback only.
3. Add explicit posture chips in narrative compare rows and inspector.
4. Add regression guard ensuring no JSON/localStorage UI-state persistence in these pages.

## Milestone F: Docs/TODO/changelog sync (completed)
1. Update top-level TODO statuses for recent workbench followthrough.
2. Record behavior changes in `itir-svelte/CHANGELOG.md`.
3. Reconcile project-memory files with implemented state.

## Milestone G: P0 tokenizer + lexeme closeout refresh (completed)
1. Re-run deterministic tokenizer/lexeme migration tests in project venv.
2. Update tokenizer migration planning note with fresh verification evidence.
3. Mark `[P0]` tokenizer migration and lexeme-layer TODOs done.
4. Record verification refresh in `SensibLaw/CHANGELOG.md`.

## Milestone H: P1 SL engine/profile followthrough v1 (completed)
1. Ratify profile contracts/lint docs from draft to explicit allow/deny sets.
2. Implement profile admissibility+lints (`sl_profile`, `sb_profile`, `infra_profile`).
3. Add cross-profile safety tests and verify in project venv.
4. Mark TODO item done and record changelog entry.

## Milestone I: Next achievable sprint (completed)
1. Tool Use Summary hydration fixes:
   - DONE: diagnosed Shell/hour and Input/hour coupling in SB daily reducer.
   - DONE: implemented reducer-layer fix (agent `exec_command` and `request_user_input` hour bins).
   - DONE: added NotebookLM event-path coverage into the tool-use stream (`notebooklm_meta_event` family + hour bins).
2. DONE: add explicit regression tests for shell/input counter hydration.

## Milestone J: OpenRecall query/read-model interface (completed)
1. Update OpenRecall planning/TODO/context docs to define the neutral
   query/read-model seam over imported captures.
2. Add query-first helpers for:
   - latest import runs
   - capture counts by app/title/date
   - screenshot coverage
   - recent filtered capture rows
3. Add a bounded CLI around those helpers without introducing GUI-first
   coupling.
4. Add focused tests and record the shipped behavior in the changelog.

## Milestone K: NotebookLM bounded live smoke (completed)
1. Define the intended bounded live smoke in docs/context/TODOs.
2. Add a repeatable runner over:
   - `auth check --test`
   - readonly notebook list/get
   - one bounded readonly chat ask
   - source listing
3. Run the smoke against live auth after token refresh/network approval.
4. Record outcomes and any auth/network blockers without widening into the full
   generation-heavy E2E suite.

## Milestone K: Assumption Stress Controls Slice (completed)
1. Implement `A8` fail-closed CI stubs with explicit waiver-receipt path.
2. Implement `A1/Q1` axis hierarchy fixture coverage (collision + deterministic 2D fallback).
3. Update TODO/changelog/project-memory artifacts with verification output.

## Milestone L: Assumption Stress A2/Q2 Fold Neutrality (completed)
1. Implement SB fold-policy receipt surface with explicit machine flags.
2. Add explicit fold loss-profile declaration for the minimal fold path.
3. Add anti-nudge red-team tests for fold-policy/loss-profile outputs.

## Milestone M: Next Assumption Stress Slice (completed)
1. Implement `A3` claim-link provenance quality gates for receipts-backed artifacts.

## Milestone N: Next Assumption Stress Slice (pending)
1. Implement `A4` plural-law non-reduction preservation fixtures (`Q7`).
2. Add deterministic lexical-noise guard fixtures (`A7`) for stopwords and citation-noise flooding.

## Milestone O: NotebookLM metadata/review parity (completed)
1. Update docs/TODO/context to freeze NotebookLM as metadata-first until a
   separate activity contract exists.
2. Add a neutral NotebookLM observer report/query seam over
   `runs/<date>/logs/notes/*.jsonl`.
3. Add NotebookLM source-summary `TextUnit` projection for downstream
   structure/semantic reuse.
4. Add focused tests and a bounded query CLI.

## Milestone P: NotebookLM interaction capture (completed)
1. Document the additive interaction contract over history + notes.
2. Add bounded raw capture for `conversation_observed` and `note_observed`.
3. Normalize into a separate `notebooklm_activity` signal.
4. Add query/read-model helpers plus preview `TextUnit` projection.
5. Keep the lane out of dashboard activity/session accounting for now.

## Milestone Q: NotebookLM later activity/session contract (planned)
1. Decide whether future capture should use richer ask/request/result events
   instead of history-only observation.
2. Define stronger timestamp/dedupe guarantees before any dashboard parity.
3. Keep mission-lens and SB accounting deferred until those guarantees exist.

## Milestone R: SL observation + case-construction architecture pass (planned)
1. Ratify the whitepaper-derived planning note
   `docs/planning/sl_whitepaper_followthrough_20260314.md`.
2. Define explicit `Observation` / `Claim` / evidence-link contracts before any
   broader ontology growth.
3. Freeze RDF/Wikidata as a projection/export boundary over the richer SL
   event/observation model.
4. Queue temporal-law/versioning and jurisdiction as the follow-on milestone
   after the observation seam is explicit.
5. Define a typed-transition receipt surface for norm application and state
   progression.
6. Decide whether to run a bounded p-adic / ultrametric similarity prototype as
   an explanation-first retrieval experiment.

## Milestone S: Mary-Parity Fact Layer (planned)
1. Use `docs/planning/mary_parity_roadmap_20260315.md` as the near-term SL
   planning source.
2. Treat Mary Technology as the benchmark for fact-management, chronology,
   provenance, contestation, and operator-facing litigation workflow surfaces.
3. Reframe current ontology/bridge/branch-set work as support infrastructure
   for a credible fact layer rather than as the primary milestone by itself.
4. Define and implement the minimum parity substrate:
   - source/excerpt/statement capture
   - explicit text-grounded observations with a small stable predicate catalog
   - chronology over captured facts/statements
   - contestable fact/claim handling
   - review/curation surfaces
   - external-reference/linkage support
5. Keep Milestone R as the next semantic/reasoning followthrough after the
   parity substrate is credible.
6. Treat existing projection-style observation types as adjacent downstream
   views, not substitutes for the canonical fact-intake observation seam.
