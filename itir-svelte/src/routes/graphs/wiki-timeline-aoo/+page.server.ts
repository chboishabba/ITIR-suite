import path from 'node:path';
import { existsSync } from 'node:fs';

import { normalizeWikiTimelineSourceKey } from '$lib/server/wikiTimeline';
import { loadWikiTimelineAooSource } from '$lib/server/wikiTimelineAoo';
const VIEW_TYPES = new Set(['roles', 'step-ribbon']);

function resolveRepoRoot(): string {
  const candidates = [path.resolve('.'), path.resolve('..')];
  for (const c of candidates) {
    if (existsSync(path.join(c, 'SensibLaw'))) return c;
  }
  return path.resolve('..');
}

export async function load({ url }: { url: URL }) {
  const repoRoot = resolveRepoRoot();
  const source = normalizeWikiTimelineSourceKey(url.searchParams.get('source'), 'gwb');
  const rawView = (url.searchParams.get('view') || 'step-ribbon').toLowerCase();
  const view = VIEW_TYPES.has(rawView) ? rawView : 'step-ribbon';
  try {
    const loaded = await loadWikiTimelineAooSource(repoRoot, source, { variant: 'aoo' });
    return { payload: loaded.payload, relPath: loaded.relPath, source, view, error: null as string | null };
  } catch (e) {
    return {
      payload: { root_actor: { label: '', surname: '' }, events: [] },
      relPath: '',
      source,
      view,
      error: e instanceof Error ? e.message : String(e)
    };
  }
}
