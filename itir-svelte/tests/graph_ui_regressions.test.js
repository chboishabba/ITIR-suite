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
  const overlay = read('src/lib/server/wiki_timeline/hca_overlay.ts');
  assert.ok(overlay.includes('maybeOverlayHcaPayload'));
  assert.ok(overlay.includes('needsHcaEventOverlay'));
  assert.ok(overlay.includes('wiki_timeline_hca_s942025_aoo.json'));
});

test('chat archive path resolver falls back to non-dot chat archive path', () => {
  const s = read('src/lib/server/chatArchive.ts');
  assert.ok(s.includes('ITIR_CHAT_ARCHIVE_DB_PATH'));
  assert.ok(s.includes('CHAT_ARCHIVE_DB_PATH'));
  assert.ok(s.includes('resolveChatArchiveCandidates'));
  assert.ok(s.includes("'/tmp/dashig_chat_archive_latest.sqlite'"));
  assert.ok(s.includes("'.chat_archive.sqlite'"));
  assert.ok(s.includes("'chat_archive.sqlite'"));
  assert.ok(s.indexOf("'chat_archive.sqlite'") < s.indexOf("'/tmp/dashig_chat_archive_latest.sqlite'"));
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

test('timeline ribbon workbench is distinct from step-ribbon and wires the ribbon UI contract', () => {
  const home = read('src/routes/+page.svelte');
  const page = read('src/routes/graphs/timeline-ribbon/+page.svelte');
  const server = read('src/routes/graphs/timeline-ribbon/+page.server.ts');
  const ribbon = read('src/lib/sb-dashboard/components/TimelineRibbonLite.svelte');
  const adapter = read('src/lib/sb-dashboard/adapters/ribbon.ts');
  assert.ok(home.includes('/graphs/timeline-ribbon'));
  assert.ok(page.includes('Timeline Ribbon Workbench'));
  assert.ok(page.includes('This keeps conserved-allocation ribbon behavior separate from AAO step-ribbon graph placement.'));
  assert.ok(server.includes('buildTimelinePayload'));
  assert.ok(server.includes('query_dashboard_db.py'));
  assert.ok(server.includes('timeline'));
  assert.ok(ribbon.includes('data-testid="ribbon-viewport"'));
  assert.ok(ribbon.includes('data-testid="conservation-badge"'));
  assert.ok(ribbon.includes('data-testid="segment"'));
  assert.ok(ribbon.includes('data-testid="lens-switcher"'));
  assert.ok(ribbon.includes('data-testid={`lens-item:${item.id}`}'));
  assert.ok(ribbon.includes('data-testid="compare-overlay"'));
  assert.ok(adapter.includes("export type RibbonLensId = 'chat_chars' | 'chat_events' | 'events';"));
  assert.ok(adapter.includes('width_norm'));
  assert.ok(adapter.includes('threads: RibbonThreadCallout[]'));
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
  const reviewState = read('src/lib/workbench/reviewState.ts');
  const selectionBridge = read('src/lib/workbench/selectionBridge.ts');
  assert.ok(server.includes('loadNarrativeComparison'));
  assert.ok(server.includes("url.searchParams.get('threadId')"));
  assert.ok(loader.includes('narrative_compare.py'));
  assert.ok(loader.includes("'--thread-id'"));
  assert.ok(loader.includes('friendlyjordies_demo'));
  assert.ok(loader.includes('friendlyjordies_thread_extract'));
  assert.ok(page.includes('Narrative Comparison Workbench'));
  assert.ok(page.includes('Review rows'));
  assert.ok(page.includes('Inspector'));
  assert.ok(page.includes('Open graph focus'));
  assert.ok(page.includes('Scoped graph'));
  assert.ok(page.includes('selectionBadge'));
  assert.ok(page.includes('createSelectionBridge'));
  assert.ok(page.includes('rowSelectionBridge'));
  assert.ok(server.includes('stateReason'));
  assert.ok(server.includes('narrativeCompareReviewState'));
  assert.ok(reviewState.includes('narrativeCompareReviewState'));
  assert.ok(selectionBridge.includes('createSelectionBridge'));
  assert.ok(loader.includes('FriendlyJordies public-media demo'));
});

test('arguments workbench route renders split transcript plus inspector tabs', () => {
  const server = read('src/routes/arguments/thread/[threadId]/+page.server.ts');
  const page = read('src/routes/arguments/thread/[threadId]/+page.svelte');
  const loader = read('src/lib/server/threadArguments.ts');
  const reviewState = read('src/lib/workbench/reviewState.ts');
  const selectionBridge = read('src/lib/workbench/selectionBridge.ts');
  assert.ok(server.includes('loadThreadArgumentsWorkbench'));
  assert.ok(page.includes('Thread transcript'));
  assert.ok(page.includes('Claim inspector'));
  assert.ok(page.includes('Literal'));
  assert.ok(page.includes('Family'));
  assert.ok(page.includes('Counterpoints'));
  assert.ok(page.includes('Graph'));
  assert.ok(page.includes('Thread mini-map'));
  assert.ok(page.includes('Open graph focus'));
  assert.ok(page.includes('data.stateReason'));
  assert.ok(page.includes('claimSelectionBridge'));
  assert.ok(page.includes('setHovered'));
  assert.ok(server.includes('stateReason'));
  assert.ok(server.includes('threadReviewState'));
  assert.ok(loader.includes('friendlyjordies_thread_extract'));
  assert.ok(loader.includes('friendlyjordies_chat_arguments'));
  assert.ok(loader.includes('friendlyjordies_authority_wrappers'));
  assert.ok(loader.includes('thread.sourceThreadId ?? thread.canonicalThreadId'));
  assert.ok(reviewState.includes('threadReviewState'));
  assert.ok(selectionBridge.includes('SelectionBridgeState'));
});

test('arguments workbench anchors only matched spans and does not fan out by family keywords', () => {
  const loader = read('src/lib/server/threadArguments.ts');
  assert.ok(loader.includes('function claimCandidates'));
  assert.ok(loader.includes('function findFamilySentenceSpan'));
  assert.ok(loader.includes('return null;'));
  assert.ok(!loader.includes("FAMILY_META[claim.familyId]?.keywords[0]"));
  assert.ok(!loader.includes('findMessageMatches('));
  assert.ok(!loader.includes('end: Math.min(haystack.length, Math.max(32'));
});

test('TranscriptViewer exposes a polite live region for the active cue', () => {
  const s = read('src/lib/viewers/TranscriptViewer.svelte');
  assert.ok(s.includes('aria-live="polite"'));
  assert.ok(s.includes('role="status"'));
  assert.ok(s.includes('activeCueAnnouncement'));
  assert.ok(s.includes('No active transcript cue.'));
  assert.ok(s.includes('aria-label={searchAriaLabel}'));
  assert.ok(s.includes('aria-label={manualScrubAriaLabel}'));
  assert.ok(s.includes('for={transcriptSearchId}'));
  assert.ok(s.includes('for={manualScrubId}'));
  assert.ok(s.includes('aria-pressed={globalIdx === activeCueIndex}'));
  assert.ok(s.includes('aria-label={`Select cue'));
});

test('DocumentViewer exposes labeled search and line-selection announcement state', () => {
  const s = read('src/lib/viewers/DocumentViewer.svelte');
  assert.ok(s.includes('aria-label="Search document text"'));
  assert.ok(s.includes('selectedLineAnnouncement'));
  assert.ok(s.includes('role="status"'));
  assert.ok(s.includes('aria-label={`Select line'));
  assert.ok(s.includes('aria-pressed={selectedLine === row.idx}'));
});

test('FolderListViewer exposes labeled filter and selected entry state', () => {
  const s = read('src/lib/viewers/FolderListViewer.svelte');
  assert.ok(s.includes('aria-label={searchAriaLabel}'));
  assert.ok(s.includes('for={searchInputId}'));
  assert.ok(s.includes('aria-label={`${entry.kind} ${entry.name}`'));
  assert.ok(s.includes("aria-current={selectedId === entry.id ? 'true' : undefined}"));
});

test('HCA viewbench keeps transcript/document viewer components wired together', () => {
  const page = read('src/routes/viewers/hca-case/+page.svelte');
  const transcript = read('src/lib/viewers/TranscriptViewer.svelte');
  const document = read('src/lib/viewers/DocumentViewer.svelte');
  const folder = read('src/lib/viewers/FolderListViewer.svelte');
  assert.ok(page.includes('TranscriptViewer'));
  assert.ok(page.includes('DocumentViewer'));
  assert.ok(page.includes('FolderListViewer'));
  assert.ok(page.includes('selectionState'));
  assert.ok(transcript.includes('role="region" aria-label={title}'));
  assert.ok(document.includes('role="region" aria-label={title}'));
  assert.ok(folder.includes('role="region" aria-label={title}'));
});

test('Threads route exposes a labeled search control', () => {
  const page = read('src/routes/threads/+page.svelte');
  assert.ok(page.includes('aria-label="Search threads"'));
  assert.ok(page.includes('id="threads-search"'));
});

test('Thread viewer route exposes a labeled filter control', () => {
  const page = read('src/routes/thread/[threadId]/+page.svelte');
  assert.ok(page.includes('aria-label="Filter thread messages"'));
  assert.ok(page.includes('id="thread-filter"'));
});

test('Thread viewer stays client-rendered and truncates oversized payloads for stability', () => {
  const routeFlags = read('src/routes/thread/[threadId]/+page.ts');
  const server = read('src/routes/thread/[threadId]/+page.server.ts');
  assert.ok(routeFlags.includes('export const ssr = false;'));
  assert.ok(server.includes('MAX_TOOL_THREAD_TEXT_CHARS'));
  assert.ok(server.includes('thread viewer stability'));
});

test('Mission lens form inputs expose accessible names', () => {
  const page = read('src/routes/graphs/mission-lens/+page.svelte');
  assert.ok(page.includes('aria-label="Mission lens run id"'));
  assert.ok(page.includes('aria-label="Mission title"'));
  assert.ok(page.includes('aria-label="Deadline"'));
  assert.ok(page.includes('aria-label="Start window"'));
  assert.ok(page.includes('aria-label="Note for review link"'));
  assert.ok(page.includes('aria-label="Note for reassign activity"'));
  assert.ok(page.includes('aria-label="Note for unlink activity"'));
  assert.ok(page.includes('aria-label="Note for unresolved activity"'));
});

test('Semantic report search inputs are labeled', () => {
  const page = read('src/routes/graphs/semantic-report/+page.svelte');
  assert.ok(page.includes('aria-label="Search selected event text"'));
  assert.ok(page.includes('aria-label="Search source document text"'));
});

test('Wiki candidates inputs are labeled', () => {
  const page = read('src/routes/graphs/wiki-candidates/+page.svelte');
  assert.ok(page.includes('aria-label="Top N results"'));
});

test('Wiki timeline controls are labeled', () => {
  const page = read('src/routes/graphs/wiki-timeline/+page.svelte');
  assert.ok(page.includes('aria-label="Top N timeline events"'));
});

test('Wiki timeline AAO controls are labeled', () => {
  const page = read('src/routes/graphs/wiki-timeline-aoo/+page.svelte');
  assert.ok(page.includes('aria-label="Dataset source"'));
});

test('Wiki fact timeline controls are labeled', () => {
  const page = read('src/routes/graphs/wiki-fact-timeline/+page.svelte');
  assert.ok(page.includes('aria-label="Max facts"'));
});

test('Wiki timeline AAO-all controls are labeled', () => {
  const panel = read('src/lib/wiki_timeline/components/ControlsPanel.svelte');
  assert.ok(panel.includes('aria-label="Dataset source"'));
  assert.ok(panel.includes('aria-label="Time granularity"'));
  assert.ok(panel.includes('aria-label="Max events"'));
  assert.ok(panel.includes('aria-label="Max subjects"'));
  assert.ok(panel.includes('aria-label="Max objects"'));
  assert.ok(panel.includes('aria-label="Max numeric values"'));
  assert.ok(panel.includes('aria-label="Show source lane"'));
  assert.ok(panel.includes('aria-label="Show lens lane"'));
  assert.ok(panel.includes('aria-label="Show evidence lane"'));
  assert.ok(panel.includes('aria-label="Show requesters"'));
  assert.ok(panel.includes('aria-label="Show purpose"'));
});

test('Wiki timeline AAO-all context panel is extracted', () => {
  const panel = read('src/lib/wiki_timeline/components/ContextPanel.svelte');
  assert.ok(panel.includes('selected: {selectedNodeId}'));
  assert.ok(panel.includes('requester_window: signal={requesterCoverageWindow.requestSignalEvents}'));
  assert.ok(panel.includes('data-ctx-id={r.event_id}'));
  assert.ok(panel.includes('bind:this={contextBox}'));
});

test('Wiki revision contested selects are labeled', () => {
  const page = read('src/routes/graphs/wiki-revision-contested/+page.svelte');
  assert.ok(page.includes('aria-label="Contested graph pack"'));
  assert.ok(page.includes('aria-label="Contested graph run"'));
  assert.ok(page.includes('aria-label="Contested article"'));
});

test('Timeline ribbon date inputs are labeled', () => {
  const page = read('src/routes/graphs/timeline-ribbon/+page.svelte');
  assert.ok(page.includes('aria-label="Timeline start date"'));
  assert.ok(page.includes('aria-label="Timeline end date"'));
});

test('Narrative comparison inspector tabs expose tab semantics', () => {
  const page = read('src/routes/graphs/narrative-compare/+page.svelte');
  assert.ok(page.includes('role="tablist"'));
  assert.ok(page.includes('role="tab"'));
  assert.ok(page.includes('aria-selected={activeTab === tab}'));
});

test('Arguments workbench tabs and highlight controls expose stateful a11y attributes', () => {
  const page = read('src/routes/arguments/thread/[threadId]/+page.svelte');
  assert.ok(page.includes("aria-pressed={highlightMode === 'literal'}"));
  assert.ok(page.includes("aria-pressed={highlightMode === 'family'}"));
  assert.ok(page.includes('role="tablist"'));
  assert.ok(page.includes('role="tab"'));
  assert.ok(page.includes('aria-selected={activeTab === tab}'));
});

test('chat tool renderer handles request_user_input as structured questions', () => {
  const parse = read('src/lib/chat/parseToolCall.ts');
  const block = read('src/lib/chat/ToolCallBlock.svelte');
  assert.ok(parse.includes("'request_user_input'"));
  assert.ok(block.includes("tool === 'request_user_input'"));
  assert.ok(block.includes('user input request'));
  assert.ok(block.includes('No structured questions found in payload.'));
});

test('wiki revision contested page distinguishes producer errors from missing or ready graph payloads', () => {
  const page = read('src/routes/graphs/wiki-revision-contested/+page.svelte');
  const server = read('src/routes/graphs/wiki-revision-contested/+page.server.ts');
  const reviewState = read('src/lib/workbench/reviewState.ts');
  const selectionBridge = read('src/lib/workbench/selectionBridge.ts');
  assert.ok(page.includes('Selected article state'));
  assert.ok(page.includes('wikiContestedReviewState'));
  assert.ok(page.includes('graphNodeSelectionBridge'));
  assert.ok(page.includes('producer_error'));
  assert.ok(page.includes('graph_not_enabled'));
  assert.ok(page.includes('missing_graph_payload'));
  assert.ok(page.includes('graph_ready'));
  assert.ok(page.includes('Producer error: the selected article did not complete revision processing'));
  assert.ok(page.includes('Graph not enabled: this pack only persisted pair-level revision analysis'));
  assert.ok(page.includes('The run marked a contested graph as available, but the selected graph payload did not hydrate.'));
  assert.ok(server.includes('computeStateReason'));
  assert.ok(server.includes('stateReason'));
  assert.ok(reviewState.includes('wikiContestedReviewState'));
  assert.ok(selectionBridge.includes('SelectionBridgeReason'));
});

test('workbench routes do not persist UI state through JSON blobs/localStorage', () => {
  const argsPage = read('src/routes/arguments/thread/[threadId]/+page.svelte');
  const narrativePage = read('src/routes/graphs/narrative-compare/+page.svelte');
  const wikiPage = read('src/routes/graphs/wiki-revision-contested/+page.svelte');
  assert.ok(!argsPage.includes('localStorage'));
  assert.ok(!narrativePage.includes('localStorage'));
  assert.ok(!wikiPage.includes('localStorage'));
  assert.ok(!argsPage.includes('JSON.stringify('));
  assert.ok(!narrativePage.includes('JSON.stringify('));
  assert.ok(!wikiPage.includes('JSON.stringify('));
});

test('graphs catch-all route redirects canonical chat-archive graph refs to the narrative comparison workbench', () => {
  const server = read('src/routes/graphs/[...graphRef]/+page.server.ts');
  assert.ok(server.includes('chat_archive://canonical_thread/'));
  assert.ok(server.includes("friendlyjordies_thread_extract"));
  assert.ok(server.includes('/graphs/narrative-compare?fixture='));
  assert.ok(server.includes("'/graphs/narrative-compare'"));
});

test('fact review workbench route loads persisted workbench and acceptance payloads', () => {
  const server = read('src/routes/graphs/fact-review/+page.server.ts');
  const page = read('src/routes/graphs/fact-review/+page.svelte');
  const loader = read('src/lib/server/factReview.ts');
  const helpers = read('src/lib/workbench/factReview.js');
  const home = read('src/routes/+page.svelte');
  assert.ok(server.includes('loadFactReviewWorkbench'));
  assert.ok(server.includes('loadFactReviewAcceptance'));
  assert.ok(server.includes("url.searchParams.get('workflow')"));
  assert.ok(server.includes("url.searchParams.get('wave')"));
  assert.ok(loader.includes('query_fact_review.py'));
  assert.ok(loader.includes("'workbench'"));
  assert.ok(loader.includes("'acceptance'"));
  assert.ok(loader.includes("'sources'"));
  assert.ok(loader.includes('parseFactReviewCliPayload'));
  assert.ok(page.includes('Recent / source-centric reopen'));
  assert.ok(page.includes('resolveFactReviewSourceRows'));
  assert.ok(page.includes('resolveFactReviewAvailableIssueFilters'));
  assert.ok(page.includes('Open current persisted run'));
  assert.ok(page.includes('Inspector classification'));
  assert.ok(page.includes('resolveInspectorStatusRows'));
  assert.ok(helpers.includes("label: 'Party assertion'"));
  assert.ok(helpers.includes("label: 'Procedural outcome'"));
  assert.ok(helpers.includes("label: 'Later annotation'"));
  assert.ok(page.includes("filterKey.replaceAll('_', ' ')"));
  assert.ok(page.includes('Fact Review Workbench'));
  assert.ok(page.includes('Read-only Mary-parity inspection'));
  assert.ok(page.includes('Operator views'));
  assert.ok(page.includes('Story acceptance'));
  assert.ok(page.includes('Approximate chronology'));
  assert.ok(page.includes('Observation signals:'));
  assert.ok(page.includes('Source provenance:'));
  assert.ok(page.includes('Inspector'));
  assert.ok(page.includes('resolveChronologyBuckets'));
  assert.ok(page.includes('No reopen sources are available for this workflow yet.'));
  assert.ok(page.includes('No acceptance stories were recorded for this selector.'));
  assert.ok(page.includes('No items are available for this operator view and filter yet.'));
  assert.ok(home.includes('Mary-parity fact review workbench'));
});

test('normalized artifacts route surfaces operator questions and review-specific next actions without local reinterpretation', () => {
  const server = read('src/routes/graphs/normalized-artifacts/+page.server.ts');
  const loader = read('src/lib/server/normalizedArtifacts.ts');
  const conformance = read('src/lib/server/normalizedArtifactConformance.ts');
  const tircorder = read('src/lib/server/tircorderSourceArtifact.ts');
  const page = read('src/routes/graphs/normalized-artifacts/+page.svelte');

  assert.ok(server.includes('loadFactReviewNormalizedArtifact'));
  assert.ok(server.includes('loadSbNormalizedArtifact'));
  assert.ok(server.includes('loadArchiveNormalizedArtifact'));
  assert.ok(server.includes('summarizeNormalizedArtifactConformance'));
  assert.ok(server.includes("url.searchParams.get('archiveArtifact')"));
  assert.ok(server.includes("url.searchParams.get('captureArtifact')"));
  assert.ok(loader.includes('buildFactReviewInspectHref'));
  assert.ok(loader.includes("producer: 'chat-export-structurer'"));
  assert.ok(loader.includes("inspect_href: '/corpora/chat-archive'"));
  assert.ok(loader.includes("inspect_label: workflowSummary?.recommended_view ? 'Open recommended review view' : 'Open fact review workbench'"));
  assert.ok(loader.includes("inspect_href: '/graphs/timeline-ribbon'"));
  assert.ok(loader.includes('return loadTircorderSourceArtifact(artifactPath);'));
  assert.ok(tircorder.includes("producer: 'tircorder-JOBBIE'"));
  assert.ok(!tircorder.includes("inspect_href: '/graphs/timeline-ribbon'"));
  assert.ok(conformance.includes("const SCHEMA_VERSION = 'itir.normalized.artifact.v1'"));
  assert.ok(conformance.includes('promoted_record requires authority.promotion_receipt_ref.receipt_id'));
  assert.ok(page.includes('what this artifact is, why it exists, what supports it, and what remains unresolved'));
  assert.ok(page.includes('Contract conformance'));
  assert.ok(page.includes('Promotion gate'));
  assert.ok(page.includes('Recommended next action'));
  assert.ok(loader.includes('Open recommended review view'));
  assert.ok(page.includes('Upstream artifacts'));
  assert.ok(page.includes('The operator questions are explicit here'));
  assert.ok(page.includes('Archive artifact'));
  assert.ok(page.includes('Capture artifact'));
  assert.ok(page.includes('No contract issues detected in the loaded payload.'));
  assert.ok(page.includes('Capture/archive adoption is explicit-path only for now.'));
});
