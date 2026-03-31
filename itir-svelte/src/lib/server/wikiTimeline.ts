import path from 'node:path';
import { spawn } from 'node:child_process';

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

export type WikiTimelineSourceKey = 'gwb' | 'gwb_public_bios_v1' | 'gwb_corpus_v1' | 'hca' | 'legal' | 'legal_follow';

function isObj(v: unknown): v is Record<string, unknown> {
  return Boolean(v) && typeof v === 'object';
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

type SourceEnvelope = {
  source: WikiTimelineSourceKey;
  rel_path: string;
  timeline_suffix: string;
  payload: WikiTimelinePayload;
};

async function loadFromDb(repoRoot: string, sourceKey: WikiTimelineSourceKey, dbEnv: string | null): Promise<SourceEnvelope> {
  const script = path.join(repoRoot, 'SensibLaw', 'scripts', 'query_wiki_timeline_aoo_db.py');
  const args = [script, '--source-key', sourceKey, '--projection', 'timeline_view', '--with-source-meta'];
  if (dbEnv && dbEnv.trim()) {
    args.splice(1, 0, '--db-path', dbEnv.trim());
  }
  const stdout = await readStdout('python', args, repoRoot);
  const parsed = JSON.parse(stdout);
  if (!parsed) {
    throw new Error(`No DB payload found for source ${sourceKey}`);
  }
  if (!isObj(parsed)) throw new Error('DB payload missing');
  return parsed as SourceEnvelope;
}

export function normalizeWikiTimelineSourceKey(rawSource: string | null | undefined, fallback: WikiTimelineSourceKey = 'gwb'): WikiTimelineSourceKey {
  const normalized = String(rawSource ?? fallback).trim().toLowerCase() as WikiTimelineSourceKey;
  if (
    normalized === 'gwb' ||
    normalized === 'gwb_public_bios_v1' ||
    normalized === 'gwb_corpus_v1' ||
    normalized === 'hca' ||
    normalized === 'legal' ||
    normalized === 'legal_follow'
  ) {
    return normalized;
  }
  return fallback;
}

export async function loadWikiTimelineDb(repoRoot: string, opts: { dbEnv?: string | null; sourceKey: WikiTimelineSourceKey }) {
  const dbEnv = opts?.dbEnv ?? process.env.ITIR_DB_PATH ?? process.env.SL_WIKI_TIMELINE_DB ?? process.env.SL_WIKI_TIMELINE_AOO_DB ?? null;
  if (!opts?.sourceKey) {
    throw new Error('sourceKey is required for DB loader');
  }
  return loadFromDb(repoRoot, opts.sourceKey, dbEnv);
}

export async function loadWikiTimelineSourceDb(
  repoRoot: string,
  rawSource: string | null | undefined,
  opts?: { dbEnv?: string | null; fallback?: WikiTimelineSourceKey }
): Promise<{ source: WikiTimelineSourceKey; relPath: string; timelineSuffix: string; payload: WikiTimelinePayload }> {
  const sourceKey = normalizeWikiTimelineSourceKey(rawSource, opts?.fallback ?? 'gwb');
  const loaded = await loadWikiTimelineDb(repoRoot, {
    dbEnv: opts?.dbEnv ?? null,
    sourceKey
  });
  return {
    source: loaded.source,
    relPath: loaded.rel_path,
    timelineSuffix: loaded.timeline_suffix,
    payload: loaded.payload
  };
}
