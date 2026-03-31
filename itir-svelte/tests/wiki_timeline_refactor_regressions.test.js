import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';

const ROOT = new URL('..', import.meta.url);

function read(rel) {
  return readFileSync(join(ROOT.pathname, rel), 'utf8');
}

test('wikiTimeline centralizes source registry and DB source loader', () => {
  const server = read('src/lib/server/wikiTimeline.ts');
  assert.ok(server.includes('export function normalizeWikiTimelineSourceKey'));
  assert.ok(server.includes('export async function loadWikiTimelineSourceDb'));
  assert.ok(server.includes("'--source-key'"));
  assert.ok(server.includes("'--with-source-meta'"));
  assert.ok(server.includes("'timeline_view'"));
  assert.ok(!server.includes('outEvents.sort('));
  assert.ok(!server.includes('event_id = String('));
});

test('wiki-timeline route server delegates source resolution to shared loader', () => {
  const route = read('src/routes/graphs/wiki-timeline/+page.server.ts');
  assert.ok(route.includes("from '$lib/server/wikiTimeline'"));
  assert.ok(route.includes('loadWikiTimelineSourceDb'));
  assert.ok(route.includes('normalizeWikiTimelineSourceKey'));
  assert.ok(!route.includes('const SOURCE_PATHS = {'));
  assert.ok(!route.includes('const TIMELINE_SUFFIX = {'));
});

test('wiki fact timeline route uses Python source meta instead of local source maps', () => {
  const route = read('src/routes/graphs/wiki-fact-timeline/+page.server.ts');
  assert.ok(route.includes('normalizeWikiTimelineSourceKey'));
  assert.ok(route.includes("'--source-key'"));
  assert.ok(route.includes("'--with-source-meta'"));
  assert.ok(!route.includes('const SOURCE_PATHS = {'));
  assert.ok(!route.includes('HCA_REL'));
});

test('graph.ts re-exports numeric helpers from dedicated numeric module', () => {
  const graph = read('src/lib/wiki_timeline/graph.ts');
  const numeric = read('src/lib/wiki_timeline/numeric.ts');
  assert.ok(graph.includes("from './numeric'"));
  assert.ok(graph.includes('numericMentionsForEvent'));
  assert.ok(numeric.includes('export function normalizeNumericMention'));
  assert.ok(numeric.includes('export function numericKey'));
  assert.ok(numeric.includes('export function compareNumericLaneEntries'));
  assert.ok(numeric.includes('projectedNumericMentions'));
  assert.ok(numeric.includes('numeric_mentions'));
});

test('wiki fact timeline server delegates projection/coalescing to dedicated helper', () => {
  const server = read('src/routes/graphs/wiki-fact-timeline/+page.server.ts');
  const projection = read('src/routes/graphs/wiki-fact-timeline/projection.ts');
  assert.ok(server.includes('runPythonJson'));
  assert.ok(server.includes("'fact_timeline'"));
  assert.ok(!server.includes("from './projection'"));
  assert.ok(!server.includes('function coalesceFactRows('));
  assert.ok(projection.includes('fact_row_source'));
  assert.ok(projection.includes('coalesceFactRows'));
});
