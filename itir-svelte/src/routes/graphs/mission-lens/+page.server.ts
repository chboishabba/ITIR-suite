import { fail, redirect } from '@sveltejs/kit';

import { loadMissionLensReport, invokeMissionLensAction } from '$lib/server/mission-lens';

function trimmed(form: FormData, key: string): string {
  return String(form.get(key) ?? '').trim();
}

function trimmedOrDefault(form: FormData, key: string, fallback: string): string {
  const value = trimmed(form, key);
  return value || fallback;
}

function redirectWithUpdated(url: URL, date: string, runId: string): never {
  const next = new URL(url);
  next.searchParams.set('date', date);
  next.searchParams.set('runId', runId);
  next.searchParams.set('updated', '1');
  throw redirect(303, next.toString());
}

export async function load({ url }: { url: URL }) {
  const date = url.searchParams.get('date') || process.env.SB_DATE || new Date().toISOString().slice(0, 10);
  const runId = url.searchParams.get('runId') || '';
  const { report, error } = await loadMissionLensReport(date, runId);
  return { date, runId, report, error };
}

export const actions = {
  addPlanNode: async ({ request, url }: { request: Request; url: URL }) => {
    const form = await request.formData();
    const runId = trimmed(form, 'runId');
    const date = trimmed(form, 'date');
    const title = trimmed(form, 'title');
    if (!runId || !date || !title) {
      return fail(400, { ok: false, error: 'Missing required mission-plan fields.' });
    }
    await invokeMissionLensAction('add-node', [
      ['--run-id', runId],
      ['--date', date],
      ['--title', title],
      ['--node-kind', trimmedOrDefault(form, 'nodeKind', 'task')],
      ['--status', trimmedOrDefault(form, 'status', 'active')],
      ['--source-kind', trimmedOrDefault(form, 'sourceKind', 'manual')],
      ['--parent-plan-node-id', trimmed(form, 'parentPlanNodeId')],
      ['--target-weight', trimmedOrDefault(form, 'targetWeight', '1')],
      ['--raw-deadline', trimmed(form, 'rawDeadline')],
      ['--due-start', trimmed(form, 'dueStart')],
      ['--due-end', trimmed(form, 'dueEnd')],
      ['--certainty-kind', trimmed(form, 'certaintyKind')],
      ['--urgency-level', trimmed(form, 'urgencyLevel')],
      ['--flexibility-level', trimmed(form, 'flexibilityLevel')]
    ]);
    redirectWithUpdated(url, date, runId);
  },
  addActualMapping: async ({ request, url }: { request: Request; url: URL }) => {
    const form = await request.formData();
    const runId = trimmed(form, 'runId');
    const date = trimmed(form, 'date');
    const planNodeId = trimmed(form, 'planNodeId');
    const activityRefId = trimmed(form, 'activityRefId');
    if (!runId || !date || !planNodeId || !activityRefId) {
      return fail(400, { ok: false, error: 'Missing required mapping fields.' });
    }
    await invokeMissionLensAction('add-mapping', [
      ['--run-id', runId],
      ['--date', date],
      ['--activity-ref-id', activityRefId],
      ['--plan-node-id', planNodeId],
      ['--mapping-kind', 'reviewed_link'],
      ['--status', 'linked'],
      ['--confidence-tier', 'high'],
      ['--authoring', trimmedOrDefault(form, 'authoring', 'mission_lens_ui')],
      ['--recommendation-kind', trimmed(form, 'recommendationKind')],
      ['--recommendation-reason', trimmed(form, 'recommendationReason')],
      ['--note', trimmed(form, 'note')]
    ]);
    redirectWithUpdated(url, date, runId);
  },
  reassignActualMapping: async ({ request, url }: { request: Request; url: URL }) => {
    const form = await request.formData();
    const runId = trimmed(form, 'runId');
    const date = trimmed(form, 'date');
    const planNodeId = trimmed(form, 'planNodeId');
    const activityRefId = trimmed(form, 'activityRefId');
    if (!runId || !date || !planNodeId || !activityRefId) {
      return fail(400, { ok: false, error: 'Missing required reassignment fields.' });
    }
    await invokeMissionLensAction('reassign-mapping', [
      ['--run-id', runId],
      ['--date', date],
      ['--activity-ref-id', activityRefId],
      ['--plan-node-id', planNodeId],
      ['--confidence-tier', 'high'],
      ['--note', trimmed(form, 'note')]
    ]);
    redirectWithUpdated(url, date, runId);
  },
  unlinkActualMapping: async ({ request, url }: { request: Request; url: URL }) => {
    const form = await request.formData();
    const runId = trimmed(form, 'runId');
    const date = trimmed(form, 'date');
    const activityRefId = trimmed(form, 'activityRefId');
    if (!runId || !date || !activityRefId) {
      return fail(400, { ok: false, error: 'Missing required unlink fields.' });
    }
    await invokeMissionLensAction('unlink-mapping', [
      ['--run-id', runId],
      ['--date', date],
      ['--activity-ref-id', activityRefId],
      ['--confidence-tier', 'high'],
      ['--note', trimmed(form, 'note')]
    ]);
    redirectWithUpdated(url, date, runId);
  },
  abstainActualMapping: async ({ request, url }: { request: Request; url: URL }) => {
    const form = await request.formData();
    const runId = trimmed(form, 'runId');
    const date = trimmed(form, 'date');
    const activityRefId = trimmed(form, 'activityRefId');
    if (!runId || !date || !activityRefId) {
      return fail(400, { ok: false, error: 'Missing required abstain fields.' });
    }
    await invokeMissionLensAction('abstain-mapping', [
      ['--run-id', runId],
      ['--date', date],
      ['--activity-ref-id', activityRefId],
      ['--confidence-tier', 'high'],
      ['--note', trimmed(form, 'note')]
    ]);
    redirectWithUpdated(url, date, runId);
  },
  applySafeRecommendations: async ({ request, url }: { request: Request; url: URL }) => {
    const form = await request.formData();
    const runId = trimmed(form, 'runId');
    const date = trimmed(form, 'date');
    if (!runId || !date) {
      return fail(400, { ok: false, error: 'Missing required safe recommendation fields.' });
    }
    await invokeMissionLensAction('apply-safe-recommendations', [
      ['--run-id', runId],
      ['--date', date]
    ]);
    redirectWithUpdated(url, date, runId);
  }
};
