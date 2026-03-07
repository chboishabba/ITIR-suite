<script lang="ts">
  import LayeredGraph from '$lib/ui/LayeredGraph.svelte';
  import TokenArcInspector from '$lib/semantic/TokenArcInspector.svelte';

  export let data: {
    source: string;
    label: string;
    report: any;
    reviewedLinkage: any;
    available: Array<{ key: string; label: string }>;
    comparison?: any;
    graphGate?: any;
    semanticGraph?: any;
    tokenArcDebug?: any;
    error: string | null;
  };

  function changeSource(source: string) {
    window.location.href = `/graphs/semantic-report?source=${encodeURIComponent(source)}`;
  }

  function deltaClass(n: number): string {
    if (n > 0) return 'text-emerald-700';
    if (n < 0) return 'text-rose-700';
    return 'text-zinc-600';
  }

  const topPromoted = data.report?.promoted_relations?.slice(0, 25) ?? [];
  const topCandidate = data.report?.candidate_only_relations?.slice(0, 25) ?? [];
  const unresolved = data.report?.unresolved_mentions?.slice(0, 25) ?? [];
  const perSeed = data.reviewedLinkage?.per_seed ?? [];
  const perEntity = data.report?.per_entity?.slice(0, 25) ?? [];
  const unmatchedSeeds = data.reviewedLinkage?.unmatched_seeds ?? [];
  const ambiguousEvents = data.reviewedLinkage?.ambiguous_events ?? [];
  const compare = data.comparison;
  const gwbSnap = compare?.corpora?.gwb;
  const hcaSnap = compare?.corpora?.hca;
  const predicateDelta = compare?.delta?.predicates ?? [];
  const summaryDelta = compare?.delta?.summary ?? {};
  const graphGate = data.graphGate ?? compare?.graphGate;
  const semanticGraph = data.semanticGraph ?? compare?.semanticGraph;
  const graphViewportKey = `${String(graphGate?.enabled ?? false)}:${String(graphGate?.predicateTypeCount ?? 0)}:${String(graphGate?.totalRelationCandidates ?? 0)}`;
  const tokenArcDebug = data.tokenArcDebug ?? { events: [], unavailableReason: null };
</script>

<svelte:head>
  <title>Semantic Report</title>
</svelte:head>

<div class="mx-auto max-w-7xl px-6 py-8">
  <div class="mb-6 flex flex-wrap items-center justify-between gap-4">
    <div>
      <h1 class="text-3xl font-semibold tracking-tight">Semantic report</h1>
      <p class="text-sm text-zinc-600">Corpus-level semantic report over the current working semantic lanes.</p>
    </div>
    <label class="flex items-center gap-3 text-sm">
      <span>Corpus</span>
      <select
        class="rounded border border-zinc-300 bg-white px-3 py-2"
        value={data.source}
        on:change={(e) => changeSource((e.currentTarget as HTMLSelectElement).value)}
      >
        {#each data.available as option}
          <option value={option.key}>{option.label}</option>
        {/each}
      </select>
    </label>
  </div>

  {#if data.error}
    <div class="rounded border border-red-300 bg-red-50 px-4 py-3 text-sm text-red-800">
      {data.error}
    </div>
  {:else if data.report}
    {#if gwbSnap && hcaSnap}
      <section class="mb-6 rounded border border-zinc-200 bg-white p-4">
        <div class="mb-4 flex flex-wrap items-center justify-between gap-3">
          <h2 class="text-lg font-semibold">Split + delta comparison</h2>
          <div class="text-xs uppercase tracking-[0.16em] text-zinc-500">hca minus gwb deltas</div>
        </div>
        <div class="grid gap-4 lg:grid-cols-2">
          <div class="rounded border border-zinc-200 bg-zinc-50 p-3">
            <div class="mb-2 text-xs uppercase tracking-[0.16em] text-zinc-500">{gwbSnap.label}</div>
            <div class="grid grid-cols-2 gap-2 text-sm">
              <div>Entities: <span class="font-semibold">{gwbSnap.summary.entity_count}</span></div>
              <div>Candidates: <span class="font-semibold">{gwbSnap.summary.relation_candidate_count}</span></div>
              <div>Promoted: <span class="font-semibold">{gwbSnap.summary.promoted_relation_count}</span></div>
              <div>Candidate-only: <span class="font-semibold">{gwbSnap.summary.candidate_only_relation_count}</span></div>
              <div>Unresolved: <span class="font-semibold">{gwbSnap.summary.unresolved_mention_count}</span></div>
              <div>Unmatched seeds: <span class="font-semibold">{gwbSnap.reviewed?.unmatched_count ?? '-'}</span></div>
            </div>
          </div>
          <div class="rounded border border-zinc-200 bg-zinc-50 p-3">
            <div class="mb-2 text-xs uppercase tracking-[0.16em] text-zinc-500">{hcaSnap.label}</div>
            <div class="grid grid-cols-2 gap-2 text-sm">
              <div>Entities: <span class="font-semibold">{hcaSnap.summary.entity_count}</span></div>
              <div>Candidates: <span class="font-semibold">{hcaSnap.summary.relation_candidate_count}</span></div>
              <div>Promoted: <span class="font-semibold">{hcaSnap.summary.promoted_relation_count}</span></div>
              <div>Candidate-only: <span class="font-semibold">{hcaSnap.summary.candidate_only_relation_count}</span></div>
              <div>Unresolved: <span class="font-semibold">{hcaSnap.summary.unresolved_mention_count}</span></div>
              <div>Unmatched seeds: <span class="font-semibold">{hcaSnap.reviewed?.unmatched_count ?? '-'}</span></div>
            </div>
          </div>
        </div>
        <div class="mt-4 grid gap-3 md:grid-cols-5">
          <div class="rounded border border-zinc-200 bg-white p-3 text-sm">
            <div class="text-xs uppercase text-zinc-500">Entities delta</div>
            <div class={`mt-1 text-lg font-semibold ${deltaClass(summaryDelta.entity_count ?? 0)}`}>{summaryDelta.entity_count ?? 0}</div>
          </div>
          <div class="rounded border border-zinc-200 bg-white p-3 text-sm">
            <div class="text-xs uppercase text-zinc-500">Candidates delta</div>
            <div class={`mt-1 text-lg font-semibold ${deltaClass(summaryDelta.relation_candidate_count ?? 0)}`}>{summaryDelta.relation_candidate_count ?? 0}</div>
          </div>
          <div class="rounded border border-zinc-200 bg-white p-3 text-sm">
            <div class="text-xs uppercase text-zinc-500">Promoted delta</div>
            <div class={`mt-1 text-lg font-semibold ${deltaClass(summaryDelta.promoted_relation_count ?? 0)}`}>{summaryDelta.promoted_relation_count ?? 0}</div>
          </div>
          <div class="rounded border border-zinc-200 bg-white p-3 text-sm">
            <div class="text-xs uppercase text-zinc-500">Candidate-only delta</div>
            <div class={`mt-1 text-lg font-semibold ${deltaClass(summaryDelta.candidate_only_relation_count ?? 0)}`}>{summaryDelta.candidate_only_relation_count ?? 0}</div>
          </div>
          <div class="rounded border border-zinc-200 bg-white p-3 text-sm">
            <div class="text-xs uppercase text-zinc-500">Unresolved delta</div>
            <div class={`mt-1 text-lg font-semibold ${deltaClass(summaryDelta.unresolved_mention_count ?? 0)}`}>{summaryDelta.unresolved_mention_count ?? 0}</div>
          </div>
        </div>
        {#if predicateDelta.length}
          <div class="mt-4 overflow-x-auto rounded border border-zinc-200">
            <table class="min-w-full text-left text-sm">
              <thead class="border-b border-zinc-200 bg-zinc-50 text-zinc-600">
                <tr>
                  <th class="px-3 py-2 font-medium">Predicate</th>
                  <th class="px-3 py-2 font-medium">GWB total</th>
                  <th class="px-3 py-2 font-medium">HCA total</th>
                  <th class="px-3 py-2 font-medium">Delta</th>
                </tr>
              </thead>
              <tbody>
                {#each predicateDelta as row}
                  <tr class="border-b border-zinc-100">
                    <td class="px-3 py-2">{row.display_label}</td>
                    <td class="px-3 py-2">{row.gwb_total}</td>
                    <td class="px-3 py-2">{row.hca_total}</td>
                    <td class={`px-3 py-2 font-medium ${deltaClass(row.delta_hca_minus_gwb)}`}>{row.delta_hca_minus_gwb}</td>
                  </tr>
                {/each}
              </tbody>
            </table>
          </div>
        {/if}
      </section>
    {/if}

    <div class="mb-6 grid gap-4 md:grid-cols-3 xl:grid-cols-6">
      <div class="rounded border border-zinc-200 bg-white p-4">
        <div class="text-xs uppercase text-zinc-500">Entities</div>
        <div class="mt-1 text-2xl font-semibold">{data.report.summary.entity_count}</div>
      </div>
      <div class="rounded border border-zinc-200 bg-white p-4">
        <div class="text-xs uppercase text-zinc-500">Candidates</div>
        <div class="mt-1 text-2xl font-semibold">{data.report.summary.relation_candidate_count}</div>
      </div>
      <div class="rounded border border-zinc-200 bg-white p-4">
        <div class="text-xs uppercase text-zinc-500">Promoted</div>
        <div class="mt-1 text-2xl font-semibold">{data.report.summary.promoted_relation_count}</div>
      </div>
      <div class="rounded border border-zinc-200 bg-white p-4">
        <div class="text-xs uppercase text-zinc-500">Candidate only</div>
        <div class="mt-1 text-2xl font-semibold">{data.report.summary.candidate_only_relation_count}</div>
      </div>
      <div class="rounded border border-zinc-200 bg-white p-4">
        <div class="text-xs uppercase text-zinc-500">Unresolved</div>
        <div class="mt-1 text-2xl font-semibold">{data.report.summary.unresolved_mention_count}</div>
      </div>
      <div class="rounded border border-zinc-200 bg-white p-4">
        <div class="text-xs uppercase text-zinc-500">Run</div>
        <div class="mt-1 break-all text-sm font-medium">{data.report.run_id}</div>
      </div>
    </div>

    {#if graphGate}
      <section class="mb-6 rounded border border-zinc-200 bg-white p-4">
        <div class="mb-3 flex flex-wrap items-center justify-between gap-3">
          <h2 class="text-lg font-semibold">AU semantic graph lane</h2>
          <div class="text-xs text-zinc-600">
            gate: {graphGate.predicateTypeCount}/{graphGate.threshold.minPredicateTypes} predicate types,
            {graphGate.totalRelationCandidates}/{graphGate.threshold.minTotalRelationCandidates} relation candidates
          </div>
        </div>
        {#if graphGate.enabled && semanticGraph}
          <LayeredGraph
            layers={semanticGraph.layers}
            edges={semanticGraph.edges}
            width={2860}
            height={780}
            colGap={760}
            leftPad={110}
            scrollWhenOverflow={true}
            fitToWidth={false}
            viewportResetKey={graphViewportKey}
          />
          <p class="mt-3 text-xs text-zinc-600">Solid edges indicate promoted support. Dashed edges indicate candidate-only support.</p>
        {:else}
          <div class="rounded border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-900">
            Graph lane is waiting for richer AU coverage. It auto-enables at
            {graphGate.threshold.minPredicateTypes}+ predicate types and {graphGate.threshold.minTotalRelationCandidates}+ relation candidates.
          </div>
        {/if}
      </section>
    {/if}

    <div class="mb-6">
      <TokenArcInspector events={tokenArcDebug.events ?? []} unavailableReason={tokenArcDebug.unavailableReason ?? null} />
    </div>

    <div class="grid gap-6 xl:grid-cols-3">
      <section class="rounded border border-zinc-200 bg-white p-4">
        <h2 class="mb-3 text-lg font-semibold">Promoted relations</h2>
        {#if topPromoted.length}
          <ul class="space-y-3 text-sm">
            {#each topPromoted as row}
              <li class="rounded border border-zinc-100 bg-zinc-50 p-3">
                <div class="font-medium">{row.subject.canonical_label} → {row.predicate_key} → {row.object.canonical_label}</div>
                <div class="mt-1 text-xs text-zinc-600">{row.event_id} · {row.confidence_tier}</div>
              </li>
            {/each}
          </ul>
        {:else}
          <p class="text-sm text-zinc-500">No promoted relations.</p>
        {/if}
      </section>

      <section class="rounded border border-zinc-200 bg-white p-4">
        <h2 class="mb-3 text-lg font-semibold">Candidate-only relations</h2>
        {#if topCandidate.length}
          <ul class="space-y-3 text-sm">
            {#each topCandidate as row}
              <li class="rounded border border-amber-100 bg-amber-50 p-3">
                <div class="font-medium">{row.subject.canonical_label} → {row.predicate_key} → {row.object.canonical_label}</div>
                <div class="mt-1 text-xs text-zinc-600">{row.event_id} · {row.confidence_tier}</div>
              </li>
            {/each}
          </ul>
        {:else}
          <p class="text-sm text-zinc-500">No candidate-only relations.</p>
        {/if}
      </section>

      <section class="rounded border border-zinc-200 bg-white p-4">
        <h2 class="mb-3 text-lg font-semibold">Unresolved mentions</h2>
        {#if unresolved.length}
          <ul class="space-y-3 text-sm">
            {#each unresolved as row}
              <li class="rounded border border-zinc-100 bg-zinc-50 p-3">
                <div class="font-medium">{row.surface_text}</div>
                <div class="mt-1 text-xs text-zinc-600">{row.event_id} · {row.resolution_rule}</div>
              </li>
            {/each}
          </ul>
        {:else}
          <p class="text-sm text-zinc-500">No unresolved mentions.</p>
        {/if}
      </section>
    </div>

    <div class="mt-6 grid gap-6 xl:grid-cols-2">
      <section class="rounded border border-zinc-200 bg-white p-4">
        <h2 class="mb-3 text-lg font-semibold">Top entities</h2>
        {#if perEntity.length}
          <ul class="space-y-3 text-sm">
            {#each perEntity as row}
              <li class="rounded border border-zinc-100 bg-zinc-50 p-3">
                <div class="font-medium">{row.entity.canonical_label}</div>
                <div class="mt-1 text-xs text-zinc-600">
                  {row.entity.entity_kind} · promoted {row.promoted_relation_count}
                  {#if row.candidate_relation_count !== undefined}
                    · candidate {row.candidate_relation_count}
                  {/if}
                </div>
              </li>
            {/each}
          </ul>
        {:else}
          <p class="text-sm text-zinc-500">No per-entity summary available.</p>
        {/if}
      </section>

      <section class="rounded border border-zinc-200 bg-white p-4">
        <h2 class="mb-3 text-lg font-semibold">Reviewed linkage summary</h2>
        {#if data.reviewedLinkage}
          <div class="space-y-3 text-sm">
            <div class="rounded border border-zinc-100 bg-zinc-50 p-3">
              <div class="font-medium">{data.reviewedLinkage.label}</div>
              <div class="mt-1 text-xs text-zinc-600">
                {perSeed.length} seeds · {unmatchedSeeds.length} unmatched · {ambiguousEvents.length} ambiguous events
              </div>
            </div>
            {#if unmatchedSeeds.length}
              <div>
                <div class="mb-1 text-xs uppercase text-zinc-500">Unmatched seeds</div>
                <div class="flex flex-wrap gap-2">
                  {#each unmatchedSeeds.slice(0, 12) as seedId}
                    <span class="rounded border border-zinc-200 bg-white px-2 py-1 text-xs">{seedId}</span>
                  {/each}
                </div>
              </div>
            {:else}
              <p class="text-sm text-zinc-500">All reviewed seeds matched at least one event.</p>
            {/if}
          </div>
        {:else}
          <p class="text-sm text-zinc-500">No reviewed linkage summary for this corpus.</p>
        {/if}
      </section>
    </div>

    {#if perSeed.length}
      <section class="mt-6 rounded border border-zinc-200 bg-white p-4">
        <h2 class="mb-3 text-lg font-semibold">{data.reviewedLinkage?.label ?? 'Reviewed seed coverage'}</h2>
        <div class="overflow-x-auto">
          <table class="min-w-full text-left text-sm">
            <thead class="border-b border-zinc-200 text-zinc-600">
              <tr>
                <th class="px-3 py-2 font-medium">Seed</th>
                <th class="px-3 py-2 font-medium">Matched</th>
                <th class="px-3 py-2 font-medium">Candidates</th>
              </tr>
            </thead>
            <tbody>
              {#each perSeed as row}
                <tr class="border-b border-zinc-100">
                  <td class="px-3 py-2">{row.seed_id}</td>
                  <td class="px-3 py-2">{row.matched_count}</td>
                  <td class="px-3 py-2">{row.candidate_count}</td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
      </section>
    {/if}
  {/if}
</div>
