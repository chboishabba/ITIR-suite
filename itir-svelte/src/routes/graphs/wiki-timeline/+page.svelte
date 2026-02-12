<script lang="ts">
  import BipartiteGraph, { type GraphEdge, type GraphNode } from '$lib/ui/BipartiteGraph.svelte';
  import Panel from '$lib/ui/Panel.svelte';
  import { afterUpdate } from 'svelte';

  export let data: {
    payload: {
      snapshot: { title: string | null; wiki: string | null; revid: number | null; source_url: string | null };
      events: Array<{
        event_id: string;
        anchor: { year: number; month: number | null; day: number | null; precision: string; text: string; kind: string };
        section: string;
        text: string;
        links: string[];
      }>;
    };
    relPath: string;
    source?: string;
    error: string | null;
  };

  let bucket: 'year' | 'month' = 'month';
  let topN = 140;
  let selectedNodeId: string | null = null;
  let showAllContextRows = false;
  let expandedContextIds = new Set<string>();
  let contextBox: HTMLDivElement | null = null;
  let lastScrollKey = '';

  function pad2(n: number): string {
    return String(n).padStart(2, '0');
  }

  function bucketKey(a: { year: number; month: number | null }, mode: 'year' | 'month'): string {
    const y = a.year || 9999;
    if (mode === 'year') return String(y);
    const m = a.month ?? 0;
    return `${y}-${pad2(m || 0)}`;
  }

  $: eventsAll = data.payload.events ?? [];
  $: events = eventsAll.slice(0, Math.max(20, Math.min(260, Math.floor(topN))));

  $: bucketCounts = (() => {
    const m = new Map<string, number>();
    for (const e of events) {
      const k = bucketKey(e.anchor, bucket);
      m.set(k, (m.get(k) ?? 0) + 1);
    }
    return m;
  })();

  $: left = Array.from(bucketCounts.entries())
    .sort((a, b) => a[0].localeCompare(b[0]))
    .map<GraphNode>(([k, c]) => ({
      id: `time:${k}`,
      label: `${k} (${c})`,
      color: '#e8f4ff',
      tooltip: 'Time bucket (non-authoritative)'
    }));

  $: right = events.map<GraphNode>((e) => {
    const label = e.text.length > 64 ? e.text.slice(0, 64) + '...' : e.text;
    return {
      id: `ev:${e.event_id}`,
      label,
      color: '#f6f6f6',
      tooltip: `${e.event_id} | ${e.anchor.text} | section=${e.section}`
    };
  });

  $: edges = events.map<GraphEdge>((e) => ({
    from: `time:${bucketKey(e.anchor, bucket)}`,
    to: `ev:${e.event_id}`,
    weight: 1
  }));

  $: contextRows = (() => {
    if (!selectedNodeId) return [] as typeof events;
    if (selectedNodeId.startsWith('ev:')) {
      const eventId = selectedNodeId.slice('ev:'.length);
      return events.filter((e) => e.event_id === eventId);
    }
    if (selectedNodeId.startsWith('time:')) {
      const key = selectedNodeId.slice('time:'.length);
      return events.filter((e) => bucketKey(e.anchor, bucket) === key);
    }
    return [] as typeof events;
  })();
  $: contextRowsShown = showAllContextRows ? contextRows : contextRows.slice(0, 80);

  function toggleContextExpand(eventId: string) {
    const next = new Set(expandedContextIds);
    if (next.has(eventId)) next.delete(eventId);
    else next.add(eventId);
    expandedContextIds = next;
  }

  function highlightParts(text: string, needle: string): Array<{ s: string; hit: boolean }> {
    const t = String(text ?? '');
    const n = String(needle ?? '').trim();
    if (!n) return [{ s: t, hit: false }];
    const lower = t.toLowerCase();
    const nl = n.toLowerCase();
    const out: Array<{ s: string; hit: boolean }> = [];
    let i = 0;
    while (i < t.length) {
      const j = lower.indexOf(nl, i);
      if (j < 0) {
        out.push({ s: t.slice(i), hit: false });
        break;
      }
      if (j > i) out.push({ s: t.slice(i, j), hit: false });
      out.push({ s: t.slice(j, j + n.length), hit: true });
      i = j + n.length;
    }
    return out.length ? out : [{ s: t, hit: false }];
  }

  $: contextNeedle = (() => {
    if (!selectedNodeId) return '';
    if (selectedNodeId.startsWith('time:')) return selectedNodeId.slice('time:'.length);
    return '';
  })();

  afterUpdate(() => {
    if (!contextBox || !selectedNodeId) return;
    const k = `${selectedNodeId}:${contextRowsShown[0]?.event_id ?? ''}`;
    if (!k || k === lastScrollKey) return;
    lastScrollKey = k;
    const first = contextRowsShown[0];
    if (!first) return;
    const el = contextBox.querySelector(`[data-ctx-id="${first.event_id}"]`);
    if (el && 'scrollIntoView' in el) (el as HTMLElement).scrollIntoView({ block: 'center' });
  });
</script>

<div class="space-y-4 p-6">
  <Panel>
    <div class="text-xs uppercase tracking-[0.28em] text-ink-800/70">Wiki timeline</div>
    <div class="mt-2 text-sm text-ink-950">
      Source: <span class="font-mono text-xs">{data.relPath}</span>
    </div>
    <div class="mt-2 text-xs text-ink-800/60">
      Snapshot: <span class="font-mono">{data.payload.snapshot.title ?? '(unknown)'}</span>
      {#if data.payload.snapshot.revid}
        <span class="ml-2 font-mono">revid={data.payload.snapshot.revid}</span>
      {/if}
    </div>

    <div class="mt-3 flex flex-wrap items-center gap-3 text-sm">
      <label class="flex items-center gap-2">
        <span class="text-ink-800/70">Source</span>
        <select
          class="rounded-md border border-ink-950/15 bg-white px-2 py-1 text-sm"
          value={data.source ?? 'gwb'}
          on:change={(e) => {
            const v = (e.currentTarget as HTMLSelectElement).value;
            window.location.href = `/graphs/wiki-timeline?source=${encodeURIComponent(v)}`;
          }}
        >
          <option value="gwb">gwb</option>
          <option value="hca">hca</option>
          <option value="legal">legal</option>
          <option value="legal_follow">legal_follow</option>
        </select>
      </label>
      <label class="flex items-center gap-2">
        <span class="text-ink-800/70">Bucket</span>
        <select bind:value={bucket} class="rounded-md border border-ink-950/15 bg-white px-2 py-1 text-sm">
          <option value="month">Month</option>
          <option value="year">Year</option>
        </select>
      </label>
      <label class="flex items-center gap-2">
        <span class="text-ink-800/70">Top N</span>
        <input
          type="number"
          min="20"
          max="260"
          step="10"
          bind:value={topN}
          class="w-24 rounded-md border border-ink-950/15 px-2 py-1 font-mono text-xs"
        />
      </label>
      <a
        class="rounded-md border border-ink-950/15 px-2 py-1 text-xs text-ink-950 hover:border-ink-950/30 hover:bg-ink-950/[0.03]"
        href={`/graphs/wiki-timeline-aoo?source=${encodeURIComponent(data.source ?? 'gwb')}`}
      >
        Open AAO
      </a>
      <a
        class="rounded-md border border-ink-950/15 px-2 py-1 text-xs text-ink-950 hover:border-ink-950/30 hover:bg-ink-950/[0.03]"
        href={`/graphs/wiki-timeline-aoo?source=${encodeURIComponent(data.source ?? 'gwb')}&view=step-ribbon`}
      >
        Open Step-Ribbon
      </a>
      <a
        class="rounded-md border border-ink-950/15 px-2 py-1 text-xs text-ink-950 hover:border-ink-950/30 hover:bg-ink-950/[0.03]"
        href={`/graphs/wiki-timeline-aoo-all?source=${encodeURIComponent(data.source ?? 'gwb')}`}
      >
        Open AAO-all
      </a>
      <a
        class="rounded-md border border-ink-950/15 px-2 py-1 text-xs text-ink-950 hover:border-ink-950/30 hover:bg-ink-950/[0.03]"
        href={`/graphs/wiki-fact-timeline?source=${encodeURIComponent(data.source ?? 'gwb')}`}
      >
        Open Fact Timeline
      </a>
    </div>
  </Panel>

  {#if data.error}
    <Panel tone="danger">
      <div class="text-xs uppercase tracking-[0.28em] text-red-800/80">Load error</div>
      <pre class="mt-3 whitespace-pre-wrap font-mono text-xs text-ink-950">{data.error}</pre>
    </Panel>
  {/if}

  <BipartiteGraph
    left={left}
    right={right}
    edges={edges}
    width={1200}
    height={820}
    on:nodeSelect={(e) => (selectedNodeId = (e as CustomEvent<{ nodeId: string }>).detail.nodeId)}
  />

  <Panel>
    <div class="flex flex-wrap items-center justify-between gap-3">
      <div class="text-xs uppercase tracking-[0.28em] text-ink-800/70">Context</div>
      <div class="text-[11px] font-mono text-ink-800/60">
        {#if selectedNodeId}
          selected: {selectedNodeId} | rows: {contextRows.length}
          {#if contextRows.length > 80}
            <label class="ml-2 inline-flex items-center gap-1 rounded border border-ink-950/10 bg-white px-2 py-0.5">
              <input type="checkbox" bind:checked={showAllContextRows} />
              <span>all rows ({contextRows.length})</span>
            </label>
          {/if}
        {:else}
          click a node to inspect matching timeline rows
        {/if}
      </div>
    </div>
    {#if selectedNodeId && contextRows.length}
      <div class="mt-3 max-h-[320px] overflow-auto rounded-lg border border-ink-950/10 bg-white" bind:this={contextBox}>
        {#each contextRowsShown as r (r.event_id)}
          {@const expanded = expandedContextIds.has(r.event_id)}
          <div class="border-b border-ink-950/10 p-3 last:border-b-0" data-ctx-id={r.event_id}>
            <button class="w-full text-left" on:click={() => toggleContextExpand(r.event_id)}>
              <div class="flex flex-wrap items-center justify-between gap-2">
                <div class="font-mono text-[10px] text-ink-800/60">{bucketKey(r.anchor, 'month')} {r.event_id}</div>
                <div class="font-mono text-[10px] text-ink-800/60">section={r.section} {expanded ? '[-]' : '[+]'}</div>
              </div>
            </button>
            <div class="mt-2 text-sm text-ink-950">
              {#if contextNeedle}
                {#each highlightParts(r.text, contextNeedle) as part, i (r.event_id + ':' + i)}
                  {#if part.hit}
                    <span class="rounded bg-amber-200/60 px-1">{part.s}</span>
                  {:else}
                    {part.s}
                  {/if}
                {/each}
              {:else}
                {r.text}
              {/if}
            </div>
            {#if expanded && r.links?.length}
              <div class="mt-2 text-[11px] text-ink-800/80">
                links ({r.links.length}):
                {#each r.links as l}
                  <span class="ml-1 mt-1 inline-block rounded bg-slate-100 px-1.5 py-0.5 font-mono text-[10px]">{l}</span>
                {/each}
              </div>
            {:else if r.links?.length}
              <div class="mt-2 text-[11px] text-ink-800/80">
                links ({r.links.length}):
                {#each r.links.slice(0, 12) as l}
                  <span class="ml-1 inline-block rounded bg-slate-100 px-1.5 py-0.5 font-mono text-[10px]">{l}</span>
                {/each}
                {#if r.links.length > 12}
                  <span class="ml-1 font-mono text-[10px] text-ink-800/60">+{r.links.length - 12} more (expand)</span>
                {/if}
              </div>
            {/if}
          </div>
        {/each}
      </div>
    {/if}
  </Panel>

  <Panel>
    <div class="text-xs uppercase tracking-[0.28em] text-ink-800/70">Notes</div>
    <div class="mt-2 text-xs text-ink-800/70">
      This view is a pre-graph substrate: date anchors extracted from prose (explicit month/day/year when present). No causality, authority, or SL/SB commitments.
    </div>
  </Panel>
</div>
