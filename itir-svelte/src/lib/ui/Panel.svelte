<script lang="ts">
  type PanelTone = 'neutral' | 'info' | 'warn' | 'danger' | 'success';

  export let tone: PanelTone = 'neutral';
  export let padded = true;

  const toneClass: Record<PanelTone, string> = {
    neutral: 'bg-paper-50 ring-ink-900/10 text-ink-950',
    info: 'bg-paper-50 ring-blue-700/25 text-ink-950',
    warn: 'bg-paper-50 ring-amber-700/25 text-ink-950',
    danger: 'bg-paper-50 ring-red-700/30 text-ink-950',
    success: 'bg-paper-50 ring-emerald-700/25 text-ink-950'
  };

  $: cls = `rounded-2xl shadow-crisp ring-1 ${toneClass[tone] ?? toneClass.neutral} ${padded ? 'px-5 py-4' : ''}`;
</script>

<div class={cls}>
  <slot />
</div>
