# DA51 formal artifact resolution weld (2026-10-17)

## Decision

Reuse the existing `shared-shard-artifact/v1` contract and the existing ITIR
file/HF/IPFS resolver. DA51 and proof routing do **not** introduce another
artifact locator or storage ontology.

The logical order remains:

```text
selector
  -> logical artifact + shard
  -> objectRefs[]
  -> chosen file/HF/IPFS sink
  -> fetched payload
  -> digest verification
  -> artifact-resolution-receipt/v1
```

The receipt is transport/provenance evidence only:

```text
CID != shard meaning
CID != theorem proof
content digest != semantic claim
artifact resolution receipt != kernel certification
artifact resolution receipt != legal authority
```

## Receipt schema

`itir_jmd_bridge.artifact_receipt` emits:

```text
schemaVersion          artifact-resolution-receipt/v1
logicalContractVersion shared-shard-artifact/v1
logicalArtifactRef     artifactId@artifactRevision#shardId
artifactId
artifactRevision
shardId
contentDigest
payloadDigest
payloadSizeBytes
objectRef
transport
verified               true
authority              transport-only
establishesProof       false
```

A receipt is marked verified only when:

- the logical shard itself declares `contentDigest`;
- fetched payload SHA-256 equals that logical shard digest;
- an object-ref digest, when supplied, agrees with the same logical digest;
- payload and object-ref sizes are strict non-negative integers and agree;
- the resolver supplies explicit fetch `sink` and `uri` equal to the selected
  object ref;
- for IPFS, `transport.cid` agrees with the selected `ipfs://` object ref and
  with observed CID metadata when present.

A container CID remains distinct from the digest of a member extracted from
that container.

## Operational flow

The existing resolver still performs the actual read:

```sh
python -m itir_jmd_bridge rehearse-remote-ipfs-bundle \
  --manifest-path promoted-manifest.json \
  --tar-path local-layout-reference.tar \
  --ipfs-uri ipfs://<cid> \
  --selector direct-shard=<proof-shard> \
  --output resolved-artifact.json
```

The canonical bridge command then turns that verified resolver output into the
portable receipt consumed by repository/proof infrastructure:

```sh
python -m itir_jmd_bridge emit-artifact-resolution-receipt \
  --resolved-json resolved-artifact.json \
  --output artifact-resolution-receipt.json
```

The module entrypoint remains available for direct library/diagnostic use, but
the package command above is the normal operator surface.

The receipt is intentionally serialization-small. It does not copy the proof,
legal proposition, PNF graph, or SLR Matter state.

## DA51 / dashi-repo handoff

`dashi-repo` may join the receipt to a DA51-addressed formal evidence row, but
only after the exact external demand/obligation/statement digest exists.

The portable identity partition is:

```text
DA51 address            typed cross-system logical identity
logicalArtifactRef      transport-neutral artifact/shard identity
IPFS CID                immutable transport object identity
contentDigest           resolved shard payload identity
statement_digest        exact formal proposition identity
kernel receipt          formal certification authority
SLR review/payment      legal/runtime payment authority
```

None substitutes for another.

Gateway response metadata is retained inside the canonical ITIR receipt as
transport provenance. Consumers should normalize only stable identity fields
needed by their own joins rather than promoting transient gateway URLs or
headers into logical artifact identity.

## Verification status

Focused RED-first source tests cover:

- logical identity binding;
- payload/content-digest equality;
- object-ref/logical-digest equality;
- strict integer size validation;
- required explicit fetch evidence;
- IPFS URI/CID equality;
- authority non-escalation;
- canonical package-CLI dispatch.

An isolated local harness executing the current hardened pure-Python receipt
logic on 2026-10-17 reports `6 passed`. This is not a claim that the complete
ITIR-suite test matrix or a live remote IPFS endpoint was rerun on this branch.
The existing 2026-03-30 Kubo/gateway receipt remains the prior live IPFS
publication/read-back evidence.
