<script lang="ts">
  import type { PageData } from './$types';
  import type { SuiteNormalizedArtifact } from '$lib/server/normalizedArtifacts';

  export let data: PageData;

  type ArtifactCard = {
    label: string;
    producer: string;
    source: string;
    artifact: Record<string, unknown> | null;
    inspect_href?: string | null;
    inspect_label?: string | null;
    gate?: {
      decision?: string;
      reason?: string;
      product_ref?: string;
    } | null;
    workflow?: {
      stage?: string;
      title?: string;
      recommended_view?: string;
      recommended_filter?: string | null;
      reason?: string;
    } | null;
    conformance: {
      artifactPresent: boolean;
      schemaVersion: string | null;
      schemaVersionMatches: boolean;
      artifactRole: string | null;
      requiredFieldCoverage: {
        total: number;
        satisfied: number;
        missing: string[];
      };
      authorityConsistency: {
        authorityClass: string | null;
        derived: boolean | null;
        hints: string[];
      };
      followObligationConsistency: {
        hasFollowObligation: boolean;
        unresolvedPressureStatus: string | null;
        hints: string[];
      };
      issues: string[];
    };
    error?: string | null;
  };

  const cards = [
    data.reviewArtifact,
    data.stateArtifact,
    data.archiveArtifactRef,
    data.captureArtifactRef,
    data.researchArtifactRef,
    data.conversationArtifactRef
  ].filter(Boolean) as ArtifactCard[];

  function asArtifact(value: Record<string, unknown> | null): SuiteNormalizedArtifact | null {
    return (value as SuiteNormalizedArtifact | null) ?? null;
  }

  function summaryEntries(artifact: SuiteNormalizedArtifact | null): Array<[string, unknown]> {
    if (!artifact?.summary) return [];
    return Object.entries(artifact.summary).slice(0, 8);
  }

  function lineageCount(artifact: SuiteNormalizedArtifact | null): number {
    return artifact?.lineage?.upstream_artifact_ids?.length ?? 0;
  }

  function lineagePreview(artifact: SuiteNormalizedArtifact | null): string[] {
    return artifact?.lineage?.upstream_artifact_ids?.slice(0, 4) ?? [];
  }

  function artifactQuestionRows(
    card: ArtifactCard,
    artifact: SuiteNormalizedArtifact | null
  ): Array<{ label: string; value: string }> {
    if (!artifact) return [];
    const unresolvedValue =
      artifact.unresolved_pressure_status === 'none'
        ? 'No open unresolved pressure recorded'
        : artifact.follow_obligation?.scope ?? artifact.unresolved_pressure_status ?? 'unknown';
    return [
      {
        label: 'What this is',
        value: [artifact.artifact_role, artifact.canonical_identity?.identity_class].filter(Boolean).join(' · ')
      },
      {
        label: 'Why it exists',
        value:
          card.workflow?.reason ||
          card.gate?.reason ||
          artifact.follow_obligation?.trigger ||
          `${artifact.provenance_anchor?.source_system ?? 'producer'} emitted this artifact`
      },
      {
        label: 'What supports it',
        value: `${lineageCount(artifact)} upstream artifact${lineageCount(artifact) === 1 ? '' : 's'}`
      },
      {
        label: 'What remains unresolved',
        value: unresolvedValue
      }
    ];
  }

  function gateTone(decision: string | undefined): string {
    if (decision === 'promote') return 'border-emerald-200 bg-emerald-50 text-emerald-900';
    if (decision === 'audit') return 'border-amber-200 bg-amber-50 text-amber-900';
    if (decision === 'abstain') return 'border-rose-200 bg-rose-50 text-rose-900';
    return 'border-zinc-200 bg-zinc-50 text-zinc-700';
  }

  function conformanceTone(issueCount: number): string {
    if (issueCount === 0) return 'border-emerald-200 bg-emerald-50 text-emerald-950';
    return 'border-amber-200 bg-amber-50 text-amber-950';
  }
</script>

<svelte:head>
  <title>Normalized Artifacts</title>
</svelte:head>

<div class="mx-auto max-w-7xl px-6 py-8">
  <div class="mb-6 flex flex-wrap items-end justify-between gap-4">
    <div>
      <h1 class="text-3xl font-semibold tracking-tight">Normalized Artifacts</h1>
      <p class="mt-1 text-sm text-zinc-600">
        Read-only suite contract view over current adopter families without local reinterpretation.
      </p>
    </div>
    <form method="GET" class="flex flex-wrap items-end gap-3">
      <label class="space-y-1 text-sm text-zinc-700">
        <span>Review workflow</span>
        <input class="rounded-xl border border-zinc-300 px-3 py-2" type="text" name="workflow" value={data.workflowKind} />
      </label>
      <label class="space-y-1 text-sm text-zinc-700">
        <span>Workflow run</span>
        <input class="rounded-xl border border-zinc-300 px-3 py-2" type="text" name="workflowRunId" value={data.workflowRunId ?? ''} />
      </label>
      <label class="space-y-1 text-sm text-zinc-700">
        <span>SB date</span>
        <input class="rounded-xl border border-zinc-300 px-3 py-2" type="date" name="sbDate" value={data.sbDate ?? ''} />
      </label>
      <label class="space-y-1 text-sm text-zinc-700">
        <span>Archive artifact</span>
        <input
          class="w-[24rem] rounded-xl border border-zinc-300 px-3 py-2"
          type="text"
          name="archiveArtifact"
          value={data.archiveArtifact ?? ''}
          placeholder="chat-export-structurer/output/archive.normalized.json"
        />
      </label>
      <label class="space-y-1 text-sm text-zinc-700">
        <span>Capture artifact</span>
        <input
          class="w-[24rem] rounded-xl border border-zinc-300 px-3 py-2"
          type="text"
          name="captureArtifact"
          value={data.captureArtifact ?? ''}
          placeholder="tircorder-JOBBIE/output/capture.normalized.json"
        />
      </label>
      <label class="space-y-1 text-sm text-zinc-700">
        <span>Research artifact</span>
        <input
          class="w-[24rem] rounded-xl border border-zinc-300 px-3 py-2"
          type="text"
          name="researchArtifact"
          value={data.researchArtifact ?? ''}
          placeholder="notebooklm-py/output/research-follow.normalized.json"
        />
      </label>
      <label class="space-y-1 text-sm text-zinc-700">
        <span>Conversation artifact</span>
        <input
          class="w-[24rem] rounded-xl border border-zinc-300 px-3 py-2"
          type="text"
          name="conversationArtifact"
          value={data.conversationArtifact ?? ''}
          placeholder="reverse-engineered-chatgpt/output/conversation.normalized.json"
        />
      </label>
      <button class="rounded-full bg-zinc-950 px-4 py-2 text-sm font-medium text-white" type="submit">Load</button>
    </form>
  </div>

  <section class="mb-6 rounded-3xl border border-zinc-200 bg-zinc-50 p-5 text-sm text-zinc-700">
    <p class="font-medium text-zinc-900">Shared contract</p>
    <p class="mt-2">
      This surface reads the suite normalized artifact shape from the producing repos directly. It does not reinterpret
      compiled state as review output, and it does not reinterpret review output as state.
    </p>
    <p class="mt-2">
      The operator questions are explicit here: what this artifact is, why it exists, what supports it, and what remains unresolved.
    </p>
    <p class="mt-2">
      Capture/archive adoption is explicit-path only for now. If you pass one `chat-export-structurer` normalized artifact path,
      the route reads that producer-owned archive artifact directly and keeps it archive-shaped.
    </p>
    <p class="mt-2">
      Capture producer adoption works the same way: pass one `tircorder-JOBBIE` normalized source-artifact sidecar path and the
      route reads it directly without reclassifying capture as archive, state, or review output.
    </p>
    <p class="mt-2">
      Retrieval producer adoption is explicit-path too: pass one `notebooklm-py` research-follow normalized artifact path and the
      route keeps it as a derived inspection surface rather than treating it as archive, state, or promoted truth.
    </p>
    <p class="mt-2">
      Live acquisition/chat producer adoption is explicit-path too: pass one `reverse-engineered-chatgpt` conversation normalized
      artifact path and the route keeps it as a source/acquisition artifact rather than flattening it into downstream archive or review output.
    </p>
  </section>

  <section class="grid gap-6 lg:grid-cols-2">
    {#each cards as card}
      {@const artifact = asArtifact(card.artifact)}
      <article class="rounded-3xl border border-zinc-200 bg-white p-6 shadow-sm">
        <div class="flex items-start justify-between gap-4">
          <div>
            <p class="text-xs uppercase tracking-[0.2em] text-zinc-500">{card.producer}</p>
            <h2 class="mt-1 text-xl font-semibold text-zinc-950">{card.label}</h2>
            <p class="mt-1 break-all text-xs text-zinc-500">{card.source}</p>
          </div>
          {#if artifact?.artifact_role}
            <span class="rounded-full border border-zinc-300 bg-zinc-50 px-3 py-1 text-xs font-medium text-zinc-700">
              {artifact.artifact_role}
            </span>
          {/if}
        </div>

        {#if card.error}
          <p class="mt-4 rounded-2xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">{card.error}</p>
        {:else if artifact}
          <div class="mt-5 grid gap-3 md:grid-cols-2">
            {#each artifactQuestionRows(card, artifact) as row}
              <div class="rounded-2xl border border-zinc-200 bg-zinc-50 px-4 py-3">
                <div class="text-[11px] uppercase tracking-[0.16em] text-zinc-500">{row.label}</div>
                <div class="mt-1 text-sm font-medium text-zinc-900">{row.value}</div>
              </div>
            {/each}
          </div>

          <div class={`mt-5 rounded-2xl border px-4 py-3 text-sm ${conformanceTone(card.conformance.issues.length)}`}>
            <div class="text-[11px] uppercase tracking-[0.16em]">Contract conformance</div>
            <div class="mt-1 font-medium">
              {card.conformance.requiredFieldCoverage.satisfied}/{card.conformance.requiredFieldCoverage.total} required fields present
            </div>
            <div class="mt-1 text-xs">
              Schema: {card.conformance.schemaVersion ?? 'missing'}
              {#if card.conformance.schemaVersionMatches}
                · matches root contract
              {:else}
                · contract mismatch
              {/if}
            </div>
            <div class="mt-1 text-xs">
              Authority: {card.conformance.authorityConsistency.authorityClass ?? 'unknown'}
              {#if typeof card.conformance.authorityConsistency.derived === 'boolean'}
                · {card.conformance.authorityConsistency.derived ? 'derived' : 'non-derived'}
              {/if}
            </div>
            {#if card.conformance.issues.length > 0}
              <div class="mt-2 text-xs">Issues: {card.conformance.issues.slice(0, 3).join(' · ')}</div>
            {:else}
              <div class="mt-2 text-xs">No contract issues detected in the loaded payload.</div>
            {/if}
          </div>

          {#if card.gate?.decision}
            <div class={`mt-5 rounded-2xl border px-4 py-3 text-sm ${gateTone(card.gate.decision)}`}>
              <div class="text-[11px] uppercase tracking-[0.16em]">Promotion gate</div>
              <div class="mt-1 font-medium">{card.gate.decision}</div>
              {#if card.gate.reason}
                <div class="mt-1 text-xs">{card.gate.reason}</div>
              {/if}
              {#if card.gate.product_ref}
                <div class="mt-1 font-mono text-xs">{card.gate.product_ref}</div>
              {/if}
            </div>
          {/if}

          {#if card.workflow?.recommended_view || card.inspect_href}
            <div class="mt-5 rounded-2xl border border-sky-200 bg-sky-50 px-4 py-3 text-sm text-sky-950">
              <div class="text-[11px] uppercase tracking-[0.16em] text-sky-700">Recommended next action</div>
              <div class="mt-1 font-medium">{card.workflow?.title ?? card.inspect_label ?? 'Open inspection surface'}</div>
              {#if card.workflow?.reason}
                <div class="mt-1 text-xs text-sky-800">{card.workflow.reason}</div>
              {/if}
              {#if card.workflow?.recommended_view}
                <div class="mt-1 text-xs text-sky-800">
                  View: <span class="font-mono">{card.workflow.recommended_view}</span>
                  {#if card.workflow.recommended_filter}
                    · Filter: <span class="font-mono">{card.workflow.recommended_filter}</span>
                  {/if}
                </div>
              {/if}
              {#if card.inspect_href}
                <a class="mt-3 inline-flex rounded-full bg-sky-950 px-4 py-2 text-xs font-medium text-white" href={card.inspect_href}>
                  {card.inspect_label ?? 'Open inspection surface'}
                </a>
              {/if}
            </div>
          {/if}

          <dl class="mt-5 grid gap-3 text-sm text-zinc-700">
            <div>
              <dt class="text-xs uppercase tracking-[0.2em] text-zinc-500">Schema</dt>
              <dd class="mt-1 font-mono text-zinc-900">{artifact.schema_version}</dd>
            </div>
            <div>
              <dt class="text-xs uppercase tracking-[0.2em] text-zinc-500">Identity</dt>
              <dd class="mt-1 text-zinc-900">{artifact.canonical_identity?.identity_class} · {artifact.canonical_identity?.identity_key}</dd>
            </div>
            <div>
              <dt class="text-xs uppercase tracking-[0.2em] text-zinc-500">Authority</dt>
              <dd class="mt-1 text-zinc-900">
                {artifact.authority?.authority_class}
                {#if typeof artifact.authority?.derived === 'boolean'}
                  · {artifact.authority.derived ? 'derived' : 'non-derived'}
                {/if}
              </dd>
            </div>
            <div>
              <dt class="text-xs uppercase tracking-[0.2em] text-zinc-500">Unresolved pressure</dt>
              <dd class="mt-1 text-zinc-900">{artifact.unresolved_pressure_status ?? 'unknown'}</dd>
            </div>
            <div>
              <dt class="text-xs uppercase tracking-[0.2em] text-zinc-500">Upstream artifacts</dt>
              <dd class="mt-1 text-zinc-900">{lineageCount(artifact)}</dd>
              {#if lineagePreview(artifact).length > 0}
                <div class="mt-2 flex flex-wrap gap-2">
                  {#each lineagePreview(artifact) as artifactId}
                    <span class="rounded-full border border-zinc-200 bg-zinc-50 px-3 py-1 text-[11px] font-mono text-zinc-700">
                      {artifactId}
                    </span>
                  {/each}
                </div>
              {/if}
            </div>
            {#if artifact.follow_obligation}
              <div>
                <dt class="text-xs uppercase tracking-[0.2em] text-zinc-500">Follow obligation</dt>
                <dd class="mt-1 text-zinc-900">{artifact.follow_obligation.trigger}</dd>
                <dd class="text-xs text-zinc-600">{artifact.follow_obligation.scope}</dd>
              </div>
            {/if}
            {#if card.conformance.followObligationConsistency.hints.length > 0}
              <div>
                <dt class="text-xs uppercase tracking-[0.2em] text-zinc-500">Follow checks</dt>
                <dd class="mt-1 text-zinc-900">{card.conformance.followObligationConsistency.hints.join(' · ')}</dd>
              </div>
            {/if}
            {#if card.conformance.authorityConsistency.hints.length > 0}
              <div>
                <dt class="text-xs uppercase tracking-[0.2em] text-zinc-500">Authority checks</dt>
                <dd class="mt-1 text-zinc-900">{card.conformance.authorityConsistency.hints.join(' · ')}</dd>
              </div>
            {/if}
          </dl>

          {#if summaryEntries(artifact).length > 0}
            <div class="mt-5">
              <p class="text-xs uppercase tracking-[0.2em] text-zinc-500">Summary</p>
              <div class="mt-2 grid gap-2 sm:grid-cols-2">
                {#each summaryEntries(artifact) as [key, value]}
                  <div class="rounded-2xl border border-zinc-200 bg-zinc-50 px-3 py-2">
                    <div class="text-[11px] uppercase tracking-[0.16em] text-zinc-500">{key}</div>
                    <div class="mt-1 text-sm font-medium text-zinc-900">{String(value)}</div>
                  </div>
                {/each}
              </div>
            </div>
          {/if}
        {:else}
          <p class="mt-4 text-sm text-zinc-600">No normalized artifact was available.</p>
        {/if}
      </article>
    {/each}
  </section>
</div>
