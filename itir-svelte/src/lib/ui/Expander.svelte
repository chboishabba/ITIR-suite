<script lang="ts">
  import { onDestroy, onMount, tick } from 'svelte';

  export let title = '';
  export let open = false;
  export let collapsedHeight = 120; // px
  export let collapsedLabel = 'Expand';
  export let expandedLabel = 'Collapse';
  export let showFade = true;
  export let lazy = false; // mount body only after first open

  let mounted = false;
  let hasMountedContent = false;
  let wrapEl: HTMLDivElement | null = null;
  let contentEl: HTMLDivElement | null = null;
  let maxHeightCss = `${collapsedHeight}px`;
  let ro: ResizeObserver | null = null;
  const contentId = `expander_${Math.random().toString(36).slice(2)}`;

  function nextFrame(): Promise<void> {
    return new Promise((resolve) => requestAnimationFrame(() => resolve()));
  }

  function measureContentHeight(): number {
    if (!contentEl) return 0;
    return contentEl.scrollHeight;
  }

  async function animateOpen(): Promise<void> {
    await tick();
    const h = measureContentHeight();
    const folded = Math.max(0, Math.min(collapsedHeight, h));

    // Start from folded height.
    maxHeightCss = `${folded}px`;
    await nextFrame();

    // Animate to full height; on transition end we switch to 'none' for natural growth.
    maxHeightCss = `${h}px`;
  }

  async function animateClose(): Promise<void> {
    await tick();
    const h = measureContentHeight();
    const folded = Math.max(0, Math.min(collapsedHeight, h));

    // Ensure we have a numeric starting point even if we were 'none'.
    maxHeightCss = `${h}px`;
    await nextFrame();

    maxHeightCss = `${folded}px`;
  }

  function onTransitionEnd(e: TransitionEvent) {
    if (e.target !== wrapEl) return;
    if (!open) return;
    maxHeightCss = 'none';
  }

  function toggle(): void {
    open = !open;
  }

  $: if (open) hasMountedContent = true;

  $: if (mounted) {
    // Keep max-height in sync when collapsedHeight changes.
    if (!open && maxHeightCss === 'none') maxHeightCss = `${collapsedHeight}px`;
  }

  $: if (mounted) {
    if (open) void animateOpen();
    else void animateClose();
  }

  onMount(async () => {
    mounted = true;
    hasMountedContent = open;
    await tick();
    const h = measureContentHeight();
    maxHeightCss = open ? 'none' : `${Math.max(0, Math.min(collapsedHeight, h))}px`;

    if (typeof ResizeObserver !== 'undefined' && contentEl) {
      ro = new ResizeObserver(() => {
        // If open and max-height isn't 'none' yet (mid-transition), keep tracking height.
        if (open && maxHeightCss !== 'none') {
          maxHeightCss = `${measureContentHeight()}px`;
          return;
        }
        // If collapsed, keep the folded height correct even as content changes.
        if (!open) {
          maxHeightCss = `${Math.max(0, Math.min(collapsedHeight, measureContentHeight()))}px`;
        }
      });
      ro.observe(contentEl);
    }
  });

  $: if (mounted && typeof ResizeObserver !== 'undefined' && contentEl && !ro) {
    ro = new ResizeObserver(() => {
      if (open && maxHeightCss !== 'none') {
        maxHeightCss = `${measureContentHeight()}px`;
        return;
      }
      if (!open) {
        maxHeightCss = `${Math.max(0, Math.min(collapsedHeight, measureContentHeight()))}px`;
      }
    });
    ro.observe(contentEl);
  }

  onDestroy(() => ro?.disconnect());
</script>

<div class="rounded-xl bg-paper-50 ring-1 ring-ink-900/10">
  <div class="flex items-center justify-between gap-3 px-3 py-2">
    <div class="min-w-0">
      {#if title}
        <div class="text-[10px] font-mono uppercase tracking-widest text-ink-800/60 truncate">{title}</div>
      {/if}
      <slot name="header" />
    </div>
    <button
      type="button"
      class="shrink-0 rounded-md bg-paper-100 px-2 py-1 text-[10px] font-mono uppercase tracking-widest ring-1 ring-ink-900/10"
      aria-controls={contentId}
      aria-expanded={open}
      on:click={toggle}
    >
      <span class="inline-flex items-center gap-1">
        <span class={`inline-block transition-transform duration-200 ${open ? 'rotate-180' : ''}`}>v</span>
        {open ? expandedLabel : collapsedLabel}
      </span>
    </button>
  </div>

  <div class="relative">
    <div
      id={contentId}
      bind:this={wrapEl}
      class="overflow-hidden transition-[max-height] duration-300 ease-in-out"
      style={`max-height:${maxHeightCss}`}
      on:transitionend={onTransitionEnd}
    >
      {#if !lazy || open || hasMountedContent}
        <div bind:this={contentEl} class="px-3 pb-3">
          <slot />
        </div>
      {/if}
    </div>

    {#if showFade && !open}
      <div class="pointer-events-none absolute inset-x-0 bottom-0 h-10 bg-gradient-to-t from-paper-50 to-transparent"></div>
    {/if}
  </div>
</div>
