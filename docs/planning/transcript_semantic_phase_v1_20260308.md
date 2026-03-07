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
- bounded candidate-only conversational relation:
  - `replied_to`

## Current Boundaries
- transcript/freeform cues do not create global actor identity
- speaker inference remains receipt-bearing and source-scoped
- candidate relations are allowed to remain candidate-only; no pressure to
  promote conversational turns into canonical semantic relations yet
- this lane is for semantic-shape proving, not for legal interpretation of
  transcripts

## Next Tightening Targets
1. widen transcript/freeform participant/context extraction without inventing
   actors
2. add stronger event-role coverage for explicit hearing/forum markers
3. decide whether any transcript/freeform relation family deserves medium/high
   promotion under the current spine
