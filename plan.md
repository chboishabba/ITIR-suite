# Implementation Plan

## Milestone X: Latent-State and Cross-System Mapping Contract (in progress)
1. Normalize the canonical planning state around the current doctrine:
   - `spec.md`
   - `architecture.md`
   - `plan.md`
   - `status.json`
   - `devlog.md`
2. Freeze the single-system latent-state contract:
   - `L(P)` is downstream of promotion
   - reconstruction and provenance rules are explicit
   - latent outputs cannot act as hidden truth
3. DONE: Freeze the cross-system extension:
   - local promoted truth sets `P_i`
   - checked mapping layer `Phi`
   - explicit statuses:
     `exact`, `partial`, `incompatible`, `undefined`
4. Define the first bounded prototype contract:
   - DONE: two systems only
   - DONE: one small promoted relation family
   - DONE: one checked mapping table
   - DONE: one mismatch report
   - DONE: freeze the bounded executable `Phi` transport schema at:
     `SensibLaw/schemas/sl.cross_system_phi.contract.v1.schema.yaml`
   - DONE: implement one real promoted-record prototype over existing emitted
     semantic reports:
     `SensibLaw/src/cross_system_phi.py`
   - DONE: make mismatch review workflow and provenance-preservation rule
     explicit in the executable contract
   - DONE: add regression coverage over real AU/GWB promoted reports:
     `SensibLaw/tests/test_cross_system_phi_prototype.py`
5. Next formalization after the bounded real prototype:
   - DONE: add `Phi_meta` admissibility/type gate above `Phi_ij`
   - DONE: widen witness structure over real promoted records and thread it
     into emitted mapping explanations
   - DONE: formalize the first typed `L(P)` node/edge/constraint slice over
     promoted relations and connect it back to emitted `Phi` mapping refs
   - explain any future `v2` schema relative to the current bounded `v1`
     transport contract

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
2. DONE: Add deterministic lexical-noise guard fixtures (`A7`) for stopwords and citation-noise flooding.

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
1. DONE: Ratify the whitepaper-derived planning note and explicit
   Observation/Claim contract in:
   `docs/planning/sl_observation_claim_contract_20260327.md`
   `docs/planning/sl_whitepaper_followthrough_20260314.md`.
2. DONE: Define explicit `Observation` / `Claim` / evidence-link contracts before any
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
   - deterministic event-candidate assembly over observations
   - explicit abstention/status handling and clean structural-identity vs run
     metadata separation
   - chronology over captured facts/statements
   - contestable fact/claim handling
   - review/curation surfaces
   - external-reference/linkage support
5. Keep Milestone R as the next semantic/reasoning followthrough after the
   parity substrate is credible.
6. Treat existing projection-style observation types as adjacent downstream
   views, not substitutes for the canonical fact-intake observation seam.
7. Use the expanded role stories in `docs/user_stories.md` plus:
   - `docs/planning/mary_parity_user_story_acceptance_matrix_20260315.md`
   - `docs/planning/mary_parity_gap_analysis_20260315.md`
   as the checkpoint discipline for the next implementation loop.
8. Prioritize the resumed loop as:
   - richer review queue reasons and contested/chronology triage
   - source workflow run -> fact-review run reopen ergonomics
   - widened legal/procedural observation visibility
9. Add the next Mary-parity operator slice:
   - story-driven acceptance reports over persisted fact-review runs
   - source-label-centric listing/reopen helpers
   - bounded operator views for intake/chronology/procedure/contestation
   - a thin read-only `itir-svelte` fact-review workbench over the same
     persisted contract
10. Expand the Mary-parity fixture/acceptance family beyond transcript/AU-only
    pressure:
   - contested Wikipedia/Wikidata moderation and public-figure legality lanes
   - family-law / child-sensitive / cross-side handoff lanes
   - medical-negligence / professional-discipline overlap lanes
   - personal-to-professional handoff and anti-false-coherence lanes
11. Keep Wave 1 legal parity explicitly gated by:
   - the canonical fixture manifest
   - the batch acceptance runner over transcript/AU persisted runs
   - pass/partial/fail backlog triage against `SL-US-09` to `SL-US-14`
12. Use the next implementation loop to close the highest-friction Wave 1 gaps
    surfaced by that batch report before moving to Wave 2 ITIR parity.
13. Add a broad random-page article-ingest harness over revision-locked
    Wikipedia samples:
   - treat article-wide actor/action/object extraction as the parent quality
     surface
   - keep lexer/reducer coverage as companion diagnostics only
   - keep timeline-candidate plus AAO readiness as a derived chronology
     surface, not the whole lane
   - start bounded link expansion at one hop only with replayable manifests
   - treat the next follow-on as bridging those general-text outputs into the
     canonical observation/event sender rather than inventing a second store
14. Realign the Wikipedia lane around one canonical wiki-state compiler:
   - make article ingest, timeline, and revision three projections over the
     same deterministic state
   - keep `timeline` as the named chronology surface while allowing ordered
     undated events with explicit anchor status
   - make revision moderation state-first so disputed facts/aspects/claims are
     visible directly to reviewers

## Milestone T: Mary-Parity Acceptance Expansion (completed)
1. Greened explicit acceptance gates for:
   - `wave1_legal`
   - `wave2_balanced`
   - `wave3_trauma_advocacy`
   - `wave3_public_knowledge`
   - `wave4_family_law`
   - `wave4_medical_regulatory`
   - `wave5_handoff_false_coherence`
2. Added later-wave fixture families for:
   - contested wiki / Wikidata / public-knowledge moderation
   - family-law / child-sensitive / cross-side handoff
   - medical / regulatory review
   - personal-to-professional handoff
   - anti-false-coherence / anti-AI-psychosis pressure
3. Broadened Wave 5 beyond synthetic-only coverage with repo-curated real
   transcript fixtures.

## Milestone U: Post-Gate Parity Audit (planned)
1. Use `docs/planning/mary_parity_status_audit_20260315.md` as the next
   Mary-parity planning baseline.
2. Broaden real-fixture depth for waves that are still synthetic-heavy.
3. Audit workbench/export ergonomics across the currently green wave set.
4. Only then decide whether the next move is:
   - another real-fixture expansion
   - operator/workbench polish
   - or a genuinely new family.

## Milestone W: JMD Boundary Triage (planned)
1. Use `docs/planning/jmd_triage_roadmap_20260320.md` as the canonical triage
   note for all JMD-related planning references.
2. Keep the JMD/ERDFA shard/task lane documented as future external-surface
   awareness only until a pinned schema and concrete adapter target exist.
3. Treat the JMD object graph -> SL corpus graph bridge as the only near-term
   JMD implementation candidate.
4. Close the read-only bridge contract around:
   - fixture-backed ingest payloads
   - reversible anchor/group identities
   - advisory overlay payloads
   - reserved provenance-bundle and metric-commitment fields
5. Defer Casey-governed promotion paths and StatiBaker receipt details until the
   read-only bridge invariants are explicit.

## Milestone V: Fact-Intake Semantic Normalization (completed)
1. Added additive semantic sidecar storage over `fact_intake`:
   - vocab tables
   - entity class assertions
   - entity relations
   - policy outcomes
   - semantic refresh receipts
2. Kept raw fact/source/excerpt/statement/observation/event tables as the
   canonical observed layer.
3. Dual-wrote semantic materialization during `persist_fact_intake_payload(...)`
   and added a bounded `backfill_fact_semantics.py` script for legacy runs.
4. Cut review summary/workbench projections over to normalized semantic rows
   with fallback for non-materialized runs.

## Milestone W: Wikidata Hotspot Benchmark Lane (planned)
1. Use `docs/planning/wikidata_hotspot_benchmark_lane_20260325.md` as the
   planning source for the benchmark-facing extension.
2. DONE: freeze the hotspot taxonomy and pack contract in:
   - `docs/planning/wikidata_hotspot_pack_contract_20260325.md`
   - `docs/planning/wikidata_hotspot_pilot_pack_v1.manifest.json`
3. DONE: keep the first pilot pack bounded to five hotspot entries:
   - one mixed-order fixture-backed pack
   - one `P279` SCC fixture-backed pack
   - one qualifier-drift revision-pair pack
   - one finance entity-kind-collapse fixture-backed pack
   - one software entity-kind-collapse fixture-backed pack
4. DONE: preserve provenance from source slice/revision/page review -> hotspot family
   -> generated cluster family.
5. DONE: implement the first minimal cluster generator path:
   - module:
     `SensibLaw/src/ontology/wikidata_hotspot.py`
   - CLI:
     `sensiblaw wikidata hotspot-generate-clusters`
   - tests:
     `SensibLaw/tests/test_wikidata_hotspot.py`,
     `SensibLaw/tests/test_wikidata_hotspot_cli.py`
6. Next:
   - expand score-file fixtures across more hotspot families
   - decide whether a later adapter-command runner belongs in `v2`
   - keep comparison/reporting stable as more packs are added
