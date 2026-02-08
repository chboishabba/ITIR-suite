# Planning Docs

This folder contains ADRs, UI component specs, doctrine notes, and validation
artifacts for the context invariant.

## ITIR Orchestrator Contract

ITIR-suite orchestration role and boundaries:
- `docs/planning/itir_orchestrator.md`
- `docs/planning/why_itir_not_sl.md` (separation of powers: ITIR vs SL)

## Validation (Stub)

The context envelope validation stub lives at:
- `docs/planning/context_envelope_validate_stub.py`

To wire validation:
1. Choose a JSON Schema validator (draft 2020-12 compatible).
2. Implement the TODOs in the stub.
3. Add the script to CI or a pre-commit hook.

## Fuzzymodo Selector DSL Pack

Fuzzymodo planning artifacts live under:
- `docs/planning/fuzzymodo/`

This pack defines selector DSL contracts, norm-constraint schemas, canonical
hashing rules, and fixture samples for implementation scaffolding.

## Casey Git Clone Pack

Casey-derived superposition VCS planning artifacts live under:
- `docs/planning/casey-git-clone/`

## Project Interface Contracts

Suite-wide interface contract index:
- `docs/planning/project_interfaces.md`

## Capability Posture (Audit-Safe) (2026-02-08)

Separates current capabilities from roadmap targets to prevent over-claiming:
- `docs/planning/itir_capability_posture_20260208.md`

## UI Surface Registry (2026-02-08)

Canonical list of current user-facing interfaces (URLs/paths + launch commands)
across core components.

Documents:
- `docs/planning/ui_surface_registry_20260208.md`
- `docs/planning/ui_surface_manifest.json`

## UI Integration Strategy (2026-02-08)

Phased policy for linking and optionally federating multiple renderers while
keeping authority boundaries explicit.

Document:
- `docs/planning/ui_integration_strategy_20260208.md`

## Cross-Thread Followthrough (2026-02-07)

Concrete outputs for:
- SB/fuzzer invariants and acceptance checks
- casey-git model/operation contracts
- JesusCrust integration and ADR-ready principles

Document:
- `docs/planning/sb_casey_jesuscrust_followthrough_20260207.md`

## SL LCE/Profile Followthrough (2026-02-08)

Concrete outputs from thread `6986d38e-4b5c-839b-813a-608aa0de88d5`
(`ADR language vs SensibLaw`) covering:
- engine/profile separation
- ingest-safe invariant language
- profile contract and safety-test backlog

Document:
- `docs/planning/sl_lce_profile_followthrough_20260208.md`

## Moltbook Feedback Intake (2026-02-08)

Captured community feedback and doctrine-aligned followthrough for SB/ITIR
authority/replay requirements.

Document:
- `docs/planning/moltbook_feedback_alignment_20260208.md`

## Crisis-Advocacy Module (CAM) (2026-02-08)

Formal, bounded spec for crisis advocacy execution using pre-authorized
escalation envelopes, with explicit SB vs norms-review boundaries.

Document:
- `docs/planning/crisis_advocacy_module_cam_20260208.md`
- Accepted ADR:
  - `docs/adr/ADR_014_crisis_advocacy_module_cam_20260208.md`
- Schemas/examples:
  - `docs/planning/schemas/escalation_envelope.schema.json`
  - `docs/planning/schemas/escalation_envelope.example.healthcare.json`

## SL/TiRCorder/Ribbon/SB Intersection (2026-02-08)

Focused cross-component contract map for the four-way handoff between
`SensibLaw`, `tircorder-JOBBIE`, `itir-ribbon`, and `StatiBaker` under ITIR
orchestration.

Document:
- `docs/planning/sl_tircorder_ribbon_sb_intersection_20260208.md`

## Idempotency/Dedupe Cooperation Addendum (2026-02-08)

Integrated shared-vs-siloed idempotency model, authority-crossing handshake,
anti-enshittification expansion invariant, and open decision queue (`Q1`-`Q11`)
for schema freeze readiness.

Document:
- `docs/planning/itir_idempotency_dedupe_cooperation_20260208.md`

## Reducer Ownership Contract (2026-02-08)

Dedicated contract for SL/SB/TiRCorder reducer boundaries, including ownership
options and recommended hybrid model (shared runtime, SL-governed semantics).

Document:
- `docs/planning/reducer_ownership_contract_20260208.md`

## ITIR Consumption Matrix (2026-02-08)

Canonical producer/consumer matrix for `SensibLaw`, `tircorder-JOBBIE`,
`StatiBaker`, and `itir-ribbon` to reduce cross-team boundary drift.

Document:
- `docs/planning/itir_consumption_matrix_20260208.md`

## Receipts Pack Automation Contract (2026-02-08)

Target-state contract for graph-seeded receipts pack generation, verification,
reproducibility metadata, and expansion-invariant compliance.

Document:
- `docs/planning/receipts_pack_automation_contract_20260208.md`

## Concept/RuleAtom + Expansion + Contradiction Contract (2026-02-08)

Ratified boundary contract covering semantic atoms vs logic atoms, formal
Expansion Invariant cost model, and cross-system contradiction detection output
rules (`needs_reconciliation` default).

Document:
- `docs/planning/concept_ruleatom_expansion_contradiction_contract_20260208.md`

## TiRC->SL + Context Envelope + Promotion Receipt Contract (2026-02-08)

Implementation contract for TiRCorder consumption of SL reducer surfaces,
trauma-aware Context Envelope grounding, and authority-crossing promotion receipt
requirements.

Document:
- `docs/planning/tirc_sl_context_envelope_promotion_receipts_contract_20260208.md`

## Three Locks + Narrative Sovereignty Contract (2026-02-08)

Enforcement contract for thesis/receipt/action locks with anti-gaming quality
gates (explicitly avoiding hard exact-word-count correctness).

Document:
- `docs/planning/three_locks_narrative_sovereignty_contract_20260208.md`

## Prospective Sprint 10 Refactor Slice (2026-02-08)

Single-sprint execution plan to convert current SL/TiRCorder/SB/Ribbon
contracts into a thin-slice implementation with explicit ratification gates and
replay/idempotency contract tests.

Document:
- `docs/planning/itir_prospective_sprint_10_refactor_20260208.md`

## Refactor Master Coordination (2026-02-08)

Single control-plane artifact for refactor execution sequencing, doc lockdown,
decision queue state, sprint gates, and PR merge policy.

Document:
- `docs/planning/refactor-master-coordination.md`

## Assumption Stress Test (2026-02-08)

Critical-assumption register translating architectural critiques into explicit
failure modes, controls, and test-gate requirements.

Document:
- `docs/planning/assumption_stress_test_20260208.md`

## Chat Artifact Capture Contract (2026-02-08)

Capture contract for assistant-generated downloadable files, inline file
emissions, and execution claims in archived ChatGPT threads.

Document:
- `docs/planning/chat_artifact_capture_contract_20260208.md`

## Indigenous Data Sovereignty Connector Guardrails (2026-02-08)

Guardrails for connector/context-field behavior where Indigenous authority,
consent, provenance, and non-flattening requirements apply.

Document:
- `docs/planning/indigenous_data_sovereignty_connector_guardrails_20260208.md`

## Health Data Connector Guardrails (2026-02-08)

Guardrails for ingesting personal health data exports (FHIR, scans, clinician
notes) with meta-only defaults, identity minimization, and no-inference rules.

Document:
- `docs/planning/health_data_connector_guardrails_20260208.md`

## DBpedia/Wikitology Priority Context (2026-02-08)

Canonical context pointer for external ontology integration framing (DBpedia/Wikitology
analogy) and the in-repo landing points.

Document:
- `docs/planning/dbpedia_wikitology_priority_context_20260208.md`

## DBpedia External ID Representation Decision (2026-02-08)

Records the tradeoff case for short-form DBpedia IDs (Option 2), while choosing
to implement full DBpedia URIs as the supported representation (Option 1).

Document:
- `docs/planning/dbpedia_external_id_representation_decision_20260208.md`
