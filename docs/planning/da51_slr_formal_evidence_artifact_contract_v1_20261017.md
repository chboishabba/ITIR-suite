# DA51 × SLR Formal Evidence Artifact Contract v1

Date: 2026-10-17
Contract: `da51-slr-formal-evidence-artifact/v1`

## Purpose

This contract connects an SLR proof obligation to repository-intelligence routing, independently certified formal evidence, and optional ITIR logical-artifact publication without moving semantic/payment authority out of SLR or turning transport metadata into proof.

```text
SLR reviewed PNF
 -> ProofResidual / ProofObligation
 -> FormalProofDemand
 -> dashi-repo discovery/dedupe/history
 -> FormalProofRouteReceipt
 -> reuse | agda2lean | Aristotle | Lean/Agda formalisation
 -> independent checker receipt
 -> FormalEvidenceReceipt
 -> exact SLR obligation/statement-digest weld
 -> dependency-scoped reopen
 -> optional ITIR artifact/shard publication
 -> HF / IPFS / file object refs
```

## Ownership

- SLR owns PNF, proposition support, residuals, proof obligations, payment and recurrence.
- dashi-repo owns discovery, dedupe, history and routing receipts.
- DA51 is a semantic/reference join namespace, not a proof token.
- agda2lean owns translation capability only.
- Aristotle owns assigned reasoning/reconstruction work only.
- Lean/Agda checkers own certification receipts for their own outputs.
- ITIR owns cross-project artifact/message/provenance contracts.
- ERDFA/Kant owns artifact/shard packaging.
- HF/IPFS/file are materialisation sinks.

## FormalProofDemand attachment

An artifact may carry an optional non-authoritative demand attachment:

```json
{
  "formalDemandRef": "formal-demand:smith:1",
  "externalObligationRef": "proof-obligation:smith:1",
  "statementDigest": "sha256:...",
  "da51Address": "0xDA51831100800000"
}
```

This attachment is a join only. The artifact does not own the SLR obligation payload.

## FormalEvidence attachment

A logical artifact may attach a formal evidence reference after independently checked evidence exists:

```json
{
  "formalEvidenceRef": "formal-evidence:smith:1",
  "statementDigest": "sha256:...",
  "checker": "lean",
  "checkerRevision": "lean:<commit/toolchain>",
  "certificationState": "kernel-certified"
}
```

The ITIR artifact stores provenance/transport for that evidence. It does not reinterpret the checker's result or pay the SLR obligation itself.

## Shared-shard linkage

Optional artifact-level provenance additions:

- `da51Address`
- `formalDemandRef`
- `formalEvidenceRef`
- `statementDigest`

These fields are not part of logical shard identity. Existing identity remains:

```text
contractVersion + artifactId + artifactRevision + shardId + contentDigest
```

A CID, HF path or file URI remains an `objectRef` attached after logical shard resolution.

## Exact-payment invariant

A certificate may be offered back to SLR only when:

```text
demand_ref matches
external_obligation_ref matches
statement_digest matches
required result kind matches
required DA51 join matches when present
checker/certification state satisfies the SLR formal-obligation contract
```

If a backend changes the statement, it must provide explicit transport/equivalence evidence or create a new demand. Same symbol name, same DA51 address, or same artifact family is not enough.

## Runtime evidence

`zkperf`, eBPF/MCPtrace and other runtime producers may attach sibling evidence to the same object/artifact graph:

```text
trace
benchmark
runtime_observation
kernel_observation
security_input
```

Those evidence classes are observational. They do not become theorem proof or security conclusions merely because they share a DA51 address, demand ref or artifact.

## Forbidden implications

```text
route receipt != proof
DA51 status/address != proof
agda2lean capability != proof
Aristotle candidate != certification
formal certificate != legal applicability
formal certificate != claim truth
zkperf/eBPF observation != theorem
zkperf/eBPF observation != security conclusion
artifactId/shardId != CID/URI
CID/URI != semantic identity
publication acknowledgement != proof
```

## Canonical fixture

`docs/planning/jmd_fixtures/da51_slr_formal_evidence_v1.example.json` is the bounded cross-repo fixture for this contract. It contains one positive identity chain and explicit negative vectors for the forbidden substitutions above.
