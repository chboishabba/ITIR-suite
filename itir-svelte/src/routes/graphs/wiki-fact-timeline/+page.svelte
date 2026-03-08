<script lang="ts">
  import Panel from '$lib/ui/Panel.svelte';
  import LayeredGraph, { type LayerNode, type LayeredEdge } from '$lib/ui/LayeredGraph.svelte';
  import { computeImportanceScores, percentileScaleMap, type ImportanceProfileId } from '$lib/importanceProfiles';
  import { afterUpdate } from 'svelte';

  export let data: {
    payload: {
      root_actor: { label: string; surname: string };
      parser: any;
      diagnostics?: {
        event_count: number;
        fact_row_source: string;
        raw_fact_rows: number;
        output_fact_rows: number;
      };
      facts: Array<{
        fact_id: string;
        event_id: string;
        anchor: { year: number; month: number | null; day: number | null; precision: string; text: string; kind: string };
        event_anchor?: { year: number; month: number | null; day: number | null; precision: string; text: string; kind: string } | null;
        anchor_source: 'event' | 'mention';
        party: string;
        subjects: string[];
        action: string | null;
        negation?: { kind: string; scope?: string; source?: string };
        objects: string[];
        purpose: string | null;
        text: string;
        section: string;
        prev_fact_ids: string[];
        next_fact_ids: string[];
        chain_kinds: string[];
      }>;
      propositions: Array<{
        proposition_id: string;
        event_id: string;
        proposition_kind: string;
        predicate_key: string;
        negation?: { kind: string; scope?: string; source?: string };
        source_fact_id?: string;
        source_signal?: string;
        anchor_text?: string;
        arguments: Array<{ role: string; value: string }>;
        receipts: Array<{ kind: string; value: string }>;
      }>;
      proposition_links: Array<{
        link_id: string;
        event_id: string;
        source_proposition_id: string;
        target_proposition_id: string;
        link_kind: string;
        receipts: Array<{ kind: string; value: string }>;
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
  let importanceProfile: ImportanceProfileId = 'entropy_role_section_v1';

  let selectedNodeId: string | null = null;
  let contextBox: HTMLDivElement | null = null;
  let lastScrollKey = '';
  let graphWidth = 3200;
  const GRAPH_HEIGHT = 920;
  const GRAPH_COL_GAP = 800;
  const GRAPH_LEFT_PAD = 100;
  $: graphViewportKey = `${String(selectedNodeId ?? 'none')}:${String(granularity)}:${String(facts.length)}`;

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
  function node(id: string, label: string, color: string, tooltip?: string, scale?: number): LayerNode {
    const short = label.length > 72 ? label.slice(0, 72) + '...' : label;
    return { id, label: short, fullLabel: label, color, tooltip: tooltip ?? label, scale };
  }
  function uniq(xs: string[]): string[] {
    return Array.from(new Set(xs.map((x) => String(x || '').trim()).filter(Boolean)));
  }
  function actionLabel(action: string | null | undefined, negation?: { kind?: string | null }): string {
    const base = String(action ?? '').trim();
    if (!base) return '(no action)';
    if (String(negation?.kind ?? '').toLowerCase() === 'not') return `not_${base}`;
    return base;
  }
  function propositionLabel(predicate: string | null | undefined, negation?: { kind?: string | null }): string {
    const base = String(predicate ?? '').trim();
    if (!base) return '(no predicate)';
    if (String(negation?.kind ?? '').toLowerCase() === 'not') {
      if (base === 'negate') return 'does_not_negate';
      return `not_${base}`;
    }
    return base;
  }

  $: factsAll = data.payload.facts ?? [];
  $: facts = factsAll.slice(0, Math.max(20, Math.min(factsAll.length, Math.floor(maxFacts))));
  $: graphWidth = Math.max(
    3600,
    GRAPH_LEFT_PAD * 2 + Math.max(0, (graph as any)?.layers?.length ? (graph as any).layers.length - 1 : 8) * GRAPH_COL_GAP + 720
  );

  function validateNodeFactScope(
    rows: typeof facts,
    nodeFactMap: Map<string, Set<string>>,
    g: TimeGranularity
  ): { ok: boolean; leakCount: number; sample: string[] } {
    const byFactId = new Map(rows.map((r) => [String(r.fact_id), r]));
    const leaks: string[] = [];
    for (const [nodeId, factIds] of nodeFactMap) {
      for (const fid of factIds) {
        const f = byFactId.get(fid);
        if (!f) {
          leaks.push(`${nodeId} -> missing:${fid}`);
          continue;
        }
        if (nodeId.startsWith('sub:')) {
          const key = nodeId.slice(4);
          if (!(f.subjects ?? []).includes(key)) leaks.push(`${nodeId} !sub ${fid}`);
          continue;
        }
        if (nodeId.startsWith('obj:')) {
          const key = nodeId.slice(4);
          if (!(f.objects ?? []).includes(key)) leaks.push(`${nodeId} !obj ${fid}`);
          continue;
        }
        if (nodeId.startsWith('pty:')) {
          const key = nodeId.slice(4);
          if (String(f.party || '') !== key) leaks.push(`${nodeId} !party ${fid}`);
          continue;
        }
        if (nodeId.startsWith('time:')) {
          const key = nodeId.slice(5);
          if (keyFromAnchor(f.anchor, g) !== key) leaks.push(`${nodeId} !time ${fid}`);
          continue;
        }
        if (nodeId.startsWith('fact:')) {
          const key = nodeId.slice(5);
          if (String(f.fact_id) !== key) leaks.push(`${nodeId} !fact ${fid}`);
          continue;
        }
      }
    }
    return { ok: leaks.length === 0, leakCount: leaks.length, sample: leaks.slice(0, 8) };
  }

  $: graph = (() => {
    const partyCounts = new Map<string, number>();
    const subCounts = new Map<string, number>();
    const objCounts = new Map<string, number>();
    const timeNodes = new Map<string, LayerNode>();
    const actionNodes: LayerNode[] = [];
    const edges: LayeredEdge[] = [];
    const nodeFactMap = new Map<string, Set<string>>();

    function linkNodeToFact(nodeId: string, factId: string) {
      if (!nodeId || !factId) return;
      const set = nodeFactMap.get(nodeId) ?? new Set<string>();
      set.add(factId);
      nodeFactMap.set(nodeId, set);
    }

    for (const f of facts) {
      if (f.party) partyCounts.set(f.party, (partyCounts.get(f.party) ?? 0) + 1);
      for (const s of f.subjects ?? []) subCounts.set(s, (subCounts.get(s) ?? 0) + 1);
      for (const o of f.objects ?? []) objCounts.set(o, (objCounts.get(o) ?? 0) + 1);
    }

    const scoreByEntity = computeImportanceScores(
      facts.map((f) => ({
        event_id: String(f.event_id || ''),
        section: String(f.section || ''),
        subjects: f.subjects ?? [],
        objects: f.objects ?? []
      })),
      importanceProfile
    );

    const top = (m: Map<string, number>, n: number) =>
      Array.from(m.entries())
        .sort((a, b) => {
          const sa = Number(scoreByEntity.get(a[0]) ?? 0);
          const sb = Number(scoreByEntity.get(b[0]) ?? 0);
          if (sb !== sa) return sb - sa;
          if (b[1] !== a[1]) return b[1] - a[1];
          return a[0].localeCompare(b[0]);
        })
        .slice(0, Math.max(1, Math.floor(n)));
    const topParties = top(partyCounts, maxParties);
    const topSubs = top(subCounts, maxSubjects);
    const topObjs = top(objCounts, maxObjects);

    const partySet = new Set(topParties.map(([k]) => k));
    const subSet = new Set(topSubs.map(([k]) => k));
    const objSet = new Set(topObjs.map(([k]) => k));

    const subScale = percentileScaleMap(topSubs.map(([k]) => k), scoreByEntity);
    const objScale = percentileScaleMap(topObjs.map(([k]) => k), scoreByEntity);

    const partyNodes = topParties.map(([k, c]) => node(`pty:${k}`, `${k} (${c})`, '#efe7ff'));
    const subNodes = topSubs.map(([k, c]) => {
      const score = Number(scoreByEntity.get(k) ?? 0);
      const scale = importanceProfile === 'none' ? 1 : Number(subScale.get(k) ?? 1);
      return node(`sub:${k}`, `${k} (${c})`, '#bbf7d0', `${k} | count=${c} | importance=${score.toFixed(3)}`, scale);
    });
    const objNodes = topObjs.map(([k, c]) => {
      const score = Number(scoreByEntity.get(k) ?? 0);
      const scale = importanceProfile === 'none' ? 1 : Number(objScale.get(k) ?? 1);
      return node(`obj:${k}`, `${k} (${c})`, '#f5f5f5', `${k} | count=${c} | importance=${score.toFixed(3)}`, scale);
    });

    for (const f of facts) {
      const t = keyFromAnchor(f.anchor, granularity);
      const tid = `time:${t}`;
      if (!timeNodes.has(tid)) timeNodes.set(tid, node(tid, t, '#e8f4ff'));
      const action = actionLabel(f.action, f.negation);
      const subjHead = f.subjects?.[0] ?? '(no subject)';
      const aid = `fact:${f.fact_id}`;
      actionNodes.push(node(aid, `${subjHead} -> ${action}`, '#fde68a', `${f.fact_id} | ${f.section}`));
      linkNodeToFact(aid, f.fact_id);
      linkNodeToFact(tid, f.fact_id);
      edges.push({ from: tid, to: aid });
      if (f.party && partySet.has(f.party)) {
        const pid = `pty:${f.party}`;
        linkNodeToFact(pid, f.fact_id);
        edges.push({ from: pid, to: aid });
      }
      for (const s of uniq(f.subjects ?? [])) {
        if (!subSet.has(s)) continue;
        const sid = `sub:${s}`;
        linkNodeToFact(sid, f.fact_id);
        edges.push({ from: sid, to: aid });
      }
      for (const o of uniq(f.objects ?? [])) {
        if (!objSet.has(o)) continue;
        const oid = `obj:${o}`;
        linkNodeToFact(oid, f.fact_id);
        edges.push({ from: aid, to: oid });
      }
    }

    const scopeValidation = validateNodeFactScope(facts, nodeFactMap, granularity);

    return {
      layers: [
        { id: 'time', title: 'Time', nodes: Array.from(timeNodes.values()).sort((a, b) => a.id.localeCompare(b.id)) },
        { id: 'party', title: 'Party', nodes: partyNodes.length ? partyNodes : [node('pty:none', '(none)', '#fff')] },
        { id: 'sub', title: 'Subjects', nodes: subNodes.length ? subNodes : [node('sub:none', '(none)', '#fff')] },
        { id: 'act', title: 'Facts', nodes: actionNodes.length ? actionNodes : [node('fact:none', '(none)', '#fff')] },
        { id: 'obj', title: 'Objects', nodes: objNodes.length ? objNodes : [node('obj:none', '(none)', '#fff')] }
      ],
      edges,
      nodeFactMap,
      scopeValidation
    };
  })();

  $: selectedFacts = (() => {
    if (!selectedNodeId) return [] as typeof facts;
    const ids = graph.nodeFactMap?.get(selectedNodeId);
    if (!ids?.size) return [] as typeof facts;
    return facts.filter((f) => ids.has(f.fact_id));
  })();
  $: selectedEventIds = new Set(selectedFacts.map((f) => String(f.event_id || '')));
  $: selectedFactIds = new Set(selectedFacts.map((f) => String(f.fact_id || '')));
  $: selectedPropositions = (data.payload.propositions ?? []).filter(
    (prop) =>
      selectedEventIds.has(String(prop.event_id || '')) ||
      (prop.source_fact_id ? selectedFactIds.has(String(prop.source_fact_id)) : false)
  );
  $: selectedPropositionLinks = (data.payload.proposition_links ?? []).filter((link) =>
    selectedEventIds.has(String(link.event_id || ''))
  );
  $: propositionById = new Map(selectedPropositions.map((prop) => [prop.proposition_id, prop]));

  afterUpdate(() => {
    if (!contextBox || !selectedNodeId || !selectedFacts.length) return;
    const key = `${selectedNodeId}:${selectedFacts[0]?.fact_id ?? ''}`;
    if (!key || key === lastScrollKey) return;
    lastScrollKey = key;
    const first = selectedFacts[0];
    if (!first) return;
    const el = contextBox.querySelector(`[data-fact-id="${first.fact_id}"]`);
    if (el && 'scrollIntoView' in el) (el as HTMLElement).scrollIntoView({ block: 'center' });
  });
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
    {#if data.payload.diagnostics}
      <div class="mt-2 font-mono text-[10px] text-ink-800/70">
        events={data.payload.diagnostics.event_count}
        rows_raw={data.payload.diagnostics.raw_fact_rows}
        rows_out={data.payload.diagnostics.output_fact_rows}
        source={data.payload.diagnostics.fact_row_source}
      </div>
    {/if}

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
      <label class="flex items-center gap-2">
        <span class="text-ink-800/70">Importance</span>
        <select bind:value={importanceProfile} class="rounded-md border border-ink-950/15 bg-white px-2 py-1 text-sm">
          <option value="entropy_role_section_v1">entropy_role_section_v1</option>
          <option value="none">none</option>
        </select>
      </label>
      <a
        class="rounded-md border border-ink-950/15 px-2 py-1 text-xs text-ink-950 hover:border-ink-950/30 hover:bg-ink-950/[0.03]"
        href={`/graphs/wiki-timeline-aoo-all?source=${encodeURIComponent(data.source ?? 'hca')}`}
      >
        Open AAO-all
      </a>
    </div>
    <div class="mt-2 font-mono text-[10px] text-ink-800/70">
      scope_validator={graph.scopeValidation.ok ? 'ok' : 'leak'}
      leaks={graph.scopeValidation.leakCount}
      profile={importanceProfile}
    </div>
    {#if !graph.scopeValidation.ok}
      <div class="mt-1 rounded border border-red-300/60 bg-red-50 px-2 py-1 font-mono text-[10px] text-red-800">
        {graph.scopeValidation.sample.join(' | ')}
      </div>
    {/if}
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
    width={graphWidth}
    height={GRAPH_HEIGHT}
    colGap={GRAPH_COL_GAP}
    leftPad={GRAPH_LEFT_PAD}
    fitToWidth={false}
    scrollWhenOverflow={true}
    viewportResetKey={graphViewportKey}
    on:nodeSelect={(e) => (selectedNodeId = (e as CustomEvent<{ nodeId: string }>).detail.nodeId)}
  />

  <Panel>
    <div class="text-xs uppercase tracking-[0.28em] text-ink-800/70">Context</div>
    {#if !selectedNodeId}
      <div class="mt-2 text-xs text-ink-800/70">Click a node to inspect matching linearized facts.</div>
    {:else if !selectedFacts.length}
      <div class="mt-2 text-xs text-ink-800/70">No facts for current selection.</div>
    {:else}
      <div class="mt-2 max-h-[340px] overflow-auto rounded-lg border border-ink-950/10 bg-white" bind:this={contextBox}>
        {#each selectedFacts.slice(0, 120) as f (f.fact_id)}
          <div class="border-b border-ink-950/10 p-3 last:border-b-0" data-fact-id={f.fact_id}>
            <div class="flex flex-wrap items-center justify-between gap-2">
              <div class="font-mono text-[10px] text-ink-800/60">{keyFromAnchor(f.anchor, 'day')} {f.fact_id}</div>
              <div class="font-mono text-[10px] text-ink-800/60">event={f.event_id} section={f.section || '(n/a)'} anchor={f.anchor_source}</div>
            </div>
            {#if f.prev_fact_ids?.length || f.next_fact_ids?.length}
              <div class="mt-1 font-mono text-[10px] text-ink-800/65">
                {#if f.prev_fact_ids?.length}prev={f.prev_fact_ids.join(', ')} {/if}
                {#if f.next_fact_ids?.length}next={f.next_fact_ids.join(', ')} {/if}
                {#if f.chain_kinds?.length}kind={f.chain_kinds.join(', ')}{/if}
              </div>
            {/if}
            {#if f.event_anchor}
              <div class="mt-1 font-mono text-[10px] text-amber-900/70">
                event_date={keyFromAnchor(f.event_anchor, 'day')} ({f.event_anchor.text || 'date'})
              </div>
            {/if}
            <div class="mt-2 text-[11px] text-ink-950">
              {#if f.party}<span class="rounded bg-emerald-50 px-1.5 py-0.5 font-mono">{f.party}</span>{/if}
              {#each f.subjects as s}
                <span class="ml-1 rounded bg-emerald-100 px-1.5 py-0.5 font-mono">[{s}]</span>
              {/each}
              <span class="ml-1 rounded bg-amber-100 px-1.5 py-0.5 font-mono">[{actionLabel(f.action, f.negation)}]</span>
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

  <Panel>
    <div class="text-xs uppercase tracking-[0.28em] text-ink-800/70">Propositions</div>
    <div class="mt-2 text-xs text-ink-800/65">
      Proposition-scoped reasoning overlay. Additive to facts; authoritative only for bounded debug/review.
    </div>
    {#if !selectedNodeId}
      <div class="mt-2 text-xs text-ink-800/70">Select a node to inspect event-local propositions and proposition links.</div>
    {:else if !selectedPropositions.length}
      <div class="mt-2 text-xs text-ink-800/70">No proposition rows for the current fact/event selection.</div>
    {:else}
      <div class="mt-3 space-y-3">
        {#each selectedPropositions as prop (prop.proposition_id)}
          <div class="rounded-lg border border-ink-950/10 bg-white p-3">
            <div class="flex flex-wrap items-center justify-between gap-2">
              <div class="font-mono text-[10px] text-ink-800/60">{prop.proposition_id}</div>
              <div class="flex flex-wrap items-center gap-2 font-mono text-[10px] text-ink-800/65">
                <span>{prop.proposition_kind}</span>
                <span>event={prop.event_id}</span>
                {#if prop.source_fact_id}<span>fact={prop.source_fact_id}</span>{/if}
              </div>
            </div>
            <div class="mt-2 flex flex-wrap items-center gap-2 text-[11px] text-ink-950">
              <span class="rounded bg-amber-100 px-1.5 py-0.5 font-mono">
                [{propositionLabel(prop.predicate_key, prop.negation)}]
              </span>
              {#if prop.source_signal}
                <span class="rounded bg-sky-50 px-1.5 py-0.5 font-mono text-sky-900">{prop.source_signal}</span>
              {/if}
            </div>
            {#if prop.arguments.length}
              <div class="mt-2 flex flex-wrap items-center gap-2 text-[11px] text-ink-950">
                {#each prop.arguments as arg}
                  <span class="rounded bg-slate-100 px-1.5 py-0.5 font-mono">[{arg.role}: {arg.value}]</span>
                {/each}
              </div>
            {/if}
            {#if prop.receipts.length}
              <div class="mt-2 flex flex-wrap items-center gap-2 font-mono text-[10px] text-ink-800/65">
                {#each prop.receipts as receipt}
                  <span class="rounded bg-ink-950/[0.04] px-1.5 py-0.5">{receipt.kind}={receipt.value}</span>
                {/each}
              </div>
            {/if}
            {#if prop.anchor_text}
              <div class="mt-2 text-sm text-ink-950">{prop.anchor_text}</div>
            {/if}
            {#if selectedPropositionLinks.some((link) => link.source_proposition_id === prop.proposition_id || link.target_proposition_id === prop.proposition_id)}
              <div class="mt-3 space-y-1 font-mono text-[10px] text-ink-800/70">
                {#each selectedPropositionLinks.filter((link) => link.source_proposition_id === prop.proposition_id || link.target_proposition_id === prop.proposition_id) as link (link.link_id)}
                  <div class="rounded border border-ink-950/8 bg-ink-950/[0.02] px-2 py-1">
                    {#if link.source_proposition_id === prop.proposition_id}
                      <span>{link.link_kind} -> {propositionById.get(link.target_proposition_id)?.predicate_key ?? link.target_proposition_id}</span>
                    {:else}
                      <span>{link.link_kind} {'<-'} {propositionById.get(link.source_proposition_id)?.predicate_key ?? link.source_proposition_id}</span>
                    {/if}
                  </div>
                {/each}
              </div>
            {/if}
          </div>
        {/each}
      </div>
    {/if}
  </Panel>
</div>
