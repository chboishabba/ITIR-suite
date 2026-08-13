# Refactor Master Coordination (2026-02-08)

## Purpose
Keep all refactor work for SL/TiRCorder/SB/Ribbon synchronized under one
coordination artifact.

This file is the execution control plane for Sprint 10 and related followthrough.

## Lockdown status
- Status: `LOCKED_FOR_REFRACTOR`
- Effective date: `2026-02-08`
- Rule: contract docs listed below are frozen unless changed through this
  coordination process.

## Source-of-truth stack (frozen)
### Tier 1: Execution authority
- `docs/planning/refactor-master-coordination.md` (this file)
- `docs/planning/itir_prospective_sprint_10_refactor_20260208.md`

### Tier 2: Contract authority
- `docs/planning/sl_tircorder_ribbon_sb_intersection_20260208.md`
- `docs/planning/itir_idempotency_dedupe_cooperation_20260208.md`
- `docs/planning/reducer_ownership_contract_20260208.md`
- `docs/planning/itir_consumption_matrix_20260208.md`
- `docs/planning/tirc_sl_context_envelope_promotion_receipts_contract_20260208.md`
- `docs/planning/concept_ruleatom_expansion_contradiction_contract_20260208.md`
- `docs/planning/receipts_pack_automation_contract_20260208.md`
- `docs/planning/three_locks_narrative_sovereignty_contract_20260208.md`
- `docs/planning/assumption_stress_test_20260208.md`
- `docs/planning/indigenous_data_sovereignty_connector_guardrails_20260208.md`

### Tier 3: Interface and orchestration authority
- `docs/planning/project_interfaces.md`
- `docs/planning/itir_orchestrator.md`

## Non-negotiable boundaries
- Shared primitives, siloed semantics.
- SL owns canonical semantic equivalence.
- SB owns temporal/state reducer semantics.
- TiRCorder owns capture/ingest semantics.
- Ribbon is projection-only and non-authoritative.
- No competing canonical token/concept identity stores in SB or TiRCorder.

## Change-control protocol (required)
1. Open/update decision entry in this file (Decision queue section).
2. Update impacted contract doc(s).
3. Update `TODO.md` with executable tasks.
4. Implement code/tests.
5. Update changelog(s) in touched submodule(s).
6. Log outcome in `__CONTEXT/COMPACTIFIED_CONTEXT.md`.

Any PR that skips steps 1-3 is blocked.

## Workstreams and owners
- WS1 Schema and envelope:
  - Scope: `itir.exchange.v1`, required envelope/provenance fields.
  - Owner role: integration/schema owner.
- WS2 Shared reducer runtime:
  - Scope: Option C integration surface, version pinning, compatibility matrix.
  - Owner role: SL infrastructure owner.
- WS3 Adapter thin slice:
  - Scope: TiRCorder -> canonical IDs, SB -> canonical refs, SB -> Ribbon map.
  - Owner role: adapter owners per component.
- WS4 Contract tests:
  - Scope: replay no-op/conflict, identity parity, projection safety,
    expansion-invariant smoke.
  - Owner role: QA/contracts owner.
- WS5 UI surface coordination:
  - Scope: suite interface registry, launcher manifest, and integration-depth
    guardrails (link-hub first, federation optional).
  - Owner role: frontend/orchestration owner.

## Decision queue (blocking)
- `Q2` SB mechanical-should representation.
- `Q6` authority-crossing idempotency collision-domain semantics.
- `Q11` canonical reducer ownership ratification (Option C).
- `Q12` cross-project UI integration depth (link-hub only vs federated shell).

Status convention:
- `OPEN`
- `RATIFIED`
- `IMPLEMENTED`
- `VERIFIED`

Current state (2026-02-08):
- `Q2`: `OPEN`
- `Q6`: `OPEN`
- `Q11`: `OPEN`
- `Q12`: `OPEN`

## Assumption stress register
Reference: `docs/planning/assumption_stress_test_20260208.md`

State convention:
- `OPEN`
- `CONTROL_DEFINED`
- `TESTED`
- `GATED`

Current state (2026-02-08):
- `A1` axis overload risk: `OPEN`
- `A2` SB hidden agency risk: `CONTROL_DEFINED` (linked to `Q2`)
- `A3` receipt-to-intent gap: `CONTROL_DEFINED` (quality-gate policy tracked)
- `A4` cross-jurisdiction flattening risk: `OPEN`
- `A5` perf-vs-sovereignty risk: `OPEN`
- `A6` contradiction terminal-state risk: `OPEN`
- `A7` lexical-noise guardrail risk: `OPEN`
- `A8` fail-open gate discipline risk: `CONTROL_DEFINED`
- `A9` summary-of-summary decay risk: `OPEN`
- `A10` loss-profile schema drift risk: `OPEN`

## Sprint gate checklist
- [ ] ADRs ratified for `Q2`, `Q6`, `Q11`.
- [ ] `itir.exchange.v1` schema frozen.
- [ ] Shared reducer integration surface frozen.
- [ ] Adapter thin slice merged.
- [ ] Contract gate tests passing in CI.
- [ ] Projection safety assertions enforced.
- [ ] Assumption stress controls wired for Sprint 10 blockers (`A2`, `A3`).
- [ ] Fail-closed CI stub tests exist for all unresolved AIDs/Qx controls.
- [ ] UI surface registry + launcher manifest are current and reviewed.
- [ ] `Q12` integration-depth decision is recorded before shell federation work.

## PR merge policy (refactor window)
- Must cite impacted Tier 1/2 docs in PR description.
- Must include test evidence for any boundary-affecting change.
- Must include explicit statement:
  - "No new canonical identity store introduced in SB/TiRCorder."
- Must include rollback note for schema/adapter changes.
- Any `OPEN` AID/Qx touched by the PR must include a fail-closed CI stub test
  or an explicit waiver receipt.

## Reporting cadence
- Daily: update sprint gate checklist and decision states in this file.
- Per merge: append one-line change note under "Execution log".

## Execution log
- 2026-02-08: coordination file created; lockdown and merge gate policy enabled.
- 2026-02-08: added UI coordination workstream (`WS5`) and integration-depth
  decision queue item (`Q12`); linked to registry/strategy docs.
- 2026-02-08: added non-codex ChatGPT artifact-capture contract for
  assistant-generated files/execution claims and linked TODO followthrough.
- 2026-02-08: added Indigenous data sovereignty guardrails for connectors and
  context overlays (observer metadata only, consent/provenance/promotion rules).
