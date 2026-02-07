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

## Operational Rule
- Docs define orchestration intent first.
- TODO tracks executable orchestration steps second.
- Code and adapters follow those contracts.
