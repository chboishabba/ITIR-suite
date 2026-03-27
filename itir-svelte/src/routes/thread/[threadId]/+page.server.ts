import { error } from '@sveltejs/kit';
import { fetchThreadTail, fetchThreadTailBySourceThreadId } from '$lib/server/chatArchive';
import {
  fetchNotebookMetaThreadTail,
  isNotebookMetaThreadId,
  type NotebookMetaSummary,
  type NotebookMetaSourceRow
} from '$lib/server/notebookMeta';
import path from 'node:path';

const MAX_TOOL_THREAD_TEXT_CHARS = 40000;
const MAX_GENERIC_THREAD_TEXT_CHARS = 120000;

function isDateText(v: string): boolean {
  return /^\d{4}-\d{2}-\d{2}$/.test(v);
}

function looksLikeOnlineConversationId(v: string): boolean {
  // ChatGPT conversation UUID style.
  return /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(v);
}

function truncateThreadMessageText(role: string, text: string): string {
  const value = typeof text === 'string' ? text : '';
  if (!value) return value;
  const limit = role === 'tool' ? MAX_TOOL_THREAD_TEXT_CHARS : MAX_GENERIC_THREAD_TEXT_CHARS;
  if (value.length <= limit) return value;
  const omitted = value.length - limit;
  return `${value.slice(0, limit)}\n\n[truncated ${omitted.toLocaleString()} chars for thread viewer stability]`;
}

export async function load({ params, url }: { params: { threadId: string }; url: URL }) {
  const threadId = params.threadId;
  if (!threadId || threadId.length < 8) throw error(400, 'Invalid thread id.');
  const notebookMetaThread = isNotebookMetaThreadId(threadId);

  const start = url.searchParams.get('start');
  const end = url.searchParams.get('end');
  const tailParam = url.searchParams.get('tail');
  const tailCap = notebookMetaThread ? 400 : 2000;
  const tailDefault = notebookMetaThread ? 200 : 400;
  const tailMin = notebookMetaThread ? 20 : 50;
  const tail = Math.max(tailMin, Math.min(tailCap, Number(tailParam ?? tailDefault) || tailDefault));

  // SvelteKit dev server runs with cwd at `itir-svelte/`; repo root is parent.
  const repoRoot = path.resolve('..');

  const startIso = start && isDateText(start) ? start : null;
  const endIso = end && isDateText(end) ? end : null;

  // `threadId` can be:
  // - canonical_thread_id (sha1 hex)
  // - online/source conversation UUID (when archive captured upstream IDs)
  let canonicalThreadId = threadId;
  let title: string | null = null;
  let total = 0;
  let messages: any[] = [];
  let notebookMetaSummary: NotebookMetaSummary | null = null;
  let notebookMetaSources: NotebookMetaSourceRow[] | null = null;

  if (notebookMetaThread) {
    const r = await fetchNotebookMetaThreadTail(threadId, {
      startDate: startIso,
      endDate: endIso,
      tail,
      runsRootEnv: process.env.SB_RUNS_ROOT
    });
    canonicalThreadId = threadId;
    title = r.title;
    total = r.total;
    messages = r.messages;
    notebookMetaSummary = r.summary;
    notebookMetaSources = r.sources;
  } else if (looksLikeOnlineConversationId(threadId)) {
    const mapped = await fetchThreadTailBySourceThreadId(repoRoot, threadId, { startIso, endIso, tail });
    canonicalThreadId = mapped.canonicalThreadId ?? threadId;
    title = mapped.title;
    total = mapped.total;
    messages = mapped.messages;
  } else {
    const r = await fetchThreadTail(repoRoot, threadId, { startIso, endIso, tail });
    title = r.title;
    total = r.total;
    messages = r.messages;
  }

  return {
    threadId: canonicalThreadId,
    title,
    total,
    tail,
    range: { start: start && isDateText(start) ? start : null, end: end && isDateText(end) ? end : null },
    messages: messages.map((message) => ({
      ...message,
      text: truncateThreadMessageText(String(message?.role ?? ''), String(message?.text ?? ''))
    })),
    notebookMetaSummary,
    notebookMetaSources
  };
}
