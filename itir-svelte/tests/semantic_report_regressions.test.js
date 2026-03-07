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

test('semantic report server exposes comparison and graph gate payloads', () => {
  const s = read('src/routes/graphs/semantic-report/+page.server.ts');
  assert.ok(s.includes('loadSemanticComparison'));
  assert.ok(s.includes('graphGate'));
  assert.ok(s.includes('semanticGraph'));
});
