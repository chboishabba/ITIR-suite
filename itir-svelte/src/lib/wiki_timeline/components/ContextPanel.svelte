<script lang="ts">
  import Panel from '$lib/ui/Panel.svelte';
  import { actionLabel } from '$lib/wiki_timeline/graph';
  import { highlightParts } from '$lib/wiki_timeline/selection';

  export let selectedNodeId: string | null = null;
  export let contextRows: any[] = [];
  export let contextRowsShown: any[] = [];
  export let requesterCoverageWindow: any = null;
  export let requesterCoverageGlobal: any = null;
  export let requesterCoverageWindowGap = false;
  export let requesterCoverageGlobalGap = false;
  export let contextNeedle: string = '';
  export let showAllContextRows = false;
  export let contextBox: HTMLDivElement | null = null;
</script>

<Panel>
  <div class="flex flex-wrap items-center justify-between gap-3">
    <div class="text-xs uppercase tracking-[0.28em] text-ink-800/70">Context</div>
    <div class="flex flex-wrap items-center gap-3 text-[11px] font-mono text-ink-800/60">
      {#if selectedNodeId}
        <span>selected: {selectedNodeId}</span>
        {#if contextRows.length > 80}
          <label class="inline-flex items-center gap-1 rounded border border-ink-950/10 bg-white px-2 py-0.5">
            <input type="checkbox" bind:checked={showAllContextRows} />
            <span>all rows ({contextRows.length})</span>
          </label>
        {:else}
          <span>rows: {contextRows.length}</span>
        {/if}
      {:else}
        <span>click a node to preview the relevant extracted timeline text</span>
      {/if}
    </div>
  </div>

  <div class="mt-3 max-h-[320px] overflow-auto rounded-lg border border-ink-950/10 bg-white" bind:this={contextBox}>
    {#if !selectedNodeId}
      <div class="p-3 text-xs text-ink-800/70">
        This panel shows sentence-local timeline evidence for the selected node (from the extracted timeline substrate, not the full Wikipedia article).
      </div>
    {:else}
      {#if selectedNodeId === 'req:missing'}
        <div class="border-b border-ink-950/10 bg-amber-50/40 p-3 text-[11px]">
          <div class="font-mono text-ink-900">
            requester_window: signal={requesterCoverageWindow.requestSignalEvents} requester={requesterCoverageWindow.requesterEvents}
            missing={requesterCoverageWindow.missingRequesterEventIds.length} total={requesterCoverageWindow.totalEvents}
          </div>
          {#if requesterCoverageGlobal}
            <div class="mt-1 font-mono text-ink-900">
              requester_global: signal={requesterCoverageGlobal.requestSignalEvents} requester={requesterCoverageGlobal.requesterEvents}
              missing={requesterCoverageGlobal.missingRequesterEventIds.length} total={requesterCoverageGlobal.totalEvents}
            </div>
          {:else}
            <div class="mt-1 font-mono text-ink-800/70">requester_global: unavailable (payload missing requester_coverage)</div>
          {/if}
          <div class="mt-2 flex flex-wrap gap-2 font-mono">
            {#if requesterCoverageWindowGap}
              <span class="rounded bg-red-100 px-1.5 py-0.5 text-red-900">window_gap: request-signal events exceed requester-tagged events</span>
            {:else}
              <span class="rounded bg-emerald-100 px-1.5 py-0.5 text-emerald-900">window_gap: none</span>
            {/if}
            {#if requesterCoverageGlobalGap}
              <span class="rounded bg-red-100 px-1.5 py-0.5 text-red-900">global_gap: request-signal events exceed requester-tagged events</span>
            {:else if requesterCoverageGlobal}
              <span class="rounded bg-emerald-100 px-1.5 py-0.5 text-emerald-900">global_gap: none</span>
            {/if}
          </div>
          {#if requesterCoverageWindow.missingRequesterEventIds.length}
            <div class="mt-2">
              <span class="font-mono text-ink-800/60">window_missing_ids</span>
              {#each requesterCoverageWindow.missingRequesterEventIds as x (x)}
                <span class="ml-1 inline-block rounded bg-red-50 px-1.5 py-0.5 font-mono text-red-900">{x}</span>
              {/each}
            </div>
          {:else if requesterCoverageGlobal?.missingRequesterEventIds.length}
            <div class="mt-2">
              <span class="font-mono text-ink-800/60">global_missing_ids</span>
              {#each requesterCoverageGlobal.missingRequesterEventIds.slice(0, 24) as x (x)}
                <span class="ml-1 inline-block rounded bg-red-50 px-1.5 py-0.5 font-mono text-red-900">{x}</span>
              {/each}
            </div>
          {/if}
        </div>
      {/if}
      {#if !contextRows.length}
        <div class="p-3 text-xs text-ink-800/70">No matching extracted timeline rows for this node in the current event window.</div>
      {:else}
        {#each contextRowsShown as r (r.key)}
          <div class="border-b border-ink-950/10 p-3 last:border-b-0" data-ctx-id={r.event_id}>
            <div class="flex flex-wrap items-center justify-between gap-2">
              <div class="font-mono text-[10px] text-ink-800/60">{r.time} {r.event_id}</div>
              <div class="font-mono text-[10px] text-ink-800/60">section={r.section}</div>
            </div>
            <div class="mt-2 flex flex-wrap items-center gap-2 text-[11px] text-ink-950">
              {#if r.requesters.length}
                {#each r.requesters as x (r.event_id + ':req:' + x)}
                  <span class="rounded bg-purple-100 px-1.5 py-0.5 font-mono">[{x}]</span>
                {/each}
                <span class="font-mono text-ink-800/50">request</span>
              {/if}
              {#if r.subjects.length}
                {#each r.subjects as x (r.event_id + ':sub:' + x)}
                  <span class="rounded bg-emerald-100 px-1.5 py-0.5 font-mono">[{x}]</span>
                {/each}
                <span class="font-mono text-ink-800/50">do</span>
              {/if}
              {#if r.actions.length}
                {#each r.actions as a (r.event_id + ':act:' + a)}
                  <span class="rounded bg-amber-100 px-1.5 py-0.5 font-mono">[{a}]</span>
                {/each}
              {:else}
                <span class="rounded bg-amber-100 px-1.5 py-0.5 font-mono">[{actionLabel(r.action, r.negation)}]</span>
              {/if}
              {#if r.objects.length}
                <span class="font-mono text-ink-800/50">object</span>
                {#each r.objects as x (r.event_id + ':obj:' + x)}
                  <span class="rounded bg-slate-100 px-1.5 py-0.5 font-mono">[{x}]</span>
                {/each}
              {/if}
              {#if r.numerics.length}
                <span class="font-mono text-ink-800/50">numeric</span>
                {#each r.numerics as x (r.event_id + ':num:' + x)}
                  <span class="rounded bg-rose-100 px-1.5 py-0.5 font-mono">[{x}]</span>
                {/each}
              {/if}
              {#if r.purpose}
                <span class="font-mono text-ink-800/50">purpose</span>
                <span class="rounded bg-yellow-50 px-1.5 py-0.5 font-mono">[{r.purpose}]</span>
              {/if}
            </div>
            {#if r.connected.length}
              <div class="mt-2 text-[11px]">
                <span class="font-mono text-ink-800/50">connected</span>
                {#each r.connected as x (r.event_id + ':conn:' + x)}
                  <span class="ml-1 inline-block rounded bg-slate-50 px-1.5 py-0.5 font-mono text-ink-900">{x}</span>
                {/each}
              </div>
            {/if}
            {#if r.numericClaims.length}
              <div class="mt-2 text-[11px]">
                <span class="font-mono text-ink-800/50">numeric_claims</span>
                {#each r.numericClaims.slice(0, 8) as x (r.event_id + ':nclaim:' + x)}
                  <span class="ml-1 inline-block rounded bg-rose-50 px-1.5 py-0.5 font-mono text-ink-900">{x}</span>
                {/each}
              </div>
            {/if}
            {#if r.sources.length}
              <div class="mt-2 text-[11px]">
                <span class="font-mono text-ink-800/50">sources</span>
                {#each r.sources.slice(0, 8) as x (r.event_id + ':src:' + x)}
                  <span class="ml-1 inline-block rounded bg-emerald-50 px-1.5 py-0.5 font-mono text-ink-900">{x}</span>
                {/each}
              </div>
            {/if}
            {#if r.lenses.length}
              <div class="mt-2 text-[11px]">
                <span class="font-mono text-ink-800/50">lenses</span>
                {#each r.lenses.slice(0, 8) as x (r.event_id + ':lens:' + x)}
                  <span class="ml-1 inline-block rounded bg-violet-50 px-1.5 py-0.5 font-mono text-ink-900">{x}</span>
                {/each}
              </div>
            {/if}
            {#if r.slRefs.length}
              <div class="mt-2 text-[11px]">
                <span class="font-mono text-ink-800/50">sl_refs</span>
                {#each r.slRefs.slice(0, 6) as x (r.event_id + ':sl:' + x)}
                  <span class="ml-1 inline-block rounded bg-blue-50 px-1.5 py-0.5 font-mono text-ink-900">{x}</span>
                {/each}
              </div>
            {/if}
            {#if r.checkNext.length}
              <div class="mt-2 text-[11px]">
                <span class="font-mono text-ink-800/50">check_next</span>
                {#each r.checkNext as x (r.event_id + ':next:' + x)}
                  <span class="ml-1 inline-block rounded bg-violet-50 px-1.5 py-0.5 font-mono text-ink-900">{x}</span>
                {/each}
              </div>
            {/if}
            {#if r.party}
              <div class="mt-2 text-[11px]">
                <span class="font-mono text-ink-800/50">party</span>
                <span class="ml-1 inline-block rounded bg-emerald-50 px-1.5 py-0.5 font-mono text-ink-900">{r.party}</span>
              </div>
            {/if}
            {#if r.tocContext.length}
              <div class="mt-2 text-[11px]">
                <span class="font-mono text-ink-800/50">toc</span>
                {#each r.tocContext.slice(0, 4) as x (r.event_id + ':toc:' + x)}
                  <span class="ml-1 inline-block rounded bg-slate-50 px-1.5 py-0.5 font-mono text-ink-900">{x}</span>
                {/each}
              </div>
            {/if}
            {#if r.legalMarkers.length}
              <div class="mt-2 text-[11px]">
                <span class="font-mono text-ink-800/50">legal_markers</span>
                {#each r.legalMarkers.slice(0, 8) as x (r.event_id + ':lm:' + x)}
                  <span class="ml-1 inline-block rounded bg-indigo-50 px-1.5 py-0.5 font-mono text-ink-900">{x}</span>
                {/each}
              </div>
            {/if}
            {#if r.factRows.length}
              <div class="mt-2 text-[11px]">
                <span class="font-mono text-ink-800/50">timeline_facts</span>
                {#each r.factRows.slice(0, 4) as x (r.event_id + ':fact:' + x)}
                  <span class="ml-1 inline-block rounded bg-lime-50 px-1.5 py-0.5 font-mono text-ink-900">{x}</span>
                {/each}
              </div>
            {/if}
            {#if r.citations.length}
              <div class="mt-2 text-[11px]">
                <span class="font-mono text-ink-800/50">citations</span>
                {#each r.citations.slice(0, 6) as x (r.event_id + ':cit:' + x)}
                  <span class="ml-1 inline-block rounded bg-amber-50 px-1.5 py-0.5 font-mono text-ink-900">{x}</span>
                {/each}
              </div>
            {/if}
            <div class="mt-2 text-sm text-ink-950">
              {#if contextNeedle}
                {#each highlightParts(r.text, contextNeedle) as part, i (r.event_id + ':' + i)}
                  {#if part.hit}
                    <span class="rounded bg-amber-200/60 px-1">{part.s}</span>
                  {:else}
                    {part.s}
                  {/if}
                {/each}
              {:else}
                {r.text}
              {/if}
            </div>
          </div>
        {/each}
      {/if}
    {/if}
  </div>
</Panel>
