<script lang="ts">
  import Panel from '$lib/ui/Panel.svelte';
  import LayeredGraph, { type LayerNode, type LayeredEdge } from '$lib/ui/LayeredGraph.svelte';

  export let data: {
    payload: {
      root_actor: { label: string; surname: string };
      parser?: any;
      events: Array<{
        event_id: string;
        anchor: { year: number; month: number | null; day: number | null; precision: string; text: string; kind: string };
        section: string;
        text: string;
        actors: Array<{ label: string; resolved: string; role: string; source: string }>;
        action: string | null;
        chains?: Array<{ from_step?: number; to_step?: number; to?: string; kind: string }>;
        span_candidates?: Array<{
          span_id: string;
          text: string;
          span_type: string;
          recurrence?: { seen_events: number };
          hygiene?: { view_score?: number; token_count?: number };
        }>;
        objects: Array<{
          title: string;
          source: string;
          resolver_hints?: Array<{ lane: string; kind: string; title: string; score: number }>;
        }>;
        purpose: string | null;
        warnings: string[];
      }>;
    };
    relPath: string;
    source?: string;
    error: string | null;
  };

  let selectedId: string | null = null;
  let showAllSpans = false;

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
  $: spanSorted =
    selected?.span_candidates?.slice().sort((a, b) => {
      const as = Number(a.hygiene?.view_score ?? 0);
      const bs = Number(b.hygiene?.view_score ?? 0);
      if (bs !== as) return bs - as;
      const ar = Number(a.recurrence?.seen_events ?? 0);
      const br = Number(b.recurrence?.seen_events ?? 0);
      if (br !== ar) return br - ar;
      const al = Number(a.hygiene?.token_count ?? 0);
      const bl = Number(b.hygiene?.token_count ?? 0);
      if (bl !== al) return bl - al;
      return String(a.text ?? '').localeCompare(String(b.text ?? ''));
    }) ?? [];
  $: spanShown = showAllSpans ? spanSorted : spanSorted.slice(0, 24);
  $: objectHintRows =
    selected?.objects?.map((o) => ({
      title: o.title,
      source: o.source,
      hints: (o.resolver_hints ?? []).slice().sort((a, b) => Number(b.score ?? 0) - Number(a.score ?? 0)).slice(0, 4)
    })) ?? [];

  function node(id: string, label: string, color: string, tooltip?: string): LayerNode {
    const short = label.length > 54 ? label.slice(0, 54) + '...' : label;
    return { id, label: short, fullLabel: label, color, tooltip: tooltip ?? label };
  }

  $: graph = (() => {
    if (!selected) return { layers: [], edges: [] as LayeredEdge[] };

    const time = timeLayersForEvent(selected.event_id, selected.anchor);

    const requesters = selected.actors.filter((a) => a.role === 'requester');

    const requesterNodes = requesters.map((a) => node(`req:${a.resolved}`, a.resolved, '#e9d5ff', `source=${a.source}`));

    const steps = Array.isArray((selected as any).steps) && (selected as any).steps.length
      ? ((selected as any).steps as Array<{ action: string; subjects: string[]; objects: string[]; purpose: string | null }>)
      : [{
          action: selected.action ?? '(no action matched)',
          subjects: selected.actors.filter((a) => a.role !== 'requester').map((a) => a.resolved),
          objects: (selected.objects ?? []).map((o) => o.title),
          purpose: selected.purpose ?? null
        }];

    const stepSubjectSet = new Set<string>();
    for (const s of steps) for (const sub of s.subjects ?? []) if (sub) stepSubjectSet.add(String(sub));
    const subjectNodes = (() => {
      if (!stepSubjectSet.size) {
        return selected.actors
          .filter((a) => a.role !== 'requester')
          .map((a) => node(`sub:${a.resolved}`, a.resolved, '#bbf7d0', `source=${a.source}`));
      }
      const out: LayerNode[] = [];
      for (const sub of stepSubjectSet) out.push(node(`sub:${sub}`, sub, '#bbf7d0'));
      return out;
    })();

    const actionNodes = steps.map((s, i) =>
      node(`act:${selected.event_id}:${i}`, s.action || '(no action matched)', '#fde68a')
    );

    // Objects/purpose are step-local when `steps[]` is present; fall back to legacy fields.
    const objSeen = new Set<string>();
    const objNodes: LayerNode[] = [];
    for (const s of steps) {
      for (const t of s.objects ?? []) {
        const title = String(t ?? '').trim();
        if (!title || objSeen.has(title)) continue;
        objSeen.add(title);
        objNodes.push(node(`obj:${title}`, title, '#f6f6f6'));
      }
    }
    if (!objNodes.length) {
      for (const o of selected.objects ?? []) {
        const title = String(o.title ?? '').trim();
        if (!title || objSeen.has(title)) continue;
        objSeen.add(title);
        objNodes.push(node(`obj:${title}`, title, '#f6f6f6', `source=${o.source}`));
      }
    }

    const purposeNodes: LayerNode[] = [];
    steps.forEach((s, i) => {
      if (s.purpose) purposeNodes.push(node(`pur:${selected.event_id}:${i}`, s.purpose, '#fef3c7'));
    });

    const layers = [
      ...time.layers,
      { id: 'request', title: 'Requester', nodes: requesterNodes.length ? requesterNodes : [node('req:none', '(none)', '#ffffff')] },
      { id: 'subjects', title: 'Subjects', nodes: subjectNodes.length ? subjectNodes : [node('sub:none', '(none)', '#ffffff')] },
      { id: 'action', title: 'Action', nodes: actionNodes.length ? actionNodes : [node('act:none', '(none)', '#ffffff')] },
      { id: 'objects', title: 'Objects', nodes: objNodes.length ? objNodes : [node('obj:none', '(none)', '#ffffff')] },
      { id: 'purpose', title: 'Purpose', nodes: purposeNodes.length ? purposeNodes : [node('pur:none', '(none)', '#ffffff')] }
    ];

    const edges: LayeredEdge[] = [];
    const firstActionId = actionNodes[0]?.id ?? 'act:none';
    edges.push(...time.edges);
    edges.push({ from: time.attachId, to: firstActionId, label: 'at' });
    for (const r of requesterNodes) edges.push({ from: r.id, to: firstActionId, label: 'request' });

    // Step-local wiring: connect only the subjects/objects that belong to that step when possible.
    steps.forEach((st, i) => {
      const aid = actionNodes[i]?.id ?? firstActionId;
      // If step subjects are explicit resolved strings, connect those nodes when present; else connect all subjects.
      const subSet = new Set((st.subjects ?? []).map((x) => String(x)).filter(Boolean));
      const didOne = (() => {
        let ok = false;
        for (const s of subjectNodes) {
          if (!subSet.size || subSet.has(s.fullLabel ?? s.label)) {
            edges.push({ from: s.id, to: aid, label: 'do' });
            ok = true;
          }
        }
        return ok;
      })();
      if (!didOne) for (const s of subjectNodes) edges.push({ from: s.id, to: aid, label: 'do' });

      const objSet = new Set((st.objects ?? []).map((x) => String(x)).filter(Boolean));
      for (const o of objNodes) {
        const title = o.fullLabel ?? o.label;
        if (!objSet.size || objSet.has(title)) edges.push({ from: aid, to: o.id, label: 'object' });
      }
      if (st.purpose) edges.push({ from: aid, to: `pur:${selected.event_id}:${i}`, label: 'purpose' });
      const next = actionNodes[i + 1];
      if (next) edges.push({ from: aid, to: next.id, label: 'then' });
    });

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
    <div class="mt-3 flex flex-wrap items-center gap-2 text-xs">
      <label class="flex items-center gap-2">
        <span class="text-ink-800/70">Dataset</span>
        <select
          class="rounded-md border border-ink-950/15 bg-white px-2 py-1 text-xs"
          value={data.source ?? 'gwb'}
          on:change={(e) => {
            const v = (e.currentTarget as HTMLSelectElement).value;
            window.location.href = `/graphs/wiki-timeline-aoo?source=${encodeURIComponent(v)}`;
          }}
        >
          <option value="gwb">gwb</option>
          <option value="hca">hca</option>
          <option value="legal">legal</option>
          <option value="legal_follow">legal_follow</option>
        </select>
      </label>
      <a
        class="rounded-md border border-ink-950/15 px-2 py-1 text-xs text-ink-950 hover:border-ink-950/30 hover:bg-ink-950/[0.03]"
        href={`/graphs/wiki-timeline?source=${encodeURIComponent(data.source ?? 'gwb')}`}
      >
        Open Timeline
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
          {#if selected.chains?.length}
            <div class="mt-2 text-xs text-ink-800/60 font-mono">
              chains:
              {#each selected.chains as c, i (i)}
                <span class="ml-2">{c.kind}({c.from_step ?? '-'}->{c.to_step ?? c.to ?? '-'})</span>
              {/each}
            </div>
          {/if}
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

        <Panel>
          <div class="flex flex-wrap items-center justify-between gap-2">
            <div class="text-xs uppercase tracking-[0.28em] text-ink-800/70">Span candidates</div>
            <div class="font-mono text-[10px] text-ink-800/60">
              {#if data.payload.parser}
                parser={data.payload.parser.model ?? '(unknown)'}
              {:else}
                parser=(none)
              {/if}
            </div>
          </div>
          {#if selected.span_candidates?.length}
            <div class="mt-3 flex flex-wrap items-center gap-3 text-xs text-ink-950">
              <label class="flex items-center gap-2">
                <input type="checkbox" bind:checked={showAllSpans} />
                <span class="text-ink-800/70">show all</span>
              </label>
              <div class="font-mono text-[10px] text-ink-800/60">
                showing {spanShown.length} / {selected.span_candidates.length}
              </div>
            </div>
            <div class="mt-3 flex flex-wrap gap-2 text-[11px]">
              {#each spanShown as s (s.span_id)}
                <span class="rounded border border-ink-950/10 bg-white px-2 py-1 font-mono text-ink-950">
                  <span class="text-ink-800/70">{s.span_type}</span>
                  <span class="ml-2">{s.text}</span>
                  {#if s.hygiene?.view_score !== undefined}
                    <span class="ml-2 text-ink-800/60">score={Number(s.hygiene.view_score).toFixed(2)}</span>
                  {/if}
                  {#if s.recurrence?.seen_events}
                    <span class="ml-2 text-ink-800/60">seen={s.recurrence.seen_events}</span>
                  {/if}
                </span>
              {/each}
            </div>
          {:else}
            <div class="mt-3 text-xs text-ink-800/70">
              No span candidates emitted (model not installed, parsing disabled, or no noun chunks outside resolved entities).
            </div>
          {/if}
        </Panel>

        <Panel>
          <div class="text-xs uppercase tracking-[0.28em] text-ink-800/70">Object resolver hints</div>
          {#if objectHintRows.length}
            <div class="mt-3 max-h-[260px] overflow-auto space-y-2">
              {#each objectHintRows as r (r.title + ':' + r.source)}
                <div class="rounded border border-ink-950/10 bg-white px-2 py-2">
                  <div class="font-mono text-[11px] text-ink-950">
                    [{r.source}] {r.title}
                  </div>
                  {#if r.hints.length}
                    <div class="mt-1 flex flex-wrap gap-2 text-[10px]">
                      {#each r.hints as h, i (r.title + ':' + i)}
                        <span class="rounded bg-slate-100 px-1.5 py-0.5 font-mono text-ink-900">
                          {h.kind}@{h.lane}: {h.title} ({Number(h.score).toFixed(2)})
                        </span>
                      {/each}
                    </div>
                  {:else}
                    <div class="mt-1 text-[11px] text-ink-800/70">no resolver hints</div>
                  {/if}
                </div>
              {/each}
            </div>
          {:else}
            <div class="mt-3 text-xs text-ink-800/70">No objects available for hinting in this event.</div>
          {/if}
        </Panel>
      {/if}
    </div>
  </div>
</div>
