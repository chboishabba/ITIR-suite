Got it — you want **comprehensive, concrete help** pulling ITIR together at the *documentation + roadmap* level, now that:

* SL’s **deterministic structural spine** is solid and correctly scoped
* the “logic graph confusion” is resolved and documented
* ITIR-suite is now a **meta-repo with submodules**
* the Epstein / tranche / citizen-journalism use-case is explicit

Below is a **clean, opinionated ITIR documentation + roadmap package** you can drop straight into the suite. This is not hand-wavy vision; it’s meant to guide real work without collapsing SL/ITIR boundaries.

---

# ITIR: Documentation & Roadmap (Authoritative Draft)

## 0. One-paragraph positioning (this should appear early in docs)

> **ITIR (Investigative & Interpretive Reasoning)** is a collaborative analysis layer that operates *over* the SensibLaw (SL) structural substrate.
> SL guarantees deterministic, span-anchored truth of source material.
> ITIR enables hypotheses, claims, narratives, and disagreement — always explicitly, always attributable, always reversible.

This sentence is the anchor. Everything else should be consistent with it.

---

## 1. Architectural layering (lock this in)

### Layer 0 — Raw sources

* PDFs, scans, audio, spreadsheets, emails, images
* Redactions preserved verbatim
* Originals immutable

### Layer 1 — SL (Structural substrate)

* Canonical token stream
* Span offsets
* Logic tree (structural, not semantic)
* Page maps
* Provenance
* Deterministic exports (JSON / SQLite / DOT)

**Invariant:**
SL never asserts meaning, intent, or truth beyond literal structure.

---

### Layer 2 — ITIR Core (Interpretive overlay)

This is what ITIR *is*.

ITIR introduces **objects that are not facts**:

| Object       | Meaning                                            |
| ------------ | -------------------------------------------------- |
| Claim        | Someone asserts something                          |
| Hypothesis   | A tentative model (actor, motive, event, timeline) |
| Actor        | An identity hypothesis, not a resolved person      |
| Event        | A hypothesised occurrence                          |
| Narrative    | An ordered interpretation                          |
| Relationship | Supports / contradicts / implies / uncertain       |
| Confidence   | Explicit uncertainty                               |
| Attribution  | Who proposed this, when, why                       |

**Invariant:**
Every ITIR object must reference SL spans.

No free-floating meaning. No detached summaries.

---

### Layer 3 — Collaboration / distribution

* Forks
* Branches
* Competing interpretations
* Merges with attribution
* No forced consensus

This is where “good citizen journalism” lives.

---

## 2. What ITIR explicitly allows (and SL forbids)

This table belongs in docs.

| Capability          | SL | ITIR                     |
| ------------------- | -- | ------------------------ |
| Tokenisation        | ✅  | ❌                        |
| Structural spans    | ✅  | ❌                        |
| Logic tree          | ✅  | ❌                        |
| Claim assertion     | ❌  | ✅                        |
| Hypothesis          | ❌  | ✅                        |
| Actor unification   | ❌  | ✅ (tentative)            |
| Redaction inference | ❌  | ✅ (explicitly uncertain) |
| Narrative building  | ❌  | ✅                        |
| Disagreement        | ❌  | ✅                        |
| Forking             | ❌  | ✅                        |

This prevents future scope creep.

---

## 3. Redactions as first-class citizens (must be documented)

### In SL

* Redactions are literal spans:

  * `[REDACTED]`
  * black boxes
  * missing pages
* Stored with offsets
* No guessing

### In ITIR

Redactions become:

* uncertainty anchors
* comparison points across documents
* evidence of omission
* investigative signals

**Example questions ITIR may ask:**

* “Which names are always redacted?”
* “What appears immediately before/after redactions?”
* “Which actors disappear after page X?”

SL never answers these.
ITIR can — explicitly, with uncertainty.

---

## 4. ITIR data model (minimal but sufficient)

This should be a dedicated doc (`docs/itir_model.md`).

### Core tables / collections (conceptual)

#### Claim

```text
claim_id
asserted_by (user / org / branch)
span_refs [(doc_id, start, end)]
text (optional, derived)
confidence
created_at
```

#### Hypothesis

```text
hypothesis_id
type (actor | event | motive | timeline)
description
supporting_claims []
contradicting_claims []
confidence
```

#### Actor (hypothesis)

```text
actor_id
labels [name variants]
evidence_spans []
confidence
```

#### Relationship

```text
source_id
target_id
relation_type (supports | contradicts | implies | uncertain)
provenance_spans []
confidence
```

**Hard invariant:**
No ITIR object exists without at least one `(doc_id, span)` reference.

---

## 5. Git-like collaboration model (very important)

You should document this explicitly — it’s a differentiator.

### Mental model

* SL = read-only `main`
* ITIR = branches

### Properties

* Branches may:

  * disagree
  * contradict
  * overlap
* Nothing forces merge
* Merges require attribution
* History preserved

### Why this matters

* Journalists can explore risky hypotheses safely
* Lawyers can maintain conservative branches
* Activists can publish interpretations without mutating source truth

This is **epistemic safety by design**.

---

## 6. File-type diversity (ITIR responsibility)

ITIR must accept that:

* not all sources are text
* not all text is reliable
* OCR errors exist
* metadata matters

### SL responsibility

* extract text where possible
* preserve originals
* anchor text to artifacts

### ITIR responsibility

* align across modalities
* track confidence
* record uncertainty
* never overwrite SL text

---

## 7. Roadmap (realistic, staged)

### Phase 1 — ITIR skeleton (docs + empty schema)

**Goal:** make it impossible to accidentally add inference to SL.

* [ ] ITIR model doc (claims, hypotheses, actors)
* [ ] Explicit namespace separation in repos
* [ ] “No ITIR object without span” test
* [ ] Read-only SL contract documented

*No UI. No inference.*

---

### Phase 2 — Manual interpretive tooling

**Goal:** human-driven investigation.

* [ ] Create claims manually
* [ ] Attach spans
* [ ] Build simple relationship graphs
* [ ] Visualise disagreements

This already supports citizen journalism.

---

### Phase 3 — Assisted analysis (optional)

**Goal:** speed, not authority.

* [ ] Pattern-suggested claims (flagged as suggestions)
* [ ] Actor clustering suggestions
* [ ] Timeline candidates
* [ ] Never auto-accept

Still no ML authority.

---

### Phase 4 — Publication & audit

**Goal:** safe release.

* [ ] Publish a branch as narrative
* [ ] Include provenance overlays
* [ ] Show uncertainty explicitly
* [ ] Link back to SL for verification

---

## 8. Documentation set you should now have

At minimum, the ITIR-suite should contain:

* `README.md` (you’ve added this ✅)
* `docs/architecture.md` (SL vs ITIR)
* `docs/logic_graph_layers.md` (already added ✅)
* `docs/principle_relationship_map.md` (already added ✅)
* `docs/itir_model.md` (next)
* `docs/redactions.md` (next)
* `docs/collaboration.md` (git-like branching)
* `docs/roadmap.md`

These are not redundant — each enforces a boundary.

---

## 9. One sentence that should appear verbatim in ITIR docs

> **ITIR allows interpretation without mutating truth; SL guarantees truth without interpretation.**

If future contributors violate this, you have a clear standard to point to.

---

## 10. Bottom line

You are *not* behind.
You are exactly where a serious investigative system must be **before** it becomes powerful.

Most systems:

* infer too early
* collapse uncertainty
* hallucinate consensus

Your stack:

* preserves disagreement
* exposes provenance
* supports distributed inquiry

That’s what makes Epstein-style tranches survivable — legally, ethically, and epistemically.

If you want, next I can:

* write `docs/itir_model.md` in full
* sketch the minimal DB schema for ITIR
* design the first “investigative branch” walkthrough
* or convert this into a formal ADR set

Just tell me where you want the pressure applied.


Perfect — this is the right moment to **lock ITIR in as a first-class system** rather than an aspiration.

Below are **four concrete deliverables**, written so you can drop them straight into the repo with minimal editing:

1. **`docs/itir_model.md` — full, authoritative**
2. **Minimal ITIR DB schema (implementation-agnostic)**
3. **First investigative branch walkthrough (Epstein-class tranche)**
4. **Formal ADR set (architecture decision records)**

I’ll keep everything consistent with the SL/ITIR separation you’ve already enforced.

---

# 1. `docs/itir_model.md` (FULL)

```md
# ITIR Data Model

## Purpose

ITIR (Investigative & Interpretive Reasoning) defines the **explicit interpretation layer** over the SensibLaw (SL) structural substrate.

ITIR objects represent **claims, hypotheses, actors, events, and relationships** that are:
- non-authoritative
- explicitly attributed
- reversible
- span-backed by SL

ITIR never mutates source text or structural spans.  
All interpretation remains an overlay.

---

## Core Principle

> **Every ITIR object must cite SL spans.  
> No interpretation exists without provenance.**

---

## Object Classes

### Claim

A Claim represents an asserted statement about the world.

Claims may be true, false, disputed, or unknown.

**Required fields**
- `claim_id`
- `asserted_by` (user, org, branch)
- `span_refs` (list of `(doc_id, start, end)`)
- `confidence` (0–1 or enum)
- `created_at`

**Optional**
- `summary` (derived, non-authoritative)
- `notes`

Claims do not imply correctness.

---

### Hypothesis

A Hypothesis is a tentative explanatory model.

Types include:
- `actor`
- `event`
- `motive`
- `timeline`
- `relationship`

**Required**
- `hypothesis_id`
- `type`
- `description`
- `supporting_claims`
- `contradicting_claims`
- `confidence`

Hypotheses may coexist and conflict.

---

### Actor (Hypothesis subtype)

Actors represent **identity hypotheses**, not resolved entities.

**Fields**
- `actor_id`
- `labels` (names, aliases, spellings)
- `evidence_spans`
- `confidence`

Actors may be merged or split later; history is preserved.

---

### Event (Hypothesis subtype)

Represents a hypothesised occurrence.

**Fields**
- `event_id`
- `description`
- `time_bounds` (optional)
- `evidence_spans`
- `confidence`

---

### Relationship

Directed relationships between ITIR objects.

**Types**
- `supports`
- `contradicts`
- `implies`
- `associated_with`
- `uncertain`

**Required**
- `source_id`
- `target_id`
- `relation_type`
- `provenance_spans`
- `confidence`

---

## Redactions & Uncertainty

Redactions are **structural spans in SL**.

In ITIR:
- redactions may anchor hypotheses
- uncertainty must be explicit
- no filling or guessing allowed

Example:
> “Actor A appears adjacent to repeated redactions in documents X, Y.”

---

## Branching & Attribution

All ITIR objects belong to a **branch**.

Branches:
- may diverge
- may be merged
- never overwrite history

Each object records:
- creator
- branch
- timestamp

---

## Invariants

- No ITIR object without span provenance
- No silent merges
- No inferred truth
- No mutation of SL text
- Deterministic references

---

## Non-goals

ITIR does NOT:
- decide truth
- rank narratives
- resolve guilt
- enforce consensus
- overwrite sources

---

## Summary

ITIR enables **explicit, auditable disagreement** over a shared factual substrate.

SL guarantees everyone sees the same text.  
ITIR allows them to argue responsibly.
```

---

# 2. Minimal ITIR DB Schema (Sketch)

This is **intentionally small**.

You can implement this in SQLite, Postgres, or as JSON-first storage.

---

### `itir_branch`

```sql
branch_id TEXT PRIMARY KEY
parent_branch_id TEXT
created_by TEXT
created_at TIMESTAMP
description TEXT
```

---

### `itir_claim`

```sql
claim_id TEXT PRIMARY KEY
branch_id TEXT
asserted_by TEXT
confidence REAL
created_at TIMESTAMP
```

---

### `itir_claim_span`

```sql
claim_id TEXT
doc_id TEXT
span_start INTEGER
span_end INTEGER
```

---

### `itir_hypothesis`

```sql
hypothesis_id TEXT PRIMARY KEY
branch_id TEXT
type TEXT
description TEXT
confidence REAL
```

---

### `itir_actor`

```sql
actor_id TEXT PRIMARY KEY
branch_id TEXT
confidence REAL
```

---

### `itir_actor_label`

```sql
actor_id TEXT
label TEXT
```

---

### `itir_relationship`

```sql
source_id TEXT
target_id TEXT
relation_type TEXT
confidence REAL
```

---

### `itir_relationship_span`

```sql
source_id TEXT
target_id TEXT
doc_id TEXT
span_start INTEGER
span_end INTEGER
```

---

### **Hard DB Constraint (recommended)**

```sql
CHECK (EXISTS (
  SELECT 1 FROM itir_*_span
))
```

> No interpretation without spans.

---

# 3. First Investigative Branch Walkthrough (Epstein-class)

This is the **canonical example** you should document.

---

## Step 0 — Ingest (SL)

* Ingest tranche PDFs (flight logs, depositions)
* Preserve redactions verbatim
* Produce:

  * canonical tokens
  * spans
  * logic trees

SL is now frozen.

---

## Step 1 — Create an ITIR branch

```text
branch: "epstein-analysis-v1"
parent: main
created_by: journalist_A
```

No interpretation yet.

---

## Step 2 — Add claims

Example claim:

> “Individual X appears in flight log Y on date Z.”

* Attach spans from flight log PDF
* Confidence: medium
* No actor resolution yet

---

## Step 3 — Propose actor hypotheses

Create two actor hypotheses:

* Actor A: “John Doe (politician)”
* Actor B: “John Doe (businessman)”

Attach:

* name spans
* contextual spans
* confidence estimates

No forced merge.

---

## Step 4 — Handle redactions

Claim:

> “Repeated redactions occur adjacent to Actor A mentions.”

* Attach spans around `[REDACTED]`
* Confidence: low–medium
* Explicit uncertainty

---

## Step 5 — Competing branches

Another journalist forks:

```text
branch: "epstein-analysis-alt"
parent: epstein-analysis-v1
```

They:

* dispute Actor A hypothesis
* propose alternative timeline
* add contradictory relationships

Both branches coexist.

---

## Step 6 — Publication

A branch is published with:

* visible uncertainty
* clickable span provenance
* redactions intact
* no authoritative claims

Readers can verify everything back to SL.

---

# 4. ADR Set (Formal)

You should store these in `docs/adr/`.

---

## ADR-001: Separation of Structural and Interpretive Layers

**Status:** Accepted
**Decision:** SL produces structure only; ITIR produces interpretation only.
**Consequences:** No semantic inference at ingest; interpretive layers are explicit.

---

## ADR-002: Span-Anchored Provenance Requirement

**Status:** Accepted
**Decision:** All ITIR objects must reference SL spans.
**Consequences:** Prevents hallucination, enforces auditability.

---

## ADR-003: Redactions as First-Class Objects

**Status:** Accepted
**Decision:** Redactions are preserved verbatim in SL; interpreted only in ITIR.
**Consequences:** Absence becomes analyzable without speculation.

---

## ADR-004: Branch-Based Interpretive Workflow

**Status:** Accepted
**Decision:** ITIR interpretations are branched, not overwritten.
**Consequences:** Enables disagreement, citizen journalism, collaboration.

---

## ADR-005: No Automated Truth Resolution

**Status:** Accepted
**Decision:** ITIR does not resolve truth or guilt automatically.
**Consequences:** Human accountability preserved.

---

## Final sanity check

You now have:

* A **closed SL contract**
* A **fully specified ITIR model**
* A **defensible investigative workflow**
* A **clear legal / epistemic safety story**
* A **roadmap that doesn’t collapse layers**

This is rare. Most systems never get this far without cutting corners.

If you want next, I can:

* turn this into migration tasks
* write ITIR UI wireframes
* design a first CLI (`itir branch create`, `itir claim add`)
* or produce a public-facing “Why this system is safe” explainer

Just say the word.

---

# Conversation: Python plugin for NotebookLM

- ID: 698192a6-c740-839f-b0bc-8a00ac01b84f
- Updated (UTC): 2026-02-03T06:30:03.642401Z
- Source: 698192a6-c740-839f-b0bc-8a00ac01b84f:1-80

## Latest assistant excerpt (lines 1-80)
1. - SQLite schema = **ground truth**
2. - Deterministic ordering
3. - Lossless ingest
4.
5. ### TIRC (Temporal / Thematic Recurrence)
6. - SQL queries over:
7.   - repeated n-grams
8.   - concept recurrence
9.   - question → answer evolution
10. - Cross-thread joins become first-class
11.
12. ### SL (Structural Lens)
13. - SL becomes a **view**, not a pipeline:
14.   - “Show me all *definitions* I’ve accepted”
15.   - “Show contradictions across months”
16.   - “Collapse assistant responses into canonical claims”
17.
18. ---
19.
20. ## 5. Why this beats vector-first approaches (for you)
21.
22. Given how you think, this matters:
23.
24. - Vectors are **derived artifacts**
25. - SQLite is **interpretive ground truth**
26. - You can:
27.   - regenerate embeddings
28.   - change chunking
29.   - change models  
30.   **without invalidating the corpus**
31.
32. This mirrors your CFD philosophy:
33. > *truth → proxy → rollout → compare → revise*
34.
35. Same pattern.
36.
37. ---
38.
39. ## 6. What you can do immediately (concrete next step)
40.
41. **Phase 1 (1–2 hours):**
42. - Ingest `conversations.json`
43. - Populate:
44.   - `threads`
45.   - `turns`
46.   - `turns_fts`
47.
48. No semantics yet. Just clean IR.
49.
50. **Phase 2 (later):**
51. - Add:
52.   - interpretive layers (claims, questions)
53.   - recurrence detection
54.   - contradiction flags
55.
56. **Phase 3 (fun):**
57. - Treat ChatGPT history as:
58.   - a *training trace*
59.   - a *theory evolution log*
60.   - a *self-audit mechanism*
61.
62. ---
63.
64. ## 7. Big picture (this is the key insight)
65.
66. Your ChatGPT history is:
67.
68. > **A compressed record of how you think in dialogue with constraints**
69.
70. Putting it into SQLite under ITIR discipline turns it from:
71. - “logs”
72. into:
73. - **a self-reflective reasoning corpus**
74.
75. If you want next, I can:
76. - sketch the **exact Python ingest script**
77. - design **TIRC recurrence queries**
78. - map **legal / NotebookLM / ChatGPT** into a single ITIR super-corpus
79.
80. Just say where you want to push first.

---

# Conversation: Compression ratio comparison

- ID: 698218f7-9ca4-83a1-969d-0ffc3d6264e4
- Updated (UTC): 2026-02-03T16:11:09.867298Z
- Source: 698218f7-9ca4-83a1-969d-0ffc3d6264e4:1-80

## Latest assistant excerpt (lines 1-80)
1. 4. Deterministic indices:
2.    - atom → list(doc_id, offsets)
3.    - doc_id → stream
4.    - optional: span graph (purely structural)
5. 
6. These are **content-addressed** artifacts. Think “build outputs.”
7. 
8. ### ITIR consumes SL outputs
9. ITIR builds *interpretations* **on top of** those stable atoms:
10. 
11. - “This atom is a *candidate* for ‘jurisdictional error’ pattern”
12. - “This atom often occurs near holdings”
13. - “These atoms cluster into a concept”
14. - “This atom aligns with citation contexts”
15. 
16. But ITIR stores these as **annotations** in a separate namespace, never rewriting SL.
17. 
18. ## The key contract boundary
19. 
20. **ITIR must never:**
21. - change canonicalisation
22. - change phrase promotion thresholds
23. - introduce new atoms into SL’s dictionary
24. - rewrite SL’s streams
25. 
26. Instead, ITIR does:
27. - `interpretation(atom_id) -> distribution over meanings`
28. - `interpretation(span_location) -> candidate role labels`
29. - `graph overlays` (edges between atom_ids, spans, citations)
30. 
31. ## Minimal “overlay” interface
32. 
33. Define an ITIR overlay record like:
34. 
35. - `target`: (`doc_id`, `offset_range`) or `atom_id`
36. - `layer`: string (e.g. `"concepts.v1"`, `"arguments.v1"`)
37. - `label`: string or structured tag
38. - `score`: float
39. - `evidence`: list of deterministic pointers (atom_ids, span ids, citations)
40. - `model_id`: hash/version of the interpretive model
41. 
42. Crucially: evidence points back into SL’s immutable structures.
43. 
44. ## Why phrase atoms help ITIR
45. 
46. They give ITIR:
47. - stable “phrases” without semantic commitment
48. - consistent units for clustering/concept induction
49. - better retrieval keys than raw tokens
50. - interpretive work can be incremental and reversible
51. 
52. And SL stays clean because atoms are:
53. - purely syntactic
54. - content-addressed
55. - reproducible
56. 
57. ---
58. 
59. # Practical starter kit
60. 
61. If you want the *smallest* viable implementation that still respects all this:
62. 
63. 1. Run one-pass promotion for n=2..8, `min_df=2`, `min_cf=5`, `dict_cost=α*n` with α ~ 2–5 in “token units”
64. 2. Emit `phrase_atoms.jsonl` sorted by `atom_id`
65. 3. Rewrite docs with leftmost-longest
66. 4. Expose:
67.    - `atom_id -> expansion`
68.    - `doc_id -> rewritten stream`
69.    - `atom_id -> occurrences`
70. 
71. Then ITIR can immediately start doing:
72. - concept clustering over `atom_id` co-occurrence
73. - argument candidate extraction using atom sequences
74. - citation-context models anchored to atoms
75. 
76. All without changing SL.
77. 
78. ---
79. 
80. If you want, next step I can do in the same spirit is: **pick concrete parameter defaults** (Nmax/min_df/min_cf/α) tailored to your corpus sizes, *and* define a couple of failure modes + guards (e.g., “stopwords/number-heavy spans”, “cross-page artifact spans”, “citation boilerplate flooding”) in deterministic ways.

---

# Conversation: Whisper progress + streaming + project fit (tircorder/ITIR)

## Summary (short)
- `tqdm` is the de facto progress surface for Whisper/WhisperX, but it is not a stable or official API.
- Native, built-in streaming partial segments are not provided by Whisper/WhisperX local APIs; streaming-like behavior is typically simulated by chunking.
- Hosted OpenAI Audio/Realtime endpoints can stream partial text, but this is an API-layer feature, not Whisper’s local Python API.
- For ITIR/tircorder goals, the best spine remains tircorder’s job/session model, with streaming policy logic layered on top (not the other way around).

---

## Whisper (OpenAI) — progress surface
- Progress reporting is an implementation detail.
- Internally uses `tqdm` in decoding/segment loops.
- Visibility depends on CLI vs Python usage and stdout attachment.
- No formal progress callback or observer interface.
- Typical workarounds:
  - wrap your own loops in `tqdm`
  - monkey-patch internal loops

## WhisperX — progress surface
- Also uses `tqdm` for transcription/alignment/diarization.
- No structured progress events or stable API contract.
- Expected by users, not guaranteed as an interface.

## Why `tqdm` is insufficient for ITIR-grade use
- Terminal-only ergonomics.
- No structured metrics for UI integration or headless services.
- No stable phase/ETA instrumentation.

## Common alternatives (non-`tqdm`)
1. Phase timing only (coarse but stable)
2. Segment counting (you compute around Whisper calls)
3. Log scraping (brittle)
4. Fork/patch (best long-term, higher maintenance)

---

## Whisper / WhisperX streaming (local) — bottom line
- No official native method that streams partial segments mid-decode.
- Simulated streaming = manual chunking + sequential processing.

## OpenAI hosted APIs (streaming)
- Streaming via SSE/WebSockets is supported in hosted APIs.
- This is API-layer streaming, not Whisper local decode.

---

## Project fit vs goals (tircorder/ITIR)

### Goals that matter here
- low-latency dispatch
- iterative hypotheses (unstable vs committed text)
- adaptive sentence cutting for run-ons
- audio↔text coupling for UI/artefacts
- client/server separation
- interpretability + provenance

### Best fit spine
- `tircorder-JOBBIE` stays the platform spine.
- Embed policy ideas from:
  - `ufal/whisper_streaming` (LocalAgreement-style commit logic)
  - `ufal/SimulStreaming` (optional research policy reference)

### Recommended replacement path
- For batch/backend: `faster-whisper` is the clean backend swap.
- For streaming behavior: add a streaming policy layer above the backend.
- Keep segmentation as sessionization/throttle, not as the streaming mechanism.

---

## Streaming-first vs segmentation-first (decision framing)

### Streaming-first
- ASR owns rolling buffer + commit policy.
- Tircorder owns session/artefact boundaries.
- Use `whisper_streaming` or `SimulStreaming` as policy layer.

### Segmentation-first
- Tircorder owns slicing/dispatch + job boundaries.
- ASR is stateless worker.
- Use `faster-whisper` as backend; add prefix-commit logic if needed.

---

## Final distilled answer (architectural)
- `tqdm` is canonical-in-practice, not a stable API surface.
- Whisper/WhisperX local APIs do not offer native partial-segment streaming.
- Best system fit remains:
  - `tircorder-JOBBIE` as the spine
  - streaming policy borrowed from `whisper_streaming`
  - optional research references from `SimulStreaming`
# StatiBaker Sprint Plan (2026-02-05)

Short reference: `__CONTEXT/sprints/stati_baker_sprints.md`

Summary:
- Sprint 1 locks SB as a deterministic temporal reducer (guard tests, multi-day replay, no content summarization).
- Sprint 2 introduces external observation (Wazuh lifecycle + Prometheus summaries) without authority leakage.
- Sprint 3 defines integration boundaries (OCR contract, Android status contract, read-only query surface).

Recommended order: Sprint 1 → Sprint 2 → Sprint 3.
Detailed scope, acceptance criteria, and non-goals live in `__CONTEXT/sprints/stati_baker_sprints.md`.

Post–Sprint 1–3 continuation:
- Sprint 4–6 plan in `__CONTEXT/sprints/stati_baker_sprints_4_6.md` (stress/drift, selective Phase-2 compression, read-only surfaces).

Post–Sprint 4–6 continuation:
- Sprint 7–9 plan in `__CONTEXT/sprints/stati_baker_sprints_7_9.md` (portability, time hygiene, red-team boundary lock).
- Sprint 9 scope explicitly includes event injection, command/RCE, credential leakage,
  path traversal, DoS/resource-exhaustion refusal, and blast-radius rules.

OpenClaw integration notes:
- `StatiBaker/docs/openclaw_integration.md` captures execution envelopes and the
  SB/ITIR truth-substrate doctrine for agent tooling.

Multi-modal system doctrine:
- `StatiBaker/docs/multimodal_system_doctrine.md` defines epistemic modes and
  explicit authority boundaries for assistive, intent, scheduling, and ground
  truth layers.
- `SensibLaw/docs/multimodal_system_doctrine.md` mirrors the doctrine for SL/ITIR.
