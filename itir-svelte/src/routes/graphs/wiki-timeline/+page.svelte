<script lang="ts">
  import BipartiteGraph, { type GraphEdge, type GraphNode } from '$lib/ui/BipartiteGraph.svelte';
  import Panel from '$lib/ui/Panel.svelte';

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
    error: string | null;
  };

  let bucket: 'year' | 'month' = 'month';
  let topN = 140;

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
</script>

<div class="space-y-4 p-6">
  <Panel>
    <div class="text-xs uppercase tracking-[0.28em] text-ink-800/70">Wiki timeline (GWB)</div>
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
    </div>
  </Panel>

  {#if data.error}
    <Panel tone="danger">
      <div class="text-xs uppercase tracking-[0.28em] text-red-800/80">Load error</div>
      <pre class="mt-3 whitespace-pre-wrap font-mono text-xs text-ink-950">{data.error}</pre>
    </Panel>
  {/if}

  <BipartiteGraph left={left} right={right} edges={edges} width={1200} height={820} />

  <Panel>
    <div class="text-xs uppercase tracking-[0.28em] text-ink-800/70">Notes</div>
    <div class="mt-2 text-xs text-ink-800/70">
      This view is a pre-graph substrate: date anchors extracted from prose (explicit month/day/year when present). No causality, authority, or SL/SB commitments.
    </div>
  </Panel>
</div>

