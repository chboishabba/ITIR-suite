# Cross-System Latent-State Architecture

## Core theorem
`SensibLaw` remains the truth-construction layer:

`source -> annotation/signal -> candidate -> promoted`

Any latent or global graph layer is derived downstream of that pipeline and may
not replace promotion as the truth gate.

## Shared contracts
- `L(P)` contract:
  - latent state is a compressed, provenance-preserving, loss-bounded derived
    structure over promoted truth
  - every latent node or edge maps back to promoted records and, through them,
    to source anchors
  - latent outputs do not mutate truth without returning through explicit
    review and promotion
- Cross-system contract:
  - local systems contribute promoted truth sets `P_i`
  - global latent state is derived over `union_i P_i`
  - cross-system mappings live in `Phi`, not in silent semantic collapse
  - mapping outcomes must allow:
    `exact`, `partial`, `incompatible`, `undefined`

## Modules to define next
- latent graph schema:
  - bounded node/edge/constraint grammar over promoted records
- `Phi` mapping schema:
  - source system
  - target system
  - source motif/reference
  - target motif/reference
  - status
  - compatibility rationale
  - provenance refs
- mismatch report schema:
  - unresolved mappings
  - incompatibilities
  - contradiction/gluing diagnostics

## Governance
- Local `P_i` remains authoritative for its own system.
- Global latent state is analytical/compressive, not a superior truth store.
- Candidate motifs remain below promotion unless a lane defines explicit
  promotion semantics.
- Cross-system transfer claims require checked `Phi` rows and target-system
  compatibility, not intuition.

## Prototype boundary
- two bounded systems
- one small promoted motif family
- one checked `Phi` table
- one mismatch report
- no automatic truth merge

## Risks
- drifting from bounded mapping into universal ontology language
- treating motif alignment as proof of equivalence
- letting latent structure behave like hidden canonical truth
- skipping mismatch reporting when mappings are only partial or undefined
