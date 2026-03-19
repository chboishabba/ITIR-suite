<script lang="ts">
  import { afterUpdate, createEventDispatcher } from 'svelte';
  import type { TranscriptCue } from './transcript';
  import { cuesFromTranscriptText, findActiveCueIndex, formatTimecode } from './transcript';

  type TranscriptCueSelectEvent = {
    cue: TranscriptCue;
    index: number;
    timeSec: number;
  };

  export let title = 'Transcript';
  export let cues: TranscriptCue[] = [];
  export let transcriptText = '';
  export let audioSrc: string | null = null;
  export let showAudio = true;
  export let showSearch = true;
  export let maxHeightPx = 520;

  const dispatch = createEventDispatcher<{ cueSelect: TranscriptCueSelectEvent }>();

  let query = '';
  let currentTimeSec = 0;
  let manualTimeSec = 0;
  let lastActiveKey = '';
  let audioEl: HTMLAudioElement | null = null;
  let cueListEl: HTMLDivElement | null = null;

  const cueEls = new Map<string, HTMLElement>();

  $: derivedCues = cues.length ? cues : cuesFromTranscriptText(transcriptText);
  $: durationSec = derivedCues.length ? Math.max(...derivedCues.map((c) => c.endSec)) : 0;
  $: effectiveTimeSec = audioSrc ? currentTimeSec : manualTimeSec;
  $: activeCueIndex = findActiveCueIndex(derivedCues, effectiveTimeSec);
  $: activeCue = activeCueIndex >= 0 && activeCueIndex < derivedCues.length ? derivedCues[activeCueIndex] : null;
  $: activeCueAnnouncement = activeCue
    ? `[${activeCue.startLabel} -> ${activeCue.endLabel}] ${activeCue.text}`
    : 'No active transcript cue.';
  $: filteredCues = (() => {
    const q = query.trim().toLowerCase();
    if (!q) return derivedCues;
    return derivedCues.filter((cue) => {
      const hay = `${cue.startLabel} ${cue.endLabel} ${cue.text}`.toLowerCase();
      return hay.includes(q);
    });
  })();

  function registerCueEl(id: string, el: HTMLElement | null): void {
    if (!id) return;
    if (!el) {
      cueEls.delete(id);
      return;
    }
    cueEls.set(id, el);
  }

  function trackCue(node: HTMLElement, cueId: string) {
    registerCueEl(cueId, node);
    return {
      update(nextId: string) {
        if (nextId !== cueId) {
          registerCueEl(cueId, null);
          cueId = nextId;
          registerCueEl(cueId, node);
        }
      },
      destroy() {
        registerCueEl(cueId, null);
      }
    };
  }

  function onAudioTimeUpdate(): void {
    if (!audioEl) return;
    currentTimeSec = Number(audioEl.currentTime || 0);
  }

  function seekTo(timeSec: number): void {
    if (!Number.isFinite(timeSec) || timeSec < 0) return;
    if (audioEl) {
      audioEl.currentTime = timeSec;
      currentTimeSec = timeSec;
    } else {
      manualTimeSec = timeSec;
    }
  }

  function onCueSelect(cue: TranscriptCue, index: number): void {
    seekTo(cue.startSec);
    dispatch('cueSelect', { cue, index, timeSec: cue.startSec });
  }

  afterUpdate(() => {
    if (!cueListEl || activeCueIndex < 0 || activeCueIndex >= derivedCues.length) return;
    const cue = derivedCues[activeCueIndex];
    if (!cue) return;
    const key = `${cue.id}:${activeCueIndex}`;
    if (key === lastActiveKey) return;
    lastActiveKey = key;
    const el = cueEls.get(cue.id);
    if (!el) return;
    el.scrollIntoView({ block: 'nearest' });
  });
</script>

<div class="rounded-2xl bg-paper-50 shadow-crisp ring-1 ring-ink-900/10" role="region" aria-label={title}>
  <div class="flex items-center justify-between gap-3 border-b border-ink-900/10 px-4 py-3">
    <div class="font-display text-sm tracking-tight text-ink-950">{title}</div>
    <div class="font-mono text-[10px] text-ink-800/70">
      cues={derivedCues.length}
      {#if showSearch && query.trim()} matches={filteredCues.length}{/if}
      time={formatTimecode(effectiveTimeSec)}
    </div>
  </div>

  {#if showAudio}
    <div class="border-b border-ink-900/10 px-4 py-3">
      {#if audioSrc}
        <audio bind:this={audioEl} class="w-full" controls src={audioSrc} on:timeupdate={onAudioTimeUpdate}></audio>
      {:else}
        <div class="space-y-2">
          <div class="text-xs text-ink-800/70">
            No audio source attached. Use manual time scrub to inspect cue sync behavior.
          </div>
          <label class="sr-only">Manual transcript scrub (seconds)</label>
          <input
            type="range"
            class="w-full"
            min="0"
            max={Math.max(1, Math.ceil(durationSec))}
            step="0.1"
            bind:value={manualTimeSec}
            aria-label="Manual transcript scrub (seconds)"
          />
        </div>
      {/if}
    </div>
  {/if}

  {#if showSearch}
    <div class="border-b border-ink-900/10 px-4 py-2">
      <label class="sr-only">Search transcript text</label>
      <input
        class="w-full rounded-lg bg-paper-100 px-3 py-2 text-sm ring-1 ring-ink-900/10"
        bind:value={query}
        placeholder="Search transcript..."
        aria-label="Search transcript cues"
      />
    </div>
  {/if}

  <div class="sr-only" role="status" aria-live="polite" aria-atomic="true">
    {activeCueAnnouncement}
  </div>

  <div class="overflow-auto px-2 py-2" bind:this={cueListEl} style={`max-height:${Math.max(200, Math.floor(maxHeightPx))}px`}>
    {#if !filteredCues.length}
      <div class="px-3 py-2 text-xs text-ink-800/70">No cues match the current filter.</div>
    {:else}
      <div class="space-y-1">
        {#each filteredCues as cue, idx (cue.id)}
          {@const globalIdx = derivedCues.findIndex((c) => c.id === cue.id)}
          <button
            type="button"
            aria-label={`Select cue ${cue.startLabel} to ${cue.endLabel}`}
            aria-pressed={globalIdx === activeCueIndex}
            class={`w-full rounded-md px-3 py-2 text-left ring-1 ring-ink-900/10 hover:bg-ink-950/[0.03] ${
              globalIdx === activeCueIndex ? 'bg-amber-50 ring-amber-300/60' : 'bg-white'
            }`}
            on:click={() => onCueSelect(cue, globalIdx >= 0 ? globalIdx : idx)}
            use:trackCue={cue.id}
          >
            <div class="font-mono text-[10px] text-ink-800/70">
              [{cue.startLabel} -> {cue.endLabel}]
            </div>
            <div class="mt-1 whitespace-pre-wrap break-words text-sm text-ink-950">{cue.text}</div>
          </button>
        {/each}
      </div>
    {/if}
  </div>
</div>
