import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';

const source = readFileSync(
  new URL('../src/lib/workbench/ReadingSurface.svelte', import.meta.url),
  'utf8',
);

test('context drawer consumes the pure context inspection projection', () => {
  assert.match(source, /projectContextInspection/);
  assert.match(source, /contextInspection\.wikidataQid/);
  assert.match(source, /contextInspection\.wikipediaRef/);
  assert.match(source, /contextInspection\.exactSourceRef/);
});

test('context drawer labels navigation separately from exact source', () => {
  assert.match(source, /Wikidata identity/);
  assert.match(source, /Wikipedia context/);
  assert.match(source, /Exact source/);
  assert.match(source, /does not create legal authority or applicability/);
});
