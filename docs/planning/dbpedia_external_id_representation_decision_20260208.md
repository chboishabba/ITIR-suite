# DBpedia External ID Representation: Case For Option 2, Implement Option 1 (2026-02-08)

## Decision (what we do now)

**Implement Option 1**: store DBpedia `external_id` as a full DBpedia URI, e.g.:

- `http://dbpedia.org/resource/Westmead_Hospital`

Rationale: it yields immediately valid IRI targets for `owl:sameAs` / `skos:exactMatch`
without requiring prefix expansion, URL encoding rules, or runtime knowledge-base access.

This is documented for ingestion in:
- `SensibLaw/docs/ONTOLOGY_EXTERNAL_REFS.md`
- `tircorder-JOBBIE/docs/external_ontologies.md`

And the graph triple export preserves URL-form external IDs as-is in:
- `SensibLaw/src/graph/inference.py`

## Option 2 (case for): store a short DBpedia identifier and expand later

**Option 2** would store DBpedia `external_id` in a compact form, then expand to a
full URI at export time. Examples of “short” forms:

- Page-title form: `Westmead_Hospital`
- CURIE-ish form: `dbpedia:Westmead_Hospital`
- Potentially language/version-specific: `en:Westmead_Hospital` (or `dbpedia-en:...`)

### Why Option 2 is attractive (the good arguments)

1. **Diff/readability and editorial workflow**
   - Curated batches are easier to review and edit when identifiers are short.
   - Reduced noise in JSON/CSV and PR diffs when curating large mappings.

2. **Storage normalization**
   - Avoid hard-coding scheme/domain in every row (`http://dbpedia.org/...`).
   - If we ever want `https://` or a mirrored endpoint, we can change the expander,
     not every row.

3. **Consistency with other providers**
   - Wikidata is naturally stored as a compact `Q...` and expanded/prefixed.
   - A similar “provider + id” representation is conceptually tidy across providers.

4. **Offline / private deployments**
   - Expansion rules can be deterministic and offline.
   - You can avoid “leaking” full URIs in some UI contexts while still having a
     reversible mapping.

### Why Option 2 is risky (why we are *not* doing it yet)

1. **Ambiguity and correctness traps**
   - DBpedia has language editions and multiple namespaces; “title-only” is not
     globally unambiguous without a base.
   - Title normalization/encoding is non-trivial (spaces, parentheses, unicode,
     redirects, capitalization conventions).

2. **Prefix expansion becomes part of the canonical contract**
   - Once we accept short forms, we must define a strict, versioned expansion
     algorithm (including escaping) and test it.
   - Any change to the expander can silently change graph identity and break
     deterministic exports.

3. **Bad failure mode**
   - A short-form that expands incorrectly yields a plausible-but-wrong `owl:sameAs`,
     which is worse than “no link”.

4. **It pushes complexity into the exporter**
   - Exporters then need scheme awareness and normalization logic (and probably
     per-provider rules).
   - This is the opposite of the “keep enrichment boring and auditable” posture.

## Guarded path to Option 2 (if/when we want it)

If we want Option 2 later, do it explicitly and test-gated:

1. Define a versioned expander contract, e.g. `dbpedia_expander_v1`:
   - input: `external_id` short form + optional `lang`
   - output: canonical URI
   - exact escaping rules

2. Add conformance tests:
   - fixtures for known tricky titles
   - forbid empty/whitespace IDs
   - ensure expansion is byte-identical for fixed version

3. Migration posture:
   - Either keep stored values as full URIs and support short-form only at ingest UI
     (convert to full URI at ingest time), or
   - Introduce a separate column (or metadata field) for “raw input” vs “canonical IRI”.

Until those are in place, **Option 1 remains the only supported representation**.

