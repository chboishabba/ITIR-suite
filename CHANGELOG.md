# Changelog

## Unreleased
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
