<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import MarkdownLite from '$lib/ui/MarkdownLite.svelte';
  type DocumentLineSelectEvent = {
    lineNumber: number;
    text: string;
    charStart: number;
    charEnd: number;
  };

  export let title = 'Document';
  export let text = '';
  export let mode: 'plain' | 'markdown' = 'plain';
  export let showSearch = true;
  export let showLineNumbers = true;
  export let maxHeightPx = 520;
  export let placeholder = 'Search text...';

  const dispatch = createEventDispatcher<{ lineSelect: DocumentLineSelectEvent }>();

  let query = '';
  let selectedLine = -1;

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

  function highlightHtml(line: string, needle: string): string {
    const src = String(line ?? '');
    const n = String(needle ?? '').trim();
    if (!n) return escapeHtml(src);
    const lower = src.toLowerCase();
    const hit = n.toLowerCase();
    let i = 0;
    let out = '';
    while (i < src.length) {
      const j = lower.indexOf(hit, i);
      if (j < 0) {
        out += escapeHtml(src.slice(i));
        break;
      }
      if (j > i) out += escapeHtml(src.slice(i, j));
      out += `<mark class="rounded bg-amber-200/70 px-0.5">${escapeHtml(src.slice(j, j + n.length))}</mark>`;
      i = j + n.length;
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

<div class="rounded-2xl bg-paper-50 shadow-crisp ring-1 ring-ink-900/10">
  <div class="flex items-center justify-between gap-3 border-b border-ink-900/10 px-4 py-3">
    <div class="font-display text-sm tracking-tight text-ink-950">{title}</div>
    <div class="font-mono text-[10px] text-ink-800/70">
      lines={lines.length} {#if showSearch && query.trim()}matches={resultCount}{/if}
    </div>
  </div>

  {#if showSearch}
    <div class="border-b border-ink-900/10 px-4 py-2">
      <input
        class="w-full rounded-lg bg-paper-100 px-3 py-2 text-sm ring-1 ring-ink-900/10"
        bind:value={query}
        placeholder={placeholder}
      />
    </div>
  {/if}

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
              {@html highlightHtml(row.line, query)}
            </span>
          </button>
        {/each}
      </div>
    {/if}
  </div>
</div>
