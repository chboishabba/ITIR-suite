# AO-PNF-1 — Deterministic spectral hierarchy and concurrent fleet rounds

Status: planned contract, implementation follows in this branch; executable tests are the acceptance boundary. No spectral theorem, producer verification, or Agda/Lean theorem is claimed by the Python layer.

## Authority and reuse

- `dashi_agda` golden Agda surfaces are authoritative for formal claims; `dashi_lean4` mirrors them.
- This ITIR-suite change is an operational discriminator/scheduler contract. It does not implement or claim Marchenko–Pastur eigenvectors, a covariance eigensolver, Goemans–Williamson SDP proof, or cross-domain Yang–Mills/Navier–Stokes theorem.
- Reuse existing PNF work-packet, typed-reference, frontier, and governed handoff contracts. Candidate labels remain unverified and cannot grant promotion or dispatch authority.
- Existing external repository ownership and source attribution remain unchanged.

## Multi-scale PNF contract

The hierarchy has distinct levels; they must not be collapsed into a single topic label:

1. **Eigenspace**: a producer-supplied, continuous orthonormal spectral basis associated with covariance `Σ = (1/M) AAᵀ`. For MP analysis, only eigenvalues above the declared `λ+` edge are eligible. This Python module records eligibility metadata; it does not compute eigenvectors.
2. **Primary topics**: macro-quotients of eligible spectral representations under an explicit primary threshold.
3. **Subtopics**: local sub-eigen/orbit refinements, kept distinct from macro topics.
4. **Fibres**: complete-link groups; every pair in a fibre must satisfy the declared similarity threshold. Single-link chaining is not equivalent.
5. **Goals**: typed deliverables/lemmas/invariants with explicit blocker state. Only unblocked goals enter a dispatch frontier.

Requested rank K is restricted to 50 or 100. Missing producer evidence yields an unverified/held result, not synthetic eigenvectors or authority.

## Discriminator contract

Reject candidate world heads/eigen-motifs that are hexadecimal literals or memory-address dumps (`0x...`); raw UI/DOM tokens; comparative particles and grammatical noise such as `than`, `rather`, `ago`, `also`; or bare function-word/preposition/conjunction combinations with no substantive entity.

Admit candidates only when there is substantive evidence: a known domain-entity label, ontology/Wikidata label, capitalized proper noun, or formal AST symbol. A capitalization heuristic alone is not sufficient for promotion; outputs remain candidates with evidence/provenance.

Examples of valid-shaped heads include `YangMillsMassGap`, `NavierStokesTriadKN`, `GoemansWilliamsonMaxCut`, `DeonticObligationCalculus`, `DioxusReactiveTree`, `E8LatticeMoonshine`, and `BalabanRenormalization`.

## Fleet-round contract

A **round** is a simultaneous fleet tranche, not a worker slot. For each requested round r in 1..R:

1. Recompute the global Pareto frontier over eligible unblocked goals.
2. Select at most W=20 lanes; never confuse R=20 rounds with 20 total worker calls.
3. Each pair of concurrently selected lanes must carry an explicit `noTypedMeet` proof over typed AST support (files, symbols, lemmas). Missing or overlapping support blocks co-scheduling.
4. Dispatch the selected tranche concurrently; reconcile returns, retire completed goals, update blockers/world state, then compute the next round from the updated state.

Thus R=20 rounds and W=20 available lanes can permit up to 400 worker calls, but actual calls are bounded by frontier size, availability, proof-bearing independence, and completion/hold outcomes. The scheduler creates a deterministic dispatch plan only; this module does not call remote workers.

## Acceptance

From repository root:

```bash
python -m unittest discover -s tests -p 'test_pnf_spectral_packet.py' -v
python -m unittest discover -s tests -p 'test_fleet_round_runner.py' -v
```

Acceptance covers deterministic filtering, K validation, complete-link semantics, round-versus-worker accounting, W cap, pairwise proof fail-closed behavior, Pareto frontier selection, and bounded 20×20 planning. It does not constitute Agda/Lean kernel verification or a live concurrency test.

## Follow-up formal obligations

- Link producer-authenticated spectral metadata to golden Agda/Lean formalization without asserting Python receipts prove spectral claims.
- Formalize exact typed-support `noTypedMeet` relation and scheduler preservation in safe Agda, then mirror in Lean.
- Keep discrete Max Cut, Yang–Mills gauge dynamics, and Navier–Stokes commutator expansions as separate operators until a typed bridge theorem states and proves the exact map. Names or structural analogies are not a bridge.
