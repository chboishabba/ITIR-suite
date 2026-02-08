# ITIR as Orchestrator

ITIR-suite is the orchestration layer for the workspace. It does not replace
component internals; it coordinates them through explicit contracts.

## Role
- Maintain cross-project intent, priorities, and context.
- Route work between component interfaces.
- Keep artifacts, provenance, and planning aligned across boundaries.

## What ITIR Orchestrates
- `SensibLaw/`: deterministic legal substrate and graph outputs.
- `SL-reasoner/`: interpretive overlays over SensibLaw outputs.
- `tircorder-JOBBIE/` and `WhisperX-WebUI/`: capture and transcription flows.
- `StatiBaker/`: state compilation over multi-project signals.
- Chat/context stack: `reverse-engineered-chatgpt/` and
  `chat-export-structurer/`.
- Analytics/connectors and research utilities (`Chatistics/`,
  `pyThunderbird/`, `notebooklm-py/`, streaming modules, ribbon module).
- Local projects (`fuzzymodo/`, `casey-git-clone/`) as actively developed
  orchestrated components.

## Boundaries
- ITIR-suite does not silently mutate component semantics.
- Component contracts remain authoritative inside each project directory.
- Cross-component behavior must be declared via interface channels.
- ITIR object-schema ownership lives in `SensibLaw/docs/itir_model.md`.

## Orchestration Channels
### Channel O1: Context and Planning Ingress
- Inputs: `__CONTEXT/*`, `.planning/phases/*`, `docs/planning/*`.
- Purpose: maintain explicit intent and current state before execution.

### Channel O2: Component Contract Routing
- Inputs: per-project `docs/interfaces.md` contracts.
- Purpose: map upstream outputs to downstream expected ingress fields.

### Channel O3: Execution and Sync Control
- Inputs: workspace scripts and submodule operations.
- Purpose: execute coordinated updates without violating component ownership.

### Channel O4: Artifact and Decision Egress
- Outputs: `TODO.md`, `__CONTEXT/COMPACTIFIED_CONTEXT.md`, planning indexes.
- Purpose: record what changed, why, and what remains.

## Current Priority Intersection
- Four-way handoff contract:
  `docs/planning/sl_tircorder_ribbon_sb_intersection_20260208.md`
  (`SensibLaw` x `tircorder-JOBBIE` x `itir-ribbon` x `StatiBaker`).
- Idempotency/dedupe cooperation addendum:
  `docs/planning/itir_idempotency_dedupe_cooperation_20260208.md`
  (shared invariants vs siloed semantics + schema-freeze decision queue).
- Reducer ownership contract:
  `docs/planning/reducer_ownership_contract_20260208.md`
  (shared runtime distribution with SL semantic governance).
- Canonical consumption matrix:
  `docs/planning/itir_consumption_matrix_20260208.md`
  (ratified producer/consumer paths and authority-write null paths).
- Receipts pack automation contract:
  `docs/planning/receipts_pack_automation_contract_20260208.md`
  (verification-first export bundles and expansion-invariant enforcement).
- Concept/RuleAtom + contradiction contract:
  `docs/planning/concept_ruleatom_expansion_contradiction_contract_20260208.md`
  (layer boundaries + contradiction detection outputs + reconciliation boundary).
- TiRC->SL + context/receipt contract:
  `docs/planning/tirc_sl_context_envelope_promotion_receipts_contract_20260208.md`
  (reducer wiring + trauma-aware context envelopes + promotion receipt rules).
- Three Locks + narrative sovereignty contract:
  `docs/planning/three_locks_narrative_sovereignty_contract_20260208.md`
  (public artifact quality gates + anti-gaming lock enforcement).

## Operational Rule
- Docs define orchestration intent first.
- TODO tracks executable orchestration steps second.
- Code and adapters follow those contracts.
