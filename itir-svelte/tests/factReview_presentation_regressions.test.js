import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';

const ROOT = new URL('..', import.meta.url);

function read(rel) {
  return readFileSync(join(ROOT.pathname, rel), 'utf8');
}

test('fact review route surfaces operator-facing provenance and abstention cues without changing backend ownership', () => {
  const page = read('src/routes/graphs/fact-review/+page.svelte');
  const server = read('src/lib/server/factReview.ts');

  assert.ok(page.includes('Read-only operator review over persisted evidence. Provenance-first, no reasoning overlay.'));
  assert.ok(page.includes('Abstained / bounded context:'));
  assert.ok(page.includes('Operator constraints:'));
  assert.ok(page.includes('bounded-context material'));
  assert.ok(page.includes('Mary operator'));
  assert.ok(page.includes('ITIR operator'));
  assert.ok(page.includes('These story cards are operator-facing acceptance cues only.'));
  assert.ok(page.includes('Control-plane summary'));
  assert.ok(server.includes('policy_outcomes?: string[];'));
});
