• Here’s the current ingest → DB flow, based on what’s in this repo today. There are a few parallel “DBs”/schemas, so I’m outlining each path and where it lands.

  1) PDF / legal document ingest → VersionedStore (SQLite)

  - Entry point: src/pdf_ingest.py (process_pdf / iter_process_pdf).
  - Flow: extract PDF text → build Document (sections, TOC, rules) → validate payload sizes → persist.
  - DB: src/storage/versioned_store.py (tables: documents, revisions, toc, provisions, rule_atoms, plus FTS tables).
  - Persist happens only if db_path is provided; it calls VersionedStore.generate_id() and VersionedStore.add_revision(...).
  - References: docs/ingestion.md, src/pdf_ingest.py, src/storage/versioned_store.py.

  2) AustLII search/fetch → PDF ingest → VersionedStore

  - Entry: src/ingestion/austlii_pipeline.py (ingest_pdf_from_search).
  - Flow: SINO search → select hit → fetch PDF → calls process_pdf(..., db_path=...).
  - References: src/ingestion/austlii_pipeline.py, src/pdf_ingest.py.

  3) Citation-following ingest (helper)

  - src/ingestion/citation_follow.py orchestrates bounded follow of citations.
  - It expects an ingest(...) callback; in practice that’s the same PDF ingest + VersionedStore path.
  - Reference: src/ingestion/citation_follow.py.

  4) Story/event ingest → core Storage (SQLite)

  - Entry: src/sensiblaw/ingest/story_importer.py (DefaultStoryImporter.import_stories).
  - Validates against schemas/event.schema.yaml, then inserts nodes via Storage.insert_node.
  - DB: src/storage/schema.sql used by src/storage/core.py.
  - API mention: legacy /import_stories in docs/api.md.
  - References: src/sensiblaw/ingest/story_importer.py, src/storage/core.py, src/storage/schema.sql, schemas/event.schema.yaml, docs/api.md.

  5) Ontology / legal source upsert → ontology schema (SQLite)

  - Entry: CLI ontology upsert in cli/__main__.py calling sensiblaw/db/dao.py.
  - DB schema managed by src/sensiblaw/db/migrations via MigrationRunner.
  - References: cli/__main__.py, src/sensiblaw/db/dao.py, src/sensiblaw/db/migrations.

  6) Rule-atom anchoring → lightweight normalized tables

  - src/ingestion/anchors.py writes rule atoms + actor classes to a simple SQLite schema.
  - This is a separate store from VersionedStore and the ontology migrations.
  - Reference: src/ingestion/anchors.py.

  If you want, tell me which “DB” you mean (VersionedStore vs core Storage vs ontology DB), and I can drill into the exact tables/columns and the ingest call chain.
