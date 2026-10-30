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

## Milestone M6: Sole PostgreSQL Store Migration & Deprecation of SQLite/SLRW (Jul 2026)
- Deliverables:
  - **Sole PostgreSQL Store Mandate**: TrueNAS PostgreSQL (`sensiblaw_sparse_ready_20260818`) is the
    **sole and only database** for the entire ITIR suite. No SQLite, no SLRW. All three transitional
    SQLite databases (`~/chat_archive.sqlite`, `~/.chatgpt_history.sqlite3`, `~/.chat_archive.sqlite`)
    and binary `.slrw` files are fully deprecated, backfilled into PostgreSQL, and slated for deletion.
  - **Convergent Manifold Rejuvenation & Thread Coalescence**: Candidates from the PostgreSQL processing
    queue (`corpus.chat_archive_message`, `operational.rejuvenation_job`) are evaluated against the Marchenko-Pastur
    spectral manifold ($\lambda_1, \lambda_2, \lambda_3$) and TrueNAS PostgreSQL PNF factors (`pnf.statement_candidate_factor`).
    Complete-link agglomeration identifies clusters of related disjoint threads tackling the same deliverable
    (e.g., 20 disparate UI threads or 15 separate fluid flux chats). High-overlap threads are yanked from the queue,
    documented with source lineage in `operational.conversation_lineage`, and coalesced into unified, world-enhanced
    joined threads to end infinite loops of disconnected tidbits and converge sublinearly toward completion.
  - **Bounded Formal Slicing & AST Symbol Similarity Engine**: Rather than basic text grep fragments or
    whole-file context dumps, automatically isolate the transitive dependency closure of target lemmas
    (signatures, defining clauses, helper types, and referenced lemmas) via `re_gpt.formal_slicer.build_pruned_formal_slice`
    and `related_symbol_candidates`. Embeds the self-contained pruned Agda slice into the world-enhanced capsule
    and lists exact symbol coordinates (`file:line`), preventing workers from re-inventing existing in-repo constructions.
  - **Golden Sublinear Topic Width Law ($W=20$)**: Wire `itir_mcp.fleet_round_runner.execute_pareto_conductor`
    directly against PostgreSQL to size allocations across topics ($\mathcal{C}(T_k, W) = \alpha(T_k) \cdot \frac{\text{unblocked}}{\text{total}} \cdot \min(20, \dim(\text{SubEigens}), W)$)
    and allocate workers to topic deliverables rather than raw thread IDs.
  - **Formal Family Triangulation & AST Consensus Deduplication (`RNNN` / `R193` & ClaySprint Series)**:
    Rather than letting threads proliferate versioned round files without proof closure (e.g. `Round1` through `Round199`, `ClaySprint1` through `ClaySprint133`),
    `re_gpt.formal_triangulator.triangulate_formal_family` performs an AST-level 3-way partition:
    1. *Shared Invariant Baseline (`[OWNED / VERIFIED]`)*: Verified properties frozen as immutable preconditions.
    2. *Divergent Construction Branches*: Competing hypotheses (e.g., temporal links absorbed into $T_k$ vs tracked as spatial boundary defects) exposed side-by-side.
    3. *Unresolved Gap Intersection (`[BLOCKED / UNPROVEN]`)*: Universal blockers across all modules isolated as the sole proving frontier (e.g. `round193ClayPromotion = false` and `round193PackageAClosed = false` across `Round190`–`Round199` in `NSTriadKNClayFrontierRound193Exact.agda`; `AllDiameterWeightedKP` in YM).
  - **Git Lineage & Active PR Context in World Evidence**:
    Per `SUBLINEAR_TOPIC_METASYSTEM_AND_DIOXUS_UI.md` (Level 3: Deliverables & PR Lineage) and `pnf_work_packet_v1.md`,
    `re_gpt.automatic_formal_evidence` embeds recent Git commit hashes and active GitHub PRs directly into world gap capsules.
  - Unified Schema Coverage: Transcripts (`corpus.chat_archive_message`), mutation ops (`operational.rejuvenation_job`),
    PNF relational factors (`pnf.statement_candidate_factor`, `pnf.candidate_semantic_product`, `pnf.graph`),
    docs & user stories (`corpus.document_manifest`), StatiBaker deliverables (`task.candidate`, `goal.timeline`),
    Wikidata entities (`wikidata.claim_entity`), and formal proof gaps (`formal.proof_gap`) reside exclusively in PostgreSQL.
  - Headless CFFI Direct-to-PG: Wire `MutationService` directly to PostgreSQL for turns and SSE receipts.
  - Full-World Pareto Conductor Allocation: Run the autonomous orchestrator (AO) dynamic cost function
    $\mathcal{C}(T_k, W)$ directly against PostgreSQL across the unified cross-project world model.

## Next Candidate Deliverables
- Python ingest script for `conversations.json`.
- TIRC recurrence query set.
- Unified super-corpus mapping across legal / NotebookLM / ChatGPT sources.
- Explicit ITIR roadmap item for WhisperX-WebUI-backed call intelligence and
  livestream transcription completions as a shared service/interface layer.
- Cross-project contract note covering how Corkysoft and other operator-facing
  tools submit audio, poll jobs, and consume reviewed transcript completions
  from WhisperX-WebUI.


## Milestone M7: RPD PNF Fibre Bundle and Ontology Lemma Routing (Oct 2026)

- Base implementation must start from `main` commit `cf4ae65` or later. Do not stack this tranche on stale `master`.
- Remove all ad-hoc English predicate sets from the active PNF spectral path. Use SensibLaw parser POS evidence plus data-driven document-frequency and Marchenko–Pastur retention.
- Keep five explicit hierarchy levels: eigenspace, primary topic, subtopic, fibre, typed goal.
- Normalize representational drift as typed child branches under canonical ontology roots. Yang–Mills uses `Q271810` and shared invariant fibre `F_YM`.
- Treat shared fibre invariants as routing/discovery evidence only. They do not imply representation equivalence or automatic theorem transport.
- Preserve the live conductor APIs and dynamic cost law. One round is an orchestration barrier over at most 20 simultaneously independent workers. Twenty rounds permit at most 400 planned worker calls.
- Concurrent lanes require explicit pairwise `noTypedMeet` separation over files, symbols, and lemmas.
- Reuse SensibLaw Wikimedia providers. Resolve permanent Wikidata QIDs where supported. Keep novel frontier nodes as candidate-only `cand:Q_*` records with explicit `P279`/`P361` anchors and observational P2738 disjointness audit.
- Route verified lemma references only along explicit ontology edges and explicit lemma attachments. Ontology ancestry never creates proof authority.
- Golden safe Agda is authoritative; Lean mirrors Agda. Reuse current dashi_agda TOE/fleet formal owners instead of creating a competing scheduler formalism.
- Acceptance requires focused deterministic Python tests, zero ESD edits, zero hardcoded lexical wordlists, and no regression of `execute_pareto_conductor`, `spawn_parallel_lanes`, or the live cost-law contract.
