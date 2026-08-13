# Global Latent Legal State Across Systems (2026-03-27)

## Purpose
Extend the single-system `L(P)` discipline into the cross-system case without
flattening multiple legal traditions into one hidden universal ontology.

This note is planning-only. It does not introduce new runtime behavior.

## Source Context
- source: current working turn
- informed by the archived thread:
  - title: `Zero Trust Ontology`
  - online UUID: `69c68637-ca2c-839e-826c-f5e8a034ed2e`
  - canonical thread ID: `c2571b2b17183df38dd03704cf6e34f7bee44392`
  - source used: `db`
- adjacent governing notes:
  - `docs/planning/latent_state_over_promoted_truth_20260327.md`
  - `docs/planning/motif_candidate_promotion_legal_tree_20260327.md`
  - `docs/architecture/admissibility_lattice.md`
  - `docs/planning/concept_ruleatom_expansion_contradiction_contract_20260208.md`

## Main Decision
The safe cross-system reading is not one global promoted set with erased
boundaries. It is:

- multiple locally promoted truth sets `P_i`
- one derived global latent structure over their union
- explicit cross-system mappings `Phi`
- explicit incompatibility and undefined cases

So the disciplined form is:

`P = union_i P_i`

and:

`L_global = (G, Phi, C)`

where:

- `G` is a graph over promoted records or promoted motif-like structures drawn
  from multiple systems
- `Phi` is a mapping layer between systems
- `C` is the set of local and cross-system constraints

## Local Truth Still Comes First
Each `P_i` remains authoritative only for its own system under the usual
promotion rules.

Examples may include:

- common-law promoted state
- civil-law promoted state
- Islamic-law promoted state
- customary-law promoted state

The global layer does not erase or outrank those local truth-bearing surfaces.

## Mapping Layer `Phi`
The key new object is the mapping layer between systems.

The repo should treat `Phi` as:

- translation candidates
- analogies
- partial correspondences
- incompatibility markers
- explicitly undefined relationships where no safe mapping exists

The safe status set is:

- `exact`
- `partial`
- `incompatible`
- `undefined`

This means the repo must not assume every motif or legal structure has a clean
cross-system equivalent.

## Motif Classes Across Systems
If motifs are used in this lane, the safe reading is:

- local motifs still depend on the local promotion and latent-state discipline
- a global motif class is an alignment surface across systems, not automatic
  identity
- the mapping relation sits in `Phi`, not in wishful semantic collapse

So the repo should read:

`motif_class = aligned structures across systems, subject to Phi`

not:

`motif_class = universal legal primitive`

## Transfer Operation
Any motif or structure transfer across systems must be treated as a checked
operation, not a free rewrite.

At minimum it should require:

- a source structure in one `P_i`-derived latent surface
- a target candidate in another `P_j`-derived latent surface
- compatibility under target-system constraints
- explicit handling of exact, partial, incompatible, or undefined results

## Constraint Layer `C`
The constraint set should include:

- local consistency rules within each system
- cross-system compatibility or mismatch rules
- explicit conflict markers where systems do not glue cleanly

This is where the repo should keep cross-system contradiction detection rather
than hiding mismatches inside vague ontology language.

## Geometry / DASHI Reading
The global latent layer is an acceptable place for:

- MDL-governed compression over the multi-system promoted basis
- equivalence-class discovery that remains provenance-preserving
- valid transforms that preserve anchors and respect local-system constraints

But it is not acceptable for:

- overwriting local promoted truth
- forcing incompatible systems into one canonical rule set
- treating cross-system compression as proof of universal equivalence

## Cohomology Reading
If cohomology language is used here, the safe reading is again diagnostic:

- obstructions to consistent cross-system gluing
- cycles or mismatches in the mapping layer
- irreducible differences between systems

This can help explain why some legal motifs align cleanly and others do not.
It is still not a substitute for promotion semantics.

## Non-Goals
- not a claim that a full `Phi` schema already exists
- not a claim that the repo has solved cross-cultural legal alignment
- not a claim that every legal tradition can be losslessly unified
- not a claim that the repo should pursue a universal ontology before bounded
  mapping contracts exist

## Followthrough
- if a future cross-system latent-state lane is proposed, require:
  - one bounded `Phi` mapping contract
  - one incompatibility/undefined status contract
  - one provenance rule showing every global node maps back to some `P_i`
  - one contradiction-detection surface for cross-system mismatch
- if a prototype is built, start with:
  - two bounded systems, not "all cultures"
  - one small promoted motif family
  - one checked mapping table with exact/partial/incompatible/undefined status
  - one mismatch report instead of any automatic truth merge
