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
