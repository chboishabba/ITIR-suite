import path from 'node:path';
import { existsSync } from 'node:fs';

import { loadWikiTimelineAoo } from '$lib/server/wikiTimelineAoo';

const GWB_REL = path.join('SensibLaw', '.cache_local', 'wiki_timeline_gwb_aoo.json');
const GWB_PUBLIC_BIOS_REL = path.join(
  'SensibLaw',
  'demo',
  'ingest',
  'gwb',
  'public_bios_v1',
  'wiki_timeline_gwb_public_bios_v1_aoo.json'
);
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
const SOURCE_PATHS = {
  gwb: GWB_REL,
  gwb_public_bios_v1: GWB_PUBLIC_BIOS_REL,
  hca: HCA_REL,
  legal: LEGAL_REL,
  legal_follow: LEGAL_FOLLOW_REL
} as const;
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
  const source = (url.searchParams.get('source') || 'gwb').toLowerCase();
  const rawView = (url.searchParams.get('view') || 'step-ribbon').toLowerCase();
  const view = VIEW_TYPES.has(rawView) ? rawView : 'step-ribbon';
  const rel = SOURCE_PATHS[source as keyof typeof SOURCE_PATHS] ?? GWB_REL;
  try {
    const payload = await loadWikiTimelineAoo(repoRoot, rel);
    return { payload, relPath: rel, source, view, error: null as string | null };
  } catch (e) {
    return {
      payload: { root_actor: { label: '', surname: '' }, events: [] },
      relPath: rel,
      source,
      view,
      error: e instanceof Error ? e.message : String(e)
    };
  }
}
