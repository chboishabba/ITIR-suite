# Unified Single Semantic Spine: PostgreSQL Canonical Store & Full-World AO Allocation

**Status:** Approved Architecture & Phase Roadmap  
**Target Milestone:** M6 (Jul 2026)  
**Cross-Project Scope:** `ITIR-suite` $\leftrightarrow$ `SensibLaw` $\leftrightarrow$ `StatiBaker` $\leftrightarrow$ `reverse-engineered-chatgpt` $\leftrightarrow$ `DASHI`

---

## 1. Executive Summary & Problem Framing

Currently, conversation and semantic assets span two local SQLite databases (`~/.chatgpt_history.sqlite3` for re-gpt operational turns, and `~/chat_archive.sqlite` with 814k messages and 6.9k threads for structured canonical archives) alongside a high-capacity TrueNAS PostgreSQL cluster (`postgresql://admin:admin@truenas.local:5432/sensiblaw_sparse_ready_20260818`, housing 124 tables, 157k PNF factor rows, and semantic product lattices).

To resolve fragmentation and enable the **Autonomous Orchestrator (AO)** to allocate resources across the **entire universe of repository knowledge** (chats, docs, planning, user stories, Wikidata relations, proof gaps, and golden formalisms), we define the migration to a **single canonical PostgreSQL semantic spine**, with local SQLite operating strictly as a fast edge write-ahead log (WAL) and local execution cache.

---

## 2. Store Topology: Canonical PostgreSQL Spine + Local Edge Cache

```mermaid
flowchart TD
    subgraph Edge ["Local Developer Environment (Edge)"]
        CFFI["Headless curl_cffi / Async Engine"]
        SQLite["~/.chatgpt_history.sqlite3<br/>(Local Edge WAL & Fast Turn Cache)"]
        LocalCLI["Local Referees & Preflight<br/>(dashi-agda-preflight / pytest)"]
    end

    subgraph Spine ["TrueNAS PostgreSQL Cluster (sensiblaw_sparse_ready_20260818)"]
        PG_Chat["corpus.chat_archive_message<br/>(Unified Transcripts & Turn Digests)"]
        PG_PNF["pnf.statement_candidate_factor & pnf.graph<br/>(Relational PNF Candidates & World Atoms)"]
        PG_Docs["corpus.document_manifest<br/>(Markdown, Architecture Specs, User Stories)"]
        PG_Stati["task.candidate & goal.timeline<br/>(StatiBaker Kanban Cards & Roadmap Milestones)"]
        PG_Wiki["wikidata.claim_entity & disjointness<br/>(Wikidata Relations & Ontologies)"]
        PG_Formal["formal.proof_gap & theorem_manifest<br/>(Lean 4 / Golden Agda Formalisms)"]
    end

    subgraph Orchestration ["Autonomous Orchestrator (AO) & Dynamic Conductor"]
        Spectral["Continuous/Discrete Pareto Manifold<br/>(t-SNE / Eigenspace Spectral Decomposition)"]
        CostFunc["Dynamic Conductor Sizing:<br/>C(T_k, W) = α · (unblocked/total) · min(W_cap, dim(SubEigens), W)"]
        Workers["Governed Worker Fleet (Max W=20)<br/>Dispatched across Sublinear Topic Manifolds"]
    end

    CFFI -->|Fast Local Write| SQLite
    SQLite -->|One-Way Immutable Sync<br/>register_sqlite_chat_coordinates| PG_Chat
    LocalCLI -->|Proof Gap Analysis| PG_Formal

    PG_Chat --> Spectral
    PG_PNF --> Spectral
    PG_Docs --> Spectral
    PG_Stati --> Spectral
    PG_Wiki --> Spectral
    PG_Formal --> Spectral

    Spectral --> CostFunc
    CostFunc --> Workers
    Workers -->|Golden Agda + Code PRs| Edge
```

### 2.1 Why Not Pure SQLite?
- **Global Cross-Project Joins:** SQLite cannot easily cross-join across 157k PNF relational factor products, distributed Wikidata entities, and live proof gaps without mounting gigabyte SQLite files across machines.
- **Concurrent Worker Ingest:** Multiple remote workers and local background pipelines require robust MVCC (Multi-Version Concurrency Control) and row-level locking provided natively by PostgreSQL.
- **Single Source of Truth:** Unifying everything in PostgreSQL allows a single SQL query or view to trace:
  $$\text{User Story} \longrightarrow \text{StatiBaker Task} \longrightarrow \text{Chat Turn} \longrightarrow \text{PNF Factor} \longrightarrow \text{Proof Gap} \longrightarrow \text{Golden Agda Lemma}$$

### 2.2 Why Keep Local SQLite as Edge WAL?
- **Zero-Latency Headless Turns:** Headless `curl_cffi` writes immediately to local SQLite in milliseconds, insulating conversational turns from network spikes to the TrueNAS storage pool.
- **Fail-Closed Offline Operation:** If TrueNAS is undergoing ZFS scrubbing or network maintenance, local development, tests, and CLI continuation continue uninterrupted.
- **Immutable Registration:** Synchronization to PostgreSQL uses `register_sqlite_chat_coordinates()` with `archive_locator="sqlite:canonical#<node_id>"` and `body_sha256` hashing—never destructive overwrites.

---

## 3. The 6 Dimensions of the Unified World Model

Rather than running the AO over an isolated 500-chat slice, the entire corpus will be ingested into the unified semantic spine:

| Domain Layer | Canonical PostgreSQL Table / Schema | Role in AO Dynamic Scheduling |
| :--- | :--- | :--- |
| **1. Conversations** | `corpus.chat_archive_message` | 2,389+ threads providing historical theory evolution, reasoning logs, and past design decisions. |
| **2. PNF World Model** | `pnf.statement_candidate_factor`, `pnf.graph` | Relational dependency frames ($S \to V \to O$), extracting motifs and thematic centroids. |
| **3. Project Docs & RFCs** | `corpus.document_manifest` | READMEs, ADRs, user stories, and specs defining system requirements. |
| **4. StatiBaker Planning** | `task.candidate`, `goal.timeline` | Kanban deliverables, unblocked milestones, and deliverable sequencing. |
| **5. Wikidata & Ontologies** | `wikidata.claim_entity`, `wikidata.disjointness` | External entity grounding, structural disjointness, and superclass pressure. |
| **6. Formal Proof Gaps** | `formal.proof_gap`, `formal.theorem_manifest` | Unproven lemmas, postulate boundaries, and golden Agda/Lean theorem interfaces. |

---

## 4. Sublinear Topic Scaling & Dynamic AO Allocation

### 4.1 Sublinear Manifold Collapse Law
As conversation volume expands from 500 to 3,000+ chats, topics do not grow linearly:
$$\mathcal{T}(N) \sim C \cdot N^\gamma \quad (\gamma < 0.5)$$
- 500 conversations collapse into $\approx 30$–$50$ primary topic clusters.
- 3,000 conversations collapse into $\approx 250$–$350$ primary topic manifolds.
- Each primary topic manifold aggregates $20$–$50$ temporal deliverables sourced across dozens of separate conversations over months.

### 4.2 Dynamic Worker Sizing Function
Naive rotation through 3,000 individual threads starves low-$\alpha$ topics. The AO rotates through **topics**, utilizing the dynamic cost function:
$$\mathcal{C}(T_k, W) = \alpha(T_k) \cdot \frac{\text{unblocked\_goals}}{\text{total\_goals}} \cdot \min\left(W_{\text{cap}}, \dim(\text{SubEigens}), W\right) - \text{TokenCost}(W)$$

- **Low-$\alpha$ Sub-Topics:** Automatically rolled into their parent topic manifold as sequenced internal work packets (preventing starvation while preserving cross-pollination promotion).
- **Worker Allocation:** Sequential theorem chains receive 1 worker; parallelizable frontier blockers receive workers matched to the unblocked lemma count up to $W=20$.

---

## 5. Mandatory Golden Agda Invariant on All Worker Turns

Every dispatch to remote MCP workers unconditionally mandates:
> **"Check dashi_lean4 and dashi_agda and formalise the current problem in terms of relevant in-repo machinery. and ensure to keep the formalism in-step with the impl. recall the agdas are the golden."**

All prompt presets (`@rpd`, `@steelman`, `@lemmas`, `@surrounds`, `@docs`, `@max_cut`, `@grug_ste100`, `@zkp_qa`, `@introspective_viz`, `@converge_toe`, `@referee_pass`) enforce this rule. Any implementation returned by a remote worker is validated against local Agda/Lean referees (`dashi-agda-preflight`, `ExactGapComparator`) with **strictly zero postulates, zero unsolved metas, and zero TERMINATING pragmas**.
