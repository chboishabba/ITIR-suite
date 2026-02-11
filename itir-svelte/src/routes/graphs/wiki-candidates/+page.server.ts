import path from 'node:path';

import { loadWikiCandidates } from '$lib/server/wikiCandidates';

export async function load() {
  // SvelteKit dev server runs with cwd at `itir-svelte/`; repo root is parent.
  const repoRoot = path.resolve('..');
  const rel = path.join('SensibLaw', '.cache_local', 'wiki_candidates_gwb.json');
  try {
    const payload = await loadWikiCandidates(repoRoot, rel);
    return { payload, relPath: rel, error: null as string | null };
  } catch (e) {
    return {
      payload: { pages: [], candidates: [] },
      relPath: rel,
      error: e instanceof Error ? e.message : String(e)
    };
  }
}
