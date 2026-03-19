# itir-svelte Transcript Browser Parity Pass (2026-03-19)

## Intent

Record the migration-oriented parity status between the retained legacy
transcript-browser behavior in `tircorder-JOBBIE/Pelican/` and the current
`itir-svelte/` implementation.

This is not a request to keep investing in Pelican or Zola. It is a bounded
check that developers are porting the right behavior into `itir-svelte/` and
not spending effort on legacy web stacks.

## Compared surfaces

- Legacy reference:
  - `tircorder-JOBBIE/docs/transcript_browser_pipeline.md`
  - `tircorder-JOBBIE/Pelican/generate_html_timeline_item.py`
  - `tircorder-JOBBIE/Pelican/scripts.js`
- Current Svelte implementation:
  - `itir-svelte/src/lib/viewers/TranscriptViewer.svelte`
  - `itir-svelte/src/lib/viewers/transcript.ts`
  - `itir-svelte/src/lib/viewers/DocumentViewer.svelte`
  - `itir-svelte/src/routes/viewers/hca-case/+page.svelte`
  - `itir-svelte/src/routes/viewers/hca-case/+page.server.ts`

## Parity summary

### Already covered in `itir-svelte`

- Deterministic transcript cue parsing
  - legacy: SRT-like line parsing in `Pelican/scripts.js`
  - current: shared parser utilities in `src/lib/viewers/transcript.ts`
- Cue activation and seek behavior
  - legacy: click cue -> seek audio
  - current: `TranscriptViewer` click/select -> `audio.currentTime`
- Active cue highlighting
  - legacy: highlighted current line + cue-button rendering
  - current: active cue row styling with scroll-into-view
- Transcript search/filtering
  - current-only improvement in `TranscriptViewer`
- Transcript + document split inspection
  - current: `/viewers/hca-case` already provides the stronger migration target
    compared with the legacy single-column HTML timeline

### Closed in this pass

- Accessibility live-status parity
  - legacy behavior mirrored the current cue into a live region during
    playback/highlight refresh
  - `TranscriptViewer` now exposes a polite `aria-live` cue-status region so
    assistive tech has the same class of current-cue signal

### Still not treated as parity targets

- Pelican timeline-item list shell, dangling-audio/transcript page assembly,
  and old static-site wrappers
- Zola placeholder site structure
- 3D timeline enhancer bootstrap

These remain legacy/reference-only unless there is a specific reason to port
one behavior into `itir-svelte/`.

## Migration rule

If a developer finds a useful behavior in Pelican/Zola:

1. restate the behavior as an `itir-svelte` UI contract or TODO
2. implement it in `itir-svelte`
3. keep only bounded reference/regression coverage on the legacy side

Do not extend Pelican/Zola to chase parity directly.

## Next reasonable transcript-viewer followthrough

- wire `TranscriptViewer` into more real thread/event surfaces when transcript
  artifacts are present
- add a shared cue/selection sync store when graph/document/transcript
  synchronization becomes active across multiple routes
- decide whether any legacy “timeline of matched audio + transcript artifacts”
  behavior is still product-relevant enough to deserve a dedicated
  `itir-svelte` route
