<script lang="ts">
  import Panel from '$lib/ui/Panel.svelte';
  import LayeredGraph, { type LayerNode, type LayeredEdge } from '$lib/ui/LayeredGraph.svelte';

  export let data: {
    payload: {
      root_actor: { label: string; surname: string };
      events: Array<{
        event_id: string;
        anchor: { year: number; month: number | null; day: number | null; precision: string; text: string; kind: string };
        section: string;
        text: string;
        actors: Array<{ label: string; resolved: string; role: string; source: string }>;
        action: string | null;
        objects: Array<{ title: string; source: string }>;
        purpose: string | null;
        warnings: string[];
      }>;
    };
    relPath: string;
    error: string | null;
  };

  let selectedId: string | null = null;

  type TimeGranularity = 'auto' | 'year' | 'month' | 'day';
  let timeGranularity: TimeGranularity = 'auto';

  function fmtTime(a: { year: number; month: number | null; day: number | null; precision: string }): string {
    const y = a.year || 0;
    const m = a.month ?? null;
    const d = a.day ?? null;
    if (a.precision === 'day' && m && d) return `${y}-${String(m).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
    if (a.precision === 'month' && m) return `${y}-${String(m).padStart(2, '0')}`;
    return String(y);
  }

  function timeLayersForEvent(
    eventId: string,
    a: { year: number; month: number | null; day: number | null; precision: string; text: string }
  ): { layers: Array<{ id: string; title: string; nodes: LayerNode[] }>; edges: LayeredEdge[]; attachId: string } {
    const y = a.year || 0;
    const m = a.month ?? null;
    const d = a.day ?? null;

    const want = (g: TimeGranularity): TimeGranularity => {
      if (g !== 'auto') return g;
      if (a.precision === 'day') return 'day';
      if (a.precision === 'month') return 'month';
      return 'year';
    };

    const g = want(timeGranularity);

    const yearNode = node(`time:${eventId}:y:${y}`, String(y), '#e8f4ff', a.text);
    const monthNode =
      m && (g === 'month' || g === 'day')
        ? node(`time:${eventId}:m:${y}-${String(m).padStart(2, '0')}`, `${y}-${String(m).padStart(2, '0')}`, '#e8f4ff', a.text)
        : null;
    const dayNode =
      m && d && g === 'day'
        ? node(
            `time:${eventId}:d:${y}-${String(m).padStart(2, '0')}-${String(d).padStart(2, '0')}`,
            `${y}-${String(m).padStart(2, '0')}-${String(d).padStart(2, '0')}`,
            '#e8f4ff',
            a.text
          )
        : null;

    const layers: Array<{ id: string; title: string; nodes: LayerNode[] }> = [{ id: 'year', title: 'Year', nodes: [yearNode] }];
    if (g === 'month' || g === 'day') layers.push({ id: 'month', title: 'Month', nodes: [monthNode ?? node('time:none:m', '(none)', '#ffffff')] });
    if (g === 'day') layers.push({ id: 'day', title: 'Day', nodes: [dayNode ?? node('time:none:d', '(none)', '#ffffff')] });

    const edges: LayeredEdge[] = [];
    if (monthNode) edges.push({ from: yearNode.id, to: monthNode.id, label: 'in' });
    if (monthNode && dayNode) edges.push({ from: monthNode.id, to: dayNode.id, label: 'on' });

    const attachId = dayNode?.id ?? monthNode?.id ?? yearNode.id;
    return { layers, edges, attachId };
  }

  $: events = data.payload.events ?? [];
  $: {
    const first = events[0];
    if (!selectedId && first) selectedId = first.event_id;
  }
  $: selected = selectedId ? events.find((e) => e.event_id === selectedId) ?? null : null;

  function node(id: string, label: string, color: string, tooltip?: string): LayerNode {
    const short = label.length > 54 ? label.slice(0, 54) + '...' : label;
    return { id, label: short, fullLabel: label, color, tooltip: tooltip ?? label };
  }

  $: graph = (() => {
    if (!selected) return { layers: [], edges: [] as LayeredEdge[] };

    const time = timeLayersForEvent(selected.event_id, selected.anchor);

    const requesters = selected.actors.filter((a) => a.role === 'requester');
    const subjects = selected.actors.filter((a) => a.role !== 'requester');

    const requesterNodes = requesters.map((a) => node(`req:${a.resolved}`, a.resolved, '#e9d5ff', `source=${a.source}`));
    const subjectNodes = subjects.map((a) => node(`sub:${a.resolved}`, a.resolved, '#bbf7d0', `source=${a.source}`));

    const actionText = selected.action ?? '(no action matched)';
    const actionNodes = [node(`act:${selected.event_id}`, actionText, '#fde68a')];

    const objNodes = (selected.objects ?? []).map((o) => node(`obj:${o.title}`, o.title, '#f6f6f6', `source=${o.source}`));
    const purposeNodes = selected.purpose ? [node(`pur:${selected.event_id}`, selected.purpose, '#fef3c7')] : [];

    const layers = [
      ...time.layers,
      { id: 'request', title: 'Requester', nodes: requesterNodes.length ? requesterNodes : [node('req:none', '(none)', '#ffffff')] },
      { id: 'subjects', title: 'Subjects', nodes: subjectNodes.length ? subjectNodes : [node('sub:none', '(none)', '#ffffff')] },
      { id: 'action', title: 'Action', nodes: actionNodes },
      { id: 'objects', title: 'Objects', nodes: objNodes.length ? objNodes : [node('obj:none', '(none)', '#ffffff')] },
      { id: 'purpose', title: 'Purpose', nodes: purposeNodes.length ? purposeNodes : [node('pur:none', '(none)', '#ffffff')] }
    ];

    const edges: LayeredEdge[] = [];
    const actionId = actionNodes[0]?.id ?? 'act:none';
    edges.push(...time.edges);
    edges.push({ from: time.attachId, to: actionId, label: 'at' });
    for (const r of requesterNodes) edges.push({ from: r.id, to: actionId, label: 'request' });
    for (const s of subjectNodes) edges.push({ from: s.id, to: actionId, label: 'do' });
    for (const o of objNodes) edges.push({ from: actionId, to: o.id, label: 'object' });
    for (const p of purposeNodes) edges.push({ from: actionId, to: p.id, label: 'purpose' });

    return { layers, edges };
  })();
</script>

<div class="space-y-4 p-6">
  <Panel>
    <div class="text-xs uppercase tracking-[0.28em] text-ink-800/70">Wiki timeline: actor/action/object</div>
    <div class="mt-2 text-sm text-ink-950">
      Source: <span class="font-mono text-xs">{data.relPath}</span>
    </div>
    <div class="mt-2 text-xs text-ink-800/60">
      Sentence-local extraction. Non-causal. Non-authoritative.
    </div>
  </Panel>

  {#if data.error}
    <Panel tone="danger">
      <div class="text-xs uppercase tracking-[0.28em] text-red-800/80">Load error</div>
      <pre class="mt-3 whitespace-pre-wrap font-mono text-xs text-ink-950">{data.error}</pre>
    </Panel>
  {/if}

  <div class="grid grid-cols-1 gap-4 lg:grid-cols-[360px_1fr]">
    <Panel>
      <div class="text-xs uppercase tracking-[0.28em] text-ink-800/70">Events</div>
      <div class="mt-3 max-h-[560px] overflow-auto">
        {#each events as e (e.event_id)}
          <button
            class="mb-2 w-full rounded-lg border px-3 py-2 text-left text-xs transition hover:border-ink-950/30 hover:bg-ink-950/[0.02] {e.event_id===selectedId ? 'border-ink-950/35 bg-ink-950/[0.03]' : 'border-ink-950/10 bg-white'}"
            on:click={() => (selectedId = e.event_id)}
          >
            <div class="font-mono text-[10px] text-ink-800/60">{fmtTime(e.anchor)} {e.event_id}</div>
            <div class="mt-1 text-ink-950">{e.text.length > 140 ? e.text.slice(0, 140) + '...' : e.text}</div>
            {#if e.warnings?.length}
              <div class="mt-1 font-mono text-[10px] text-amber-900/70">warnings: {e.warnings.join(', ')}</div>
            {/if}
          </button>
        {/each}
      </div>
    </Panel>

    <div class="space-y-4">
      {#if selected}
        <Panel>
          <div class="text-xs uppercase tracking-[0.28em] text-ink-800/70">Selected</div>
          <div class="mt-2 text-sm text-ink-950">{selected.text}</div>
          <div class="mt-2 text-xs text-ink-800/60">
            {selected.anchor.text} | section: <span class="font-mono">{selected.section}</span>
          </div>
          <div class="mt-4 flex flex-wrap items-center gap-2 text-xs text-ink-950">
            <div class="font-mono text-[10px] uppercase tracking-[0.20em] text-ink-800/70">Time view</div>
            <button
              class="rounded-md border px-2 py-1 font-mono text-[11px] {timeGranularity==='auto' ? 'border-ink-950/40 bg-ink-950/[0.04]' : 'border-ink-950/10 bg-white hover:border-ink-950/25 hover:bg-ink-950/[0.02]'}"
              on:click={() => (timeGranularity = 'auto')}
            >
              auto
            </button>
            <button
              class="rounded-md border px-2 py-1 font-mono text-[11px] {timeGranularity==='year' ? 'border-ink-950/40 bg-ink-950/[0.04]' : 'border-ink-950/10 bg-white hover:border-ink-950/25 hover:bg-ink-950/[0.02]'}"
              on:click={() => (timeGranularity = 'year')}
            >
              year
            </button>
            <button
              class="rounded-md border px-2 py-1 font-mono text-[11px] {timeGranularity==='month' ? 'border-ink-950/40 bg-ink-950/[0.04]' : 'border-ink-950/10 bg-white hover:border-ink-950/25 hover:bg-ink-950/[0.02]'}"
              on:click={() => (timeGranularity = 'month')}
            >
              month
            </button>
            <button
              class="rounded-md border px-2 py-1 font-mono text-[11px] {timeGranularity==='day' ? 'border-ink-950/40 bg-ink-950/[0.04]' : 'border-ink-950/10 bg-white hover:border-ink-950/25 hover:bg-ink-950/[0.02]'}"
              on:click={() => (timeGranularity = 'day')}
            >
              day
            </button>
          </div>
        </Panel>

        <LayeredGraph layers={graph.layers} edges={graph.edges} />
      {/if}
    </div>
  </div>
</div>
