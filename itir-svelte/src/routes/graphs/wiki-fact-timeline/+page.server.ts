import path from 'node:path';

import { loadWikiTimelineAoo, type AooTimelineFact } from '$lib/server/wikiTimelineAoo';

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

type FactRow = {
  fact_id: string;
  event_id: string;
  anchor: { year: number; month: number | null; day: number | null; precision: string; text: string; kind: string };
  party: string;
  subjects: string[];
  action: string | null;
  objects: string[];
  purpose: string | null;
  text: string;
  section: string;
};

function keyForAnchor(a: { year: number; month: number | null; day: number | null }): number {
  return (a.year || 9999) * 10_000 + (a.month ?? 99) * 100 + (a.day ?? 99);
}

function coerceFactRow(raw: AooTimelineFact, sectionByEvent: Map<string, string>, textByEvent: Map<string, string>): FactRow {
  return {
    fact_id: String(raw.fact_id || ''),
    event_id: String(raw.event_id || ''),
    anchor: {
      year: Number(raw.anchor?.year ?? 0) || 0,
      month: Number.isFinite(Number(raw.anchor?.month)) ? Number(raw.anchor?.month) : null,
      day: Number.isFinite(Number(raw.anchor?.day)) ? Number(raw.anchor?.day) : null,
      precision: String(raw.anchor?.precision ?? 'year'),
      text: String(raw.anchor?.text ?? ''),
      kind: String(raw.anchor?.kind ?? '')
    },
    party: String(raw.party ?? ''),
    subjects: Array.isArray(raw.subjects) ? raw.subjects.map((x) => String(x)).filter(Boolean) : [],
    action: typeof raw.action === 'string' ? raw.action : null,
    objects: Array.isArray(raw.objects) ? raw.objects.map((x) => String(x)).filter(Boolean) : [],
    purpose: typeof raw.purpose === 'string' ? raw.purpose : null,
    text: String(raw.text ?? textByEvent.get(String(raw.event_id || '')) ?? ''),
    section: String(sectionByEvent.get(String(raw.event_id || '')) ?? '')
  };
}

export async function load({ url }: { url: URL }) {
  const repoRoot = path.resolve('..');
  const source = (url.searchParams.get('source') || 'hca').toLowerCase();
  const rel = SOURCE_PATHS[source as keyof typeof SOURCE_PATHS] ?? HCA_REL;
  try {
    const payload = await loadWikiTimelineAoo(repoRoot, rel);
    const sectionByEvent = new Map(payload.events.map((e) => [e.event_id, e.section || '']));
    const textByEvent = new Map(payload.events.map((e) => [e.event_id, e.text || '']));

    const rawFacts: AooTimelineFact[] =
      Array.isArray(payload.fact_timeline) && payload.fact_timeline.length
        ? payload.fact_timeline
        : payload.events.flatMap((e) => Array.isArray(e.timeline_facts) ? e.timeline_facts : []);

    const facts = rawFacts
      .map((f) => coerceFactRow(f, sectionByEvent, textByEvent))
      .filter((f) => Boolean(f.fact_id) && Boolean(f.text))
      .sort((a, b) => keyForAnchor(a.anchor) - keyForAnchor(b.anchor) || a.fact_id.localeCompare(b.fact_id));

    return {
      payload: {
        root_actor: payload.root_actor,
        parser: payload.parser ?? null,
        facts
      },
      relPath: rel,
      source,
      error: null as string | null
    };
  } catch (e) {
    return {
      payload: { root_actor: { label: '', surname: '' }, parser: null, facts: [] as FactRow[] },
      relPath: rel,
      source,
      error: e instanceof Error ? e.message : String(e)
    };
  }
}

