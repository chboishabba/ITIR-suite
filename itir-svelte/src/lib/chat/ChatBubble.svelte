<script lang="ts">
  import type { ChatRole } from './types';
  import ToolCallBlock from './ToolCallBlock.svelte';
  import { parseToolCallText } from './parseToolCall';

  export let role: ChatRole = 'other';
  export let ts: string | null = null;
  export let source: string | null = null;
  export let text: string = '';
  export let messageId: string | null = null;
  export let focused = false;
  export let collapsed = false;
  export let maxCollapsedChars = 600;

  $: isLong = text.length > maxCollapsedChars;
  $: showText = collapsed && isLong ? text.slice(0, maxCollapsedChars) + '\n…' : text;
  // Parse against the full text so "Collapse long" doesn't break structured tool rendering.
  $: toolCall = parseToolCallText(text);
  $: isEmptyText = !text || !text.trim();

  function shortTs(v: string | null): string {
    if (!v) return '';
    // 2026-02-10T06:28:45Z -> 06:28:45
    return v.length >= 19 ? v.slice(11, 19) : v;
  }

  const roleStyle: Record<ChatRole, { wrap: string; bubble: string; meta: string }> = {
    user: {
      wrap: 'justify-end',
      bubble: 'bg-gradient-to-br from-ink-900 to-ink-800 text-paper-50 ring-ink-900/10',
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
    other: {
      wrap: 'justify-start',
      bubble: 'bg-paper-100 text-ink-950 ring-ink-900/10',
      meta: 'text-ink-800/60'
    }
  };
</script>

<div
  id={messageId ? `msg_${messageId}` : undefined}
  data-message-id={messageId ?? undefined}
  data-ts={ts ? ts.slice(0, 19) : undefined}
  class={`flex ${roleStyle[role].wrap} ${focused ? 'scroll-mt-24' : ''}`}
>
  <div class="max-w-[48rem] w-full sm:w-auto">
    <div class={`rounded-2xl ring-1 shadow-crisp px-4 py-3 ${roleStyle[role].bubble} ${focused ? 'ring-2 ring-accent-600/70' : ''}`}>
      {#if toolCall}
        <ToolCallBlock tool={toolCall.tool} payload={toolCall.payload} rawJson={toolCall.rawJson} parseError={toolCall.parseError} />
      {:else if isEmptyText}
        <div class="font-mono text-[12px] leading-relaxed text-ink-800/60 italic">
          (empty message)
        </div>
      {:else}
        <pre class="whitespace-pre-wrap break-words font-mono text-[12px] leading-relaxed">{showText}</pre>
      {/if}
    </div>
    <div class={`mt-1 flex items-center justify-between gap-3 px-1 text-[11px] ${roleStyle[role].meta}`}>
      <div class="font-mono uppercase tracking-widest">{role}</div>
      <div class="font-mono truncate" title={source ?? ''}>
        {source ? source : ''}
      </div>
      <div class="font-mono" title={ts ?? ''}>{shortTs(ts)}</div>
    </div>
  </div>
</div>
