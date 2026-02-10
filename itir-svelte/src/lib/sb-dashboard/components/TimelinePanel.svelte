<script lang="ts">
  import Section from '$lib/ui/Section.svelte';
  import type { DashboardTimelineEvent } from '../contracts/dashboard';

  export let events: DashboardTimelineEvent[] | undefined;

  let q = '';
  let kind = 'all';
  let showPreview = true;
  let expanded = new Set<string>();

  $: kinds = Array.from(new Set((events ?? []).map((e) => e.kind))).sort();
  $: filtered = (events ?? []).filter((e) => {
    if (kind !== 'all' && e.kind !== kind) return false;
    if (!q.trim()) return true;
    const needle = q.toLowerCase();
    return (e.detail ?? '').toLowerCase().includes(needle) || (e.ts ?? '').toLowerCase().includes(needle);
  });

  const roleColors: Record<string, string> = {
    user: '#1d4ed8',
    assistant: '#0f766e',
    tool: '#a16207',
    system: '#b91c1c',
    unknown: '#6b7280'
  };

  function roleFor(e: DashboardTimelineEvent): string {
    const role = (e.meta as any)?.role;
    return typeof role === 'string' && role.trim() ? role.trim().toLowerCase() : 'unknown';
  }

  function sourceFor(e: DashboardTimelineEvent): string {
    const source = (e.meta as any)?.source_id ?? (e.meta as any)?.source;
    return typeof source === 'string' ? source : '';
  }

  function charsFor(e: DashboardTimelineEvent): number {
    const chars = (e.meta as any)?.chars;
    return typeof chars === 'number' && Number.isFinite(chars) ? Math.max(0, chars) : 0;
  }

  $: maxChars = Math.max(1, ...filtered.map(charsFor));
  function barWidth(chars: number): number {
    // Log-ish scaling so 50 vs 5000 is still readable.
    const a = Math.log10(1 + chars);
    const b = Math.log10(1 + maxChars);
    return b > 0 ? Math.max(0, Math.min(1, a / b)) : 0;
  }

  function shortTime(ts: string): string {
    // Expect ISO; show HH:MM only. Full ts on hover.
    return ts.length >= 16 ? ts.slice(11, 16) : ts;
  }

  function rowKey(e: DashboardTimelineEvent, i: number): string {
    return `${e.ts}:${e.kind}:${e.source_path ?? ''}:${i}`;
  }

  function toggle(k: string) {
    const next = new Set(expanded);
    if (next.has(k)) next.delete(k);
    else next.add(k);
    expanded = next;
  }

  function parseDetailFields(detail: string): Record<string, string> {
    const out: Record<string, string> = {};
    for (const tok of (detail ?? '').split(/\s+/g)) {
      const idx = tok.indexOf('=');
      if (idx <= 0) continue;
      const k = tok.slice(0, idx).trim();
      const v = tok.slice(idx + 1).trim();
      if (!k) continue;
      out[k] = v;
    }
    return out;
  }

  function toolPreviewMeta(e: DashboardTimelineEvent): { tool: string; payload: any | null; raw: string } | null {
    const preview = (e.meta as any)?.preview;
    if (typeof preview !== 'string' || !preview.trim()) return null;
    const raw = preview;
    const tool = preview.split(/\s+/, 1)[0] ?? 'tool';
    const brace = preview.indexOf('{');
    if (brace === -1) return { tool, payload: null, raw };
    const jsonText = preview.slice(brace).trim();
    try {
      return { tool, payload: JSON.parse(jsonText), raw };
    } catch {
      return { tool, payload: null, raw };
    }
  }

  function kvRows(obj: Record<string, unknown> | null | undefined): Array<{ k: string; v: string }> {
    if (!obj) return [];
    const rows: Array<{ k: string; v: string }> = [];
    for (const [k, v] of Object.entries(obj)) {
      if (v === null || v === undefined) continue;
      const s = typeof v === 'string' ? v : typeof v === 'number' || typeof v === 'boolean' ? String(v) : JSON.stringify(v);
      rows.push({ k, v: s });
    }
    return rows;
  }
</script>

<Section title="Timeline" subtitle="Accounting list. Order is by timestamp; full timestamp/details on hover.">
  <div slot="actions" class="flex flex-wrap items-center gap-2">
    <input
      class="rounded-lg bg-paper-100 ring-1 ring-ink-900/10 px-3 py-2 text-sm"
      placeholder="Filter..."
      bind:value={q}
    />
    <select class="rounded-lg bg-paper-100 ring-1 ring-ink-900/10 px-2 py-2 text-sm" bind:value={kind}>
      <option value="all">all kinds</option>
      {#each kinds as k}
        <option value={k}>{k}</option>
      {/each}
    </select>
    <label class="flex items-center gap-2 text-xs uppercase tracking-widest text-ink-800/60">
      <input type="checkbox" bind:checked={showPreview} />
      Preview
    </label>
  </div>

  {#if filtered.length}
    <div class="max-h-[560px] overflow-auto overscroll-contain rounded-xl ring-1 ring-ink-900/10 bg-paper-50">
      <div class="min-w-[780px]">
        {#each filtered as e, i (rowKey(e, i))}
          {@const role = e.kind === 'chat' ? roleFor(e) : 'unknown'}
          {@const src = sourceFor(e)}
          {@const chars = charsFor(e)}
          {@const k = rowKey(e, i)}
          {@const isOpen = expanded.has(k)}
          {@const detailFields = parseDetailFields(e.detail ?? '')}
          {@const metaRows = kvRows((e.meta as any) ?? null)}
          {@const toolMeta = e.kind === 'chat' ? toolPreviewMeta(e) : null}
          {@const command = toolMeta?.payload && typeof toolMeta.payload.cmd === 'string' ? toolMeta.payload.cmd : null}
          {@const workdir = toolMeta?.payload && typeof toolMeta.payload.workdir === 'string' ? toolMeta.payload.workdir : null}
          <div
            class={`border-b border-ink-900/10 hover:bg-paper-100 ${isOpen ? 'bg-paper-100' : ''}`}
            title={`${e.ts} | ${e.kind}${e.kind === 'chat' ? ` role=${role} chars=${chars}${src ? ` source=${src}` : ''}` : ''} | ${e.detail}`}
          >
            <button
              class="flex w-full items-center gap-3 px-3 py-2 text-left"
              type="button"
              aria-expanded={isOpen}
              on:click={() => toggle(k)}
            >
              <div class="w-5 font-mono text-xs text-ink-800/50">{isOpen ? 'v' : '>'}</div>

              <div class="w-12 font-mono text-xs text-ink-800/60">{shortTime(e.ts)}</div>

              <div class="w-20 font-mono text-xs text-ink-900/80">{e.kind}</div>

              <div class="flex items-center gap-2 w-52">
                {#if e.kind === 'chat'}
                  <span
                    class="inline-flex items-center rounded-full px-2 py-1 font-mono text-[11px] ring-1 ring-ink-900/10"
                    style={`background: ${roleColors[role] ?? roleColors.unknown}22; color: ${roleColors[role] ?? roleColors.unknown};`}
                  >
                    role={role}
                  </span>
                  {#if src}
                    <span class="truncate font-mono text-[11px] text-ink-800/70" title={src}>src={src}</span>
                  {/if}
                {:else}
                  <span class="font-mono text-[11px] text-ink-800/60">meta</span>
                {/if}
              </div>

              <div class="flex-1">
                {#if e.kind === 'chat'}
                  <div class="flex items-center gap-3">
                    <div class="h-2 flex-1 rounded bg-ink-900/10">
                      <div
                        class="h-2 rounded bg-accent-600/70"
                        style={`width: ${(barWidth(chars) * 100).toFixed(1)}%`}
                      ></div>
                    </div>
                    <div class="w-20 text-right font-mono text-xs text-ink-800/60">{chars.toLocaleString()}</div>
                  </div>
                {:else if showPreview}
                  <div class="text-sm text-ink-950 truncate">{e.detail}</div>
                {/if}
              </div>
            </button>

            {#if isOpen}
              <div class="px-6 pb-3">
                <div class="grid gap-2 rounded-xl bg-paper-50 ring-1 ring-ink-900/10 px-4 py-3">
                  <div class="grid gap-2 md:grid-cols-2">
                    <div class="text-xs text-ink-800/60">
                      <div><span class="font-mono text-ink-900/80">ts</span>: <span class="font-mono">{e.ts}</span></div>
                      <div><span class="font-mono text-ink-900/80">kind</span>: <span class="font-mono">{e.kind}</span></div>
                      {#if e.source_path}
                        <div><span class="font-mono text-ink-900/80">source</span>: <span class="font-mono break-all">{e.source_path}</span></div>
                      {/if}
                    </div>
                    <div class="text-xs text-ink-800/60">
                      {#if command}
                        <div><span class="font-mono text-ink-900/80">cmd</span>:</div>
                        <pre class="mt-1 whitespace-pre-wrap break-words rounded-lg bg-paper-100 ring-1 ring-ink-900/10 px-3 py-2 font-mono text-[11px] text-ink-900/80">{command}</pre>
                      {/if}
                      {#if workdir}
                        <div class="mt-2"><span class="font-mono text-ink-900/80">pwd</span>: <span class="font-mono break-all">{workdir}</span></div>
                      {/if}
                    </div>
                  </div>

                  {#if toolMeta?.raw}
                    <div>
                      <div class="text-xs uppercase tracking-widest text-ink-800/60">preview</div>
                      <pre class="mt-2 whitespace-pre-wrap break-words rounded-lg bg-paper-100 ring-1 ring-ink-900/10 px-3 py-2 font-mono text-[11px] text-ink-900/80">{toolMeta.raw}</pre>
                    </div>
                  {:else if e.detail}
                    <div>
                      <div class="text-xs uppercase tracking-widest text-ink-800/60">detail</div>
                      <pre class="mt-2 whitespace-pre-wrap break-words rounded-lg bg-paper-100 ring-1 ring-ink-900/10 px-3 py-2 font-mono text-[11px] text-ink-900/80">{e.detail}</pre>
                    </div>
                  {/if}

                  {#if Object.keys(detailFields).length}
                    <div>
                      <div class="text-xs uppercase tracking-widest text-ink-800/60">fields</div>
                      <div class="mt-2 grid gap-1 md:grid-cols-2">
                        {#each Object.entries(detailFields) as [dk, dv] (dk)}
                          <div class="flex items-baseline justify-between gap-3 rounded-lg bg-paper-100 ring-1 ring-ink-900/10 px-3 py-2">
                            <div class="font-mono text-[11px] text-ink-800/70">{dk}</div>
                            <div class="font-mono text-[11px] text-ink-900/80 break-all">{dv}</div>
                          </div>
                        {/each}
                      </div>
                    </div>
                  {/if}

                  {#if metaRows.length}
                    <details class="rounded-lg bg-paper-100 ring-1 ring-ink-900/10 px-3 py-2">
                      <summary class="cursor-pointer select-none text-xs uppercase tracking-widest text-ink-800/60">meta</summary>
                      <div class="mt-2 grid gap-1 md:grid-cols-2">
                        {#each metaRows as mr (mr.k)}
                          <div class="flex items-baseline justify-between gap-3">
                            <div class="font-mono text-[11px] text-ink-800/70">{mr.k}</div>
                            <div class="font-mono text-[11px] text-ink-900/80 break-all text-right">{mr.v}</div>
                          </div>
                        {/each}
                      </div>
                    </details>
                  {/if}
                </div>
              </div>
            {/if}
          </div>
        {/each}
      </div>
    </div>
  {:else}
    <div class="text-sm text-ink-800/70">No timeline events.</div>
  {/if}
</Section>
