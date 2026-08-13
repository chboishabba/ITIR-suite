<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import MarkdownLite from '$lib/ui/MarkdownLite.svelte';
  import type {
    DocumentHighlight,
    DocumentHighlightKind,
    DocumentHighlightSource,
    DocumentLineSelectEvent,
    DocumentViewerProps
  } from './document-viewer.types';
  export type { DocumentViewerProps };

  export let title = 'Document';
  export let text = '';
  export let mode: 'plain' | 'markdown' = 'plain';
  export let showSearch = true;
  export let showLineNumbers = true;
  export let maxHeightPx = 520;
  export let placeholder = 'Search text...';
  export let ariaLabel: string | null = null;
  export let searchAriaLabel = 'Search document text';
  export let highlights: DocumentHighlight[] = [];
  export let selectedHighlightKey: string | null = null;


  const dispatch = createEventDispatcher<{ lineSelect: DocumentLineSelectEvent }>();

  let query = '';
  let selectedLine = -1;
  const searchInputId = `document-viewer-search-${Math.random().toString(36).slice(2, 8)}`;

  function splitLines(value: string): string[] {
    return String(value ?? '').split(/\r?\n/);
  }

  function escapeHtml(v: string): string {
    return String(v ?? '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function hexToRgb(color: string): { r: number; g: number; b: number } | null {
    const raw = String(color ?? '').trim().replace('#', '');
    if (!/^[0-9a-fA-F]{6}$/.test(raw)) return null;
    return {
      r: Number.parseInt(raw.slice(0, 2), 16),
      g: Number.parseInt(raw.slice(2, 4), 16),
      b: Number.parseInt(raw.slice(4, 6), 16)
    };
  }

  function highlightStyle(
    color: string,
    opacity: number,
    kind: DocumentHighlightKind,
    isSelected: boolean,
    source: DocumentHighlightSource
  ): string {
    const rgb = hexToRgb(color);
    if (!rgb) return '';
    const alpha =
      kind === 'active'
        ? Math.max(0.22, opacity * 0.55)
        : kind === 'relation_peer'
          ? Math.max(0.16, opacity * 0.4)
          : Math.max(0.08, opacity * 0.22);
    const ringAlpha = isSelected ? Math.max(0.45, alpha * 1.4) : Math.max(0.18, alpha * 1.1);
    const outlineStyle =
      source === 'mention'
        ? `box-shadow: inset 0 0 0 1.4px rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, ${Math.max(0.48, ringAlpha)});`
        : source === 'receipt'
          ? `box-shadow: inset 0 -2px 0 rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, ${Math.max(0.38, ringAlpha)});`
          : source === 'label_fallback'
            ? `box-shadow: inset 0 0 0 1px rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, ${Math.max(0.22, ringAlpha * 0.85)}); background-image: linear-gradient(135deg, rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, 0.08) 25%, transparent 25%, transparent 50%, rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, 0.08) 50%, rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, 0.08) 75%, transparent 75%, transparent); background-size: 0.45rem 0.45rem;`
            : `box-shadow: inset 0 0 0 1px rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, ${Math.max(0.14, ringAlpha * 0.7)});`;
    return `background-color: rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, ${alpha}); ${outlineStyle} border-radius: 0.2rem;${kind === 'active' ? ' font-weight: 600;' : ''}`;
  }

  function searchRanges(src: string, needle: string): Array<{ start: number; end: number }> {
    const out: Array<{ start: number; end: number }> = [];
    const n = String(needle ?? '').trim();
    if (!n) return out;
    const lower = src.toLowerCase();
    const hit = n.toLowerCase();
    let i = 0;
    while (i < src.length) {
      const j = lower.indexOf(hit, i);
      if (j < 0) break;
      out.push({ start: j, end: j + n.length });
      i = j + n.length;
    }
    return out;
  }

  function lineHighlights(lineStart: number, lineEnd: number): DocumentHighlight[] {
    return (highlights ?? [])
      .filter((row) => Number(row.charEnd) > lineStart && Number(row.charStart) < lineEnd)
      .map((row) => ({
        ...row,
        charStart: Math.max(0, Number(row.charStart) - lineStart),
        charEnd: Math.min(lineEnd - lineStart, Number(row.charEnd) - lineStart)
      }))
      .filter((row) => row.charEnd > row.charStart);
  }

  function highlightHtml(line: string, needle: string, lineStart: number): string {
    const src = String(line ?? '');
    if (!src) return '';
    const localHighlights = lineHighlights(lineStart, lineStart + src.length);
    const localSearch = searchRanges(src, needle);
    if (!localHighlights.length && !localSearch.length) return escapeHtml(src);

    const boundaries = new Set<number>([0, src.length]);
    for (const row of localHighlights) {
      boundaries.add(row.charStart);
      boundaries.add(row.charEnd);
    }
    for (const row of localSearch) {
      boundaries.add(row.start);
      boundaries.add(row.end);
    }
    const points = Array.from(boundaries).sort((a, b) => a - b);
    const kindPriority: Record<DocumentHighlightKind, number> = { active: 3, relation_peer: 2, echo: 1 };
    let out = '';
    for (let i = 0; i < points.length - 1; i += 1) {
      const start = points[i] ?? 0;
      const end = points[i + 1] ?? 0;
      if (end <= start) continue;
      const segment = src.slice(start, end);
      const matchingHighlight = [...localHighlights]
        .filter((row) => row.charStart < end && row.charEnd > start)
        .sort((a, b) => {
          const ak = kindPriority[(a.kind ?? 'echo') as DocumentHighlightKind] ?? 0;
          const bk = kindPriority[(b.kind ?? 'echo') as DocumentHighlightKind] ?? 0;
          return bk - ak || Number(b.opacity ?? 0) - Number(a.opacity ?? 0);
        })[0];
      const isSearch = localSearch.some((row) => row.start < end && row.end > start);
      const styles: string[] = [];
      if (matchingHighlight) {
        styles.push(
          highlightStyle(
            String(matchingHighlight.color ?? '#475569'),
            Number(matchingHighlight.opacity ?? 0.3),
            (matchingHighlight.kind ?? 'echo') as DocumentHighlightKind,
            selectedHighlightKey === matchingHighlight.key,
            (matchingHighlight.source ?? 'event_span') as DocumentHighlightSource
          )
        );
      }
      if (isSearch) {
        styles.push('text-decoration: underline 2px rgba(217, 119, 6, 0.65); text-underline-offset: 0.16rem;');
      }
      const style = styles.filter(Boolean).join(' ');
      out += style ? `<span style="${style}">${escapeHtml(segment)}</span>` : escapeHtml(segment);
    }
    return out;
  }

  $: lines = splitLines(text);
  $: offsets = (() => {
    const out: number[] = [];
    let pos = 0;
    for (const line of lines) {
      out.push(pos);
      pos += String(line ?? '').length + 1;
    }
    return out;
  })();
  $: filtered = (() => {
    const q = query.trim().toLowerCase();
    if (!q || mode === 'markdown') return lines.map((line, idx) => ({ idx, line }));
    const out: Array<{ idx: number; line: string }> = [];
    for (let i = 0; i < lines.length; i += 1) {
      const line = lines[i] ?? '';
      if (line.toLowerCase().includes(q)) out.push({ idx: i, line });
    }
    return out;
  })();
  $: resultCount = filtered.length;
  $: selectedLineAnnouncement =
    selectedLine >= 0 && lines[selectedLine]
      ? `Selected document line ${selectedLine + 1}: ${lines[selectedLine] ?? ''}`
      : 'No document line selected.';
  $: resolvedSearchAriaLabel = (searchAriaLabel || ariaLabel || 'Search document text').trim();

  function selectLine(idx: number): void {
    if (idx < 0 || idx >= lines.length) return;
    selectedLine = idx;
    const line = lines[idx] ?? '';
    const charStart = offsets[idx] ?? 0;
    dispatch('lineSelect', {
      lineNumber: idx + 1,
      text: line,
      charStart,
      charEnd: charStart + line.length
    });
  }
</script>

<div class="rounded-2xl bg-paper-50 shadow-crisp ring-1 ring-ink-900/10" role="region" aria-label={title}>
  <div class="flex items-center justify-between gap-3 border-b border-ink-900/10 px-4 py-3">
    <div class="font-display text-sm tracking-tight text-ink-950">{title}</div>
    <div class="font-mono text-[10px] text-ink-800/70">
      lines={lines.length} {#if showSearch && query.trim()}matches={resultCount}{/if}
    </div>
  </div>

  {#if showSearch}
    <div class="border-b border-ink-900/10 px-4 py-2">
      <label class="sr-only" for={searchInputId} aria-label="Search document text">{resolvedSearchAriaLabel}</label>
      <input
        id={searchInputId}
        class="w-full rounded-lg bg-paper-100 px-3 py-2 text-sm ring-1 ring-ink-900/10"
        bind:value={query}
        placeholder={placeholder}
        aria-label={resolvedSearchAriaLabel}
      />
    </div>
  {/if}

  <div class="sr-only" role="status" aria-live="polite" aria-atomic="true">
    {selectedLineAnnouncement}
  </div>

  <div class="overflow-auto px-2 py-2" style={`max-height:${Math.max(180, Math.floor(maxHeightPx))}px`}>
    {#if mode === 'markdown'}
      <div class="px-2 py-1 text-sm text-ink-950">
        <MarkdownLite text={text} />
      </div>
    {:else if !filtered.length}
      <div class="px-3 py-2 text-xs text-ink-800/70">No lines match the current filter.</div>
    {:else}
      <div class="space-y-0.5">
        {#each filtered as row (row.idx)}
          <button
            type="button"
            aria-label={`Select line ${row.idx + 1}`}
            aria-pressed={selectedLine === row.idx}
            class={`grid w-full grid-cols-[auto_1fr] items-start gap-3 rounded-md px-2 py-1 text-left hover:bg-ink-950/[0.03] ${
              selectedLine === row.idx ? 'bg-amber-50 ring-1 ring-amber-300/50' : ''
            }`}
            on:click={() => selectLine(row.idx)}
          >
            {#if showLineNumbers}
              <span class="w-10 text-right font-mono text-[10px] text-ink-800/60">{row.idx + 1}</span>
            {:else}
              <span class="w-2"></span>
            {/if}
            <span class="min-w-0 whitespace-pre-wrap break-words font-mono text-[12px] leading-relaxed text-ink-950">
              {@html highlightHtml(row.line, query, offsets[row.idx] ?? 0)}
            </span>
          </button>
        {/each}
      </div>
    {/if}
  </div>
</div>
