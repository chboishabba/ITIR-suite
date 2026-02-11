import path from 'node:path';

import { loadWikiTimelineAoo } from '$lib/server/wikiTimelineAoo';

const GWB_REL = path.join('SensibLaw', '.cache_local', 'wiki_timeline_gwb_aoo.json');
const HCA_REL = path.join('SensibLaw', '.cache_local', 'wiki_timeline_hca_s942025_aoo.json');
const LEGAL_REL = path.join(
  'SensibLaw',
  'demo',
  'ingest',
  'legal_principles_au_v1',
  'wiki_timeline_legal_principles_au_v1_aoo.json'
);
const LEGAL_FOLLOW_REL = path.join(
  'SensibLaw',
  'demo',
  'ingest',
  'legal_principles_au_v1',
  'follow',
  'wiki_timeline_legal_principles_au_v1_follow_aoo.json'
);
const SOURCE_PATHS = { gwb: GWB_REL, hca: HCA_REL, legal: LEGAL_REL, legal_follow: LEGAL_FOLLOW_REL } as const;

export async function load({ url }: { url: URL }) {
  const repoRoot = path.resolve('..');
  const source = (url.searchParams.get('source') || 'gwb').toLowerCase();
  const rel = SOURCE_PATHS[source as keyof typeof SOURCE_PATHS] ?? GWB_REL;
  try {
    const payload = await loadWikiTimelineAoo(repoRoot, rel);
    return { payload, relPath: rel, source, error: null as string | null };
  } catch (e) {
    return {
      payload: { root_actor: { label: '', surname: '' }, events: [] },
      relPath: rel,
      source,
      error: e instanceof Error ? e.message : String(e)
    };
  }
}
