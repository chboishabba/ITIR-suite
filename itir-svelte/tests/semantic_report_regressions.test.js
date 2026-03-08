import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';

const ROOT = new URL('..', import.meta.url);

function read(rel) {
  return readFileSync(join(ROOT.pathname, rel), 'utf8');
}

test('semantic report page renders split + delta comparison section', () => {
  const s = read('src/routes/graphs/semantic-report/+page.svelte');
  assert.ok(s.includes('Split + delta comparison'));
  assert.ok(s.includes('hca minus gwb deltas'));
  assert.ok(s.includes('predicateDelta'));
});

test('semantic report page includes gated AU graph lane copy', () => {
  const s = read('src/routes/graphs/semantic-report/+page.svelte');
  assert.ok(s.includes('AU semantic graph lane'));
  assert.ok(s.includes('Graph lane is waiting for richer AU coverage'));
  assert.ok(s.includes('<LayeredGraph'));
});

test('semantic report page includes token arc inspector workbench', () => {
  const s = read('src/routes/graphs/semantic-report/+page.svelte');
  assert.ok(s.includes('TokenArcInspector'));
  assert.ok(s.includes('DocumentViewer'));
  assert.ok(s.includes('tokenArcDebug'));
  assert.ok(s.includes('sourceDocumentsById'));
  assert.ok(s.includes('sourceViewerHighlights'));
  assert.ok(s.includes('Active Anchor Quality'));
  assert.ok(s.includes('provenanceBadgeTone'));
  assert.ok(s.includes('Compact review summary'));
  assert.ok(s.includes('Top cue surfaces'));
  assert.ok(s.includes('Source document'));
  assert.ok(s.includes('No source document payload is available for this corpus/event yet.'));
  assert.ok(s.includes('Review submission'));
  assert.ok(s.includes('Recent corrections'));
  assert.ok(s.includes('Mission observer'));
  assert.ok(s.includes('Download mission observer JSON'));
  assert.ok(s.includes('pickHighlightForRange'));
  assert.ok(s.includes('requestSelectionFromHighlight'));
});

test('semantic report server exposes comparison and graph gate payloads', () => {
  const s = read('src/routes/graphs/semantic-report/+page.server.ts');
  assert.ok(s.includes('loadSemanticComparison'));
  assert.ok(s.includes('graphGate'));
  assert.ok(s.includes('semanticGraph'));
  assert.ok(s.includes('tokenArcDebug'));
  assert.ok(s.includes('submitCorrection'));
  assert.ok(s.includes('semantic_review_admin.py'));
});

test('semantic report loader includes transcript as a reusable non-legal producer', () => {
  const s = read('src/lib/server/semanticReport.ts');
  assert.ok(s.includes("key: 'transcript'"));
  assert.ok(s.includes('Transcript / freeform'));
  assert.ok(s.includes("scripts', 'transcript_semantic.py"));
});

test('semantic report loader consumes producer-owned text_debug payloads', () => {
  const s = read('src/lib/server/semanticReport.ts');
  assert.ok(s.includes('report.text_debug ??'));
  assert.ok(s.includes('source_documents?:'));
  assert.ok(s.includes('review_summary?:'));
  assert.ok(s.includes('mission_observer?:'));
  assert.ok(!s.includes('function tokenizeEventText'));
});

test('token arc inspector consumes the shared text-debug contract', () => {
  const s = read('src/lib/semantic/TokenArcInspector.svelte');
  assert.ok(s.includes("$lib/semantic/textDebug"));
  assert.ok(s.includes('TextDebugEvent'));
  assert.ok(s.includes('TextDebugAnchor'));
  assert.ok(s.includes('selectedEventChange'));
  assert.ok(s.includes('activeSelectionChange'));
  assert.ok(s.includes('selectionRequest'));
});

test('shared text-debug contract defines generic anchor provenance', () => {
  const s = read('src/lib/semantic/textDebug.ts');
  assert.ok(s.includes("export type TextDebugAnchorSource = 'mention' | 'receipt' | 'label_fallback'"));
  assert.ok(s.includes('export type TextDebugPayload'));
  assert.ok(s.includes('sourceDocumentId?: string | null;'));
  assert.ok(s.includes('export type TextDebugSourceDocument'));
  assert.ok(s.includes('charStart: number;'));
  assert.ok(s.includes('sourceArtifactId: string;'));
});

test('token arc inspector documents hover arc semantics', () => {
  const s = read('src/lib/semantic/TokenArcInspector.svelte');
  assert.ok(s.includes('Token arc debugger'));
  assert.ok(s.includes('Hover a token anchor to draw relation arcs'));
  assert.ok(s.includes('opacity tracks confidence'));
  assert.ok(s.includes('Clear pin'));
  assert.ok(s.includes('Pinned relations'));
  assert.ok(s.includes("anchor.source"));
  assert.ok(s.includes('sourceArtifactId'));
  assert.ok(s.includes('charStart'));
  assert.ok(s.includes('echoTokenStyles'));
  assert.ok(s.includes('Matching same-role anchors in the same family'));
  assert.ok(s.includes('Pin relation'));
  assert.ok(s.includes('relationProvenanceSummary'));
  assert.ok(s.includes('mention-backed'));
  assert.ok(s.includes('fallback-anchored'));
});

test('document viewer supports external semantic highlight spans', () => {
  const s = read('src/lib/viewers/DocumentViewer.svelte');
  assert.ok(s.includes('export let highlights'));
  assert.ok(s.includes('selectedHighlightKey'));
  assert.ok(s.includes("type DocumentHighlightSource = 'mention' | 'receipt' | 'label_fallback' | 'event_span'"));
  assert.ok(s.includes("background-image: linear-gradient(135deg"));
  assert.ok(s.includes('highlightHtml(row.line, query, offsets[row.idx] ?? 0)'));
});
