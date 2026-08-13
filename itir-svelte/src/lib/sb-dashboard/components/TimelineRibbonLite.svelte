<script lang="ts">
  import Section from '$lib/ui/Section.svelte';
  import type { DashboardTimelineEvent } from '../contracts/dashboard';
  import {
    buildTimelineRibbonModel,
    type RibbonLayoutMode,
    type RibbonLensId,
    type RibbonSegment,
    type TimelineRibbonModel
  } from '../adapters/ribbon';

  export let events: DashboardTimelineEvent[] | undefined;
  export let initialLens: RibbonLensId = 'chat_chars';
  export let mode: 'dashboard' | 'workbench' = 'dashboard';
  export let title = mode === 'workbench' ? 'Timeline Ribbon Workbench' : 'Ribbon';
  export let subtitle =
    mode === 'workbench'
      ? 'Contract-aware ribbon over the selected SB timeline payload. Read-only and projection-only.'
      : 'Accounting strip over the selected events. Conserves a named quantity under the active lens.';

  let lens: RibbonLensId = initialLens;
  let layout: RibbonLayoutMode = 'mass';
  let previousLens: RibbonLensId | null = null;
  let showCompareOverlay = false;
  let selectedSegmentId = '';

  const roleColors: Record<string, string> = {
    User: '#1d4ed8',
    Assistant: '#0f766e',
    Tool: '#a16207',
    System: '#b91c1c',
    Unknown: '#6b7280'
  };

  $: model = buildTimelineRibbonModel(events, lens);
  $: compareModel = showCompareOverlay && previousLens ? buildTimelineRibbonModel(events, previousLens) : null;
  $: defaultSegmentId = firstMassSegment(model)?.id ?? model.segments[0]?.id ?? '';
  $: if ((!selectedSegmentId && defaultSegmentId) || (selectedSegmentId && !model.segments.some((segment) => segment.id === selectedSegmentId))) {
    selectedSegmentId = defaultSegmentId;
  }
  $: selectedSegment = model.segments.find((segment) => segment.id === selectedSegmentId) ?? firstMassSegment(model) ?? model.segments[0];
  $: totalEvents = model.segments.reduce((sum, segment) => sum + segment.event_count, 0);

  function firstMassSegment(input: TimelineRibbonModel): RibbonSegment | undefined {
    return input.segments.find((segment) => segment.mass > 0);
  }

  function chooseLens(next: RibbonLensId) {
    if (next === lens) return;
    previousLens = lens;
    lens = next;
    if (mode !== 'workbench') showCompareOverlay = false;
  }

  function selectSegment(segmentId: string) {
    selectedSegmentId = segmentId;
  }

  function pct(value: number): string {
    return `${(value * 100).toFixed(1)}%`;
  }

  function segmentTitle(segment: RibbonSegment): string {
    const lines = [
      segment.label,
      `mass=${segment.mass.toFixed(0)} ${model.lens.units}`,
      `width=${pct(segment.width_norm)}`,
      `events=${segment.event_count}`
    ];
    return [...lines, ...segment.top_detail].join(' | ');
  }

  function roleColor(label: string): string {
    return roleColors[label] ?? '#6b7280';
  }

  function segmentFillStyle(segment: RibbonSegment): string {
    if (segment.mass <= 0 || model.zero_mass) return 'background: rgba(15,23,42,0.06);';
    const top = segment.contributors[0];
    return `background: ${top ? roleColor(top.label) : '#64748b'}; opacity: 0.22;`;
  }
</script>

<Section {title} {subtitle}>
  <div slot="actions" class="flex flex-wrap items-center gap-3">
    <div class="flex items-center gap-2" data-testid="lens-switcher">
      <span class="text-xs uppercase tracking-widest text-ink-800/60">Lens</span>
      {#each [
        { id: 'chat_chars', label: 'Chat chars' },
        { id: 'chat_events', label: 'Chat events' },
        { id: 'events', label: 'All events' }
      ] as item (item.id)}
        <button
          type="button"
          class={`rounded-full border px-3 py-1 text-xs font-mono ${lens === item.id ? 'border-ink-950/40 bg-ink-950 text-white' : 'border-ink-950/15 bg-white text-ink-950 hover:border-ink-950/30'}`}
          data-testid={`lens-item:${item.id}`}
          on:click={() => chooseLens(item.id as RibbonLensId)}
        >
          {item.label}
        </button>
      {/each}
    </div>

    <div class="flex items-center gap-2">
      <span class="text-xs uppercase tracking-widest text-ink-800/60">Layout</span>
      <button
        type="button"
        class={`rounded-full border px-3 py-1 text-xs font-mono ${layout === 'mass' ? 'border-ink-950/40 bg-ink-950 text-white' : 'border-ink-950/15 bg-white text-ink-950 hover:border-ink-950/30'}`}
        on:click={() => (layout = 'mass')}
      >
        mass
      </button>
      <button
        type="button"
        class={`rounded-full border px-3 py-1 text-xs font-mono ${layout === 'time' ? 'border-ink-950/40 bg-ink-950 text-white' : 'border-ink-950/15 bg-white text-ink-950 hover:border-ink-950/30'}`}
        on:click={() => (layout = 'time')}
      >
        time
      </button>
    </div>

    {#if mode === 'workbench'}
      <label class="flex items-center gap-2 text-xs uppercase tracking-widest text-ink-800/60">
        <input type="checkbox" bind:checked={showCompareOverlay} />
        Compare previous lens
      </label>
    {/if}

    <div
      class="rounded-full border border-ink-950/15 bg-paper-100 px-3 py-1 text-xs text-ink-950"
      data-testid="conservation-badge"
      data-total-mass={String(model.lens.total_mass)}
      data-lens-id={model.lens.id}
    >
      <span class="font-mono">{model.lens.id}</span>
      <span class="mx-2 text-ink-800/50">|</span>
      total mass <span class="font-mono">{model.lens.total_mass.toFixed(0)}</span> {model.lens.units}
      <span class="mx-2 text-ink-800/50">|</span>
      events <span class="font-mono">{totalEvents}</span>
    </div>
  </div>

  {#if !events || !events.length}
    <div class="text-sm text-ink-800/70">No timeline events.</div>
  {:else}
    <div class="space-y-4 rounded-2xl bg-paper-100 p-4 ring-1 ring-ink-900/10">
      <div class="text-xs text-ink-800/65">
        <span class="font-semibold text-ink-950">Conserved quantity:</span>
        <span class="ml-2 font-mono">{model.lens.units}</span>
        <span class="mx-2 text-ink-800/45">|</span>
        {model.lens.definition}
      </div>

      {#if layout === 'mass'}
        {#if model.zero_mass}
          <div class="rounded-xl border border-dashed border-ink-950/15 bg-white px-4 py-6 text-sm text-ink-800/70">
            The active lens has zero total mass for this payload. No width allocation is rendered.
          </div>
        {:else}
          <div class="space-y-2">
            <div
              class="relative flex h-14 w-full overflow-hidden rounded-xl bg-white ring-1 ring-ink-900/10"
              data-testid="ribbon-viewport"
            >
              {#each model.segments as segment (segment.id)}
                <button
                  type="button"
                  class={`group relative h-full min-w-0 border-r border-ink-950/8 last:border-r-0 ${selectedSegmentId === segment.id ? 'ring-2 ring-inset ring-ink-950/25' : ''}`}
                  style={`flex: ${Math.max(segment.mass, 0)} 0 0;`}
                  title={segmentTitle(segment)}
                  data-testid="segment"
                  data-seg-id={segment.id}
                  data-mass={String(segment.mass)}
                  data-width-norm={String(segment.width_norm)}
                  on:click={() => selectSegment(segment.id)}
                >
                  <div class="absolute inset-0" style={segmentFillStyle(segment)}></div>
                  {#if segment.contributors.length}
                    <div class="absolute inset-0 flex">
                      {#each segment.contributors.slice(0, 3) as contributor (segment.id + contributor.id)}
                        <div
                          class="h-full"
                          style={`flex: ${Math.max(contributor.mass, 0)} 0 0; background: ${roleColor(contributor.label)}; opacity: 0.65;`}
                        ></div>
                      {/each}
                    </div>
                  {/if}
                  <div class="absolute inset-x-1 bottom-1 flex items-end justify-between gap-2 text-[10px] font-mono text-white">
                    <span>{String(segment.hour).padStart(2, '0')}</span>
                    {#if segment.width_norm >= 0.08}
                      <span>{pct(segment.width_norm)}</span>
                    {/if}
                  </div>
                </button>
              {/each}

              {#if compareModel && !compareModel.zero_mass}
                <div class="pointer-events-none absolute inset-0 flex opacity-25" data-testid="compare-overlay">
                  {#each compareModel.segments as segment (segment.id)}
                    <div style={`flex: ${Math.max(segment.mass, 0)} 0 0;`} class="h-full border-r border-sky-700/20 bg-sky-500/35 last:border-r-0"></div>
                  {/each}
                </div>
              {/if}
            </div>

            <div class="grid text-[10px] font-mono text-ink-800/60" style="grid-template-columns: repeat(24, minmax(0, 1fr));">
              {#each model.segments as segment (segment.id)}
                <div class="text-center">{segment.hour % 3 === 0 ? String(segment.hour).padStart(2, '0') : ''}</div>
              {/each}
            </div>
          </div>
        {/if}
      {:else}
        <div class="space-y-2">
          <div
            class="grid h-14 w-full overflow-hidden rounded-xl bg-white ring-1 ring-ink-900/10"
            style="grid-template-columns: repeat(24, minmax(0, 1fr));"
            data-testid="ribbon-viewport"
          >
            {#each model.segments as segment (segment.id)}
              <button
                type="button"
                class={`relative h-full border-r border-ink-950/8 last:border-r-0 ${selectedSegmentId === segment.id ? 'ring-2 ring-inset ring-ink-950/25' : ''}`}
                title={segmentTitle(segment)}
                data-testid="segment"
                data-seg-id={segment.id}
                data-mass={String(segment.mass)}
                data-width-norm={String(segment.width_norm)}
                on:click={() => selectSegment(segment.id)}
              >
                <div class="absolute inset-0" style={segmentFillStyle(segment)}></div>
                <div class="absolute inset-x-1 bottom-1 text-left text-[10px] font-mono text-ink-950/75">
                  {String(segment.hour).padStart(2, '0')}
                </div>
              </button>
            {/each}
          </div>
          <div class="text-[11px] text-ink-800/60">
            Uniform time layout keeps hour widths fixed; conservation is still shown via tooltip mass and the badge.
          </div>
        </div>
      {/if}

      {#if mode === 'dashboard'}
        <div class="text-xs text-ink-800/65">
          Normalization basis: {model.lens.normalization_basis}
        </div>
      {:else}
        <div class="grid gap-4 xl:grid-cols-[1.1fr,0.9fr]">
          <article class="rounded-2xl border border-ink-950/10 bg-white p-4">
            <div class="text-xs uppercase tracking-[0.24em] text-ink-800/55">Lens Inspector</div>
            <div class="mt-3 space-y-2 text-sm text-ink-950/80">
              <div><span class="font-semibold text-ink-950">Lens:</span> {model.lens.name}</div>
              <div><span class="font-semibold text-ink-950">Units:</span> {model.lens.units}</div>
              <div><span class="font-semibold text-ink-950">Definition:</span> {model.lens.definition}</div>
              <div><span class="font-semibold text-ink-950">Normalization:</span> {model.lens.normalization_basis}</div>
              <div><span class="font-semibold text-ink-950">Threads:</span> Callouts are read-only annotations anchored to segments and do not contribute mass.</div>
            </div>
          </article>

          <article class="rounded-2xl border border-ink-950/10 bg-white p-4">
            <div class="text-xs uppercase tracking-[0.24em] text-ink-800/55">Selected Segment</div>
            {#if selectedSegment}
              <div class="mt-3 space-y-3 text-sm text-ink-950/80">
                <div>
                  <div class="font-semibold text-ink-950">{selectedSegment.label}</div>
                  <div class="mt-1 text-ink-800/65">
                    mass <span class="font-mono">{selectedSegment.mass.toFixed(0)}</span> {model.lens.units}
                    <span class="mx-2 text-ink-800/45">|</span>
                    width <span class="font-mono">{pct(selectedSegment.width_norm)}</span>
                    <span class="mx-2 text-ink-800/45">|</span>
                    events <span class="font-mono">{selectedSegment.event_count}</span>
                  </div>
                </div>

                <div>
                  <div class="text-xs uppercase tracking-[0.18em] text-ink-800/55">Top Contributors</div>
                  <div class="mt-2 space-y-2">
                    {#if selectedSegment.contributors.length}
                      {#each selectedSegment.contributors.slice(0, 4) as contributor (selectedSegment.id + contributor.id)}
                        <div class="flex items-center justify-between gap-3 rounded-xl bg-paper-100 px-3 py-2">
                          <div class="flex items-center gap-2">
                            <span class="inline-block h-2.5 w-2.5 rounded-full" style={`background: ${roleColor(contributor.label)};`}></span>
                            <span>{contributor.label}</span>
                          </div>
                          <div class="font-mono text-xs text-ink-800/70">
                            {contributor.mass.toFixed(0)} {model.lens.units} / {contributor.eventCount} ev
                          </div>
                        </div>
                      {/each}
                    {:else}
                      <div class="rounded-xl bg-paper-100 px-3 py-2 text-ink-800/65">No contributors for this segment.</div>
                    {/if}
                  </div>
                </div>

                <div>
                  <div class="text-xs uppercase tracking-[0.18em] text-ink-800/55">Anchored Threads</div>
                  <div class="mt-2 space-y-2">
                    {#if selectedSegment.threads.length}
                      {#each selectedSegment.threads as thread (thread.id)}
                        <div class="rounded-xl bg-paper-100 px-3 py-2 text-sm text-ink-950/80">
                          <div class="font-medium text-ink-950">{thread.label}</div>
                          <div class="mt-1 font-mono text-xs text-ink-800/70">
                            {thread.event_count} ev
                            {#if thread.mass > 0}
                              <span class="mx-2 text-ink-800/45">|</span>
                              {thread.mass.toFixed(0)} {model.lens.units}
                            {/if}
                          </div>
                        </div>
                      {/each}
                    {:else}
                      <div class="rounded-xl bg-paper-100 px-3 py-2 text-ink-800/65">No anchored thread/source callouts for this segment.</div>
                    {/if}
                  </div>
                </div>
              </div>
            {/if}
          </article>
        </div>

        <div class="rounded-2xl border border-ink-950/10 bg-white p-4">
          <div class="text-xs uppercase tracking-[0.24em] text-ink-800/55">Segment Table</div>
          <div class="mt-3 overflow-x-auto">
            <table class="min-w-full text-sm">
              <thead class="text-left text-ink-800/55">
                <tr>
                  <th class="px-3 py-2 font-medium">Hour</th>
                  <th class="px-3 py-2 font-medium">Mass</th>
                  <th class="px-3 py-2 font-medium">Width</th>
                  <th class="px-3 py-2 font-medium">Events</th>
                  <th class="px-3 py-2 font-medium">Top detail</th>
                </tr>
              </thead>
              <tbody>
                {#each model.segments as segment (segment.id)}
                  <tr class={`border-t border-ink-950/8 ${selectedSegmentId === segment.id ? 'bg-paper-100' : ''}`}>
                    <td class="px-3 py-2">
                      <button type="button" class="font-mono hover:underline" on:click={() => selectSegment(segment.id)}>
                        {segment.label}
                      </button>
                    </td>
                    <td class="px-3 py-2 font-mono">{segment.mass.toFixed(0)} {model.lens.units}</td>
                    <td class="px-3 py-2 font-mono">{pct(segment.width_norm)}</td>
                    <td class="px-3 py-2 font-mono">{segment.event_count}</td>
                    <td class="px-3 py-2 text-ink-800/70">{segment.top_detail.join(' | ')}</td>
                  </tr>
                {/each}
              </tbody>
            </table>
          </div>
        </div>
      {/if}
    </div>
  {/if}
</Section>
