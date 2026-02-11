import fs from 'node:fs/promises';
import path from 'node:path';

export type TimelineAnchor = {
  year: number;
  month: number | null;
  day: number | null;
  precision: 'year' | 'month' | 'day';
  text: string;
  kind: string;
};

export type TimelineEvent = {
  event_id: string;
  anchor: TimelineAnchor;
  section: string;
  text: string;
  links: string[];
};

export type WikiTimelinePayload = {
  snapshot: { title: string | null; wiki: string | null; revid: number | null; source_url: string | null };
  events: TimelineEvent[];
};

function isObj(v: unknown): v is Record<string, unknown> {
  return Boolean(v) && typeof v === 'object';
}

export async function loadWikiTimeline(repoRoot: string, relPath: string): Promise<WikiTimelinePayload> {
  const p = path.resolve(repoRoot, relPath);
  const raw = await fs.readFile(p, 'utf-8');
  const parsed = JSON.parse(raw) as any;
  const snapshot = isObj(parsed?.snapshot) ? parsed.snapshot : {};
  const events = Array.isArray(parsed?.events) ? (parsed.events as any[]) : [];

  const outEvents: TimelineEvent[] = [];
  for (const e of events) {
    if (!isObj(e)) continue;
    const event_id = String(e.event_id ?? '').trim();
    const text = String(e.text ?? '').trim();
    if (!event_id || !text) continue;
    const section = String(e.section ?? '').trim() || '(unknown)';
    const anchor = isObj(e.anchor) ? e.anchor : {};
    const a: TimelineAnchor = {
      year: Number((anchor as any).year ?? 0) || 0,
      month: Number.isFinite(Number((anchor as any).month)) ? Number((anchor as any).month) : null,
      day: Number.isFinite(Number((anchor as any).day)) ? Number((anchor as any).day) : null,
      precision: (anchor as any).precision === 'day' || (anchor as any).precision === 'month' ? (anchor as any).precision : 'year',
      text: String((anchor as any).text ?? ''),
      kind: String((anchor as any).kind ?? '')
    };
    const links = Array.isArray(e.links) ? e.links.map((x: any) => String(x)).filter(Boolean) : [];
    outEvents.push({ event_id, anchor: a, section, text, links });
  }

  // Sort by date (best-effort). Unknown year goes last.
  outEvents.sort((a, b) => {
    const ka = (a.anchor.year || 9999) * 10_000 + (a.anchor.month ?? 99) * 100 + (a.anchor.day ?? 99);
    const kb = (b.anchor.year || 9999) * 10_000 + (b.anchor.month ?? 99) * 100 + (b.anchor.day ?? 99);
    return ka - kb || a.event_id.localeCompare(b.event_id);
  });

  return {
    snapshot: {
      title: typeof snapshot.title === 'string' ? snapshot.title : null,
      wiki: typeof snapshot.wiki === 'string' ? snapshot.wiki : null,
      revid: Number.isFinite(Number(snapshot.revid)) ? Number(snapshot.revid) : null,
      source_url: typeof snapshot.source_url === 'string' ? snapshot.source_url : null
    },
    events: outEvents
  };
}

