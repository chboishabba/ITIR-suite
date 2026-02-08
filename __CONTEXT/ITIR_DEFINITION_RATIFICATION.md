# ITIR Definition Ratification (Draft v0.1)

## Status
- Drafted: `2026-02-07`
- Ratification state: `pending sign-off`
- Scope: define canonical wording for ITIR/ITIR-suite without adding unstated assumptions.

## Inputs
- Source extracts: `__CONTEXT/ITIR_DEFINITION_CONTEXT.md`
  - `S1`: assistant snippet (`ITIR is the investigative operating system`)
  - `S2`: assistant snippet (`ITIR-suite is now a meta-repo with submodules`)
  - `S3`: user snippet (`one system, multiple operating modes`)
  - `S4`: tool snippet (`StatiBaker/ITIR is one system with multiple operating modes`)
  - `S5`: user snippet (StatiBaker as daily state distillation engine/context prosthesis)
  - `S6`: assistant snippet (`ITIR can never accidentally re-segment time`)
- Current repo boundary docs:
  - `README.md`
  - `docs/planning/itir_orchestrator.md`
  - `docs/planning/why_itir_not_sl.md`
  - `docs/planning/project_interfaces.md`

## Clause Register

### Accepted

1. **ITIR-suite is a meta-repo orchestration/control plane, not a runtime OS.**
- rationale: aligns with `S2` and current workspace architecture docs.
- evidence: `S2`

2. **ITIR is an investigative/interpretive coordination layer over the SensibLaw substrate.**
- rationale: keeps SL/ITIR boundary explicit without overloading runtime meaning.
- evidence: `S1` (qualified phrasing in section below), `README.md`, `docs/planning/itir_orchestrator.md`

3. **StatiBaker is a daily state distillation engine/context prosthesis, and is not equivalent to ITIR itself.**
- rationale: product distinction required for clear ecosystem definitions.
- evidence: `S5`

4. **Temporal segmentation authority belongs to source tools/components; ITIR should consume and coordinate, not redefine by default.**
- rationale: boundary guardrail belongs to component contracts, not blanket ITIR ownership.
- evidence: `S6` (qualified interpretation), `StatiBaker` boundary docs

### Qualified / Context-Dependent

1. **`ITIR is the investigative operating system`**
- status: historical metaphor, not canonical runtime definition.
- rationale: useful shorthand in `S1`, but too overloaded if left unqualified.
- evidence: `S1`

2. **`one system, multiple operating modes`**
- status: likely stack-level doctrine, not a direct ITIR product identity statement.
- rationale: phrasing in `S3` is broad and includes SB/ITIR framing.
- evidence: `S3`

3. **`StatiBaker/ITIR is one system with multiple operating modes`**
- status: acceptable only as stack/doctrine shorthand; not acceptable as `StatiBaker == ITIR`.
- rationale: preserve component distinction.
- evidence: `S4`, `S5`

4. **`ITIR can never accidentally re-segment time`**
- status: boundary guardrail statement, not evidence that ITIR normally performs segmentation.
- rationale: should be interpreted as a contract constraint on consumers/overlays.
- evidence: `S6`

### Rejected (as canonical phrasing)

1. **`ITIR = the operating system` (unqualified statement).**
- reason: overloaded and repeatedly misread as system-runtime authority.
- replacement: use accepted clauses 1-4 above.
- evidence: ambiguity pressure observed around `S1`; corrected by architecture docs and current README wording.

2. **`StatiBaker/ITIR` as a single undifferentiated product identity.**
- reason: collapses product boundaries; conflicts with `S5` and current repo structure.
- replacement: represent `StatiBaker` as one component/product within the ITIR stack.
- evidence: `S5`, component docs

### Pending

1. **Decide public-doc policy for historical phrase `investigative operating system`**
- options:
  - keep as historical alias with warning label
  - remove from top-level docs and keep only in historical context files
- evidence anchor: `S1`

## Canonical Definition Block (Proposed)

`ITIR-suite` is the orchestration/control plane for the ITIR product stack and submodules.
`ITIR` is an investigative/interpretive coordination layer over the SensibLaw provenance substrate.
`ITIR` is not a standalone operating system runtime.
`StatiBaker` is a distinct product/component within the stack (daily state distillation + context prosthesis), not equivalent to ITIR.
Temporal segmentation authority remains with the producing component unless explicitly delegated by contract.

## Review Pass (2026-02-07)

User adjudication applied to source statements:
1. `ITIR is the investigative operating system` -> qualified metaphor (`close`, not canonical)
2. `ITIR-suite is now a meta-repo with submodules` -> accepted as true
3. `one system, multiple operating modes` -> qualified as probable stack doctrine
4. `StatiBaker/ITIR is one system with multiple operating modes` -> qualified; reject product conflation
5. `StatiBaker ... daily state distillation engine ... context prosthesis` -> accepted as SB-specific, not ITIR definition
6. `ITIR can never accidentally re-segment time` -> qualified boundary guardrail, not default ITIR function

## Sign-off
- Requested by: user
- Prepared by: Codex
- Final approver: _(pending)_
