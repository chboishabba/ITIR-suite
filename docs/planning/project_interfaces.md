# ITIR Project Interface Index

This index tracks the intended intersections, interaction models, and exchange
channels for each core project directory in this workspace.

## Orchestrator Contract
- `docs/planning/itir_orchestrator.md` (ITIR-suite control-plane role)
- ITIR object model ownership: `SensibLaw/docs/itir_model.md`

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
