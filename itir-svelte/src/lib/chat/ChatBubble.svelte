<script lang="ts">
  import type { ChatRole } from './types';
  import ToolCallBlock from './ToolCallBlock.svelte';
  import { parseToolCallText } from './parseToolCall';
  import MarkdownLite from '$lib/ui/MarkdownLite.svelte';

  export let role: ChatRole = 'other';
  export let ts: string | null = null;
  export let source: string | null = null;
  export let text: string = '';
  export let messageId: string | null = null;
  export let sourceMessageId: string | null = null;
  export let notebookSourceIndex: Record<string, number> | null = null;
  export let focused = false;
  export let collapsed = false;
  export let maxCollapsedChars = 600;

  const MAX_INLINE_TOOL_PARSE_CHARS = 50000;

  let expanded = false;
  let lastCollapsed = collapsed;

  $: isLong = text.length > maxCollapsedChars;
  $: if (!isLong) expanded = true;
  $: if (collapsed !== lastCollapsed) {
    // Global toggle should control the default, but allow per-message overrides afterwards.
    expanded = !collapsed;
    lastCollapsed = collapsed;
  }

  $: showText = collapsed && isLong && !expanded ? text.slice(0, maxCollapsedChars) + '\n…' : text;
  $: oversizedToolPayload = role === 'tool' && text.length > MAX_INLINE_TOOL_PARSE_CHARS;
  // Parse against the full text only when the payload is small enough to be safe.
  $: toolCall = oversizedToolPayload ? null : parseToolCallText(text);
  $: isEmptyText = !text || !text.trim();

  function shortTs(v: string | null): string {
    if (!v) return '';
    // 2026-02-10T06:28:45Z -> 06:28:45
    return v.length >= 19 ? v.slice(11, 19) : v;
  }

  const roleStyle: Record<ChatRole, { wrap: string; bubble: string; meta: string }> = {
    user: {
      wrap: 'justify-end',
      // Keep user bubbles close in lightness to assistant bubbles (easy reading),
      // but preserve a distinct hue/sat identity.
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
  data-source-message-id={sourceMessageId ?? undefined}
  data-ts={ts ? ts.slice(0, 19) : undefined}
  class={`flex ${roleStyle[role].wrap} ${focused ? 'scroll-mt-24' : ''}`}
>
  <div class="max-w-[48rem] w-full sm:w-auto">
    <div class={`rounded-2xl ring-1 shadow-crisp px-4 py-3 ${roleStyle[role].bubble} ${focused ? 'ring-2 ring-accent-600/70' : ''}`}>
      {#if toolCall}
        <ToolCallBlock
          tool={toolCall.tool}
          payload={toolCall.payload}
          rawJson={toolCall.rawJson}
          parseError={toolCall.parseError}
          notebookSourceIndex={notebookSourceIndex}
        />
      {:else if oversizedToolPayload}
        <div class="space-y-2">
          <div class="rounded-lg bg-amber-50 px-3 py-2 text-[11px] text-amber-950 ring-1 ring-amber-900/15">
            Oversized tool payload not parsed inline. Showing raw text preview to keep the thread viewer stable.
          </div>
          <pre class="max-h-[320px] overflow-auto overscroll-contain whitespace-pre-wrap break-words font-mono text-[12px] leading-relaxed text-ink-950">{showText}</pre>
          {#if collapsed && isLong}
            <div class="mt-2 flex items-center justify-end">
              <button
                type="button"
                class="rounded-md bg-paper-100 px-2 py-1 text-[10px] font-mono uppercase tracking-widest ring-1 ring-ink-900/10"
                on:click={() => (expanded = !expanded)}
                title={expanded ? 'Collapse this message' : 'Expand this message'}
              >
                {expanded ? 'Collapse' : 'Expand'}
              </button>
            </div>
          {/if}
        </div>
      {:else if isEmptyText}
        <div class="font-mono text-[12px] leading-relaxed text-ink-800/60 italic">
          (empty message)
        </div>
      {:else}
        <MarkdownLite text={showText} />
        {#if collapsed && isLong}
          <div class="mt-2 flex items-center justify-end">
            <button
              type="button"
              class="rounded-md bg-paper-100 px-2 py-1 text-[10px] font-mono uppercase tracking-widest ring-1 ring-ink-900/10"
              on:click={() => (expanded = !expanded)}
              title={expanded ? 'Collapse this message' : 'Expand this message'}
            >
              {expanded ? 'Collapse' : 'Expand'}
            </button>
          </div>
        {/if}
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
