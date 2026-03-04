# HCA Case `S94/2025` Ingest Follow-ups (2026-02-11)

## Scope
Operational follow-ups for `SensibLaw/scripts/hca_case_demo_ingest.py` and demo outputs in `SensibLaw/demo/ingest/hca_case_s942025/`.

## Completed
- [x] Added case-page document-link scoring so `Judgment (Judgment Summary)` prefers the summary PDF URL over judgment HTML.
- [x] Added transcript fallback extraction from AV recording page (`field-av-transcripts`) and persisted transcript HTML/TXT artifacts.
- [x] Added Vimeo fallback path (`/config/request` scraped from player HTML) when `/config` is forbidden.
- [x] Added HLS/DASH manifest capture under `media/video/` when progressive MP4 is unavailable.
- [x] Confirmed caption extraction with timestamps (`en-x-autogen` VTT + markdown + segments JSON).
- [x] Added explicit parse-lane contract docs for HCA AAO output:
  `artifact_status` vs `narrative_sentence` with non-authoritative SB observer handoff guidance.
- [x] Replaced regex-heavy narrative sentence gates with deterministic parser-first checks (spaCy token/POS features) and kept regex only as fallback hygiene.
- [x] Added deterministic citation extraction on narrative events (`citations[]`) and citation follower hints (Wikipedia-first, then `wiki_connector`, then local source document/PDF).

## Open TODO
- [ ] Surface HCA narrative parser metadata (`model`, `version`, fallback reason/hash) in Svelte UI context panel for reproducibility receipts.
- [ ] Add source-row IDs to document table rows so narrative events can join directly to the originating row without filename heuristics.
- [ ] Add per-source lane filtering in Svelte HCA views (`artifact_status` only, `narrative_sentence` only, combined).
- [ ] Add optional dedupe/cluster pass for near-identical narrative sentences across appellant/respondent PDFs.
- [ ] Add optional ffmpeg handoff helper that converts captured HLS/DASH manifests into an MP4 output when local tooling is available.
- [ ] Add a flag to choose manifest capture only vs full media pulls for faster re-runs.
- [ ] Add stricter HTML-to-text transcript extraction for AustLII pages (content-body selection to reduce navigation noise).
- [ ] Add a regression fixture for multi-link document rows to prevent future summary-link regressions.
- [ ] Investigate whether `Notice of appeal` can be discovered from a secondary page or API when absent from the documents table.
- [x] Integrate SL-native references into narrative events (`sl_references[]`) by joining each narrative event to the originating `*.document.json` parse output.
- [x] Expose `sl_references[]` in SB observer payload alongside `citations[]` with provenance (`source_document_json`, `provision_stable_id`/`rule_atom_stable_id`).
- [ ] Add stronger sentence->provision alignment (span-index join) to reduce broad matches when OCR/provision segmentation is noisy.

## Gap check: where we are vs where we want to be

### Current (implemented)
- Narrative events are extracted through the AAO adapter lane and tagged `signal_class=narrative_sentence`.
- Parser-first sentence filtering is in place (spaCy token/POS/dependency features), with regex reserved for fallback hygiene.
- Adapter emits deterministic `citations[]` plus ordered follower hints (`wikipedia -> wiki_connector -> source_document -> source_pdf`).
- Adapter emits parser-native `sl_references[]` from `provisions[].references`, `rule_tokens.references`, and `rule_atoms[*]` reference lanes, with provenance (`source_document_json`, `provision_stable_id`, `rule_atom_stable_id`).
- `SensibLaw/demo/ingest/hca_case_s942025/sb_signals.json` carries both `citations[]` and `sl_references[]` as separate observer lanes.
- Adapter output remains explicitly non-authoritative and reversible for SB observer use.

### Target (not yet implemented)
- Reference extraction resolves citation anchors to sentence-precise parser spans (not just provision text overlap) where available.
- Svelte context view surfaces both `citations[]` and `sl_references[]` with provenance and source row links.

### Delta (implementation sequence)
1. Add source-row IDs so event->artifact join is explicit in both payload and UI.
2. Improve SL reference scoring with sentence-span joins when parser emits sentence offsets.
3. Add UI rendering and filters for `citations[]` vs `sl_references[]`.
4. Keep regression fixture green for both lanes.

### Acceptance criteria
- At least one known narrative event (for example the current `ev:0062` class) shows non-empty `sl_references[]`.
- Every emitted `sl_references[]` entry contains provenance back to source parse artifact.
- Running ingest twice on same inputs yields byte-identical `sl_references[]` ordering/content.
- SB payload includes both hint (`citations[]`) and structured (`sl_references[]`) lanes without changing existing event IDs.

## Runtime constraints observed
- `dot` binary was unavailable in this runtime; DOT output is produced, SVG render is skipped with `dot_not_found`.
- Vimeo `/config` returned 403 consistently for this case recording; `/config/request` path succeeded.
- Sentence-level narrative parsing depends on extracted PDF text quality; malformed OCR/layout noise can still produce weak AAO steps and should remain review-tagged.
