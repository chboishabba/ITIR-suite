# Transcript Semantic Phase v1 (2026-03-08)

## Purpose
Pressure-test the frozen semantic v1.1 spine against transcript/freeform text
without widening the canonical semantic schema.

## Chosen Defaults
- use existing transcript/message `TextUnit` inputs as the first corpus
- use current deterministic speaker inference as the upstream identity surface
- non-famous participants resolve to source-local/document-local speaker actors
- ambiguous speaker/actor cases abstain rather than inventing identity
- relation output is hybrid in this phase:
  - mention resolution and `event_role` rows persist in the shared semantic
    tables
  - relation candidates may persist
  - promoted semantic relations remain conservative and can stay at zero

## Current v1 Coverage
- explicit message-header speakers
- Messenger-style bracketed sender rows
- `Q:/A:` mapping when known participants are supplied
- timing-only subtitle ranges abstain
- role-only labels such as `User:` remain non-person abstentions
- bounded source-local general entity extraction for freeform/journal text:
  - titlecase person/place-style mentions become source-local actor entities
  - simple object/theme mentions can become source-local concept entities
  - obvious titlecase noise (`Thanks`, `Today`, role/system labels, similar
    sentence-openers) now abstains instead of becoming source-local actors
- bounded candidate-only non-legal affect/state relation:
  - `felt_state`
- bounded candidate-only conversational relation:
  - `replied_to`

## Current Boundaries
- transcript/freeform cues do not create global actor identity
- speaker inference remains receipt-bearing and source-scoped
- the generalized transcript/freeform lane is profile-neutral by default:
  - broad actor/entity extraction is allowed
  - legal predicates/courts/authority vocab do not load implicitly
- actor identity and role boundaries should stay aligned with the existing
  semantic/actor architecture:
  - canonical identity belongs to the shared entity/actor spine, not to
    transcript-local role labels
  - `event_role` remains the place for participation/context structure
  - do not treat transcript/freeform participation labels as new actor
    ontology kinds
- candidate relations are allowed to remain candidate-only; no pressure to
  promote conversational turns into canonical semantic relations yet
- explicit affect/state cues may emit candidate-only semantics, but there is no
  promotion of mood/state relations in v1
- this lane is for semantic-shape proving and general human-text handling, not
  for legal interpretation of transcripts by default

## Next Tightening Targets
1. tighten general freeform entity heuristics so obvious non-entity titlecase
   words stay abstained without shrinking broad human-text coverage
   - implemented in bounded form with contextual single-token gating for
     person/place-style entities plus explicit noise suppression
2. add stronger event-role coverage for explicit hearing/forum markers and
   general non-legal participant/context structure
   - align this work with the existing actor/event-role contracts rather than
     inventing a transcript-only role taxonomy
   - reuse established role/slot language where it already exists in the repo
     (`subject`, `object`, `requester`, `speaker`, `event_role` boundaries)
   - keep any narrower transcript/freeform role additions explicitly reviewable
     and subordinate to the shared semantic spine
   - archive-backed rationale and thread IDs are captured in
     `docs/planning/archive_actor_semantic_threads_20260308.md`
3. decide whether any transcript/freeform relation family deserves medium/high
   promotion under the current spine, starting from candidate-only
   `felt_state` / `replied_to`
