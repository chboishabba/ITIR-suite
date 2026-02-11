<script lang="ts">
  import Expander from '$lib/ui/Expander.svelte';

  export let tool = 'tool_call';
  export let payload: Record<string, unknown> | null = null;
  export let rawJson: string | null = null;
  export let parseError: string | null = null;

  let copied = '';

  type Tone = 'neutral' | 'warn' | 'danger' | 'teal' | 'indigo';

  function badgeClass(tone: 'neutral' | 'warn' | 'danger'): string {
    if (tone === 'danger') return 'bg-red-600/10 text-red-900 ring-red-900/20';
    if (tone === 'warn') return 'bg-amber-500/10 text-amber-950 ring-amber-900/20';
    return 'bg-paper-100 text-ink-900/80 ring-ink-900/10';
  }

  function toolTone(t: string): Tone {
    const s = (t ?? '').toLowerCase().trim();
    if (s === 'exec_command') return 'teal';
    if (s === 'write_stdin') return 'indigo';
    if (s === 'update_plan') return 'warn';
    if (s === 'apply_patch') return 'danger';
    return 'neutral';
  }

  function toneBadge(tone: Tone): string {
    if (tone === 'teal') return 'bg-teal-600/10 text-teal-950 ring-teal-900/20';
    if (tone === 'indigo') return 'bg-indigo-600/10 text-indigo-950 ring-indigo-900/20';
    if (tone === 'danger') return badgeClass('danger');
    if (tone === 'warn') return badgeClass('warn');
    return badgeClass('neutral');
  }

  function getString(v: unknown): string {
    return typeof v === 'string' ? v : '';
  }

  function cmdText(): string {
    const c = payload ? payload['cmd'] : null;
    return typeof c === 'string' ? c : '';
  }

  function getNum(v: unknown): number | null {
    return typeof v === 'number' && Number.isFinite(v) ? v : null;
  }

  function getBool(v: unknown): boolean | null {
    return typeof v === 'boolean' ? v : null;
  }

  function isEmptyString(v: unknown): boolean {
    return typeof v === 'string' && v.length === 0;
  }

  function shortText(v: string, max = 140): string {
    const s = v.replace(/\s+/g, ' ').trim();
    if (s.length <= max) return s;
    return s.slice(0, max - 1) + '…';
  }

  function planItems(): Array<{ step: string; status: string }> {
    const p = payload?.plan;
    if (!Array.isArray(p)) return [];
    const out: Array<{ step: string; status: string }> = [];
    for (const it of p) {
      if (!it || typeof it !== 'object' || Array.isArray(it)) continue;
      const rec = it as Record<string, unknown>;
      const step = typeof rec.step === 'string' ? rec.step : '';
      const status = typeof rec.status === 'string' ? rec.status : '';
      if (!step && !status) continue;
      out.push({ step, status });
    }
    return out;
  }

  function statusPill(status: string): { cls: string; label: string } {
    const s = (status ?? '').toLowerCase().trim();
    if (s === 'completed' || s === 'done')
      return { cls: 'bg-emerald-600/10 text-emerald-950 ring-emerald-900/20', label: 'completed' };
    if (s === 'in_progress')
      return { cls: 'bg-sky-600/10 text-sky-950 ring-sky-900/20', label: 'in_progress' };
    if (s === 'pending' || !s) return { cls: 'bg-paper-100 text-ink-900/80 ring-ink-900/10', label: s || 'pending' };
    return { cls: 'bg-paper-100 text-ink-900/80 ring-ink-900/10', label: s };
  }

  async function copyText(label: string, text: string): Promise<void> {
    if (!text.trim()) return;
    try {
      await navigator.clipboard.writeText(text);
      copied = label;
      window.setTimeout(() => (copied = ''), 900);
    } catch {
      // ignore
    }
  }

  $: tone = toolTone(tool);
  $: cmd = cmdText();
  $: justification = getString(payload?.justification);
  $: prefixRule = Array.isArray(payload?.prefix_rule) ? payload?.prefix_rule : null;
  $: sandboxPerm = getString(payload?.sandbox_permissions);
  $: workdir = getString(payload?.workdir);
  $: tty = getBool(payload?.tty);
  $: sessionId = getNum(payload?.session_id);
  $: chars = typeof payload?.chars === 'string' ? (payload?.chars as string) : null;
  $: yieldMs = getNum(payload?.yield_time_ms);
  $: maxOut = getNum(payload?.max_output_tokens);
  $: explanation = getString(payload?.explanation);
  $: plan = planItems();
</script>

<div class="space-y-2">
  <div class="flex flex-wrap items-center justify-between gap-2">
    <div class="flex items-center gap-2">
      <div class="font-mono text-xs text-ink-900/80">
        <span class="inline-block rounded-md bg-paper-100 px-2 py-1 ring-1 ring-ink-900/10">>_</span>
        <span class={`ml-2 inline-flex items-center rounded-full px-2 py-1 text-[10px] font-mono uppercase tracking-widest ring-1 ${toneBadge(tone)}`}>
          {tool}
        </span>
      </div>
    </div>
    <div class="flex flex-wrap items-center gap-2">
      {#if sandboxPerm === 'require_escalated'}
        <span class={`rounded-full px-2 py-1 text-[10px] font-mono uppercase tracking-widest ring-1 ${badgeClass('danger')}`}>escalated</span>
      {/if}
      {#if justification}
        <span class={`rounded-full px-2 py-1 text-[10px] font-mono uppercase tracking-widest ring-1 ${badgeClass('warn')}`}>justification</span>
      {/if}
      {#if prefixRule}
        <span class={`rounded-full px-2 py-1 text-[10px] font-mono uppercase tracking-widest ring-1 ${badgeClass('neutral')}`}>prefix rule</span>
      {/if}
    </div>
  </div>

  {#if tool === 'exec_command' && cmd}
    <div class="rounded-xl bg-paper-50 ring-1 ring-ink-900/10">
      <div class="flex items-center justify-between gap-3 px-3 py-2">
        <div class="text-[10px] font-mono uppercase tracking-widest text-ink-800/60">cmd</div>
        <button
          type="button"
          class="rounded-md bg-paper-100 px-2 py-1 text-[10px] font-mono uppercase tracking-widest ring-1 ring-ink-900/10"
          on:click={() => copyText('cmd', cmd)}
        >
          {copied === 'cmd' ? 'copied' : 'copy'}
        </button>
      </div>
      <pre class="max-h-[220px] overflow-auto overscroll-contain whitespace-pre-wrap break-words font-mono text-[12px] leading-relaxed px-3 pb-3">{cmd}</pre>
      {#if workdir || tty !== null || yieldMs !== null || maxOut !== null}
        <div class="border-t border-ink-900/10 px-3 py-2 text-[11px] text-ink-800/70">
          <div class="flex flex-wrap items-center gap-x-4 gap-y-1 font-mono">
            {#if workdir}<span>workdir={workdir}</span>{/if}
            {#if tty !== null}<span>tty={tty ? 'true' : 'false'}</span>{/if}
            {#if yieldMs !== null}<span>yield_ms={yieldMs}</span>{/if}
            {#if maxOut !== null}<span>max_output_tokens={maxOut}</span>{/if}
          </div>
        </div>
      {/if}
    </div>
  {/if}

  {#if tool === 'write_stdin'}
    <div class="rounded-xl bg-paper-50 ring-1 ring-ink-900/10 px-3 py-2">
      <div class="text-[10px] font-mono uppercase tracking-widest text-ink-800/60">stdin</div>
      <div class="mt-1 flex flex-wrap items-center gap-x-4 gap-y-1 font-mono text-[11px] text-ink-800/70">
        {#if sessionId !== null}<span>session_id={sessionId}</span>{/if}
        {#if yieldMs !== null}<span>yield_ms={yieldMs}</span>{/if}
        {#if maxOut !== null}<span>max_output_tokens={maxOut}</span>{/if}
        {#if chars !== null}
          <span>
            chars=
            {#if isEmptyString(chars)}
              (empty)
            {:else}
              {chars.length}
            {/if}
          </span>
        {/if}
      </div>
      {#if chars && chars.trim()}
        <pre class="mt-2 whitespace-pre-wrap break-words font-mono text-[12px] leading-relaxed text-ink-900/80">{shortText(chars, 500)}</pre>
      {/if}
    </div>
  {/if}

  {#if tool === 'update_plan'}
    <div class="rounded-xl bg-paper-50 ring-1 ring-ink-900/10 px-3 py-2">
      <div class="flex flex-wrap items-center justify-between gap-2">
        <div class="text-[10px] font-mono uppercase tracking-widest text-ink-800/60">plan</div>
        <div class="text-[11px] font-mono text-ink-800/60">{plan.length.toLocaleString()} item(s)</div>
      </div>
      {#if explanation}
        <div class="mt-2 text-[12px] text-ink-900/80 whitespace-pre-wrap">{explanation}</div>
      {/if}
      {#if plan.length}
        <div class="mt-2 space-y-2">
          {#each plan as p, idx (idx)}
            {@const pill = statusPill(p.status)}
            <div class="flex items-start gap-2">
              <span class={`mt-[2px] inline-flex items-center rounded-full px-2 py-[2px] text-[10px] font-mono uppercase tracking-widest ring-1 ${pill.cls}`}>{pill.label}</span>
              <div class="min-w-0 text-[12px] text-ink-950/90 leading-snug">{p.step}</div>
            </div>
          {/each}
        </div>
      {:else}
        <div class="mt-2 text-[12px] text-ink-800/60">No plan items found in payload.</div>
      {/if}
    </div>
  {/if}

  {#if justification}
    <div class="rounded-xl bg-amber-500/10 ring-1 ring-amber-900/20 px-3 py-2 text-[12px] text-amber-950">
      <div class="text-[10px] font-mono uppercase tracking-widest text-amber-950/70">justification</div>
      <div class="mt-1 whitespace-pre-wrap">{justification}</div>
    </div>
  {/if}

  {#if prefixRule}
    <div class="rounded-xl bg-paper-50 ring-1 ring-ink-900/10 px-3 py-2">
      <div class="text-[10px] font-mono uppercase tracking-widest text-ink-800/60">prefix_rule</div>
      <pre class="mt-1 whitespace-pre-wrap break-words font-mono text-[12px] leading-relaxed">{JSON.stringify(prefixRule, null, 2)}</pre>
    </div>
  {/if}

  <Expander title="raw payload" collapsedHeight={0} collapsedLabel="Show" expandedLabel="Hide" showFade={false}>
    {#if parseError}
      <div class="text-[11px] text-red-900/80">parse error: {parseError}</div>
    {/if}
    <div class="mt-2 flex items-center justify-between gap-3">
      <div class="text-[10px] font-mono uppercase tracking-widest text-ink-800/40">json</div>
      <button
        type="button"
        class="rounded-md bg-paper-100 px-2 py-1 text-[10px] font-mono uppercase tracking-widest ring-1 ring-ink-900/10"
        on:click={() => copyText('json', rawJson ?? '')}
      >
        {copied === 'json' ? 'copied' : 'copy'}
      </button>
    </div>
    <pre class="mt-2 max-h-[260px] overflow-auto overscroll-contain whitespace-pre-wrap break-words font-mono text-[11px] leading-relaxed text-ink-900/80">{rawJson ?? ''}</pre>
  </Expander>
</div>
