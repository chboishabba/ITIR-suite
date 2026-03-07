<script lang="ts">
  import { onMount, tick } from 'svelte';
  import type { TextDebugAnchor, TextDebugEvent } from '$lib/semantic/textDebug';

  export let events: TextDebugEvent[] = [];
  export let unavailableReason: string | null = null;

  let selectedEventId = '';
  let hoveredTokenIndex: number | null = null;
  let pinnedTokenIndex: number | null = null;
  let pinnedEventId: string | null = null;
  let containerEl: HTMLDivElement | null = null;
  let tokenEls: Array<HTMLButtonElement | null> = [];
  let tokenCenters: Array<{ x: number; y: number } | null> = [];
  let overlayWidth = 0;
  let overlayHeight = 0;
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
    activeTokenIndex === null || !selectedEvent
      ? []
      : selectedEvent.relations.filter((relation) => relation.anchors.some((anchor) => anchorContains(anchor, activeTokenIndex as number)));

  $: if (selectedEvent) {
    tokenEls = [];
    hoveredTokenIndex = null;
    if (pinnedEventId && pinnedEventId !== selectedEvent.eventId) {
      pinnedTokenIndex = null;
      pinnedEventId = null;
    }
    void measure();
  }

  function clearPinned(): void {
    pinnedTokenIndex = null;
    pinnedEventId = null;
  }

  function togglePinned(tokenIndex: number): void {
    if (pinnedEventId === selectedEvent?.eventId && pinnedTokenIndex === tokenIndex) {
      clearPinned();
      return;
    }
    pinnedEventId = selectedEvent?.eventId ?? null;
    pinnedTokenIndex = tokenIndex;
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
            {pinnedTokenIndex !== null ? 'pinned' : 'hover mode'}
          </span>
          {#if pinnedTokenIndex !== null}
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
                    : 'bg-white text-ink-950 ring-1 ring-ink-950/8 hover:bg-sky-50 hover:ring-sky-300'
                }`}
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
              <li class="rounded-xl border border-ink-950/10 bg-white p-3">
                <div class="flex items-center gap-2">
                  <span class="inline-block h-2.5 w-2.5 rounded-full" style={`background:${relation.color}; opacity:${relation.opacity};`}></span>
                  <span class="font-medium">{relation.displayLabel}</span>
                </div>
                <div class="mt-1 text-xs text-ink-800/65">
                  {relation.family} · {relation.confidenceTier} · {relation.promotionStatus}
                </div>
                <div class="mt-2 flex flex-wrap gap-2 text-xs">
                  {#each relation.anchors as anchor}
                    <span class="rounded-full border border-ink-950/10 bg-zinc-50 px-2 py-1">
                      {anchor.role}: {anchor.label} · {anchor.source}
                    </span>
                  {/each}
                </div>
              </li>
            {/each}
          </ul>
        {:else}
          <p class="text-sm text-ink-800/60">Hover a token that belongs to a subject, predicate, or object anchor. Click to pin the current arc set.</p>
        {/if}
      </div>
    </div>
  {/if}
</section>
