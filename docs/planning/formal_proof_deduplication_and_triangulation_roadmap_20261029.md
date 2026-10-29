# Formal Proof Deduplication & Family Triangulation Roadmap (YM & NS)

**Date:** 2026-10-29  
**Status:** Approved Technical Architecture & Roadmap  
**Framework:** O / R / C / S / L / P / G / F  
**Target Topics:** Yang-Mills Mass Gap (YM), Navier-Stokes Smooth Regularity (NS), Monster Moonshine (3B Representation)  
**Database Authority:** TrueNAS PostgreSQL (`sensiblaw_sparse_ready_20260818`) — **SOLE AND ONLY DATABASE**

---

## 1. Context & Problem Framing

Historically, over 300–500 conversation threads have targeted the Clay Millennium problems (Yang-Mills and Navier-Stokes) across dozens of iterative sprints (`ClaySprint1` through `ClaySprint133`, `NSSprint1` through `NSSprint43`, `Round1` through `Round16`). 

Despite accumulating thousands of lines of verified code, proof closure was repeatedly delayed by **formal proliferation and algorithmic divergence**:
1. **Unidentified Consensus Baselines:** Workers re-implemented and re-checked the same 90%+ shared invariant code on every turn.
2. **Untracked Divergent Branches:** Threads split into 2 or 3 competing approaches for an intermediate lemma (e.g., whether temporal transfer terms are absorbed into the transfer matrix $T_k$ or tracked as spatial boundary defects) without explicitly comparing the trade-offs.
3. **Obscured Gap Intersections:** The true scientific blockers (e.g., the all-diameter Kotecký-Preiss polymer activity bound, or the finite-to-continuum BKM vorticity passage) were buried beneath surface syntax churn.

To halt this infinite cycle of disconnected sprints, the AST-level **Formal Family Triangulator** (`re_gpt.formal_triangulator`) and **Bounded Formal Slicer** (`re_gpt.formal_slicer`) were developed to deduplicate and triangulate formal families automatically.

---

## 2. Mathematical & Formal Architecture

The triangulator operates across an Agda module family $\mathcal{M} = \{M_1, M_2, \dots, M_k\}$ according to a 3-way partition:

```
                            Family of Modules M = {M_1, ..., M_k}
                                             │
             ┌───────────────────────────────┼──────────────────────────────┐
             ▼                               ▼                              ▼
 1. Shared Invariant Baseline     2. Divergent Constructions      3. Unresolved Gap Intersection
    (Proved True in ALL M_i)       (True in some, False in others)   (False / Blocked in ALL M_i)
             │                               │                              │
             ▼                               ▼                              ▼
    [OWNED / VERIFIED]             Reconcile Competing Branch     Target Scientific Blocker
    Do not re-ask or re-prove      Select optimal construction    Only actionable proving frontier
```

### Triangulation Sets
- **Shared Invariants ($\mathcal{I}$):**
  $$\mathcal{I} = \{ \phi \mid \forall M \in \mathcal{M}, M \vdash \phi \equiv \text{true} \}$$
  *Action:* Freeze and preserve as immutable preconditions; never prompt workers to re-prove these.
- **Divergent Constructions ($\mathcal{D}$):**
  $$\mathcal{D} = \{ (\phi, \{ M \mapsto \text{val}_M(\phi) \}) \mid \exists M_a, M_b \in \mathcal{M} : \text{val}_{M_a}(\phi) \neq \text{val}_{M_b}(\phi) \}$$
  *Action:* Expose competing hypotheses side-by-side so workers can select or synthesize the dominant route.
- **Unresolved Gap Intersection ($\mathcal{G}$):**
  $$\mathcal{G} = \{ \psi \mid \forall M \in \mathcal{M}, M \vdash \psi \equiv \text{false} \}$$
  *Action:* Dispatch strictly these universal blockers as the sole actionable proving deliverables.

---

## 3. Empirical Results Across Live In-Repo Families

Running `triangulate_formal_family` on live in-repo Agda modules in `/home/c/.cache/dashi-agda29/dashi-shadow/DASHI/` isolated the exact formal status of each problem domain:

### A. Yang-Mills Mass Gap (`ClaySprintSeventyEightYM*.agda` — 9 files)
- **Shared Invariants (10 properties proved true across all 9 variants):**
  - `MixedPlaquettesAreTransferMatrixFaceAction`
  - `TemporalMeasureFactorizationLambdaOne`
  - `TemporalSupportNonCreationForSlabs`
  - `SpatialOnlyBlockingPreservesTemporalLinks`
  - `paper12bB6A1A3RouteRecorded`
  - `fineLatticeSpatialEtaSixDoesNotClose` (formally proves $\eta = 6$ fine lattice fails because $6q = 1.39069 > 1$)
  - `KPEntropyFromL2BlockingOrientations`
  - `PolymerDefinedOnBlockedLattice`
  - `theoremRemainsOpenOrConditional`
- **Divergent Construction Branches (2 competing branches):**
  1. `temporalTermsAbsorbedIntoTransferMatrix`: Split between absorbing temporal links directly into $T_k$ vs tracking residual boundary defect faces.
  2. `KPIncompatibilityGraphUsesOnlySpatialAdjacency`: Split between spatial-only graph adjacency vs slab-extended adjacency.
- **Unresolved Gap Intersection (The 22 True Scientific Blockers):**
  - `AllDiameterWeightedKP` (Kotecký-Preiss polymer activity bound across all diameters)
  - `BalabanPartitionIdentityCompatibleWithTemporalTransferMatrix`
  - `ContinuumMassGapTransfer`
  - `LatticeMassGapFromAnisotropicKP`
  - `TemporalEntropyQuotientHalvesGeneric4DCount`
  - `clayYangMillsPromoted`

### B. Navier-Stokes Smooth Regularity (`ClayNS*` & `NSRegularity*` — 5 files)
- **Shared Invariants (11 properties proved true across all 5 variants):**
  - `lerayWeakSolutionBranchAvailable` (Leray weak solutions verified)
  - `candidateSelfContainedPacketRecorded` (CKN, ESS, LRT, A1–A9 package verified)
  - `finiteDepthRegularityRungsRecorded` (finite-depth energy, vorticity, and BKM rungs closed)
  - `globalSmoothRegularityProved` (at finite-depth / classical level)
  - `criticalBesovNextTargetRecorded`
  - `theoremShapeGrammarGapClosedFlag`
- **Divergent Construction Branches:**
  - `0` algorithmic divergences (complete structural consensus on the tower).
- **Unresolved Gap Intersection (The 3 True Scientific Blockers):**
  - `clayNavierStokesPromoted`
  - `smoothGlobalRegularityProved` (finite-to-continuum BKM passage)
  - `terminalClayClaimPromoted`

### C. Monster Moonshine (`Base369Monster3BRepresentationBidiSearchRound<N>Exact.agda`)
- **Consensus Invariants (23 properties):** Corner geometry, Fin8 $\leftrightarrow$ Corner3 bijection, $90 \cong \text{Completed10} \times T^2$, $729 \cong \text{Corner8} \times \text{Completed10} \times T^2 + T^2$.
- **Unresolved Gap Intersection (The 4 Blockers):**
  - `actualZetaRecognition`
  - `fixedRegularBlockRecognition`
  - `literalResidualFiftyThree`
  - `outerFin90CompletedTenTritSquareRecognition`

---

## 4. Integration with PostgreSQL & Topic Coalescence

Per the **Sole Database Mandate** ([SINGLE_CANONICAL_STORE_AND_PG_SPINE_ROADMAP.md](../architecture/SINGLE_CANONICAL_STORE_AND_PG_SPINE_ROADMAP.md)), all operational data lives exclusively in PostgreSQL `sensiblaw_sparse_ready_20260818`:

1. **Automatic Coalescence Trigger:** When `re_gpt.postgres_coalescence.discover_coalescence_clusters` identifies overlapping threads ($\ge 0.75$ Jaccard similarity on PNF statement factors), `build_coalesced_world_capsule` automatically invokes `triangulate_formal_family` on the associated formal files.
2. **Unified World Capsule:** The capsule directly injects:
   - Consensus Invariants (`[OWNED / VERIFIED]`)
   - Divergent Branches (with per-module approach summaries)
   - Universal Blocker Checklist (`[BLOCKED / UNPROVEN]`)
3. **Zero Redundant Turns:** The remote worker receives the exact deduplicated gap, eliminating the need to re-derive foundations or generate redundant `Round<N+1>` files.

---

## 5. Verification Checklist & Milestones

- [x] Implement AST declaration grouper in `re_gpt.formal_slicer` (preserves multi-line signatures and clauses).
- [x] Implement bounded formal slicer with transitive declaration closures and dead-code exclusion (`re_gpt.formal_slicer.build_pruned_formal_slice`).
- [x] Implement formal family triangulator (`re_gpt.formal_triangulator.triangulate_formal_family`).
- [x] Extend triangulator to support top-level Booleans, record equality proofs (`IsTrue`/`IsFalse`), and `data ...OpenGate` constructors.
- [x] Integrate triangulator into topic coalescence capsule generator (`re_gpt.postgres_coalescence.build_coalesced_world_capsule`).
- [x] Run empirical verification across real YM 78, NS Regularity, and Moonshine families in `dashi-shadow`.
- [x] Unit test suite passing 100% (26 unit tests in `reverse-engineered-chatgpt` across slicer, triangulator, coalescence, and PostgreSQL registration).
