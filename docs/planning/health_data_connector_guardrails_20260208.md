# Health Data Connector Guardrails (2026-02-08)

## Purpose
Define mandatory guardrails for connectors that ingest personal health data
into the ITIR/TiRCorder/SensibLaw workspace, including:
- medical scans (DICOM and scan exports)
- clinician notes and visit summaries (text/PDF exports)
- EHR exports in FHIR (Bundle/NDJSON)

This is a contract/policy document for implementation work.

## Scope
- TiRCorder connector implementations under `tircorder-JOBBIE/integrations/medical/`.
- Any downstream ingestion that promotes observer-class health artifacts into
  more authoritative lanes.

## Non-negotiable rules
1. Local-first and explicit consent.
- Default posture is offline/local import from user-provided files.
- If remote APIs are added (SMART on FHIR, MyChart, etc.), they must require
  explicit opt-in and must record the exact scopes/authorizations used.

2. Meta-only by default.
- Connector defaults must avoid ingesting full PHI content (free-text notes,
  base64 attachments, images/pixels).
- Connectors may emit references (hashes, file metadata) plus minimal clinical
  metadata required for timeline anchoring.

3. No silent inference.
- Connectors must not infer diagnosis, intent, prognosis, “meaning”, or any
  semantic labels.
- Connector output is observation metadata only; interpretation belongs in
  higher layers with explicit receipts.

4. Identity minimization.
- Do not emit real names, MRNs, addresses, phone numbers, or emails into
  story-event payloads by default.
- Prefer hashed identifiers at the connector boundary when a stable link is
  required.

5. Attachment handling.
- Never store FHIR `attachment.data` (base64) by default.
- For scans/notes, prefer `sha256` + file size + content-type + filename.

6. Promotion gating.
- Any transition from observer/projection health artifacts into canonical or
  “compiled” lanes must require explicit promotion receipts.

## Handwritten Notes and OCR (Policy)
Handwritten medical notes and scanned forms are common. The system must treat
OCR output as a *transcription hypothesis*, not ground truth.

1. Source-of-truth is the artifact.
- The image/PDF is the authoritative capture artifact.
- OCR text (local or remote) must never overwrite or replace the artifact.

2. Local OCR is allowed as a baseline.
- Local OCR may be attempted for searchability and rough triage.
- Expect poor results on messy handwriting; treat low-confidence spans as
  `ocr_uncertain`-class signals where applicable (see `SensibLaw/docs/span_signal_hypotheses.md`).

3. Frontier OCR may be better, but it is a different risk class.
- Frontier multimodal models (e.g., ChatGPT-class) often outperform local OCR
  on messy handwriting because they can use context clues.
- This path is optional and must be explicit opt-in for the user and incident,
  because it typically involves sending images off-device.
- Remote OCR output must be recorded as an observer artifact with provenance:
  model/provider, input hash, timestamps, and any prompts/parameters used.

4. Minimum-necessary disclosure still applies.
- Prefer cropping/redacting identifiers before any remote OCR.
- Never send full bundles when a single page or region suffices.
- Do not upload base64 blobs or full exports by default.

## Connector output contract (current)
The near-term integration surface for health connectors is TiRCorder’s story
event schema (validated by `tircorder-JOBBIE/tircorder/schemas/story.schema.yaml`):

Required keys:
- `event_id` (stable/deterministic where possible)
- `timestamp` (ISO-8601 date-time)
- `actor` (string label)
- `action` (string label)
- `details` (object)

Health connectors must keep `details` non-semantic and minimised by default.

## Implementation checklist
- Deterministic `event_id` for file-backed items using content hash.
- `details.sha256`, `details.file_size_bytes`, `details.filename` where applicable.
- Timestamp derived from resource metadata when present, else explicit
  `collected_at` parameter (do not rely solely on filesystem mtime).
- Red-team tests: ensure no `name`, `address`, `email`, `phone`, `mrn`, or
  base64 attachments leak by default from common FHIR resource shapes.

## Open decisions
- Where full-text doctor-note content should live (TiRCorder observer vs
  SensibLaw document store) and under which receipts.
- Whether to support a first-class "remote OCR" toolchain and, if so, the
  required consent receipt + redaction workflow.
- Default encryption-at-rest posture for locally stored health artifacts.
- Salt/key management for hashed identifiers (per-user salts vs workspace salts).
