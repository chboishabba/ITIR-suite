# OAC v1.0: Object Admissibility Contract (Truth vs View) (2026-02-11)

## Origin
- `origin_online_id`: `698bdf6e-43f8-839c-9089-34ee3d3338dd`
- `origin_note`: User-provided online thread reference for the contract framing; documented here without performing live fetch.

This document freezes the *object admissibility* contract for the Wikipedia -> AAO substrate lane,
with explicit separation between:

- **Truth capture** (maximal, deterministic, provenance-preserving)
- **View surfacing** (filters, caps, promotion UX; reversible)

It is intentionally **not** a causal model.

## Decisions (ratified)

1. **Span candidates exist in truth, but not as entities.** (`1B`)
   - Truth includes unresolved mentions only as `span_candidates` with provenance.
   - Entities remain only `wikilink|ontology|wikidata/dbpedia` resolved.

2. **Allowed "semantic" signals** (`2A + 2B`)
   - Wikipedia/Wikidata/DBpedia typing (structured, replayable).
   - Deterministic dependency parsing (spaCy) **only** for roles/attachments
     (subject/object/agent, clause boundaries). No NER, no "meaning".

3. **Pinned parser artifact** (`3 Yes`)
   - spaCy model + version is treated like a compiler: versioned, reproducible.
   - Record model name + version + hash in the AAO artifact provenance.

4. **Auto-promotion policy (hard gate)** (`4B`)
   - Spans auto-promote only if:
     - Recurs across >= N events
       - N=2: candidate
       - N=3: eligible to promote
     - AND later **hard-resolves** to a stable ID (Wikidata/DBpedia/ontology) OR exact canonical
       match to an existing entity.
   - Otherwise spans remain spans forever unless explicitly user-promoted (optional UI affordance).

5. **Type lattice includes `COLLECTIVE_ROLE` on day 1** (`5 Yes`)
   - Needed for phrases like "UN weapons inspectors" without lying about ORG or PERSON.

## Canonical JSON Shapes

This contract introduces two parallel lanes:

- `entities`: stable IDs + typing
- `span_candidates`: unresolved mentions (TextSpan-like), never treated as entities until promotion

### Entity (truth)

```json
{
  "id": "wiki:en:Mohamed_ElBaradei",
  "label": "Mohamed ElBaradei",
  "type": "PERSON",
  "provenance": {
    "source": "wikilink",
    "ref": "George W. Bush@revid:1336322390#ev:0039"
  },
  "confidence": 0.95
}
```

### SpanCandidate (truth)

Spans are anchored to a specific event sentence by default.

```json
{
  "span_id": "span:ev:0039:17:36",
  "event_id": "ev:0039",
  "span": {
    "kind": "event_text",
    "start": 17,
    "end": 36
  },
  "text": "UN weapons inspectors",
  "span_type": "COLLECTIVE_ROLE",
  "sources": [
    {
      "source": "dep_parse",
      "note": "nsubj|dobj attachment under head verb 'led'"
    }
  ],
  "recurrence": {
    "seen_events": 1
  }
}
```

### SpanCandidate Scope (what belongs in this lane)

`span_candidates` are intentionally **unresolved mentions only**:

- They must **not** be redundant with already-resolved entities in the same sentence.
  - If a noun chunk overlaps a wikilink-resolved entity span (or is largely composed of resolved
    entity tokens, like `"President Bush"`), it is not a span candidate.
- They must **not** be time-only expressions.
  - Time anchors are modeled separately; month/day/year noun chunks (e.g. `"November 25, 1981"`)
    are excluded from `span_candidates`.

This is not “trimming”; it is definitional. Spans are the lane for *unresolved mentions* that could
later hard-resolve to stable IDs, not a second copy of the entity lane.

### Optional Hygiene Metadata (truth, view-oriented)

`span_candidates` may include optional hygiene fields used only for *view surfacing* (not truth
admissibility). Example:

```json
{
  "hygiene": {
    "token_count": 3,
    "is_time_expression": false,
    "overlaps_resolved_entity": false,
    "view_score": 0.82
  }
}
```

Views may sort/filter by `hygiene.view_score` without mutating the truth payload.

## Span Reference Model

We support multiple anchoring modes because we may not have stable full-article char offsets early.

```json
{
  "kind": "event_text",     // offsets relative to event.text (sentence-local)
  "start": 17,
  "end": 36
}
```

Future extension (optional):

```json
{
  "kind": "revision_text",  // offsets relative to stripped full-article text
  "revision_id": "wiki:en:George_W._Bush@revid:1336322390",
  "start": 19480,
  "end": 19507
}
```

## AAO Event Shape (truth)

The AAO artifact remains sentence-local. It may include multiple `steps[]` for multi-verb sentences.

```json
{
  "event_id": "ev:0039",
  "anchor": { "year": 2002, "month": 11, "day": null, "precision": "month", "text": "In November 2002", "kind": "explicit" },
  "section": "Iraq invasion",
  "text": "In November 2002, Hans Blix and Mohamed ElBaradei led ...",
  "actors": [
    { "label": "Hans Blix", "resolved": "Hans Blix", "role": "subject", "source": "wikilink_person" }
  ],
  "steps": [
    { "action": "led", "subjects": ["Hans Blix", "Mohamed ElBaradei"], "objects": ["Mohamed ElBaradei"], "purpose": null }
  ],
  "objects": [
    { "title": "Mohamed ElBaradei", "source": "wikilink" }
  ],
  "span_candidates": [
    { "span_id": "span:ev:0039:...", "event_id": "ev:0039", "span": { "kind": "event_text", "start": 17, "end": 36 }, "text": "UN weapons inspectors", "span_type": "COLLECTIVE_ROLE" }
  ],
  "warnings": []
}
```

## Resolver Rules (deterministic)

### Entities

Entities are created only from:

- Wikilinks (Wikipedia titles in `timeline.links`)
- Ontology entries / curated external refs (DBpedia/Wikidata)
- Explicit registry entities (project-owned)

### Spans

Spans are created from:

- Dependency parse attachments where the referent does not hard-resolve to an entity.
- They are typed (`COLLECTIVE_ROLE`, etc.) but not assigned stable IDs.

## Promotion Rules (view layer)

Promotion is not truth mutation unless the promotion results in a stable ID.

States:

- `span_only` (default)
- `candidate` (recurrence >= 2)
- `eligible` (recurrence >= 3)
- `promoted` (hard-resolved stable ID OR exact canonical match)

Promotion "hard gate":

- do not promote based on surface similarity, embeddings, or heuristics
- only promote when resolution is exact and provenance is recorded

## Svelte Boundary (Truth vs View)

### Truth store

- Raw AAO artifact JSON:
  - `SensibLaw/.cache_local/wiki_timeline_gwb_aoo.json`

Loaded by:
- `itir-svelte/src/lib/server/wikiTimelineAoo.ts`
- `itir-svelte/src/routes/graphs/wiki-timeline-aoo/+page.server.ts`
- `itir-svelte/src/routes/graphs/wiki-timeline-aoo-all/+page.server.ts`

### View model (client)

- Rendering-only caps/toggles:
  - `itir-svelte/src/routes/graphs/wiki-timeline-aoo/+page.svelte`
  - `itir-svelte/src/routes/graphs/wiki-timeline-aoo-all/+page.svelte`

Rule:
- caps and filters must not mutate the JSON artifact; they only decide visibility.

## Provenance fields (required for pinned parser)

When spaCy parsing is introduced for roles/attachments, record in the AAO output:

```json
{
  "parser": {
    "name": "spacy",
    "model": "en_core_web_sm",
    "version": "x.y.z",
    "model_sha256": "..."
  }
}
```

## TODO (implementation)

- Add `span_candidates[]` emission in the AAO extractor using dependency attachments
  (sentence-local; bounded).
- Add `entity_meta` map (id -> {type, provenance, confidence}) alongside the AAO payload so views can
  surface types without re-parsing strings.
- Add a view toggle to show spans as dashed nodes and a promotion affordance (optional).
