<script lang="ts" context="module">
  export type LayerNode = {
    id: string;
    label: string;
    color?: string;
    tooltip?: string;
    fullLabel?: string;
    // Optional view-layer emphasis scaling (truth-neutral).
    scale?: number;
  };

  export type LayeredEdge = {
    from: string;
    to: string;
    label?: string;
    kind?: 'role' | 'sequence' | 'evidence' | 'context';
  };
</script>

<script lang="ts">
  import GraphViewport from '$lib/ui/GraphViewport.svelte';
  import { createEventDispatcher } from 'svelte';

  export let layers: Array<{ id: string; title: string; nodes: LayerNode[] }> = [];
  export let edges: LayeredEdge[] = [];

  export let width = 1200;
  export let height = 820;
  export let fitToWidth = true;
  export let scrollWhenOverflow = false;
  export let viewportResetKey: string | number = '';

  export let colGap = 200;
  export let leftPad = 70;
  export let topPad = 60;

  export let nodeW = 190;
  export let nodeH = 18;
  export let expandedNodeW = 420;
  export let padY = 10;
  export let fontSize = 10;

  type Pt = { x: number; y: number };

  let expandedId: string | null = null;
  const dispatch = createEventDispatcher<{ nodeSelect: { nodeId: string } }>();
  $: edgeCounts = (() => {
    let evidence = 0;
    let context = 0;
    for (const e of edges) {
      if (e.kind === 'evidence') evidence += 1;
      else if (e.kind === 'context') context += 1;
    }
    return { evidence, context };
  })();

  function isExpanded(n: LayerNode): boolean {
    return Boolean(expandedId) && n.id === expandedId;
  }

  function displayLabel(n: LayerNode): string {
    return isExpanded(n) ? n.fullLabel ?? n.label : n.label;
  }

  function wrapLines(text: string, approxCharsPerLine: number, maxLines: number): string[] {
    const t = String(text ?? '').trim();
    if (!t) return [''];
    const words = t.split(/\s+/g);
    const lines: string[] = [];
    let cur = '';
    for (const w of words) {
      const next = cur ? cur + ' ' + w : w;
      if (next.length <= approxCharsPerLine) {
        cur = next;
      } else {
        if (cur) lines.push(cur);
        cur = w;
      }
      if (lines.length >= maxLines) break;
    }
    if (lines.length < maxLines && cur) lines.push(cur);
    if (lines.length === maxLines && words.join(' ').length > lines.join(' ').length) {
      lines[lines.length - 1] = (lines[lines.length - 1] ?? '').replace(/\.*$/, '') + '...';
    }
    return lines.length ? lines : [''];
  }

  function nodeWidth(n: LayerNode): number {
    const s = Math.max(0.75, Math.min(2.2, Number(n.scale ?? 1)));
    return (isExpanded(n) ? expandedNodeW : nodeW) * s;
  }

  function nodeLines(n: LayerNode): string[] {
    const w = nodeWidth(n);
    // Heuristic: average glyph width ~= 0.62em; keep a little padding for the left margin.
    const chars = Math.max(18, Math.floor((w - 18) / (fontSize * 0.62)));
    return isExpanded(n) ? wrapLines(displayLabel(n), chars, 6) : [displayLabel(n)];
  }

  function nodeHeight(n: LayerNode): number {
    const lines = nodeLines(n);
    const s = Math.max(0.75, Math.min(2.2, Number(n.scale ?? 1)));
    if (!isExpanded(n)) return nodeH * s;
    // Keep a compact but readable leading.
    return Math.max(nodeH * s, 6 + lines.length * (fontSize + 3));
  }

  function findLayerIndex(nodeId: string): number {
    for (let i = 0; i < layers.length; i++) {
      const layer = layers[i];
      if (layer?.nodes?.some((n) => n.id === nodeId)) return i;
    }
    return -1;
  }

  function neighborsOf(nodeId: string): Set<string> {
    const s = new Set<string>();
    for (const e of edges) {
      if (e.kind === 'evidence' || e.kind === 'context') continue;
      if (e.from === nodeId) s.add(e.to);
      if (e.to === nodeId) s.add(e.from);
    }
    return s;
  }

  function centeredOrder(nodes: LayerNode[], focusId: string, neighborIds?: Set<string>): LayerNode[] {
    // Stable-ish ordering: put focus (or neighbors) near the center, not the top.
    if (!nodes.length) return nodes;

    const isMid = (n: LayerNode) => (n.id === focusId ? 2 : neighborIds?.has(n.id) ? 1 : 0);
    const mids = nodes.filter((n) => isMid(n) > 0);
    const rest = nodes.filter((n) => isMid(n) === 0);

    const half = Math.floor(rest.length / 2);
    const a = rest.slice(0, half);
    const b = rest.slice(half);
    return [...a, ...mids, ...b];
  }

  $: orderedLayers = (() => {
    const exp = expandedId;
    if (!exp) return layers;
    const idx = findLayerIndex(exp);
    const nbrs = neighborsOf(exp);
    return layers.map((layer, i) => {
      if (!layer?.nodes?.length) return layer;
      if (i === idx) return { ...layer, nodes: centeredOrder(layer.nodes, exp) };
      if (i === idx - 1 || i === idx + 1) return { ...layer, nodes: centeredOrder(layer.nodes, exp, nbrs) };
      return layer;
    });
  })();

  function layout(): Map<string, Pt> {
    const m = new Map<string, Pt>();
    const cols = Math.max(1, orderedLayers.length);
    const usableW = width - leftPad * 2;
    // If horizontal scrolling is enabled, keep a stable requested column gap
    // rather than compressing lanes to fit within `width`.
    const stepX = cols <= 1 ? 0 : scrollWhenOverflow ? colGap : Math.min(colGap, usableW / (cols - 1));

    orderedLayers.forEach((layer, i) => {
      const x = leftPad + i * stepX;
      const usableH = height - topPad * 2;
      const nodes = layer.nodes ?? [];

      const heights = nodes.map((n) => nodeHeight(n));
      const total = heights.reduce((acc, h) => acc + h, 0) + Math.max(0, nodes.length - 1) * padY;
      const startY = topPad + Math.max(0, (usableH - total) / 2);

      let y = startY;
      nodes.forEach((n, j) => {
        m.set(n.id, { x, y });
        y += (heights[j] ?? nodeH) + padY;
      });
    });

    return m;
  }

  $: pos = layout();

  function edgePath(a: Pt, aw: number, ah: number, b: Pt, bh: number): string {
    const x1 = a.x + aw;
    const y1 = a.y + ah / 2;
    const x2 = b.x;
    const y2 = b.y + bh / 2;
    const dx = Math.max(40, (x2 - x1) * 0.55);
    return `M ${x1} ${y1} C ${x1 + dx} ${y1}, ${x2 - dx} ${y2}, ${x2} ${y2}`;
  }

  function edgeStroke(e: LayeredEdge): { stroke: string; w: number; dasharray?: string } {
    // NOTE: dashed strokes look great, but they're expensive when the graph is dense.
    // We keep them for small graphs and for "hot" edges when a node is expanded.
    const DASH_EVIDENCE_LIMIT = 250;
    // Context edges (Source/Lens -> action) tend to connect broadly; be more conservative.
    const DASH_CONTEXT_LIMIT = 120;
    const allowDashedEvidence = edgeCounts.evidence <= DASH_EVIDENCE_LIMIT;
    const allowDashedContext = edgeCounts.context <= DASH_CONTEXT_LIMIT;

    if (e.kind === 'evidence') {
      if (!expandedId)
        return allowDashedEvidence ? { stroke: 'rgba(44, 96, 140, 0.42)', w: 1.1, dasharray: '3 4' } : { stroke: 'rgba(44, 96, 140, 0.30)', w: 1.05 };
      const hot = e.from === expandedId || e.to === expandedId;
      return hot
        ? { stroke: 'rgba(44, 96, 140, 0.58)', w: 1.4, dasharray: '3 4' }
        : { stroke: 'rgba(44, 96, 140, 0.24)', w: 0.95 };
    }
    if (e.kind === 'sequence') {
      if (!expandedId) return { stroke: 'rgba(10,10,10,0.26)', w: 1.25 };
      const hot = e.from === expandedId || e.to === expandedId;
      return hot ? { stroke: 'rgba(10,10,10,0.50)', w: 1.9 } : { stroke: 'rgba(10,10,10,0.20)', w: 1.15 };
    }
    if (e.kind === 'context') {
      // Used for cross-lane "context" links (e.g. Source/Lens -> action). Prefer dashed only when sparse.
      if (!expandedId)
        return allowDashedContext ? { stroke: 'rgba(79, 70, 229, 0.34)', w: 1.05, dasharray: '2 5' } : { stroke: 'rgba(79, 70, 229, 0.22)', w: 1.0 };
      const hot = e.from === expandedId || e.to === expandedId;
      return hot
        ? { stroke: 'rgba(79, 70, 229, 0.52)', w: 1.3, dasharray: '2 5' }
        : { stroke: 'rgba(79, 70, 229, 0.18)', w: 0.92 };
    }
    if (!expandedId) return { stroke: 'rgba(10,10,10,0.22)', w: 1.2 };
    const hot = e.from === expandedId || e.to === expandedId;
    if (hot) return { stroke: 'rgba(10,10,10,0.45)', w: 1.8 };
    return { stroke: 'rgba(10,10,10,0.18)', w: 1.1 };
  }

  function toggleExpand(nodeId: string) {
    expandedId = expandedId === nodeId ? null : nodeId;
    dispatch('nodeSelect', { nodeId });
  }

  function findNode(nodeId: string): LayerNode | null {
    for (const layer of orderedLayers) {
      const hit = layer.nodes.find((n) => n.id === nodeId);
      if (hit) return hit;
    }
    return null;
  }

  function onNodeKeydown(e: KeyboardEvent, nodeId: string) {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      toggleExpand(nodeId);
    }
  }
</script>

<GraphViewport {width} {height} {fitToWidth} {scrollWhenOverflow} resetKey={viewportResetKey}>
  <g>
    {#each edges as e (e.from + '->' + e.to)}
      {@const a = pos.get(e.from)}
      {@const b = pos.get(e.to)}
      {#if a && b}
        {@const an = findNode(e.from)}
        {@const bn = findNode(e.to)}
        {@const aw = an ? nodeWidth(an) : nodeW}
        {@const ah = an ? nodeHeight(an) : nodeH}
        {@const bh = bn ? nodeHeight(bn) : nodeH}
        {@const st = edgeStroke(e)}
        <path d={edgePath(a, aw, ah, b, bh)} fill="none" stroke={st.stroke} stroke-width={st.w} stroke-dasharray={st.dasharray} />
        {#if e.label}
          <text
            x={(a.x + b.x) / 2}
            y={(a.y + b.y) / 2}
            font-size="9"
            fill="rgba(0,0,0,0.55)"
          >
            {e.label}
          </text>
        {/if}
      {/if}
    {/each}
  </g>

  <g>
    {#each orderedLayers as layer (layer.id)}
      {@const col = pos.get(layer.nodes[0]?.id ?? '')}
      {#if col}
        <text x={col.x} y={30} font-size="10" fill="rgba(0,0,0,0.60)">{layer.title}</text>
      {:else}
        <text x={leftPad} y={30} font-size="10" fill="rgba(0,0,0,0.60)">{layer.title}</text>
      {/if}
    {/each}
  </g>

  <g>
    {#each orderedLayers as layer (layer.id)}
      {#each layer.nodes as n (n.id)}
        {@const p = pos.get(n.id)}
        {#if p}
          {@const w = nodeWidth(n)}
          {@const h = nodeHeight(n)}
          {@const lines = nodeLines(n)}
          <g
            class="cursor-pointer"
            role="button"
            tabindex="0"
            aria-label="Toggle node details"
            on:pointerdown|stopPropagation
            on:click={() => toggleExpand(n.id)}
            on:keydown={(e) => onNodeKeydown(e, n.id)}
          >
            <rect
              x={p.x}
              y={p.y}
              width={w}
              height={h}
              rx="6"
              fill={n.color ?? '#f6f6f6'}
              stroke={expandedId === n.id ? 'rgba(0,0,0,0.25)' : 'rgba(0,0,0,0.12)'}
            />
            <title>{n.tooltip ?? n.fullLabel ?? n.label}</title>
            {#if lines.length <= 1}
              <text x={p.x + 8} y={p.y + 12} font-size={fontSize} fill="rgba(0,0,0,0.88)">{lines[0]}</text>
            {:else}
              {#each lines as line, i (n.id + ':' + i)}
                <text x={p.x + 8} y={p.y + 14 + i * (fontSize + 3)} font-size={fontSize} fill="rgba(0,0,0,0.88)">{line}</text>
              {/each}
            {/if}
          </g>
        {/if}
      {/each}
    {/each}
  </g>
</GraphViewport>
