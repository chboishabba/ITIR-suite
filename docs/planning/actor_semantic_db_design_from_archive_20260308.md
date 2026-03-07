# Actor / Semantic DB Design From Archive (2026-03-08)

## Purpose
Recover concrete DB/table recommendations from the local archive threads and
compare them against the current implemented semantic schema.

This note is archive-derived guidance plus an explicit mismatch inventory. It
does not change code by itself.

## Implementation Decision (2026-03-08)
Chosen placement for the next identity-governance wave:
- keep the current semantic v1.1 spine intact
- add alias registry, merge audit, and governed `event_role` vocabulary in a
  shared actor layer rather than duplicating them inside the `semantic_*`
  family
- map actor-like semantic entities onto shared actors through
  `semantic_entities.shared_actor_id`

Implemented bounded scope:
- shared `actors`
- shared `actor_aliases`
- shared `actor_merges`
- shared `event_role_vocab`
- semantic actor rows now attach to shared actors
- actor seed aliases and transcript/source-local actor labels now persist into
  `actor_aliases`
- `semantic_event_roles.role_kind` is now backed by `event_role_vocab`

Still deferred:
- actor detail/profile/annotation extension tables
- broader relationship-basis/shape/intensity structures
- automatic merge behavior beyond the audit table itself

## Post-Implementation Assessment

### What this wave actually improved
- It turned earlier archive conclusions into durable schema rather than leaving
  them as chat-only guidance.
- It gave the repo one shared place for canonical actor surface forms
  (`actor_aliases`) instead of scattering them only across in-code seeds,
  receipts, and source-local mention rows.
- It added identity-governance scaffolding (`actor_merges`) without forcing any
  automatic merge behavior before the corpus pressure is understood.
- It stopped `event_role` governance from being purely implicit by adding a
  shared `event_role_vocab`.
- It did all of that without disturbing the working semantic spine:
  `entity -> mention_resolution -> event_role -> relation_candidate ->
  semantic_relation`.

### What this wave did not change
- Mention resolution still resolves into `semantic_entities`, not directly into
  shared actors.
- The semantic lanes are not yet broadly querying `actor_aliases` as a general
  alias-matching authority beyond the current seeded/source-local actor flows.
- `actor_merges` is present as an audit substrate only; there is no automatic
  or reviewer-driven merge workflow yet.
- Actor detail/profile/annotation tables remain deferred.
- This wave does not reopen the broader ontology/relationship-structure
  proposals from older chats.

### Main lesson
The archive-backed “clean” schema was not meaningfully different from the
implemented semantic v1.1 core. The real gap was not core shape; it was shared
identity governance around that core.

That means the current architecture should continue to be read as:
- semantic spine for text-derived evidence and promotion
- shared actor layer for durable identity governance
- broader ontology/detail extensions only when concrete corpus pressure appears

### Next decision pressure
The next useful choice is not another core schema redesign. It is deciding how
far the new shared actor layer should be allowed to influence matching:
- conservative option:
  - keep `actor_aliases` mainly as a persisted registry/audit surface for now
  - continue using lane-local deterministic matching rules as the main matching
    authority
- wider option:
  - let reviewed `actor_aliases` participate more directly in deterministic
    actor matching across lanes
  - this increases reuse, but also increases the risk of cross-lane alias
    bleed if provenance/review discipline slips

Current recommendation:
- keep alias consumption conservative
- use the shared alias layer first for seed-backed actor reuse and audit
- defer broader alias-driven matching until there is specific corpus evidence
  that lane-local matching is leaving too much value on the table

## Primary Archive Sources

### 1. `Actor table design`
- thread: `21f55daa80206517e38f8c0fa56ee9bb2db8a9a0`
- strongest recovered DB guidance:
  - keep `actors` as a minimal identity spine only
  - do not put mutable/biographical/descriptive fields directly in the actor
    identity table
  - move descriptive data into extension tables

Recovered example direction from the thread:
- preferred actor core:
  - `actors(id, kind, display_name, created_at)`
- explicitly rejected in the actor core:
  - birthdate
  - gender
  - ethnicity
  - notes
  - address-like / profile-like descriptive fields

Rationale recovered from the thread:
- avoids polymorphism drift
- avoids merge ambiguity
- avoids null-heavy mixed-kind identity rows
- keeps actor identity mergeable and stable

### 2. `Actor Model Feedback`
- thread: `691d79376cb653e7170ea6c200a0a1d0a34bec6b`
- strongest recovered DB guidance:
  - use a unified entity spine plus subtype tables
  - keep mention resolution separate from actor ontology
  - keep `event_role` separate from promoted relations
  - avoid `*_kind + *_id` polymorphic relation targets where a shared FK target
    can be used instead

Recovered example direction from the thread:
- `entity(entity_id, entity_kind, canonical_key, canonical_label, review_status, pipeline_version)`
- `actor(entity_id, actor_kind, ...)`
- `office(entity_id, ...)`
- `office_holding(...)`
- `mention_cluster(...)`
- `mention_resolution(...)`
- `event_role(...)`
- `predicate_vocab(...)`
- `relation_candidate(...)`
- `semantic_relation(...)`

Rationale recovered from the thread:
- maintain FK integrity
- keep text evidence from mutating canonical structure without promotion
- keep role lanes from contaminating actor ontology

## Secondary Archive Context
- `Milestone Slice Feedback`
  - `1802fc3d13a0ad01ad95cef07eeaae9c16c22bed`
  - reinforces read-only/descriptive surfaces and the semantic-vs-normative
    boundary; less direct on table design
- `Taxonomising legal wrongs`
  - `74f6d0e08de82556df95c6ab1edb51557fede4fa`
  - reinforces broader ontology layering (`subject`, `object`, streams,
    relationships), but not a tighter semantic v1 DB schema than the two
    threads above
- `SENSIBLAW`
  - `4d535d3f33f54b1040ab38ec67f8f550a0f69dce`
  - broad project/history context, but not as precise as the two focused
    threads for DB recommendations

## Current Implemented Semantic Schema
Current semantic v1.1 implementation lives primarily in:
- `SensibLaw/src/gwb_us_law/semantic.py`
- reused by:
  - `SensibLaw/src/au_semantic/semantic.py`
  - `SensibLaw/src/transcript_semantic/semantic.py`

Implemented core tables:
- `semantic_entities`
- `semantic_entity_actors`
- `semantic_entity_offices`
- `semantic_entity_legal_refs`
- `semantic_office_holdings`
- `semantic_mention_clusters`
- `semantic_mention_resolutions`
- `semantic_mention_resolution_receipts`
- `semantic_event_roles`
- `semantic_predicate_vocab`
- `semantic_relation_candidates`
- `semantic_relation_candidate_receipts`
- `semantic_relations`
- `semantic_relation_receipts`

## Comparison: Archive Guidance vs Current Schema

### A. Where current code already matches the archive guidance

#### A1. Small canonical identity spine
Match quality: strong

Archive guidance:
- actor identity should stay minimal and clean

Current implementation:
- `semantic_entities` is small:
  - `entity_id`
  - `entity_kind`
  - `canonical_key`
  - `canonical_label`
  - `review_status`
  - `pipeline_version`

Assessment:
- current code follows the “clean identity spine” direction well
- the current implementation is actually stricter than the older chat wording,
  because it uses a unified entity spine rather than a standalone `actors`
  table

#### A2. Unified spine + subtype tables
Match quality: strong

Archive guidance:
- prefer unified `entity` spine plus subtype tables over loose polymorphic
  relation targets

Current implementation:
- `semantic_entities`
- `semantic_entity_actors`
- `semantic_entity_offices`
- `semantic_entity_legal_refs`

Assessment:
- current code is aligned with the later archive recommendation

#### A3. Mention resolution as a first-class layer
Match quality: strong

Archive guidance:
- mention resolution must be separate from actor ontology

Current implementation:
- `semantic_mention_clusters`
- `semantic_mention_resolutions`
- `semantic_mention_resolution_receipts`

Assessment:
- current code is explicitly aligned here

#### A4. Event-role -> candidate -> promoted relation progression
Match quality: strong

Archive guidance:
- `event_role`
- `relation_candidate`
- `semantic_relation`

Current implementation:
- `semantic_event_roles`
- `semantic_relation_candidates`
- `semantic_relations`

Assessment:
- current code matches the recovered semantic-spine design directly

### B. Where current code diverges or is narrower than the archive guidance

#### B1. No first-class actor alias table in the semantic schema
Archive-style expectation:
- `actor_aliases` as a persistent table of surface forms

Current implementation:
- aliases are mostly embedded in code/data seeds and matching logic
- resolved mentions are persisted as mention clusters/resolutions, but there is
  no dedicated persistent `semantic_actor_aliases` table

Assessment:
- this is a real mismatch relative to the broader actor-table design direction
- current code can resolve aliases deterministically, but alias persistence and
  alias-level audit are weaker than the older broader model

Consequence:
- alias behavior is inspectable through mention-resolution receipts, but not as
  a durable canonical alias registry inside the semantic schema

#### B2. No first-class merge audit table in the semantic schema
Archive-style expectation:
- `actor_merges` recording deduplication history

Current implementation:
- no semantic merge/audit table exists for actor/entity collapsing

Assessment:
- real mismatch
- current semantic lane mostly avoids the issue by staying deterministic and
  source-local/document-local where appropriate, but it does not yet provide a
  formal merge history table

#### B3. No actor extension tables in the semantic schema
Archive-style expectation:
- extension tables such as:
  - `actor_person_details`
  - `actor_org_details`
  - `actor_institution_details`
  - `actor_profiles`
  - `actor_annotations`
  - `actor_metadata`

Current implementation:
- semantic subtype support is currently narrow:
  - `semantic_entity_actors(actor_kind, classification_tag)`
  - `semantic_entity_offices(office_kind)`
  - `semantic_entity_legal_refs(ref_kind, source_title)`

Assessment:
- current code is intentionally much narrower than the older broader actor
  model
- this is not necessarily a bug; it reflects the current bounded proving scope

Consequence:
- the repo lacks an implemented path for mutable/biographical/annotation-style
  actor detail within the semantic schema family

#### B4. No explicit semantic role vocabulary table for `event_role`
Archive-style expectation:
- not always stated as a separate table, but the broader role architecture
  implies a clearer governed role vocabulary

Current implementation:
- `semantic_event_roles.role_kind` is stored as free text
- no `semantic_event_role_vocab` table exists

Assessment:
- moderate mismatch
- workable for the current bounded proving lanes, but weaker for governance and
  cross-lane consistency than the predicate vocabulary pattern

#### B5. No relationship-basis / shape / intensity tables in the semantic schema
Archive-style expectation from the broader actor/ontology guidance:
- `relationship_basis`
- `relationship_shape`
- `relationship_intensity`

Current implementation:
- no equivalent semantic tables in the current v1.1 spine

Assessment:
- real mismatch relative to the broader ontology direction
- likely an intentional deferment rather than an omission, because current
  semantic v1.1 is focused on proving the smaller edge-first relation model

### C. Where the repo has related older ontology structures, but not in the current semantic family

The repo does contain a separate older/parallel ontology-oriented lane with:
- `actor_classes`
- `role_markers`
- `relationship_kinds`

Relevant code:
- `SensibLaw/src/ingestion/anchors.py`
- `SensibLaw/src/sensiblaw/db/dao.py`

Assessment:
- these tables are part of a different schema family than the current semantic
  v1.1 spine
- they show the repo already has precedent for classification/marker tables,
  but those structures are not yet integrated into the current semantic entity
  / mention / event-role / relation pipeline

## Explicit Mismatch Summary

### Current semantic schema is strong on:
- clean identity spine
- unified entity FK target
- explicit mention-resolution artifacts
- event-role / relation-candidate / promoted-relation separation
- avoiding `kind + id` relation target polymorphism

### Current semantic schema is still missing or narrower on:
- persistent actor alias registry table
- merge audit table
- actor detail / profile / annotation extension tables
- governed event-role vocabulary table
- richer relationship-structure tables (`basis` / `shape` / `intensity`)

## Recommended Follow-Through

### 1. Treat the current semantic v1.1 spine as the active implemented truth
Do not backslide from the current clean entity/mention/event-role/relation
shape.

### 2. Treat the missing actor-model pieces as explicit deferments
If revived, they should be reintroduced deliberately, not smuggled in via
transcript/freeform helper code.

### 3. If actor-model expansion resumes, add it in this order
1. persistent alias registry / alias audit
2. merge audit table
3. governed event-role vocabulary
4. only then consider actor detail/annotation extensions

This order preserves the current proving spine while addressing the most
architecturally important gaps first.
