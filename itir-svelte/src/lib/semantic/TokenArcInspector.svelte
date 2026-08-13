<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { onMount, tick } from 'svelte';
  import type { TextDebugAnchor, TextDebugEvent } from '$lib/semantic/textDebug';

  export let events: TextDebugEvent[] = [];
  export let unavailableReason: string | null = null;
  export let selectedEventId = '';
  export let selectionRequest:
    | {
        requestKey: string;
        eventId: string;
        relationId: string;
        anchorKey: string | null;
      }
    | null = null;

  type DocumentHighlight = {
    key: string;
    charStart: number;
    charEnd: number;
    color: string;
    opacity: number;
    kind: 'active' | 'relation_peer' | 'echo';
    label: string;
    source: TextDebugAnchor['source'] | 'event_span';
    sourceArtifactId: string;
  };

  type ActiveSelectionPayload = {
    eventId: string;
    text: string;
    activeAnchorKey: string | null;
    activeRelationId: string | null;
    role: string | null;
    family: string | null;
    color: string | null;
    activeAnchorSource: TextDebugAnchor['source'] | null;
    sourceArtifactId: string | null;
    charStart: number | null;
    charEnd: number | null;
    provenanceSummary: {
      strongestSource: TextDebugAnchor['source'];
      counts: Record<string, number>;
      note: string;
    } | null;
    highlights: DocumentHighlight[];
  } | null;

  const dispatch = createEventDispatcher<{
    selectedEventChange: { eventId: string };
    activeSelectionChange: ActiveSelectionPayload;
  }>();

  let hoveredTokenIndex: number | null = null;
  let pinnedTokenIndex: number | null = null;
  let pinnedRelationId: string | null = null;
  let pinnedAnchorKey: string | null = null;
  let pinnedEventId: string | null = null;
  let containerEl: HTMLDivElement | null = null;
  let tokenEls: Array<HTMLButtonElement | null> = [];
  let tokenCenters: Array<{ x: number; y: number } | null> = [];
  let overlayWidth = 0;
  let overlayHeight = 0;
  let lastSelectionRequestKey = '';
  type HoverLink = {
    relationId: string;
    from: { x: number; y: number };
    to: { x: number; y: number };
    color: string;
    opacity: number;
    width: number;
    label: string;
    family: string;
    confidenceTier: string;
    promotionStatus: string;
    sourceAnchor: TextDebugAnchor;
  };

  $: if (!selectedEventId && events.length) {
    selectedEventId = events[0]?.eventId ?? '';
  }

  $: selectedEvent = events.find((event) => event.eventId === selectedEventId) ?? events[0] ?? null;
  $: activeTokenIndex = pinnedEventId === selectedEvent?.eventId && pinnedTokenIndex !== null ? pinnedTokenIndex : hoveredTokenIndex;

  async function measure(): Promise<void> {
    await tick();
    if (!containerEl || !selectedEvent) return;
    const box = containerEl.getBoundingClientRect();
    overlayWidth = Math.max(containerEl.clientWidth, Math.ceil(box.width));
    overlayHeight = Math.max(containerEl.scrollHeight, Math.ceil(box.height));
    tokenCenters = selectedEvent.tokens.map((token) => {
      const el = tokenEls[token.index];
      if (!el) return null;
      const rect = el.getBoundingClientRect();
      return {
        x: rect.left - box.left + rect.width / 2,
        y: rect.top - box.top + rect.height / 2
      };
    });
  }

  function anchorContains(anchor: { tokenStart: number; tokenEnd: number }, tokenIndex: number): boolean {
    return tokenIndex >= anchor.tokenStart && tokenIndex <= anchor.tokenEnd;
  }

  function anchorCenter(anchor: { tokenStart: number; tokenEnd: number }): { x: number; y: number } | null {
    const centers = tokenCenters.slice(anchor.tokenStart, anchor.tokenEnd + 1).filter(Boolean) as Array<{ x: number; y: number }>;
    if (!centers.length) return null;
    const sum = centers.reduce((acc, point) => ({ x: acc.x + point.x, y: acc.y + point.y }), { x: 0, y: 0 });
    return { x: sum.x / centers.length, y: sum.y / centers.length };
  }

  function arcPath(from: { x: number; y: number }, to: { x: number; y: number }): string {
    const dx = Math.abs(to.x - from.x);
    const midX = (from.x + to.x) / 2;
    const lift = Math.max(24, Math.min(120, dx * 0.35));
    const controlY = Math.min(from.y, to.y) - lift;
    return `M ${from.x} ${from.y} Q ${midX} ${controlY} ${to.x} ${to.y}`;
  }

  function formatCharSpan(anchor: TextDebugAnchor): string {
    return `${anchor.charStart}-${anchor.charEnd}`;
  }

  function hexToRgb(color: string): { r: number; g: number; b: number } | null {
    const raw = color.trim().replace('#', '');
    if (!/^[0-9a-fA-F]{6}$/.test(raw)) return null;
    return {
      r: Number.parseInt(raw.slice(0, 2), 16),
      g: Number.parseInt(raw.slice(2, 4), 16),
      b: Number.parseInt(raw.slice(4, 6), 16)
    };
  }

  function alphaColor(color: string, alpha: number): string {
    const rgb = hexToRgb(color);
    if (!rgb) return color;
    return `rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, ${Math.max(0, Math.min(1, alpha))})`;
  }

  function provenancePriority(source: TextDebugAnchor['source']): number {
    if (source === 'mention') return 3;
    if (source === 'receipt') return 2;
    return 1;
  }

  function provenanceTone(source: TextDebugAnchor['source']): string {
    if (source === 'mention') return 'border-emerald-200 bg-emerald-50 text-emerald-800';
    if (source === 'receipt') return 'border-sky-200 bg-sky-50 text-sky-800';
    return 'border-amber-200 bg-amber-50 text-amber-900';
  }

  function relationProvenanceSummary(relation: TextDebugEvent['relations'][number]): {
    strongestSource: TextDebugAnchor['source'];
    counts: Record<string, number>;
    note: string;
  } {
    const counts: Record<string, number> = { mention: 0, receipt: 0, label_fallback: 0 };
    for (const anchor of relation.anchors) {
      counts[anchor.source] = (counts[anchor.source] ?? 0) + 1;
    }
    const strongestSource =
      relation.anchors
        .slice()
        .sort((a, b) => provenancePriority(b.source) - provenancePriority(a.source))[0]?.source ?? 'label_fallback';
    const note =
      strongestSource === 'mention'
        ? 'mention-backed'
        : strongestSource === 'receipt'
          ? 'receipt-anchored'
          : 'fallback-anchored';
    return { strongestSource, counts, note };
  }

  $: hoverLinks = (
    activeTokenIndex === null || !selectedEvent
      ? []
      : selectedEvent.relations.flatMap((relation) => {
          const sourceAnchor = relation.anchors.find((anchor) => anchorContains(anchor, activeTokenIndex as number));
          if (!sourceAnchor) return [];
          const from = anchorCenter(sourceAnchor);
          if (!from) return [];
          return relation.anchors
            .filter((anchor) => anchor.key !== sourceAnchor.key)
            .map((anchor) => {
              const to = anchorCenter(anchor);
              if (!to) return null;
              return {
                relationId: relation.relationId,
                from,
                to,
                color: relation.color,
                opacity: relation.opacity,
                width: relation.promotionStatus === 'promoted' ? 2.4 : 1.5,
                label: `${relation.displayLabel}: ${sourceAnchor.label} -> ${anchor.label}`,
                family: relation.family,
                confidenceTier: relation.confidenceTier,
                promotionStatus: relation.promotionStatus,
                sourceAnchor
              };
            })
            .filter((value): value is HoverLink => Boolean(value));
        })
  ) as HoverLink[];

  $: hoveredRelations =
    !selectedEvent
      ? []
      : pinnedEventId === selectedEvent.eventId && pinnedRelationId
        ? selectedEvent.relations.filter((relation) => relation.relationId === pinnedRelationId)
        : activeTokenIndex === null
          ? []
          : selectedEvent.relations.filter((relation) => relation.anchors.some((anchor) => anchorContains(anchor, activeTokenIndex as number)));

  $: activeAnchorRef =
    !selectedEvent
      ? null
      : pinnedEventId === selectedEvent.eventId && pinnedRelationId
        ? (() => {
            const relation = selectedEvent.relations.find((row) => row.relationId === pinnedRelationId);
            if (!relation) return null;
            const anchor =
              relation.anchors.find((row) => row.key === pinnedAnchorKey)
              ?? relation.anchors.find((row) => row.role === 'predicate')
              ?? relation.anchors[0]
              ?? null;
            if (!anchor) return null;
            return {
              anchor,
              relation,
              family: relation.family,
              color: relation.color
            };
          })()
        : activeTokenIndex === null
          ? null
          : (() => {
          for (const relation of selectedEvent.relations) {
            const sourceAnchor = relation.anchors.find((anchor) => anchorContains(anchor, activeTokenIndex as number));
            if (sourceAnchor) {
              return {
                anchor: sourceAnchor,
                relation,
                family: relation.family,
                color: relation.color
              };
            }
          }
          return null;
        })();

  $: echoTokenStyles = (() => {
    const out = new Map<number, { background: string; ring: string; strength: number }>();
    if (!selectedEvent || !activeAnchorRef) return out;
    for (const relation of selectedEvent.relations) {
      if (relation.family !== activeAnchorRef.family) continue;
      for (const anchor of relation.anchors) {
        if (anchor.role !== activeAnchorRef.anchor.role) continue;
        if (anchor.key === activeAnchorRef.anchor.key) continue;
        const background = alphaColor(activeAnchorRef.color, Math.max(0.08, relation.opacity * 0.24));
        const ring = alphaColor(activeAnchorRef.color, Math.max(0.18, relation.opacity * 0.48));
        for (let tokenIndex = anchor.tokenStart; tokenIndex <= anchor.tokenEnd; tokenIndex += 1) {
          const current = out.get(tokenIndex);
          if (!current || relation.opacity > current.strength) {
            out.set(tokenIndex, { background, ring, strength: relation.opacity });
          }
        }
      }
    }
    return out;
  })();

  $: documentHighlights = (() => {
    const out = new Map<string, DocumentHighlight>();
    if (!selectedEvent || !activeAnchorRef) return [];
    for (const anchor of activeAnchorRef.relation.anchors) {
      out.set(anchor.key, {
        key: anchor.key,
        charStart: anchor.charStart,
        charEnd: anchor.charEnd,
        color: activeAnchorRef.color,
        opacity: anchor.key === activeAnchorRef.anchor.key ? Math.max(0.48, activeAnchorRef.relation.opacity) : Math.max(0.26, activeAnchorRef.relation.opacity * 0.7),
        kind: anchor.key === activeAnchorRef.anchor.key ? 'active' : 'relation_peer',
        label: anchor.label,
        source: anchor.source,
        sourceArtifactId: anchor.sourceArtifactId
      });
    }
    for (const relation of selectedEvent.relations) {
      if (relation.family !== activeAnchorRef.family) continue;
      for (const anchor of relation.anchors) {
        if (anchor.role !== activeAnchorRef.anchor.role) continue;
        if (out.has(anchor.key)) continue;
        out.set(anchor.key, {
          key: anchor.key,
          charStart: anchor.charStart,
          charEnd: anchor.charEnd,
          color: activeAnchorRef.color,
          opacity: Math.max(0.12, relation.opacity * 0.45),
          kind: 'echo',
          label: anchor.label,
          source: anchor.source,
          sourceArtifactId: anchor.sourceArtifactId
        });
      }
    }
    return Array.from(out.values());
  })();

  $: dispatch('activeSelectionChange', selectedEvent && activeAnchorRef ? {
    eventId: selectedEvent.eventId,
    text: selectedEvent.text,
    activeAnchorKey: activeAnchorRef.anchor.key,
    activeRelationId: activeAnchorRef.relation.relationId,
    role: activeAnchorRef.anchor.role,
    family: activeAnchorRef.family,
    color: activeAnchorRef.color,
    activeAnchorSource: activeAnchorRef.anchor.source,
    sourceArtifactId: activeAnchorRef.anchor.sourceArtifactId,
    charStart: activeAnchorRef.anchor.charStart,
    charEnd: activeAnchorRef.anchor.charEnd,
    provenanceSummary: relationProvenanceSummary(activeAnchorRef.relation),
    highlights: documentHighlights
  } : (selectedEvent ? {
    eventId: selectedEvent.eventId,
    text: selectedEvent.text,
    activeAnchorKey: null,
    activeRelationId: null,
    role: null,
    family: null,
    color: null,
    activeAnchorSource: null,
    sourceArtifactId: null,
    charStart: null,
    charEnd: null,
    provenanceSummary: null,
    highlights: []
  } : null));

  $: if (selectedEvent) {
    tokenEls = [];
    hoveredTokenIndex = null;
    if (pinnedEventId && pinnedEventId !== selectedEvent.eventId) {
      pinnedTokenIndex = null;
      pinnedRelationId = null;
      pinnedAnchorKey = null;
      pinnedEventId = null;
    }
    void measure();
  }

  $: if (
    selectionRequest
    && selectionRequest.requestKey
    && selectionRequest.requestKey !== lastSelectionRequestKey
    && events.some((event) => event.eventId === selectionRequest.eventId)
  ) {
    lastSelectionRequestKey = selectionRequest.requestKey;
    selectedEventId = selectionRequest.eventId;
    pinnedEventId = selectionRequest.eventId;
    pinnedRelationId = selectionRequest.relationId;
    pinnedAnchorKey = selectionRequest.anchorKey;
    pinnedTokenIndex = null;
    hoveredTokenIndex = null;
    dispatch('selectedEventChange', { eventId: selectionRequest.eventId });
    void measure();
  }

  function clearPinned(): void {
    pinnedTokenIndex = null;
    pinnedRelationId = null;
    pinnedAnchorKey = null;
    pinnedEventId = null;
  }

  function togglePinned(tokenIndex: number): void {
    if (pinnedEventId === selectedEvent?.eventId && pinnedTokenIndex === tokenIndex) {
      clearPinned();
      return;
    }
    pinnedEventId = selectedEvent?.eventId ?? null;
    pinnedTokenIndex = tokenIndex;
    pinnedRelationId = null;
    pinnedAnchorKey = null;
  }

  function pinRelation(relationId: string, preferredAnchorKey: string | null = null): void {
    if (pinnedEventId === selectedEvent?.eventId && pinnedRelationId === relationId) {
      clearPinned();
      return;
    }
    pinnedEventId = selectedEvent?.eventId ?? null;
    pinnedRelationId = relationId;
    pinnedAnchorKey = preferredAnchorKey;
    pinnedTokenIndex = null;
    hoveredTokenIndex = null;
  }

  onMount(() => {
    void measure();
    const onResize = () => void measure();
    window.addEventListener('resize', onResize);
    return () => window.removeEventListener('resize', onResize);
  });
</script>

<section class="rounded border border-ink-950/10 bg-white p-4">
  <div class="mb-3 flex flex-wrap items-center justify-between gap-3">
    <div>
      <h2 class="text-lg font-semibold">Token arc debugger</h2>
      <p class="text-sm text-ink-800/70">Hover a token anchor to draw relation arcs. Color tracks relation family; opacity tracks confidence.</p>
    </div>
    {#if events.length}
      <label class="flex items-center gap-2 text-sm">
        <span>Event</span>
        <select
          class="rounded border border-ink-950/15 bg-white px-3 py-2"
          bind:value={selectedEventId}
          on:change={() => {
            dispatch('selectedEventChange', { eventId: selectedEventId });
            clearPinned();
            void measure();
          }}
        >
          {#each events as event}
            <option value={event.eventId}>{event.eventId} · {event.relationCount} relations · {event.tokenCount} tokens</option>
          {/each}
        </select>
      </label>
    {/if}
  </div>

  {#if !events.length}
    <div class="rounded border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-900">
      {unavailableReason ?? 'No token-arc debug payload available.'}
    </div>
  {:else if selectedEvent}
    <div class="mb-3 flex flex-wrap gap-2 text-[11px] font-medium uppercase tracking-[0.16em] text-ink-800/65">
      <span class="rounded-full bg-sky-100 px-2 py-1 text-sky-800">review</span>
      <span class="rounded-full bg-emerald-100 px-2 py-1 text-emerald-800">authority</span>
      <span class="rounded-full bg-amber-100 px-2 py-1 text-amber-800">governance</span>
      <span class="rounded-full bg-rose-100 px-2 py-1 text-rose-800">conversation</span>
      <span class="rounded-full bg-violet-100 px-2 py-1 text-violet-800">state</span>
      <span class="rounded-full bg-zinc-100 px-2 py-1 text-zinc-700">opacity = confidence</span>
    </div>

    <div class="grid gap-4 xl:grid-cols-[minmax(0,1.7fr)_minmax(18rem,0.9fr)]">
      <div class="rounded-2xl border border-ink-950/10 bg-[radial-gradient(circle_at_top,rgba(191,219,254,0.28),transparent_42%),linear-gradient(180deg,rgba(248,250,252,0.96),rgba(255,255,255,1))] p-4">
        <div class="mb-2 flex flex-wrap items-center gap-2 text-xs text-ink-800/70">
          <span class="rounded-full border border-ink-950/10 bg-white px-2 py-1 font-mono">{selectedEvent.eventId}</span>
          <span>{selectedEvent.relationCount} arc-ready relations</span>
          <span>{selectedEvent.promotedCount} promoted</span>
          <span class={`rounded-full border px-2 py-1 ${pinnedTokenIndex !== null ? 'border-sky-300 bg-sky-50 text-sky-800' : 'border-ink-950/10 bg-white'}`}>
            {pinnedRelationId !== null ? 'relation pinned' : pinnedTokenIndex !== null ? 'token pinned' : 'hover mode'}
          </span>
          {#if pinnedTokenIndex !== null || pinnedRelationId !== null}
            <button
              type="button"
              class="rounded-full border border-ink-950/15 bg-white px-2 py-1 text-xs font-medium text-ink-900 hover:border-ink-950/30 hover:bg-ink-950/[0.03]"
              on:click={clearPinned}
            >
              Clear pin
            </button>
          {/if}
        </div>
        <div bind:this={containerEl} class="relative min-h-[12rem] rounded-xl border border-ink-950/10 bg-white/80 px-4 py-5 shadow-[inset_0_1px_0_rgba(255,255,255,0.8)]">
          <svg class="pointer-events-none absolute inset-0 h-full w-full overflow-visible">
            {#each hoverLinks as link}
              <path
                d={arcPath(link.from, link.to)}
                stroke={link.color}
                stroke-opacity={link.opacity}
                stroke-width={link.width}
                fill="none"
                stroke-linecap="round"
              />
            {/each}
          </svg>
          <div class="relative z-10 flex flex-wrap gap-x-1 gap-y-2 leading-8">
            {#each selectedEvent.tokens as token}
              <button
                type="button"
                bind:this={tokenEls[token.index]}
                class={`rounded-md px-1.5 py-0.5 font-mono text-[13px] transition ${
                  activeTokenIndex === token.index
                    ? 'bg-ink-950 text-white shadow-sm'
                    : echoTokenStyles.has(token.index)
                      ? 'text-ink-950 shadow-sm'
                      : 'bg-white text-ink-950 ring-1 ring-ink-950/8 hover:bg-sky-50 hover:ring-sky-300'
                }`}
                style={
                  activeTokenIndex === token.index || !echoTokenStyles.has(token.index)
                    ? undefined
                    : `background:${echoTokenStyles.get(token.index)?.background}; box-shadow: inset 0 0 0 1px ${echoTokenStyles.get(token.index)?.ring};`
                }
                on:mouseenter={() => {
                  if (pinnedTokenIndex !== null) return;
                  hoveredTokenIndex = token.index;
                  void measure();
                }}
                on:mouseleave={() => {
                  if (pinnedTokenIndex !== null) return;
                  hoveredTokenIndex = null;
                }}
                on:click={() => {
                  togglePinned(token.index);
                  void measure();
                }}
              >
                {token.text}
              </button>
            {/each}
          </div>
        </div>
      </div>

      <div class="rounded-2xl border border-ink-950/10 bg-zinc-50 p-4">
        <h3 class="mb-2 text-sm font-semibold uppercase tracking-[0.16em] text-ink-800/70">{pinnedTokenIndex !== null ? 'Pinned relations' : 'Hovered relations'}</h3>
        {#if hoveredRelations.length}
          <ul class="space-y-3 text-sm">
            {#each hoveredRelations as relation}
              {@const provenance = relationProvenanceSummary(relation)}
              <li class="rounded-xl border border-ink-950/10 bg-white p-3">
                <div class="flex items-center gap-2">
                  <span class="inline-block h-2.5 w-2.5 rounded-full" style={`background:${relation.color}; opacity:${relation.opacity};`}></span>
                  <span class="font-medium">{relation.displayLabel}</span>
                </div>
                <div class="mt-1 flex flex-wrap items-center gap-2 text-xs text-ink-800/65">
                  {relation.family} · {relation.confidenceTier} · {relation.promotionStatus}
                  <span class={`rounded-full border px-2 py-0.5 font-medium ${provenanceTone(provenance.strongestSource)}`}>{provenance.note}</span>
                </div>
                <div class="mt-2 flex flex-wrap gap-2 text-xs">
                  {#each relation.anchors as anchor}
                    <button
                      type="button"
                      class={`rounded-full border px-2 py-1 text-left ${
                        pinnedRelationId === relation.relationId && pinnedAnchorKey === anchor.key
                          ? 'border-sky-300 bg-sky-50 text-sky-900'
                          : 'border-ink-950/10 bg-zinc-50'
                      }`}
                      on:click={() => pinRelation(relation.relationId, anchor.key)}
                    >
                      {anchor.role}: {anchor.label} · {anchor.source}
                    </button>
                  {/each}
                </div>
                <div class="mt-2 flex flex-wrap gap-2 text-[11px] text-ink-800/70">
                  <span class="rounded-full border border-emerald-200 bg-emerald-50 px-2 py-1 text-emerald-800">mention {provenance.counts.mention ?? 0}</span>
                  <span class="rounded-full border border-sky-200 bg-sky-50 px-2 py-1 text-sky-800">receipt {provenance.counts.receipt ?? 0}</span>
                  <span class="rounded-full border border-amber-200 bg-amber-50 px-2 py-1 text-amber-900">fallback {provenance.counts.label_fallback ?? 0}</span>
                </div>
                <div class="mt-2 space-y-1 text-[11px] text-ink-800/60">
                  {#each relation.anchors as anchor}
                    <div>{anchor.role} span {formatCharSpan(anchor)} · {anchor.sourceArtifactId}</div>
                  {/each}
                </div>
                <div class="mt-3 flex flex-wrap gap-2">
                  <button
                    type="button"
                    class={`rounded-full border px-2 py-1 text-xs font-medium ${
                      pinnedRelationId === relation.relationId
                        ? 'border-sky-300 bg-sky-50 text-sky-900'
                        : 'border-ink-950/15 bg-white text-ink-900 hover:border-ink-950/30 hover:bg-ink-950/[0.03]'
                    }`}
                    on:click={() => pinRelation(relation.relationId, relation.anchors.find((anchor) => anchor.role === 'predicate')?.key ?? relation.anchors[0]?.key ?? null)}
                  >
                    {pinnedRelationId === relation.relationId ? 'Unpin relation' : 'Pin relation'}
                  </button>
                </div>
              </li>
            {/each}
          </ul>
        {:else}
          <p class="text-sm text-ink-800/60">Hover a token that belongs to a subject, predicate, or object anchor. Click a token to pin the current arc set, or pin a relation directly from this panel once visible. Matching same-role anchors in the same family will echo lightly in the token field.</p>
        {/if}
      </div>
    </div>
  {/if}
</section>
