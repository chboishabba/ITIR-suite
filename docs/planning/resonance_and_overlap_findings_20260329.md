# Resonance and Overlap findings - 2026-03-29

source
- ChatGPT online UUID: `69c8913d-5240-839b-9bf8-d757ae8b208a`
- title: `Resonance and Overlap`
- canonical thread ID: `343e73cc6a60cd1f29be15301a69aed0fa682002`
- source used: `db` after async pull on 2026-03-29

read
- `CLOCK` should be modeled as a cyclic lift of `DASHI`, not as a dihedral construction.
- Safe algebraic reading:
  - `DASHI ≅ Z/3`
  - `CLOCK ≅ Z/6`
  - if `g` is the one-step `CLOCK` rotation, then `g^2` is the coarse `DASHI` step
  - `CLOCK` is the cyclic square-root lift of `DASHI`, not a symmetry involution
- Complex realization:
  - `DASHI` aligns with cube roots of unity
  - `CLOCK` aligns with sixth roots of unity, with step `e^(i*pi/3)`
- Phase by itself is only kinematics. Admissible dynamics require:
  - cone admissibility
  - contractive / Lyapunov directionality
  - MDL descent
- The extra `CLOCK` bit should be read as microphase / half-step refinement, not as a dihedral reversal operator.

master schema
- Let `S` be a state space with:
  - a `CLOCK` phase map
  - a cone admissibility predicate
  - a contractive / Lyapunov dynamic
  - an MDL functional
- Physical evolution is `T : S -> S` with:
  - `phase : S -> HexTruth`
  - `coarse : HexTruth -> TriTruth`
  - `coarse(phase(T^2 x)) = rotateTri(coarse(phase(x)))`
- The retrieval / proposal stack should not claim more than this schema supports.

parallel reading
- The same refinement/projection pattern now appears in the retrieval stack:
  - `CLOCK -> DASHI` is fine phase -> coarse phase
  - `ZOS -> SL` is proposal space -> promoted truth
- Safe analogy:
  - `CLOCK` = microphase / proposal-level variation
  - `DASHI` = coarse admissible phase
  - `ZOS` = possible answers / proposal layer
  - `SL` = admissible promoted truth
- This is only a structural analogy. It does not grant `ZOS` truth authority.

implication
- Keep `CLOCK`/`DASHI` phase discussion tied to cyclic lift, cone admissibility, contraction, and MDL.
- Do not let later retrieval or resonance work smuggle in a dihedral or purely combinatorial reading.
- The missing retrieval-side counterpart is an explicit admissibility filter after ranking:
  - candidate/proposal set first
  - admissibility / promotion boundary second
  - promoted outputs only after that check
