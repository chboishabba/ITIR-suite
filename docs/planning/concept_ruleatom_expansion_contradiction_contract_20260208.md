# Concept vs RuleAtom + Expansion + Contradiction Contract (2026-02-08)

## Purpose
Lock three related architecture contracts to reduce semantic drift:
- `Concept` vs `RuleAtom` layer boundaries.
- Expansion Invariant formalization and cost model.
- Contradiction finder handling for cross-system norm conflicts.

This is a planning contract artifact only.

## 1) Concept vs RuleAtom contract

### Concept (Layer 0 semantic atom)
- Unit: semantic identity/equivalence atom.
- Role: compression and unification of lexical/phrase variants.
- Scope: substrate-level meaning anchors used across layers.
- Example shape: stable code/label/kind and external references.

### RuleAtom (Rule/logic layer atom)
- Unit: structured deontic logic statement.
- Role: deterministic computable norm decomposition.
- Scope: actor/modality/action/conditions/exceptions and provenance links.
- Example shape: `[actor] [modality] [action] IF [conditions] UNLESS [exceptions]`.

### Boundary invariant
- Concepts do not encode full deontic logic.
- RuleAtoms do not replace concept identity/equivalence ownership.
- RuleAtoms may reference concepts; concepts remain reusable substrate atoms.

## 2) Expansion Invariant formalization

Invariant:

> `Cost(expand(S)) < Cost(summarize(E))`

Where:
- `S` is a summary/fold/view.
- `E` is original raw evidence/events.

### Cost dimensions
- `C1` Cognitive: human effort to verify.
- `C2` Epistemic: truth-loss/hallucination risk.
- `C3` Computational: runtime/model/hardware cost.
- `C4` Coordination: social/process effort to re-establish trust/context.

### Contract requirements
- Summaries are indexes over immutable events, not replacements.
- Expansion path is deterministic pointer traversal.
- Expansion must not require probabilistic model inference.
- Loss profile must be explicit for each summary/fold surface.
- Corrections are additive events/annotations; no silent rewrite.

## 3) Contradiction finder contract (cross-system)

### Detection objective
Surface contradictions across legal/norm systems (including state and
customary/indigenous law lanes) without forced automatic resolution.

### Contradiction candidate conditions
- Opposing modalities (e.g., `MUST` vs `MUST_NOT`) or incompatible obligation
  outcomes.
- Overlapping subject/object/scope references.
- Overlapping effective conditions without an explicit resolving exception.

### Output contract
- Emit contradiction artifacts with:
  - participating RuleAtom IDs
  - source legal-system IDs
  - modality/scope overlap rationale
  - provenance pointers
  - status flag (`needs_reconciliation` by default)

### Reconciliation policy boundary
- Detection is deterministic and auditable.
- Resolution policy is controlled by explicit authority/reconciliation rules,
  not silent auto-merge.
- `Q7` governs precedence/reconciliation policy ratification.

## 4) Integration with existing contracts
- Uses shared envelope + receipt invariants from:
  - `docs/planning/itir_idempotency_dedupe_cooperation_20260208.md`
- Uses reducer ownership boundaries from:
  - `docs/planning/reducer_ownership_contract_20260208.md`
- Uses flow boundaries from:
  - `docs/planning/itir_consumption_matrix_20260208.md`
- Uses receipts-pack verification posture from:
  - `docs/planning/receipts_pack_automation_contract_20260208.md`

## 5) Immediate followthrough
- Add conformance checks that RuleAtom extraction and Concept linking remain
  layer-correct.
- Add expansion-invariant checks for receipts packs and SB SITREP surfaces.
- Add contradiction-finder test fixtures for cross-system modality clashes and
  `needs_reconciliation` output behavior.
