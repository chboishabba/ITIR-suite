<script lang="ts">
  import Section from '$lib/ui/Section.svelte';
  import type { WaterfallSegment } from '../adapters/dashboard';
  import { createWaterfallPrefs, hydrateWaterfallPrefs, colorFor, type WaterfallAlgoName, type WaterfallPaletteName } from '../hooks/waterfallColors';
  import { onMount } from 'svelte';
  import ToolCallBlock from '$lib/chat/ToolCallBlock.svelte';
  import { parseToolCallText } from '$lib/chat/parseToolCall';
  import { page } from '$app/stores';

  // Initial, intentionally simple visualization:
  // consecutive segments grouped by hour+thread rendered as a striped bar,
  // with palette/algo settings persisted to the same localStorage keys as the legacy HTML.
  export let segments: WaterfallSegment[];

  const prefs = createWaterfallPrefs();

  const paletteOptions: WaterfallPaletteName[] = ['viridis', 'magma', 'plasma', 'inferno', 'custom'];
  const algoOptions: WaterfallAlgoName[] = ['thread', 'hour', 'role', 'switch'];

  type WidthMode = 'time' | 'messages';
  let widthMode: WidthMode = 'time';
  let hover:
    | {
        hour: number;
        title: string;
        threadId: string;
        messageCount: number;
        durationSeconds: number;
        firstTs: string | null;
        lastTs: string | null;
        firstRole: string | null;
        lastRole: string | null;
      }
    | null = null;
  let hoverMsg: { ts: string; role: string; text: string } | null = null;
  let hoverLoading = false;
  const msgCache = new Map<string, { ts: string; role: string; text: string } | null>();
  let hoverTimer: number | null = null;

  type Pinned = {
    hour: number;
    title: string;
    threadId: string;
    messageCount: number;
    durationSeconds: number;
    firstTs: string | null;
    lastTs: string | null;
    firstRole: string | null;
    lastRole: string | null;
    segmentKey: string;
  };
  let pinned: Pinned | null = null;
  let pinnedMsg: { ts: string; role: string; text: string } | null = null;
  let pinnedLoading = false;

  let byHour: WaterfallSegment[][] = Array.from({ length: 24 }, () => []);
  let totals: number[] = Array.from({ length: 24 }, () => 0); // messages
  let maxTotal = 0;

  $: {
    byHour = Array.from({ length: 24 }, () => []);
    totals = Array.from({ length: 24 }, () => 0);
    for (const s of segments ?? []) {
      if (typeof s.hour !== 'number' || s.hour < 0 || s.hour > 23) continue;
      byHour[s.hour]!.push(s);
      totals[s.hour] = (totals[s.hour] ?? 0) + (s.messageCount ?? 0);
    }
    maxTotal = Math.max(0, ...totals);
  }

  function weight(s: WaterfallSegment): number {
    if (widthMode === 'messages') return Math.max(1, s.messageCount ?? 0);
    return Math.max(1, Math.round(s.durationSeconds ?? 0));
  }

  function fmtDur(s: number): string {
    const v = Math.max(0, Math.round(s));
    if (v >= 3600) return `${(v / 3600).toFixed(1)}h`;
    if (v >= 60) return `${Math.round(v / 60)}m`;
    return `${v}s`;
  }

  let custom = '';
  onMount(() => {
    // Avoid SSR/CSR hydration mismatch: apply stored prefs after mount.
    hydrateWaterfallPrefs(prefs, $prefs);
    custom = $prefs.custom;
  });

  function setPalette(palette: WaterfallPaletteName) {
    prefs.update((v) => ({ ...v, palette }));
  }
  function setAlgo(algo: WaterfallAlgoName) {
    prefs.update((v) => ({ ...v, algo }));
  }
  function applyCustom() {
    prefs.update((v) => ({ ...v, palette: 'custom', custom }));
  }
  function resetCustom() {
    custom = '';
    prefs.update((v) => ({ ...v, palette: 'viridis', custom: '' }));
  }

  function cacheKey(threadId: string, ts: string, range: { startTs: string | null; endTs: string | null } | null): string {
    if (range?.startTs || range?.endTs) return `${threadId}|range|${range?.startTs ?? ''}|${range?.endTs ?? ''}`;
    return `${threadId}|ts|${ts}`;
  }

  async function fetchMessageInto(
    kind: 'hover' | 'pinned',
    threadId: string,
    ts: string,
    range: { startTs: string | null; endTs: string | null } | null
  ): Promise<void> {
    const k = cacheKey(threadId, ts, range);
    if (msgCache.has(k)) {
      const v = msgCache.get(k) ?? null;
      if (kind === 'hover') {
        hoverMsg = v;
        hoverLoading = false;
      } else {
        pinnedMsg = v;
        pinnedLoading = false;
      }
      return;
    }
    if (kind === 'hover') {
      hoverLoading = true;
      hoverMsg = null;
    } else {
      pinnedLoading = true;
      pinnedMsg = null;
    }
    try {
      const u = new URL('/api/chat-message', window.location.origin);
      u.searchParams.set('threadId', threadId);
      if (range?.startTs || range?.endTs) {
        if (range?.startTs) u.searchParams.set('startTs', range.startTs);
        if (range?.endTs) u.searchParams.set('endTs', range.endTs);
      } else {
        u.searchParams.set('ts', ts);
      }
      const resp = await fetch(u.toString());
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const data = (await resp.json()) as any;
      const m = data?.message;
      const parsed =
        m && typeof m === 'object' && typeof m.ts === 'string' && typeof m.role === 'string' && typeof m.text === 'string'
          ? { ts: m.ts, role: m.role, text: m.text }
          : null;
      msgCache.set(k, parsed);
      if (kind === 'hover') hoverMsg = parsed;
      else pinnedMsg = parsed;
    } catch {
      msgCache.set(k, null);
      if (kind === 'hover') hoverMsg = null;
      else pinnedMsg = null;
    } finally {
      if (kind === 'hover') hoverLoading = false;
      else pinnedLoading = false;
    }
  }

  function segmentKeyFor(s: WaterfallSegment, idx: number): string {
    // Stable enough for UI pin/highlight; doesn't need to be globally unique across days.
    return `${s.hour}:${idx}:${s.threadId}:${s.firstTs ?? ''}:${s.lastTs ?? ''}`;
  }

  function pinSegment(s: WaterfallSegment, idx: number, hour: number): void {
    const segKey = segmentKeyFor(s, idx);
    pinned = {
      hour,
      title: (s.threadTitle ?? '(no title)').trim() || '(no title)',
      threadId: s.threadId,
      messageCount: s.messageCount,
      durationSeconds: s.durationSeconds,
      firstTs: s.firstTs ?? null,
      lastTs: s.lastTs ?? null,
      firstRole: s.firstRole ?? null,
      lastRole: s.lastRole ?? null,
      segmentKey: segKey
    };
    pinnedMsg = null;
    pinnedLoading = false;
    if (hoverTimer !== null) window.clearTimeout(hoverTimer);
    hoverTimer = null;

    const ts = (pinned.messageCount > 1 ? pinned.lastTs : pinned.firstTs) ?? null;
    if (ts) void fetchMessageInto('pinned', pinned.threadId, ts, { startTs: pinned.firstTs, endTs: pinned.lastTs });
  }

  function unpin(): void {
    pinned = null;
    pinnedMsg = null;
    pinnedLoading = false;
  }

  function threadHref(threadId: string, focusTs: string | null): string {
    const u = new URL($page.url);
    u.pathname = `/thread/${threadId}`;
    // Preserve date range when present.
    const start = $page.url.searchParams.get('start');
    const end = $page.url.searchParams.get('end');
    if (start) u.searchParams.set('start', start);
    else u.searchParams.delete('start');
    if (end) u.searchParams.set('end', end);
    else u.searchParams.delete('end');

    // Ask for a larger tail so "open at message" works for big threads within a range.
    u.searchParams.set('tail', '2000');
    if (focusTs) u.searchParams.set('focus_ts', focusTs);
    else u.searchParams.delete('focus_ts');
    return u.pathname + '?' + u.searchParams.toString();
  }
</script>

<Section title="Chat Flow Waterfall" subtitle="Grouped by hour+thread. Hour strip always fills width; per-hour volume shown separately.">
  <div slot="actions" class="flex flex-wrap items-center gap-2">
    <label class="text-xs uppercase tracking-widest text-ink-800/60" for="wf-palette">Palette</label>
    <select
      id="wf-palette"
      class="rounded-lg bg-paper-100 ring-1 ring-ink-900/10 px-2 py-1 text-sm"
      on:change={(e) => setPalette((e.currentTarget as HTMLSelectElement).value as WaterfallPaletteName)}
      value={$prefs.palette}
    >
      {#each paletteOptions as p}
        <option value={p}>{p}</option>
      {/each}
    </select>

    <label class="text-xs uppercase tracking-widest text-ink-800/60" for="wf-algo">Algo</label>
    <select
      id="wf-algo"
      class="rounded-lg bg-paper-100 ring-1 ring-ink-900/10 px-2 py-1 text-sm"
      on:change={(e) => setAlgo((e.currentTarget as HTMLSelectElement).value as WaterfallAlgoName)}
      value={$prefs.algo}
    >
      {#each algoOptions as a}
        <option value={a}>{a}</option>
      {/each}
    </select>

    <input
      class="min-w-[14rem] rounded-lg bg-paper-100 ring-1 ring-ink-900/10 px-3 py-1 text-sm font-mono"
      placeholder="custom colors: #111,#222,..."
      bind:value={custom}
    />
    <button class="rounded-lg bg-ink-900 text-paper-50 px-3 py-1 text-xs uppercase tracking-widest" type="button" on:click={applyCustom}>
      Apply
    </button>
    <button class="rounded-lg bg-paper-100 ring-1 ring-ink-900/10 px-3 py-1 text-xs uppercase tracking-widest" type="button" on:click={resetCustom}>
      Reset
    </button>
  </div>

  <div class="space-y-2">
    {#each Array.from({ length: 24 }, (_, i) => i) as h}
      {@const hourSegs = byHour[h] ?? []}
      {@const total = totals[h] ?? 0}
      <div class="flex items-center gap-3">
        <div class="w-10 text-right font-mono text-xs text-ink-800/60">{h}</div>
        <div class="w-24 shrink-0">
          <div
            class="h-2 w-full rounded bg-ink-900/10 overflow-hidden"
            title={`hour=${h} total=${total}`}
          >
            <div
              class="h-2 rounded bg-ink-900/40"
              style={`width:${maxTotal ? Math.round((total / maxTotal) * 100) : 0}%`}
            ></div>
          </div>
        </div>
	        <div class="flex-1 overflow-hidden rounded-lg bg-paper-100 ring-1 ring-ink-900/10">
	          <div class="flex h-6 w-full">
	            {#each hourSegs as s, idx (h + ':' + idx)}
	              {@const segKey = segmentKeyFor(s, idx)}
	              <button
	                type="button"
	                class={`h-full p-0 m-0 border-0 ${pinned?.segmentKey === segKey ? 'ring-2 ring-ink-950 ring-offset-2 ring-offset-paper-100 relative z-10' : ''}`}
	                style={`background:${colorFor({ hour: s.hour, role: s.role, switch: s.switch, threadIndex: s.threadIndex, threadStartHour: s.threadStartHour, defaultColor: s.colorHex }, $prefs)}; flex:${weight(s)} 0 0`}
	                title={`${s.threadTitle ?? '(no title)'}\n${s.threadId}\nmsgs=${s.messageCount} span_s=${Math.round(s.durationSeconds)} (hour=${h})`}
	                aria-label={`${(s.threadTitle ?? '(no title)').trim() || '(no title)'} ${s.threadId} msgs ${s.messageCount} span_s ${Math.round(s.durationSeconds)}`}
	                on:mouseenter={() => {
	                  if (pinned) return;
	                  hover = {
	                    hour: h,
	                    title: (s.threadTitle ?? '(no title)').trim() || '(no title)',
	                    threadId: s.threadId,
                    messageCount: s.messageCount,
                    durationSeconds: s.durationSeconds,
                    firstTs: s.firstTs ?? null,
                    lastTs: s.lastTs ?? null,
                    firstRole: s.firstRole ?? null,
                    lastRole: s.lastRole ?? null
                  };
	                  hoverMsg = null;
	                  hoverLoading = false;
	                  if (hoverTimer !== null) window.clearTimeout(hoverTimer);
	                  const ts = (hover.messageCount > 1 ? hover.lastTs : hover.firstTs) ?? null;
	                  if (ts) hoverTimer = window.setTimeout(() => fetchMessageInto('hover', hover!.threadId, ts, { startTs: hover!.firstTs, endTs: hover!.lastTs }), 60);
	                }}
	                on:mouseleave={() => {
	                  if (pinned) return;
	                  hover = null;
	                  hoverMsg = null;
	                  hoverLoading = false;
	                  if (hoverTimer !== null) window.clearTimeout(hoverTimer);
                  hoverTimer = null;
                }}
	                on:focus={() => {
	                  if (pinned) return;
	                  hover = {
	                    hour: h,
	                    title: (s.threadTitle ?? '(no title)').trim() || '(no title)',
	                    threadId: s.threadId,
                    messageCount: s.messageCount,
                    durationSeconds: s.durationSeconds,
                    firstTs: s.firstTs ?? null,
                    lastTs: s.lastTs ?? null,
                    firstRole: s.firstRole ?? null,
                    lastRole: s.lastRole ?? null
                  };
	                  hoverMsg = null;
	                  hoverLoading = false;
	                  if (hoverTimer !== null) window.clearTimeout(hoverTimer);
	                  const ts = (hover.messageCount > 1 ? hover.lastTs : hover.firstTs) ?? null;
	                  if (ts) hoverTimer = window.setTimeout(() => fetchMessageInto('hover', hover!.threadId, ts, { startTs: hover!.firstTs, endTs: hover!.lastTs }), 60);
	                }}
	                on:blur={() => {
	                  if (pinned) return;
	                  hover = null;
	                  hoverMsg = null;
	                  hoverLoading = false;
	                  if (hoverTimer !== null) window.clearTimeout(hoverTimer);
	                  hoverTimer = null;
	                }}
	                on:click={() => pinSegment(s, idx, h)}
	              ></button>
	            {/each}
	          </div>
	        </div>
      </div>
    {/each}
  </div>

  <!-- Keep hover info out of the waterfall area (no layout shift under cursor). -->
  <div
    class="mt-3 rounded-xl bg-paper-100 ring-1 ring-ink-900/10 px-4 py-3"
    style="min-height: 8.5rem;"
    aria-live="polite"
  >
    <div class="text-xs uppercase tracking-widest text-ink-800/60">{pinned ? 'Pinned' : 'Hover'}</div>
    {#if pinned}
      {@const pinnedToolCall = pinnedMsg ? parseToolCallText(pinnedMsg.text) : null}
      <div class="mt-1 flex items-start justify-between gap-3">
        <div class="min-w-0">
          <div class="text-sm text-ink-950 truncate" title={`${pinned.title}\n${pinned.threadId}`}>
            {pinned.title} <span class="font-mono text-ink-800/70">({pinned.threadId})</span>
          </div>
          <div class="mt-1 font-mono text-xs text-ink-800/70">
            pinned hour={pinned.hour} msgs={pinned.messageCount.toLocaleString()} span={fmtDur(pinned.durationSeconds)}
          </div>
        </div>
        <div class="shrink-0 flex items-center gap-2">
          <a
            class="rounded-lg bg-ink-900 text-paper-50 px-3 py-1 text-xs uppercase tracking-widest"
            href={threadHref(pinned.threadId, pinnedMsg?.ts ?? null)}
            target="_blank"
            rel="noreferrer"
            title="Open this thread in the thread viewer (new tab). Attempts to focus the pinned message."
          >
            Open thread
          </a>
          <button
            type="button"
            class="rounded-lg bg-paper-50 ring-1 ring-ink-900/10 px-3 py-1 text-xs uppercase tracking-widest"
            on:click={unpin}
          >
            Unpin
          </button>
        </div>
      </div>

      {#if pinnedLoading}
        <div class="mt-2 text-[12px] text-ink-800/60">Loading message…</div>
      {:else if pinnedMsg}
        <div class="mt-2 rounded-lg bg-paper-50 ring-1 ring-ink-900/10 px-3 py-2">
          <div class="flex flex-wrap items-center gap-2 font-mono text-[11px] text-ink-800/60">
            <span>{pinnedMsg.ts}</span>
            <span class="rounded-full px-2 py-1 ring-1 ring-ink-900/10 bg-paper-100 text-ink-900/80">role={pinnedMsg.role}</span>
            {#if pinned.messageCount > 1}
              <span>(latest in segment)</span>
            {/if}
            {#if pinned.lastTs && pinnedMsg.ts && pinned.lastTs.slice(0, 19) !== pinnedMsg.ts.slice(0, 19)}
              <span class="text-ink-800/60">(showing last non-empty)</span>
            {/if}
          </div>
          <div class="mt-2">
            {#if pinnedToolCall}
              <ToolCallBlock tool={pinnedToolCall.tool} payload={pinnedToolCall.payload} rawJson={pinnedToolCall.rawJson} parseError={pinnedToolCall.parseError} />
            {:else}
              {#if pinnedMsg.text && pinnedMsg.text.trim()}
                <pre class="max-h-[260px] overflow-auto overscroll-contain whitespace-pre-wrap break-words font-mono text-[12px] leading-relaxed text-ink-950">{pinnedMsg.text}</pre>
              {:else}
                <div class="font-mono text-[12px] leading-relaxed text-ink-800/60 italic">(empty message)</div>
              {/if}
            {/if}
          </div>
        </div>
      {:else}
        <div class="mt-2 text-[12px] text-ink-800/60">No message text available for this segment.</div>
      {/if}
    {:else if hover}
      {@const hoverToolCall = hoverMsg ? parseToolCallText(hoverMsg.text) : null}
      <div class="mt-1 text-sm text-ink-950 truncate" title={`${hover.title}\n${hover.threadId}`}>
        {hover.title} <span class="font-mono text-ink-800/70">({hover.threadId})</span>
      </div>
      <div class="mt-1 font-mono text-xs text-ink-800/70">
        hour={hover.hour} msgs={hover.messageCount.toLocaleString()} span={fmtDur(hover.durationSeconds)}
      </div>
      {#if hoverLoading}
        <div class="mt-2 text-[12px] text-ink-800/60">Loading message…</div>
      {:else if hoverMsg}
        <div class="mt-2 rounded-lg bg-paper-50 ring-1 ring-ink-900/10 px-3 py-2">
          <div class="flex flex-wrap items-center gap-2 font-mono text-[11px] text-ink-800/60">
            <span>{hoverMsg.ts}</span>
            <span class="rounded-full px-2 py-1 ring-1 ring-ink-900/10 bg-paper-100 text-ink-900/80">role={hoverMsg.role}</span>
            {#if hover.messageCount > 1}
              <span>(latest in segment)</span>
            {/if}
            {#if hover.lastTs && hoverMsg.ts && hover.lastTs.slice(0, 19) !== hoverMsg.ts.slice(0, 19)}
              <span class="text-ink-800/60">(showing last non-empty)</span>
            {/if}
          </div>
          <div class="mt-2">
            {#if hoverToolCall}
              <ToolCallBlock tool={hoverToolCall.tool} payload={hoverToolCall.payload} rawJson={hoverToolCall.rawJson} parseError={hoverToolCall.parseError} />
            {:else}
              {#if hoverMsg.text && hoverMsg.text.trim()}
                <pre class="max-h-[260px] overflow-auto overscroll-contain whitespace-pre-wrap break-words font-mono text-[12px] leading-relaxed text-ink-950">{hoverMsg.text}</pre>
              {:else}
                <div class="font-mono text-[12px] leading-relaxed text-ink-800/60 italic">(empty message)</div>
              {/if}
            {/if}
          </div>
        </div>
      {:else}
        <div class="mt-2 text-[12px] text-ink-800/60">No message text available for this segment.</div>
      {/if}
    {:else}
      <div class="mt-1 text-sm text-ink-800/60">Hover a segment to see details. Click to pin.</div>
    {/if}
  </div>

  <div class="mt-3 flex flex-wrap items-center gap-2 text-xs text-ink-800/60">
    <span class="font-mono">width:</span>
    <button
      class={`rounded-lg px-3 py-1 uppercase tracking-widest ring-1 ${widthMode === 'time' ? 'bg-ink-900 text-paper-50 ring-ink-900/10' : 'bg-paper-100 text-ink-900 ring-ink-900/10'}`}
      type="button"
      on:click={() => (widthMode = 'time')}
    >
      time
    </button>
    <button
      class={`rounded-lg px-3 py-1 uppercase tracking-widest ring-1 ${widthMode === 'messages' ? 'bg-ink-900 text-paper-50 ring-ink-900/10' : 'bg-paper-100 text-ink-900 ring-ink-900/10'}`}
      type="button"
      on:click={() => (widthMode = 'messages')}
    >
      messages
    </button>
    <span>Order is chronological within each hour; time mode uses gap-to-next-message (or hour boundary) as span weight.</span>
  </div>
</Section>
