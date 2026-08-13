<script lang="ts">
  import LayeredGraph from '$lib/ui/LayeredGraph.svelte';
  import TokenArcInspector from '$lib/semantic/TokenArcInspector.svelte';
  import DocumentViewer from '$lib/viewers/DocumentViewer.svelte';

  export let form:
    | {
        ok?: boolean;
        error?: string;
      }
    | undefined;

  export let data: {
    source: string;
    label: string;
    report: any;
    reviewedLinkage: any;
    available: Array<{ key: string; label: string }>;
    comparison?: any;
    graphGate?: any;
    semanticGraph?: any;
    tokenArcDebug?: any;
    corrections?: Array<{
      correction_submission_id: string;
      action_kind: string;
      event_id: string;
      relation_id?: string | null;
      created_at: string;
      note?: string;
    }>;
    error: string | null;
  };

  type DocumentHighlight = {
    key: string;
    charStart: number;
    charEnd: number;
    color: string;
    opacity?: number;
    kind?: 'active' | 'relation_peer' | 'echo';
    label?: string;
    source?: 'mention' | 'receipt' | 'label_fallback' | 'event_span';
    sourceArtifactId?: string;
  };

  type SourceDocument = {
    sourceDocumentId: string;
    sourceType: string;
    title: string;
    text: string;
    eventCount: number;
    eventIds: string[];
  };

  type SelectionRequest = {
    requestKey: string;
    eventId: string;
    relationId: string;
    anchorKey: string | null;
  };

  function changeSource(source: string) {
    window.location.href = `/graphs/semantic-report?source=${encodeURIComponent(source)}`;
  }

  function deltaClass(n: number): string {
    if (n > 0) return 'text-emerald-700';
    if (n < 0) return 'text-rose-700';
    return 'text-zinc-600';
  }

  const topPromoted = data.report?.promoted_relations?.slice(0, 25) ?? [];
  const topCandidate = data.report?.candidate_only_relations?.slice(0, 25) ?? [];
  const unresolved = data.report?.unresolved_mentions?.slice(0, 25) ?? [];
  const perSeed = data.reviewedLinkage?.per_seed ?? [];
  const perEntity = data.report?.per_entity?.slice(0, 25) ?? [];
  const unmatchedSeeds = data.reviewedLinkage?.unmatched_seeds ?? [];
  const ambiguousEvents = data.reviewedLinkage?.ambiguous_events ?? [];
  const compare = data.comparison;
  const gwbSnap = compare?.corpora?.gwb;
  const hcaSnap = compare?.corpora?.hca;
  const predicateDelta = compare?.delta?.predicates ?? [];
  const summaryDelta = compare?.delta?.summary ?? {};
  const graphGate = data.graphGate ?? compare?.graphGate;
  const semanticGraph = data.semanticGraph ?? compare?.semanticGraph;
  const graphViewportKey = `${String(graphGate?.enabled ?? false)}:${String(graphGate?.predicateTypeCount ?? 0)}:${String(graphGate?.totalRelationCandidates ?? 0)}`;
  const tokenArcDebug = data.tokenArcDebug ?? { events: [], unavailableReason: null };
  const reviewSummary = data.report?.review_summary ?? {};
  const reviewPredicateCounts = reviewSummary?.predicate_counts ?? {};
  const reviewCandidateCounts = Object.entries(reviewPredicateCounts?.candidate_only ?? {}).sort((a, b) => Number(b[1]) - Number(a[1]) || String(a[0]).localeCompare(String(b[0]))).slice(0, 8) as Array<[string, number]>;
  const reviewPromotedCounts = Object.entries(reviewPredicateCounts?.promoted ?? {}).sort((a, b) => Number(b[1]) - Number(a[1]) || String(a[0]).localeCompare(String(b[0]))).slice(0, 8) as Array<[string, number]>;
  const reviewCueSurfaces = Object.entries(reviewSummary?.top_cue_surfaces ?? {}).slice(0, 6) as Array<[string, Array<[string, number]>]>;
  const reviewFamilyCounts = Object.entries(reviewSummary?.family_counts ?? {}).sort((a, b) => Number(b[1]) - Number(a[1]) || String(a[0]).localeCompare(String(b[0]))) as Array<[string, number]>;
  const reviewTextDebug = reviewSummary?.text_debug ?? {};
  const missionObserver = data.report?.mission_observer ?? null;
  const missionSummary = missionObserver?.summary ?? {};
  const missionMissions = missionObserver?.missions ?? [];
  const missionFollowups = missionObserver?.followups ?? [];
  const missionOverlays = missionObserver?.sb_observer_overlays ?? [];
  const corrections = data.corrections ?? [];
  const sourceDocuments = (data.report?.source_documents ?? []) as SourceDocument[];
  const sourceDocumentsById = new Map(sourceDocuments.map((row) => [row.sourceDocumentId, row]));
  let selectedSemanticEventId = tokenArcDebug.events?.[0]?.eventId ?? '';
  let correctionActionKind = 'mark_false_positive';
  let proposedPredicateKey = '';
  let replacementLabel = '';
  let correctionNote = '';
  let selectionRequest: SelectionRequest | null = null;
  let selectionRequestCounter = 0;
  let activeSemanticSelection: {
    eventId: string;
    text: string;
    activeAnchorKey: string | null;
    activeRelationId: string | null;
    role: string | null;
    family: string | null;
    color: string | null;
    activeAnchorSource: 'mention' | 'receipt' | 'label_fallback' | null;
    sourceArtifactId: string | null;
    charStart: number | null;
    charEnd: number | null;
    provenanceSummary: {
      strongestSource: 'mention' | 'receipt' | 'label_fallback';
      counts: Record<string, number>;
      note: string;
    } | null;
    highlights: DocumentHighlight[];
  } | null = null;

  $: if ((!selectedSemanticEventId || !(tokenArcDebug.events ?? []).some((event: any) => event.eventId === selectedSemanticEventId)) && (tokenArcDebug.events?.length ?? 0)) {
    selectedSemanticEventId = tokenArcDebug.events[0]?.eventId ?? '';
  }
  $: selectedSemanticEvent =
    (tokenArcDebug.events ?? []).find((event: any) => event.eventId === selectedSemanticEventId) ?? tokenArcDebug.events?.[0] ?? null;
  $: selectedSemanticRelation =
    activeSemanticSelection?.eventId === selectedSemanticEvent?.eventId
      ? selectedSemanticEvent?.relations?.find((relation: any) => relation.relationId === activeSemanticSelection?.activeRelationId) ?? null
      : null;
  $: correctionEvidencePayload = JSON.stringify(
    activeSemanticSelection
      ? [
          {
            event_id: activeSemanticSelection.eventId,
            relation_id: activeSemanticSelection.activeRelationId,
            anchor_key: activeSemanticSelection.activeAnchorKey,
            source_artifact_id: activeSemanticSelection.sourceArtifactId,
            char_start: activeSemanticSelection.charStart,
            char_end: activeSemanticSelection.charEnd,
            anchor_source: activeSemanticSelection.activeAnchorSource,
          },
          ...activeSemanticSelection.highlights.map((row) => ({
            highlight_key: row.key,
            source_artifact_id: row.sourceArtifactId,
            char_start: row.charStart,
            char_end: row.charEnd,
            source: row.source,
            kind: row.kind,
          })),
        ]
      : [],
    null,
    0,
  );
  $: eventViewerText = activeSemanticSelection?.eventId === selectedSemanticEvent?.eventId ? activeSemanticSelection?.text ?? selectedSemanticEvent?.text ?? '' : selectedSemanticEvent?.text ?? '';
  $: passiveEventHighlights = (() => {
    if (!selectedSemanticEvent?.relations) return [];
    const out = new Map<string, DocumentHighlight>();
    for (const relation of selectedSemanticEvent.relations) {
      for (const anchor of relation.anchors ?? []) {
        if (!out.has(anchor.key)) {
          out.set(anchor.key, {
            key: anchor.key,
            charStart: anchor.charStart,
            charEnd: anchor.charEnd,
            color: relation.color,
            opacity: Math.max(0.12, relation.opacity * 0.45),
            kind: 'echo',
            label: anchor.label,
            source: anchor.source,
            sourceArtifactId: anchor.sourceArtifactId,
          });
        }
      }
    }
    return Array.from(out.values());
  })();
  $: eventViewerHighlights =
    activeSemanticSelection?.eventId === selectedSemanticEvent?.eventId
      ? activeSemanticSelection?.highlights ?? []
      : passiveEventHighlights;
  $: selectedSemanticSourceDocument =
    selectedSemanticEvent?.sourceDocumentId ? sourceDocumentsById.get(selectedSemanticEvent.sourceDocumentId) ?? null : null;
  $: sourceViewerText = selectedSemanticSourceDocument?.text ?? '';
  $: sourceViewerHighlights = (() => {
    if (!selectedSemanticEvent || !selectedSemanticSourceDocument) return [];
    const eventStart = Number(selectedSemanticEvent.sourceCharStart);
    const eventEnd = Number(selectedSemanticEvent.sourceCharEnd);
    if (!Number.isFinite(eventStart) || !Number.isFinite(eventEnd)) return [];
    const selection = activeSemanticSelection;
    const baseHighlights =
      selection && selection.eventId === selectedSemanticEvent.eventId
        ? selection.highlights
        : passiveEventHighlights;
    const translated = baseHighlights.map((row) => ({
      ...row,
      charStart: row.charStart + eventStart,
      charEnd: row.charEnd + eventStart
    }));
    return [
      {
        key: `${selectedSemanticEvent.eventId}:event-span`,
        charStart: eventStart,
        charEnd: eventEnd,
        color: activeSemanticSelection?.color ?? '#64748b',
        opacity: activeSemanticSelection ? 0.1 : 0.14,
        kind: 'echo',
        label: 'Selected event',
        source: 'event_span',
        sourceArtifactId: selectedSemanticEvent.sourceDocumentId ?? undefined
      } satisfies DocumentHighlight,
      ...translated
    ];
  })();
  const sourceViewerUnavailableReason = 'No source document payload is available for this corpus/event yet.';

  function requestSelectionFromHighlight(highlight: DocumentHighlight | undefined, sourceEventId: string | undefined): void {
    if (!highlight || !sourceEventId || !selectedSemanticEvent?.relations) return;
    const relation = selectedSemanticEvent.relations.find((row: any) => row.anchors?.some((anchor: any) => anchor.key === highlight.key));
    if (!relation) return;
    selectionRequestCounter += 1;
    selectionRequest = {
      requestKey: `${selectionRequestCounter}`,
      eventId: sourceEventId,
      relationId: relation.relationId,
      anchorKey: highlight.key,
    };
  }

  function pickHighlightForRange(highlights: DocumentHighlight[], charStart: number, charEnd: number): DocumentHighlight | undefined {
    return [...highlights]
      .filter((row) => Number(row.charEnd) > charStart && Number(row.charStart) < charEnd)
      .sort((a, b) => Number(b.opacity ?? 0) - Number(a.opacity ?? 0))[0];
  }

  function downloadMissionObserver(): void {
    if (!missionObserver || typeof window === 'undefined') return;
    const blob = new Blob([JSON.stringify(missionObserver, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = `mission-observer-${data.source}-${data.report?.run_id ?? 'unknown'}.json`;
    anchor.click();
    URL.revokeObjectURL(url);
  }

  function provenanceBadgeTone(source: 'mention' | 'receipt' | 'label_fallback' | null): string {
    if (source === 'mention') return 'border-emerald-200 bg-emerald-50 text-emerald-800';
    if (source === 'receipt') return 'border-sky-200 bg-sky-50 text-sky-800';
    if (source === 'label_fallback') return 'border-amber-200 bg-amber-50 text-amber-900';
    return 'border-zinc-200 bg-zinc-50 text-zinc-700';
  }
</script>

<svelte:head>
  <title>Semantic Report</title>
</svelte:head>

<div class="mx-auto max-w-7xl px-6 py-8">
  <div class="mb-6 flex flex-wrap items-center justify-between gap-4">
    <div>
      <h1 class="text-3xl font-semibold tracking-tight">Semantic report</h1>
      <p class="text-sm text-zinc-600">Corpus-level semantic report over the current working semantic lanes.</p>
    </div>
    <label class="flex items-center gap-3 text-sm">
      <span>Corpus</span>
      <select
        class="rounded border border-zinc-300 bg-white px-3 py-2"
        value={data.source}
        on:change={(e) => changeSource((e.currentTarget as HTMLSelectElement).value)}
      >
        {#each data.available as option}
          <option value={option.key}>{option.label}</option>
        {/each}
      </select>
    </label>
  </div>

  {#if data.error}
    <div class="rounded border border-red-300 bg-red-50 px-4 py-3 text-sm text-red-800">
      {data.error}
    </div>
  {:else if data.report}
    {#if gwbSnap && hcaSnap}
      <section class="mb-6 rounded border border-zinc-200 bg-white p-4">
        <div class="mb-4 flex flex-wrap items-center justify-between gap-3">
          <h2 class="text-lg font-semibold">Split + delta comparison</h2>
          <div class="text-xs uppercase tracking-[0.16em] text-zinc-500">hca minus gwb deltas</div>
        </div>
        <div class="grid gap-4 lg:grid-cols-2">
          <div class="rounded border border-zinc-200 bg-zinc-50 p-3">
            <div class="mb-2 text-xs uppercase tracking-[0.16em] text-zinc-500">{gwbSnap.label}</div>
            <div class="grid grid-cols-2 gap-2 text-sm">
              <div>Entities: <span class="font-semibold">{gwbSnap.summary.entity_count}</span></div>
              <div>Candidates: <span class="font-semibold">{gwbSnap.summary.relation_candidate_count}</span></div>
              <div>Promoted: <span class="font-semibold">{gwbSnap.summary.promoted_relation_count}</span></div>
              <div>Candidate-only: <span class="font-semibold">{gwbSnap.summary.candidate_only_relation_count}</span></div>
              <div>Unresolved: <span class="font-semibold">{gwbSnap.summary.unresolved_mention_count}</span></div>
              <div>Unmatched seeds: <span class="font-semibold">{gwbSnap.reviewed?.unmatched_count ?? '-'}</span></div>
            </div>
          </div>
          <div class="rounded border border-zinc-200 bg-zinc-50 p-3">
            <div class="mb-2 text-xs uppercase tracking-[0.16em] text-zinc-500">{hcaSnap.label}</div>
            <div class="grid grid-cols-2 gap-2 text-sm">
              <div>Entities: <span class="font-semibold">{hcaSnap.summary.entity_count}</span></div>
              <div>Candidates: <span class="font-semibold">{hcaSnap.summary.relation_candidate_count}</span></div>
              <div>Promoted: <span class="font-semibold">{hcaSnap.summary.promoted_relation_count}</span></div>
              <div>Candidate-only: <span class="font-semibold">{hcaSnap.summary.candidate_only_relation_count}</span></div>
              <div>Unresolved: <span class="font-semibold">{hcaSnap.summary.unresolved_mention_count}</span></div>
              <div>Unmatched seeds: <span class="font-semibold">{hcaSnap.reviewed?.unmatched_count ?? '-'}</span></div>
            </div>
          </div>
        </div>
        <div class="mt-4 grid gap-3 md:grid-cols-5">
          <div class="rounded border border-zinc-200 bg-white p-3 text-sm">
            <div class="text-xs uppercase text-zinc-500">Entities delta</div>
            <div class={`mt-1 text-lg font-semibold ${deltaClass(summaryDelta.entity_count ?? 0)}`}>{summaryDelta.entity_count ?? 0}</div>
          </div>
          <div class="rounded border border-zinc-200 bg-white p-3 text-sm">
            <div class="text-xs uppercase text-zinc-500">Candidates delta</div>
            <div class={`mt-1 text-lg font-semibold ${deltaClass(summaryDelta.relation_candidate_count ?? 0)}`}>{summaryDelta.relation_candidate_count ?? 0}</div>
          </div>
          <div class="rounded border border-zinc-200 bg-white p-3 text-sm">
            <div class="text-xs uppercase text-zinc-500">Promoted delta</div>
            <div class={`mt-1 text-lg font-semibold ${deltaClass(summaryDelta.promoted_relation_count ?? 0)}`}>{summaryDelta.promoted_relation_count ?? 0}</div>
          </div>
          <div class="rounded border border-zinc-200 bg-white p-3 text-sm">
            <div class="text-xs uppercase text-zinc-500">Candidate-only delta</div>
            <div class={`mt-1 text-lg font-semibold ${deltaClass(summaryDelta.candidate_only_relation_count ?? 0)}`}>{summaryDelta.candidate_only_relation_count ?? 0}</div>
          </div>
          <div class="rounded border border-zinc-200 bg-white p-3 text-sm">
            <div class="text-xs uppercase text-zinc-500">Unresolved delta</div>
            <div class={`mt-1 text-lg font-semibold ${deltaClass(summaryDelta.unresolved_mention_count ?? 0)}`}>{summaryDelta.unresolved_mention_count ?? 0}</div>
          </div>
        </div>
        {#if predicateDelta.length}
          <div class="mt-4 overflow-x-auto rounded border border-zinc-200">
            <table class="min-w-full text-left text-sm">
              <thead class="border-b border-zinc-200 bg-zinc-50 text-zinc-600">
                <tr>
                  <th class="px-3 py-2 font-medium">Predicate</th>
                  <th class="px-3 py-2 font-medium">GWB total</th>
                  <th class="px-3 py-2 font-medium">HCA total</th>
                  <th class="px-3 py-2 font-medium">Delta</th>
                </tr>
              </thead>
              <tbody>
                {#each predicateDelta as row}
                  <tr class="border-b border-zinc-100">
                    <td class="px-3 py-2">{row.display_label}</td>
                    <td class="px-3 py-2">{row.gwb_total}</td>
                    <td class="px-3 py-2">{row.hca_total}</td>
                    <td class={`px-3 py-2 font-medium ${deltaClass(row.delta_hca_minus_gwb)}`}>{row.delta_hca_minus_gwb}</td>
                  </tr>
                {/each}
              </tbody>
            </table>
          </div>
        {/if}
      </section>
    {/if}

    <div class="mb-6 grid gap-4 md:grid-cols-3 xl:grid-cols-6">
      <div class="rounded border border-zinc-200 bg-white p-4">
        <div class="text-xs uppercase text-zinc-500">Entities</div>
        <div class="mt-1 text-2xl font-semibold">{data.report.summary.entity_count}</div>
      </div>
      <div class="rounded border border-zinc-200 bg-white p-4">
        <div class="text-xs uppercase text-zinc-500">Candidates</div>
        <div class="mt-1 text-2xl font-semibold">{data.report.summary.relation_candidate_count}</div>
      </div>
      <div class="rounded border border-zinc-200 bg-white p-4">
        <div class="text-xs uppercase text-zinc-500">Promoted</div>
        <div class="mt-1 text-2xl font-semibold">{data.report.summary.promoted_relation_count}</div>
      </div>
      <div class="rounded border border-zinc-200 bg-white p-4">
        <div class="text-xs uppercase text-zinc-500">Candidate only</div>
        <div class="mt-1 text-2xl font-semibold">{data.report.summary.candidate_only_relation_count}</div>
      </div>
      <div class="rounded border border-zinc-200 bg-white p-4">
        <div class="text-xs uppercase text-zinc-500">Unresolved</div>
        <div class="mt-1 text-2xl font-semibold">{data.report.summary.unresolved_mention_count}</div>
      </div>
      <div class="rounded border border-zinc-200 bg-white p-4">
        <div class="text-xs uppercase text-zinc-500">Run</div>
        <div class="mt-1 break-all text-sm font-medium">{data.report.run_id}</div>
      </div>
    </div>

    {#if graphGate}
      <section class="mb-6 rounded border border-zinc-200 bg-white p-4">
        <div class="mb-3 flex flex-wrap items-center justify-between gap-3">
          <h2 class="text-lg font-semibold">AU semantic graph lane</h2>
          <div class="text-xs text-zinc-600">
            gate: {graphGate.predicateTypeCount}/{graphGate.threshold.minPredicateTypes} predicate types,
            {graphGate.totalRelationCandidates}/{graphGate.threshold.minTotalRelationCandidates} relation candidates
          </div>
        </div>
        {#if graphGate.enabled && semanticGraph}
          <LayeredGraph
            layers={semanticGraph.layers}
            edges={semanticGraph.edges}
            width={2860}
            height={780}
            colGap={760}
            leftPad={110}
            scrollWhenOverflow={true}
            fitToWidth={false}
            viewportResetKey={graphViewportKey}
          />
          <p class="mt-3 text-xs text-zinc-600">Solid edges indicate promoted support. Dashed edges indicate candidate-only support.</p>
        {:else}
          <div class="rounded border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-900">
            Graph lane is waiting for richer AU coverage. It auto-enables at
            {graphGate.threshold.minPredicateTypes}+ predicate types and {graphGate.threshold.minTotalRelationCandidates}+ relation candidates.
          </div>
        {/if}
      </section>
    {/if}

    <div class="mb-6">
      <TokenArcInspector
        events={tokenArcDebug.events ?? []}
        selectedEventId={selectedSemanticEventId}
        {selectionRequest}
        unavailableReason={tokenArcDebug.unavailableReason ?? null}
        on:selectedEventChange={(ev) => {
          selectedSemanticEventId = ev.detail.eventId;
          activeSemanticSelection = null;
        }}
        on:activeSelectionChange={(ev) => {
          activeSemanticSelection = ev.detail;
        }}
      />
    </div>

    {#if activeSemanticSelection?.provenanceSummary}
      <section class="mb-6 rounded border border-zinc-200 bg-white p-4">
        <div class="mb-2 flex flex-wrap items-center gap-2">
          <h2 class="text-sm font-semibold uppercase tracking-[0.16em] text-zinc-700">Active Anchor Quality</h2>
          <span class={`rounded-full border px-2 py-0.5 text-xs font-medium ${provenanceBadgeTone(activeSemanticSelection.activeAnchorSource)}`}>
            {activeSemanticSelection.provenanceSummary.note}
          </span>
        </div>
        <div class="flex flex-wrap gap-2 text-xs">
          <span class="rounded-full border border-emerald-200 bg-emerald-50 px-2 py-1 text-emerald-800">
            mention {activeSemanticSelection.provenanceSummary.counts.mention ?? 0}
          </span>
          <span class="rounded-full border border-sky-200 bg-sky-50 px-2 py-1 text-sky-800">
            receipt {activeSemanticSelection.provenanceSummary.counts.receipt ?? 0}
          </span>
          <span class="rounded-full border border-amber-200 bg-amber-50 px-2 py-1 text-amber-900">
            fallback {activeSemanticSelection.provenanceSummary.counts.label_fallback ?? 0}
          </span>
          {#if activeSemanticSelection.sourceArtifactId}
            <span class="rounded-full border border-zinc-200 bg-zinc-50 px-2 py-1 text-zinc-700">
              source {activeSemanticSelection.sourceArtifactId}
            </span>
          {/if}
        </div>
      </section>
    {/if}

    <div class="mb-6 grid gap-4 xl:grid-cols-2">
      <!-- aria-label="Search selected event text" -->
      <DocumentViewer
        title={selectedSemanticEvent ? `Event text (${selectedSemanticEvent.eventId})` : 'Event text'}
        text={eventViewerText}
        mode="plain"
        maxHeightPx={360}
        highlights={eventViewerHighlights}
        selectedHighlightKey={activeSemanticSelection?.activeAnchorKey ?? null}
        ariaLabel="Search selected event text"
        placeholder="Search selected event text..."
        searchAriaLabel="Search selected event text"
        on:lineSelect={(ev) => {
          const highlight = pickHighlightForRange(eventViewerHighlights, ev.detail.charStart, ev.detail.charEnd);
          requestSelectionFromHighlight(highlight, selectedSemanticEvent?.eventId);
        }}
      />
      {#if selectedSemanticSourceDocument}
        <!-- aria-label="Search source document text" -->
        <DocumentViewer
          title={`Source document (${selectedSemanticSourceDocument.title})`}
          text={sourceViewerText}
          mode="plain"
          maxHeightPx={360}
          highlights={sourceViewerHighlights}
          selectedHighlightKey={activeSemanticSelection?.eventId === selectedSemanticEvent?.eventId ? activeSemanticSelection?.activeAnchorKey ?? null : null}
          ariaLabel="Search source document text"
          placeholder="Search source document text..."
          searchAriaLabel="Search source document text"
          on:lineSelect={(ev) => {
            const highlight = pickHighlightForRange(sourceViewerHighlights, ev.detail.charStart, ev.detail.charEnd);
            requestSelectionFromHighlight(highlight, selectedSemanticEvent?.eventId);
          }}
        />
      {:else}
        <div class="rounded-2xl bg-paper-50 shadow-crisp ring-1 ring-ink-900/10">
          <div class="flex items-center justify-between gap-3 border-b border-ink-900/10 px-4 py-3">
            <div class="font-display text-sm tracking-tight text-ink-950">Source document</div>
            <div class="font-mono text-[10px] text-ink-800/70">explicit fallback</div>
          </div>
          <div class="px-4 py-4 text-sm text-ink-800/75">
            {sourceViewerUnavailableReason}
          </div>
        </div>
      {/if}
    </div>

    <section class="mb-6 grid gap-4 xl:grid-cols-[minmax(0,1.2fr)_minmax(0,0.8fr)]">
      <div class="rounded border border-zinc-200 bg-white p-4">
        <div class="mb-3 flex items-center justify-between gap-3">
          <h2 class="text-lg font-semibold">Review submission</h2>
          <div class="text-xs uppercase tracking-[0.16em] text-zinc-500">append-only</div>
        </div>
        {#if form?.error}
          <div class="mb-3 rounded border border-red-300 bg-red-50 px-3 py-2 text-sm text-red-800">{form.error}</div>
        {/if}
        {#if activeSemanticSelection && selectedSemanticRelation}
          <form method="POST" action="?/submitCorrection" class="space-y-3">
            <input type="hidden" name="source" value={data.source} />
            <input type="hidden" name="runId" value={data.report.run_id} />
            <input type="hidden" name="corpusLabel" value={data.label} />
            <input type="hidden" name="eventId" value={activeSemanticSelection.eventId} />
            <input type="hidden" name="relationId" value={activeSemanticSelection.activeRelationId ?? ''} />
            <input type="hidden" name="anchorKey" value={activeSemanticSelection.activeAnchorKey ?? ''} />
            <input type="hidden" name="evidencePayload" value={correctionEvidencePayload} />
            <div class="rounded border border-zinc-200 bg-zinc-50 p-3 text-sm">
              <div class="font-medium">{selectedSemanticRelation.displayLabel}</div>
              <div class="mt-1 text-xs text-zinc-600">
                {activeSemanticSelection.eventId} · {selectedSemanticRelation.predicateKey} · {selectedSemanticRelation.confidenceTier} · {selectedSemanticRelation.promotionStatus}
              </div>
            </div>
            <div class="grid gap-3 md:grid-cols-2">
              <label class="text-sm">
                <span class="mb-1 block font-medium">Action</span>
                <select class="w-full rounded border border-zinc-300 bg-white px-3 py-2" bind:value={correctionActionKind} name="actionKind">
                  <option value="mark_false_positive">Mark false positive</option>
                  <option value="abstain_relation">Abstain relation</option>
                  <option value="correct_predicate">Correct predicate</option>
                  <option value="correct_anchor">Correct anchor/span</option>
                  <option value="confirm_relation">Confirm relation</option>
                </select>
              </label>
              <label class="text-sm">
                <span class="mb-1 block font-medium">Proposed predicate</span>
                <input class="w-full rounded border border-zinc-300 bg-white px-3 py-2" bind:value={proposedPredicateKey} name="proposedPredicateKey" placeholder="Optional predicate key" />
              </label>
            </div>
            <label class="block text-sm">
              <span class="mb-1 block font-medium">Replacement label / anchor note</span>
              <input class="w-full rounded border border-zinc-300 bg-white px-3 py-2" bind:value={replacementLabel} name="replacementLabel" placeholder="Optional replacement label or anchor note" />
            </label>
            <label class="block text-sm">
              <span class="mb-1 block font-medium">Reviewer note</span>
              <textarea class="min-h-[6rem] w-full rounded border border-zinc-300 bg-white px-3 py-2" bind:value={correctionNote} name="note" placeholder="Why this relation/anchor should be changed or abstained."></textarea>
            </label>
            <div class="flex items-center justify-between gap-3">
              <div class="text-xs text-zinc-500">Selection can come from token arcs or either document viewer.</div>
              <button type="submit" class="rounded border border-zinc-900 bg-zinc-900 px-3 py-2 text-sm font-medium text-white hover:bg-zinc-800">Submit correction</button>
            </div>
          </form>
        {:else}
          <div class="rounded border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-900">
            Select a relation or highlighted anchor from the token arc workbench or document viewers to submit a correction.
          </div>
        {/if}
      </div>
      <div class="rounded border border-zinc-200 bg-white p-4">
        <div class="mb-3 flex items-center justify-between gap-3">
          <h2 class="text-lg font-semibold">Recent corrections</h2>
          <div class="text-xs uppercase tracking-[0.16em] text-zinc-500">{corrections.length} loaded</div>
        </div>
        {#if corrections.length}
          <ul class="space-y-3 text-sm">
            {#each corrections as row}
              <li class="rounded border border-zinc-100 bg-zinc-50 p-3">
                <div class="font-medium">{row.action_kind}</div>
                <div class="mt-1 text-xs text-zinc-600">{row.event_id} {#if row.relation_id}· {row.relation_id}{/if} · {row.created_at}</div>
                {#if row.note}
                  <div class="mt-2 text-sm text-zinc-800">{row.note}</div>
                {/if}
              </li>
            {/each}
          </ul>
        {:else}
          <p class="text-sm text-zinc-500">No corrections have been submitted for this corpus/run yet.</p>
        {/if}
      </div>
    </section>

    {#if missionObserver}
      <section class="mb-6 rounded border border-zinc-200 bg-white p-4">
        <div class="mb-3 flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 class="text-lg font-semibold">Mission observer</h2>
            <p class="text-sm text-zinc-600">Producer-owned mission/follow-up observer artifact for SB-safe reference overlays.</p>
          </div>
          <button type="button" class="rounded border border-zinc-300 bg-white px-3 py-2 text-sm font-medium hover:bg-zinc-50" on:click={downloadMissionObserver}>
            Download mission observer JSON
          </button>
        </div>
        <div class="grid gap-4 lg:grid-cols-4">
          <div class="rounded border border-zinc-200 bg-zinc-50 p-3 text-sm"><div class="text-xs uppercase tracking-[0.16em] text-zinc-500">Missions</div><div class="mt-1 text-2xl font-semibold">{missionSummary.mission_count ?? 0}</div></div>
          <div class="rounded border border-zinc-200 bg-zinc-50 p-3 text-sm"><div class="text-xs uppercase tracking-[0.16em] text-zinc-500">Follow-ups</div><div class="mt-1 text-2xl font-semibold">{missionSummary.followup_count ?? 0}</div></div>
          <div class="rounded border border-zinc-200 bg-zinc-50 p-3 text-sm"><div class="text-xs uppercase tracking-[0.16em] text-zinc-500">Linked</div><div class="mt-1 text-2xl font-semibold">{missionSummary.linked_followup_count ?? 0}</div></div>
          <div class="rounded border border-zinc-200 bg-zinc-50 p-3 text-sm"><div class="text-xs uppercase tracking-[0.16em] text-zinc-500">SB overlays</div><div class="mt-1 text-2xl font-semibold">{missionSummary.overlay_count ?? 0}</div></div>
        </div>
        {#if missionObserver.unavailableReason}
          <div class="mt-4 rounded border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-900">{missionObserver.unavailableReason}</div>
        {/if}
        <div class="mt-4 grid gap-4 xl:grid-cols-2">
          <div class="rounded border border-zinc-200 bg-white p-3 text-sm">
            <div class="mb-2 text-xs uppercase tracking-[0.16em] text-zinc-500">Missions</div>
            {#if missionMissions.length}
              <ul class="space-y-2">
                {#each missionMissions.slice(0, 8) as mission}
                  <li class="rounded border border-zinc-100 bg-zinc-50 p-3">
                    <div class="font-medium">{mission.topicLabel}</div>
                    <div class="mt-1 text-xs text-zinc-600">{mission.missionId} · {mission.confidence}{#if mission.deadline} · deadline {mission.deadline}{/if}</div>
                  </li>
                {/each}
              </ul>
            {:else}
              <div class="text-zinc-500">No mission nodes emitted.</div>
            {/if}
          </div>
          <div class="rounded border border-zinc-200 bg-white p-3 text-sm">
            <div class="mb-2 text-xs uppercase tracking-[0.16em] text-zinc-500">Follow-up resolution</div>
            {#if missionFollowups.length}
              <ul class="space-y-2">
                {#each missionFollowups.slice(0, 8) as row}
                  <li class="rounded border border-zinc-100 bg-zinc-50 p-3">
                    <div class="font-medium">{row.followupTopic}</div>
                    <div class="mt-1 text-xs text-zinc-600">{row.eventId} · {row.status} · {row.confidence}</div>
                    {#if row.resolvedTopicLabel}
                      <div class="mt-1 text-xs text-zinc-700">resolved to {row.resolvedTopicLabel}</div>
                    {/if}
                  </li>
                {/each}
              </ul>
            {:else}
              <div class="text-zinc-500">No follow-up edges emitted.</div>
            {/if}
          </div>
        </div>
        {#if missionOverlays.length}
          <div class="mt-4 rounded border border-zinc-200 bg-zinc-50 p-3 text-xs text-zinc-700">
            SB observer overlays are reference-heavy only: {missionOverlays.length} records ready for loose import without thread/state dumps.
          </div>
        {/if}
      </section>
    {/if}

    <section class="mb-6 rounded border border-zinc-200 bg-white p-4">
      <div class="mb-3 flex flex-wrap items-center justify-between gap-3">
        <h2 class="text-lg font-semibold">Compact review summary</h2>
        <div class="text-xs uppercase tracking-[0.16em] text-zinc-500">producer-owned</div>
      </div>
      <div class="grid gap-4 lg:grid-cols-3">
        <div class="rounded border border-zinc-200 bg-zinc-50 p-3 text-sm">
          <div class="mb-2 text-xs uppercase tracking-[0.16em] text-zinc-500">Text-debug coverage</div>
          <div>Arc-ready events: <span class="font-semibold">{reviewTextDebug.event_count ?? 0}</span></div>
          <div>Arc-ready relations: <span class="font-semibold">{reviewTextDebug.relation_count ?? 0}</span></div>
          <div>Excluded relations: <span class="font-semibold">{reviewTextDebug.excluded_relation_count ?? 0}</span></div>
          {#if reviewTextDebug.unavailable_reason}
            <div class="mt-2 text-xs text-amber-700">{reviewTextDebug.unavailable_reason}</div>
          {/if}
        </div>
        <div class="rounded border border-zinc-200 bg-zinc-50 p-3 text-sm">
          <div class="mb-2 text-xs uppercase tracking-[0.16em] text-zinc-500">Top promoted predicates</div>
          {#if reviewPromotedCounts.length}
            <ul class="space-y-1">
              {#each reviewPromotedCounts as [predicate, count]}
                <li class="flex items-center justify-between gap-3"><span>{predicate}</span><span class="font-semibold">{count}</span></li>
              {/each}
            </ul>
          {:else}
            <div class="text-zinc-500">No promoted predicates.</div>
          {/if}
        </div>
        <div class="rounded border border-zinc-200 bg-zinc-50 p-3 text-sm">
          <div class="mb-2 text-xs uppercase tracking-[0.16em] text-zinc-500">Top candidate-only predicates</div>
          {#if reviewCandidateCounts.length}
            <ul class="space-y-1">
              {#each reviewCandidateCounts as [predicate, count]}
                <li class="flex items-center justify-between gap-3"><span>{predicate}</span><span class="font-semibold">{count}</span></li>
              {/each}
            </ul>
          {:else}
            <div class="text-zinc-500">No candidate-only predicates.</div>
          {/if}
        </div>
      </div>
      <div class="mt-4 grid gap-4 lg:grid-cols-2">
        <div class="rounded border border-zinc-200 bg-white p-3 text-sm">
          <div class="mb-2 text-xs uppercase tracking-[0.16em] text-zinc-500">Top cue surfaces</div>
          {#if reviewCueSurfaces.length}
            <ul class="space-y-2">
              {#each reviewCueSurfaces as [predicate, rows]}
                <li>
                  <div class="font-medium">{predicate}</div>
                  <div class="mt-1 flex flex-wrap gap-2">
                    {#each rows as [surface, count]}
                      <span class="rounded-full border border-zinc-200 bg-zinc-50 px-2 py-1 text-xs">{surface} · {count}</span>
                    {/each}
                  </div>
                </li>
              {/each}
            </ul>
          {:else}
            <div class="text-zinc-500">No cue surfaces recorded.</div>
          {/if}
        </div>
        <div class="rounded border border-zinc-200 bg-white p-3 text-sm">
          <div class="mb-2 text-xs uppercase tracking-[0.16em] text-zinc-500">Relation families</div>
          {#if reviewFamilyCounts.length}
            <div class="flex flex-wrap gap-2">
              {#each reviewFamilyCounts as [family, count]}
                <span class="rounded-full border border-zinc-200 bg-zinc-50 px-2 py-1 text-xs">{family} · {count}</span>
              {/each}
            </div>
          {:else}
            <div class="text-zinc-500">No family counts available.</div>
          {/if}
          {#if reviewSummary.focus_candidate_only_note}
            <div class="mt-3 rounded border border-amber-200 bg-amber-50 px-3 py-2 text-xs text-amber-900">
              {reviewSummary.focus_candidate_only_note}
            </div>
          {/if}
        </div>
      </div>
    </section>

    <div class="grid gap-6 xl:grid-cols-3">
      <section class="rounded border border-zinc-200 bg-white p-4">
        <h2 class="mb-3 text-lg font-semibold">Promoted relations</h2>
        {#if topPromoted.length}
          <ul class="space-y-3 text-sm">
            {#each topPromoted as row}
              <li class="rounded border border-zinc-100 bg-zinc-50 p-3">
                <div class="font-medium">{row.subject.canonical_label} → {row.predicate_key} → {row.object.canonical_label}</div>
                <div class="mt-1 text-xs text-zinc-600">{row.event_id} · {row.confidence_tier}</div>
              </li>
            {/each}
          </ul>
        {:else}
          <p class="text-sm text-zinc-500">No promoted relations.</p>
        {/if}
      </section>

      <section class="rounded border border-zinc-200 bg-white p-4">
        <h2 class="mb-3 text-lg font-semibold">Candidate-only relations</h2>
        {#if topCandidate.length}
          <ul class="space-y-3 text-sm">
            {#each topCandidate as row}
              <li class="rounded border border-amber-100 bg-amber-50 p-3">
                <div class="font-medium">{row.subject.canonical_label} → {row.predicate_key} → {row.object.canonical_label}</div>
                <div class="mt-1 text-xs text-zinc-600">{row.event_id} · {row.confidence_tier}</div>
              </li>
            {/each}
          </ul>
        {:else}
          <p class="text-sm text-zinc-500">No candidate-only relations.</p>
        {/if}
      </section>

      <section class="rounded border border-zinc-200 bg-white p-4">
        <h2 class="mb-3 text-lg font-semibold">Unresolved mentions</h2>
        {#if unresolved.length}
          <ul class="space-y-3 text-sm">
            {#each unresolved as row}
              <li class="rounded border border-zinc-100 bg-zinc-50 p-3">
                <div class="font-medium">{row.surface_text}</div>
                <div class="mt-1 text-xs text-zinc-600">{row.event_id} · {row.resolution_rule}</div>
              </li>
            {/each}
          </ul>
        {:else}
          <p class="text-sm text-zinc-500">No unresolved mentions.</p>
        {/if}
      </section>
    </div>

    <div class="mt-6 grid gap-6 xl:grid-cols-2">
      <section class="rounded border border-zinc-200 bg-white p-4">
        <h2 class="mb-3 text-lg font-semibold">Top entities</h2>
        {#if perEntity.length}
          <ul class="space-y-3 text-sm">
            {#each perEntity as row}
              <li class="rounded border border-zinc-100 bg-zinc-50 p-3">
                <div class="font-medium">{row.entity.canonical_label}</div>
                <div class="mt-1 text-xs text-zinc-600">
                  {row.entity.entity_kind} · promoted {row.promoted_relation_count}
                  {#if row.candidate_relation_count !== undefined}
                    · candidate {row.candidate_relation_count}
                  {/if}
                </div>
              </li>
            {/each}
          </ul>
        {:else}
          <p class="text-sm text-zinc-500">No per-entity summary available.</p>
        {/if}
      </section>

      <section class="rounded border border-zinc-200 bg-white p-4">
        <h2 class="mb-3 text-lg font-semibold">Reviewed linkage summary</h2>
        {#if data.reviewedLinkage}
          <div class="space-y-3 text-sm">
            <div class="rounded border border-zinc-100 bg-zinc-50 p-3">
              <div class="font-medium">{data.reviewedLinkage.label}</div>
              <div class="mt-1 text-xs text-zinc-600">
                {perSeed.length} seeds · {unmatchedSeeds.length} unmatched · {ambiguousEvents.length} ambiguous events
              </div>
            </div>
            {#if unmatchedSeeds.length}
              <div>
                <div class="mb-1 text-xs uppercase text-zinc-500">Unmatched seeds</div>
                <div class="flex flex-wrap gap-2">
                  {#each unmatchedSeeds.slice(0, 12) as seedId}
                    <span class="rounded border border-zinc-200 bg-white px-2 py-1 text-xs">{seedId}</span>
                  {/each}
                </div>
              </div>
            {:else}
              <p class="text-sm text-zinc-500">All reviewed seeds matched at least one event.</p>
            {/if}
          </div>
        {:else}
          <p class="text-sm text-zinc-500">No reviewed linkage summary for this corpus.</p>
        {/if}
      </section>
    </div>

    {#if perSeed.length}
      <section class="mt-6 rounded border border-zinc-200 bg-white p-4">
        <h2 class="mb-3 text-lg font-semibold">{data.reviewedLinkage?.label ?? 'Reviewed seed coverage'}</h2>
        <div class="overflow-x-auto">
          <table class="min-w-full text-left text-sm">
            <thead class="border-b border-zinc-200 text-zinc-600">
              <tr>
                <th class="px-3 py-2 font-medium">Seed</th>
                <th class="px-3 py-2 font-medium">Matched</th>
                <th class="px-3 py-2 font-medium">Candidates</th>
              </tr>
            </thead>
            <tbody>
              {#each perSeed as row}
                <tr class="border-b border-zinc-100">
                  <td class="px-3 py-2">{row.seed_id}</td>
                  <td class="px-3 py-2">{row.matched_count}</td>
                  <td class="px-3 py-2">{row.candidate_count}</td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
      </section>
    {/if}
  {/if}
</div>
