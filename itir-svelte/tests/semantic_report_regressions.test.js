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
  assert.ok(s.includes('tokenArcDebug'));
});

test('semantic report server exposes comparison and graph gate payloads', () => {
  const s = read('src/routes/graphs/semantic-report/+page.server.ts');
  assert.ok(s.includes('loadSemanticComparison'));
  assert.ok(s.includes('graphGate'));
  assert.ok(s.includes('semanticGraph'));
  assert.ok(s.includes('tokenArcDebug'));
});

test('semantic report loader includes transcript as a reusable non-legal producer', () => {
  const s = read('src/lib/server/semanticReport.ts');
  assert.ok(s.includes("key: 'transcript'"));
  assert.ok(s.includes('Transcript / freeform'));
  assert.ok(s.includes("scripts', 'transcript_semantic.py"));
});

test('token arc inspector consumes the shared text-debug contract', () => {
  const s = read('src/lib/semantic/TokenArcInspector.svelte');
  assert.ok(s.includes("$lib/semantic/textDebug"));
  assert.ok(s.includes('TextDebugEvent'));
  assert.ok(s.includes('TextDebugAnchor'));
});

test('shared text-debug contract defines generic anchor provenance', () => {
  const s = read('src/lib/semantic/textDebug.ts');
  assert.ok(s.includes("export type TextDebugAnchorSource = 'mention' | 'receipt' | 'label_fallback'"));
  assert.ok(s.includes('export type TextDebugPayload'));
});

test('token arc inspector documents hover arc semantics', () => {
  const s = read('src/lib/semantic/TokenArcInspector.svelte');
  assert.ok(s.includes('Token arc debugger'));
  assert.ok(s.includes('Hover a token anchor to draw relation arcs'));
  assert.ok(s.includes('opacity tracks confidence'));
  assert.ok(s.includes('Clear pin'));
  assert.ok(s.includes('Pinned relations'));
  assert.ok(s.includes("anchor.source"));
});
