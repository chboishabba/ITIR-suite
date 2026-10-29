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
- Shared speech/transcript infrastructure should prefer WhisperX-WebUI, or a
  compatible successor, as the reusable external transcription surface across
  ITIR-adjacent projects.

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
- Define and stabilize the call-intelligence / livestream transcription
  completion seam so new completion-oriented transcription projects can roll
  into the WhisperX-WebUI surface instead of creating separate incompatible
  contracts.

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

## Milestone M4: Sublinear Topic Scaling & Conductor Cost Functions (May 2026)
- Deliverables:
  - Sublinear Topic Extraction: As conversation volume expands from 500 to 3,000+ chats,
    extract sublinearly scaling primary topic manifolds ($\mathcal{T}(N) \sim C \cdot N^\gamma, \gamma < 0.5$)
    with 20–50 concrete implementation goals per topic.
  - Topic-Centric Rotation: Replace naive thread rotation with topic-level rotation,
    using `itir.chatgpt.revive` and headless `curl_cffi` to synthesize cross-thread history
    and rich PostgreSQL world-model context.
  - Conductor Cost Function: Dynamic worker sizing balancing continuous $\alpha$-priority,
    perplexity, frontier obstruction counts (e.g. 4 unblocked workers on 4 lemmas), and
    sub-eigen dimensionality, preventing blind overspawning up to capacity $W=20$.
  - Canonical Presets: Updated all worker prompt presets (`@max_cut`, `@grug_ste100`, `@zkp_qa`,
    `@introspective_viz`, `@converge_toe`, `@referee_pass`, `@rpd`, `@steelman`, `@lemmas`,
    `@surrounds`, `@docs`) to unconditionally mandate checking `dashi_lean4` and `dashi_agda`
    golden formalisms before generating code.

## Milestone M5: `itir-dioxus` Interactive Graph & Sankey UI (Jun 2026)
- Deliverables:
  - Multi-Scale Topic Explorer: Click extracted main topic $\to$ view constituent goals $\to$
    deliverables timeline across conversations.
  - Cross-Project Drag-and-Drop Node Graph: Interactive canvas connecting nodes across
    `ITIR-suite`, `SensibLaw`, `StatiBaker`, and `SeaMeInIt` with governed bridge receipts.
  - Multi-Metric Sankey Flow: Visualizing flow from chats to PNF factor clusters to active worker lanes,
    with dynamic metric toggling (Continuous $\alpha$, Perplexity, Frontier Blockers, Task Priority).
  - StatiBaker Kanban Integration: Direct projection of topic deliverables into StatiBaker
    Kanban boards linked with Wikidata entity relations.

## Milestone M6: Unified Single Semantic Spine & Full-Corpus AO Allocation (Jul 2026)
- Deliverables:
  - PostgreSQL Single Canonical Spine: Unify storage onto TrueNAS PostgreSQL (`sensiblaw_sparse_ready_20260818`),
    housing transcripts (`corpus.chat_archive_message`), PNF relational world models (`pnf.statement_candidate_factor`, `pnf.graph`),
    planning/docs/user stories (`corpus.document_manifest`), StatiBaker kanban deliverables (`task.candidate`),
    Wikidata entity alignments (`wikidata.claim_entity`), and formal proof gaps (`formal.proof_gap`).
  - Edge Cache & WAL Separation: Local SQLite (`~/.chatgpt_history.sqlite3`) transitions to an edge cache
    and write-ahead log for fast headless `curl_cffi` streaming, registered immutably into PG via
    `register_sqlite_chat_coordinates` (`archive_locator="sqlite:canonical#<node_id>"`).
  - 1,000+ Conversation Tranche Expansion: Hydrate the 500 next-oldest threads below the top-500 tranche,
    expanding the manifold to 1,000+ conversations and compiling unified PNF spectra.
  - Full-World Pareto Conductor Allocation: Run the autonomous orchestrator (AO) dynamic cost function
    $\mathcal{C}(T_k, W)$ over the entire consolidated world model, cross-pollinating goals across
    ITIR, SensibLaw, StatiBaker, and Wikidata.

## Next Candidate Deliverables
- Python ingest script for `conversations.json`.
- TIRC recurrence query set.
- Unified super-corpus mapping across legal / NotebookLM / ChatGPT sources.
- Explicit ITIR roadmap item for WhisperX-WebUI-backed call intelligence and
  livestream transcription completions as a shared service/interface layer.
- Cross-project contract note covering how Corkysoft and other operator-facing
  tools submit audio, poll jobs, and consume reviewed transcript completions
  from WhisperX-WebUI.
