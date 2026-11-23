# GOV-1 Integrated Control Case Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement GOV-1 as one cross-repository control plane that makes requirements, risk, controls, evidence, residual/CAPA, service state, privacy/security lifecycle and human-interface firewalls explicit without creating a second semantic authority or claiming standards certification.

**Architecture:** SensibLaw remains the canonical control-profile/evaluation owner. StatiBaker supplies execution/service evidence; SLR binds REL/INV runtime objects into governance packets and durable lower-authority sidecars; Dioxus renders Matter-scoped projections; DASHI proves projection/non-promotion/Pareto laws; ITIR-suite owns the cross-repo control map and C4 documentation. Existing semantic/review/persistence authorities are extended rather than duplicated.

**Tech Stack:** Python/Pytest (SensibLaw, StatiBaker), Rust/PostgreSQL (SLR), Rust/Dioxus (itir-dioxus), Agda (dashi_agda), Markdown/PlantUML (ITIR-suite).

**Spec:** `docs/superpowers/specs/2026-10-03-gov1-integrated-control-case-design.md`

## Global Constraints

- Standards are engineering-control provenance/design lenses, never certification claims.
- Preserve existing authority boundaries: SensibLaw control evaluator; SLR semantic/source stores; S29 review; S30 MatterContext; StatiBaker execution memory; Dioxus read projection.
- Governance never scalarizes INV `(I,D,C,N,L)` Pareto priority.
- Selection, render order, sorting, filtering, frontier membership and executable state never imply preference, truth, access authority or semantic promotion.
- `not_located`, `known_absent`, excluded/redacted/unavailable and hidden-by-view remain distinct.
- Information-asset/processing metadata supplements MatterContext; it does not replace visibility authorization.
- New source-present transitions still require canonical source persistence before INV update/reopening.
- TDD for executable changes: failing test first, observed RED, minimal implementation, GREEN, then full-suite verification.
- Preserve JMD/original-source attribution; do not rewrite upstream proof owners merely to fit GOV-1.

## Review Focus

1. **False certification implication:** profile/source-standard metadata must never emit language equivalent to “certified/compliant with ISO”. Test in SensibLaw control-case rendering.
2. **UI ordering bias:** stable route order or an explicit axis sort must not mutate frontier membership or emit a preferred/winner flag. Test in Dioxus read-model/UI projection.
3. **Governance-vs-priority collapse:** blocked/unauthorized route may remain Pareto-frontier; governance state must not be folded into Pareto coordinates. Test in SLR.
4. **Privacy scope leakage:** an INV control case referencing a source outside current MatterContext must not be viewable in Dioxus. Test against existing scope projection.
5. **Formal/runtime mismatch:** Agda frontier law must match Rust mixed-orientation dominance without hidden `1000 ∸ x` saturation. Add >1000 finite specimen.

---

### Task 1: SensibLaw canonical GOV-1 control case

**Files:**
- Modify: `SensibLaw/src/policy/control_profiles.py`
- Modify: `SensibLaw/src/policy/control_evaluator.py`
- Create: `SensibLaw/src/policy/control_case.py`
- Test: `SensibLaw/tests/policy/test_control_case.py`
- Test: `SensibLaw/tests/policy/test_compliance_assessment.py`

**Interfaces:**
- Consumes: existing `normalize_control_profile(...)`, `evaluate_control_profile(...)`, existing evidence bundles.
- Produces:
  - `GOV1_PROFILE_ID = "itir_gov1_integrated"`
  - `build_control_case(*, control_case_ref, subject_ref, subject_kind, requirement_refs, risk_refs, control_refs, implementation_refs, evidence_refs, residual_refs, service_change_state, evidence_state, profile=GOV1_PROFILE_ID) -> dict[str, Any]`
  - typed string enums/validators for `ServiceChangeState` and `EvidenceState`.

- [ ] **Step 1: Write failing tests** asserting the GOV-1 profile contains the portable control families from the spec, preserves standards only as `source_standards`, rejects empty identity/control/evidence references, keeps service/evidence state orthogonal, and never emits a certification claim flag.
- [ ] **Step 2: Run focused tests and observe RED.**
  - Run: `pytest -q tests/policy/test_control_case.py tests/policy/test_compliance_assessment.py`
  - Expected: failures for missing GOV-1 profile/control-case APIs.
- [ ] **Step 3: Implement the minimal GOV-1 profile and `control_case.py` carrier/validator.** Reuse `evaluate_control_profile`; do not fork the evaluator into a second compliance engine.
- [ ] **Step 4: Extend evaluator clauses only for evidence dimensions actually required by GOV-1 control groups.** Unsupported/unpaid groups must yield `insufficient_evidence` or `not_applicable`, not synthetic satisfaction.
- [ ] **Step 5: Run focused tests to GREEN, then full SensibLaw suite.**
  - Run focused command above.
  - Run project-standard full `pytest` command.
- [ ] **Step 6: Commit** with a narrow GOV-1 control-case message.

### Task 2: SensibLaw information-asset, processing-activity and CAPA carriers

**Files:**
- Create: `SensibLaw/src/policy/information_governance.py`
- Create: `SensibLaw/src/policy/nonconformance.py`
- Test: `SensibLaw/tests/policy/test_information_governance.py`
- Test: `SensibLaw/tests/policy/test_nonconformance.py`

**Interfaces:**
- Produces:
  - `build_information_asset(...) -> dict[str, Any]`
  - `build_processing_activity(...) -> dict[str, Any]`
  - `build_nonconformance(...) -> dict[str, Any]`
  - `build_capa_cycle(...) -> dict[str, Any]`
- Required asset fields match the spec: asset/data class/PII/sensitivity/accountable role/purpose/matter/access basis/consumers/storage/providers/retention/revocation-or-deletion/audit refs.
- CAPA defect kinds include semantic mismatch, provenance loss, authority leak, scope leak, privacy exposure, security boundary violation, UI ambiguity, replay nondeterminism, performance regression and hidden-work amplification.

- [ ] **Step 1: Write failing tests** for mandatory identity/purpose fields, explicit `contains_pii` rather than inferred PII, processing input/output linkage, and a DMAIC/CAPA record whose improvement cannot erase the original residual/evidence refs.
- [ ] **Step 2: Run tests and observe RED.**
- [ ] **Step 3: Implement minimal immutable dictionary carriers/validators following existing policy-module conventions.**
- [ ] **Step 4: Run focused tests to GREEN, then full SensibLaw suite.**
- [ ] **Step 5: Commit.**

### Task 3: StatiBaker execution/service evidence projection

**Files:**
- Create: `StatiBaker/src/statibaker_governance_evidence.py`
- Test: `StatiBaker/tests/test_statibaker_governance_evidence.py`
- Modify: `StatiBaker/docs/user_stories.md`
- Modify: `StatiBaker/docs/kanboard_runsheet_roadmap.md`

**Interfaces:**
- Consumes existing runsheet/status/heartbeat/sync-report artifacts only.
- Produces `build_governance_evidence_projection(...) -> dict` with execution refs, service-change state, evidence-state, incident/problem/change/release refs and provenance refs.
- No semantic evaluation, standards satisfaction verdict, user priority or compliance authority lives in StatiBaker.

- [ ] **Step 1: Write failing tests** for `implemented != validated`, failed external sync -> incident evidence without corrupting canonical local state, and absent validation -> no `validated` promotion.
- [ ] **Step 2: Run tests and observe RED.**
- [ ] **Step 3: Implement the projection over existing artifacts; no new canonical task store.**
- [ ] **Step 4: Update SB user-story/roadmap language to make service/evidence states and one-way governance evidence explicit.**
- [ ] **Step 5: Run focused tests then full StatiBaker suite.**
- [ ] **Step 6: Commit.**

### Task 4: SLR INV governance packet and durable sidecar

**Files:**
- Create: `slr/crates/sl-pg-source-store/src/governance_control_case.rs`
- Create: `slr/crates/sl-pg-source-store/src/governance_control_case_store.rs`
- Modify: `slr/crates/sl-pg-source-store/src/lib.rs`
- Modify: existing migration/schema owner used by `investigation_acquisition_store.rs` for a new immutable lower-authority governance table.
- Test: Rust unit tests in the new modules; PG reopen test following existing store patterns.

**Interfaces:**
- Consumes: `DurableAcquisitionQueue`, persisted REL comparison/residual, source revision refs, explicit governance evidence supplied by caller.
- Produces:
  - `AcquisitionGovernancePacket`
  - `GovernanceAccessState`
  - `PrivacyExposureState`
  - `AiUseState`
  - `ServiceEvidenceState`
  - `build_inv_governance_packet(...)`
  - `persist_inv_governance_packet(...)`
  - `load_inv_governance_packet(...)`
- Packet carries purpose, authorization/access, privacy, security, AI intended-use/risk, service/evidence state, control refs and evidence refs. It carries `creates_semantic_authority=false`, `creates_access_authority=false`, `creates_priority=false`.

- [ ] **Step 1: Write failing unit tests** for blocked-but-Pareto route remaining frontier, no governance coordinate entering Pareto dominance, nonempty evidence refs for claimed governed states, and no authority/promotion booleans.
- [ ] **Step 2: Observe RED with `cargo test -p sl-pg-source-store governance_control_case`.**
- [ ] **Step 3: Implement the pure packet builder.**
- [ ] **Step 4: Write failing PG persistence/reopen test** requiring exact obligation/comparison/source bindings and immutable replay equality.
- [ ] **Step 5: Observe RED, implement table/store, then GREEN.**
- [ ] **Step 6: Run full crate/workspace Rust tests.**
- [ ] **Step 7: Commit.**

### Task 5: SLR explainable Pareto and potential reopening projection

**Files:**
- Modify: `slr/crates/sl-pg-source-store/src/investigation_acquisition.rs`
- Test: existing module tests plus new regression specimens.

**Interfaces:**
- Produces:
  - `ParetoDominanceWitness { dominator_ref, dominated_ref, weak_axis_relations, strict_axis_refs }`
  - `RouteFrontierDisposition { FrontierExecutable, FrontierBlocked, Dominated { witness_refs } }`
  - `PotentialReopeningCone { direct_refs, transitive_refs }`
  - helpers that explain why a route is retained/eliminated without scalar scoring.

- [ ] **Step 1: Write failing tests** for two jointly nondominated routes, blocked nondominated route, executable dominated route, stable route-id display order, and dominance witness matching all five mixed-orientation axes.
- [ ] **Step 2: Observe RED.**
- [ ] **Step 3: Implement minimal explanation/disposition functions over the already-correct runtime mixed-orientation dominance.**
- [ ] **Step 4: Add counterfactual reopening-cone test proving it is only a projection and creates no actual reopening receipt.**
- [ ] **Step 5: GREEN plus full workspace tests.**
- [ ] **Step 6: Commit.**

### Task 6: Dioxus investigation workbench projection/HCD pass

**Files:**
- Modify: `itir-dioxus/src/workbench/investigation.rs`
- Modify: `itir-dioxus/src/app.rs`
- Create: `itir-dioxus/src/workbench/investigation_projection.rs`
- Test: add module/component regression tests following current workbench test conventions.

**Interfaces:**
- Consumes only persisted SLR acquisition/governance/explanation data under `SENSIBLAW_MATTER_SCOPE`.
- Produces typed read projections:
  - `InvestigationMode::{Investigate, Inspect, Graph}`
  - structurally separate frontier/executable/blocked/dominated collections
  - explicit current display sort lens
  - potential-reopening versus actual-reopening labels
  - no `preferred`, `winner` or scalar-priority field.

- [ ] **Step 1: Write failing projection tests** for hidden != absent, selected != preferred, sort preserving frontier membership, blocked != dominated, executable != frontier and outside-Matter governance denial.
- [ ] **Step 2: Observe RED with focused cargo tests.**
- [ ] **Step 3: Implement the typed projection model and Matter-scoped loader reuse.**
- [ ] **Step 4: Write failing UI regression tests** requiring obligation-first copy, explicit `Pareto set — no overall ranking`, structural frontier/executable/access state, text+semantic labels rather than color-only state, governance evidence provenance and potential-reopening wording.
- [ ] **Step 5: Implement Investigate/Inspect/Graph progressive disclosure without introducing write actions.**
- [ ] **Step 6: GREEN focused tests, then full Dioxus/workspace tests.**
- [ ] **Step 7: Commit and update SLR dependency pins only after the backend head is final.**

### Task 7: DASHI formal GOV-1 and investigation GUI owners

**Files:**
- Modify or supersede on current Agda integration branch: `DASHI/Core/ITIRInvestigationAcquisitionParetoExact.agda`
- Create: `DASHI/Core/ITIRInvestigationWorkbenchProjectionExact.agda`
- Create: `DASHI/Core/ITIRGovernanceControlCaseExact.agda`
- Add focused check script/workflow only if the repository already uses that pattern for these Core owners.

**Interfaces:**
- `ITIRInvestigationAcquisitionParetoExact` must expose direct mixed-orientation dominance matching Rust, or prove a bound before any loss embedding.
- `ITIRInvestigationWorkbenchProjectionExact` formalizes visible-real-route, hidden-not-false, selected-not-preferred, sort/filter frontier preservation, blocked-not-dominated, executable-not-preferred, frontier-not-authorized, potential-not-actual reopening and unrelated-node closure.
- `ITIRGovernanceControlCaseExact` separates requirement/risk/control/evidence/residual/service/evidence states and proves evidence/control records do not create semantic truth or certification authority.

- [ ] **Step 1: Add a RED/static target for the new module names and >1000 Pareto specimen before implementation.**
- [ ] **Step 2: Implement direct mixed-orientation dominance and prove the finite >1000 specimen preserves the runtime order.**
- [ ] **Step 3: Implement GUI projection firewalls by reusing Matter workspace/review/selective-reopening owners rather than re-encoding them.**
- [ ] **Step 4: Implement GOV-1 control-case non-promotion owners.**
- [ ] **Step 5: Run focused Agda kernel checks if executable is available; otherwise report source-written status without a kernel claim.**
- [ ] **Step 6: Commit/open or update the appropriate draft PR.**

### Task 8: ITIR-suite GOV-1 roadmap, acceptance matrix and C4/PlantUML

**Files:**
- Modify: `ITIR-suite/docs/user_stories.md`
- Modify: `ITIR-suite/plan.md`
- Create: `ITIR-suite/docs/planning/gov1_integrated_control_case_20261003.md`
- Create: `ITIR-suite/docs/planning/gov1_acceptance_matrix_20261003.md`
- Create: `ITIR-suite/docs/architecture/itir_suite_gov1_c4.puml`
- Update: `ITIR-suite/docs/superpowers/specs/2026-10-03-gov1-integrated-control-case-design.md` only if implementation reveals a true design correction.

**Interfaces:**
- C4 Level 1/2/INV component/deployment views identify semantic authority, review authority, read projections, PII boundaries and external-provider boundaries.
- Acceptance matrix maps user story -> requirement -> risk -> control -> implementation owner -> evidence -> residual/CAPA -> release state.

- [ ] **Step 1: Add GOV-1 roadmap milestone without displacing REL-1C/INV-1 corpus/runtime hard gates.**
- [ ] **Step 2: Add explicit governance acceptance criteria to the PI/OSINT story: control-case visibility, no certification implication, asset/processing purpose, accessible non-color-only states, and service/evidence-state separation.**
- [ ] **Step 3: Add acceptance matrix with INV-1 as first proving case and mark each runtime/formal receipt honestly as source-written/compile/fixture/runtime/production observed.**
- [ ] **Step 4: Add C4/PlantUML views and lint/render with the repo's existing PlantUML validation path if available.**
- [ ] **Step 5: Cross-check docs against actual branch heads and update PR descriptions; no certification/conformance claim beyond observed evidence.**
- [ ] **Step 6: Commit.**

### Task 9: Cross-repository verification and promotion report

**Files:**
- Create/update promotion evidence in existing repo-native changelog/PR descriptions; do not invent a new global runtime authority.

**Interfaces:**
- Produces one factual GOV-1 status table listing exact heads and evidence state per repo.

- [ ] **Step 1: Run full available SensibLaw and StatiBaker tests and record failures by name.**
- [ ] **Step 2: Run SLR workspace tests and any available PostgreSQL INV/GOV reopen acceptance.**
- [ ] **Step 3: Run Dioxus workspace/component tests.**
- [ ] **Step 4: Run focused Agda checks if executable/CI exists; otherwise leave formal evidence state at `source_written`.**
- [ ] **Step 5: Inspect exact-head GitHub workflow/status receipts; distinguish CodeRabbit/static status from compile/kernel/runtime evidence.**
- [ ] **Step 6: Produce a no-overclaim final matrix: implemented vs verified vs validated vs released/observed, outstanding REL-1C source-corpus gate, and residual GOV-1 gaps.**
