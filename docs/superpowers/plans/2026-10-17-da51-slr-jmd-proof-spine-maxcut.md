# DA51 × SLR × JMD Proof Spine Max-Cut Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Connect SLR's persisted PNF/proof-obligation runtime to dashi-repo proof routing, DA51 evidence linkage, formal backends, and ITIR artifact publication without duplicating semantic stores or escalating authority.

**Architecture:** Use typed bridge receipts between existing owners. SLR exports replay-stable formal proof demands from existing residual/obligation state; dashi-repo discovers/dedupes/routes them; independently certified formal results return as evidence receipts; SLR reopens only the exact obligation and recomputes its ordinary frontier. ITIR/ERDFA/Kant may package resulting evidence as logical artifacts with IPFS/HF/file refs, but transport identifiers never become semantic or proof authority.

**Tech Stack:** Rust + PostgreSQL (`slr`), Python + SQLite/MCP (`dashi_agda/tools/agda_preflight`), Lean 4 (`dashi_lean4`), Agda (`dashi_agda`), Haskell (`agda2lean`), Rust (`zkperf`), Python (`zkSEC`), Markdown/JSON fixtures (`ITIR-suite`).

**Spec:** `docs/superpowers/specs/2026-10-17-da51-slr-jmd-proof-spine-maxcut-design.md`

## Global Constraints

- DA51 v1 header/types remain frozen: types 0-7 unchanged, type 8 atlas layout unchanged, types 9-15 reserved/unassigned.
- DA51 identity, provenance, status nibble, CID, artifact location, route receipt, Aristotle candidate, agda2lean capability, zkperf/eBPF observation, and legal review are never proof authority by themselves.
- SLR/PostgreSQL remains the production owner for PNF, proposition support, residuals, proof obligations, payment, Matters, and recurrence.
- `.dashi/repository.sqlite3` stores routing/discovery/evidence joins only; it must not mirror SLR semantic state as a second canonical store.
- `agda2lean` capability must retain `establishes_proof = false`.
- Formal evidence may pay only the exact obligation/statement digest it was issued for, with explicit transport/equivalence evidence required for a changed statement.
- Artifact/shard logical identity is separate from `artifactRevision`, content digest, CID, HF path, and file URI.
- CI is not a project-management gate, but no compiler/test GREEN claim is allowed without fresh exact-head execution evidence.
- No PR merges are part of this plan unless explicitly requested after implementation review.

## Review Focus

- A formal receipt for the right theorem but wrong `obligation_ref` must fail closed rather than pay a neighboring residual.
- A proof route found through an exact/equivalent repository match must not be treated as a proof before independent certification.
- A statement whose text changes after routing must be detected by `statement_digest`, even if the same DA51 address or symbol name is reused.
- Publication to multiple sinks must preserve one logical artifact identity while allowing different CIDs/URIs and revisions.
- Runtime evidence (`zkperf`, eBPF, security input) linked to the same DA51 object must remain observational unless an explicit formal bridge consumes it.

---

## File Structure

### `slr`
- Create `crates/sl-core/src/formal_proof_bridge.rs`: pure bridge types and validation predicates.
- Modify `crates/sl-core/src/lib.rs`: export bridge module.
- Create `crates/sl-pg-source-store/src/formal_proof_bridge_store.rs`: durable demand/evidence receipt persistence and strict reopen/payment checks.
- Modify `crates/sl-pg-source-store/src/lib.rs`: export store module.
- Create `crates/sl-pg-source-store/tests/formal_proof_bridge_contract.rs`: RED/green contract tests.
- Create `docs/architecture/formal_proof_bridge.md`: ownership and authority boundary.
- Modify relevant proof-search/runtime roadmap docs to point to the bridge.

### `dashi_agda` PR #1200 branch
- Modify `tools/agda_preflight/agda_preflight/proof_router.py`: external obligation + statement-digest routing contract and durable route/evidence joins.
- Modify `tools/agda_preflight/agda_preflight/product_cli.py`: `prove route-external-obligation`, `prove evidence-for-obligation`.
- Modify `tools/agda_preflight/agda_preflight/repository_mcp.py`: read-only MCP counterparts.
- Modify `tools/agda_preflight/tests/test_proof_router.py`, `test_product_cli_proof_router.py`, `test_mcp_proof_router.py`.
- Modify `Docs/support/reference/DA51ProofRouterMaxCut20261017.md` and `tools/agda_preflight/README.md`.

### `dashi_lean4` PR #81 branch
- Modify `DA51/Provenance.lean`: statement/artifact digest-aware evidence linkage without changing proof authority.
- Modify provenance/ABI docs and add focused source-level examples/tests if the branch already has a validation surface.

### `dashi_agda` DA51 PR #1219 branch
- Modify `DASHI/DA51/Provenance.agda`: mirror digest-aware evidence linkage and non-authority predicate.
- Update DA51 compatibility/provenance docs.

### `agda2lean` PR #9 branch
- Modify `docs/DASHI_PROOF_ROUTER_CONTRACT.md`: external SLR demand semantics and statement-digest handoff.
- Extend `test/CapabilityContract.hs` only if a machine-readable field/CLI output is changed; otherwise docs-only.

### `zkperf` PR #2 branch
- Extend provenance docs/types only as needed to represent sibling runtime evidence against a demand/object without adding proof authority.
- Add negative tests proving runtime evidence cannot advertise formal certification.

### `zkSEC` PR #1 branch
- Extend DA51/evidence firewall docs/tests so security inputs may reference formal/runtime evidence but cannot inherit theorem/security authority from linkage.

### `ITIR-suite` design branch / implementation successor
- Create `docs/planning/da51_slr_formal_evidence_artifact_contract_v1_20261017.md`.
- Create `docs/planning/jmd_fixtures/da51_slr_formal_evidence_v1.example.json`.
- Modify `docs/planning/shared_shard_artifact_contract_v1_20260327.md`, `docs/planning/zkperf_on_sl_roadmap_20260329.md`, planning index/roadmap docs, and relevant JMD push/pull notes.

### Read-side repos
- Update `solfunmeme-dioxus`/`itir-dioxus`, Zelph, ZOS, ERDFA/Kant docs only unless an existing typed read model already exposes generic evidence refs suitable for a small additive adapter.
- Do not introduce a new UI persistence or publication authority.

---

### Task 1: SLR Formal Proof Bridge

**Files:**
- Create: `slr/crates/sl-core/src/formal_proof_bridge.rs`
- Modify: `slr/crates/sl-core/src/lib.rs`
- Create: `slr/crates/sl-pg-source-store/src/formal_proof_bridge_store.rs`
- Modify: `slr/crates/sl-pg-source-store/src/lib.rs`
- Test: `slr/crates/sl-pg-source-store/tests/formal_proof_bridge_contract.rs`
- Docs: `slr/docs/architecture/formal_proof_bridge.md`

**Interfaces:**
- Consumes: existing SLR proof-obligation/residual, PNF revision, proposition/source revision identities.
- Produces: `FormalProofDemand`, `FormalEvidenceReceiptInput`, strict persistence/reopen/payment functions keyed by `demand_ref`, `obligation_ref`, and `statement_digest`.

- [ ] **Step 1: Write failing contract tests**

Pin tests named:
- `formal_demand_requires_existing_exact_obligation_and_pnf_revision`
- `formal_evidence_wrong_obligation_fails_closed`
- `formal_evidence_wrong_statement_digest_fails_closed`
- `route_receipt_cannot_pay_formal_obligation`
- `formal_evidence_payment_reopens_only_declared_dependents`

Assertions must require all authority-promotion flags to remain false unless the existing SLR obligation transition explicitly pays only the formal premise.

- [ ] **Step 2: Run focused tests and record RED**

Run: `cargo test -p sensiblaw-pg-source-store --test formal_proof_bridge_contract`
Expected: FAIL because the bridge module/store does not exist.

- [ ] **Step 3: Implement bridge types**

Define immutable Rust types with these required fields:

```rust
FormalProofDemand {
    demand_ref,
    obligation_ref,
    consumer_ref,
    pnf_revision_ref,
    residual_ref,
    proposition_ref,
    statement_digest,
    statement_language,
    target_prover,
    da51_address,
    source_revision_refs,
    requested_result_kind,
}

FormalEvidenceReceiptInput {
    evidence_ref,
    demand_ref,
    obligation_ref,
    da51_address,
    producer,
    artifact_ref,
    artifact_digest,
    statement_digest,
    checker,
    checker_revision,
    source_revision,
    result_kind,
    certification_state,
    dependencies,
}
```

Use existing SLR identity/digest conventions rather than inventing another hash format.

- [ ] **Step 4: Implement strict PostgreSQL persistence/reopen/payment**

Persist only bridge receipts/foreign joins. Reopen existing SLR semantic owners for validation; do not duplicate PNF/proposition/residual payloads. Reject mismatched obligation, PNF, source, or digest coordinates before recording payment.

- [ ] **Step 5: Run focused tests**

Run: `cargo test -p sensiblaw-pg-source-store --test formal_proof_bridge_contract`
Expected: PASS.

- [ ] **Step 6: Run adjacent proof-search/store tests if available**

Run focused legal-controversy / real-matter / proof-search tests touched by imports. Record actual result without upgrading status if unavailable.

- [ ] **Step 7: Document the bridge**

Document the canonical chain `PNF -> ProofResidual/Obligation -> FormalProofDemand -> external route -> FormalEvidenceReceipt -> exact reopen`, and the non-collapse firewalls.

- [ ] **Step 8: Commit on a new SLR branch from current main**

Commit message: `feat: bridge SLR proof obligations to formal evidence`

---

### Task 2: dashi-repo External Obligation Router

**Files:**
- Modify: `dashi_agda/tools/agda_preflight/agda_preflight/proof_router.py`
- Modify: `dashi_agda/tools/agda_preflight/agda_preflight/product_cli.py`
- Modify: `dashi_agda/tools/agda_preflight/agda_preflight/repository_mcp.py`
- Test: `dashi_agda/tools/agda_preflight/tests/test_proof_router.py`
- Test: `dashi_agda/tools/agda_preflight/tests/test_product_cli_proof_router.py`
- Test: `dashi_agda/tools/agda_preflight/tests/test_mcp_proof_router.py`

**Interfaces:**
- Consumes: serialized `FormalProofDemand` coordinates from Task 1, existing repository discovery/history/DA51/debt/translator capability services.
- Produces: authority-neutral `FormalProofRouteReceipt` and evidence lookup keyed by external obligation/demand.

- [ ] **Step 1: Extend tests first**

Add tests that require:
- `demand_ref`, `external_obligation_ref`, `statement_digest` round-trip through route persistence;
- an exact/equivalent repository match suppresses new-generation recommendation but does not set `establishes_proof`;
- incomplete discovery cannot mint an absence receipt;
- a changed statement digest creates a distinct route identity/requires rerouting;
- evidence lookup returns only evidence linked to the same obligation/demand.

- [ ] **Step 2: Run focused pytest and record RED**

Run: `pytest tools/agda_preflight/tests/test_proof_router.py tools/agda_preflight/tests/test_product_cli_proof_router.py tools/agda_preflight/tests/test_mcp_proof_router.py -q`
Expected: FAIL on missing external-obligation fields/commands.

- [ ] **Step 3: Extend router persistence and typed results**

Add external obligation/demand/digest columns/tables additively. Keep SLR refs opaque and do not mirror SLR semantic payloads.

- [ ] **Step 4: Add CLI commands**

Add:
- `dashi-repo prove route-external-obligation`
- `dashi-repo prove evidence-for-obligation`

Inputs must carry the demand/obligation/digest coordinates; outputs retain `establishes_proof = false` for routes.

- [ ] **Step 5: Add read-only MCP functions**

Expose `proof_route_for_obligation` and `formal_evidence_for_obligation` using the same service functions as CLI; do not duplicate routing semantics in MCP code.

- [ ] **Step 6: Run focused pytest**

Expected: PASS for the new focused suite; report exact failures if the environment cannot execute it.

- [ ] **Step 7: Update router docs**

Describe SLR as an external obligation consumer/producer and map SLR formal/transcription/certification/empirical residuals onto existing proof-debt kinds.

- [ ] **Step 8: Commit onto PR #1200 branch**

Commit message: `feat: route external SLR proof obligations`

---

### Task 3: DA51 Digest-Aware Evidence Linkage

**Files:**
- Modify: `dashi_lean4/DA51/Provenance.lean`
- Modify: `dashi_agda/DASHI/DA51/Provenance.agda`
- Modify corresponding DA51 ABI/provenance docs.

**Interfaces:**
- Consumes: existing DA51 `EvidenceRef` semantics.
- Produces: additive digest/statement linkage or a companion receipt type sufficient to bind formal evidence to a concrete statement/artifact revision while preserving identity-only authority.

- [ ] **Step 1: Add formal/source-level regression examples first**

Pin that two receipts may share one DA51 address while differing in artifact/statement digest, and neither receipt proves the referenced proposition merely from metadata.

- [ ] **Step 2: Implement the smallest additive type change**

Prefer a companion typed receipt if adding fields to `EvidenceRef` would break existing constructors. Do not change DA51 header/type encoding or type-8 layout.

- [ ] **Step 3: Preserve Lean/Agda parity**

Use matching field semantics/names where language conventions permit. Add explicit non-authority predicates/theorems rather than comments alone.

- [ ] **Step 4: Execute exact-head Lean/Agda checks if toolchains are available**

Otherwise report `SOURCE-WRITTEN / KERNEL-UNVERIFIED`.

- [ ] **Step 5: Update DA51 docs and commit on the existing DA51 PR branches**

Lean commit: `feat: bind DA51 evidence to concrete statement revisions`
Agda commit: `feat: mirror digest-aware DA51 evidence linkage`

---

### Task 4: Formal Backend Contract Alignment

**Files:**
- Modify: `agda2lean/docs/DASHI_PROOF_ROUTER_CONTRACT.md`
- Test/modify if needed: `agda2lean/test/CapabilityContract.hs`
- Modify Aristotle/repository routing reference docs in `dashi_agda` where backend semantics are described.

**Interfaces:**
- Consumes: `FormalProofRouteReceipt` and SLR statement digest.
- Produces: documented capability/reconstruction handoff that never self-certifies proof.

- [ ] **Step 1: Add/extend capability contract test only if CLI/schema changes**

If no executable schema change is needed, keep this docs-only and do not add a gratuitous field.

- [ ] **Step 2: Document routing rules**

Pin:
- `Exact/Encoded -> translation lane -> independent Lean check`;
- `Reconstruct -> reconstruction obligation -> Aristotle/Lean -> independent check`;
- `Quarantined/Unsupported -> independent formalisation`;
- all modes retain `establishes_proof = false`.

- [ ] **Step 3: Document statement-digest preservation/transport**

A backend changing the statement must return an explicit equivalence/transport receipt before its certificate can pay the original SLR obligation.

- [ ] **Step 4: Commit to agda2lean PR #9 and dashi-repo docs**

Commit message: `docs: align formal backend contract with SLR proof demands`

---

### Task 5: ITIR Logical Artifact Contract and Cross-Repo Fixture

**Files:**
- Create: `ITIR-suite/docs/planning/da51_slr_formal_evidence_artifact_contract_v1_20261017.md`
- Create: `ITIR-suite/docs/planning/jmd_fixtures/da51_slr_formal_evidence_v1.example.json`
- Modify: `ITIR-suite/docs/planning/shared_shard_artifact_contract_v1_20260327.md`
- Modify: `ITIR-suite/docs/planning/zkperf_on_sl_roadmap_20260329.md`
- Modify planning index / roadmap reconciliation docs that enumerate current JMD architecture.

**Interfaces:**
- Consumes: Task 1-4 contract shapes.
- Produces: canonical interop fixture and publication linkage contract.

- [ ] **Step 1: Write the fixture with one positive chain and required negatives**

Positive chain must name distinct coordinates for source/span, PNF revision, residual, obligation, demand, route, DA51 object, certified evidence, ITIR artifact/revision/shard, and sink refs.

Negative cases must include wrong statement digest, wrong obligation, route-as-proof, agda2lean-capability-as-proof, DA51-status-as-proof, CID-as-semantic-identity, runtime-observation-as-theorem, stale source revision, and similar-symbol-as-equivalent.

- [ ] **Step 2: Add a lightweight schema/contract test if ITIR already has fixture validators**

Reuse existing validation style; do not introduce a new validation framework solely for this fixture.

- [ ] **Step 3: Update shared shard contract**

Add optional `da51Address`, `formalDemandRef`, `formalEvidenceRef`/equivalent provenance attachments without changing logical artifact identity rules.

- [ ] **Step 4: Update zkperf-on-SL roadmap**

Position zkperf trace/benchmark receipts as sibling evidence linked through the same object/artifact graph, not formal proof.

- [ ] **Step 5: Update ITIR planning index/roadmap and commit**

Commit message: `docs: connect DA51 SLR proof evidence to JMD artifacts`

---

### Task 6: Runtime Evidence and Security Firewalls

**Files:**
- Modify relevant provenance module/tests/docs on `zkperf` PR #2.
- Modify relevant DA51/evidence firewall module/tests/docs on `zkSEC` PR #1.

**Interfaces:**
- Consumes: DA51 address/demand/artifact linkage from prior tasks.
- Produces: sibling runtime/security-input evidence that cannot masquerade as formal certification or security authority.

- [ ] **Step 1: Add failing negative tests**

Pin that `trace`, `benchmark`, `runtime_observation`, and `security_input` linkage cannot set formal certification; zkSEC ingestion cannot infer vulnerability/security conclusion from DA51 status or proof linkage alone.

- [ ] **Step 2: Implement only missing additive evidence-link fields/kinds**

Reuse existing `Da51EvidenceRef` / envelope types and authority flags. Do not redesign the provenance ABI if existing `artifact` plus kind already suffices; add demand/artifact revision refs only where needed.

- [ ] **Step 3: Run focused Rust/Python tests if available**

Record actual receipts or state unverified.

- [ ] **Step 4: Update docs and commit to existing PR branches**

zkperf: `feat: link runtime evidence to formal demand graph`
zkSEC: `test: harden DA51 formal/runtime evidence firewall`

---

### Task 7: Read-Side Documentation/Adapters

**Files:**
- Update `solfunmeme-dioxus` and/or `itir-dioxus` architecture docs/read model if a generic evidence projection already exists.
- Update Zelph, ZOS, ERDFA/Kant docs where current shard/publish/query ownership is described.

**Interfaces:**
- Consumes: read-only object/evidence/artifact graph.
- Produces: operator/query projections; no persistence authority.

- [ ] **Step 1: Inspect existing generic evidence/read models before coding**

If they can already carry opaque provenance/evidence refs, make docs-only changes. Add code only when an existing typed projection has a clearly missing coordinate required by the fixture.

- [ ] **Step 2: Pin read-side invariants in existing tests if code changes**

Require that rendering/selection cannot mutate proof payment, review state, semantic authority, or sink identity.

- [ ] **Step 3: Update docs**

Dioxus = cockpit; Zelph = selector/query; ZOS = publish/pull orchestration; ERDFA/Kant = package/shard owner; IPFS/HF/file = sinks.

- [ ] **Step 4: Commit per touched repo**

Use focused docs/read-model commit messages; do not create new subsystems.

---

### Task 8: Cross-Repo Verification and PR Reconciliation

**Files:**
- Update PR descriptions/docs for `dashi_agda` #1200/#1219, `dashi_lean4` #81, `agda2lean` #9, `zkperf` #2, `zkSEC` #1, ITIR-suite #20 or its implementation successor, and the new SLR PR.

**Interfaces:**
- Consumes: all earlier tasks.
- Produces: one explicit landing ledger with exact heads, ownership, and verification status.

- [ ] **Step 1: Verify structural contract across heads**

Check each PR/file surface contains the intended bridge and that no repo duplicated another repo's canonical semantic store/ABI.

- [ ] **Step 2: Run available exact-head focused tests/toolchains**

Do not use CI as a stopping rule. Do not claim unobserved GREEN. Capture per-repo status as `EXECUTED-GREEN`, `EXECUTED-FAILED`, or `SOURCE-WRITTEN / EXECUTION-UNOBSERVED`.

- [ ] **Step 3: Validate canonical fixture semantics manually/programmatically**

Confirm all positive identities line up and every negative vector fails for the intended reason.

- [ ] **Step 4: Reconcile PR descriptions and cross-links**

State the final ownership graph, dependencies, and recommended landing order. Keep existing open PRs open; do not merge.

- [ ] **Step 5: Final whole-tranche review**

Verify the following final invariants:

```text
SLR PNF/payment owner != dashi-repo router
dashi-repo route != proof
DA51 address/status != proof
agda2lean capability != proof
Aristotle output != certification
formal certificate pays exact statement/obligation only
runtime observation != theorem/security conclusion
artifact/CID/URI != semantic identity
Dioxus/Zelph/ZOS presentation/orchestration != authority
```

- [ ] **Step 6: Report implementation status and outstanding execution receipts**

List PRs/heads, exact source changes, executed checks, unexecuted checks, and remaining landing order. Do not merge without an explicit later instruction.
