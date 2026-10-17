# xPollenation neighbourhood artifact weld — 2026-10-17

## Decision

xPollenation is a typed cross-domain discovery/enrichment graph. It is not a new storage system and it does not route by CID.

Canonical order:

```text
external/domain coordinates
QID / ChEBI / Rhea / UniProt / PDB / SABIO / PMID / DOI / OEIS
        ↓
dashi.xpollenation-neighbourhood/v1
        ↓
shared-shard-artifact/v1
        ↓
logical shard identity + contentDigest + objectRefs[]
        ↓
file / HF / IPFS
        ↓
artifact-resolution-receipt/v1
```

`itir_jmd_bridge.xpollenation_artifact` performs only the middle projection. It canonicalizes edge order, serializes the neighbourhood deterministically, hashes the exact payload bytes, and emits one logical `neighbourhood` shard. `objectRefs[]` starts empty; the existing publisher/pinning paths attach file/HF/IPFS refs later without changing the logical shard.

## Command

```bash
python -m itir_jmd_bridge emit-xpollenation-artifact \
  --input RHEA-19897.json \
  --artifact-id xpollenation:bh4:RHEA-19897 \
  --output RHEA-19897.shared-shard.json
```

After the payload has been published/resolved through an existing sink, the existing command emits the transport receipt:

```bash
python -m itir_jmd_bridge emit-artifact-resolution-receipt \
  --resolved-json resolved-artifact.json \
  --output artifact-resolution-receipt.json
```

## Authority boundary

```text
xPollenation edge != same object unless separately verified
QID adjacency != theorem/scientific truth
OEIS match != semantic equivalence
logicalArtifactRef != DA51 identity
CID != shard meaning
CID != scientific admissibility
contentDigest != claim truth
artifact resolution != proof
artifact resolution != consumer payment
```

The neighbourhood itself must carry:

```text
authority = navigation-enrichment-only
establishesProof = false
establishesPayment = false
```

Every edge must carry `promotionAllowed=false`.

## BH4 acceptance path

The first consumer is the BH4 finite reaction panel in `dashi_agda`:

```text
12 finite Rhea columns
 -> typed Rhea/ChEBI/UniProt/SABIO/PDB/QID neighbourhoods
 -> one logical xPollenation artifact per reaction
 -> optional IPFS mirror / CID
 -> artifact-resolution-receipt
 -> dashi-repo xPollenation store
 -> existing BH4 kinetic payment gates
```

The transport layer does not decide whether a kinetic datum can constrain an in-vivo reaction flux.
