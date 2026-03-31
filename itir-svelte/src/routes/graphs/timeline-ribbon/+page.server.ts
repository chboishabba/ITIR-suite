import path from 'node:path';
import { spawn } from 'node:child_process';

import { parseDashboardPayload } from '$lib/sb-dashboard/contracts/parse';
import type { DashboardPayload } from '$lib/sb-dashboard/contracts/dashboard';

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

async function listAvailableDates(repoRoot: string, runsRoot: string, dbPath: string): Promise<string[]> {
  try {
    const raw = await runPythonJson(repoRoot, ['--db-path', dbPath, '--view', 'daily', '--list-dates', '--runs-root', runsRoot]);
    if (Array.isArray(raw)) return raw.filter((value) => typeof value === 'string' && isDateText(value)).sort();
  } catch {
    return [];
  }
  return [];
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

  let projected: any = null;
  try {
    projected = await runPythonJson(repoRoot, [
      '--db-path',
      dbPath,
      '--view',
      'daily',
      '--start',
      start,
      '--end',
      end,
      '--prefer-all',
      '--projection',
      'timeline_ribbon',
      '--runs-root',
      runsRoot
    ]);
  } catch {
    projected = null;
  }

  if (!projected?.payload) {
    return {
      availableDates,
      selected: { start, end },
      payload: { date: end, period_start: start, period_end: end, timeline: [] } as DashboardPayload,
      source: '',
      error: 'No dashboard payload could be loaded for the selected range.'
    };
  }

  return {
    availableDates,
    selected: { start, end },
    payload: parseDashboardPayload(projected.payload as Record<string, unknown>),
    source: String(projected?.source ?? ''),
    error: null as string | null
  };
}
