import path from 'node:path';

import { readStdout, resolveItirDbPath, resolveRepoRoot } from '$lib/server/utils';

type ParamTuple = [string, string];

function missionLensScriptPath(repoRoot: string): string {
  return path.join(repoRoot, 'SensibLaw', 'scripts', 'mission_lens.py');
}

function resolveSbRunsRoot(repoRoot: string): string {
  const fallback = path.join(repoRoot, 'StatiBaker', 'runs');
  const raw = process.env.SB_RUNS_ROOT?.trim() || fallback;
  return path.resolve(raw);
}

function resolveSbDbPath(repoRoot: string): string {
  const explicit = process.env.SB_DASHBOARD_DB?.trim();
  if (explicit) return path.resolve(explicit);
  return path.join(resolveSbRunsRoot(repoRoot), 'dashboard.sqlite');
}

function buildMissionLensArgs(repoRoot: string, action: string, params: ParamTuple[]): string[] {
  const args: string[] = [
    missionLensScriptPath(repoRoot),
    '--itir-db-path',
    resolveItirDbPath(repoRoot),
    '--sb-db-path',
    resolveSbDbPath(repoRoot),
    action
  ];
  for (const [key, value] of params) {
    args.push(key, value);
  }
  return args;
}

async function runMissionLens(action: string, params: ParamTuple[]): Promise<string> {
  const repoRoot = resolveRepoRoot();
  const args = buildMissionLensArgs(repoRoot, action, params);
  return await readStdout('python3', args, repoRoot);
}

export async function loadMissionLensReport(date: string, runId: string): Promise<{ report: unknown | null; error: string | null }> {
  try {
    const raw = await runMissionLens('report', [
      ['--date', date],
      ['--run-id', runId]
    ]);
    return { report: JSON.parse(raw), error: null };
  } catch (error) {
    return {
      report: null,
      error: error instanceof Error ? error.message : String(error)
    };
  }
}

export async function invokeMissionLensAction(action: string, params: ParamTuple[]): Promise<void> {
  await runMissionLens(action, params);
}
