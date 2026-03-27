# Devlog

## 2026-03-28
- Added `docs/planning/orchestrator_control_plane_20260328.md` to record the
  current orchestration control-plane state for this repo.
- Locked the current boundary:
  - multi-runner orchestration in one repo is supported via runner-local
    namespaced status/log files
  - child handoffs should begin from a compact ZKP frame plus runtime
    model-allocation block
  - master-orchestrator -> sub-orchestrator hierarchy is not yet first-class
- Updated `TODO.md`, `COMPACTIFIED_CONTEXT.md`, and `CHANGELOG.md` so that
  boundary is durable repo state rather than chat-only context.
- No repo-owned code changed in this pass; the relevant behavior already lives
  in shared Codex skill files under `/home/c/.codex/skills`.
- Audited the largest repo-owned code files to choose the next bounded
  refactor/normalization slices:
  - added planning note:
    `docs/planning/largest_file_refactor_roadmap_20260328.md`
  - recorded the next high-value decomposition targets:
    - `scripts/chat_context_resolver.py`
    - `itir-svelte` wiki timeline server/route family
    - Zelph/HF/shared-shard builders
    - `itir_jmd_bridge/runtime.py`
    - `casey-git-clone` CLI/runtime store
- Locked the rule that large-file cleanup should prioritize:
  - reusable core extraction
  - thinner route/CLI entrypoints
  - removal of accidental corpus/tool/provider-specific naming from
    general-use suite contracts
- Tightened the workflow for this lane:
  - before triaging any specific oversized file, write a bounded file-local
    refactor brief covering reusable core, specialized remainder, split
    boundary, and acceptance checks
- No code behavior changed in this pass; this was a docs/TODO/context audit.
- Implemented the first bounded typed `L(P)` runtime slice over promoted
  relations:
  - added `SensibLaw/src/latent_promoted_graph.py`
  - added executable schema:
    `SensibLaw/schemas/sl.latent_promoted_graph.v1.schema.yaml`
  - added focused regression coverage:
    `SensibLaw/tests/test_latent_promoted_graph.py`
- The new latent graph builder stays below the truth gate:
  - it operates only on already-promoted records
  - it emits typed nodes/edges/constraints plus record-indexed provenance
  - it derives bounded motif nodes from repeated promoted relation signatures
- Integrated that graph slice back into the current `Phi` runtime:
  - `SensibLaw/src/cross_system_phi.py` now builds one latent graph per
    system from the same promoted records feeding `Phi_meta -> Phi_ij`
  - emitted `sl.cross_system_phi.contract.v1` payloads now include:
    - `latent_graphs` summaries
    - `mapping_explanation.latent_graph_refs`
- Revalidated with the workspace venv:
  - `/home/c/Documents/code/ITIR-suite/.venv/bin/python -m pytest -q SensibLaw/tests/test_au_semantic.py SensibLaw/tests/test_gwb_semantic.py SensibLaw/tests/test_latent_promoted_graph.py SensibLaw/tests/test_cross_system_phi_meta.py SensibLaw/tests/test_cross_system_phi_schema.py SensibLaw/tests/test_cross_system_phi_prototype.py`
- Enriched the bounded `Phi_meta` path with explicit witness payloads:
  - `type_alignment`
  - `role_alignments`
  - `authority_alignment`
  - `constraint_check`
  - `scope_check`
- Extended the `Phi` prototype output so mappings now emit:
  - `meta_validation.witness`
  - `mapping_explanation`
  instead of relying on a bare compatibility rationale alone
- Updated the executable `sl.cross_system_phi.contract.v1` schema and minimal
  example to match the richer explanation surface.
- Revalidated with the workspace venv:
  - `/home/c/Documents/code/ITIR-suite/.venv/bin/python -m pytest -q SensibLaw/tests/test_au_semantic.py SensibLaw/tests/test_gwb_semantic.py SensibLaw/tests/test_cross_system_phi_meta.py SensibLaw/tests/test_cross_system_phi_schema.py SensibLaw/tests/test_cross_system_phi_prototype.py`
- Added the bounded `Phi_meta` admissibility layer above `Phi_ij`:
  - schema:
    `SensibLaw/schemas/sl.cross_system_phi_meta.v1.schema.yaml`
  - runtime:
    `SensibLaw/src/cross_system_phi_meta.py`
  - focused validation:
    `SensibLaw/tests/test_cross_system_phi_meta.py`
- Extended the existing `Phi` prototype to become meta-gated instead of pure
  structural matching:
  - `SensibLaw/src/cross_system_phi.py` now evaluates candidate pairs through
    `Phi_meta` first
  - blocked pairs are surfaced explicitly in
    `meta_validation_report.blocked_pairs`
  - admitted mappings now carry `meta_validation` receipts in the emitted
    `sl.cross_system_phi.contract.v1` payload
- Validated with the workspace venv:
  - `/home/c/Documents/code/ITIR-suite/.venv/bin/python -m pytest -q SensibLaw/tests/test_au_semantic.py SensibLaw/tests/test_gwb_semantic.py SensibLaw/tests/test_cross_system_phi_meta.py SensibLaw/tests/test_cross_system_phi_schema.py SensibLaw/tests/test_cross_system_phi_prototype.py`
- Expanded the bounded `Phi` package from schema-only into a real promoted-record
  prototype:
  - added runtime:
    `SensibLaw/src/cross_system_phi.py`
  - extended the executable contract with:
    - explicit `provenance_rule`
    - explicit `mismatch_report.workflow`
    - anchored `provenance_index`
  - kept the bounded status grammar unchanged:
    `exact`, `partial`, `incompatible`, `undefined`
- The new prototype now consumes real promoted relations emitted by existing
  semantic pipelines instead of synthetic placeholder refs:
  - AU semantic promoted relations
  - GWB semantic promoted relations
  - bounded matching over shared promoted-record shape, rule family, and
    mismatch diagnostics
- Added focused regression coverage:
  - `SensibLaw/tests/test_cross_system_phi_prototype.py`
  - existing schema test retained in:
    `SensibLaw/tests/test_cross_system_phi_schema.py`
- Validated with the workspace venv:
  - `/home/c/Documents/code/ITIR-suite/.venv/bin/python -m pytest -q SensibLaw/tests/test_cross_system_phi_schema.py SensibLaw/tests/test_cross_system_phi_prototype.py`
- Added the next formalization note above the bounded executable `Phi` schema:
  - `docs/planning/phi_mapping_and_latent_graph_schema_20260328.md`
- Locked the key compatibility rule:
  - current executable `v1` schema remains the bounded transport grammar with
    `exact|partial|incompatible|undefined`
  - richer relation kinds (`exact`, `refinement`, `abstraction`, `analogue`,
    `conflict`, `none`) are now documented as the intended next semantic layer,
    not falsely claimed as already shipped
- Recorded the typed latent graph target for `L(P)`:
  - node schema
  - edge schema
  - first-class constraint schema
  - explicit typing relation and provenance requirements
- Repointed `Milestone X` checklist/status toward the next formalization step:
  richer `Phi` semantics and typed latent graph design over the existing
  bounded executable contract.
- Implemented the first machine-readable `Phi` mapping contract artifact for
  `Milestone X`:
  - schema:
    `SensibLaw/schemas/sl.cross_system_phi.contract.v1.schema.yaml`
  - minimal example payload:
    `SensibLaw/examples/cross_system_phi_minimal.json`
  - focused regression coverage:
    `SensibLaw/tests/test_cross_system_phi_schema.py`
- The new contract freezes the bounded cross-system status grammar in an
  executable schema:
  - allowed mapping outcomes are now explicitly validated as:
    `exact`, `partial`, `incompatible`, `undefined`
  - `undefined` mappings must carry `target_ref: null`
  - the prototype contract is bounded to two systems, one motif family, one
    checked mapping table, and one mismatch report surface
- Validated with the workspace venv:
  - `/home/c/Documents/code/ITIR-suite/.venv/bin/python -m pytest -q SensibLaw/tests/test_cross_system_phi_schema.py`
- Reframed the canonical orchestrator state around the current repo doctrine
  instead of the stale workbench milestone files.
- Replaced the root `spec.md` with the bounded latent-state / cross-system
  mapping spec:
  - single-system latent state as `L(P)` over promoted truth
  - cross-system state as local promoted sets `P_i` plus checked `Phi`
    mappings
  - first prototype boundary:
    two systems, one promoted motif family, one checked mapping table, one
    mismatch report
- Replaced the root `architecture.md` with the matching architecture:
  - promotion remains the only truth gate
  - latent state stays downstream of promotion
  - global alignment is mapping-based rather than universal-ontology-based
- Added `Milestone X` to `plan.md` so the next durable repo milestone is the
  latent-state / `Phi` contract package rather than the stale workbench scope.
- Updated `status.json` so the autonomous orchestrator now points at
  `Milestone X` and the cross-system mapping checklist instead of the old
  `Milestone R` tracking.

## 2026-03-25

## 2026-03-27
- Ratified Milestone R phase-1 contract language for SL observation/case
  construction by adding:
  - `docs/planning/sl_observation_claim_contract_20260327.md`
- Linked the ratified contract back into `sl_whitepaper_followthrough_20260314.md`.
- Advanced `plan.md` checklist state to reflect completion of `R.1`
  (`R.1 Contract ratification` -> `R.2 Contract definition` in status tracking).
- Completed R.2 contract definition by adding the machine-readable contract artifact:
  - `SensibLaw/schemas/sl.observation_claim.contract.v1.schema.yaml`
  - this file now gives explicit field/enum contracts for
    `Observation`, `Claim`, and deterministic `evidence_link`/transition-receipt
    payloads.
- Split the disjointness candidate scanner into explicit backends:
  - `wdqs` for live subclass/instance discovery
  - `zelph` for local instance-only discovery from explicit pair seeds
- Added local seed/config support for the new `zelph` scan mode:
  - `SensibLaw/data/ontology/wikidata_disjointness_pair_seed_v1.json`
- Added callable/end-to-end regression coverage for the `zelph` scan path:
  - in-process backend test and CLI smoke in
    `SensibLaw/tests/test_wikidata_disjointness_scan.py`
- Validated the backend split with the repo venv:
  - `.venv/bin/python -m pytest -q SensibLaw/tests/test_wikidata_disjointness.py SensibLaw/tests/test_wikidata_disjointness_cli.py SensibLaw/tests/test_wikidata_disjointness_scan.py`
- Added phase-2 disjointness governance and discovery surfaces:
  - callable live scan script:
    `SensibLaw/scripts/run_wikidata_disjointness_candidate_scan.py`
  - machine-readable disjointness case index:
    `docs/planning/wikidata_disjointness_case_index_v1.json`
  - machine-readable page-review candidate index:
    `docs/planning/wikidata_page_review_candidate_index_v1.json`
- Added a second real Wikidata-backed disjointness pack with an actual
  contradiction:
  - `SensibLaw/tests/fixtures/wikidata/disjointness_p2738_fixed_construction_real_pack_v1/slice.json`
- Added an additional real live-scan-backed instance contradiction pack:
  - `SensibLaw/tests/fixtures/wikidata/disjointness_p2738_working_fluid_real_pack_v1/slice.json`
- Tightened disjointness culprit semantics:
  - culprit classes now emit downstream subclass/instance impact counts
  - instance rows now emit `explained_by_culprit_class_qid`
- Validated the updated disjointness/hotspot suites with the repo venv:
  - `.venv/bin/python -m pytest -q SensibLaw/tests/test_wikidata_disjointness.py SensibLaw/tests/test_wikidata_disjointness_cli.py SensibLaw/tests/test_wikidata_disjointness_scan.py`
  - `.venv/bin/python -m pytest -q SensibLaw/tests/test_wikidata_hotspot.py SensibLaw/tests/test_wikidata_hotspot_cli.py SensibLaw/tests/test_wikidata_hotspot_eval.py`
- Live scan smoke now fails cleanly when network/DNS is unavailable instead of
  crashing through a raw traceback.
- With network enabled, the live instance scan now returns real candidates and
  surfaced a very clean `fluid -> {gas, liquid} -> working fluid` contradiction.

## 2026-03-26
- Started Milestone N assumption-stress follow-through by implementing `A7` lexical
  noise guards:
  - added deterministic actor-guard fixtures for stopword-only, number-heavy,
    and citation-noise preambles:
    - `SensibLaw/tests/fixtures/actors/lexical_noise_stopwords.txt`
    - `SensibLaw/tests/fixtures/actors/lexical_noise_numbers.txt`
    - `SensibLaw/tests/fixtures/actors/lexical_noise_citations.txt`
  - updated `SensibLaw/src/obligations.py` to suppress false actor anchors when
    pre-modality token spans are noise-only
  - added fixture-backed assertions in
    `SensibLaw/tests/test_obligations_detection.py`
  - moved `A7` in `docs/planning/assumption_controls_registry.json` from
    waived -> implemented with test references
  - reduced `A7` waiver scope in
    `docs/planning/waivers/assumption_controls_waiver_20260311.md`
  - validated with:
    - `SensibLaw/tests/test_obligations_detection.py`
    - `SensibLaw/tests/test_assumption_controls_fail_closed.py`

## 2026-03-25
- Activated the Wikidata promotion ladder as repo policy in the hotspot lane:
  - hotspot manifest now distinguishes:
    - `status` for backing/provenance
    - `promotion_status` for readiness
    - `hold_reason` for non-promoted entries
  - current pilot-manifest classifications are now explicit:
    - `mixed_order_live_pack_v1`: `promoted`
    - `p279_scc_live_pack_v1`: `promoted`
    - `qualifier_drift_p166_live_pack_v1`: `promoted`
    - `finance_entity_kind_collapse_pack_v0`: `promotable`
    - `software_entity_kind_collapse_pack_v0`: `promotable`
- Froze the disjointness-side rule:
  - use the same readiness language in docs/governance
  - keep `wikidata_disjointness_report/v1` observational and free of promotion
    metadata
- Validated the updated hotspot/disjointness contracts with the repo venv:
  - `.venv/bin/python -m pytest -q SensibLaw/tests/test_wikidata_hotspot.py SensibLaw/tests/test_wikidata_hotspot_cli.py SensibLaw/tests/test_wikidata_hotspot_eval.py`
  - `.venv/bin/python -m pytest -q SensibLaw/tests/test_wikidata_disjointness.py SensibLaw/tests/test_wikidata_disjointness_cli.py`

## 2026-03-25
- Implemented the first bounded standalone `P2738` disjointness lane:
  - module: `SensibLaw/src/ontology/wikidata_disjointness.py`
  - CLI: `sensiblaw wikidata disjointness-report`
  - fixture pack:
    `SensibLaw/tests/fixtures/wikidata/disjointness_p2738_pilot_pack_v1/slice.json`
  - tests:
    - `SensibLaw/tests/test_wikidata_disjointness.py`
    - `SensibLaw/tests/test_wikidata_disjointness_cli.py`
- The new deterministic report now covers:
  - pair extraction from `P2738` with `P11260`
  - subclass violations over local `P279` closure
  - instance violations over local `P31`/`P279` closure
  - bounded culprit class/item surfacing
- Validated the new lane and revalidated the hotspot lane with the repo venv:
  - `.venv/bin/python -m pytest -q SensibLaw/tests/test_wikidata_disjointness.py SensibLaw/tests/test_wikidata_disjointness_cli.py`
  - `.venv/bin/python -m pytest -q SensibLaw/tests/test_wikidata_hotspot.py SensibLaw/tests/test_wikidata_hotspot_eval.py SensibLaw/tests/test_wikidata_hotspot_cli.py`
- Added one real Wikidata-backed baseline disjointness pack beside the
  synthetic pilot:
  - `SensibLaw/tests/fixtures/wikidata/disjointness_p2738_nucleon_real_pack_v1/slice.json`
- Froze the report contract and lane decision in:
  - `docs/planning/wikidata_disjointness_report_contract_v1_20260325.md`
  - current decision: disjointness remains a sibling lane for now, not a
    hotspot family

## 2026-03-25
- Added two planning notes to make the current comparison with Rosario and
  Ege/Peter explicit and to define the next parity move:
  - `docs/planning/wikidata_parity_gap_note_rosario_ege_20260325.md`
  - `docs/planning/wikidata_p2738_disjointness_lane_20260325.md`
- Current repo position is now documented more clearly:
  - Rosario parity is meaningful but partial on the benchmark/scorer side
  - Ege/Peter parity is still low on concrete method until a dedicated `P2738`
    disjointness lane exists
- Defined the next bounded parity target as a standalone deterministic
  disjointness lane:
  pair extraction from `P2738`/`P11260`, subclass violations, instance
  violations, culprit mining, and one reviewer-facing report contract.

## 2026-03-25
- Added `docs/planning/wikidata_hotspot_eval_adapter_boundary_v2_20260325.md`
  to freeze the post-`v1` policy:
  keep live execution outside `SensibLaw` by default, and if a `v2` convenience
  layer is ever added, allow only a thin adapter-command wrapper over the
  existing response-bundle schema.

## 2026-03-25
- Added canned evaluator response-bundle fixtures so the hotspot evaluator no
  longer relies only on inline synthetic positive-path payloads:
  - `SensibLaw/tests/fixtures/wikidata/hotspot_eval_v1/qualifier_drift_p166_live_pack_v1_responses_consistent.json`
  - `SensibLaw/tests/fixtures/wikidata/hotspot_eval_v1/software_entity_kind_collapse_pack_v0_responses_inconsistent.json`
  - `SensibLaw/tests/fixtures/wikidata/hotspot_eval_v1/finance_entity_kind_collapse_pack_v0_responses_incomplete.json`
- Switched evaluator regression coverage to those canned bundles and kept the
  inline payloads only for invalid-shape validation cases.
- Revalidated the hotspot lane with the repo venv:
  - `.venv/bin/python -m pytest -q SensibLaw/tests/test_wikidata_hotspot.py SensibLaw/tests/test_wikidata_hotspot_eval.py SensibLaw/tests/test_wikidata_hotspot_cli.py`
  - `.venv/bin/python -m pytest -q SensibLaw/tests/test_wikidata_projection.py -k "live_fixture_emits_mixed_order_and_nonzero_eii or qualifier_drift_fixture_emits_property_set_change"`

## 2026-03-25
- Promoted the hotspot pilot pack to a ratified manifest:
  `docs/planning/wikidata_hotspot_pilot_pack_v1.manifest.json`
  while keeping the old `v0` manifest as historical planning context.
- Promoted the emitted hotspot cluster-pack schema from the earlier draft to
  `wikidata_hotspot_cluster_pack/v1` and gave each generated question a stable
  `question_id`.
- Added the first score-only evaluator surface:
  - `SensibLaw/src/ontology/wikidata_hotspot_eval.py`
  - `sensiblaw wikidata hotspot-eval`
  - evaluator contract is normalized response-bundle in, deterministic JSON
    report out; no live provider execution in `v1`
- Expanded hotspot tests so the lane now covers:
  - all-manifest pack generation
  - evaluator classification/validation
  - CLI smoke for `hotspot-eval`
- Updated planning/status files so they no longer describe the hotspot lane as
  pre-implementation:
  - `docs/planning/wikidata_hotspot_benchmark_lane_20260325.md`
  - `docs/planning/wikidata_hotspot_pack_contract_20260325.md`
  - `docs/planning/README.md`
  - `TODO.md`
  - `plan.md`
  - `COMPACTIFIED_CONTEXT.md`
- Validated the new slice with the repo venv:
  - `.venv/bin/python -m pytest -q SensibLaw/tests/test_wikidata_hotspot.py SensibLaw/tests/test_wikidata_hotspot_eval.py SensibLaw/tests/test_wikidata_hotspot_cli.py`
  - `.venv/bin/python -m pytest -q SensibLaw/tests/test_wikidata_projection.py -k "live_fixture_emits_mixed_order_and_nonzero_eii or qualifier_drift_fixture_emits_property_set_change"`

## 2026-03-25
- Reviewed IBM's paper `2405.20163v1_rosario.pdf` on LLM knowledge consistency
  over Wikidata-derived ontologies and extracted the repo-relevant design
  takeaway:
  - their cluster generation approach is useful
  - their flattening of `P31` and `P279` into a generic `subConceptOf` relation
    is exactly where this repo can do better by preserving structural pathology
    provenance
- Added a new planning note:
  `docs/planning/wikidata_hotspot_benchmark_lane_20260325.md`
  which defines a bounded benchmark lane built from hotspot families rather
  than generic ontology flattening.
- Added the next planning/spec artifacts for the same lane:
  - `docs/planning/wikidata_hotspot_pack_contract_20260325.md`
  - `docs/planning/wikidata_hotspot_pilot_pack_v0.manifest.json`
  - these freeze the draft taxonomy/schema, map the first five candidate packs,
    and sketch the generator/evaluator contracts before code exists
- Updated:
  - `.gitignore`
  - `TODO.md`
  - `COMPACTIFIED_CONTEXT.md`
  - `plan.md`
  - `docs/planning/README.md`
  - `docs/planning/wikidata_zelph_single_handoff_20260325.md`
  - `SensibLaw/docs/wikidata_working_group_status.md`
  so the repo now states explicitly that the Wikidata diagnostics are
  domain-agnostic and can catch entity-kind collapse across software/project as
  well as finance/property examples.
- Tightened the hotspot lane from "good planning idea" into an explicit
  milestone roadmap:
  - taxonomy + pack contract first
  - pilot-pack ratification second
  - compare/report contract third
  - deterministic pilot tooling fourth
  - generator/evaluator work only after those gates are stable
- Continued the same lane into the first minimal implementation slice:
  - promoted the finance/product-service-category and software/project/artifact
    entity-kind-collapse examples into local slice-backed fixtures:
    - `SensibLaw/tests/fixtures/wikidata/finance_entity_kind_collapse_pack_v0/slice.json`
    - `SensibLaw/tests/fixtures/wikidata/software_entity_kind_collapse_pack_v0/slice.json`
  - added `SensibLaw/src/ontology/wikidata_hotspot.py`
  - added `sensiblaw wikidata hotspot-generate-clusters`
  - added focused tests:
    - `SensibLaw/tests/test_wikidata_hotspot.py`
    - `SensibLaw/tests/test_wikidata_hotspot_cli.py`
  - validated the new slice with the repo venv:
    - `.venv/bin/python -m pytest -q SensibLaw/tests/test_wikidata_hotspot.py SensibLaw/tests/test_wikidata_hotspot_cli.py`
    - `.venv/bin/python -m pytest -q SensibLaw/tests/test_wikidata_projection.py -k "live_fixture_emits_mixed_order_and_nonzero_eii or qualifier_drift_fixture_emits_property_set_change"`

## 2026-03-25
- Added `docs/planning/wikidata_zelph_single_handoff_20260325.md` as the new
  canonical first-link handoff for the evening meetings with the Wikidata
  Ontology Working Group and the Zelph developer.
- The new note is intentionally plain-language and records:
  - exact current Wikidata results:
    bounded structural diagnostics, pinned qualifier-drift cases, and parthood
    packs
  - exact current Zelph results:
    deterministic bridge proof, checked GWB/AU handoffs, and corpus-level
    companion scorecards
  - explicit non-claims so the note does not oversell completeness or
    integration depth
  - the concrete value proposition for each audience
- Repointed the main doc entrypoints so the repo tells one consistent story:
  - `README.md`
  - `docs/planning/zelph_handoff_index_20260324.md`
  - `docs/planning/zelph_external_handoff_20260320.md`
  - `SensibLaw/docs/wikidata_working_group_status.md`
  - `SensibLaw/README.md`
  - `TODO.md`
  - `COMPACTIFIED_CONTEXT.md`
- No code or runtime behavior changed; this pass was documentation/context
  alignment only.

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

## 2026-03-20
- Added `docs/planning/zelph_external_handoff_20260320.md` as a Stefan-facing
  technical brief that explains:
  - SensibLaw's upstream role at the text-to-structure boundary
  - the current tiny deterministic SL -> Zelph bridge posture
  - repo-backed demo evidence in `SensibLaw/sl_zelph_demo/`
  - the fact-semantic benchmark as supporting context rather than a blanket
    external-sharing artifact
- Updated `docs/planning/README.md`, `TODO.md`, and `COMPACTIFIED_CONTEXT.md`
  so the external-collaboration note is indexed and the sharing/sanitization
  followthrough is explicit.
- No code changes were needed for this turn; the work was docs/context only.

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
