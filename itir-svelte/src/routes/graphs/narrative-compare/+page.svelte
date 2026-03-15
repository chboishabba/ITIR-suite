<script lang="ts">
  import Panel from '$lib/ui/Panel.svelte';
  import LayeredGraph, { type LayerNode, type LayeredEdge } from '$lib/ui/LayeredGraph.svelte';
  import { createSelectionBridge } from '$lib/workbench/selectionBridge';

  export let data: {
    selectedFixture: string;
    fixtureMeta?: { fixture_id?: string; label?: string };
    comparison: any;
    availableFixtures: Array<{ key: string; label: string }>;
    stateReason?: string;
    error: string | null;
  };

  type InspectorTab = 'Claim' | 'Graph';
  type SelectionKind = 'shared' | 'disputed' | 'source_only' | 'corroboration' | 'abstention';
  type SelectionItem = {
    key: string;
    kind: SelectionKind;
    title: string;
    subtitle: string;
    leftLabel?: string;
    rightLabel?: string;
    receipts: Array<{ kind: string; value: string }>;
    nodeHints: Array<{ id: string; label: string; color?: string }>;
  };

  function changeFixture(fixture: string) {
    window.location.href = `/graphs/narrative-compare?fixture=${encodeURIComponent(fixture)}`;
  }

  const comparison = data.comparison;
  const sources = comparison?.sources ?? [];
  const reports = comparison?.reports ?? {};

  let activeTab: InspectorTab = 'Claim';
  let selectedKey = '';
  const rowSelectionBridge = createSelectionBridge<string>(null);

  $: sharedRows = comparison?.shared_propositions ?? [];
  $: disputedRows = comparison?.disputed_propositions ?? [];
  $: sourceOnlyBySource = comparison?.source_only_propositions ?? {};
  $: corroborationBySource = comparison?.corroboration_refs ?? {};
  $: abstentionsBySource = comparison?.abstentions ?? {};
  $: comparisonLinks = comparison?.comparison_links ?? [];

  $: selectionItems = buildSelectionItems();
  $: reviewState = data.stateReason ?? (data.error ? 'load_error' : selectionItems.length ? 'ready' : 'empty');
  $: selectedKey = selectionItems.some((row) => row.key === selectedKey) ? selectedKey : (selectionItems[0]?.key ?? '');
  $: if (selectedKey && $rowSelectionBridge.active !== selectedKey) {
    rowSelectionBridge.setActive(selectedKey, 'sync');
  }
  $: selectedItem = selectionItems.find((row) => row.key === selectedKey) ?? null;
  $: scopedGraph = buildScopedGraph(selectedItem);
  $: graphViewportKey = `${selectedKey}:${scopedGraph.layers.map((row) => row.nodes.length).join(',')}:${scopedGraph.edges.length}`;

  function keyFor(kind: SelectionKind, idx: number, sourceId?: string): string {
    return sourceId ? `${kind}:${sourceId}:${idx}` : `${kind}:${idx}`;
  }

  function safeText(value: unknown): string {
    return typeof value === 'string' && value.trim() ? value : 'none';
  }

  function buildSelectionItems(): SelectionItem[] {
    const rows: SelectionItem[] = [];

    for (let index = 0; index < sharedRows.length; index += 1) {
      const row = sharedRows[index] ?? {};
      const left = row.left?.[0] ?? row.left ?? {};
      const right = row.right?.[0] ?? row.right ?? {};
      const leftId = String(left.proposition_id ?? `${keyFor('shared', index)}:left`);
      const rightId = String(right.proposition_id ?? `${keyFor('shared', index)}:right`);
      rows.push({
        key: keyFor('shared', index),
        kind: 'shared',
        title: safeText(left.predicate_key ?? right.predicate_key),
        subtitle: safeText(left.anchor_text ?? right.anchor_text),
        leftLabel: safeText(left.anchor_text),
        rightLabel: safeText(right.anchor_text),
        receipts: (row.receipts ?? []).map((receipt: any) => ({ kind: String(receipt.kind ?? 'ref'), value: String(receipt.value ?? '') })),
        nodeHints: [
          { id: leftId, label: safeText(left.predicate_key ?? 'left proposition'), color: '#bbf7d0' },
          { id: rightId, label: safeText(right.predicate_key ?? 'right proposition'), color: '#dbeafe' }
        ]
      });
    }

    for (let index = 0; index < disputedRows.length; index += 1) {
      const row = disputedRows[index] ?? {};
      const left = row.left ?? {};
      const right = row.right ?? {};
      const leftId = String(left.proposition_id ?? `${keyFor('disputed', index)}:left`);
      const rightId = String(right.proposition_id ?? `${keyFor('disputed', index)}:right`);
      rows.push({
        key: keyFor('disputed', index),
        kind: 'disputed',
        title: `${safeText(left.predicate_key)} vs ${safeText(right.predicate_key)}`,
        subtitle: safeText(left.anchor_text),
        leftLabel: safeText(left.anchor_text),
        rightLabel: safeText(right.anchor_text),
        receipts: [],
        nodeHints: [
          { id: leftId, label: safeText(left.predicate_key ?? 'left claim'), color: '#fecdd3' },
          { id: rightId, label: safeText(right.predicate_key ?? 'right claim'), color: '#fde68a' }
        ]
      });
    }

    for (const source of sources) {
      const sourceId = String(source.source_id ?? 'unknown');
      const sourceRows = sourceOnlyBySource?.[sourceId] ?? [];
      for (let index = 0; index < sourceRows.length; index += 1) {
        const row = sourceRows[index] ?? {};
        const nodeId = String(row.proposition_id ?? `${keyFor('source_only', index, sourceId)}:node`);
        rows.push({
          key: keyFor('source_only', index, sourceId),
          kind: 'source_only',
          title: safeText(row.predicate_key),
          subtitle: safeText(row.anchor_text),
          leftLabel: safeText(source.title),
          receipts: [],
          nodeHints: [{ id: nodeId, label: safeText(row.predicate_key ?? 'source-only'), color: '#e2e8f0' }]
        });
      }

      const corroborationRows = corroborationBySource?.[sourceId] ?? [];
      for (let index = 0; index < corroborationRows.length; index += 1) {
        const row = corroborationRows[index] ?? {};
        rows.push({
          key: keyFor('corroboration', index, sourceId),
          kind: 'corroboration',
          title: safeText(row.label ?? 'corroboration'),
          subtitle: safeText(row.claim_text),
          leftLabel: safeText(source.title),
          receipts: [],
          nodeHints: []
        });
      }

      const abstentionRows = abstentionsBySource?.[sourceId] ?? [];
      for (let index = 0; index < abstentionRows.length; index += 1) {
        const row = abstentionRows[index] ?? {};
        rows.push({
          key: keyFor('abstention', index, sourceId),
          kind: 'abstention',
          title: safeText(row.reason ?? 'abstention'),
          subtitle: safeText(row.text),
          leftLabel: safeText(source.title),
          receipts: [],
          nodeHints: []
        });
      }
    }

    return rows;
  }

  function buildScopedGraph(selection: SelectionItem | null): { layers: Array<{ id: string; title: string; nodes: LayerNode[] }>; edges: LayeredEdge[] } {
    if (!selection) return { layers: [], edges: [] };

    const nodeMap = new Map<string, LayerNode>();
    for (const hint of selection.nodeHints) {
      nodeMap.set(hint.id, {
        id: hint.id,
        label: hint.label,
        tooltip: hint.id,
        color: hint.color ?? '#e2e8f0',
        scale: 1
      });
    }

    const edges: LayeredEdge[] = [];

    if (selection.nodeHints.length >= 2) {
      const first = selection.nodeHints[0];
      const second = selection.nodeHints[1];
      if (first && second) {
        edges.push({ id: `${selection.key}:relation`, from: first.id, to: second.id, label: selection.kind === 'disputed' ? 'dispute' : 'compare', kind: 'context' });
      }
    }

    const scopedIds = new Set(selection.nodeHints.map((row) => row.id));
    for (const link of comparisonLinks) {
      const leftId = String(link.left_proposition_id ?? '');
      const rightId = String(link.right_proposition_id ?? '');
      if (!leftId || !rightId) continue;
      if (!scopedIds.size || scopedIds.has(leftId) || scopedIds.has(rightId)) {
        if (!nodeMap.has(leftId)) nodeMap.set(leftId, { id: leftId, label: leftId.slice(0, 12), tooltip: leftId, color: '#dbeafe', scale: 0.92 });
        if (!nodeMap.has(rightId)) nodeMap.set(rightId, { id: rightId, label: rightId.slice(0, 12), tooltip: rightId, color: '#bbf7d0', scale: 0.92 });
        edges.push({ id: String(link.link_id ?? `${leftId}:${rightId}:${link.link_kind ?? ''}`), from: leftId, to: rightId, label: String(link.link_kind ?? 'link'), kind: 'evidence' });
      }
    }

    const primaryNodes = Array.from(nodeMap.values()).slice(0, 18);
    const primaryNodeIds = new Set(primaryNodes.map((row) => row.id));
    const scopedEdges = edges.filter((row) => primaryNodeIds.has(row.from) && primaryNodeIds.has(row.to));

    return {
      layers: primaryNodes.length ? [{ id: 'claims', title: 'Scoped claim graph', nodes: primaryNodes }] : [],
      edges: scopedEdges
    };
  }

  function selectItem(key: string) {
    selectedKey = key;
    rowSelectionBridge.setActive(key, 'select');
    activeTab = 'Claim';
  }

  function selectionTone(kind: SelectionKind): string {
    if (kind === 'disputed') return 'border-rose-200 bg-rose-50/60';
    if (kind === 'shared') return 'border-emerald-200 bg-emerald-50/60';
    if (kind === 'source_only') return 'border-amber-200 bg-amber-50/60';
    if (kind === 'corroboration') return 'border-sky-200 bg-sky-50/60';
    return 'border-zinc-200 bg-zinc-50';
  }

  function selectionBadge(kind: SelectionKind): string {
    if (kind === 'disputed') return 'bg-rose-100 text-rose-900 border-rose-300';
    if (kind === 'shared') return 'bg-emerald-100 text-emerald-900 border-emerald-300';
    if (kind === 'source_only') return 'bg-amber-100 text-amber-900 border-amber-300';
    if (kind === 'corroboration') return 'bg-sky-100 text-sky-900 border-sky-300';
    return 'bg-zinc-100 text-zinc-900 border-zinc-300';
  }
</script>

<svelte:head>
  <title>Narrative Comparison</title>
</svelte:head>

<div class="mx-auto flex max-w-7xl flex-col gap-4 px-6 py-6">
  <Panel>
    <div class="text-xs uppercase tracking-[0.28em] text-ink-800/70">Narrative Comparison Workbench</div>
    <div class="mt-2 text-2xl font-semibold text-ink-950">Public media narrative validation</div>
    <div class="mt-2 max-w-3xl text-sm text-ink-800/70">
      Compare shared vs disputed facts, proposition links, and attribution surfaces without collapsing two source narratives into one story.
    </div>
    <label class="mt-4 block text-xs uppercase tracking-[0.24em] text-ink-800/70" for="fixture-select">Fixture</label>
    <select
      id="fixture-select"
      class="mt-2 rounded border border-ink-950/10 bg-white px-3 py-2 text-sm text-ink-950"
      value={data.selectedFixture}
      on:change={(event) => changeFixture((event.currentTarget as HTMLSelectElement).value)}
    >
      {#each data.availableFixtures as fixture}
        <option value={fixture.key}>{fixture.label}</option>
      {/each}
    </select>
    {#if data.fixtureMeta?.label}
      <div class="mt-3 text-xs text-ink-800/60">{data.fixtureMeta.label}</div>
    {/if}
    <div class="mt-3 flex items-center gap-2">
      <span class="text-xs uppercase tracking-[0.24em] text-ink-800/70">state</span>
      <span class="rounded bg-paper-100 px-2 py-1 font-mono text-[11px]">{reviewState}</span>
    </div>
  </Panel>

  {#if data.error}
    <Panel tone="danger">
      <div class="text-xs uppercase tracking-[0.28em] text-red-800/80">Load error</div>
      <pre class="mt-3 whitespace-pre-wrap font-mono text-xs text-ink-950">{data.error}</pre>
    </Panel>
  {:else if comparison}
    <div class="grid gap-4 lg:grid-cols-2">
      {#each sources as source}
        <Panel>
          <div class="text-xs uppercase tracking-[0.28em] text-ink-800/70">Source</div>
          <div class="mt-2 text-lg font-semibold text-ink-950">{source.title}</div>
          <div class="mt-1 text-xs text-ink-800/60">{source.source_type}</div>
          <div class="mt-4 grid grid-cols-2 gap-2 text-sm">
            <div class="rounded border border-ink-950/10 bg-ink-50 p-3">
              <div class="text-[11px] uppercase tracking-[0.24em] text-ink-800/60">Facts</div>
              <div class="mt-1 text-xl font-semibold text-ink-950">{reports[source.source_id]?.summary?.fact_count ?? 0}</div>
            </div>
            <div class="rounded border border-ink-950/10 bg-ink-50 p-3">
              <div class="text-[11px] uppercase tracking-[0.24em] text-ink-800/60">Propositions</div>
              <div class="mt-1 text-xl font-semibold text-ink-950">{reports[source.source_id]?.summary?.proposition_count ?? 0}</div>
            </div>
            <div class="rounded border border-ink-950/10 bg-ink-50 p-3 col-span-2">
              <div class="text-[11px] uppercase tracking-[0.24em] text-ink-800/60">Proposition links</div>
              <div class="mt-1 text-xl font-semibold text-ink-950">{reports[source.source_id]?.summary?.proposition_link_count ?? 0}</div>
            </div>
          </div>
        </Panel>
      {/each}
    </div>

    <div class="grid gap-4 lg:grid-cols-4">
      <Panel>
        <div class="text-xs uppercase tracking-[0.28em] text-ink-800/70">Shared</div>
        <div class="mt-2 text-3xl font-semibold text-emerald-700">{comparison.summary.shared_proposition_count}</div>
      </Panel>
      <Panel>
        <div class="text-xs uppercase tracking-[0.28em] text-ink-800/70">Disputed</div>
        <div class="mt-2 text-3xl font-semibold text-rose-700">{comparison.summary.disputed_proposition_count}</div>
      </Panel>
      <Panel>
        <div class="text-xs uppercase tracking-[0.28em] text-ink-800/70">Link differences</div>
        <div class="mt-2 text-3xl font-semibold text-amber-700">{comparison.summary.link_difference_count}</div>
      </Panel>
      <Panel>
        <div class="text-xs uppercase tracking-[0.28em] text-ink-800/70">Comparison links</div>
        <div class="mt-2 text-3xl font-semibold text-violet-700">{comparison.summary.comparison_link_count}</div>
      </Panel>
    </div>

    <div class="grid gap-4 xl:grid-cols-[1.1fr_0.9fr]">
      <Panel>
        <div class="text-xs uppercase tracking-[0.28em] text-ink-800/70">Review rows</div>
        <div class="mt-2 text-sm text-ink-800/70">Select a row to inspect receipts and open bounded graph context.</div>
        <div class="mt-4 space-y-2 max-h-[72vh] overflow-y-auto pr-1">
          {#each selectionItems as item}
            <button
              type="button"
              class={`block w-full rounded-lg border p-3 text-left ${selectionTone(item.kind)} ${selectedKey === item.key ? 'ring-2 ring-ink-900/25' : ''}`}
              on:click={() => selectItem(item.key)}
            >
              <div class="flex items-center justify-between gap-2">
                <div class={`rounded-full border px-2 py-0.5 text-[10px] uppercase tracking-[0.18em] ${selectionBadge(item.kind)}`}>
                  {item.kind.replace('_', ' ')}
                </div>
                <div class="font-mono text-[10px] text-ink-800/60">{item.key}</div>
              </div>
              <div class="mt-1 font-medium text-ink-950">{item.title}</div>
              <div class="mt-1 text-xs text-ink-800/70">{item.subtitle}</div>
              {#if item.leftLabel || item.rightLabel}
                <div class="mt-2 text-[11px] text-ink-800/70">
                  {#if item.leftLabel}<span class="mr-2">A: {item.leftLabel}</span>{/if}
                  {#if item.rightLabel}<span>B: {item.rightLabel}</span>{/if}
                </div>
              {/if}
            </button>
          {/each}
          {#if !selectionItems.length}
            <div class="rounded-lg border border-dashed border-ink-950/15 bg-white p-3 text-sm text-ink-800/70">
              No comparable rows are available for this fixture.
            </div>
          {/if}
        </div>
      </Panel>

      <div class="flex flex-col gap-4">
        <Panel>
          <div class="flex items-center justify-between gap-3">
            <div>
              <div class="text-xs uppercase tracking-[0.28em] text-ink-800/70">Inspector</div>
              <div class="mt-1 text-sm text-ink-800/70">{selectedItem?.title ?? 'Select a row'}</div>
            </div>
            <div class="flex flex-wrap gap-2">
              {#each ['Claim', 'Graph'] as tab}
                <button
                  type="button"
                  class={`rounded-lg px-3 py-2 text-xs uppercase tracking-widest ring-1 ${activeTab === tab ? 'bg-ink-900 text-paper-50 ring-ink-900' : 'bg-paper-100 ring-ink-900/10'}`}
                  on:click={() => (activeTab = tab as InspectorTab)}
                >
                  {tab}
                </button>
              {/each}
            </div>
          </div>
        </Panel>

        {#if activeTab === 'Claim'}
          <Panel>
            {#if selectedItem}
              <div class="text-xs uppercase tracking-[0.28em] text-ink-800/70">Selection</div>
              <div class="mt-2 text-lg font-semibold text-ink-950">{selectedItem.title}</div>
              <div class="mt-2 text-sm text-ink-800/80">{selectedItem.subtitle}</div>
              <div class="mt-4 flex flex-wrap gap-2">
                <span class={`rounded-full border px-2 py-1 text-[11px] ${selectionBadge(selectedItem.kind)}`}>kind: {selectedItem.kind}</span>
                {#if selectedItem.leftLabel}<span class="rounded-full border border-ink-950/10 bg-paper-100 px-2 py-1 text-[11px]">A: {selectedItem.leftLabel}</span>{/if}
                {#if selectedItem.rightLabel}<span class="rounded-full border border-ink-950/10 bg-paper-100 px-2 py-1 text-[11px]">B: {selectedItem.rightLabel}</span>{/if}
              </div>

              <div class="mt-4 text-xs uppercase tracking-[0.24em] text-ink-800/60">Receipts</div>
              <div class="mt-2 flex flex-wrap gap-2">
                {#each selectedItem.receipts as receipt}
                  <span class="rounded-full border border-ink-900/10 bg-paper-100 px-2 py-1 text-[11px]">{receipt.kind}: {receipt.value}</span>
                {/each}
                {#if !selectedItem.receipts.length}
                  <span class="text-sm text-ink-800/70">No explicit receipts attached to this selected row.</span>
                {/if}
              </div>

              <div class="mt-4">
                <button
                  type="button"
                  class="rounded-lg bg-ink-900 px-3 py-2 text-xs uppercase tracking-widest text-paper-50"
                  on:click={() => (activeTab = 'Graph')}
                >
                  Open graph focus
                </button>
              </div>
            {:else}
              <div class="text-sm text-ink-800/70">Select a comparison row to inspect it.</div>
            {/if}
          </Panel>
        {:else}
          <Panel>
            <div class="text-xs uppercase tracking-[0.28em] text-ink-800/70">Scoped graph</div>
            <div class="mt-2 text-sm text-ink-800/70">Graph stays bounded to the currently selected row and nearby comparison links.</div>
            {#if scopedGraph.layers.length}
              <div class="mt-4">
                <LayeredGraph
                  layers={scopedGraph.layers}
                  edges={scopedGraph.edges}
                  width={1400}
                  height={620}
                  fitToWidth={true}
                  scrollWhenOverflow={true}
                  viewportResetKey={graphViewportKey}
                />
              </div>
            {:else}
              <div class="mt-3 rounded-lg border border-dashed border-ink-950/15 bg-white p-3 text-sm text-ink-800/70">
                No graph context is available for this selected row.
              </div>
            {/if}
          </Panel>
        {/if}
      </div>
    </div>
  {/if}
</div>
