<script lang="ts">
  import DashboardShell from '$lib/sb-dashboard/components/DashboardShell.svelte';
  import Panel from '$lib/ui/Panel.svelte';
  import Section from '$lib/ui/Section.svelte';

  export let data: {
    detail: {
      key: string;
      label: string;
      artifactPath: string;
      headline: Array<{ label: string; value: string | number }>;
      families?: Array<{
        key: string;
        label: string;
        stats: Array<{ label: string; value: string | number }>;
        unresolvedSurfaces?: string[];
        mentionHeavyEvents?: Array<{ eventId: string; mentionCount: number; matchCount: number; text: string }>;
      }>;
      seedDiagnostics?: Array<{
        seedId: string;
        linkageKind: string;
        actionSummary: string;
        families: Array<{
          sourceFamily: string;
          reviewStatus: string;
          matchedEventCount: number;
          candidateEventCount: number;
          supportKind: string;
          sampleEvents: Array<{ eventId: string; confidence: string; matched: boolean; receiptKinds: string[]; text: string }>;
        }>;
      }>;
      workflowSummaries?: Array<{
        workflowKind: string;
        stats: Array<{ label: string; value: string | number }>;
      }>;
      bundlePressure?: Array<{
        sourceLabel: string;
        workflowKind: string;
        bundlePath: string;
        pressureScore: number;
        contestedItemCount: number;
        reviewQueueCount: number;
        factCount: number;
        eventCount: number;
      }>;
      rawSourceBacklog?: {
        root: string;
        fileCount: number;
        filesBySuffix: Record<string, number>;
        files: string[];
      } | null;
    };
  };
</script>

<DashboardShell title={data.detail.label}>
  <Section title={data.detail.label} subtitle={data.detail.key}>
    <div class="text-sm text-ink-800/75 break-all">{data.detail.artifactPath}</div>
  </Section>

  <div class="grid gap-4 lg:grid-cols-4">
    {#each data.detail.headline as item}
      <Panel>
        <div class="text-[10px] uppercase tracking-widest text-ink-800/60">{item.label}</div>
        <div class="mt-2 text-sm text-ink-950">{item.value}</div>
      </Panel>
    {/each}
  </div>

  {#if data.detail.families?.length}
    <Section title="Families" subtitle="Per-family pressure, unresolved surfaces, and mention-heavy events." />
    <div class="space-y-4">
      {#each data.detail.families as family}
        <Panel>
          <div class="text-sm text-ink-950">{family.label}</div>
          <div class="mt-2 flex flex-wrap gap-2">
            {#each family.stats as stat}
              <span class="inline-flex items-center rounded-full bg-paper-100 px-2 py-1 text-[10px] font-mono uppercase tracking-widest text-ink-900 ring-1 ring-ink-900/10">
                {stat.label}: {stat.value}
              </span>
            {/each}
          </div>

          {#if family.unresolvedSurfaces?.length}
            <div class="mt-4">
              <div class="text-[10px] uppercase tracking-widest text-ink-800/60">Top unresolved surfaces</div>
              <div class="mt-2 flex flex-wrap gap-2">
                {#each family.unresolvedSurfaces as surface}
                  <span class="inline-flex items-center rounded-full bg-paper-100 px-2 py-1 text-[10px] font-mono text-ink-900 ring-1 ring-ink-900/10">
                    {surface}
                  </span>
                {/each}
              </div>
            </div>
          {/if}

          {#if family.mentionHeavyEvents?.length}
            <div class="mt-4 space-y-2">
              <div class="text-[10px] uppercase tracking-widest text-ink-800/60">Mention-heavy events</div>
              {#each family.mentionHeavyEvents as event}
                <div class="rounded-lg bg-paper-50 px-3 py-2 ring-1 ring-ink-900/10">
                  <div class="font-mono text-[11px] text-ink-800/65">{event.eventId}</div>
                  <div class="mt-1 text-[11px] text-ink-800/70">mentions={event.mentionCount} matches={event.matchCount}</div>
                  <div class="mt-2 text-sm text-ink-950">{event.text}</div>
                </div>
              {/each}
            </div>
          {/if}
        </Panel>
      {/each}
    </div>
  {/if}

  {#if data.detail.seedDiagnostics?.length}
    <Section title="Seed Diagnostics" subtitle="Matched/candidate family support with sample events." />
    <div class="space-y-4">
      {#each data.detail.seedDiagnostics as seed}
        <Panel>
          <div class="text-sm text-ink-950">{seed.actionSummary || seed.seedId}</div>
          <div class="mt-1 font-mono text-[11px] text-ink-800/65">{seed.seedId} · {seed.linkageKind}</div>
          <div class="mt-3 space-y-3">
            {#each seed.families as family}
              <div class="rounded-xl bg-paper-50 px-3 py-3 ring-1 ring-ink-900/10">
                <div class="flex flex-wrap items-center gap-2">
                  <span class="text-sm text-ink-950">{family.sourceFamily}</span>
                  <span class="inline-flex items-center rounded-full bg-paper-100 px-2 py-1 text-[10px] font-mono uppercase tracking-widest text-ink-900 ring-1 ring-ink-900/10">
                    {family.reviewStatus}
                  </span>
                  <span class="inline-flex items-center rounded-full bg-paper-100 px-2 py-1 text-[10px] font-mono uppercase tracking-widest text-ink-900 ring-1 ring-ink-900/10">
                    support: {family.supportKind}
                  </span>
                </div>
                <div class="mt-2 flex flex-wrap gap-2">
                  <span class="inline-flex items-center rounded-full bg-paper-100 px-2 py-1 text-[10px] font-mono uppercase tracking-widest text-ink-900 ring-1 ring-ink-900/10">
                    matched events: {family.matchedEventCount}
                  </span>
                  <span class="inline-flex items-center rounded-full bg-paper-100 px-2 py-1 text-[10px] font-mono uppercase tracking-widest text-ink-900 ring-1 ring-ink-900/10">
                    candidate events: {family.candidateEventCount}
                  </span>
                </div>
                {#if family.sampleEvents.length}
                  <div class="mt-3 space-y-2">
                    {#each family.sampleEvents as event}
                      <div class="rounded-lg bg-paper-100 px-3 py-2 ring-1 ring-ink-900/10">
                        <div class="font-mono text-[11px] text-ink-800/65">{event.eventId}</div>
                        <div class="mt-1 text-[11px] text-ink-800/70">
                          confidence={event.confidence} matched={event.matched ? 'yes' : 'no'} receipts={event.receiptKinds.join(', ') || '-'}
                        </div>
                        <div class="mt-2 text-sm text-ink-950">{event.text}</div>
                      </div>
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

  {#if data.detail.workflowSummaries?.length}
    <Section title="Workflow Summaries" subtitle="Workflow-level bundle pressure and counts." />
    <div class="space-y-4">
      {#each data.detail.workflowSummaries as workflow}
        <Panel>
          <div class="text-sm text-ink-950">{workflow.workflowKind}</div>
          <div class="mt-2 flex flex-wrap gap-2">
            {#each workflow.stats as stat}
              <span class="inline-flex items-center rounded-full bg-paper-100 px-2 py-1 text-[10px] font-mono uppercase tracking-widest text-ink-900 ring-1 ring-ink-900/10">
                {stat.label}: {stat.value}
              </span>
            {/each}
          </div>
        </Panel>
      {/each}
    </div>
  {/if}

  {#if data.detail.bundlePressure?.length}
    <Section title="Bundle Pressure" subtitle="Per-bundle workbench pressure inventory." />
    <div class="space-y-3">
      {#each data.detail.bundlePressure as bundle}
        <Panel>
          <div class="text-sm text-ink-950">{bundle.sourceLabel}</div>
          <div class="mt-1 font-mono text-[11px] text-ink-800/65">{bundle.workflowKind}</div>
          <div class="mt-2 flex flex-wrap gap-2">
            <span class="inline-flex items-center rounded-full bg-paper-100 px-2 py-1 text-[10px] font-mono uppercase tracking-widest text-ink-900 ring-1 ring-ink-900/10">pressure: {bundle.pressureScore}</span>
            <span class="inline-flex items-center rounded-full bg-paper-100 px-2 py-1 text-[10px] font-mono uppercase tracking-widest text-ink-900 ring-1 ring-ink-900/10">facts: {bundle.factCount}</span>
            <span class="inline-flex items-center rounded-full bg-paper-100 px-2 py-1 text-[10px] font-mono uppercase tracking-widest text-ink-900 ring-1 ring-ink-900/10">events: {bundle.eventCount}</span>
            <span class="inline-flex items-center rounded-full bg-paper-100 px-2 py-1 text-[10px] font-mono uppercase tracking-widest text-ink-900 ring-1 ring-ink-900/10">queue: {bundle.reviewQueueCount}</span>
            <span class="inline-flex items-center rounded-full bg-paper-100 px-2 py-1 text-[10px] font-mono uppercase tracking-widest text-ink-900 ring-1 ring-ink-900/10">contested: {bundle.contestedItemCount}</span>
          </div>
          <div class="mt-2 font-mono text-[11px] text-ink-800/65 break-all">{bundle.bundlePath}</div>
        </Panel>
      {/each}
    </div>
  {/if}

  {#if data.detail.rawSourceBacklog}
    <Section title="Raw Source Backlog" subtitle="Outstanding raw-source inventory still outside full semantic shaping." />
    <Panel>
      <div class="font-mono text-[11px] text-ink-800/65 break-all">{data.detail.rawSourceBacklog.root}</div>
      <div class="mt-2 flex flex-wrap gap-2">
        <span class="inline-flex items-center rounded-full bg-paper-100 px-2 py-1 text-[10px] font-mono uppercase tracking-widest text-ink-900 ring-1 ring-ink-900/10">
          file count: {data.detail.rawSourceBacklog.fileCount}
        </span>
        {#each Object.entries(data.detail.rawSourceBacklog.filesBySuffix) as [suffix, count]}
          <span class="inline-flex items-center rounded-full bg-paper-100 px-2 py-1 text-[10px] font-mono uppercase tracking-widest text-ink-900 ring-1 ring-ink-900/10">
            {suffix}: {count}
          </span>
        {/each}
      </div>
      {#if data.detail.rawSourceBacklog.files.length}
        <div class="mt-4 space-y-1">
          {#each data.detail.rawSourceBacklog.files as file}
            <div class="font-mono text-[11px] text-ink-950 break-all">{file}</div>
          {/each}
        </div>
      {/if}
    </Panel>
  {/if}
</DashboardShell>
