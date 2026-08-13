# Three Locks + Narrative Sovereignty Contract (2026-02-08)

## Purpose
Define enforceable quality gates for public-facing artifacts so "receipts over
rhetoric" remains real and cannot be gamed with jargon, ambiguity, or smooth
lies.

This is a planning/contract artifact only.

## Three Locks (required structure)
Every public artifact must include:
1. Thesis lock:
   A concise thesis line (target brevity, not magic numerology).
2. Receipt lock:
   At least one plain-speech receipt pointer that can be expanded and verified.
3. Action lock:
   One jurisdiction-aware next action that is concrete and doable.

## Explicit caution (ratified)
"12 words" is not a hard truth criterion.

Rules:
- Do not hard-fail strictly on exact word count.
- Do hard-fail on unverifiable, indecipherable, or deceptive framing.
- Use quality gates over superficial length gates.

## Thesis lock policy

### Length policy
- Target range: short sentence suitable for public framing.
- Suggested default band: 8-20 words.
- Outside-band text is warning-level unless it fails quality gates.

### Quality gates (hard-fail when violated)
- Must be semantically interpretable in plain language.
- Must map to at least one receipt-backed claim in the artifact.
- Must not contradict attached receipts/provenance.
- Must avoid ungrounded absolutist wording (unless explicitly scoped by receipts).

### Quality checks (minimum)
- Anchor check: thesis -> claim IDs -> receipt IDs exists.
- Jargon check: dense jargon ratio over threshold triggers failure or rewrite gate.
- Falsifiability check: thesis can be tested against included receipts.

## Receipt lock policy
- At least one plain-speech receipt summary + direct pointer.
- Receipt pointer must expand to raw IDs/provenance with deterministic traversal.
- Receipts must remain verifiable under bundle hash checks.
- No claim sentence may appear without at least one receipt linkage.

## Action lock policy
- Action must include jurisdiction context.
- Action must specify actor + step + venue + expected output.
- Action text must not imply legal certainty beyond receipt-backed scope.
- If jurisdiction unknown, action lock must explicitly state uncertainty and
  provide a "resolve jurisdiction" step.

## Frame Compiler enforcement (target)

### Hard fail conditions
- Missing any lock.
- Missing claim->receipt linkage.
- Thesis contradicts receipts.
- Action missing jurisdiction scope.

### Warning conditions
- Thesis outside target length band.
- High jargon density with still-valid receipt linkage.

### Build outputs
- `three_locks_report.json` with pass/fail reasons.
- Machine-readable lock status per artifact section.

## Integration with existing invariants
- Expansion Invariant still governs verification cost:
  expanding to raw receipts must be cheaper than re-summarizing.
- Promotion receipts still govern authority-crossing writes.
- No lock can bypass provenance or replay requirements.

## Related contracts
- `docs/planning/receipts_pack_automation_contract_20260208.md`
- `docs/planning/concept_ruleatom_expansion_contradiction_contract_20260208.md`
- `docs/planning/itir_idempotency_dedupe_cooperation_20260208.md`
- `docs/planning/tirc_sl_context_envelope_promotion_receipts_contract_20260208.md`

## Immediate followthrough
- Add Frame Compiler checks for lock presence + quality gates.
- Add tests for anti-gaming cases:
  - 12 indecipherable jargon words
  - smooth claim with no receipt anchors
  - jurisdiction-free action directive
