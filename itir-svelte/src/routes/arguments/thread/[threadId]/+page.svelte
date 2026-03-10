<script lang="ts">
  import Panel from '$lib/ui/Panel.svelte';
  import Section from '$lib/ui/Section.svelte';
  import DashboardShell from '$lib/sb-dashboard/components/DashboardShell.svelte';
  import LayeredGraph from '$lib/ui/LayeredGraph.svelte';
  import { buildClaimGraph, type ThreadArgumentsWorkbench } from '$lib/arguments/workbench';
  import { createSelectionBridge } from '$lib/workbench/selectionBridge';
  import { tick } from 'svelte';

export let data: { workbench: ThreadArgumentsWorkbench; stateReason?: string };

  type HighlightMode = 'literal' | 'family';
  type InspectorTab = 'Claim' | 'Counterpoints' | 'Graph';
  const defaultRoleStyle = {
    wrap: 'justify-start',
    bubble: 'bg-paper-100 text-ink-950 ring-ink-900/10',
    meta: 'text-ink-800/60'
  };

  const workbench = data.workbench;
  const roleStyle: Record<string, { wrap: string; bubble: string; meta: string }> = {
    user: {
      wrap: 'justify-end',
      bubble: 'bg-gradient-to-br from-sky-600/10 to-blue-600/5 text-ink-950 ring-ink-900/10',
      meta: 'text-ink-800/60'
    },
    assistant: {
      wrap: 'justify-start',
      bubble: 'bg-paper-50 text-ink-950 ring-ink-900/10',
      meta: 'text-ink-800/60'
    },
    tool: {
      wrap: 'justify-start',
      bubble: 'bg-gradient-to-br from-paper-100 to-paper-50 text-ink-950 ring-ink-900/10',
      meta: 'text-ink-800/60'
    },
    system: {
      wrap: 'justify-start',
      bubble: 'bg-paper-100 text-ink-950 ring-ink-900/10',
      meta: 'text-ink-800/60'
    },
    other: defaultRoleStyle
  };

  let highlightMode: HighlightMode = 'literal';
  let activeTab: InspectorTab = 'Claim';
  let selectedClaimIds = [...workbench.defaultSelectedClaimIds];
  let hoveredClaimId: string | null = null;
  const claimSelectionBridge = createSelectionBridge<string>(workbench.defaultSelectedClaimIds[0] ?? null);

  const claimsById = new Map(workbench.claims.map((row) => [row.id, row]));
  const anchorsByMessage = new Map<string, typeof workbench.anchors>();
  for (const anchor of workbench.anchors) {
    const rows = anchorsByMessage.get(anchor.messageId) ?? [];
    rows.push(anchor);
    anchorsByMessage.set(anchor.messageId, rows);
  }
  const familiesById = new Map(workbench.families.map((row) => [row.id, row]));
  const badgesByMessage = new Map(workbench.badges.map((row) => [row.messageId, row]));
  type Claim = ThreadArgumentsWorkbench['claims'][number];
  type RenderSegment = { kind: 'text'; text: string; key: string } | { kind: 'anchor'; text: string; key: string; anchorId: string };

  function familyColor(familyId: string): string {
    return familiesById.get(familyId)?.color ?? '#6b7280';
  }

  function styleForRole(role: string | null | undefined): { wrap: string; bubble: string; meta: string } {
    const key = role?.toLowerCase?.() ?? 'other';
    const style = roleStyle[key];
    return style ?? defaultRoleStyle;
  }

  function selectedClaims(): Claim[] {
    return selectedClaimIds
      .map((id) => claimsById.get(id))
      .filter((value): value is Claim => Boolean(value));
  }

  function primaryClaim(): Claim | null {
    return claimsById.get(selectedClaimIds[0] ?? '') ?? null;
  }

  function claimsForMessage(messageId: string): Claim[] {
    return (anchorsByMessage.get(messageId) ?? [])
      .map((anchor) => claimsById.get(anchor.claimId))
      .filter((value): value is Claim => Boolean(value))
      .filter((value, index, array) => array.findIndex((row) => row?.id === value?.id) === index);
  }

  function visibleAnchors(messageId: string) {
    const anchors = anchorsByMessage.get(messageId) ?? [];
    if (highlightMode === 'literal') return anchors;
    const selectedFamilies = new Set(selectedClaims().map((row) => row?.familyId));
    if (!selectedFamilies.size) return [];
    return anchors.filter((row) => selectedFamilies.has(row.familyId));
  }

  function renderSegments(text: string, messageId: string): RenderSegment[] {
    const anchors = visibleAnchors(messageId)
      .slice()
      .sort((a, b) => a.charStart - b.charStart || a.charEnd - b.charEnd);
    if (!anchors.length || highlightMode !== 'literal') {
      return [{ kind: 'text', text, key: `${messageId}:text:0` }];
    }
    const segments: RenderSegment[] = [];
    let cursor = 0;
    for (const anchor of anchors) {
      const start = Math.max(0, Math.min(text.length, anchor.charStart));
      const end = Math.max(start, Math.min(text.length, anchor.charEnd));
      if (start > cursor) {
        segments.push({ kind: 'text', text: text.slice(cursor, start), key: `${anchor.id}:pre` });
      }
      segments.push({ kind: 'anchor', text: text.slice(start, end), key: anchor.id, anchorId: anchor.id });
      cursor = end;
    }
    if (cursor < text.length) {
      segments.push({ kind: 'text', text: text.slice(cursor), key: `${messageId}:tail` });
    }
    return segments;
  }

  function selectClaim(claimId: string, additive = false) {
    if (!additive) {
      selectedClaimIds = [claimId];
      claimSelectionBridge.setActive(claimId, 'select');
      activeTab = 'Claim';
      void scrollClaimIntoView(claimId);
      return;
    }
    if (selectedClaimIds.includes(claimId)) {
      selectedClaimIds = selectedClaimIds.filter((row) => row !== claimId);
      if (!selectedClaimIds.length) selectedClaimIds = [claimId];
    } else {
      selectedClaimIds = [...selectedClaimIds, claimId].slice(0, 3);
    }
    claimSelectionBridge.setActive(selectedClaimIds[0] ?? null, 'sync');
  }

  async function scrollClaimIntoView(claimId: string) {
    await tick();
    const claim = claimsById.get(claimId);
    const messageId = claim?.messageIds?.[0];
    if (!messageId) return;
    const el = document.getElementById(`arg-msg-${messageId}`);
    el?.scrollIntoView({ block: 'center', behavior: 'smooth' });
  }

  function onAnchorClick(event: MouseEvent, claimId: string) {
    selectClaim(claimId, event.shiftKey);
  }

  function anchorClaim(anchorId: string) {
    const anchor = workbench.anchors.find((row) => row.id === anchorId);
    return anchor ? claimsById.get(anchor.claimId) ?? null : null;
  }

  function messageFamilyIds(messageId: string) {
    return badgesByMessage.get(messageId)?.familyIds ?? [];
  }

  function familyModeActive(messageId: string) {
    if (highlightMode !== 'family') return false;
    const selectedFamilies = new Set(selectedClaims().map((row) => row?.familyId));
    return messageFamilyIds(messageId).some((row) => selectedFamilies.has(row));
  }

  $: currentClaims = selectedClaims();
  $: currentClaim = primaryClaim();
  $: hoveredClaimId = $claimSelectionBridge.hovered;
  $: reviewState = data.stateReason ?? (workbench.unavailableReason ? 'unsupported' : 'ready');
  $: graphPayload = buildClaimGraph(workbench, selectedClaimIds);
  $: graphViewportKey = `${selectedClaimIds.join('|')}:${graphPayload.edges.length}:${graphPayload.layers.map((row) => row.nodes.length).join(',')}`;
  $: counterpoints = Array.from(
    new Map<string, Claim>(
      currentClaims
        .flatMap((claim) => claim.counterpointIds ?? [])
        .map((id) => [id, claimsById.get(id)] as const)
        .filter((entry): entry is readonly [string, Claim] => Boolean(entry[1]))
    ).values()
  );
  $: miniMapRows = workbench.messages.map((message) => ({
    messageId: message.message_id,
    familyIds: messageFamilyIds(message.message_id)
  }));
</script>

<svelte:head>
  <title>Arguments Workbench</title>
</svelte:head>

<DashboardShell title="Arguments Workbench">
  <Section
    title={workbench.title ?? '(untitled thread)'}
    subtitle={`thread_id=${workbench.threadId}${workbench.sourceThreadId ? ` | source=${workbench.sourceThreadId}` : ''}`}
  >
    <div class="mb-3 flex items-center gap-2">
      <span class="text-xs uppercase tracking-[0.24em] text-ink-800/70">state</span>
      <span class="rounded bg-paper-100 px-2 py-1 font-mono text-[11px]">{reviewState}</span>
    </div>
    <div slot="actions" class="flex flex-wrap items-center gap-2">
      <button
        type="button"
        class={`rounded-lg px-3 py-2 text-xs uppercase tracking-widest ring-1 ${highlightMode === 'literal' ? 'bg-ink-900 text-paper-50 ring-ink-900' : 'bg-paper-100 ring-ink-900/10'}`}
        on:click={() => {
          highlightMode = 'literal';
          claimSelectionBridge.setScope('local');
        }}
      >
        Literal
      </button>
      <button
        type="button"
        class={`rounded-lg px-3 py-2 text-xs uppercase tracking-widest ring-1 ${highlightMode === 'family' ? 'bg-ink-900 text-paper-50 ring-ink-900' : 'bg-paper-100 ring-ink-900/10'}`}
        on:click={() => {
          highlightMode = 'family';
          claimSelectionBridge.setScope('expanded');
        }}
      >
        Family
      </button>
      <a
        class="rounded-lg bg-paper-100 px-3 py-2 text-xs uppercase tracking-widest ring-1 ring-ink-900/10"
        href={`/thread/${encodeURIComponent(workbench.threadId)}`}
      >
        Open raw thread
      </a>
    </div>

    {#if workbench.unavailableReason}
      <Panel tone="danger">
        <div class="text-sm text-ink-900">{workbench.unavailableReason}</div>
      </Panel>
    {:else}
      <div class="grid gap-4 xl:grid-cols-[minmax(0,1.25fr)_minmax(22rem,0.9fr)]">
        <Panel>
          <div class="text-xs uppercase tracking-[0.28em] text-ink-800/70">Thread transcript</div>
          <div class="mt-2 text-sm text-ink-800/70">
            Click a highlight to inspect that claim. Shift-click to compare up to three claims. Family mode broadens the highlight from literal spans to every related message.
          </div>
          <div class="mt-4 max-h-[72vh] overflow-y-auto pr-2">
            <div class="space-y-4">
              {#each workbench.messages as message}
                {@const badge = badgesByMessage.get(message.message_id)}
                {@const segments = renderSegments(message.text ?? '', message.message_id)}
                {@const messageClaims = claimsForMessage(message.message_id)}
                <div id={`arg-msg-${message.message_id}`} class={`grid grid-cols-[2.4rem_minmax(0,1fr)] gap-3 ${styleForRole(message.role).wrap === 'justify-end' ? 'justify-items-end' : ''}`}>
                  <div class="flex flex-col items-center gap-2 pt-2">
                    {#if messageFamilyIds(message.message_id).length}
                      {#each messageFamilyIds(message.message_id) as familyId}
                        <button
                          type="button"
                          class="h-3 w-3 rounded-full ring-2 ring-white/80"
                          style={`background:${familyColor(familyId)}`}
                          title={familiesById.get(familyId)?.label ?? familyId}
                          on:click={() => {
                            const claim = workbench.claims.find((row) => row.familyId === familyId);
                            if (claim) selectClaim(claim.id);
                          }}
                        ></button>
                      {/each}
                    {/if}
                  </div>
                  <div class={`max-w-[52rem] ${styleForRole(message.role).wrap === 'justify-end' ? 'justify-self-end' : ''}`}>
                    <div class={`rounded-2xl px-4 py-3 shadow-crisp ring-1 ${styleForRole(message.role).bubble} ${familyModeActive(message.message_id) ? 'ring-2 ring-offset-2 ring-offset-paper-25' : ''}`} style={familyModeActive(message.message_id) ? `box-shadow: inset 0 0 0 1px ${familyColor(currentClaim?.familyId ?? 'other')}33` : ''}>
                      <div class="whitespace-pre-wrap break-words text-sm leading-relaxed">
                        {#each segments as segment}
                          {#if segment.kind === 'text'}
                            <span>{segment.text}</span>
                          {:else}
                            {@const claim = anchorClaim(segment.anchorId)}
                            <button
                              type="button"
                              class={`rounded px-0.5 py-[1px] underline decoration-dotted underline-offset-2 ${selectedClaimIds.includes(claim?.id ?? '') ? 'ring-1 ring-ink-900/20' : ''}`}
                              style={`background:${familyColor(claim?.familyId ?? 'other')}22; text-decoration-color:${familyColor(claim?.familyId ?? 'other')}`}
                              title={`${claim?.predicateKey ?? 'claim'}: ${claim?.normalizedText ?? ''}`}
                              on:mouseenter={() => claimSelectionBridge.setHovered(claim?.id ?? null, 'hover')}
                              on:mouseleave={() => claimSelectionBridge.setHovered(null, 'clear')}
                              on:click={(event) => onAnchorClick(event, claim?.id ?? '')}
                            >
                              {segment.text}
                            </button>
                          {/if}
                        {/each}
                      </div>
                    </div>
                    <div class={`mt-1 flex items-center gap-2 px-1 text-[11px] ${styleForRole(message.role).meta}`}>
                      <div class="font-mono uppercase tracking-widest">{message.role}</div>
                      <div class="font-mono">{message.ts?.slice(11, 19)}</div>
                      {#if badge && (badge.claimCount || badge.counterpointCount || badge.refCount)}
                        <div class="ml-auto flex flex-wrap gap-2">
                          {#if badge.claimCount}
                            <span class="rounded-full bg-paper-100 px-2 py-1 font-mono">{badge.claimCount} claims</span>
                          {/if}
                          {#if badge.counterpointCount}
                            <span class="rounded-full bg-paper-100 px-2 py-1 font-mono">{badge.counterpointCount} counterpoints</span>
                          {/if}
                          {#if badge.refCount}
                            <span class="rounded-full bg-paper-100 px-2 py-1 font-mono">{badge.refCount} refs</span>
                          {/if}
                        </div>
                      {/if}
                    </div>
                    {#if messageClaims.length}
                      <div class="mt-2 flex flex-wrap gap-2 px-1">
                        {#each messageClaims as claim}
                          <button
                            type="button"
                            class={`rounded-full border px-2 py-1 text-[11px] ${selectedClaimIds.includes(claim.id) ? 'border-ink-900 bg-ink-900 text-paper-50' : 'border-ink-900/10 bg-paper-100 text-ink-900'}`}
                            on:click={(event) => selectClaim(claim.id, event.shiftKey)}
                          >
                            {familiesById.get(claim.familyId)?.label ?? claim.familyId}: {claim.predicateKey}
                          </button>
                        {/each}
                      </div>
                    {/if}
                  </div>
                </div>
              {/each}
            </div>
          </div>
          <div class="mt-4 border-t border-ink-900/10 pt-4">
            <div class="mb-2 text-xs uppercase tracking-[0.24em] text-ink-800/60">Thread mini-map</div>
            <div class="grid grid-cols-[repeat(auto-fit,minmax(14px,1fr))] gap-1">
              {#each miniMapRows as row}
                <button
                  type="button"
                  class="h-8 rounded-sm ring-1 ring-ink-900/10"
                  style={`background:${row.familyIds[0] ? familyColor(row.familyIds[0]) + '66' : '#e5e7eb'}`}
                  title={row.familyIds.map((id) => familiesById.get(id)?.label ?? id).join(', ') || row.messageId}
                  on:click={() => {
                    const el = document.getElementById(`arg-msg-${row.messageId}`);
                    el?.scrollIntoView({ block: 'center', behavior: 'smooth' });
                  }}
                ></button>
              {/each}
            </div>
          </div>
        </Panel>

        <div class="flex flex-col gap-4">
          <Panel>
            <div class="flex items-center justify-between gap-3">
              <div>
                <div class="text-xs uppercase tracking-[0.28em] text-ink-800/70">Claim inspector</div>
                <div class="mt-1 text-sm text-ink-800/70">
                  {selectedClaimIds.length > 1 ? `${selectedClaimIds.length} claims selected` : currentClaim?.normalizedText ?? 'Select a claim'}
                </div>
              </div>
              <div class="flex flex-wrap gap-2">
                {#each ['Claim', 'Counterpoints', 'Graph'] as tab}
                  <button
                    type="button"
                    class={`rounded-lg px-3 py-2 text-xs uppercase tracking-widest ring-1 ${activeTab === tab ? 'bg-ink-900 text-paper-50 ring-ink-900' : 'bg-paper-100 ring-ink-900/10'}`}
                    on:click={() => (activeTab = tab as InspectorTab)}
                  >
                    {tab}
                  </button>
                {/each}
              </div>
            </div>
          </Panel>

          {#if activeTab === 'Claim'}
            <Panel>
              {#if currentClaim}
                <div class="text-xs uppercase tracking-[0.28em] text-ink-800/70">Normalized claim</div>
                <div class="mt-2 text-lg font-semibold text-ink-950">{currentClaim.normalizedText}</div>
                <div class="mt-2 flex flex-wrap gap-2 text-[11px]">
                  <span class="rounded-full border border-ink-900/10 bg-paper-100 px-2 py-1">{currentClaim.predicateKey}</span>
                  <span class="rounded-full border border-ink-900/10 bg-paper-100 px-2 py-1">{currentClaim.propositionKind}</span>
                  <span class="rounded-full border border-ink-900/10 bg-paper-100 px-2 py-1">{currentClaim.confidenceLabel}</span>
                  <span class="rounded-full border border-ink-900/10 bg-paper-100 px-2 py-1">{familiesById.get(currentClaim.familyId)?.label ?? currentClaim.familyId}</span>
                </div>
                <div class="mt-4 text-xs uppercase tracking-[0.24em] text-ink-800/60">Surface text</div>
                <div class="mt-1 rounded-lg bg-paper-100 p-3 text-sm text-ink-900">{currentClaim.surfaceText}</div>
                <div class="mt-4 text-xs uppercase tracking-[0.24em] text-ink-800/60">Arguments</div>
                <div class="mt-2 space-y-2">
                  {#each currentClaim.arguments as argument}
                    <div class="rounded-lg border border-ink-900/10 bg-paper-50 p-3 text-sm">
                      <div class="text-[11px] uppercase tracking-[0.24em] text-ink-800/60">{argument.role}</div>
                      <div class="mt-1">{argument.value}</div>
                    </div>
                  {/each}
                </div>
                <div class="mt-4 text-xs uppercase tracking-[0.24em] text-ink-800/60">Receipts</div>
                <div class="mt-2 flex flex-wrap gap-2">
                  {#each currentClaim.receipts as receipt}
                    <span class="rounded-full border border-ink-900/10 bg-paper-100 px-2 py-1 text-[11px]">{receipt.kind}: {receipt.value}</span>
                  {/each}
                </div>
                <div class="mt-4 flex flex-wrap gap-2">
                  <button
                    type="button"
                    class="rounded-lg bg-ink-900 px-3 py-2 text-xs uppercase tracking-widest text-paper-50"
                    on:click={() => (activeTab = 'Graph')}
                  >
                    Open graph focus
                  </button>
                  <button
                    type="button"
                    class="rounded-lg bg-paper-100 px-3 py-2 text-xs uppercase tracking-widest ring-1 ring-ink-900/10"
                    on:click={() => scrollClaimIntoView(currentClaim.id)}
                  >
                    Scroll transcript
                  </button>
                </div>
              {:else}
                <div class="text-sm text-ink-800/70">Select a claim from the transcript to inspect it.</div>
              {/if}
            </Panel>
          {:else if activeTab === 'Counterpoints'}
            <Panel>
              <div class="text-xs uppercase tracking-[0.28em] text-ink-800/70">Counterpoints</div>
              {#if selectedClaimIds.length > 1}
                <div class="mt-3 space-y-3">
                  {#each currentClaims as claim}
                    <div class="rounded-lg border border-ink-900/10 bg-paper-50 p-3">
                      <div class="font-medium text-ink-950">{claim?.normalizedText}</div>
                      <div class="mt-1 text-xs text-ink-800/70">{claim?.predicateKey} · {familiesById.get(claim?.familyId ?? '')?.label ?? claim?.familyId}</div>
                    </div>
                  {/each}
                </div>
              {/if}
              <div class="mt-3 space-y-3">
                {#each counterpoints as claim}
                  <button
                    type="button"
                    class="block w-full rounded-lg border border-ink-900/10 bg-paper-50 p-3 text-left"
                    on:click={() => selectClaim(claim.id)}
                  >
                    <div class="font-medium text-ink-950">{claim.normalizedText}</div>
                    <div class="mt-1 text-xs text-ink-800/70">{claim.predicateKey} · {familiesById.get(claim.familyId)?.label ?? claim.familyId}</div>
                  </button>
                {/each}
                {#if !counterpoints.length}
                  <div class="text-sm text-ink-800/70">No explicit counterpoints are currently linked for the selected claim set.</div>
                {/if}
              </div>
            </Panel>
          {:else}
            <Panel>
              <div class="text-xs uppercase tracking-[0.28em] text-ink-800/70">Graph</div>
              <div class="mt-2 text-sm text-ink-800/70">
                Scoped graph centered on the selected claim family. This stays local to the current thread instead of opening the full graph cold.
              </div>
              <div class="mt-4">
                <LayeredGraph
                  layers={graphPayload.layers}
                  edges={graphPayload.edges}
                  width={1400}
                  height={760}
                  fitToWidth={true}
                  scrollWhenOverflow={true}
                  viewportResetKey={graphViewportKey}
                />
              </div>
            </Panel>
          {/if}

          {#if hoveredClaimId && claimsById.get(hoveredClaimId)}
            {@const hovered = claimsById.get(hoveredClaimId)!}
            <Panel>
              <div class="text-xs uppercase tracking-[0.28em] text-ink-800/70">Hover preview</div>
              <div class="mt-2 text-sm font-medium text-ink-950">{hovered.normalizedText}</div>
              <div class="mt-1 text-xs text-ink-800/70">{hovered.predicateKey} · {familiesById.get(hovered.familyId)?.label ?? hovered.familyId}</div>
            </Panel>
          {/if}
        </div>
      </div>
    {/if}
  </Section>
</DashboardShell>
