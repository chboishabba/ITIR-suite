<script lang="ts">
  import Section from '$lib/ui/Section.svelte';
  import type { DashboardTimelineEvent } from '../contracts/dashboard';

  type LensId = 'chat_chars' | 'chat_events' | 'events';

  export let events: DashboardTimelineEvent[] | undefined;
  export let initialLens: LensId = 'chat_chars';

  let lens: LensId = initialLens;

  const lensMeta: Record<LensId, { name: string; units: string }> = {
    chat_chars: { name: 'Chat chars', units: 'chars' },
    chat_events: { name: 'Chat events', units: 'events' },
    events: { name: 'All events', units: 'events' }
  };

  function massFor(e: DashboardTimelineEvent): number {
    if (lens === 'events') return 1;
    if (lens === 'chat_events') return e.kind === 'chat' ? 1 : 0;
    // chat_chars
    if (e.kind !== 'chat') return 0;
    const chars = (e.meta as any)?.chars;
    return typeof chars === 'number' && Number.isFinite(chars) ? Math.max(0, chars) : 0;
  }

  function roleFor(e: DashboardTimelineEvent): string {
    const role = (e.meta as any)?.role;
    return typeof role === 'string' && role.trim() ? role.trim().toLowerCase() : 'unknown';
  }

  const roleColors: Record<string, string> = {
    user: '#1d4ed8',
    assistant: '#0f766e',
    tool: '#a16207',
    system: '#b91c1c',
    unknown: '#6b7280'
  };

  type HourBin = {
    hour: number;
    mass: number;
    count: number;
    byRole: Record<string, number>;
  };

  $: bins = (() => {
    const out: HourBin[] = Array.from({ length: 24 }, (_, hour) => ({
      hour,
      mass: 0,
      count: 0,
      byRole: {}
    }));
    for (const e of events ?? []) {
      const h = typeof e.hour === 'number' ? e.hour : Number(String(e.ts).slice(11, 13));
      if (!Number.isFinite(h) || h < 0 || h > 23) continue;
      const m = massFor(e);
      out[h]!.mass += m;
      out[h]!.count += 1;
      if (e.kind === 'chat') {
        const r = roleFor(e);
        out[h]!.byRole[r] = (out[h]!.byRole[r] ?? 0) + m;
      }
    }
    return out;
  })();

  $: totalMass = bins.reduce((acc, b) => acc + b.mass, 0);
  $: totalCount = bins.reduce((acc, b) => acc + b.count, 0);

  function pct(v: number): string {
    if (!totalMass) return '0.0%';
    return `${((v / totalMass) * 100).toFixed(1)}%`;
  }

  function tooltip(b: HourBin): string {
    const base = `${String(b.hour).padStart(2, '0')}:00 - ${String(b.hour).padStart(2, '0')}:59 | mass=${b.mass.toFixed(0)} ${lensMeta[lens].units} | width=${pct(b.mass)} | events=${b.count}`;
    if (lens !== 'chat_chars') return base;
    const roles = Object.entries(b.byRole)
      .sort((a, z) => z[1] - a[1])
      .slice(0, 4)
      .map(([r, m]) => `${r}=${m.toFixed(0)}`)
      .join(' ');
    return roles ? `${base} | ${roles}` : base;
  }
</script>

<Section
  title="Ribbon (Lite)"
  subtitle="Accounting strip over the selected events. Conserves a named quantity under the active lens."
>
  <div slot="actions" class="flex flex-wrap items-center gap-2">
    <label class="text-xs uppercase tracking-widest text-ink-800/60" for="lens">Lens</label>
    <select
      id="lens"
      class="rounded-lg bg-paper-100 ring-1 ring-ink-900/10 px-2 py-1 text-sm"
      bind:value={lens}
    >
      <option value="chat_chars">Chat chars</option>
      <option value="chat_events">Chat events</option>
      <option value="events">All events</option>
    </select>
    <div class="ml-2 text-xs text-ink-800/60">
      Conserved: <span class="font-mono">{lensMeta[lens].units}</span>,
      total mass: <span class="font-mono">{totalMass.toFixed(0)}</span>,
      total events: <span class="font-mono">{totalCount}</span>
    </div>
  </div>

  {#if !events || !events.length}
    <div class="text-sm text-ink-800/70">No timeline events.</div>
  {:else}
    <div class="rounded-xl bg-paper-100 ring-1 ring-ink-900/10 p-3">
      <div class="flex h-10 w-full overflow-hidden rounded-lg bg-paper-50 ring-1 ring-ink-900/10">
        {#each bins as b (b.hour)}
          <!-- width proportional to mass; fall back to equal widths if totalMass=0 -->
          <div
            class="relative h-full"
            style={`flex: ${totalMass ? Math.max(0, b.mass) : 1} 0 0; min-width: 6px;`}
            title={tooltip(b)}
          >
            <div class="absolute inset-0 bg-ink-900/5"></div>
            {#if lens === 'chat_chars'}
              {@const roles = Object.entries(b.byRole).sort((a, z) => z[1] - a[1]).slice(0, 3)}
              <div class="absolute inset-0 flex">
                {#each roles as [r, m] (r)}
                  <div style={`flex: ${m} 0 0; background: ${roleColors[r] ?? roleColors.unknown}; opacity: 0.55;`}></div>
                {/each}
              </div>
            {:else}
              <div class="absolute inset-0 bg-accent-600/40"></div>
            {/if}
            <div class="absolute bottom-1 left-1 font-mono text-[10px] text-ink-950/70">
              {b.hour}
            </div>
          </div>
        {/each}
      </div>
      <div class="mt-2 flex items-center justify-between text-[11px] text-ink-800/60">
        <div>00</div>
        <div>23</div>
      </div>
    </div>
  {/if}
</Section>
