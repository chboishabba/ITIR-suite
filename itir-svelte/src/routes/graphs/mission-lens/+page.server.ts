import path from 'node:path';
import { spawn } from 'node:child_process';
import { fail, redirect } from '@sveltejs/kit';

function repoRoot(): string {
  return path.resolve('..');
}

function resolveRunsRoot(): string {
  const fallback = path.join(repoRoot(), 'StatiBaker', 'runs');
  const raw = process.env.SB_RUNS_ROOT?.trim() || fallback;
  return path.resolve(raw);
}

function resolveSbDbPath(): string {
  const explicit = process.env.SB_DASHBOARD_DB?.trim();
  if (explicit) return path.resolve(explicit);
  return path.join(resolveRunsRoot(), 'dashboard.sqlite');
}

function resolveItirDbPath(): string {
  const raw = process.env.ITIR_DB_PATH?.trim() || '.cache_local/itir.sqlite';
  return path.resolve(repoRoot(), raw);
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

async function loadMissionLens(date: string, runId?: string): Promise<any> {
  const raw = await readStdout(
    'python3',
    [
      path.join(repoRoot(), 'SensibLaw', 'scripts', 'mission_lens.py'),
      '--itir-db-path',
      resolveItirDbPath(),
      '--sb-db-path',
      resolveSbDbPath(),
      'report',
      '--date',
      date,
      '--run-id',
      runId || ''
    ],
    repoRoot()
  );
  return JSON.parse(raw);
}

export async function load({ url }: { url: URL }) {
  const date = url.searchParams.get('date') || process.env.SB_DATE || new Date().toISOString().slice(0, 10);
  const runId = url.searchParams.get('runId') || '';
  try {
    const report = await loadMissionLens(date, runId);
    return { date, runId, report, error: null as string | null };
  } catch (error) {
    return { date, runId, report: null, error: error instanceof Error ? error.message : String(error) };
  }
}

export const actions = {
  addPlanNode: async ({ request, url }: { request: Request; url: URL }) => {
    const form = await request.formData();
    const runId = String(form.get('runId') ?? '').trim();
    const date = String(form.get('date') ?? '').trim();
    const title = String(form.get('title') ?? '').trim();
    if (!runId || !date || !title) {
      return fail(400, { ok: false, error: 'Missing required mission-plan fields.' });
    }
    const args = [
      path.join(repoRoot(), 'SensibLaw', 'scripts', 'mission_lens.py'),
      '--itir-db-path',
      resolveItirDbPath(),
      'add-node',
      '--run-id',
      runId,
      '--title',
      title,
      '--node-kind',
      String(form.get('nodeKind') ?? 'task'),
      '--status',
      String(form.get('status') ?? 'active'),
      '--source-kind',
      'manual',
      '--parent-plan-node-id',
      String(form.get('parentPlanNodeId') ?? ''),
      '--target-weight',
      String(form.get('targetWeight') ?? '1'),
      '--raw-deadline',
      String(form.get('rawDeadline') ?? ''),
      '--due-start',
      String(form.get('dueStart') ?? ''),
      '--due-end',
      String(form.get('dueEnd') ?? ''),
      '--certainty-kind',
      String(form.get('certaintyKind') ?? ''),
      '--urgency-level',
      String(form.get('urgencyLevel') ?? ''),
      '--flexibility-level',
      String(form.get('flexibilityLevel') ?? '')
    ];
    await readStdout('python3', args, repoRoot());
    const next = new URL(url);
    next.searchParams.set('date', date);
    next.searchParams.set('runId', runId);
    next.searchParams.set('updated', '1');
    throw redirect(303, next.toString());
  },
  addActualMapping: async ({ request, url }: { request: Request; url: URL }) => {
    const form = await request.formData();
    const runId = String(form.get('runId') ?? '').trim();
    const date = String(form.get('date') ?? '').trim();
    const planNodeId = String(form.get('planNodeId') ?? '').trim();
    const activityRefId = String(form.get('activityRefId') ?? '').trim();
    if (!runId || !date || !planNodeId || !activityRefId) {
      return fail(400, { ok: false, error: 'Missing required mapping fields.' });
    }
    const args = [
      path.join(repoRoot(), 'SensibLaw', 'scripts', 'mission_lens.py'),
      '--itir-db-path',
      resolveItirDbPath(),
      'add-mapping',
      '--run-id',
      runId,
      '--activity-ref-id',
      activityRefId,
      '--plan-node-id',
      planNodeId,
      '--mapping-kind',
      'reviewed_link',
      '--status',
      'linked',
      '--confidence-tier',
      'high',
      '--authoring',
      String(form.get('authoring') ?? 'mission_lens_ui'),
      '--recommendation-kind',
      String(form.get('recommendationKind') ?? ''),
      '--recommendation-reason',
      String(form.get('recommendationReason') ?? ''),
      '--note',
      String(form.get('note') ?? '')
    ];
    await readStdout('python3', args, repoRoot());
    const next = new URL(url);
    next.searchParams.set('date', date);
    next.searchParams.set('runId', runId);
    next.searchParams.set('updated', '1');
    throw redirect(303, next.toString());
  },
  reassignActualMapping: async ({ request, url }: { request: Request; url: URL }) => {
    const form = await request.formData();
    const runId = String(form.get('runId') ?? '').trim();
    const date = String(form.get('date') ?? '').trim();
    const planNodeId = String(form.get('planNodeId') ?? '').trim();
    const activityRefId = String(form.get('activityRefId') ?? '').trim();
    if (!runId || !date || !planNodeId || !activityRefId) {
      return fail(400, { ok: false, error: 'Missing required reassignment fields.' });
    }
    const args = [
      path.join(repoRoot(), 'SensibLaw', 'scripts', 'mission_lens.py'),
      '--itir-db-path',
      resolveItirDbPath(),
      'reassign-mapping',
      '--run-id',
      runId,
      '--activity-ref-id',
      activityRefId,
      '--plan-node-id',
      planNodeId,
      '--confidence-tier',
      'high',
      '--note',
      String(form.get('note') ?? '')
    ];
    await readStdout('python3', args, repoRoot());
    const next = new URL(url);
    next.searchParams.set('date', date);
    next.searchParams.set('runId', runId);
    next.searchParams.set('updated', '1');
    throw redirect(303, next.toString());
  },
  unlinkActualMapping: async ({ request, url }: { request: Request; url: URL }) => {
    const form = await request.formData();
    const runId = String(form.get('runId') ?? '').trim();
    const date = String(form.get('date') ?? '').trim();
    const activityRefId = String(form.get('activityRefId') ?? '').trim();
    if (!runId || !date || !activityRefId) {
      return fail(400, { ok: false, error: 'Missing required unlink fields.' });
    }
    const args = [
      path.join(repoRoot(), 'SensibLaw', 'scripts', 'mission_lens.py'),
      '--itir-db-path',
      resolveItirDbPath(),
      'unlink-mapping',
      '--run-id',
      runId,
      '--activity-ref-id',
      activityRefId,
      '--confidence-tier',
      'high',
      '--note',
      String(form.get('note') ?? '')
    ];
    await readStdout('python3', args, repoRoot());
    const next = new URL(url);
    next.searchParams.set('date', date);
    next.searchParams.set('runId', runId);
    next.searchParams.set('updated', '1');
    throw redirect(303, next.toString());
  },
  abstainActualMapping: async ({ request, url }: { request: Request; url: URL }) => {
    const form = await request.formData();
    const runId = String(form.get('runId') ?? '').trim();
    const date = String(form.get('date') ?? '').trim();
    const activityRefId = String(form.get('activityRefId') ?? '').trim();
    if (!runId || !date || !activityRefId) {
      return fail(400, { ok: false, error: 'Missing required abstain fields.' });
    }
    const args = [
      path.join(repoRoot(), 'SensibLaw', 'scripts', 'mission_lens.py'),
      '--itir-db-path',
      resolveItirDbPath(),
      'abstain-mapping',
      '--run-id',
      runId,
      '--activity-ref-id',
      activityRefId,
      '--confidence-tier',
      'high',
      '--note',
      String(form.get('note') ?? '')
    ];
    await readStdout('python3', args, repoRoot());
    const next = new URL(url);
    next.searchParams.set('date', date);
    next.searchParams.set('runId', runId);
    next.searchParams.set('updated', '1');
    throw redirect(303, next.toString());
  },
  applySafeRecommendations: async ({ request, url }: { request: Request; url: URL }) => {
    const form = await request.formData();
    const runId = String(form.get('runId') ?? '').trim();
    const date = String(form.get('date') ?? '').trim();
    if (!runId || !date) {
      return fail(400, { ok: false, error: 'Missing required safe recommendation fields.' });
    }
    const args = [
      path.join(repoRoot(), 'SensibLaw', 'scripts', 'mission_lens.py'),
      '--itir-db-path',
      resolveItirDbPath(),
      '--sb-db-path',
      resolveSbDbPath(),
      'apply-safe-recommendations',
      '--run-id',
      runId,
      '--date',
      date
    ];
    await readStdout('python3', args, repoRoot());
    const next = new URL(url);
    next.searchParams.set('date', date);
    next.searchParams.set('runId', runId);
    next.searchParams.set('updated', '1');
    throw redirect(303, next.toString());
  }
};
