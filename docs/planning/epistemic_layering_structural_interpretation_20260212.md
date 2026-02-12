# Epistemic Layering Addendum: Structural Interpretation (2026-02-12)

## Origin
- `origin_online_id`: `698bdf6e-43f8-839c-9089-34ee3d3338dd`
- `origin_note`: Documented from discussion context only; no live fetch in this step.

## Problem
`WrongType` and `ValueFrame` layering is already explicit in core ontology docs, but recent graph work exposed a terminology risk:
- "truth spine" implies ontological endorsement
- current extraction outputs are deterministic, but still profile/parser-mediated interpretations

## Decision
Use this layering language in docs and UI contracts:

1. **Identity and provenance substrate**
   - immutable anchors, spans, source references, ids, hashes
2. **Structural interpretation layer**
   - dependency-derived subject/action/object/chains
   - deterministic, replayable, profile-versioned
   - not causal and not a final truth claim
3. **Normative and evaluative overlays**
   - wrong types, protected interests, value frames, remedies

## Terminology standard
Prefer:
- `provenance spine`
- `identity substrate`
- `structural extraction`

Avoid:
- `truth spine`
- wording that implies endorsement beyond extraction contract

## Invariants
1. Structural extraction must declare parser/profile provenance.
2. Structural extraction is additive over identity substrate, not a replacement for source text.
3. Evaluative overlays must remain explicit and typed (`WrongType`, `ValueFrame`, etc.).
4. UI must not imply that structural edges equal adjudicated truth.

## Relationship to existing ontology docs
This addendum does not change `L0-L6`. It clarifies interpretation boundaries across:
- `L0` text/provenance
- structural extraction outputs used by graph views
- `L4-L6` legal/evaluative overlays

## Follow-up implementation hooks
- Surface profile id/hash in graph headers.
- Add explicit "projection scope" badge in graph views.
- Keep structural and evidence edge families visually distinct.
