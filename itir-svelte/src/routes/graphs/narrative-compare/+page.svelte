<script lang="ts">
  import Panel from '$lib/ui/Panel.svelte';

  export let data: {
    selectedFixture: string;
    fixtureMeta?: { fixture_id?: string; label?: string };
    comparison: any;
    availableFixtures: Array<{ key: string; label: string }>;
    error: string | null;
  };

  function changeFixture(fixture: string) {
    window.location.href = `/graphs/narrative-compare?fixture=${encodeURIComponent(fixture)}`;
  }

  const comparison = data.comparison;
  const sources = comparison?.sources ?? [];
  const reports = comparison?.reports ?? {};
  const leftSource = sources[0] ?? null;
  const rightSource = sources[1] ?? null;
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
          {#if source.origin_url}
            <a class="mt-2 block break-all text-sm text-sky-800 underline decoration-sky-800/20 underline-offset-4 hover:decoration-sky-800/50" href={source.origin_url} target="_blank" rel="noreferrer">
              {source.origin_url}
            </a>
          {/if}
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

    <div class="grid gap-4 lg:grid-cols-3">
      <Panel>
        <div class="text-xs uppercase tracking-[0.28em] text-ink-800/70">Shared propositions</div>
        <div class="mt-2 text-3xl font-semibold text-emerald-700">{comparison.summary.shared_proposition_count}</div>
        <div class="mt-4 space-y-3">
          {#each comparison.shared_propositions as row}
            <div class="rounded border border-emerald-200 bg-emerald-50/60 p-3">
              <div class="font-medium text-ink-950">{row.left?.[0]?.predicate_key}</div>
              <div class="mt-1 text-xs text-ink-800/70">{row.left?.[0]?.anchor_text}</div>
              <div class="mt-2 text-[11px] text-ink-800/60">Attributions</div>
              <div class="mt-1 text-xs text-ink-800/80">{row.left_attributions.join(', ') || 'none'} vs {row.right_attributions.join(', ') || 'none'}</div>
            </div>
          {/each}
        </div>
      </Panel>

      <Panel>
        <div class="text-xs uppercase tracking-[0.28em] text-ink-800/70">Disputed propositions</div>
        <div class="mt-2 text-3xl font-semibold text-rose-700">{comparison.summary.disputed_proposition_count}</div>
        <div class="mt-4 space-y-3">
          {#each comparison.disputed_propositions as row}
            <div class="rounded border border-rose-200 bg-rose-50/60 p-3">
              <div class="text-xs uppercase tracking-[0.24em] text-rose-800/70">Left</div>
              <div class="mt-1 font-medium text-ink-950">{row.left?.predicate_key}</div>
              <div class="text-xs text-ink-800/70">{row.left?.anchor_text}</div>
              <div class="mt-3 text-xs uppercase tracking-[0.24em] text-rose-800/70">Right</div>
              <div class="mt-1 font-medium text-ink-950">{row.right?.predicate_key}</div>
              <div class="text-xs text-ink-800/70">{row.right?.anchor_text}</div>
            </div>
          {/each}
        </div>
      </Panel>

      <Panel>
        <div class="text-xs uppercase tracking-[0.28em] text-ink-800/70">Link differences</div>
        <div class="mt-2 text-3xl font-semibold text-amber-700">{comparison.summary.link_difference_count}</div>
        <div class="mt-4 space-y-3">
          {#each comparison.link_differences as row}
            <div class="rounded border border-amber-200 bg-amber-50/60 p-3">
              <div class="font-medium text-ink-950">{row.signature}</div>
              <div class="mt-2 text-xs text-ink-800/70">{leftSource?.title}: {row.left_attributions.join(', ') || 'none'}</div>
              <div class="mt-1 text-xs text-ink-800/70">{rightSource?.title}: {row.right_attributions.join(', ') || 'none'}</div>
            </div>
          {/each}
        </div>
      </Panel>

      <Panel>
        <div class="text-xs uppercase tracking-[0.28em] text-ink-800/70">Comparison links</div>
        <div class="mt-2 text-3xl font-semibold text-violet-700">{comparison.summary.comparison_link_count}</div>
        <div class="mt-4 space-y-3">
          {#each comparison.comparison_links as row}
            <div class="rounded border border-violet-200 bg-violet-50/60 p-3">
              <div class="font-medium text-ink-950">{row.link_kind}</div>
              <div class="mt-1 text-xs text-ink-800/70">{row.left_proposition_id} ↔ {row.right_proposition_id}</div>
              {#if row.receipts?.length}
                <div class="mt-2 flex flex-wrap gap-2">
                  {#each row.receipts as receipt}
                    <span class="rounded-full border border-ink-950/10 bg-white px-2 py-1 text-[11px] text-ink-800/75">{receipt.kind}: {receipt.value}</span>
                  {/each}
                </div>
              {/if}
            </div>
          {/each}
        </div>
      </Panel>
    </div>

    <div class="grid gap-4 lg:grid-cols-2">
      <Panel>
        <div class="text-xs uppercase tracking-[0.28em] text-ink-800/70">Source-only propositions</div>
        {#each sources as source}
          <div class="mt-4">
            <div class="text-sm font-semibold text-ink-950">{source.title}</div>
            <div class="mt-2 space-y-2">
              {#each comparison.source_only_propositions?.[source.source_id] ?? [] as row}
                <div class="rounded border border-ink-950/10 bg-ink-50 p-3">
                  <div class="font-medium text-ink-950">{row.predicate_key}</div>
                  <div class="mt-1 text-xs text-ink-800/70">{row.anchor_text}</div>
                </div>
              {/each}
            </div>
          </div>
        {/each}
      </Panel>

      <Panel>
        <div class="text-xs uppercase tracking-[0.28em] text-ink-800/70">Corroboration + abstentions</div>
        {#each sources as source}
          <div class="mt-4">
            <div class="text-sm font-semibold text-ink-950">{source.title}</div>
            <div class="mt-2 text-[11px] uppercase tracking-[0.24em] text-ink-800/60">Corroboration refs</div>
            <div class="mt-2 space-y-2">
              {#each comparison.corroboration_refs?.[source.source_id] ?? [] as row}
                <div class="rounded border border-sky-200 bg-sky-50/60 p-3 text-xs text-ink-900">
                  <div class="font-medium">{row.label}</div>
                  <div class="mt-1">{row.claim_text}</div>
                </div>
              {/each}
            </div>
            <div class="mt-3 text-[11px] uppercase tracking-[0.24em] text-ink-800/60">Abstentions</div>
            <div class="mt-2 space-y-2">
              {#each comparison.abstentions?.[source.source_id] ?? [] as row}
                <div class="rounded border border-zinc-200 bg-zinc-50 p-3 text-xs text-ink-900">
                  <div class="font-medium">{row.reason}</div>
                  <div class="mt-1">{row.text}</div>
                </div>
              {/each}
            </div>
          </div>
        {/each}
      </Panel>
    </div>

    <div class="grid gap-4 lg:grid-cols-2">
      {#each sources as source}
        <Panel>
          <div class="text-xs uppercase tracking-[0.28em] text-ink-800/70">Source proposition links</div>
          <div class="mt-2 text-sm font-semibold text-ink-950">{source.title}</div>
          <div class="mt-3 space-y-2">
            {#each reports[source.source_id]?.proposition_links ?? [] as row}
              <div class="rounded border border-ink-950/10 bg-ink-50 p-3">
                <div class="font-medium text-ink-950">{row.link_kind}</div>
                <div class="mt-1 text-xs text-ink-800/70">{row.source_proposition_id} → {row.target_proposition_id}</div>
                {#if row.receipts?.length}
                  <div class="mt-2 flex flex-wrap gap-2">
                    {#each row.receipts as receipt}
                      <span class="rounded-full border border-ink-950/10 bg-white px-2 py-1 text-[11px] text-ink-800/75">{receipt.kind}: {receipt.value}</span>
                    {/each}
                  </div>
                {/if}
              </div>
            {/each}
          </div>
        </Panel>
      {/each}
    </div>
  {/if}
</div>
