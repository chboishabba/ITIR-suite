# OpenRecall Observer Integration v1

Date: 2026-03-09
Status: importer slice and query/read-model slice implemented

## Intent
Integrate the vendored `openrecall/` project into ITIR as an upstream
observer/capture lane, not as a semantic authority and not as a direct writer
into SB state.

The goal is to make OpenRecall captures reusable across the suite in the same
way stronger pipelines already are:
- deterministic producer-owned imports
- explicit provenance
- additive read models
- reuse by downstream review/extraction lanes without hidden promotion

This is primarily a functional/cross-pipeline standardization task, not a GUI
task.

## Current repo reality
- `openrecall/` is vendored locally.
- Its primary persisted surface is a local SQLite DB of OCR/search entries with
  minimal fields such as `app`, `title`, `text`, `timestamp`, and `embedding`.
- That is useful as raw capture substrate, but insufficient as a direct suite
  authority surface.
- The current vendored capture code looks internally inconsistent, so importer-
  first is safer than treating live capture as stable suite infrastructure.

## Chosen posture
OpenRecall should enter ITIR/SensibLaw as:
- local-first
- observer-only at ingest
- append-only / provenance-linked
- reviewable before stronger semantic or planning use

It should *not* initially be:
- a canonical semantic store
- a direct mission/state authority
- a direct SB writer
- a hidden memory substrate that silently upgrades noisy OCR into truth

## Implemented first slice

The bounded v1 seam now exists:
- `SensibLaw/scripts/import_openrecall.py` imports OpenRecall `entries` rows
  into normalized ITIR-owned tables in `itir.sqlite`
- imported captures are stored as append-only observer rows plus text units and
  refs
- `mission_lens.py` now includes imported captures as a new
  `openrecall_capture` actual-side activity kind
- `structure_report.py` now exposes `load_openrecall_units(...)` so imported
  OCR text can feed the existing transcript/freeform semantic lane as
  source-local text

This remains explicitly non-authoritative on ingest.

## Initial integration shape

### 1. Dedicated importer
Add a bounded importer from the OpenRecall SQLite DB into `itir.sqlite`.

The importer should normalize OpenRecall rows into explicit ITIR-owned capture
surfaces such as:
- import run
- capture source
- capture text unit
- capture reference / screenshot reference

Expected normalized fields:
- `capture_id`
- `captured_at`
- `app_name`
- `window_title`
- `ocr_text`
- `source_db_path`
- `screenshot_path`
- `screenshot_hash` when available
- optional embedding reference or external pointer

Import should be idempotent by stable capture key.

### 2. Reuse in existing lanes
Once imported, OpenRecall captures should feed existing suite lanes rather than
inventing a parallel semantic path.

Primary reuse targets:
- mission lens `actual` side as a new activity/capture source
- transcript/freeform semantic extraction as source-local text units
- later retrieval/review surfaces for “where did I see this?” flows

### 3. Authority separation
OpenRecall-derived rows remain observer-class on ingest.

That means:
- OCR text may support mission/topic review
- OCR text may support semantic/narrative extraction
- OCR text does not by itself become canonical mission truth
- OCR text does not silently rewrite SB state

Promotion, mapping, and stronger downstream use must remain explicit and
receipt-bearing.

## Near-term user stories

### Actual-side activity evidence
As a user, I want OpenRecall captures to appear as actual-side activity evidence
so that mission-lens review can account for screen-local work that was not
captured in shell/chat/git traces.

Acceptance direction:
- imported captures are queryable by time, app, and title
- mission lens can show them as unmapped/reviewable activity rows
- reviewed mapping remains explicit

### Source-local text reuse
As a user, I want OCR text from OpenRecall to be available to existing semantic
and narrative pipelines so that screen-local evidence can participate in
reviewable extraction without being treated as canonical truth.

Acceptance direction:
- imported OCR text can be turned into source-local text units
- downstream extraction remains additive and abstention-friendly
- provenance stays attached to capture source and timestamp

## Functional standardization target
The important standard for this lane is not immediate UI integration.

The important standard is convergence with the suite’s stronger pipelines:
- dedicated storage ownership
- deterministic import contract
- queryable/read-model surfaces
- explicit observer/authority boundary
- reusable downstream artifacts

That standard should be reached before any expectation of rich GUI integration.

This is now also the immediate standard for NotebookLM metadata:
- producer-owned read models first
- source-local text reuse first
- no waterfall/timeline parity claims until capture fidelity improves

### Embedding policy

- OpenRecall semantic-search behavior should not block capture on external
  embedding dependency availability.
- The default path is dependency-aware:
  - transformer-backed `sentence-transformers` when available
  - local deterministic fallback when it is unavailable or disabled via
    deployment policy
- Treat retrieval quality differences as an explicit deployment choice rather than
  a hard import-time requirement.

## Deferred
- live capture stabilization inside vendored OpenRecall
- direct GUI/workbench route for OpenRecall-specific browsing
- autonomous mission/topic backpropagation from OCR alone
- direct SB import of raw OpenRecall rows
- embedding-native cross-source retrieval as authority logic

## Initial milestone
**OpenRecall Observer Integration v1** is now implemented in bounded form.

Delivered:
- DB-backed importer into `itir.sqlite`
- normalized capture tables/read models
- mission-lens actual-side reuse as a new source kind
- source-local text reuse for semantic/transcript lanes

Still deferred:
- GUI-first OpenRecall browser
- canonical semantic/state promotion
- implicit memory authority
- live capture stabilization in vendored OpenRecall itself

## Query/read-model followthrough
The next functional standardization slice is now also in place.

Delivered in this followthrough:
- query-first helpers over imported captures
- a small CLI/read-model surface:
  - latest import runs
  - capture counts by app/title/date
  - screenshot coverage
  - recent capture rows with bounded filters
- a stable seam other pipelines can call without reopening raw tables

Implemented shape:
- helper/query functions in the neutral OpenRecall import module
- `SensibLaw/scripts/query_openrecall_import.py`
- mission-lens and later consumers can read the same normalized summaries
  rather than inventing local capture queries

## Current external-consumer alignment (2026-04-07)

OpenRecall now has an ITIR-facing MCP bridge for bounded comparison/policy
normalization and safe adapter-style invocation, shipped as the closed-loop
integration work in:

- https://github.com/openrecall/openrecall/pull/126

This keeps OpenRecall's role as a bounded acquisition and evidence source while
moving cross-source comparison and policy-constrained scoring through the suite
MCP path.
