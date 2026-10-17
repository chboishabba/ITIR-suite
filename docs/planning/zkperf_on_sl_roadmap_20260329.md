# ZKPerf on SL Roadmap (2026-03-29)

## Goal

Pin the intended roadmap for bringing `zkperf` onto `SL` before proceeding with
the next implementation-facing shard/container work.

This note is a staging/gating note, not a claim that the integration is already
implemented.

## Why this comes first

Current planning already says:

- `SL` remains the structured truth / promotion authority
- `erdfa`/Kant-style layers package logical artifacts
- `Zelph` consumes/querys those artifacts
- `zkperf` is part of the proof-first execution/receipt framing

If `zkperf` is going to matter in the stack, the cleanest place to pin it next
is on the `SL` side as structured, receipt-bearing execution/proof material.

That should happen before deeper work on:

1. HF container/index fixture/spec details
2. richer `erdfa-publish-rs` manifest promotion
3. rehearsal harnesses that assume the `zkperf` role is already clear

## Intended role of zkperf on SL

`zkperf` should be treated as:

- execution/proof/trace material
- structured receipt-bearing evidence
- input to ranking/optimization layers only after it has a disciplined SL-side
  representation

It should **not** be treated as:

- a replacement for SL truth promotion
- free-floating embedding material
- a reason to bypass the existing shard/artifact contract

## 2026-10-17 formal-evidence graph alignment

The DA51 × SLR proof-spine work makes the separation more explicit. `zkperf`
receipts are sibling evidence on the same object/artifact graph as formal proof
receipts; they are not a lower-quality form of kernel proof and they do not become
formal proof because they share a DA51 address or formal demand reference.

```text
SLR ProofObligation
  |-- FormalProofDemand -> dashi-repo -> Lean/Agda checker -> formal evidence
  `-- runtime/empirical demand -> zkperf -> trace/benchmark receipt

both may attach to:
  DA51 semantic identity
  ITIR artifactId / artifactRevision
  shardId / contentDigest

but:
  zkperf trace/benchmark != theorem certificate
```

A zkperf linkage may carry opaque provenance joins such as:

- `da51Address`
- `formalDemandRef` / `obligationRef` when the run is related to that demand
- `artifactId` / `artifactRevision`
- content/run digest

Those joins permit navigation and selective reopening only. They do not set
`establishesProof`, legal applicability, claim truth, or security conclusions.

Canonical companion contract and fixture:

- `docs/planning/da51_slr_formal_evidence_artifact_contract_v1_20261017.md`
- `docs/planning/jmd_fixtures/da51_slr_formal_evidence_v1.example.json`

## Minimal roadmap

### Phase 1 — bounded SL-side representation

Define the smallest useful SL-facing representation for `zkperf`:

- trace identity
- source/run provenance
- structured metrics/events
- explicit links to related facts/artifacts when present
- receipt/proof refs

Acceptance target:

- one bounded contract note plus one tiny fixture/example

### Phase 2 — proof/receipt discipline

Make the proof/receipt role explicit:

- what counts as a `zkperf` receipt
- what stays observational vs promotable
- how SL references it without confusing it for truth itself

Acceptance target:

- one explicit boundary note:
  `zkperf` receipts inform/justify/trace, but do not directly promote truth

### Phase 3 — artifact linkage

Define how `zkperf` links to the existing artifact/shard stack:

- `artifactId` / `artifactRevision` linkage
- shard-level or run-level refs where appropriate
- no sink-path semantics leakage

Acceptance target:

- one simple linkage shape that can be attached to the current logical artifact
  contract without redesigning it

### Phase 4 — only then proceed to 1/2/3

After the above is pinned, proceed in the implementation-facing order already
discussed:

1. tiny HF container/index fixture/spec
2. `erdfa-publish-rs` richer manifest promotion path
3. small rehearsal harness in ITIR

## Guardrails

- keep `zkperf` features structured and receipt-bearing
- keep `zkperf` downstream of SL representation discipline before using it in
  spectral ranking
- do not let `zkperf` turn into an excuse for raw-vector retrieval
- do not let `zkperf` redefine the logical shard contract
- do not let DA51/demand/artifact linkage turn runtime evidence into formal proof
- do not let formal proof linkage turn a benchmark into a security conclusion

## Followthrough

That first gate is now complete:

- contract:
  `docs/planning/zkperf_on_sl_contract_v1_20260329.md`
- fixture:
  `docs/planning/jmd_fixtures/zkperf_on_sl_observation_v1.example.json`

The next bounded layer on top is now:

- `docs/planning/zkperf_stream_shard_contract_v1_20260330.md`

which carries observational `zkperf` windows into a stream/container/HF
publication path without changing `SL` truth authority.

The cross-repo DA51/SLR formal-evidence contract now supplies the common object /
artifact provenance seam used to relate that observational evidence to formal
work without collapsing the two evidence classes.
