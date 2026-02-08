# ITIR Project Interface Index

This index tracks the intended intersections, interaction models, and exchange
channels for each core project directory in this workspace.

## Orchestrator Contract
- `docs/planning/itir_orchestrator.md` (ITIR-suite control-plane role)
- ITIR object model ownership: `SensibLaw/docs/itir_model.md`
- Refactor execution control plane:
  `docs/planning/refactor-master-coordination.md`

## Component Interface Specs
- `SensibLaw/docs/interfaces.md`
- `SL-reasoner/docs/interfaces.md`
- `tircorder-JOBBIE/docs/interfaces.md`
- `StatiBaker/docs/interfaces.md`
- `WhisperX-WebUI/docs/interfaces.md`
- `reverse-engineered-chatgpt/docs/interfaces.md`
- `chat-export-structurer/docs/interfaces.md`
- `notebooklm-py/docs/interfaces.md`
- `Chatistics/docs/interfaces.md`
- `pyThunderbird/docs/interfaces.md`
- `SimulStreaming/docs/interfaces.md`
- `whisper_streaming/docs/interfaces.md`
- `itir-ribbon/docs/interfaces.md`
- `fuzzymodo/docs/interfaces.md`
- `casey-git-clone/docs/interfaces.md`

## Suite-Level Intent
- Every component defines explicit ingress/egress channels.
- Cross-component handoffs should map directly to declared channels.
- Implementation work should follow these contracts before adding new behavior.

## Focused Intersection Artifacts
- `docs/planning/sl_tircorder_ribbon_sb_intersection_20260208.md`:
  four-way contract map for `SensibLaw`, `tircorder-JOBBIE`, `itir-ribbon`,
  and `StatiBaker`.
- `docs/planning/itir_idempotency_dedupe_cooperation_20260208.md`:
  shared-vs-siloed idempotency/dedupe model, authority-crossing handshake,
  and schema-freeze decision queue (`Q1`-`Q11`).
- `docs/planning/reducer_ownership_contract_20260208.md`:
  reducer ownership/reuse contract for SL, TiRCorder, and SB
  (shared runtime + SL semantic governance).
- `docs/planning/itir_consumption_matrix_20260208.md`:
  canonical producer/consumer matrix with authority-write null-path
  clarifications for SL/TiRCorder/SB/Ribbon.
- `docs/planning/receipts_pack_automation_contract_20260208.md`:
  target receipts-pack automation contract (seed traversal, reproducibility,
  verify bundle, expansion invariant constraints).
- `docs/planning/concept_ruleatom_expansion_contradiction_contract_20260208.md`:
  semantic-vs-logic atom boundary contract + expansion cost model +
  contradiction-finder output rules.
- `docs/planning/tirc_sl_context_envelope_promotion_receipts_contract_20260208.md`:
  TiRCorder->SL reducer integration contract + context-envelope grounding +
  authority-crossing promotion receipt requirements.
- `docs/planning/three_locks_narrative_sovereignty_contract_20260208.md`:
  public-artifact lock enforcement contract (thesis/receipt/action + anti-gaming
  quality gates).
- `docs/planning/assumption_stress_test_20260208.md`:
  cross-cutting assumption stress register with failure modes and gate controls
  for axis policy, SB fold neutrality, receipts-to-claim causality, plural-law
  preservation, and performance/sovereignty constraints.
- `docs/planning/ui_surface_registry_20260208.md`:
  suite UI entrypoint registry (URLs/paths, launch commands, ownership, and
  authority class boundaries).
- `docs/planning/ui_integration_strategy_20260208.md`:
  phased integration policy for multi-renderer coexistence, link-hub rollout,
  and optional Svelte-hosted federation.
- `docs/planning/ui_surface_manifest.json`:
  machine-readable registry backing a future launcher/portal and automated
  interface checks.
