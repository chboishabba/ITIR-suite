# GWB Semantic Phase v1.1 (2026-03-07)

## Purpose
Turn the current GWB legal-linkage lane into a broader semantic proving ground
with:
- a unified entity spine
- deterministic mention resolution
- office/person separation
- edge-first typed relations
- explicit abstention for unresolved political/discourse labels

This phase does not replace the existing GWB U.S.-law linkage tables. It sits
on top of them and uses the reviewed linkage results as one evidence surface.

## Chosen Defaults
- unified shared entity spine now, not later
- courts are stored as `institution_actor` plus court classification, not as a
  separate canonical actor kind
- speaker/reporting/source remain role lanes, not actor ontology kinds
- `Bush administration` is non-canonical by default and should abstain unless a
  later concept/administration layer is explicitly designed
- title-only discourse surfaces like `the President` and `the court` should
  abstain unless stronger context is present
- relation storage is edge-first and vocabulary-driven
- confidence is receipt-derived, not hand-authored
- semantic progression is three-layer:
  - `event_role`
  - `relation_candidate`
  - promoted `semantic_relation`

## Current v1 Storage Shape
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

## Frozen Invariants
- actor ontology, mention resolution, event-role evidence, and promoted
  semantic relations are distinct layers; text evidence never becomes canonical
  structure without an explicit promotion step
- unified `entity` spine is the FK target for the semantic layer; do not fall
  back to open polymorphic `kind + id` pairs for relation storage
- courts remain `institution_actor` plus classification, not a separate
  canonical actor ontology kind
- `Bush administration` stays non-canonical by default; treat it as an
  abstainable discourse/political label unless a later concept layer is added
- `mention_resolution` is a first-class artifact, not an implicit side effect
  of the actor table
- relation progression is:
  - `event_role`
  - `relation_candidate`
  - promoted `semantic_relation`
- confidence is a deterministic projection of receipts/rules, not a hand-set
  judgment field

## Open but Deliberately Deferred
- `speaker`, `reporting_actor`, `attributed_actor`, and `source_entity` remain
  participation roles, not actor ontology kinds
- `Bush` / `the President` / `the court` / `the administration` remain good
  proving examples for abstention and later office/forum/concept refinement
- broader review/litigation predicates should pressure-test the current spine
  before any schema expansion

## Initial GWB Coverage
Resolved entities:
- George W. Bush
- John Roberts
- Samuel Alito
- Harriet Miers
- U.S. Senate
- House of Representatives
- Department of Defense
- U.S. Supreme Court
- United States district court
- Sixth Circuit
- President of the United States (office)

Initial promoted predicate set:
- `nominated`
- `confirmed_by`
- `signed`
- `vetoed`

Other predicates remain in the controlled vocabulary for later use but are not
yet broadly promoted.

## Current Boundaries
- parser/event-role evidence remains distinct from promoted semantic relations
- external IDs remain downstream and reviewed only
- current GWB semantic report is DB-backed only; no UI work in this phase
- no open-world actor merge authority from Wikidata or parser heuristics
- low-confidence relation candidates remain visible as `candidate` rows; they do
  not promote into canonical semantic relations

## Next Tightening Targets
1. extend beyond title/alias-driven person resolution for Bush-era actors
2. improve office-context handling without collapsing office and person
3. add stronger candidate-only relation coverage for review/litigation lanes
4. connect the semantic entity/report surface to the bounded Wikidata
   mereology/property-pressure notes without changing canonical identity

## Current Cross-Testing Posture
- Australian legal corpora are the required cross-test source for this phase.
- The frozen v1.1 semantic shape must survive fixture-driven pressure from:
  - `Mabo [No 2]`
  - `House v The King`
  - `Plaintiff S157/2002 v Commonwealth`
  - `Native Title (New South Wales) Act 1994`
- Cross-testing goal:
  - prove the existing `entity -> mention_resolution -> event_role ->
    relation_candidate -> semantic_relation` shape can express court/forum/
    authority/review patterns without schema changes
  - keep ambiguous forum/title labels abstained unless stronger evidence exists
