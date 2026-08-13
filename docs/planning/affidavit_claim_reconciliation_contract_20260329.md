# Affidavit Claim Reconciliation Contract (2026-03-29)

## Purpose
Pin the next quality-improvement direction for the affidavit local-first
proving slice.

The current lane is already useful as a provenance-first comparison surface.
The next improvement is to move from similarity-led coverage bucketing toward
relation-led claim reconciliation.

This note does not claim the repo already implements the full reconciler
described below. It defines the intended next contract.

Current repo status after the first followthrough patch:
- the proving-slice read model now emits:
  - `relation_type`
  - `relation_root`
  - `relation_leaf`
  - `explanation`
  - `missing_dimensions`
- the proving-slice sections now expose explicit non-resolving subclasses
  instead of a stable `weakly_addressed` output section
- the upstream builder now also persists the richer relation typing at source:
  contested comparison rows now carry `relation_type`, `relation_root`,
  `relation_leaf`, `primary_target_component`, `explanation`, and
  `missing_dimensions`, with read-model derivation retained as a
  backward-compatible fallback only for older rows

## Problem

The current Google Docs affidavit/response run is:
- highly responsive
- provenance-visible
- conservative

But it is still weak at deciding what kind of response relation is present.

Current quality gap:
- explicit disputes can still hide under weaker coverage categories
- nearby/adjacent events can look like support
- partial overlap, substitution, and procedural response are not fully
  separated as first-class relation types
- bucket assignment still leans too heavily on match strength instead of a
  typed proposition/response relation
- the live `weakly_addressed` bucket is still overloaded and should now be
  treated as a defect bucket, not a stable target state
- cross-side duplicate and near-duplicate claims are still under-modeled:
  the lane can confuse same-incident sibling leaves, shared-root restatements,
  later contextual additions, and true contradiction

## Johl / Mary-parity interpretation

The Johl affidavit / response pair should now be treated as the primary
bounded test-bed for the next classifier pass.

Reason:
- it contains shared-root claims stated on both sides
- it contains same-incident sibling leaves inside composite paragraphs
- it contains contextual additions and later qualifications alongside direct
  support and contradiction
- it aligns with the family-law / cross-side / Mary-parity user-story pressure

Interpretation rule:
- do not flatten John-side and Johl-side wording into one canonical sentence
- do cluster materially duplicate or near-duplicate leaves under one shared
  claim root or incident root
- do classify support, qualification, contradiction, and adjacent-event
  relations at the leaf level inside that root

## Design reading

The next improvement is not a larger ontology.

It is a bounded `claim reconciliation` layer between extracted atoms and the
coverage review bucket surface.

Updated conceptual path:

`text -> tokens -> rules -> atoms -> claim reconciliation -> coverage graph -> output buckets`

## Required output per affidavit proposition

For each affidavit proposition, the lane should eventually produce:
- one normalized proposition record
- zero or more normalized candidate response-unit records
- one dominant relation classification
- explicit provenance spans
- explicit confidence
- explicit review trigger when ambiguity remains high

For cross-side material, the lane should also eventually produce:
- one optional shared `claim_root` or `incident_root`
- one side-local `leaf_claim`
- one explicit leaf-to-leaf relation:
  duplicate, support, qualification, contradiction, adjacent event, or
  procedural framing
- one typed authority reading for the matched material:
  source-local assertion, shared-text duplicate, procedural record, or later
  contextual addition

## Minimal normalized proposition shape

Each proposition should aim to expose:
- `proposition_id`
- `span`
- `proposition_type`
- `subject`
- `subject_role`
- `action_lemma`
- `object`
- `object_role`
- `time_expression`
- `location_expression`
- `modality`
- `polarity`
- `domain`
- `confidence`

Closed first-pass proposition types:
- `factual_event`
- `subjective_feeling`
- `allegation`
- `denial`
- `procedural_fact`
- `legal_claim`
- `relationship_state`
- `capability_statement`
- `care_or_role_performance`

## Minimal normalized response-unit shape

Each candidate response unit should aim to expose:
- `response_unit_id`
- `span`
- `response_act`
- `subject`
- `subject_role`
- `action_lemma`
- `object`
- `time_expression`
- `modality`
- `polarity`
- `explicit_dispute_flag`
- `explicit_support_flag`
- `procedural_frame_flag`
- `confidence`

Closed first-pass response acts:
- `confirm`
- `deny`
- `explain`
- `qualify`
- `redirect`
- `substitute`
- `adjacent_narrative`
- `procedural_frame`
- `non_response`

## Relation classifier

Every proposition-response pair should be reduced to exactly one relation:
- `exact_support`
- `equivalent_support`
- `explicit_dispute`
- `implicit_dispute`
- `partial_overlap`
- `adjacent_event`
- `substitution`
- `procedural_nonanswer`
- `unrelated`

These relation types are the intended next quality boundary.

For cross-side clustered reading, duplicate-root detection should happen
before final support or contradiction resolution where the material clearly
belongs to the same incident or claim family.

## Dominant relation precedence

When multiple candidate response units exist, the dominant relation should be
resolved with this order:

1. `exact_support`
2. `explicit_dispute`
3. `equivalent_support`
4. `implicit_dispute`
5. `partial_overlap`
6. `adjacent_event`
7. `substitution`
8. `procedural_nonanswer`
9. `unrelated`

This order is deliberate. It gives explicit disputes precedence over weaker
semantic closeness.

## Bucket mapping

The user-facing bucket surface should eventually resolve from dominant
relation, not only from similarity-driven coverage labels.

Target bucket mapping:
- `supported`:
  - `exact_support`
  - `equivalent_support`
- `disputed`:
  - `explicit_dispute`
  - `implicit_dispute`
- `needs_clarification`:
  - `partial_overlap`
  - `adjacent_event`
  - `substitution`
- `non_substantive_response`:
  - `procedural_nonanswer`
- `missing`:
  - `unrelated`
  - no candidate above threshold

The immediate interpretation rule is:
- eliminate `weakly_addressed` as a forward-looking target bucket
- treat current `weakly_addressed` rows as transitional `v0` outputs that
  must be redistributed into:
  - `partial_support`
  - `adjacent_event`
  - `substitution`
  - `non_substantive_response`

So the next classifier pass should move toward this operator-facing reading:
- `supported`
- `disputed`
- `partial_support`
- `adjacent_event`
- `substitution`
- `non_substantive_response`
- `missing`

The temporary proving-slice `needs_clarification` umbrella may still remain as
an optional rollup view, but not as the only explanation surface for mixed
rows.

## Acceptance criteria

For each affidavit proposition, the next quality step should aim to emit:
- one explicit `relation_type`
- one dominant matched response unit, or explicit `missing`
- one explanation string grounded in source text
- one `missing_dimension` list when alignment is incomplete

A classification is acceptable only when:
- subject alignment is checked explicitly
- action alignment is checked explicitly
- polarity alignment is checked explicitly
- explanation cites the matched response row or states that no adequate row
  exists

Minimum explanation surface per row:
- `classification`
- `matched_response`
- `reason`
- `missing_dimension`

Preferred missing dimensions:
- `subject`
- `action`
- `object`
- `time`
- `direct_response`

## Minimal first-version rule families

### A. Explicit denial

If the response contains phrases like:
- `I dispute that`
- `I deny that`
- `this is not true`
- `that did not happen`

and subject/event family aligns, classify as `explicit_dispute` unless a
stronger unambiguous support relation exists.

### B. Exact / equivalent support

If subject, action, object, and polarity align, classify as `exact_support`
or `equivalent_support`.

### C. Substitution

If subject aligns and event family aligns, but action differs materially,
classify as `substitution`.

This is the keyboard-vs-audio type failure the current lane can still blur.

Important Johl-pair clarification:
- a same-incident sibling claim should not be forced into `substitution` if
  the response corpus already contains a direct matching clause elsewhere
- the first fix should be duplicate-root and sibling-leaf alignment before
  broadening `substitution`

### D. Adjacent event

If actors/time are close but the core action or object differs, classify as
`adjacent_event`.

### E. Procedural nonanswer

If the response is mostly framing/procedural/rhetorical, classify as
`procedural_nonanswer`.

### F. Partial overlap

If some but not enough dimensions align to resolve the proposition, classify
as `partial_overlap`.

## Review triggers

Human review should remain mandatory when:
- both support and dispute score highly
- proposition modality and response modality differ sharply
- time matters but time alignment is absent
- semantic closeness is high while structure alignment is weak
- the top two relation candidates are too close
- a current `weakly_addressed`-style row cannot be cleanly separated into
  partial support, adjacent event, substitution, or procedural nonanswer

## Relationship to current repo state

The current repo does not yet expose a dedicated proposition parser, response
parser, relation classifier, or bucket resolver as separate modules.

What exists today:
- proposition splitting
- candidate retrieval by lexical/provenance-first comparison
- response-role and support/conflict signals
- grouped proving-slice read model
- progress and trace observability

So the current lane should be read as:
- `v0`: provenance-first coverage review

And the intended next improvement is:
- `v1`: bounded relation-driven claim reconciliation

## Immediate implementation reading

Do not jump straight to a full standalone micro-architecture.

The smallest useful next implementation is:
- keep existing extraction
- add typed proposition/response normalization inside the affidavit lane
- add a bounded relation classifier over existing candidate pairs
- resolve dominant relation before final bucketing
- preserve provenance-first review traces throughout
- replace the current overloaded `weakly_addressed` bucket with the smaller
  relation-led classes above
- add operator-facing explanation strings and missing-dimension reporting

What is now done:
- proving-slice read-model output now carries explicit relation-tree fields
  and per-row explanation payloads
- the proving-slice read model now also emits explicit `relation_type` and
  resolves final section bucketing from typed relation output rather than only
  from coverage/support heuristics

What remains:
- add duplicate-root / incident-cluster handling so cross-side restatements
  and sibling leaves stop cross-swapping into the wrong support or dispute row

First bounded duplicate-root followthrough now landed:
- the builder now preserves a shared claim root when a direct or near-duplicate
  clause is present alongside a different contextual clause
- row output now also exposes:
  - `claim_root_id`
  - `claim_root_text`
  - `claim_root_basis`
  - `alternate_context_excerpt`
- direct-duplicate root support now takes precedence over a nearby contextual
  clause when both are present in the same scored candidate set

Current live Johl reading after that pass:
- `p2-s38` and `p2-s39` now promote to support via duplicate-root handling
- `p2-s5` and `p2-s6` remain unresolved as sibling-leaf cross-swap failures
- `p2-s21` still reads closer to adjacent event / substitution pressure than
  support

First bounded sibling-leaf followthrough now landed:
- builder-side winner selection now runs a bounded sibling-leaf arbitration
  pass over near candidates so the direct leaf can beat a nearby contextual
  or sibling clause inside the same incident row
- relation classification now requires predicate alignment before
  `partial_support` can win over `adjacent_event` or `substitution`
- `partial` rows with strong direct leaf alignment can now promote to
  `equivalent_support` rather than being trapped under weaker contextual
  support labels
- focused regressions now pin:
  - keyboard/audio sibling-leaf disambiguation
  - the p2-s21-style adjacent-event guardrail
  - strong partial-match promotion to `equivalent_support`

Live five-row Johl spot-check after the clause pass:
- `p2-s5` now resolves to `supports / equivalent_support` on the direct
  keyboard/audio incident leaf via a clause winner
- `p2-s6` now resolves to `supports / equivalent_support` on the direct
  keyboard/audio incident leaf via a clause winner
- `p2-s38` and `p2-s39` still resolve to support inside the same incident
  cluster
- `p2-s21` no longer false-promotes to support:
  it now resolves to `disputed / explicit_dispute` on the rebuttal clause
  `John had failed to complete the necessary steps to revoke his EPOA`, with
  the echoed John claim preserved only as lineage via
  `duplicate_match_excerpt`

Dad Court notebook followthrough on the persisted visible conversation now
adds a more specific refinement target:
- it agrees the echoed John clause should not rescue the row into support
- it agrees independent Johl-authored confirmation candidates such as
  `I had only received the revocation three weeks ago` and
  `This is corroborated by the dated signature on the revocation documents`
  are stronger support signals than quote echoes
- but it suggests `p2-s21` may eventually need a
  technical-qualification / conceded-fact class rather than a flat
  `explicit_dispute`, because Johl appears to contest completion/effect rather
  than the existence of revocation steps

## Immediate prioritization

The next improvement order should be:
1. eliminate `weakly_addressed` as a target bucket by splitting it into:
   `partial_support`, `adjacent_event`, `substitution`,
   `non_substantive_response`
2. keep explicit dispute promotion above weaker semantic overlap
3. continue the duplicate-root / incident-cluster pass for cross-side and
   family-law style material:
   stop same-incident sibling leaves such as the Johl keyboard/audio pair from
   cross-swapping into each other
4. continue tightening proposition decomposition so compound rows split into:
   event, characterization, and consequence where possible
5. add the minimum explanation layer before chasing broader semantic recall
6. keep explanatory clauses and same-incident sibling leaves distinct:
   true explanatory framing should stay non-substantive, while sibling-action
   promotion should be reserved for clauses that align on the same leaf act
7. add bounded clause-level candidate decomposition inside source matching so
   compound narrative rows can expose action, cause, and effect leaves without
   changing persisted proposition ids
8. disambiguate response-side quote/reference headings from Johl-authored
   assertions so exact duplicate John claim text inside a longer Johl response
   block does not automatically count as support
9. demote allegation/OCR echo blocks before winner selection, not only after
   classification:
   if a contested row contains section headers such as `Allegation:`, `OCR of
   the Affidavit:`, `Your Explanation:`, or `Defense Context:`, the scorer
   should prefer the substantive response section and preserve the duplicate
   allegation text only as reference context
10. Dad Court notebook feedback on the exact row strings agrees with that
    direction:
    - `p2-s5`, `p2-s6`, and `p2-s38` should anchor support to Johl-authored
      explanation/admission text rather than echoed allegation text
    - `p2-s39` should not become full support from a quoted restatement alone
    - `p2-s21` should not be rescued by quote echo; it should either match an
      independent Johl confirmation of the revocation event or be treated as a
      qualification/rebuttal about completion rather than bare support
11. Next bounded refinement:
    split technical qualification / conceded fact from flat dispute when the
    response concedes the event root but contests completion, legal effect, or
    characterization

## Cross-lane priority

Relative to the temporary `TEMP_zos_sl_bridge_impl` retrieval bundle, this
affidavit reconciliation pass should be treated as the higher immediate
implementation priority.

Reason:
- affidavit is the active SQLite/local-first proving slice
- it already has live runs, persisted review data, and operator-facing grouped
  output
- the current uncertainty is in classification correctness, which can be
  reduced directly by relation typing and explanation fields

The temporary ZOS bridge remains important, but it is now the second priority:
- keep it bounded as proposal/retrieval infrastructure
- do not widen it until the explicit admissibility filter is implemented

## Non-goals

This note does not authorize:
- a fully general legal NLP stack
- silent semantic collapse
- replacing review with automatic legal conclusions
- heavy-model-first matching without bounded rule surfaces

## Formalism note

The current bounded EPOA-specific pattern lists are a stopgap, not the target
logical shape.

After checking the local formalism repos:
- `../dashi_agda/Contraction.agda`
- `../dashi_agda/Monster/Projection.agda`
- `../dashi_agda/Monster/TraceSound.agda`
- `../zkperf/README.md`
- `../zkperf/LATTICE_SHARDS.md`

the cleaner target is:
- preserve the event root
- refine the leaf relation by bounded projection / contraction
- keep witness-like lexical cues as admissibility evidence, not as the
  semantic class itself

So for affidavit reconciliation, the intended shape is:
- root:
  shared event / claim family
- leaf:
  support
  dispute
  technical_qualification
  conceded_fact
  adjacent_event
  non_substantive_response
- witness / admissibility:
  quote echo
  rebuttal pattern
  dated-signature confirmation
  receipt-of-revocation confirmation
  speaker-role attribution

This matches the formalism direction better than growing more ad hoc token
lists:
- `Projection` suggests duplicate-root text should remain a preserved root
  witness, not become the winning leaf by itself
- `Contraction` suggests refinement should move from broad/supportive collapse
  toward a smaller, more specific leaf class when the response narrows or
  qualifies the claim
- `TraceSound` suggests the row should remain tied to the concrete supporting
  clause/witness that actually produced the classification
- `zkperf` supports the same split in practice:
  witness-bearing evidence and receipts justify a classification but are not
  themselves the classification

Immediate implication:
- the current EPOA-specific anchor/rebuttal lists should be treated as local
  witness heuristics only
- the next real implementation step is to introduce a first-class
  `technical_qualification` / `conceded_fact` response-intent layer and route
  the current lexical heuristics through that layer

## Performance constraint

The current Google Docs contested-affidavit path is functionally useful but too
slow for the live Dad/Johl loop on such a small corpus.

The next bounded optimization pass should therefore:
- precompute source-row segment/clause candidates once per row
- cache repeated text analyses such as tokenization, clause splitting,
  structural parsing, and leaf-signature derivation
- avoid re-splitting and re-tokenizing the same response rows for every
  proposition

This is an implementation constraint, not a semantic change:
- root/leaf behavior should remain the same
- the optimization pass should reduce repeated local work before any further
  ontology widening

The first bounded optimization pass is now landed:
- source-row segment/clause candidates are precomputed once per row
- repeated tokenization, clause splitting, structural parsing, and
  leaf-signature derivation are memoized locally
- non-contested segment-level matching remains intact
- focused verification is green:
  `53 passed in 2.36s`
- a timed live targeted Dad/Johl `p2-s21` probe now completes fetch + group +
  payload build + row scoring in about `5.606s`

## Live Dad/Johl followthrough

The first `technical_qualification` pass is now landed and verified locally,
but the decisive live result was one step further:

- the live Dad/Johl rerun now lands `p2-s21` as:
  - `relation_root = supports`
  - `relation_leaf = conceded_fact`
  - `relation_type = conceded_fact`
- winning response clause:
  `John had failed to complete the necessary steps to revoke his EPOA`
- retained lineage echo:
  `In August 2024 I took steps to revoke my EPOA`
- decisive nearby confirmation in the same Johl block:
  `This is corroborated by the dated signature on the revocation documents.`

Interpretation:
- `technical_qualification` remains the correct response-role shape for the
  rebuttal clause itself
- but when the same response block also carries strong independent
  confirmation, the row should be promoted to `conceded_fact`

Notebook-assisted review on the persisted Dad Court thread agreed with this:
- `p2-s21` now supports `conceded_fact`
- the recommended operator label is:
  `Conceded Fact (+ Technical Qualification)`
- the highest-signal next refinement is now strict echo masking for the
  respondent's pasted allegation headers / copied affidavit text

Immediate next implementation target:
- hard-block high-similarity allegation echoes from winning supported rows when
  they are only quote headers or draft scaffolding
- force the matcher to prefer Johl-authored rebuttal / admission text beneath
  those echoed headers
