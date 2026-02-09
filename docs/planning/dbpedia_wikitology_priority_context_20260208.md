# DBpedia/Wikitology Priority Context (Ontology Topology Thread) (2026-02-08)

## Canonical thread

This is the canonical discussion to treat as the "source of truth" for the
DBpedia/Wikitology-style external ontology integration framing:

- Title: `Data management ontology topology`
- `canonical_thread_id`: `331a7d1304f329259315649e7a9d729a83b51daf`
- Latest message timestamp (DB): `2025-11-18T02:11:55Z`

### How to re-fetch it (DB-first)

Use `$robust-context-fetch` (resolver DB-first) via:

```bash
.venv/bin/python scripts/chat_context_resolver.py "topology" --no-web
```

Or fetch by canonical thread id:

```bash
.venv/bin/python scripts/chat_context_resolver.py "331a7d1304f329259315649e7a9d729a83b51daf" --no-web
```

## Why this matters

This thread contains the explicit project motivation for "wiki-ish ingestion":

- Framing: DBpedia/Wikitology treated Wikipedia as a global ontology for the web;
  we want the analogous enrichment for ITIR's internal ontology (TiRC + SL),
  without letting external sources become normative truth.
- Mapping: "Wikitology/KBP feature engineering ideas" map into TiRCorder + SensibLaw
  architecture and should inform how we ingest/link external IDs.

## Where it lands in-repo today

The concrete implementation posture that corresponds to this thread is already
captured as docs + schema, even if ingestion is still mostly manual/curated:

- `tircorder-JOBBIE/docs/external_ontologies.md`
  - Advisory enrichment posture (never normative).
  - Join tables for concept/actor external refs.
  - Candidate discovery via SPARQL (Wikidata/DBpedia).
- `SensibLaw/docs/ONTOLOGY_EXTERNAL_REFS.md`
  - How to curate + upsert external IDs into `concept_external_refs` and
    `actor_external_refs`.
  - DBpedia storage convention (full URI external_id).
- `SensibLaw/docs/external_ingestion.md`
  - Supported path: curated Wikibase/Wikidata-style enrichment, persisted in DB.

## Guardrails (non-negotiable)

- External ontologies are **advisory** and must not:
  - create/override WrongTypes, Duties, ProtectedInterests, or ValueFrames
  - create normative claims
  - "explain away" local evidence or legal-system constraints
- External links must be:
  - reviewable/curated (versionable input batches)
  - deterministic for a given batch (no silent re-mapping)
  - separable by provider (`wikidata`, `dbpedia`, etc.)

## Immediate next steps (implementation)

1. Treat DBpedia as a first-class provider for external refs:
   - Store DBpedia `external_id` as a full URI (not a `dbpedia:` CURIE).
   - Ensure graph export preserves URI targets as valid IRIs.
2. Provide a minimal "lookup + curate + upsert" tool surface:
   - Do not depend on live SPARQL at runtime; support offline caching/batches.
   - Keep it opt-in and auditable.
