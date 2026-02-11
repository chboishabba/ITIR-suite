import fs from 'node:fs/promises';
import path from 'node:path';

export type AooActor = {
  label: string;
  resolved: string;
  role: string;
  source: string;
};

export type AooObject = {
  title: string;
  source: string;
};

export type AooEvent = {
  event_id: string;
  anchor: { year: number; month: number | null; day: number | null; precision: string; text: string; kind: string };
  section: string;
  text: string;
  actors: AooActor[];
  action: string | null;
  objects: AooObject[];
  purpose: string | null;
  warnings: string[];
};

export type WikiTimelineAooPayload = {
  root_actor: { label: string; surname: string };
  events: AooEvent[];
};

function isObj(v: unknown): v is Record<string, unknown> {
  return Boolean(v) && typeof v === 'object';
}

export async function loadWikiTimelineAoo(repoRoot: string, relPath: string): Promise<WikiTimelineAooPayload> {
  const p = path.resolve(repoRoot, relPath);
  const raw = await fs.readFile(p, 'utf-8');
  const parsed = JSON.parse(raw) as any;
  const events = Array.isArray(parsed?.events) ? (parsed.events as any[]) : [];
  const root_actor = isObj(parsed?.root_actor) ? parsed.root_actor : { label: '', surname: '' };

  const outEvents: AooEvent[] = [];
  for (const e of events) {
    if (!isObj(e)) continue;
    const event_id = String(e.event_id ?? '').trim();
    const text = String(e.text ?? '').trim();
    if (!event_id || !text) continue;
    const anchor = isObj(e.anchor) ? e.anchor : {};
    const actors = Array.isArray(e.actors) ? (e.actors as any[]) : [];
    const objects = Array.isArray(e.objects) ? (e.objects as any[]) : [];
    outEvents.push({
      event_id,
      anchor: {
        year: Number((anchor as any).year ?? 0) || 0,
        month: Number.isFinite(Number((anchor as any).month)) ? Number((anchor as any).month) : null,
        day: Number.isFinite(Number((anchor as any).day)) ? Number((anchor as any).day) : null,
        precision: String((anchor as any).precision ?? 'year'),
        text: String((anchor as any).text ?? ''),
        kind: String((anchor as any).kind ?? '')
      },
      section: String(e.section ?? ''),
      text,
      actors: actors
        .filter((a) => isObj(a) && typeof (a as any).resolved === 'string')
        .map((a) => ({
          label: String((a as any).label ?? ''),
          resolved: String((a as any).resolved ?? ''),
          role: String((a as any).role ?? ''),
          source: String((a as any).source ?? '')
        })),
      action: typeof e.action === 'string' ? e.action : null,
      objects: objects
        .filter((o) => isObj(o) && typeof (o as any).title === 'string')
        .map((o) => ({ title: String((o as any).title ?? ''), source: String((o as any).source ?? '') })),
      purpose: typeof e.purpose === 'string' ? e.purpose : null,
      warnings: Array.isArray(e.warnings) ? e.warnings.map((x: any) => String(x)) : []
    });
  }

  outEvents.sort((a, b) => {
    const ka = (a.anchor.year || 9999) * 10_000 + (a.anchor.month ?? 99) * 100 + (a.anchor.day ?? 99);
    const kb = (b.anchor.year || 9999) * 10_000 + (b.anchor.month ?? 99) * 100 + (b.anchor.day ?? 99);
    return ka - kb || a.event_id.localeCompare(b.event_id);
  });

  return {
    root_actor: {
      label: typeof (root_actor as any).label === 'string' ? (root_actor as any).label : '',
      surname: typeof (root_actor as any).surname === 'string' ? (root_actor as any).surname : ''
    },
    events: outEvents
  };
}
