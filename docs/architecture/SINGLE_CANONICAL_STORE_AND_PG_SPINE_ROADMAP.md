# Architecture Directive: Sole PostgreSQL Store Mandate & Full Deprecation of SQLite and SLRW

**Status:** MANDATORY SOLE DATABASE ARCHITECTURE DIRECTIVE  
**Authority:** System Ground-Truth Invariant  
**Target Cluster:** TrueNAS PostgreSQL (`postgresql://admin:admin@truenas.local:5432/sensiblaw_sparse_ready_20260818`)  
**Scope:** Complete deprecation, migration, and retirement of all SQLite files (`~/chat_archive.sqlite`, `~/.chatgpt_history.sqlite3`, `~/.chat_archive.sqlite`) and offline binary `.slrw` / `.slro` files.

---

## 1. Absolute Rule: The Sole Database Mandate

> **POSTGRESQL IS THE SOLE AND ONLY DATABASE. PERIOD. FULL STOP. END OF STORY.**
> 
> No SQLite. No SLRW. No edge/split-database compromise.
> All repository knowledge, operational state, and analytical models reside exclusively in PostgreSQL.

Any past documentation, notes, or code implying a permanent two-tier split (e.g. SQLite as a permanent edge cache alongside PostgreSQL) is **EXPLICITLY REJECTED AND SUPERSEDED**. The existence of three separate SQLite databases and offline `.slrw` files was an accidental transitional duplication in contradiction with the true architecture.

```mermaid
flowchart TD
    subgraph Deprecated ["DEPRECATED & SCHEDULED FOR DELETION"]
        D1["~/chat_archive.sqlite (814k msgs)"]
        D2["~/.chatgpt_history.sqlite3 (230k msgs)"]
        D3["~/.chat_archive.sqlite (Legacy)"]
        D4["*.slrw / *.slro (Offline Binary World Models)"]
    end

    subgraph SoleStore ["THE ONLY DATABASE: TrueNAS PostgreSQL (sensiblaw_sparse_ready_20260818)"]
        PG_Chat["corpus.chat_archive_message<br/>(ALL Chat Transcripts, Turns, and Coordinates)"]
        PG_Ops["ops.mutation_operation & ops.receipt<br/>(Worker Turns, Mutation State, SSE Streams)"]
        PG_PNF["pnf.statement_candidate_factor & pnf.graph<br/>(Relational PNF Candidates & World Atoms)"]
        PG_Docs["corpus.document_manifest<br/>(Markdown Specs, ADRs, User Stories)"]
        PG_Stati["task.candidate & goal.timeline<br/>(StatiBaker Deliverables & Kanban Boards)"]
        PG_Wiki["wikidata.claim_entity & disjointness<br/>(Wikidata Relations & Ontological Graphs)"]
        PG_Formal["formal.proof_gap & theorem_manifest<br/>(Lean 4 & Golden Agda Proofs/Lemmas)"]
    end

    subgraph AO ["Autonomous Orchestrator (AO) & Pareto Conductor"]
        Conductor["Dynamic Sizing & Sublinear Topic Rotation<br/>Directly Querying Sole PostgreSQL Spine"]
    end

    D1 -->|One-Way Backfill & Migrate| SoleStore
    D2 -->|One-Way Backfill & Migrate| SoleStore
    D3 -->|One-Way Backfill & Migrate| SoleStore
    D4 -->|Ingest Candidates into PG| SoleStore

    SoleStore --> Conductor
```

---

## 2. Inventory of Deprecated Stores to Delete

All data currently trapped in transitional stores must be migrated into PostgreSQL, after which these files will be retired and deleted:

1. **`~/chat_archive.sqlite` (2.1 GB, 814,612 messages, 6,961 threads):**
   - *Target:* Ingest all canonical transcripts into `corpus.chat_archive_message` in PostgreSQL.
   - *Disposition:* Delete SQLite database upon migration verification.
2. **`~/.chatgpt_history.sqlite3` (896 MB, 229,735 messages, 2,389 threads):**
   - *Target:* Reconcile operational mutation tables into `ops.mutation_operation` and merge novel thread message trees into `corpus.chat_archive_message`.
   - *Disposition:* Delete SQLite database upon migration verification.
3. **`~/.chat_archive.sqlite` (1.4 MB, historical legacy):**
   - *Target:* Verify no orphan threads remain; discard.
   - *Disposition:* Delete SQLite database.
4. **Offline `.slrw` / `.slro` files (`/home/c/.chatgpt_fleet_world/*`):**
   - *Target:* Ingest any remaining PNF statement factors into `pnf.statement_candidate_factor` and `pnf.graph` in PostgreSQL.
   - *Disposition:* Delete binary files; all spectral graph computations run directly against PostgreSQL views and materialized tables.

---

## 3. The 7 Schemas of the Sole PostgreSQL Database

Every subsystem of the ITIR suite maps directly to a native PostgreSQL schema:

| Subsystem | PostgreSQL Tables / Views | Responsibility |
| :--- | :--- | :--- |
| **Conversations** | `corpus.chat_archive_message`, `corpus.conversation` | Transcripts, turns, timestamps, author roles, parent/child branches. |
| **Operations** | `ops.mutation_operation`, `ops.receipt` | Governed worker execution receipts, SSE activity digests, reconcile states. |
| **PNF World Model** | `pnf.statement_candidate_factor`, `pnf.graph`, `pnf.candidate_semantic_product` | 157k+ relational dependency factors ($S \to V \to O$), semantic product lattices. |
| **Project Docs & RFCs** | `corpus.document_manifest`, `corpus.doc_section` | In-repo documentation, architecture specs, user stories, decision records. |
| **StatiBaker Planning** | `task.candidate`, `goal.timeline`, `task.kanban_card` | Roadmap deliverables, milestone timelines, goal dependencies. |
| **Wikidata & Ontologies** | `wikidata.claim_entity`, `wikidata.disjointness` | External entity grounding, structural disjointness, ontology alignments. |
| **Formal Verification** | `formal.proof_gap`, `formal.theorem_manifest` | Unproven lemmas, theorem hashes, golden Agda/Lean interface contracts. |

---

## 4. Migration Plan & Deprecation Gates

1. **Gate 1 — Schema Verification [COMPLETE]:** Verified `corpus.chat_archive_message`, `corpus.document`, `corpus.span`, `corpus.binary_content`, and `corpus.canonical_content` in `sensiblaw_sparse_ready_20260818` accommodate full message graphs, content hashes, and mutation receipts.
2. **Gate 2 — Transcript Ingest [ACTIVE / 6a% COMPLETE]:**
   - Implemented streaming relational migrator `scripts/migrate_sqlite_to_postgres_corpus.py` (2,800+ msgs/sec).
   - Ingested 1,389 messages of the `6a%` tranche with full 5-stage relational integrity (`binary_content` -> `canonical_content` -> `document` -> `span` -> `chat_archive_message`).
   - Verified 1,389 rows active in TrueNAS PostgreSQL.
3. **Gate 3 — Headless CFFI Direct-to-PG:** Switch `MutationService` and headless `curl_cffi` write transports to connect directly to PostgreSQL, removing SQLite write paths.
4. **Gate 4 — Spectral Pipeline Switch:** Ensure `hierarchical_corpus_manifold.py` and `load_preferred_semantic_corpus` query PostgreSQL as the only source, disabling `.slrw` file fallback.
5. **Gate 5 — Deletion of SQLite & SLRW:** Remove the local `.sqlite` and `.slrw` files permanently.
