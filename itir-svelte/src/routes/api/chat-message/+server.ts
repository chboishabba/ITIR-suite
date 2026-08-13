import { json, error } from '@sveltejs/kit';
import path from 'node:path';
import { fetchLastMessageInRange, fetchMessageAtTs } from '$lib/server/chatArchive';

function isIsoTs(v: string): boolean {
  // Minimal sanity check: 2026-02-06T08:15:36Z
  return /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/.test(v);
}

function isIsoTsLoose(v: string): boolean {
  // Accept `...Z` and `...+00:00` (archive format), second precision.
  return /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(Z|\+\d{2}:\d{2})$/.test(v);
}

export async function GET({ url }: { url: URL }) {
  const threadId = (url.searchParams.get('threadId') ?? '').trim();
  const ts = (url.searchParams.get('ts') ?? '').trim();
  const startTs = (url.searchParams.get('startTs') ?? '').trim();
  const endTs = (url.searchParams.get('endTs') ?? '').trim();
  if (!threadId || threadId.length < 8) throw error(400, 'Invalid threadId.');

  // SvelteKit dev server runs with cwd at `itir-svelte/`; repo root is parent.
  const repoRoot = path.resolve('..');

  let m = null;
  if (startTs || endTs) {
    if ((startTs && !isIsoTsLoose(startTs)) || (endTs && !isIsoTsLoose(endTs))) throw error(400, 'Invalid startTs/endTs.');
    m = await fetchLastMessageInRange(
      repoRoot,
      threadId,
      { startTs: startTs || null, endTs: endTs || null },
      { preferNonEmpty: true }
    );
  } else {
    if (!isIsoTs(ts)) throw error(400, 'Invalid ts.');
    m = await fetchMessageAtTs(repoRoot, threadId, ts);
  }
  if (!m) return json({ message: null });

  return json({
    message: {
      message_id: m.message_id,
      source_message_id: m.source_message_id,
      ts: m.ts,
      role: m.role,
      text: m.text
    }
  });
}
