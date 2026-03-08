import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';

const ROOT = new URL('..', import.meta.url);

function read(rel) {
  return readFileSync(join(ROOT.pathname, rel), 'utf8');
}

test('GraphViewport wires pointer handlers via Svelte events (capture)', () => {
  const s = read('src/lib/ui/GraphViewport.svelte');
  assert.ok(s.includes('on:pointerdown|capture={onPointerDown}'));
  assert.ok(s.includes('on:pointermove|capture={onPointerMove}'));
  assert.ok(s.includes('on:pointerup|capture={onPointerUp}'));
});

test('GraphViewport does not capture pointer until pan threshold is exceeded', () => {
  const s = read('src/lib/ui/GraphViewport.svelte');
  assert.ok(s.includes('Math.hypot'));
  assert.ok(s.includes('if (!panning)'));
  assert.ok(s.includes('setPointerCapture'));
});

test('AAO view does not reset viewport on selection changes', () => {
  const s = read('src/routes/graphs/wiki-timeline-aoo/+page.svelte');
  // Regression guard: the key should not be derived from selected.event_id.
  assert.ok(!s.includes('`${selected.event_id}`'));
  assert.ok(s.includes('graphViewportKey'));
});

test('AAO server supports gwb_corpus_v1', () => {
  const s = read('src/routes/graphs/wiki-timeline-aoo/+page.server.ts');
  assert.ok(s.includes('gwb_corpus_v1'));
  assert.ok(s.includes('wiki_timeline_gwb_corpus_v1_aoo.json'));
});

test('AAO-all server uses canonical HCA AAO suffix instead of thin narrative timeline', () => {
  const s = read('src/routes/graphs/wiki-timeline-aoo-all/+page.server.ts');
  assert.ok(s.includes("SensibLaw', '.cache_local', 'wiki_timeline_hca_s942025_aoo.json"));
  assert.ok(!s.includes('hca_case_narrative.timeline.json'));
});

test('wikiTimelineAoo overlays richer HCA AAO events onto DB-backed metadata when needed', () => {
  const s = read('src/lib/server/wikiTimelineAoo.ts');
  assert.ok(s.includes('maybeOverlayHcaPayload'));
  assert.ok(s.includes('needsHcaEventOverlay'));
  assert.ok(s.includes('wiki_timeline_hca_s942025_aoo.json'));
});

test('chat archive path resolver falls back to non-dot chat archive path', () => {
  const s = read('src/lib/server/chatArchive.ts');
  assert.ok(s.includes('ITIR_CHAT_ARCHIVE_DB_PATH'));
  assert.ok(s.includes('CHAT_ARCHIVE_DB_PATH'));
  assert.ok(s.includes("'.chat_archive.sqlite'"));
  assert.ok(s.includes("'chat_archive.sqlite'"));
});

test('LayeredGraph keeps dashed Source/Lens line style but gates it for performance', () => {
  const s = read('src/lib/ui/LayeredGraph.svelte');
  // Pretty but expensive dashed strokes: keep the signature styles.
  assert.ok(s.includes("dasharray: '2 5'")); // context
  assert.ok(s.includes("dasharray: '3 4'")); // evidence

  // Regression guard: dashed edges should be thresholded (sparse-only).
  assert.ok(s.includes('DASH_CONTEXT_LIMIT'));
  assert.ok(s.includes('DASH_EVIDENCE_LIMIT'));
 });

test('mission lens workbench uses fused bipartite plus layered mission graph', () => {
  const s = read('src/routes/graphs/mission-lens/+page.svelte');
  assert.ok(s.includes('BipartiteGraph'));
  assert.ok(s.includes('LayeredGraph'));
  assert.ok(s.includes('Actual vs Should'));
  assert.ok(s.includes('Deadline Semantics'));
  assert.ok(s.includes('Add Planning Node'));
  assert.ok(s.includes('Review Actual Mapping'));
  assert.ok(s.includes('Observed Activity Rows'));
  assert.ok(s.includes('Reassign to selected node'));
  assert.ok(s.includes('Unlink'));
  assert.ok(s.includes('Abstain / leave unresolved'));
  assert.ok(s.includes('Lexical Explanation'));
  assert.ok(s.includes('Top Alternative'));
  assert.ok(s.includes('Keep primary lexical match'));
  assert.ok(s.includes('Link to top alternative'));
  assert.ok(s.includes('Apply Safe Recommendations'));
  assert.ok(s.includes('recommended:'));
  assert.ok(s.includes('Effective Provenance'));
  assert.ok(s.includes('selectedActivityCurrent.receipts?.length'));
  assert.ok(s.includes('mapping.receipts?.length'));
  assert.ok(s.includes('receipt.kind'));
  assert.ok(s.includes('receipt.value'));
});

test('wiki fact timeline surfaces proposition overlay details', () => {
  const server = read('src/routes/graphs/wiki-fact-timeline/+page.server.ts');
  const page = read('src/routes/graphs/wiki-fact-timeline/+page.svelte');
  assert.ok(server.includes('type AooProposition'));
  assert.ok(server.includes('proposition_links'));
  assert.ok(page.includes('Propositions'));
  assert.ok(page.includes('propositionLabel('));
  assert.ok(page.includes('does_not_negate'));
  assert.ok(page.includes('source_signal'));
});

test('narrative comparison workbench renders shared vs disputed narrative sections', () => {
  const server = read('src/routes/graphs/narrative-compare/+page.server.ts');
  const page = read('src/routes/graphs/narrative-compare/+page.svelte');
  const loader = read('src/lib/server/narrativeCompare.ts');
  assert.ok(server.includes('loadNarrativeComparison'));
  assert.ok(loader.includes("scripts', 'narrative_compare.py"));
  assert.ok(loader.includes('friendlyjordies_demo'));
  assert.ok(page.includes('Narrative Comparison Workbench'));
  assert.ok(page.includes('Shared propositions'));
  assert.ok(page.includes('Disputed propositions'));
  assert.ok(page.includes('Link differences'));
  assert.ok(page.includes('Corroboration + abstentions'));
  assert.ok(page.includes('FriendlyJordies public-media demo'));
});
