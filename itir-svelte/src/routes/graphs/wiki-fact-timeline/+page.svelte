<script lang="ts">
  import Panel from '$lib/ui/Panel.svelte';
  import LayeredGraph, { type LayerNode, type LayeredEdge } from '$lib/ui/LayeredGraph.svelte';

  export let data: {
    payload: {
      root_actor: { label: string; surname: string };
      parser: any;
      facts: Array<{
        fact_id: string;
        event_id: string;
        anchor: { year: number; month: number | null; day: number | null; precision: string; text: string; kind: string };
        party: string;
        subjects: string[];
        action: string | null;
        objects: string[];
        purpose: string | null;
        text: string;
        section: string;
      }>;
    };
    relPath: string;
    source?: string;
    error: string | null;
  };

  type TimeGranularity = 'year' | 'month' | 'day';
  let granularity: TimeGranularity = 'month';
  let maxFacts = 240;
  let maxParties = 12;
  let maxSubjects = 120;
  let maxObjects = 180;

  let selectedNodeId: string | null = null;

  function pad2(n: number): string {
    return String(n).padStart(2, '0');
  }
  function keyFromAnchor(
    a: { year: number; month: number | null; day: number | null; precision: string; kind: string },
    g: TimeGranularity
  ): string {
    const y = String(a.year || 0);
    if (g === 'year') return y;
    const m = a.month ? `${y}-${pad2(a.month)}` : y;
    if (g === 'month') return m;
    return a.month && a.day ? `${m}-${pad2(a.day)}` : m;
  }
  function node(id: string, label: string, color: string, tooltip?: string): LayerNode {
    const short = label.length > 72 ? label.slice(0, 72) + '...' : label;
    return { id, label: short, fullLabel: label, color, tooltip: tooltip ?? label };
  }
  function uniq(xs: string[]): string[] {
    return Array.from(new Set(xs.map((x) => String(x || '').trim()).filter(Boolean)));
  }

  $: factsAll = data.payload.facts ?? [];
  $: facts = factsAll.slice(0, Math.max(20, Math.min(factsAll.length, Math.floor(maxFacts))));

  $: graph = (() => {
    const partyCounts = new Map<string, number>();
    const subCounts = new Map<string, number>();
    const objCounts = new Map<string, number>();
    const timeNodes = new Map<string, LayerNode>();
    const actionNodes: LayerNode[] = [];
    const edges: LayeredEdge[] = [];

    for (const f of facts) {
      if (f.party) partyCounts.set(f.party, (partyCounts.get(f.party) ?? 0) + 1);
      for (const s of f.subjects ?? []) subCounts.set(s, (subCounts.get(s) ?? 0) + 1);
      for (const o of f.objects ?? []) objCounts.set(o, (objCounts.get(o) ?? 0) + 1);
    }

    const top = (m: Map<string, number>, n: number) =>
      Array.from(m.entries())
        .sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))
        .slice(0, Math.max(1, Math.floor(n)));
    const topParties = top(partyCounts, maxParties);
    const topSubs = top(subCounts, maxSubjects);
    const topObjs = top(objCounts, maxObjects);

    const partySet = new Set(topParties.map(([k]) => k));
    const subSet = new Set(topSubs.map(([k]) => k));
    const objSet = new Set(topObjs.map(([k]) => k));

    const partyNodes = topParties.map(([k, c]) => node(`pty:${k}`, `${k} (${c})`, '#efe7ff'));
    const subNodes = topSubs.map(([k, c]) => node(`sub:${k}`, `${k} (${c})`, '#bbf7d0'));
    const objNodes = topObjs.map(([k, c]) => node(`obj:${k}`, `${k} (${c})`, '#f5f5f5'));

    for (const f of facts) {
      const t = keyFromAnchor(f.anchor, granularity);
      const tid = `time:${t}`;
      if (!timeNodes.has(tid)) timeNodes.set(tid, node(tid, t, '#e8f4ff'));
      const action = f.action ?? '(no action)';
      const subjHead = f.subjects?.[0] ?? '(no subject)';
      const aid = `fact:${f.fact_id}`;
      actionNodes.push(node(aid, `${subjHead} -> ${action}`, '#fde68a', `${f.fact_id} | ${f.section}`));
      edges.push({ from: tid, to: aid });
      if (f.party && partySet.has(f.party)) edges.push({ from: `pty:${f.party}`, to: aid });
      for (const s of uniq(f.subjects ?? [])) if (subSet.has(s)) edges.push({ from: `sub:${s}`, to: aid });
      for (const o of uniq(f.objects ?? [])) if (objSet.has(o)) edges.push({ from: aid, to: `obj:${o}` });
    }

    return {
      layers: [
        { id: 'time', title: 'Time', nodes: Array.from(timeNodes.values()).sort((a, b) => a.id.localeCompare(b.id)) },
        { id: 'party', title: 'Party', nodes: partyNodes.length ? partyNodes : [node('pty:none', '(none)', '#fff')] },
        { id: 'sub', title: 'Subjects', nodes: subNodes.length ? subNodes : [node('sub:none', '(none)', '#fff')] },
        { id: 'act', title: 'Facts', nodes: actionNodes.length ? actionNodes : [node('fact:none', '(none)', '#fff')] },
        { id: 'obj', title: 'Objects', nodes: objNodes.length ? objNodes : [node('obj:none', '(none)', '#fff')] }
      ],
      edges
    };
  })();

  $: selectedFacts = (() => {
    if (!selectedNodeId) return [] as typeof facts;
    if (selectedNodeId.startsWith('fact:')) {
      const id = selectedNodeId.slice('fact:'.length);
      return facts.filter((f) => f.fact_id === id);
    }
    if (selectedNodeId.startsWith('time:')) {
      const key = selectedNodeId.slice('time:'.length);
      return facts.filter((f) => keyFromAnchor(f.anchor, granularity) === key);
    }
    if (selectedNodeId.startsWith('pty:')) {
      const key = selectedNodeId.slice('pty:'.length);
      return facts.filter((f) => (f.party || '') === key);
    }
    if (selectedNodeId.startsWith('sub:')) {
      const key = selectedNodeId.slice('sub:'.length);
      return facts.filter((f) => (f.subjects || []).includes(key));
    }
    if (selectedNodeId.startsWith('obj:')) {
      const key = selectedNodeId.slice('obj:'.length);
      return facts.filter((f) => (f.objects || []).includes(key));
    }
    return [] as typeof facts;
  })();
</script>

<div class="space-y-4 p-6">
  <Panel>
    <div class="text-xs uppercase tracking-[0.28em] text-ink-800/70">Fact timeline</div>
    <div class="mt-2 text-sm text-ink-950">
      Source: <span class="font-mono text-xs">{data.relPath}</span>
    </div>
    <div class="mt-2 text-xs text-ink-800/60">
      Linearized fact rows from sentence-local extraction. Non-causal. Non-authoritative.
    </div>

    <div class="mt-4 flex flex-wrap items-center gap-3 text-sm">
      <label class="flex items-center gap-2">
        <span class="text-ink-800/70">Dataset</span>
        <select
          class="rounded-md border border-ink-950/15 bg-white px-2 py-1 text-sm"
          value={data.source ?? 'hca'}
          on:change={(e) => {
            const v = (e.currentTarget as HTMLSelectElement).value;
            window.location.href = `/graphs/wiki-fact-timeline?source=${encodeURIComponent(v)}`;
          }}
        >
          <option value="hca">hca</option>
          <option value="gwb">gwb</option>
          <option value="legal">legal</option>
          <option value="legal_follow">legal_follow</option>
        </select>
      </label>
      <label class="flex items-center gap-2">
        <span class="text-ink-800/70">Time</span>
        <select bind:value={granularity} class="rounded-md border border-ink-950/15 bg-white px-2 py-1 text-sm">
          <option value="year">Year</option>
          <option value="month">Month</option>
          <option value="day">Day</option>
        </select>
      </label>
      <label class="flex items-center gap-2">
        <span class="text-ink-800/70">Facts</span>
        <input type="number" min="20" max={factsAll.length} step="10" bind:value={maxFacts} class="w-24 rounded-md border border-ink-950/15 px-2 py-1 font-mono text-xs" />
      </label>
      <a
        class="rounded-md border border-ink-950/15 px-2 py-1 text-xs text-ink-950 hover:border-ink-950/30 hover:bg-ink-950/[0.03]"
        href={`/graphs/wiki-timeline-aoo-all?source=${encodeURIComponent(data.source ?? 'hca')}`}
      >
        Open AAO-all
      </a>
    </div>
  </Panel>

  {#if data.error}
    <Panel tone="danger">
      <div class="text-xs uppercase tracking-[0.28em] text-red-800/80">Load error</div>
      <pre class="mt-3 whitespace-pre-wrap font-mono text-xs text-ink-950">{data.error}</pre>
    </Panel>
  {/if}

  <LayeredGraph
    layers={graph.layers}
    edges={graph.edges}
    width={1700}
    height={920}
    on:nodeSelect={(e) => (selectedNodeId = (e as CustomEvent<{ nodeId: string }>).detail.nodeId)}
  />

  <Panel>
    <div class="text-xs uppercase tracking-[0.28em] text-ink-800/70">Context</div>
    {#if !selectedNodeId}
      <div class="mt-2 text-xs text-ink-800/70">Click a node to inspect matching linearized facts.</div>
    {:else if !selectedFacts.length}
      <div class="mt-2 text-xs text-ink-800/70">No facts for current selection.</div>
    {:else}
      <div class="mt-2 max-h-[340px] overflow-auto rounded-lg border border-ink-950/10 bg-white">
        {#each selectedFacts.slice(0, 120) as f (f.fact_id)}
          <div class="border-b border-ink-950/10 p-3 last:border-b-0">
            <div class="flex flex-wrap items-center justify-between gap-2">
              <div class="font-mono text-[10px] text-ink-800/60">{keyFromAnchor(f.anchor, 'day')} {f.fact_id}</div>
              <div class="font-mono text-[10px] text-ink-800/60">event={f.event_id} section={f.section || '(n/a)'}</div>
            </div>
            <div class="mt-2 text-[11px] text-ink-950">
              {#if f.party}<span class="rounded bg-emerald-50 px-1.5 py-0.5 font-mono">{f.party}</span>{/if}
              {#each f.subjects as s}
                <span class="ml-1 rounded bg-emerald-100 px-1.5 py-0.5 font-mono">[{s}]</span>
              {/each}
              <span class="ml-1 rounded bg-amber-100 px-1.5 py-0.5 font-mono">[{f.action ?? '(no action)'}]</span>
              {#each f.objects as o}
                <span class="ml-1 rounded bg-slate-100 px-1.5 py-0.5 font-mono">[{o}]</span>
              {/each}
            </div>
            <div class="mt-2 text-sm text-ink-950">{f.text}</div>
          </div>
        {/each}
      </div>
    {/if}
  </Panel>
</div>

