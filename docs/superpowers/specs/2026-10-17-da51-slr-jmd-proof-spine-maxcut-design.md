# DA51 × SLR × JMD Proof Spine Max-Cut Design

Date: 2026-10-17
Status: design approved in chat; implementation not yet started
Coordination owner: ITIR-suite

## 1. Purpose

Unify the existing formal-semantics, PNF/proof-search, repository-intelligence, execution-evidence, artifact-packaging, publication, and operator-query lanes without creating a new universal authority or duplicating existing semantic stores.

The target is a cross-repo object/evidence graph in which:

- DA51 is a stable semantic/reference namespace and join key;
- SLR remains the Rust production owner for PNF, proposition support, residuals, proof obligations, payment/reopening, and Matter/runtime state;
- DASHI/Agda remains the golden formal contract for PNF/proof/debt/search invariants;
- dashi_lean4 remains the canonical DA51 ABI and Lean proof-bearing authority boundary;
- dashi-repo owns repository discovery, dedupe, history, proof routing, and authority-neutral DA51/evidence joins;
- agda2lean owns translation capability only;
- Aristotle consumes proof-routing output as an adaptive proof/formalisation backend;
- zkperf and eBPF lanes produce runtime/trace/observation evidence only;
- ITIR owns cross-project artifact/message/provenance contracts;
- ERDFA/Kant owns logical artifact/shard packaging;
- IPFS/HF/file are publication/materialisation sinks;
- ZOS owns publish/pull orchestration;
- Zelph and Dioxus consume the resulting graph read-only.

No layer may silently upgrade another layer's evidence into theorem, legal, security, or authorization authority.

## 2. Existing owners to preserve

### Formal semantics

- `dashi_lean4/DA51/Core.lean` is the normative DA51 header/type ABI owner.
- `dashi_agda` mirrors the DA51 ABI and carries mature formal PNF/debt/proof-search owners.
- Historical DA51 type codes 0-7 remain frozen.
- DA51 type 8 remains the frozen atlas coordinate/snapshot encoding already defined by the existing v1 work.
- Types 9-15 remain reserved/unassigned.

### SLR runtime semantics

SLR remains the production runtime owner for the existing chain:

```text
source/span
-> Candidate PNF
-> Reviewed PNF
-> Reviewed Proposition Support
-> LegalIR / semantic runtime materialisation
-> ProofResidual / ProofObligation
-> PropositionChainPayment
-> PropositionPayment / Reader ABI
-> selective reopening / recurrence
```

This design does not add a second PNF implementation, second proposition store, second proof frontier, or second PostgreSQL semantic authority.

### Repository intelligence

`dashi-repo` remains the owner for:

- exact/equivalent/similar symbol discovery;
- repository-history and lineage lookup;
- fail-closed absence receipts;
- dedupe-before-generation;
- proof-debt routing;
- DA51 registry/evidence joins;
- read-only proof-route/history surfaces for agents and MCP consumers.

### Translation and proof generation

- `agda2lean` owns declaration-level translation capability (`Exact`, `Encoded`, `Reconstruct`, `Quarantined`, `Unsupported`) and never self-certifies theorem truth.
- Aristotle is an adaptive reasoning/formalisation/proof-search backend, not a proof authority.
- Lean/Agda kernel validation remains the certification boundary for formal claims.

### Artifact and publication stack

- ITIR shared artifact contracts own logical artifact/revision/shard/provenance semantics.
- ERDFA/Kant packages logical artifacts/shards/manifests.
- IPFS CID, HF path, and file URI are sink/materialisation identities, not semantic-object identities.
- ZOS may publish/pull/mirror logical artifacts but must not redefine their meaning.

## 3. Chosen architecture

Use typed bridge receipts between existing owners.

Rejected alternatives:

1. **Put DA51 directly into every SLR semantic row.** Rejected because it couples the runtime schema to one interoperability namespace and risks turning DA51 into an internal database primary key.
2. **Mirror SLR semantic state into dashi-repo as the new canonical store.** Rejected because it creates duplicate persistence authority and replay ambiguity.
3. **One universal JSON object spanning theorem, PNF, artifact, CID, runtime observation, and UI state.** Rejected because it collapses authority classes and makes evolution brittle.

The canonical pattern is instead:

```text
SLR proof obligation
    -> typed FormalProofDemand
    -> dashi-repo discovery/dedupe/history
    -> FormalProofRouteReceipt
    -> reuse / agda2lean / Aristotle / Lean / Agda
    -> kernel/result-specific FormalEvidenceReceipt
    -> DA51 EvidenceRef linkage
    -> SLR exact-obligation reopen
    -> residual recomputation / payment transition
    -> optional ITIR artifact packaging/publication
```

## 4. Core bridge contracts

### 4.1 FormalProofDemand

Owned by SLR as an export from an existing proof residual/obligation.

Required fields:

```text
FormalProofDemand
  demand_ref
  obligation_ref
  consumer_ref
  pnf_revision_ref
  residual_ref
  proposition_ref?
  statement_digest
  statement_language
  target_prover
  da51_address?
  source_revision_refs[]
  requested_result_kind
```

Rules:

- `demand_ref` is immutable/content-derived or otherwise replay-stable.
- `obligation_ref`, `pnf_revision_ref`, and `residual_ref` must reopen existing SLR-owned rows.
- `statement_digest` commits to the formal statement surface presented to the router.
- optional `da51_address` is a join to an existing DA51 semantic object; absence does not authorize minting a new DA51 type.
- emitting a demand creates no theorem/legal/security authority.

### 4.2 FormalProofRouteReceipt

Owned by dashi-repo.

```text
FormalProofRouteReceipt
  route_ref
  demand_ref
  external_obligation_ref
  statement_digest
  exact_matches[]
  equivalent_matches[]
  similar_matches[]
  historical_matches[]
  debt_kind
  selected_backend
  agda2lean_capability?
  da51_address?
  absence_receipt?
  policy_owner_refs[]
  establishes_proof = false
```

Routing rules:

- exact/equivalent reuse is considered before generation;
- generation is not opened merely because name search fails;
- a true absence receipt requires the configured semantic search surfaces to have completed sufficiently to justify absence;
- `similar` never implies theorem equivalence;
- route selection never grants proof or legal authority;
- routing receipts cite the merged/formal policy owners they operationalize where available.

### 4.3 FormalEvidenceReceipt

Produced by formal backends after an independently checkable result exists.

```text
FormalEvidenceReceipt
  evidence_ref
  demand_ref
  obligation_ref
  da51_address?
  producer
  artifact_ref
  artifact_digest
  statement_digest
  checker
  checker_revision
  source_revision
  result_kind
  certification_state
  dependencies[]
```

Rules:

- a route receipt is not a formal evidence receipt;
- an Aristotle candidate is not certified evidence;
- agda2lean `Exact`/`Encoded` capability is not certification;
- Lean/Agda certification must name the checker/toolchain/result artifact actually used;
- the evidence must retain the same `statement_digest` as the demand, or carry an explicit transport/equivalence receipt before it can pay that obligation.

### 4.4 SLR FormalEvidencePayment

SLR consumes a `FormalEvidenceReceipt` only through a strict same-object weld.

Required equality/reopen checks:

```text
receipt.demand_ref == persisted demand
receipt.obligation_ref == persisted obligation
receipt.statement_digest == persisted demand statement digest
receipt.da51_address matches expected DA51 join when one is required
checker/result kind satisfies the obligation's required result class
source/provenance refs reopen without silent substitution
```

Payment result:

- may close or narrow the exact formal residual when the obligation contract says the formal premise is sufficient;
- may expose new residuals;
- must trigger ordinary SLR dependency-scoped reopening;
- must not automatically promote legal applicability, claim truth, security findings, or user authorization.

## 5. DA51 role

DA51 is a cross-system semantic/reference join key, not a universal content hash or authority token.

Hard distinctions:

```text
DA51 address != theorem proof
DA51 address != literature truth
DA51 address != legal applicability
DA51 address != ZK validity
DA51 address != security violation
DA51 address != authorization
DA51 status nibble != external proof authority
```

Type-8 remains an atlas coordinate/snapshot carrying level/biome/status/serial/reserved. Because status is encoded, a type-8 address is not silently redefined as the universal immutable theory identity. If a future stable-theory DA51 namespace is required, it must use an explicit vNext allocation/governance decision; types 9-15 remain reserved until then.

For v1 infrastructure, a stable non-DA51 registry key may identify the durable theory object while type-8 remains an atlas coordinate/snapshot join.

## 6. SLR/PNF integration

The design integrates the existing SLR proof loop rather than placing a new router in front of PNF.

Canonical flow:

```text
source acquisition/materialisation
-> candidate PNF
-> explicit review
-> reviewed PNF
-> proposition support / legal IR as applicable
-> active consumer residual
-> ProofResidual / ProofObligation
-> classify required producer
```

Producer routing:

```text
source/acquisition residual
    -> existing SLR LegalFollow / INV / governed acquisition

identity/same-object residual
    -> existing source/world identity lanes

formal mathematical/logical residual
    -> FormalProofDemand -> dashi-repo router

transcription/formalisation residual
    -> agda2lean/formalisation backend where capability permits

certification residual
    -> Lean/Agda checking/replay lane

runtime/empirical residual
    -> zkperf/eBPF/other evidence producer, not theorem lane
```

The existing proof-debt distinctions remain authoritative for routing; no runtime router may collapse mathematical, transcription, certification, and empirical-evidence debt into one queue.

## 7. JMD / ITIR artifact linkage

Formal or runtime evidence may be published as ITIR logical artifacts after the evidence object exists.

Link shape:

```text
EvidenceRef
  -> artifactId
  -> artifactRevision
  -> shardId?
  -> contentDigest
  -> objectRefs[]
```

Sink examples:

```text
hf://...
ipfs://<cid>
file:///...
```

Rules:

- `artifactId`/`shardId` are logical identities;
- `artifactRevision` and `contentDigest` identify a concrete build/content revision;
- CID/URI is a transport/materialisation attachment;
- sink changes do not change the underlying proof/evidence meaning;
- publication does not create theorem/legal/security authority.

## 8. zkperf and eBPF

These are sibling evidence producers against the same object/obligation graph.

Suggested evidence classes:

```text
proof
trace
benchmark
source
receipt
runtime_observation
kernel_observation
security_input
```

Rules:

- zkperf trace/benchmark receipts may support empirical/runtime obligations;
- eBPF/MCPtrace observations may support runtime/security investigation;
- neither is accepted as formal proof merely because it is linked to a DA51 address;
- zkSEC may consume these inputs but must independently apply its own grounding/admissibility/security logic.

## 9. Repository and MCP surfaces

### dashi-repo CLI/API

Required additive operations:

```text
dashi-repo prove route-external-obligation
dashi-repo prove evidence-for-obligation
dashi-repo da51 resolve
dashi-repo da51 evidence
dashi-repo da51 frontier
```

### MCP

Read-oriented surfaces should expose:

```text
proof_route_for_obligation
formal_evidence_for_obligation
da51_resolve
da51_evidence
da51_frontier
```

MCP is an orchestration/query seam only. It does not own theorem, legal, or publication semantics.

## 10. Dioxus and Zelph

Dioxus is the operator cockpit.

It may render:

- PNF/residual state;
- formal proof route/history;
- exact/equivalent/similar repository matches;
- formal evidence/certification state;
- zkperf/eBPF evidence;
- ITIR artifact/shard/publication refs;
- selective-reopening consequences.

It must not recompute proof payment or silently create review/admission state.

Zelph remains a selector/query consumer for logical artifacts/shards. It resolves selectors to logical shard IDs before choosing HF/IPFS/file materialisations.

## 11. Canonical fixture

One bounded cross-repo fixture must exercise the whole chain:

```text
source revision/span
-> candidate PNF
-> reviewed PNF
-> ProofResidual
-> ProofObligation
-> FormalProofDemand
-> dashi-repo discovery/dedupe
-> FormalProofRouteReceipt
-> formal backend result
-> FormalEvidenceReceipt
-> DA51 evidence linkage
-> SLR exact-obligation reopen
-> residual/payment transition
-> ITIR artifact revision
-> ERDFA/Kant shard
-> IPFS/HF/file objectRef
```

The fixture must also contain negative vectors for:

- wrong statement digest;
- wrong obligation ref;
- route receipt presented as proof;
- agda2lean capability presented as proof;
- DA51 status presented as proof;
- CID/URI presented as semantic identity;
- eBPF/zkperf observation presented as theorem evidence;
- stale/mismatched source revision;
- duplicate/similar symbol mistaken for exact equivalence.

## 12. Documentation updates required during implementation

### ITIR-suite

- add this design to the planning/index docs;
- update JMD/PNF/publish roadmaps to name the DA51/SLR bridge and preserve existing authority boundaries;
- update shared shard/artifact docs with optional DA51/formal-evidence linkage.

### slr

- document `FormalProofDemand` and `FormalEvidencePayment` in the proof-search/runtime roadmap;
- update ownership docs to state that dashi-repo routes formal proof work but does not own PNF or payment;
- document exact reopening and nonpromotion guarantees.

### dashi_agda

- update repository-intelligence/proof-router docs to name SLR external obligations as a supported consumer;
- document debt-kind to SLR residual/producer mapping;
- retain Agda formal-owner references.

### dashi_lean4

- update DA51 ABI/provenance docs with formal-demand/evidence linkage and statement-digest requirement where applicable;
- retain type-8/status authority firewall.

### agda2lean

- update capability contract docs to state how an SLR-routed formalisation demand consumes capability output;
- retain `establishes_proof = false`.

### zkperf / zkSEC

- update DA51/evidence docs to place runtime receipts beside, not above, formal evidence;
- preserve zkSEC's independent security-admissibility boundary.

### Dioxus / Zelph / ZOS / ERDFA/Kant

- update consumer/publisher docs to treat DA51/formal-evidence refs as optional logical provenance attachments, never sink identity or authority.

## 13. Testing and verification requirements

Implementation must be test-first per repo where executable tests exist.

Minimum contract checks:

- SLR rejects mismatched demand/obligation/statement digests;
- dashi-repo refuses generation without sufficient discovery/absence evidence;
- agda2lean capability never sets proof authority;
- DA51 status never self-certifies proof;
- formal evidence can pay only the exact SLR obligation it was issued for;
- selective reopening reaches dependent residuals and leaves unrelated fibres closed;
- artifact publication preserves logical identity across HF/IPFS projections;
- eBPF/zkperf evidence stays observational/runtime unless a separate formal bridge is supplied.

Compiler/test success may only be claimed from fresh exact-head execution receipts. CI is not a project-management gate, but absence of CI/local execution means the status must remain source-written/unverified.

## 14. Rollout order

Recommended dependency order:

1. preserve/land existing DA51 ABI/mirror/provenance tranches;
2. preserve/land agda2lean capability contract;
3. extend dashi-repo external-obligation routing schema/API;
4. add SLR `FormalProofDemand` export and `FormalEvidencePayment` import;
5. add cross-repo canonical fixture;
6. wire ITIR artifact linkage and update shard/message contracts;
7. register zkperf/eBPF sibling evidence classes;
8. expose Dioxus/Zelph read paths;
9. update all relevant ownership/roadmap docs;
10. only then consider vNext DA51 namespace allocation for stable theory identity if type-8 snapshot semantics prove insufficient.

## 15. Definition of complete

The max-cut is complete when:

- SLR can emit a replay-stable formal proof demand from a real persisted proof obligation;
- dashi-repo can discover/reuse/dedupe/route that external obligation without duplicating SLR state;
- agda2lean/Aristotle/formal checkers can participate through typed authority-neutral route/evidence receipts;
- a certified formal evidence receipt can be re-opened by SLR and pay only its exact obligation;
- DA51 joins the same object/evidence graph without redefining status as proof;
- zkperf/eBPF runtime evidence can attach to the same graph without becoming theorem authority;
- ITIR/ERDFA/Kant can package the resulting evidence artifact with HF/IPFS/file projections while keeping logical identity separate from sink identity;
- Dioxus/Zelph can query/render the graph without owning semantic payment;
- the canonical fixture and negative vectors exist across the participating repos;
- relevant roadmaps and ownership docs agree on the same separation of powers;
- no duplicate PNF, proof frontier, DA51 ABI, artifact-identity model, or semantic persistence authority is introduced.
