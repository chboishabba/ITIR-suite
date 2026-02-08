# Why ITIR Is Not SL

## Purpose
Resolve the recurring red flag: if ITIR is "constitutional," why is that not
the same as SensibLaw (SL)?

## Short Answer
SL is constitutional about content.
ITIR is constitutional about movement between systems.

They are orthogonal governance layers.

## Governance Axes

### SensibLaw (SL) Governs
- lexical authority (what text is present)
- structural authority (spans, clauses, references)
- provenance authority (where assertions came from)

### ITIR Governs
- cross-component contract boundaries
- routing and attachment rules for overlays
- authority separation between products
- failure semantics when boundaries are violated

## Non-Crossing Axioms
1. SL must not govern SB state compression policy, TIRC lens policy, or LES
   simulation policy.
2. ITIR must not rewrite SL text/structure/provenance.
3. Overlay outputs (interpret/reason layers) must not silently mutate substrate
   records.
4. Component-specific authorities (for example temporal segmentation ownership)
   remain local unless explicitly delegated by contract.

## Why This Separation Exists
- If SL governs everything, legal/substrate semantics leak into unrelated
  products and collapse product autonomy.
- If ITIR governs content semantics, ITIR becomes a covert truth engine and
  violates substrate ownership.
- Separation preserves inspectability, reversibility, and explicit authority
  boundaries.

## Canonical Wording
`ITIR-suite` is the orchestration/control plane for the product stack.
`ITIR` coordinates investigative/interpretive workflows across components.
`SL` remains the authoritative substrate for text/structure/provenance content.

## Anti-Patterns (Rejected)
- `ITIR = SL`
- `ITIR = operating system` (unqualified runtime meaning)
- `StatiBaker = ITIR`
- `Orchestration layer can mutate substrate semantics silently`
