<script lang="ts">
  import type { DashboardPayload } from '../contracts/dashboard';

  export let payload: DashboardPayload;

  const maybe = payload as unknown as { period_start?: string; period_end?: string; days?: number };
</script>

<div class="rounded-2xl bg-paper-50 shadow-crisp ring-1 ring-ink-900/10 px-5 py-4">
  <div class="flex flex-wrap items-end justify-between gap-4">
    <div>
      <div class="text-xs uppercase tracking-[0.28em] text-ink-800/60">StatiBaker Dashboard</div>
      <div class="mt-2 font-display text-3xl tracking-tight text-ink-950">{payload.date}</div>
      {#if maybe.period_start && maybe.period_end && maybe.period_start !== maybe.period_end}
        <div class="mt-1 text-sm text-ink-800/70">
          Period: <span class="font-mono text-xs">{maybe.period_start}</span> .. <span class="font-mono text-xs">{maybe.period_end}</span>
          {#if typeof maybe.days === 'number'}
            <span class="ml-2 font-mono text-xs text-ink-800/60">({maybe.days}d)</span>
          {/if}
        </div>
      {/if}
      {#if payload.generated_at}
        <div class="mt-2 text-sm text-ink-800/70">Generated: <span class="font-mono text-xs">{payload.generated_at}</span></div>
      {/if}
    </div>

    <div class="grid grid-cols-2 gap-x-6 gap-y-2 text-sm">
      <div class="text-ink-800/70">Chat scope</div>
      <div class="font-mono text-xs text-ink-950">{payload.chat_scope_mode ?? 'unknown'}</div>
      <div class="text-ink-800/70">Threads</div>
      <div class="font-mono text-xs text-ink-950">{payload.chat_scope_thread_count ?? 'n/a'}</div>
    </div>
  </div>

  {#if payload.warnings && payload.warnings.length}
    <div class="mt-4 rounded-xl bg-paper-100 ring-1 ring-ink-900/10 px-4 py-3">
      <div class="text-xs uppercase tracking-widest text-ink-800/60">Warnings</div>
      <ul class="mt-2 list-disc pl-5 text-sm text-ink-900/80">
        {#each payload.warnings as w}
          <li>{w}</li>
        {/each}
      </ul>
    </div>
  {/if}
</div>
