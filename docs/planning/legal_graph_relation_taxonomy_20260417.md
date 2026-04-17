# Legal Graph Relation Taxonomy (2026-04-17)

This note defines the first bounded legal relation taxonomy for graphable edges.
It is a planning/spec surface only.

The goal is to keep legal-graph relations structural, typed, and replayable
before any builder or consumer treats them as graph truth.

## Canonical Relation Set

The first structural relation set is:

- `asserts`
- `denies`
- `rules`
- `cites`
- `applies`
- `distinguishes`
- `overrules`
- `supports`
- `contradicts`

These are the only named relations in scope for the first bounded taxonomy.

## Semantics

Relation semantics are structural and typed rather than text-classified.

That means:

- relation identity comes from node and edge structure, not from free-text
  intent detection
- text may remain evidence, explanation, or receipt material, but it does not
  define the relation class
- relation consumers should rely on typed wrappers, endpoint roles, and
  admissibility state
- the taxonomy is graphable only when the participating nodes already satisfy
  the structural boundary above `Phi`

## Boundary Rules

- do not infer relation class from lexical markers in notes, reasons, or
  narrative summaries
- do not widen the relation set without a separate planning update
- do not treat dense graph structure as proof of admissibility
- do not collapse composition, admissibility, and promotion into one step

The first legal graph should consume typed relation values from bounded,
admitted structures only.

## Lane Ownership

- Lane 8 owns this planning/spec surface only
- Lane 8 may refine the taxonomy wording, but not implementation surfaces
- any edge admissibility or graph builder work belongs to later lanes

## Next Surface

The canonical companion surface is:

- [Legal IR `Phi` Composition and Admissibility Boundary](legal_ir_phi_composition_admissibility_boundary_20260417.md)

That note governs how composed candidate nodes become admissible or remain
non-authoritative.
