import fs from 'node:fs/promises';
import path from 'node:path';
import { spawn } from 'node:child_process';
import { gatherWikiDbCandidates } from '$lib/server/runtime/pathCandidates';

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

let warnedLegacyTimelineDbEnv = false;
const LEGACY_DB_VARS = new Set(['SL_WIKI_TIMELINE_DB', 'SL_WIKI_TIMELINE_AOO_DB']);

function resolveItirDbPath(repoRoot: string, explicitDbEnv?: string | null): string {
  const candidates = gatherWikiDbCandidates(repoRoot, explicitDbEnv);
  const selected = candidates[0];
  if (!selected) {
    return path.resolve(repoRoot, '.cache_local', 'itir.sqlite');
  }
  if (
    !warnedLegacyTimelineDbEnv &&
    selected.provenance.type === 'env' &&
    LEGACY_DB_VARS.has(selected.provenance.envVar)
  ) {
    warnedLegacyTimelineDbEnv = true;
    console.warn('SL_WIKI_TIMELINE_DB / SL_WIKI_TIMELINE_AOO_DB is deprecated; use ITIR_DB_PATH.');
  }
  return selected.path;
}

async function readStdout(cmd: string, args: string[], cwd: string): Promise<string> {
  return await new Promise<string>((resolve, reject) => {
    const child = spawn(cmd, args, { cwd });
    let stdout = '';
    let stderr = '';
    child.stdout.on('data', (d) => (stdout += d.toString()));
    child.stderr.on('data', (d) => (stderr += d.toString()));
    child.on('close', (code) => {
      if (code !== 0) {
        reject(new Error(`${cmd} ${args.join(' ')} failed with ${code}\n${stderr || stdout}`));
      } else {
        resolve(stdout);
      }
    });
  });
}

async function loadFromDb(repoRoot: string, timelineSuffix: string, dbEnv: string | null): Promise<WikiTimelinePayload> {
  const dbPath = resolveItirDbPath(repoRoot, dbEnv);
  const script = path.join(repoRoot, 'SensibLaw', 'scripts', 'query_wiki_timeline_aoo_db.py');
  const stdout = await readStdout('python', [script, '--db-path', dbPath, '--timeline-path-suffix', timelineSuffix], repoRoot);
  const parsed = JSON.parse(stdout);
  if (!parsed) {
    throw new Error(`No DB payload found for suffix ${timelineSuffix} in ${dbPath}`);
  }
  if (!isObj(parsed)) throw new Error('DB payload missing');
  const payload = parsed as any;
  const snapshot = isObj(payload?.snapshot) ? payload.snapshot : {};
  const events = Array.isArray(payload?.events) ? (payload.events as any[]) : [];

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

export async function loadWikiTimelineDb(repoRoot: string, opts: { dbEnv?: string | null; timelineSuffix: string }) {
  const dbEnv = opts?.dbEnv ?? process.env.ITIR_DB_PATH ?? process.env.SL_WIKI_TIMELINE_DB ?? process.env.SL_WIKI_TIMELINE_AOO_DB ?? null;
  if (!opts?.timelineSuffix) {
    throw new Error('timelineSuffix is required for DB loader');
  }
  return loadFromDb(repoRoot, opts.timelineSuffix, dbEnv);
}
