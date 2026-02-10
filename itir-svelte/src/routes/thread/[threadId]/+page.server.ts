import { error } from '@sveltejs/kit';
import { fetchThreadTail } from '$lib/server/chatArchive';
import path from 'node:path';

function isDateText(v: string): boolean {
  return /^\d{4}-\d{2}-\d{2}$/.test(v);
}

export async function load({ params, url }: { params: { threadId: string }; url: URL }) {
  const threadId = params.threadId;
  if (!threadId || threadId.length < 8) throw error(400, 'Invalid thread id.');

  const start = url.searchParams.get('start');
  const end = url.searchParams.get('end');
  const tailParam = url.searchParams.get('tail');
  const tail = Math.max(50, Math.min(2000, Number(tailParam ?? 400) || 400));

  // SvelteKit dev server runs with cwd at `itir-svelte/`; repo root is parent.
  const repoRoot = path.resolve('..');

  const { title, total, messages } = await fetchThreadTail(repoRoot, threadId, {
    startIso: start && isDateText(start) ? start : null,
    endIso: end && isDateText(end) ? end : null,
    tail
  });

  return {
    threadId,
    title,
    total,
    tail,
    range: { start: start && isDateText(start) ? start : null, end: end && isDateText(end) ? end : null },
    messages
  };
}
