<script lang="ts">
  import BipartiteGraph, { type GraphEdge, type GraphNode } from '$lib/ui/BipartiteGraph.svelte';
  import Panel from '$lib/ui/Panel.svelte';

  export let data: {
    payload: {
      pages: Array<{ title: string; revid: number | null; wiki: string | null; source_url: string | null }>;
      candidates: Array<{ title: string; score: number; evidence_pages: string[] }>;
    };
    relPath: string;
    error: string | null;
  };

  type Kind = 'event' | 'person' | 'institution' | 'other';

  function guessKind(title: string): Kind {
    const t = title.trim();
    if (/^\d{3,4}\b/.test(t)) return 'event';
    if (/\b(election|convention|debates|State of the Union|invasion|war)\b/i.test(t)) return 'event';
    if (t.startsWith('Office of ')) return 'institution';
    if (t.startsWith('Department of ')) return 'institution';
    if (/\b(Badge|Guard|Air National Guard|Research Service|Doctrine|School|University|News|Press|Service)\b/i.test(t))
      return 'institution';
    if (/^[A-Z][A-Za-z.'-]+(?:\s+[A-Z][A-Za-z.'-]+){1,4}$/.test(t)) return 'person';
    return 'other';
  }

  let mode: 'aggregate' | 'expanded' = 'aggregate';
  let topN = 120;
  let selectedNodeId: string | null = null;
  let showAllContextRows = false;
  let expandedContextKeys = new Set<string>();

  $: pages = data.payload.pages ?? [];
  $: candidatesAll = data.payload.candidates ?? [];

  $: pageNodes = pages.map<GraphNode>((p) => ({
    id: `page:${p.title}`,
    label: p.title,
    color: '#e8f4ff',
    tooltip: `${p.wiki ?? 'wiki'} revid=${p.revid ?? 'unknown'}`
  }));

  function buildAggregate(): { right: GraphNode[]; edges: GraphEdge[] } {
    const kinds: Kind[] = ['event', 'person', 'institution', 'other'];
    const countsByKind = new Map<Kind, number>();
    const perPage = new Map<string, Map<Kind, number>>();
    for (const p of pages) perPage.set(p.title, new Map());
    for (const c of candidatesAll) {
      const k = guessKind(c.title);
      countsByKind.set(k, (countsByKind.get(k) ?? 0) + 1);
      for (const pt of c.evidence_pages ?? []) {
        const m = perPage.get(pt);
        if (!m) continue;
        m.set(k, (m.get(k) ?? 0) + 1);
      }
    }

    const right: GraphNode[] = kinds.map((k) => ({
      id: `kind:${k}`,
      label: `${k} (${countsByKind.get(k) ?? 0})`,
      color: k === 'event' ? '#fef3c7' : k === 'person' ? '#e9d5ff' : k === 'institution' ? '#bbf7d0' : '#f6f6f6',
      tooltip: 'Heuristic kind bucket (non-authoritative)'
    }));

    const edges: GraphEdge[] = [];
    for (const p of pages) {
      const m = perPage.get(p.title);
      if (!m) continue;
      for (const k of kinds) {
        const w = m.get(k) ?? 0;
        if (w <= 0) continue;
        edges.push({ from: `page:${p.title}`, to: `kind:${k}`, weight: w });
      }
    }
    return { right, edges };
  }

  function buildExpanded(): { right: GraphNode[]; edges: GraphEdge[] } {
    const slice = candidatesAll.slice(0, Math.max(20, Math.min(200, Math.floor(topN))));
    const right: GraphNode[] = slice.map((c) => {
      const k = guessKind(c.title);
      const color =
        k === 'event' ? '#fef3c7' : k === 'person' ? '#e9d5ff' : k === 'institution' ? '#bbf7d0' : '#f6f6f6';
      return {
        id: `cand:${c.title}`,
        label: c.title,
        color,
        tooltip: `score=${c.score}; kind=${k}; evidence_pages=${(c.evidence_pages ?? []).length}`
      };
    });

    const edges: GraphEdge[] = [];
    const rightSet = new Set(right.map((n) => n.id));
    for (const c of slice) {
      const to = `cand:${c.title}`;
      if (!rightSet.has(to)) continue;
      for (const pt of c.evidence_pages ?? []) {
        edges.push({ from: `page:${pt}`, to, weight: 1 });
      }
    }
    return { right, edges };
  }

  $: graph = mode === 'aggregate' ? buildAggregate() : buildExpanded();

  type ContextRow = {
    key: string;
    title: string;
    subtitle: string;
    chips: string[];
    text: string;
  };

  function toggleContextExpand(key: string) {
    const next = new Set(expandedContextKeys);
    if (next.has(key)) next.delete(key);
    else next.add(key);
    expandedContextKeys = next;
  }

  $: contextRows = (() => {
    if (!selectedNodeId) return [] as ContextRow[];

    if (selectedNodeId.startsWith('page:')) {
      const pageTitle = selectedNodeId.slice('page:'.length);
      const page = pages.find((p) => p.title === pageTitle);
      const matches = candidatesAll
        .filter((c) => (c.evidence_pages ?? []).includes(pageTitle))
        .sort((a, b) => Number(b.score ?? 0) - Number(a.score ?? 0))
        .map((c) => ({
          key: `ctx:page:${pageTitle}:cand:${c.title}`,
          title: c.title,
          subtitle: `candidate score=${Number(c.score ?? 0).toFixed(3)}`,
          chips: [`kind:${guessKind(c.title)}`, `evidence_pages:${(c.evidence_pages ?? []).length}`],
          text: `Evidence from page "${pageTitle}" supports candidate "${c.title}".`
        }));
      const header: ContextRow[] = page
        ? [
            {
              key: `ctx:page:${pageTitle}:meta`,
              title: page.title,
              subtitle: `snapshot page`,
              chips: [
                `wiki:${page.wiki ?? 'unknown'}`,
                `revid:${page.revid ?? 'unknown'}`
              ],
              text: page.source_url ? `source_url=${page.source_url}` : 'source_url=(none)'
            }
          ]
        : [];
      return [...header, ...matches];
    }

    if (selectedNodeId.startsWith('cand:')) {
      const candTitle = selectedNodeId.slice('cand:'.length);
      const cand = candidatesAll.find((c) => c.title === candTitle);
      if (!cand) return [] as ContextRow[];
      const rows: ContextRow[] = [
        {
          key: `ctx:cand:${candTitle}:meta`,
          title: cand.title,
          subtitle: `candidate`,
          chips: [
            `score:${Number(cand.score ?? 0).toFixed(3)}`,
            `kind:${guessKind(cand.title)}`
          ],
          text: `Evidence pages: ${(cand.evidence_pages ?? []).join(', ') || '(none)'}`
        }
      ];
      for (const pt of cand.evidence_pages ?? []) {
        const p = pages.find((x) => x.title === pt);
        rows.push({
          key: `ctx:cand:${candTitle}:page:${pt}`,
          title: pt,
          subtitle: 'evidence page',
          chips: [
            `wiki:${p?.wiki ?? 'unknown'}`,
            `revid:${p?.revid ?? 'unknown'}`
          ],
          text: p?.source_url ? `source_url=${p.source_url}` : 'source_url=(none)'
        });
      }
      return rows;
    }

    if (selectedNodeId.startsWith('kind:')) {
      const kind = selectedNodeId.slice('kind:'.length);
      return candidatesAll
        .filter((c) => guessKind(c.title) === kind)
        .sort((a, b) => Number(b.score ?? 0) - Number(a.score ?? 0))
        .map((c) => ({
          key: `ctx:kind:${kind}:cand:${c.title}`,
          title: c.title,
          subtitle: `candidate`,
          chips: [
            `score:${Number(c.score ?? 0).toFixed(3)}`,
            `evidence_pages:${(c.evidence_pages ?? []).length}`
          ],
          text: `Evidence pages: ${(c.evidence_pages ?? []).join(', ') || '(none)'}`
        }));
    }

    return [] as ContextRow[];
  })();

  $: contextRowsShown = showAllContextRows ? contextRows : contextRows.slice(0, 60);
</script>

<div class="space-y-4 p-6">
  <Panel>
    <div class="text-xs uppercase tracking-[0.28em] text-ink-800/70">Wiki candidates graph</div>
    <div class="mt-2 text-sm text-ink-950">
      Source: <span class="font-mono text-xs">{data.relPath}</span>
    </div>
    <div class="mt-3 flex flex-wrap items-center gap-3 text-sm">
        <label class="flex items-center gap-2">
          <span class="text-ink-800/70">Mode</span>
          <select bind:value={mode} class="rounded-md border border-ink-950/15 bg-white px-2 py-1 text-sm">
            <option value="aggregate">Aggregate by kind</option>
            <option value="expanded">Expanded (top N)</option>
          </select>
        </label>

        {#if mode === 'expanded'}
          <label class="flex items-center gap-2">
            <span class="text-ink-800/70">Top N</span>
            <input type="number" min="20" max="200" step="10" bind:value={topN} class="w-24 rounded-md border border-ink-950/15 px-2 py-1 font-mono text-xs" aria-label="Top N results" />
          </label>
        {/if}
      </div>
  </Panel>

  {#if data.error}
    <Panel tone="danger">
      <div class="text-xs uppercase tracking-[0.28em] text-red-800/80">Load error</div>
      <pre class="mt-3 whitespace-pre-wrap font-mono text-xs text-ink-950">{data.error}</pre>
    </Panel>
  {/if}

  <BipartiteGraph
    left={pageNodes}
    right={graph.right}
    edges={graph.edges}
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
          {#if contextRows.length > 60}
            <label class="ml-2 inline-flex items-center gap-1 rounded border border-ink-950/10 bg-white px-2 py-0.5">
              <input type="checkbox" bind:checked={showAllContextRows} />
              <span>all rows ({contextRows.length})</span>
            </label>
          {/if}
        {:else}
          click a node to inspect candidate/page evidence context
        {/if}
      </div>
    </div>
    {#if selectedNodeId && contextRows.length}
      <div class="mt-3 max-h-[340px] overflow-auto rounded-lg border border-ink-950/10 bg-white">
        {#each contextRowsShown as r (r.key)}
          {@const expanded = expandedContextKeys.has(r.key)}
          <div class="border-b border-ink-950/10 p-3 last:border-b-0">
            <button
              class="w-full text-left"
              on:click={() => toggleContextExpand(r.key)}
            >
              <div class="flex flex-wrap items-center justify-between gap-2">
                <div class="text-sm text-ink-950">{r.title}</div>
                <div class="font-mono text-[10px] text-ink-800/60">{r.subtitle} {expanded ? '[-]' : '[+]'}</div>
              </div>
            </button>
            <div class="mt-2 flex flex-wrap gap-1 text-[10px]">
              {#each r.chips as c (r.key + ':chip:' + c)}
                <span class="rounded bg-slate-100 px-1.5 py-0.5 font-mono text-ink-900">{c}</span>
              {/each}
            </div>
            {#if expanded}
              <div class="mt-2 text-xs text-ink-900 font-mono">{r.text}</div>
            {/if}
          </div>
        {/each}
      </div>
    {/if}
  </Panel>

  <div class="text-xs text-ink-800/60">
    Note: this is a visualization of the extraction substrate (page->candidate evidence edges). It is pre-graph (no SL/SB commitments).
  </div>
</div>
