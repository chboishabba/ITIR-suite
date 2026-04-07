import fs from 'node:fs/promises';
import path from 'node:path';
import { spawn } from 'node:child_process';
import { parseDashboardPayload } from '../../sb-dashboard/contracts/parse.ts';
import type { DashboardArtifactLink, DashboardPayload } from '../../sb-dashboard/contracts/dashboard.ts';

export type NotebookMetaRow = {
  threadId: string;
  title: string;
  messageCount: number;
  origin: string;
  sources: string[];
  metaOnly: boolean;
  firstTs?: string;
  lastTs?: string;
};

export function resolveRepoRoot(): string {
  return path.resolve('..');
}

export function resolveRunsRoot(envValue?: string): string {
  const fallback = path.join(resolveRepoRoot(), 'StatiBaker', 'runs');
  const raw = envValue && envValue.trim() ? envValue.trim() : fallback;
  return path.resolve(raw);
}

export function resolveSbDbPath(envValue?: string, runsRoot?: string): string {
  const explicit = envValue && envValue.trim();
  if (explicit) return path.resolve(explicit);
  const root = runsRoot ?? resolveRunsRoot();
  return path.join(root, 'dashboard.sqlite');
}

export async function tryReadJson(filePath: string): Promise<unknown | null> {
  try {
    const raw = await fs.readFile(filePath, 'utf-8');
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

export async function fileExists(filePath: string): Promise<boolean> {
  try {
    await fs.stat(filePath);
    return true;
  } catch {
    return false;
  }
}

export function shortHash(value: string): string {
  const clean = value.replace(/^sha256:/i, '').trim();
  if (!clean) return '';
  return clean.length > 12 ? `${clean.slice(0, 12)}...` : clean;
}

export function minIso(a?: string, b?: string): string | undefined {
  if (!a) return b;
  if (!b) return a;
  return b < a ? b : a;
}

export function maxIso(a?: string, b?: string): string | undefined {
  if (!a) return b;
  if (!b) return a;
  return b > a ? b : a;
}

export function dateRangeInclusive(start: string, end: string): string[] {
  const out: string[] = [];
  if (start > end) [start, end] = [end, start];
  const [sy, sm, sd] = start.split('-').map((x) => Number(x)) as [number, number, number];
  const [ey, em, ed] = end.split('-').map((x) => Number(x)) as [number, number, number];
  if (![sy, sm, sd, ey, em, ed].every((n) => Number.isFinite(n))) return [];
  const from = new Date(Date.UTC(sy, sm - 1, sd));
  const to = new Date(Date.UTC(ey, em - 1, ed));
  for (let d = from; d <= to; d = new Date(d.getTime() + 86400_000)) {
    out.push(d.toISOString().slice(0, 10));
  }
  return out;
}

export async function runPythonJson(repoRoot: string, args: string[]): Promise<unknown> {
  return new Promise((resolve, reject) => {
    const child = spawn('python3', args, { cwd: repoRoot, stdio: ['ignore', 'pipe', 'pipe'] });
    let stdout = '';
    let stderr = '';
    child.stdout.on('data', (d) => (stdout += String(d)));
    child.stderr.on('data', (d) => (stderr += String(d)));
    child.on('error', (err) => reject(err));
    child.on('close', (code) => {
      if (code !== 0) return reject(new Error(`Python command failed (exit ${code}).\n${stderr || stdout}`));
      try {
        resolve(JSON.parse(stdout));
      } catch (err) {
        reject(new Error(`Python command returned non-JSON output.\n${stderr || ''}\n${stdout.slice(0, 2000)}`));
      }
    });
  });
}

export async function listAvailableDates(runsRoot: string, repoRoot: string, dbPath: string): Promise<string[]> {
  if (await fileExists(dbPath)) {
    try {
      const raw = await runPythonJson(repoRoot, ['--db-path', dbPath, '--view', 'daily', '--list-dates']);
      if (Array.isArray(raw)) return raw.filter((d) => typeof d === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(d)).sort();
    } catch {
      // fall through to legacy disk scan
    }
  }

  try {
    const entries = await fs.readdir(runsRoot, { withFileTypes: true });
    const dates = entries
      .filter((entry) => entry.isDirectory() && /^\d{4}-\d{2}-\d{2}$/.test(entry.name))
      .map((entry) => entry.name)
      .sort();
    const out: string[] = [];
    for (const date of dates) {
      const p = path.join(runsRoot, date, 'outputs', 'dashboard.json');
      const pAll = path.join(runsRoot, date, 'outputs', 'dashboard_all.json');
      const raw = (await tryReadJson(p)) ?? (await tryReadJson(pAll));
      if (raw) out.push(date);
    }
    return out;
  } catch {
    return [];
  }
}

export async function loadDashboardForDate(
  repoRoot: string,
  runsRoot: string,
  dbPath: string,
  date: string
): Promise<{ payload: DashboardPayload; source: string } | null> {
  if (await fileExists(dbPath)) {
    try {
      const raw = await runPythonJson(repoRoot, ['--db-path', dbPath, '--view', 'daily', '--date', date, '--prefer-all']);
      const tuple = raw as any;
      const payloadRaw = tuple?.payload ?? null;
      if (payloadRaw) {
        return {
          payload: parseDashboardPayload(payloadRaw),
          source: `${dbPath}#daily:${date}:${String(tuple?.scope ?? '')}`
        };
      }
    } catch {
      // fall through to disk reads
    }
  }

  const pAll = path.join(runsRoot, date, 'outputs', 'dashboard_all.json');
  const p = path.join(runsRoot, date, 'outputs', 'dashboard.json');
  const rawAll = await tryReadJson(pAll);
  if (rawAll) return { payload: parseDashboardPayload(rawAll), source: pAll };
  const raw = await tryReadJson(p);
  if (raw) return { payload: parseDashboardPayload(raw), source: p };
  return null;
}

export async function loadNotebookMetaRowsForDate(runsRoot: string, date: string): Promise<NotebookMetaRow[]> {
  const file = path.join(runsRoot, date, 'logs', 'notes', `${date}.jsonl`);
  let raw = '';
  try {
    raw = await fs.readFile(file, 'utf-8');
  } catch {
    return [];
  }

  const byId = new Map<string, NotebookMetaRow>();
  for (const line of raw.split(/\r?\n/g)) {
    const text = line.trim();
    if (!text) continue;
    let record: any;
    try {
      record = JSON.parse(text);
    } catch {
      continue;
    }

    if (String(record?.signal ?? '').trim().toLowerCase() !== 'notes_meta') continue;
    if (String(record?.app ?? '').trim().toLowerCase() !== 'notebooklm') continue;

    const notebookHash = String(record?.notebook_id_hash ?? '').trim();
    const isScoped = Boolean(notebookHash);
    const id = isScoped ? `meta:notebooklm:${notebookHash}` : 'meta:notebooklm:unscoped';
    const title = isScoped ? `NotebookLM ${shortHash(notebookHash)}` : 'NotebookLM (unscoped metadata)';
    const ts = String(record?.ts ?? '').trim() || undefined;

    const current =
      byId.get(id) ?? {
        threadId: id,
        title,
        messageCount: 0,
        origin: 'notebooklm',
        sources: ['notebooklm (meta-only)'],
        metaOnly: true
      };

    current.messageCount += 1;
    current.firstTs = minIso(current.firstTs, ts);
    current.lastTs = maxIso(current.lastTs, ts);
    byId.set(id, current);
  }

  return [...byId.values()].sort((a, b) => b.messageCount - a.messageCount || a.title.localeCompare(b.title));
}

export async function addArtifactMtimes(links: DashboardArtifactLink[] | undefined): Promise<DashboardArtifactLink[] | undefined> {
  if (!links || !links.length) return links;
  const MAX = 200;
  const slice = links.slice(0, MAX);
  const out: DashboardArtifactLink[] = await Promise.all(
    slice.map(async (link) => {
      try {
        const st = await fs.stat(link.path);
        const iso = st.mtime.toISOString();
        const hour = Number(iso.slice(11, 13));
        return { ...link, mtime_iso: iso, mtime_hour: Number.isFinite(hour) ? hour : undefined };
      } catch {
        return link;
      }
    })
  );
  return links.length > MAX ? [...out, ...links.slice(MAX)] : out;
}

export function autoBuildMissingEnabled(envValue?: string): boolean {
  const raw = envValue?.trim().toLowerCase();
  if (!raw) return true;
  return !['0', 'false', 'no', 'off', 'disable', 'disabled'].includes(raw);
}
