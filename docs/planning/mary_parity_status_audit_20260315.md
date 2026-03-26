# Mary-Parity Status Audit

Date: 2026-03-15
Purpose: record the current parity position after the Wave 1 through Wave 5
acceptance gates were implemented and greened, and identify what is still thin
enough to warrant another loop before calling the operator experience "full
parity".

## Current gate status

Passing canonical acceptance waves:
- `wave1_legal`
- `wave2_balanced`
- `wave3_trauma_advocacy`
- `wave3_public_knowledge`
- `wave4_family_law`
- `wave4_medical_regulatory`
- `wave5_handoff_false_coherence`

Current coverage shape:
- Waves 1 to 4 are mostly synthetic-plus-curated fixture families.
- Wave 5 now includes both synthetic and repo-curated real transcript fixtures.
- Transcript and AU remain the only real upstream workflow families feeding the
  Mary-parity substrate directly.

## What is genuinely covered now

### 1. Substrate parity is credible
- canonical seam is real and test-backed:
  `source -> excerpt -> statement -> observation -> event/fact -> review bundle`
- observations remain canonical
- events remain derived and evidence-backed
- persisted workflow-run to fact-run reopen works

### 2. Acceptance is no longer hand-wavy
- story pressure is encoded as named wave gates
- pass/partial/fail is fixture-backed rather than intuition-backed
- gap tags now serve as a real backlog source when a wave is not green

### 3. Operator review is materially real
- review queue
- contested summary
- chronology grouping
- source-centric reopen flow
- bounded workbench views
- read-only/non-reasoning posture

### 4. Expanded role/risk families are present
- legal operator wave
- balanced ITIR wave
- trauma/advocacy wave
- contested wiki/Wikidata/public-knowledge wave
- family-law / cross-side wave
- medical / regulatory wave
- personal-to-professional handoff / false-coherence wave

## What is still thin

### 1. Real-fixture depth is uneven
Strongest:
- transcript
- AU
- Wave 5 handoff/false-coherence now has curated real transcript fixtures

Still thin:
- public-knowledge / wiki / Wikidata families remain mostly synthetic with one
  stronger GWB-style anchor
- family-law and medical/regulatory are still synthetic-only proving families

Implication:
- parity is credible as a contract and review surface
- parity is still weaker as a "real-run diversity" claim for some newer waves

### 2. Workbench parity is backend-credible but still ergonomically thin
Covered:
- bounded read-only views
- source-centric reopen
- chronology triage
- handoff/public-claim/fidelity/alignment/operator views

Still thin:
- no richer matter-centric navigation model
- no stronger role-tailored presets beyond view families
- no handoff/export polish layer tuned for actual day-to-day operators

Implication:
- backend/workbench parity is good enough to test
- not yet the same as polished everyday operator parity

### 3. Real extraction breadth is still narrower than the acceptance families
Covered:
- AU legal/procedural visibility is stronger
- transcript and synthetic fixture metadata now carry bounded structured
  distinctions for assertions, outcomes, provenance classes, and uncertainty

Still thin:
- some later waves rely on explicit fixture/adaptor annotations more than broad
  naturally-produced upstream semantics
- this is acceptable for bounded parity gating, but it means "coverage exists"
  more than "pipeline breadth is naturally broad"

### 4. Corpus-to-work-product coverage is not yet a first-class lane
Covered:
- the repo now has dense transcript/AU substrate artifacts and persisted
  fact-review runs that are suitable as a source side for later comparison

Still thin:
- there is not yet a repo-stable affidavit/declaration coverage review surface
  showing what source-grounded material made it into a filing draft, what is
  partial, and what appears omitted

Implication:
- Mary parity is now strong enough to support that next step
- the next legal-operator push should include work-product coverage accounting,
  not just more extraction density

## Overall assessment

### Parity estimate
- backend/substrate parity: `~90%`
- backend operator-review parity: `~80-85%`
- full day-to-day operator parity: `~75-80%`

Interpretation:
- the substrate is no longer the bottleneck
- the next limiting factor is breadth and polish, not architecture

## Recommended next priority order

### 1. Real-fixture broadening where waves are still synthetic-heavy
Priority order:
- `wave3_public_knowledge`
- `wave4_family_law`
- `wave4_medical_regulatory`

Goal:
- add at least one more repo-curated "real" fixture anchor to each of those
  families before starting another large new family

### 2. Operator/workbench parity polish
Focus areas:
- matter-centric reopen/navigation
- stronger export/handoff posture
- clearer role presets for:
  - lawyer
  - support worker
  - wiki moderator / claim worker
  - family-law / medical reviewers

### 3. Corpus-to-affidavit coverage lane
Focus areas:
- compare an affidavit/declaration draft against a provenance-bearing source
  substrate
- surface covered / partial / missing-review / contested / unsupported rows
- preserve abstention instead of treating all non-inclusions as omissions

### 4. Gap audit before new semantic/reasoning work
Use this question:
- are the next missing pieces better solved by another acceptance family,
  by a real-fixture expansion, or by workbench/export polish?

Default:
- do not add new reasoning/state-transition layers until the answer is
  "operator/workbench polish", not "fixture breadth" or "review visibility"

## Suggested immediate next loop

Best next loop:
1. broaden `wave3_public_knowledge` with another curated real anchor
2. add one real anchor to either family-law or medical/regulatory
3. define the first bounded affidavit/declaration coverage review lane over the
   existing AU/Mary source substrate
4. run a workbench/export ergonomics audit across all green waves

This keeps the current acceptance-first discipline intact while pushing parity
from "credible and broad" toward "defensible and operator-ready".
