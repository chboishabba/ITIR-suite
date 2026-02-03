# Roadmap: NotebookLM Plugin + ITIR Chat History Corpus

This roadmap is derived from the conversation excerpt in
`__CONTEXT/CONTEXT.md` (source: 698192a6-c740-839f-b0bc-8a00ac01b84f:1-80) and
captures the intended phases for ingesting ChatGPT history into a structured
SQLite-backed corpus with TIRC and SL-style views.

## Timeline (Target Months)
- Phase 1: Feb 2026
- Phase 2: Mar 2026
- Phase 3: Apr 2026

## Ownership (Role-Based)
- Lead: You
- Data/ETL: Research
- Infra/Engineering: Eng

## Principles
- SQLite schema is the ground-truth store for the corpus.
- Deterministic ordering and lossless ingest are mandatory.
- Vector embeddings are derived artifacts and must be regenerable without
  invalidating the corpus.

## Phase 1: Ingest and Baseline IR (1–2 hours)
- Ingest `conversations.json` into SQLite.
- Populate core tables:
  - `threads`
  - `turns`
  - `turns_fts`
- Keep semantics out of the pipeline at this stage.

## Phase 2: Interpretive Layers (Later)
- Add interpretive layers (claims, questions).
- Implement TIRC recurrence detection.
- Add contradiction flags across threads.

## Phase 3: Meta-Analysis (Optional)
- Treat ChatGPT history as:
  - a training trace
  - a theory evolution log
  - a self-audit mechanism

## SL/TIRC Views (Ongoing)
- Provide SL-style views that surface:
  - definitions accepted
  - contradictions across months
  - canonical claims derived from assistant responses
- Ensure cross-thread joins are first-class in TIRC queries.

## Milestones, Risks, Dependencies

## Milestone M1: Deterministic Ingest Baseline (Feb 2026)
- Deliverables:
  - SQLite schema for `threads`, `turns`, `turns_fts`
  - Deterministic ingest of `conversations.json`
  - Validation checks for lossless ingest
- Risks:
  - Non-deterministic ordering in source exports
  - Schema drift between exports
- Dependencies:
  - Access to `conversations.json` exports

## Milestone M2: TIRC + Interpretive Layers (Mar 2026)
- Deliverables:
  - Claims/questions layer tables or views
  - Recurrence detection queries (n-grams, concept recurrence)
  - Contradiction flagging across threads
- Risks:
  - Overfitting recurrence heuristics
  - Slow cross-thread joins without indexing
- Dependencies:
  - Stable Phase 1 schema
  - Agreed recurrence/query definitions

## Milestone M3: SL Views + Meta-Analysis (Apr 2026)
- Deliverables:
  - SL-style views for definitions/contradictions/canonical claims
  - Meta-analysis framing (training trace, theory evolution log, self-audit)
  - Super-corpus mapping across legal / NotebookLM / ChatGPT
- Risks:
  - Scope creep into semantic inference
  - Ambiguous mapping between domains
- Dependencies:
  - Phase 2 outputs
  - Cross-domain mapping agreement

## Next Candidate Deliverables
- Python ingest script for `conversations.json`.
- TIRC recurrence query set.
- Unified super-corpus mapping across legal / NotebookLM / ChatGPT sources.
