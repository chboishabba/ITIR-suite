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
- bounded candidate-only explicit social relations from text-local named
  statements:
  - `sibling_of`
  - `parent_of`
  - `child_of`
  - `spouse_of`
  - `friend_of`
  - `guardian_of`
  - `caregiver_of`
  - current scope is narrow and explicit only:
    - `Alice is Bob's sister`
    - `Mary is the mother of Jane`
    - `Alice and Bob are friends`
    - `Mary is Jane's guardian`
    - `Alice cared for Bob`
  - no first-person inference (`my brother`, `our mother`) in this pass
  - no implicit social-role inference from co-presence or dialogue adjacency
  - no custody/institution inference from legal or administrative labels alone

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
- sentiment/affect cues do not justify psychometric, dashboard-authority, or
  negotiation-weighting claims in this lane; they stay speaker/utterance-anchored
  and non-canonical
- this lane is for semantic-shape proving and general human-text handling, not
  for legal interpretation of transcripts by default

## Textual Derivation Method
The bounded social/care lane should derive relations textually in this order:
1. detect an explicit social/care cue pattern in one event-local text span
2. resolve the paired named actors from that same span
3. map the observed surface to a stable canonical predicate
4. persist the surface wording only in receipts

Chosen naming rule:
- canonical predicates should be relation-stable and tense-neutral
- tense/inflection stays in receipts such as `cue_surface`

Example:
- text: `Alice cared for Bob`
- canonical predicate: `caregiver_of`
- receipts:
  - `cue_surface=cared_for`
  - `predicate=caregiver_of`

This keeps canonical predicates coherent with `guardian_of`, `parent_of`,
`friend_of`, and similar relation-style names instead of mixing event phrasing
with stable relation identity.

## Summary Artifact
The transcript/freeform lane should expose a compact review summary artifact in
addition to the full semantic report.

Required summary contents:
- candidate counts by predicate
- promoted counts by predicate
- abstained counts by predicate
- top cue surfaces by predicate
- per-event counts for social/care predicates
- explicit note when all social/care predicates remain candidate-only
- compact `text_debug` coverage stats so missing arc rows are reviewable rather
  than silent

This summary exists to support promotion and confidence review without making
reviewers inspect the full JSON report each time.

## Text-Debug Workbench Artifact
Transcript/freeform reports should also emit a producer-owned `text_debug`
artifact for workbench consumption.

Required contents:
- event-local text
- token list
- relation rows with canonical family/color metadata
- anchor provenance and token ranges
- producer-owned char spans and source artifact ids for each anchor
- grouped source-document payloads keyed by transcript/file source id
- source-level char spans so event-local anchors can be projected into the
  source-document viewer without TS re-derivation
- display-only opacity derived from confidence/promotion state

Boundary:
- this artifact is a review/debug contract
- it does not define authoritative canonical spans
- `itir-svelte` should render it rather than re-derive anchors locally

## Mission / Follow-up Observer Artifact
Transcript/freeform reports should also emit a bounded `mission_observer`
artifact for SB-safe mission/follow-up overlays.

Current v1 method:
1. detect explicit mission/task cue phrases in a local text span
2. detect explicit follow-up phrasing in later local text spans
3. resolve generic follow-up references by backtracking to prior source-local
   mission mentions
4. carry forward deadline cues only when textually grounded
5. abstain when multiple or zero defensible referents remain

Current output shape:
- compact mission summary counts
- `missions[]`
- `followups[]`
- `sb_observer_overlays[]`

Boundary:
- observer-class only
- no raw thread dumps
- no promotion into canonical semantic relations
- no SB authority transfer; SB consumes the overlays as read-only/additive refs

## Next Corpus / Validation Direction
The next transcript/freeform proving case should widen from chat/task text into
public-media narrative material.

Chosen public case:
- FriendlyJordies as a reproducible public-media/transcript validation fixture

Why:
- the user story is not only conversation/state extraction
- the lane should also support narrative validation from transcript/media text
- proposition extraction, attribution, and later comparison need a public
  proving corpus before broader web-backed validation work

Expected followthrough:
- URL/transcript ingest into the future ingress hub
- transcript/media text processed through the same bounded narrative/semantic
  pipeline
- later corroboration lanes (wiki, Wikidata, web) remain explicit and cited
  rather than replacing transcript-local extraction as authority

This lane should therefore be read as supporting:
- conversation/state/social cues
- mission/follow-up cues
- public-media narrative validation
- later competing-narratives comparison

## Review Feedback Seam
The transcript/freeform lane now also participates in the semantic workbench's
append-only review-feedback seam.

Current v1 posture:
- corrections are submitted from `itir-svelte`
- records are keyed by source/run/event/relation/anchor refs
- they persist as local review artifacts rather than rewriting semantic tables
- the transcript lane should remain the semantic authority for emitted report
  artifacts; the UI only contributes review receipts

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
   `felt_state` / `replied_to` / explicit social or care relations
4. keep social/care textual derivation narrow:
   - explicit named patterns only
   - no institutional-custody inference from labels alone
   - no first-person kinship/care inference until speaker grounding is stronger
5. widen the bounded proposition-layer followthrough from current HCA-first
   reasoning idioms into transcript/media-friendly attribution structures:
   - cited holdings (`X held that ...`)
   - attribution wrappers (`X submits that ...`)
   - current-speaker vs cited-authority separation
   - proposition-to-proposition comparison hooks for disputed narratives
