import fs from 'node:fs/promises';
import path from 'node:path';
import { spawn } from 'node:child_process';

import { parseDashboardPayload } from '$lib/sb-dashboard/contracts/parse';
import type { DashboardPayload, DashboardTimelineEvent } from '$lib/sb-dashboard/contracts/dashboard';

function isDateText(value: string): boolean {
  return /^\d{4}-\d{2}-\d{2}$/.test(value);
}

function resolveRunsRoot(): string {
  const fallback = path.resolve('..', 'StatiBaker', 'runs');
  const raw = process.env.SB_RUNS_ROOT?.trim() || fallback;
  return path.resolve(raw);
}

function resolveDbPath(runsRoot: string): string {
  const explicit = process.env.SB_DASHBOARD_DB?.trim();
  if (explicit) return path.resolve(explicit);
  return path.join(runsRoot, 'dashboard.sqlite');
}

async function tryReadJson(filePath: string): Promise<unknown | null> {
  try {
    const raw = await fs.readFile(filePath, 'utf-8');
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

async function fileExists(filePath: string): Promise<boolean> {
  try {
    await fs.stat(filePath);
    return true;
  } catch {
    return false;
  }
}

async function runPythonJson(repoRoot: string, args: string[]): Promise<unknown> {
  return await new Promise((resolve, reject) => {
    const script = path.join(repoRoot, 'StatiBaker', 'scripts', 'query_dashboard_db.py');
    const child = spawn('python3', [script, ...args], { cwd: repoRoot, stdio: ['ignore', 'pipe', 'pipe'] });
    let stdout = '';
    let stderr = '';
    child.stdout.on('data', (chunk) => (stdout += String(chunk)));
    child.stderr.on('data', (chunk) => (stderr += String(chunk)));
    child.on('error', (error) => reject(error));
    child.on('close', (code) => {
      if (code !== 0) return reject(new Error(`query_dashboard_db.py failed (${code})\n${stderr || stdout}`));
      try {
        resolve(JSON.parse(stdout));
      } catch {
        reject(new Error(`query_dashboard_db.py returned non-JSON output\n${stderr || stdout}`));
      }
    });
  });
}

function dateRangeInclusive(start: string, end: string): string[] {
  const out: string[] = [];
  if (start > end) [start, end] = [end, start];
  const startParts = start.split('-').map((x) => Number(x));
  const endParts = end.split('-').map((x) => Number(x));
  if (startParts.length !== 3 || endParts.length !== 3) return [];
  const [sy, sm, sd] = startParts as [number, number, number];
  const [ey, em, ed] = endParts as [number, number, number];
  if (![sy, sm, sd, ey, em, ed].every((value) => Number.isFinite(value))) return [];
  const startDate = new Date(Date.UTC(sy, sm - 1, sd));
  const endDate = new Date(Date.UTC(ey, em - 1, ed));
  for (let current = startDate; current <= endDate; current = new Date(current.getTime() + 86_400_000)) {
    out.push(current.toISOString().slice(0, 10));
  }
  return out;
}

async function listAvailableDates(repoRoot: string, runsRoot: string, dbPath: string): Promise<string[]> {
  if (await fileExists(dbPath)) {
    try {
      const raw = await runPythonJson(repoRoot, ['--db-path', dbPath, '--view', 'daily', '--list-dates']);
      if (Array.isArray(raw)) return raw.filter((value) => typeof value === 'string' && isDateText(value)).sort();
    } catch {
      // fall through to disk scan
    }
  }
  try {
    const entries = await fs.readdir(runsRoot, { withFileTypes: true });
    return entries
      .filter((entry) => entry.isDirectory() && isDateText(entry.name))
      .map((entry) => entry.name)
      .sort();
  } catch {
    return [];
  }
}

async function loadDashboardForDate(repoRoot: string, runsRoot: string, dbPath: string, date: string): Promise<{ payload: DashboardPayload; source: string } | null> {
  if (await fileExists(dbPath)) {
    try {
      const raw = await runPythonJson(repoRoot, ['--db-path', dbPath, '--view', 'daily', '--date', date, '--prefer-all']);
      const tuple = raw as any;
      if (tuple?.payload) {
        return {
          payload: parseDashboardPayload(tuple.payload),
          source: `${dbPath}#daily:${date}:${String(tuple?.scope ?? '')}`
        };
      }
    } catch {
      // fall back to JSON
    }
  }

  const fullPath = path.join(runsRoot, date, 'outputs', 'dashboard_all.json');
  const scopedPath = path.join(runsRoot, date, 'outputs', 'dashboard.json');
  const full = await tryReadJson(fullPath);
  if (full) return { payload: parseDashboardPayload(full), source: fullPath };
  const scoped = await tryReadJson(scopedPath);
  if (scoped) return { payload: parseDashboardPayload(scoped), source: scopedPath };
  return null;
}

function buildTimelinePayload(dailies: DashboardPayload[], start: string, end: string): DashboardPayload {
  const timeline: DashboardTimelineEvent[] = [];
  for (const payload of dailies) {
    for (const event of payload.timeline ?? []) timeline.push(event);
  }
  timeline.sort((a, b) => String(a.ts).localeCompare(String(b.ts)));
  return {
    date: end,
    period_start: start,
    period_end: end,
    days: dailies.length,
    timeline
  };
}

export async function load({ url }: { url: URL }) {
  const repoRoot = path.resolve('..');
  const runsRoot = resolveRunsRoot();
  const dbPath = resolveDbPath(runsRoot);
  const availableDates = await listAvailableDates(repoRoot, runsRoot, dbPath);
  const fallbackDate = availableDates.at(-1) || process.env.SB_DATE || new Date().toISOString().slice(0, 10);
  const start = url.searchParams.get('start') || url.searchParams.get('date') || fallbackDate;
  const end = url.searchParams.get('end') || start;

  if (!isDateText(start) || !isDateText(end)) {
    return {
      availableDates,
      selected: { start, end },
      payload: { date: fallbackDate, timeline: [] } as DashboardPayload,
      source: '',
      error: 'Invalid date parameters.'
    };
  }

  const dates = dateRangeInclusive(start, end);
  const loaded: Array<{ payload: DashboardPayload; source: string }> = [];
  for (const date of dates) {
    const result = await loadDashboardForDate(repoRoot, runsRoot, dbPath, date);
    if (result) loaded.push(result);
  }

  if (!loaded.length) {
    return {
      availableDates,
      selected: { start, end },
      payload: { date: end, period_start: start, period_end: end, timeline: [] } as DashboardPayload,
      source: '',
      error: 'No dashboard payload could be loaded for the selected range.'
    };
  }

  const payload = loaded.length === 1 && start === end ? loaded[0]!.payload : buildTimelinePayload(loaded.map((row) => row.payload), start, end);
  const source =
    loaded.length === 1 && start === end
      ? loaded[0]!.source
      : `${loaded.length} payloads merged from ${start} to ${end}`;

  return {
    availableDates,
    selected: { start, end },
    payload,
    source,
    error: null as string | null
  };
}
