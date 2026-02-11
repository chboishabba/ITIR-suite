import path from 'node:path';

import { loadWikiTimelineAoo } from '$lib/server/wikiTimelineAoo';

export async function load() {
  const repoRoot = path.resolve('..');
  const rel = path.join('SensibLaw', '.cache_local', 'wiki_timeline_gwb_aoo.json');
  try {
    const payload = await loadWikiTimelineAoo(repoRoot, rel);
    return { payload, relPath: rel, error: null as string | null };
  } catch (e) {
    return {
      payload: { root_actor: { label: '', surname: '' }, events: [] },
      relPath: rel,
      error: e instanceof Error ? e.message : String(e)
    };
  }
}

