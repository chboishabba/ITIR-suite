import type { RequestHandler } from './$types';
import path from 'node:path';

import { startBuildMissingDashboardsJob } from '$lib/server/buildMissingDashboardsJob';

function resolveRunsRoot(runsRootEnv: string | undefined): string {
  const fallback = path.resolve('..', 'StatiBaker', 'runs');
  const raw = runsRootEnv && runsRootEnv.trim() ? runsRootEnv.trim() : fallback;
  return path.resolve(raw);
}

function isDateText(v: string): boolean {
  return /^\d{4}-\d{2}-\d{2}$/.test(v);
}

export const POST: RequestHandler = async ({ request }) => {
  const body = await request.json().catch(() => null);
  const start = String(body?.start ?? '').trim();
  const end = String(body?.end ?? '').trim();
  if (!isDateText(start) || !isDateText(end)) {
    return new Response(JSON.stringify({ ok: false, error: 'invalid start/end' }), {
      status: 400,
      headers: { 'content-type': 'application/json' }
    });
  }

  const runsRoot = resolveRunsRoot(process.env.SB_RUNS_ROOT);
  const { jobId } = startBuildMissingDashboardsJob({ runsRoot, start, end });

  return new Response(JSON.stringify({ ok: true, jobId }), {
    headers: { 'content-type': 'application/json' }
  });
};

