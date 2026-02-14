import type { RequestHandler } from './$types';

import { getBuildMissingDashboardsJob } from '$lib/server/buildMissingDashboardsJob';

export const GET: RequestHandler = async ({ url }) => {
  const jobId = String(url.searchParams.get('jobId') ?? '').trim();
  if (!jobId) {
    return new Response(JSON.stringify({ ok: false, error: 'missing jobId' }), {
      status: 400,
      headers: { 'content-type': 'application/json' }
    });
  }
  const job = getBuildMissingDashboardsJob(jobId);
  if (!job) {
    return new Response(JSON.stringify({ ok: false, error: 'unknown jobId' }), {
      status: 404,
      headers: { 'content-type': 'application/json' }
    });
  }
  return new Response(JSON.stringify({ ok: true, job }), {
    headers: { 'content-type': 'application/json' }
  });
};

