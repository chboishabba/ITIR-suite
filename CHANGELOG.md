# Changelog

## Unreleased
- Refreshed online thread sync for fact-bundle and affect boundaries:
  - Refreshed three ChatGPT threads live via `robust-context-fetch`,
    including the missed `Zero Trust Ontology` UUID, and recorded the
    canonical IDs plus live-refresh status in `COMPACTIFIED_CONTEXT.md`.
  - Added
    `docs/planning/all_sources_factbundle_reconciliation_boundary_20260328.md`
    to pin the broader direction:
    current `Observation` / `Claim` work should generalize toward an
    all-sources reconciliation bundle over promoted observations/claims, not
    a Wikidata-shaped canonical ontology.
  - Added `docs/planning/sentiment_affect_noncanonical_boundary_20260328.md`
    to pin the current doctrine that sentiment/affect remains
    speaker/utterance-anchored candidate or overlay material rather than
    legal truth.
  - Updated `README.md`, `TODO.md`,
    `docs/planning/sl_observation_claim_contract_20260327.md`, and
    `docs/planning/transcript_semantic_phase_v1_20260308.md` so those
    refreshed boundaries are durable repo state rather than chat-only memory.
- Added `docs/planning/orchestrator_control_plane_20260328.md` to record the
  current shared-orchestration control-plane state for `ITIR-suite`.
- Recorded the current orchestration boundary:
  - multi-runner coordination in one repo is now supported via namespaced
    runner-local status/log files in the shared control-plane skills
  - child handoffs now start from a compact ZKP frame plus runtime
    model-allocation block
  - master-orchestrator -> sub-orchestrator hierarchy is still only supported
    by convention, not as first-class governed runtime support
- Updated `TODO.md`, `COMPACTIFIED_CONTEXT.md`, and `devlog.md` so the next
  control-plane step is explicit:
  add first-class hierarchical orchestrator support with parent/child
  registry, lane ownership, and completion/escalation reporting.
- Added `docs/planning/largest_file_refactor_roadmap_20260328.md` to inventory
  the largest repo-owned code files and pin the next high-value normalization
  slices.
- Recorded the current large-file governance rule:
  prioritize extraction where reusable suite contracts are still encoded behind
  lane-specific names such as `AAO`, Zelph/HF transport labels, or other
  historical one-surface seams.
- Tightened the roadmap workflow so file triage now requires a bounded
  file-local refactor brief before any implementation queueing starts.
- Updated `TODO.md`, `COMPACTIFIED_CONTEXT.md`, and `devlog.md` so the audit is
  durable repo state rather than an ephemeral chat decision.
- Typed latent-graph runtime slice over promoted relations:
  - Added `SensibLaw/src/latent_promoted_graph.py` and
    `SensibLaw/schemas/sl.latent_promoted_graph.v1.schema.yaml` so the repo
    now has a bounded executable `L(P)`-style graph contract over promoted
    relations rather than only planning prose.
  - Added `SensibLaw/tests/test_latent_promoted_graph.py` to validate the
    graph contract over real AU and GWB promoted semantic reports.
  - Extended `SensibLaw/src/cross_system_phi.py`,
    `SensibLaw/schemas/sl.cross_system_phi.contract.v1.schema.yaml`, and
    `SensibLaw/examples/cross_system_phi_minimal.json` so the current `Phi`
    payload now exposes latent-graph summaries and mapping-level latent graph
    refs tied to the same promoted-record provenance basis.
- `Phi` witness/explanation enrichment:
  - Extended `SensibLaw/src/cross_system_phi_meta.py` so `Phi_meta`
    validation now emits explicit witness objects for type, role, authority,
    constraint, and scope checks.
  - Extended `SensibLaw/src/cross_system_phi.py` and
    `SensibLaw/schemas/sl.cross_system_phi.contract.v1.schema.yaml` so
    admitted mappings now carry `mapping_explanation` plus structured witness
    detail rather than only a free-text rationale.
  - Updated `SensibLaw/examples/cross_system_phi_minimal.json` and tightened
    regression coverage in
    `SensibLaw/tests/test_cross_system_phi_meta.py` and
    `SensibLaw/tests/test_cross_system_phi_prototype.py`.
- `Phi_meta` admissibility gate:
  - Added `SensibLaw/schemas/sl.cross_system_phi_meta.v1.schema.yaml` and
    `SensibLaw/src/cross_system_phi_meta.py` so cross-system mapping now has a
    bounded type/authority/constraint admissibility layer above `Phi_ij`.
  - Extended `SensibLaw/src/cross_system_phi.py` and
    `SensibLaw/schemas/sl.cross_system_phi.contract.v1.schema.yaml` so the
    current real prototype emits `meta_validation` receipts for admitted
    mappings and an explicit `meta_validation_report` for blocked pairs.
  - Added regression coverage in
    `SensibLaw/tests/test_cross_system_phi_meta.py` and updated
    `SensibLaw/tests/test_cross_system_phi_prototype.py` so one
    structurally-similar-but-inadmissible pair is blocked before `Phi_ij`
    runs.
- Real promoted-record `Phi` prototype:
  - Added `SensibLaw/src/cross_system_phi.py` so the bounded
    `sl.cross_system_phi.contract.v1` package now has a real two-system
    builder over existing promoted semantic-report rows rather than only a
    schema stub.
  - Extended `SensibLaw/schemas/sl.cross_system_phi.contract.v1.schema.yaml`
    and `SensibLaw/examples/cross_system_phi_minimal.json` with:
    explicit provenance-preservation rule, provenance index, and mismatch
    workflow metadata.
  - Added `SensibLaw/tests/test_cross_system_phi_prototype.py` to validate
    the prototype against real AU and GWB promoted relations, including one
    partial mapping path, one incompatible path, and dual-anchor provenance
    guarantees.
- `Phi` relation and latent graph schema formalization:
  - Added `docs/planning/phi_mapping_and_latent_graph_schema_20260328.md` to
    document the richer formal `Phi` relation, typed `L(P)` graph schema, and
    guarded transfer semantics.
  - Recorded the crucial compatibility rule:
    the current executable `sl.cross_system_phi.contract.v1` schema remains
    the bounded transport grammar, while the richer relation kinds are a next
    formal layer rather than an already-shipped runtime change.
  - Updated the root README, TODO, compact context, `plan.md`, `status.json`,
    and `devlog.md` so the next `Milestone X` step is the richer semantic
    formalization over the bounded `v1` schema.
- Canonical planning-state realignment:
  - Replaced the stale root `spec.md` and `architecture.md` workbench scope
    with the current latent-state / cross-system mapping program.
  - Added `Milestone X` to `plan.md` and repointed `status.json` so the
    autonomous control plane now tracks the bounded `L(P)` / `Phi` contract
    package rather than the prior workbench milestone.
  - Recorded the shift in `devlog.md`; no code behavior changed in this pass.
- Global latent legal state across systems clarification:
  - Added `docs/planning/global_latent_legal_state_cross_system_20260327.md`
    to extend the latent-state discipline into the multi-system case without
    collapsing legal traditions into one hidden universal ontology.
  - Recorded that any future global lane must operate over local promoted
    truth sets `P_i` plus a checked mapping layer `Phi`, with explicit
    `exact|partial|incompatible|undefined` outcomes.
  - Updated the root README, TODO, and compact context so any future
    cross-system transfer or alignment work starts with bounded mapping
    contracts and mismatch reports rather than automatic truth merge.
- Latent state over promoted truth clarification:
  - Added `docs/planning/latent_state_over_promoted_truth_20260327.md` to pin
    `latent state` language to a derived compression over promoted truth
    rather than a hidden truth layer over raw text.
  - Recorded the required constraints for any future `L(P)` lane:
    reconstruction, anchor preservation, compression discipline, consistency
    preservation, and downstream-only authority.
  - Updated the root README, TODO, and compact context so any future latent
    graph or DASHI-style compression work stays downstream of promotion and
    cannot silently mutate truth.
- Motif candidate / promotion / legal-tree clarification:
  - Added `docs/planning/motif_candidate_promotion_legal_tree_20260327.md`
    to state the disciplined repo reading of motif, cohomology, and
    legal-tree language.
  - Recorded that motifs remain candidate/overlay structure until a lane
    defines explicit promotion semantics, and that cohomology is currently an
    analysis aid rather than a truth-bearing architectural role.
  - Updated the root README, TODO, and compact context so future legal-tree or
    motif work must stay anchored to source-linked records, promotion gates,
    and explicit node-family status.
- JMD x SensibLaw truth-construction boundary:
  - Added `docs/planning/jmd_sensiblaw_truth_construction_boundary_20260327.md`
    from the archived `Zero Trust Ontology` thread resolved via
    `robust-context-fetch`.
  - Recorded the sharpened boundary:
    `SensibLaw` is the truth-construction layer between messy source
    substrates and downstream reasoning/agent systems, not a generic JMD
    runtime or scheduler surface.
  - Updated the root README, TODO, and compact context so future JMD/SL graph
    work stays tied to source anchors, reversible transforms, promotion basis,
    and explicit abstention.
- Cross-source follow/review control-plane parity:
  - Added `SensibLaw/docs/planning/cross_source_follow_control_plane_20260327.md`
    and the first portable `follow.control.v1` queue/control-plane contract in
    `SensibLaw/src/fact_intake/control_plane.py`.
  - First concrete adopters now span AU plus generic fact-review:
    `authority_follow`, `intake_triage`, and `contested_items`.
  - `itir-svelte /graphs/fact-review` now renders these control-plane-backed
    queues generically from shared metadata/queue fields, reducing AU-specific
    UI special casing and making the next source-family rollouts cheaper.
- AU authority-follow UI bridge:
  - `itir-svelte /graphs/fact-review` now exposes the AU
    `authority_follow` operator view for AU selectors by bridging the AU
    `demo-bundle` operator surface alongside the persisted workbench route.
  - The new tab shows route-target counts plus the bounded follow-needed
    authority queue without changing the generic persisted fact-review
    workbench contract for other lanes.
- Workspace coordination boundary:
  - Added `docs/planning/workspace_coordination_boundary_20260327.md` to make
    the repo-boundary decision explicit.
  - Recorded that the workspace should continue operating across the existing
    repos, with `ITIR-suite` as the control plane for cross-repo planning and
    promotion decisions.
  - Recorded that a new top-level project dir is not justified yet; new dirs
    should be created only for genuine runtime/build or transport surfaces,
    not duplicate coordination state.
- Feedback receipt collector UI:
  - Extended `itir-svelte /corpora/processed/personal` with the first
    collector-facing feedback capture surface over the canonical ITIR DB:
    one-receipt add form, JSONL paste/import form, and recent receipt cards.
  - This now sits above the existing `feedback.receipt.v1` receiver and
    `query_fact_review.py feedback-add|feedback-import|feedback-receipts`
    commands.
  - Recent feedback receipts now use provenance-first drill-ins back to
    internal objects/routes when a stable ref already exists.
  - The collector UI now captures canonical thread ids and fact-review
    selector refs explicitly so those drill-ins are available more often.
- Feedback receipt capture ergonomics:
  - Extended `SensibLaw/scripts/query_fact_review.py` with `feedback-add` and
    `feedback-import` so `feedback.receipt.v1` rows can be captured without
    manual sqlite seeding.
  - Updated the contract/TODO/context surfaces so CLI add plus local
    JSONL/JSON import is the first bounded intake path for real user feedback.
- Feedback receipt contract + first persisted receiver:
  - Added `docs/planning/feedback_receipt_contract_20260327.md` to define the
    bounded cross-repo receipt contract for competitor frustrations,
    frustrations with our suite, and delight/retention signals.
  - Added the first persisted `feedback.receipt.v1` receiver in
    `SensibLaw`'s `itir.sqlite` path, with query surfaces for listing and
    inspecting receipts.
  - Updated the root TODO so the next step is capture/import ergonomics rather
    than leaving feedback evidence as chat lore.
- Cross-repo user-story + feedback audit:
  - Added `docs/planning/repo_user_story_state_and_feedback_20260327.md` to
    assess the major suite repos against the current user stories and record
    the strongest likely competitor frustrations, likely frustrations with our
    current surfaces, and likely user-valued strengths.
  - Made the missing evidence explicit: current frustration knowledge is still
    mostly story-derived/proxy rather than based on persisted interview or
    usability receipts.
  - Added a root TODO to establish a bounded feedback-receipt lane so future
    prioritization can use real user evidence instead of chat lore alone.
- Shared shard artifact contract:
  - Added `docs/planning/shared_shard_artifact_contract_v1_20260327.md` to
    freeze the first transport-neutral contract across Zelph, Kant, ZOS, HF,
    and IPFS.
  - Recorded that shard identity must be logical first, selectors must resolve
    to logical shard ids before sink fetch, and JSON/CBOR are projection
    formats rather than competing semantic contracts.
  - Added `tools/build_shared_shard_artifact_contract.py` plus
    `tests/test_build_shared_shard_artifact_contract.py` for the first bounded
    implementation slice:
    lift a Zelph HF manifest into one logical artifact and emit both JSON and
    CBOR projections, with optional IPFS object-ref attachment.
  - Added `tools/build_ipfs_shard_ref_map.py` plus
    `tests/test_build_ipfs_shard_ref_map.py` to derive deterministic raw
    `ipfs://` refs from a local shard tree, including the routing sidecar.
  - Completed the first real dual-sink projection on the 2026 Zelph v3 proof
    artifact:
    `1536` logical shards plus the routing index now project from the same
    logical contract into both HF-backed and IPFS-backed object refs.
  - Mirrored the bounded proof artifacts across both sink families:
    HF dataset shard/query proofs, HF bucket storage for the shared-contract
    companion pack, and IPFS proof roots.
- Zelph upstream handoff:
  - `acrion/zelph#25` merged into `develop`.
  - Stefan's post-merge review identified one real follow-up bug in manifest
    load-all behavior.
  - Rebasing onto current `develop`, isolating the selector-guard fix, and a
    successful local rebuild produced the follow-up branch/PR:
    `acrion/zelph#26`.
- Zelph / Kant / ZOS shard architecture framing:
  - Added `docs/planning/zelph_kant_zos_shard_contract_matrix_20260327.md`
    to make the current shard decision explicit as a four-axis problem:
    sharder, sink, consumer runtime, and shared artifact contract.
  - Recorded that current evidence supports role-fit, not a proof of global
    optimality.
  - Recorded the current best-fit split:
    - Zelph sharder for query-shaped remote reads
    - Kant sharder for publish/pull packaging and content identity
    - HF for practical hosted querying
    - IPFS for immutable publication
- Meta-introspector HF/shard survey:
  - Recorded `kant-zk-pastebin` as the strongest reusable shard-aware HF
    surface, because it already combines shard objects, `manifest.cbor`, IPFS
    addressing, and shard emission.
  - Recorded `monster` as a consumer-side Hugging Face inference precedent
    only, and `huggingface_hub_uploader` / `hugging-push` as generic upload /
    deployment wrappers rather than the shard transport contract.
- Perf-output compression framing:
  - Recorded the `Voxel Promotion and MDL` thread as the current design basis
    for perf output compression.
  - The thread decision is to treat perf as a compression-governed stream with
    typed motif extraction, a streaming MDL compressor, and a binary output
    format, with Fractran kept as a mechanical proof-of-concept target.
- Suite MCP contract + scaffold lane:
  - Added `docs/planning/itir_mcp_dioxus_contract_20260326.md` to define the
    first suite-level MCP boundary, the `itir-mcp/` project direction, the
    SensibLaw-first read-only tool rollout, and the Dioxus backend/native
    integration posture.
  - Updated root planning/context surfaces so the MCP lane is tracked as a
    suite contract rather than an ad hoc sidecar.
  - Added the first `itir-mcp/` scaffold as a suite adapter project instead of
    folding MCP transport directly into existing component internals.
  - Hardened `itir-mcp` with a persistent `--bridge` protocol, structured
    envelopes, and version metadata for client health/version checks.
  - Added Dioxus native-gateway persistence and optional local fallback controls
    before reducing fallback dependency for production flow.
