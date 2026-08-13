# Canonical Text And Span Evidence Contract

Date: 2026-04-07

## Purpose

Record the minimal document-evidence substrate required for compliance,
standards, legal, and audit lanes that need replayable and challengeable
evidence.

This note does not introduce a new parser family or replace current retrieval
infrastructure. It defines the normalized evidence shape that document-like
retrieval must resolve to before it can support control evaluation, receipts,
or promoted review work.

## Core Doctrine

Retrieval may help find evidence.

It is not the source of truth.

The canonical evidence path for document-like material is:

```text
raw document
  -> canonical text
  -> text revision
  -> chunk span
  -> retrieval/index references
  -> evidence resolution
  -> evaluation / promotion / receipt
```

This means:

- raw documents remain retained
- canonical text remains retained
- chunks are derived from canonical text
- evidence references resolve to exact revision and exact span
- vector stores and similar indices are lookup helpers, not authority surfaces

## Why This Is Required

`vector + file path` is not enough for the repo's current doctrine.

It can help retrieve similar text, but it does not by itself guarantee:

- exact evidence reconstruction
- deterministic replay
- stable citations against a canonical revision
- auditable control evaluation
- challengeable receipts

The repo's provenance-first and admissibility rules already require stronger
traceability than that.

## Minimal Normalized Shape

Document-like evidence should normalize around:

- `document_id`
  - stable canonical document identity
- `text_revision_id`
  - stable identity for the canonicalized full text revision
- `chunk_id`
  - deterministic identity for a derived span within that revision
- `start_offset`
- `end_offset`
- optional:
  - `section_ref`
  - `line_map`
  - `source_artifact_ref`

Recommended deterministic rules:

- `text_revision_id = hash(canonical_text)`
- `chunk_id = hash(text_revision_id || start_offset || end_offset)`

These rules are intentionally simple. They are meant to support replay,
re-chunk detection, and audit traceability without forcing a large pipeline
rewrite.

## Resolution Rule

Chunk text should be treated as a projection, not a canonical stored fact.

The authoritative reconstruction path is:

```text
chunk_id
  -> text_revision_id
  -> canonical_text
  -> canonical_text[start_offset:end_offset]
```

If a retrieval/import path cannot resolve a claimed chunk back to a canonical
revision and span, it should remain unresolved rather than silently promoted
into a stronger evidence posture.

## Compliance Tie-In

This matters because the compliance/control lanes are not "RAG answer" lanes.
They are evidence, evaluation, justification, verification, and receipt lanes.

For standards or compliance evaluation, the evidence form needs to be closer
to:

```text
(document_id, text_revision_id, span)
```

than:

```text
retrieved chunk text + file path
```

Otherwise the suite cannot reliably:

- prove which exact source slice supported a control outcome
- re-run the same evaluation deterministically
- emit auditable receipts with exact evidence references
- defend the result under review or challenge

## Relationship To Existing Lanes

This note is compatible with the current bounded ISO and standards lanes:

- keep ISO and similar standards work on the shared parser spine
- keep retrieval/index infrastructure as helper substrate
- require canonical revision/span resolution before stronger compliance or
  promotion claims

It is also compatible with the managed-host compliance planning lanes:

- host-state evidence may use non-document anchors where appropriate
- document-like evidence and standards excerpts should still resolve through
  canonical revision/span references
- action planning and receipts should cite exact evidence refs rather than
  approximate retrieval blobs

## Governance

- ITIL:
  - change control and verification require exact evidence references
- ISO 9000:
  - traceable inputs, explicit nonconformance, reproducible acceptance
- ISO 42001 / NIST AI RMF:
  - intended use, oversight, and auditability depend on challengeable evidence
- ISO 27001 / ISO 27701:
  - keep authority and exposure bounded; minimize unnecessary duplication
- ISO 23894:
  - reduce residual risk from opaque retrieval and untraceable evidence drift
- Six Sigma:
  - treat unresolved span mapping as a defect class, not an acceptable silent
    fallback

## Not In Scope

- replacing current vector stores
- broad standards-catalog ingestion
- a new top-level standards ontology
- promoting retrieval results directly to truth-bearing state
